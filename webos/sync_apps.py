#!/usr/bin/env python3
"""Collects the TV's app list, with the real icons, into webos/apps.json for the build to embed.

    python3 webos/sync_apps.py 192.168.1.50

The TV's remote control API (SSAP) on 127.0.0.1:3000 answers with the launch points LG's own
launcher shows, and with each icon as a URL the TV itself serves. An SSH tunnel brings that
port to this computer, so nothing runs on the TV but SSH. The first time, the TV asks to allow
the connection: accept it on the TV with the remote. The client key it gives back is kept in
~/.ssh/customwebos_webos_ssap, so later runs ask nothing.

Run it again after installing or removing apps on the TV, then rebuild.

Python 3 and OpenSSH only, no packages.
"""
import base64
import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, 'webos', 'apps.json')
KEYS = os.path.join(os.path.expanduser('~'), '.ssh')
SSAP_PORT = 3000


def ssap_key_path():
    return os.path.join(KEYS, 'customwebos_webos_ssap')


def read_key():
    """The client key the TV gave us, if we have one."""
    path = ssap_key_path()
    if not os.path.exists(path):
        return ''
    with open(path, encoding='utf-8') as f:
        return f.read().strip()


def write_key(key):
    if not key:
        return
    os.makedirs(KEYS, exist_ok=True)
    with open(ssap_key_path(), 'w', encoding='utf-8') as f:
        f.write(key)
    os.chmod(ssap_key_path(), 0o600)


def frame(sock, opcode, payload=b''):
    """A masked client frame, as the protocol wants."""
    mask = os.urandom(4)
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    size = len(payload)
    header = bytes([0x80 | opcode])
    if size < 126:
        header += bytes([0x80 | size])
    elif size < 65536:
        header += bytes([0x80 | 126]) + struct.pack('!H', size)
    else:
        header += bytes([0x80 | 127]) + struct.pack('!Q', size)
    sock.sendall(header + mask + masked)


def launch_points(port, client_key, timeout=60):
    """The TV's launch points, through the remote control API. Returns (list, client_key)."""
    sock = socket.create_connection(('127.0.0.1', port), timeout=timeout)
    key = base64.b64encode(os.urandom(16)).decode()
    sock.sendall(('GET / HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nUpgrade: websocket\r\n'
                   'Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n'
                   'Origin: http://127.0.0.1:%d\r\n\r\n' % (port, key, port)).encode())
    buf = b''
    while b'\r\n\r\n' not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            raise IOError('the TV closed the connection')
        buf += chunk
    head, _, rest = buf.partition(b'\r\n\r\n')
    if b'101' not in head.split(b'\r\n')[0]:
        raise IOError('the TV refused the connection: ' + head.decode('latin1')[:120])
    frame(sock, 0x1, json.dumps({'type': 'register', 'id': 'reg', 'payload': {
        'forcePairing': False, 'pairingType': 'PROMPT', 'client-key': client_key,
        'manifest': {'manifestVersion': 1, 'appVersion': '1.0',
                     'permissions': ['READ_INSTALLED_APPS']}}}).encode())
    data = rest
    sock.settimeout(timeout)
    try:
        while True:
            while len(data) < 2:
                chunk = sock.recv(4096)
                if not chunk:
                    raise IOError('the TV closed the connection')
                data += chunk
            b0, b1 = data[0], data[1]
            opcode = b0 & 0x0f
            size = b1 & 0x7f
            offset = 2
            if size == 126:
                while len(data) < 4:
                    data += sock.recv(4096)
                size = struct.unpack('!H', data[2:4])[0]
                offset = 4
            elif size == 127:
                while len(data) < 10:
                    data += sock.recv(4096)
                size = struct.unpack('!Q', data[2:10])[0]
                offset = 10
            if b1 & 0x80:
                offset += 4
            while len(data) < offset + size:
                chunk = sock.recv(4096)
                if not chunk:
                    raise IOError('the TV closed the connection')
                data += chunk
            payload = data[offset:offset + size]
            data = data[offset + size:]
            if opcode == 0x9:                       # ping
                frame(sock, 0xA, payload)
                continue
            if opcode == 0x8:
                raise IOError('the TV closed the connection: ' + payload[:80].decode('latin1', 'replace'))
            if opcode not in (0x1, 0x0):
                continue
            message = json.loads(payload.decode('utf-8', 'replace'))
            if message.get('type') == 'registered':
                write_key(message['payload'].get('client-key', ''))
                frame(sock, 0x1, json.dumps({'type': 'request', 'id': 'call', 'uri':
                                              'ssap://com.webos.applicationManager/listLaunchPoints'}).encode())
            elif message.get('id') == 'call':
                return message['payload'].get('launchPoints', []), message['payload'].get('client-key', '')
            elif message.get('type') == 'error':
                raise IOError('the TV said: ' + str(message.get('error')))
    finally:
        sock.close()


