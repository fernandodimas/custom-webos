/*
 * The TV's side of the web home screen: its apps, opening one, its inputs, its settings, the Back key, its time zone.
 *  - LG webOS: the TV's service bus (Luna), the same calls LG's launcher makes.
 *  - A desktop browser: a stand-in with sample apps, so the screen can be previewed and tested on a computer.
 * Plain ES5: older webOS TVs run a Chromium from 2015-2017 (webOS 3 and 4).
 */
var TV = (function () {
  'use strict';

  var webos = typeof window.PalmServiceBridge !== 'undefined';
  var calls = [];   // a bridge is collected if nothing holds it before its reply arrives

  /** One Luna call; done(result) with null on failure. */
  function luna(uri, params, done) {
    if (!webos) {
      if (done) setTimeout(function () { done(null); }, 0);
      return;
    }
    var bridge = new window.PalmServiceBridge();
    calls.push(bridge);
    var finished = false;
    bridge.onservicecallback = function (message) {
      if (finished) return;
      finished = true;
      var i = calls.indexOf(bridge);
      if (i >= 0) calls.splice(i, 1);
      var result = null;
      try { result = JSON.parse(message); } catch (e) {}
      if (done) done(result && result.returnValue !== false ? result : null);
    };
    bridge.call(uri, JSON.stringify(params || {}));
  }

  // LG inputs: the antenna and the four HDMI ports, with the apps LG opens for them.
  var INPUTS = [
    {id: 'com.webos.app.livetv', key: 'live', label: null, symbol: 'live_tv'},
    {id: 'com.webos.app.hdmi1', key: 'hdmi1', label: 'HDMI 1', symbol: 'hdmi'},
    {id: 'com.webos.app.hdmi2', key: 'hdmi2', label: 'HDMI 2', symbol: 'hdmi'},
    {id: 'com.webos.app.hdmi3', key: 'hdmi3', label: 'HDMI 3', symbol: 'hdmi'},
    {id: 'com.webos.app.hdmi4', key: 'hdmi4', label: 'HDMI 4', symbol: 'hdmi'}
  ];

  // Not shown among LG's apps: the inputs above, LG's own home and launchers, and the system's own pieces
  // (the keyboard, the notification centre, the setup wizards, the updates, the voice assistants).
  var HIDDEN = /^(com\.webos\.app\.(livetv|hdmi\d|home|homeconnect|discovery|launcher|inputpicker|keyboard|keyboardfull|notificationcenter|connectionwizard|softwareupdate|voice|assistant|voiceassistant|voiceboard|recordings|screensaver|miracast|smartshare|lgchannels|igallery|picturemode|soundmode|aiservice|aiportal|webosstore|store|contentshop|tts|inputdevices|dday|pvr|progrec|mydocs|snapshot|pip|webosarcade|casting|aitranslate|btmultipleting|btvolumelevel|wl|multiscreen|fita|eisc|ssdp|tvinfo|hangul|camera|multiviewsettings|sportsteamsettings|mediadiscovery|lifeonscreen|storagemanager|lglink-full)|com\.amazon\.alexa\.view|com\.google\.assistant|com\.palmdts\.devmode|com\.instantbits\.cast\.webvideo|com\.webos\.service\.eim|airplay)$/;

  var SAMPLE = [
    ['netflix', 'Netflix', '#E50914'], ['youtube.leanback.v4', 'YouTube', '#FF0033'], ['amazon', 'Prime Video', '#1A98FF'],
    ['com.disney.disneyplus-prod', 'Disney+', '#1838C8'], ['com.hbo.hbomax', 'Max', '#6C3BE0'],
    ['com.apple.appletv', 'Apple TV', '#B8BCC6'], ['globoplaywebos', 'Globoplay', '#FF5A1F'], ['spotify-beehive', 'Spotify', '#1DB954'],
    ['cdp-30', 'Plex', '#E5A00D'], ['com.crunchyroll.webapp', 'Crunchyroll', '#F47521'], ['com.webos.app.browser', 'Web Browser', '#3A7BD5'],
    ['com.palm.app.settings', 'Settings', '#8E8E93']
  ];

  // webOS 6 and newer give Developer Mode apps only the "public" Luna group, which leaves out
  // listLaunchPoints: the TV answers "Denied method call listLaunchPoints" (issue #93). What the
  // build carries (webos/sync_apps.py) is the list the TV's own launcher shows, with the icons the
  // TV serves; without it, getAppLoadStatus (also "public") says which of the known ids it has,
  // one id at a time, and the tiles show the name on the brand color.
  var KNOWN = [
    ['netflix', 'Netflix'], ['amazon', 'Prime Video'], ['youtube.leanback.v4', 'YouTube'],
    ['youtube.leanback.kids.v4', 'YouTube Kids'], ['youtube.leanback.ytv.v1', 'YouTube TV'],
    ['com.disney.disneyplus-prod', 'Disney+'], ['com.wbd.stream', 'Max'], ['com.hbo.hbomax', 'Max'],
    ['globoplaywebos', 'Globoplay'], ['com.globo.multishow', 'Multishow'], ['com.globo.gshow', 'Gshow'],
    ['com.bandplay', 'Bandplay'], ['com.sbtplus.app', 'SBT+'], ['com.recordtv.r7', 'Record TV'],
    ['spotify-beehive', 'Spotify'], ['com.mubi', 'MUBI'], ['com.crunchyroll.webapp', 'Crunchyroll'],
    ['tv.twitch.tv.starshot.lg', 'Twitch'], ['com.apple.appletv', 'Apple TV'],
    ['hulu', 'Hulu'], ['com.peacock.tv', 'Peacock'], ['com.paramount.network', 'Paramount+'],
    ['com.nfl.app', 'NFL'], ['vugu', 'Vudu'], ['com.movenetworks.app.sling-tv-sling-production', 'Sling TV'],
    ['com.dazn.dazn', 'DAZN'], ['com.fubo.app', 'fuboTV'], ['com.tviplayer.victor', 'ViU'],
    ['googleplaymovieswebos', 'Google Play Filmes'], ['cdp-30', 'Plex'], ['com.plexapp.plex', 'Plex'],
    ['com.webos.app.browser', 'Web Browser'], ['com.palm.app.settings', 'Settings'],
    ['com.webos.app.tvguide', 'Guia de TV'], ['com.webos.app.music', 'Música'],
    ['com.webos.app.photovideo', 'Fotos e Vídeos']
  ];

  /** The apps the TV has, asked one id at a time; done(list). */
  function knownApps(done) {
    var found = [], next = 0, pending = 0, sent = false;
    function finish() {
      if (sent) return;
      sent = true;
      done(found.length ? found : SAMPLE.map(function (s) { return {id: s[0], title: s[1], icon: '', color: s[2]}; }));
    }
    function step() {
      if (next >= KNOWN.length) {
        pending--;
        if (pending === 0) finish();
        return;
      }
      var k = KNOWN[next++], answered = false;
      var timer = setTimeout(function () { if (answered) return; answered = true; step(); }, 4000);
      luna('luna://com.webos.applicationManager/getAppLoadStatus', {appId: k[0]}, function (res) {
        if (answered) return;
        answered = true;
        clearTimeout(timer);
        if (res && res.exist && k[0] !== self && !HIDDEN.test(k[0])) found.push({id: k[0], title: k[1], icon: '', localIcon: localIcon(k[0]), color: ''});
        step();
      });
    }
    for (var w = 0; w < 6; w++) { pending++; step(); }   // a few at a time, so the TV's bus isn't flooded
    setTimeout(finish, 15000);                          // the TV stopped answering
  }

  /** The app list the build carries (webos/sync_apps.py): the TV's own, with its icons. */
  function storedApps() {
    var list = (typeof window.APPS !== 'undefined' && window.APPS) || [];
    var out = [];
    for (var i = 0; i < list.length; i++) {
      var a = list[i];
      if (!a || !a.id || a.id === self || HIDDEN.test(a.id)) continue;
      out.push({id: a.id, title: a.title || a.id, icon: a.icon || '', localIcon: localIcon(a.id), color: a.color || ''});
    }
    return out;
  }

  /** The icon the build carries for this app: the TV's own artwork, with its field taken out
      (tools/prepare_icons.py), so the logo lies on the brand gradient instead of in a box. */
  function localIcon(id) {
    return id ? 'icons/' + id + '.png' : '';
  }

  var self = 'com.fdimas.customwebos';
  if (webos && window.PalmSystem && window.PalmSystem.identifier) self = window.PalmSystem.identifier.split(' ')[0];

  // MARK: - The TV

  return {
    name: webos ? 'webos' : 'browser',

    /** Installed apps, as the TV's launcher lists them: [{id, title, icon, color}]. */
    apps: function (done) {
      if (!webos) {
        done(SAMPLE.map(function (s) { return {id: s[0], title: s[1], icon: '', color: s[2]}; }));
        return;
      }
      luna('luna://com.webos.applicationManager/listLaunchPoints', {}, function (res) {
        // Some webOS builds deny listing apps to sideloaded apps ("Denied method call listLaunchPoints") even
        // with requiredPermissions set; launch(id) still works there, so use the list the build carries.
        if (!res) {
          var stored = storedApps();
          if (stored.length) { done(stored); return; }
          knownApps(done);
          return;
        }
        var out = [];
        var points = res.launchPoints || [];
        for (var i = 0; i < points.length; i++) {
          var p = points[i];
          if (!p.id || p.id === self || HIDDEN.test(p.id)) continue;
          out.push({id: p.id, title: p.title || p.id, icon: p.largeIcon || p.icon || '', localIcon: localIcon(p.id), color: p.bgColor || p.iconColor || ''});
        }
        done(out);
      });
    },

    /** Opens an app (or an input); done(ok). */
    launch: function (id, params, done) {
      if (!webos) {
        if (done) setTimeout(function () { done(true); }, 0);
        return;
      }
      luna('luna://com.webos.applicationManager/launch', params ? {id: id, params: params} : {id: id}, function (res) {
        if (done) done(!!res);
      });
    },

    /** The antenna and HDMI inputs; `connected` when the TV says a device is on (when it tells). */
    inputs: function (done) {
      var list = INPUTS.map(function (x) { return {id: x.id, key: x.key, label: x.label, symbol: x.symbol, connected: true}; });
      if (!webos) {
        list[2].connected = false;
        list[3].connected = false;
        list[4].connected = false;
        done(list);
        return;
      }
      luna('luna://com.webos.service.eim/getAllInputStatus', {}, function (res) {
        var devices = res && res.devices ? res.devices : null;
        if (devices) {
          for (var i = 1; i < list.length; i++) {
            for (var j = 0; j < devices.length; j++) {
              var d = devices[j];
              if (d.appId !== list[i].id) continue;
              list[i].connected = d.connected !== false;
              // A name the person gave the input on the TV ("PS5"), if any.
              if (d.label && !/^hdmi\s*\d$/i.test(d.label)) list[i].label = d.label;
              if (d.icon) list[i].icon = d.icon;
            }
          }
        }
        for (var k = 0; k < list.length; k++) {
          var item = list[k];
          item.localIcon = localIcon(item.id);
          var lbl = (item.label || '').toLowerCase();
          if (/xbox/i.test(lbl)) {
            item.symbol = 'xbox';
            item.label = 'Xbox';
            item.gradient = ['#107C10', '#0B520B'];
            item.color = '#107C10';
            item.localIcon = null;
          } else if (/playstation|ps\s*[345]/i.test(lbl)) {
            item.symbol = 'playstation';
            item.label = 'PlayStation';
            item.gradient = ['#003791', '#001D4D'];
            item.color = '#003791';
            item.localIcon = null;
          } else if (/switch|nintendo/i.test(lbl)) {
            item.symbol = 'nintendo';
            item.label = 'Nintendo Switch';
            item.gradient = ['#E60012', '#9E000C'];
            item.color = '#E60012';
            item.localIcon = null;
          } else if (/apple.?tv|appletv/i.test(lbl)) {
            item.symbol = 'appletv_device';
            item.gradient = ['#3A3A3C', '#1C1C1E'];
            item.color = '#3A3A3C';
            item.localIcon = null;
          } else if (/fire.?tv|amazon.?tv|firestick/i.test(lbl)) {
            item.symbol = 'firetv';
            item.gradient = ['#FF9900', '#CC7A00'];
            item.color = '#FF9900';
            item.localIcon = null;
          } else if (/chromecast|google.?tv/i.test(lbl)) {
            item.symbol = 'gamepad';
            item.gradient = ['#4285F4', '#1A56C4'];
            item.color = '#4285F4';
            item.localIcon = null;
          } else if (/sound|audio|soundbar|theater|receiver|arc/i.test(lbl)) {
            item.symbol = 'speaker';
            item.gradient = ['#4A5361', '#2C323B'];
            item.color = '#4A5361';
            item.localIcon = null;
          } else if (/game|console/i.test(lbl)) {
            item.symbol = 'gamepad';
            item.gradient = ['#2B2B30', '#18181A'];
            item.color = '#2B2B30';
            item.localIcon = null;
          } else if (item.key === 'live') {
            item.gradient = ['#E55E78', '#993548'];
            item.color = '#E55E78';
          }
        }
        done(list);
      });
    },

    /** The TV's own settings; done(ok). */
    settings: function (done) {
      this.launch('com.palm.app.settings', null, done);
    },

    /** Back on the first screen: back to wherever the person came from. */
    back: function () {
      if (window.PalmSystem && window.PalmSystem.platformBack) window.PalmSystem.platformBack();
    },

    /** The TV's time zone ("America/Sao_Paulo"), or ''. */
    zone: function () {
      try { return Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) { return ''; }
    },

    /** Key codes: the arrows, OK and LG Back key (461). */
    keys: {left: 37, up: 38, right: 39, down: 40, ok: 13, back: 461}
  };
})();
