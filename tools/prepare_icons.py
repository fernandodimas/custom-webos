#!/usr/bin/env python3
"""Turns the TV's raw app icons into the set the home screen ships (web/icons/).

    python3 tools/prepare_icons.py webos/icons_raw        # reads <id>.png, writes web/icons/

webos/sync_apps.py downloads the TV's raw icons into webos/icons_raw; this turns them into
the set the app ships. The shelf draws each icon over the app's brand gradient (web/home.js,
SHELF). Most of the TV's icons are already the brand's artwork edge to edge, which reads
exactly like that; a few are a small logo on a big solid field — a box on the shelf that
doesn't match the gradient. For those the field is converted to alpha by un-blending every
pixel from it (a flood-fill would leave the anti-aliased edges as an opaque fringe of the
field color) and the logo is trimmed out, so the brand gradient shows through.
IDs are listed per hand: the treatment is only right when the field is a flat backdrop and
the logo's own colors are far from it.
"""
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'web', 'icons')

# Icons whose solid field is a backdrop, not the brand's color: strip it, keep the logo.
# 'white'  — white field, logo colors near black/red: un-blend from white.
# 'field'  — flat brand field sampled from the corners, logo is white on it.
# ('field', 'white') / ('white', 'white') — same model, but what's left is recolored white
#                      (the logo is colored or dark, and the pill it lands on is dark:
#                      recoloring keeps it legible).
STRIP_BG = {
    # the shelf: the logo floats over the brand gradient
    'netflix': 'white',
    'youtube.leanback.v4': 'white',
    'amazon': 'field',
    'com.disney.disneyplus-prod': 'field',
    'com.wbd.stream': 'field',
    'com.apple.appletv': 'field',
    'spotify-beehive': ('field', 'white'),
    # the rest: a logo on a flat field of its own
    'amazon.alexa.view': 'white',
    'com.apple.applemusic': 'field',
    'com.boosteroidtv.streaming': 'field',
    'com.crunchyroll.webapp': 'field',
    'com.dw.app.dwforsmarttv': 'field',
    'com.epoxyaisports': ('white', 'white'),
    'com.geforcenow.play': 'field',
    'com.instantbits.cast.webvideo': ('field', 'white'),
    'com.mercadolibre.mercadoplay': ('field', 'white'),
    'com.mubi': 'field',
    'com.palmdts.devmode': 'field',
    'com.plutotv.app': ('field', 'white'),
    'com.pplus.webapp.prod-intl': 'field',
    'com.twin.app.gamingportal': 'white',
    'com.webos.app.browser': 'field',
    'com.webos.app.camera': 'field',
    'com.webos.app.hdmi2': 'field',
    'com.webos.app.hdmi3': 'field',
    'com.webos.app.hdmi4': 'field',
    'com.webos.app.lgchannels': 'field',
    'com.webos.app.livetv': 'field',
    'globoplaywebos': 'field',
    'io.we3world.artlume': 'field',
    'looke': 'field',
    'org.jellyfin.webos': 'field',
    'shortcutcopilot': 'white',
    'tv.redbull.lg': 'field',
    'tv.twitch.tv.starshot.lg': 'field',
}

PAD = 2         # transparent margin kept around the trimmed logo
MIN_ALPHA = 20  # blended-from-white alpha below this counts as the field, not the logo


def field_color(im):
    """The flat field behind the logo: the corners, or the commonest opaque color when the
    artwork has rounded corners (the corner pixels are transparent there)."""
    w, h = im.size
    px = im.load()
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    if all(c[3] > 250 for c in corners):
        return tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    counts = {}
    opaque = 0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b, a = px[x, y]
            if a > 250:
                opaque += 1
                counts[(r, g, b)] = counts.get((r, g, b), 0) + 1
    if not opaque:
        return None
    color, times = max(counts.items(), key=lambda kv: kv[1])
    if times * 5 < opaque * 3:      # less than 60% of the opaque area: not a flat field
        return None
    return color


def strip_field(im, mode):
    """Un-blend every pixel from the field color (field goes transparent, anti-aliased
    edges keep a clean unblended color instead of a fringe); then trim to the logo."""
    recolor = isinstance(mode, tuple)
    if recolor:
        mode = mode[0]
    im = im.convert('RGBA')
    w, h = im.size
    px = im.load()

    field = field_color(im)
    if field is None:
        return im
    # channel where the field sits farthest from white — the one the white logo reads on
    ch = min(range(3), key=lambda i: field[i])

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if mode == 'white':
                # pixel = t*white + (1-t)*logo; t from the smallest channel (logo near 0)
                t = min(r, g, b) / 255.0
                f = (255.0, 255.0, 255.0)
            else:
                # pixel = t*field + (1-t)*white-logo; solve t on the field's weakest channel
                c = (r, g, b)[ch]
                t = (255.0 - c) / (255.0 - field[ch])
                f = field
            t = min(1.0, max(0.0, t))
            alpha = 1.0 - t
            if alpha < MIN_ALPHA / 255.0:
                px[x, y] = (r, g, b, 0)
                continue
            rgb = tuple(
                int(round(min(255.0, max(0.0, (v - t * fv) / alpha))))
                for v, fv in zip((r, g, b), f)
            )
            if recolor:
                rgb = (255, 255, 255)
            # the pixel's own alpha is how much of the shape it covers, not part of the mix
            px[x, y] = rgb + (int(round(alpha * (a / 255.0) * 255)),)
    box = im.getbbox()          # bbox of the non-transparent pixels
    if box:
        x0, y0, x1, y1 = box
        box = (max(0, x0 - PAD), max(0, y0 - PAD), min(w, x1 + PAD), min(h, y1 + PAD))
        im = im.crop(box)
    return im


def main(src):
    if not os.path.isdir(src):
        sys.exit('not a directory: ' + src)
    os.makedirs(OUT, exist_ok=True)
    made, skipped = 0, 0
    for name in sorted(os.listdir(src)):
        if not name.endswith('.png'):
            continue
        app_id = name[:-4]
        path = os.path.join(src, name)
        if app_id in STRIP_BG:
            im = strip_field(Image.open(path), STRIP_BG[app_id])
            im.save(os.path.join(OUT, name), optimize=True)
            made += 1
            print('stripped %s -> %dx%d' % (name, im.size[0], im.size[1]))
        else:
            with open(path, 'rb') as f:
                data = f.read()
            with open(os.path.join(OUT, name), 'wb') as f:
                f.write(data)
            skipped += 1
    print('web/icons: %d processed, %d copied as-is, %d total' % (made, skipped, made + skipped))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[-1])