def tunnel(ip, key, port):
    """An SSH tunnel to the TV's remote control API; returns the process."""
    sys.path.insert(0, os.path.join(ROOT, 'webos'))
    import install                                                  # the key and the SSH options
    args = ['ssh', '-N', '-L', '%d:127.0.0.1:%d' % (port, SSAP_PORT)] + install.SSH_OPTS + \
           ['-i', key, 'prisoner@' + ip]
    return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def free_port():
    """A local port for the tunnel, free right now."""
    probe = socket.socket()
    probe.bind(('127.0.0.1', 0))
    port = probe.getsockname()[1]
    probe.close()
    return port


def icon_url(url):
    """The icon's URL as the TV serves it: the TV answers on 3000, whatever the tunnel's port was."""
    if not url:
        return ''
    parts = urllib.parse.urlsplit(url)
    if not parts.scheme or not parts.netloc:
        return url
    return urllib.parse.urlunsplit((parts.scheme, '127.0.0.1:%d' % SSAP_PORT, parts.path, parts.query, parts.fragment))


def fetch_icons(points, port, out_dir):
    """The TV's raw icons, through the tunnel, as <id>.png for tools/prepare_icons.py."""
    os.makedirs(out_dir, exist_ok=True)
    made = 0
    for p in points:
        url = p.get('largeIcon') or p.get('icon') or ''
        if not p.get('id') or not url:
            continue
        parts = urllib.parse.urlsplit(url)
        try:
            with urllib.request.urlopen('http://127.0.0.1:%d%s' % (port, parts.path), timeout=15) as r:
                data = r.read()
        except Exception:
            continue
        if not data:
            continue
        with open(os.path.join(out_dir, p['id'] + '.png'), 'wb') as f:
            f.write(data)
        made += 1
    return made


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.exit(__doc__)
    ip = args[0]
    port = free_port()
    sys.path.insert(0, os.path.join(ROOT, 'webos'))
    import install                                                  # the key and the SSH options
    key = install.fetch_key(ip)
    process = tunnel(ip, key, port)
    try:
        for _ in range(20):                                         # the tunnel takes a moment
            try:
                socket.create_connection(('127.0.0.1', port), timeout=1).close()
                break
            except OSError:
                time.sleep(0.5)
        try:
            points, _ = launch_points(port, read_key())
        except (IOError, socket.timeout) as e:
            if '403' in str(e) or 'pairing' in str(e) or isinstance(e, socket.timeout):
                sys.exit('The TV is asking to allow the connection. Accept it on the TV with the remote, '
                         'then run this again.\n(%s)' % e)
            raise
        raw = os.path.join(ROOT, 'webos', 'icons_raw')
        icons = fetch_icons(points, port, raw)          # the tunnel is still open here
    finally:
        process.terminate()
    apps = []
    for p in points:
        if not p.get('id'):
            continue
        apps.append({'id': p['id'], 'title': p.get('title') or p['id'],
                     'icon': icon_url(p.get('largeIcon') or p.get('icon') or ''),
                     'color': p.get('bgColor') or p.get('iconColor') or ''})
    with open(APPS, 'w', encoding='utf-8') as f:
        json.dump(apps, f, ensure_ascii=False, indent=1)
    print('Wrote %s (%d apps) and %d raw icons. Build again to put them on the TV.'
          % (os.path.relpath(APPS, ROOT), len(apps), icons))


if __name__ == '__main__':
    main()
