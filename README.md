<div align="center">

<img src="docs/assets/icon-512.png" width="96" alt="">

# Custom webOS Home

**A fast, ad-free home screen for LG webOS TVs.**

Trending picks from your own apps, the weather at a glance, inputs and shortcuts, with a clean visual design that follows the sunset.<br>
Open source. Free of clutter. Installs via Developer Mode without root.

[**fernandodimas.github.io/custom-webos**](https://fernandodimas.github.io/custom-webos) · [Install](#install) · [Features](#features) · [Settings](#settings)

<img src=".github/preview.webp" width="880" alt="Custom webOS Home: a glass shelf of apps, trending picks, weather and inputs">

</div>

## Features

- **No ads.** No sponsored banners, promotional rows or autoplay videos.
- **Your apps, front and center.** Fast glass shelf with your favorite streaming apps.
- **Trending picks.** Top trending titles and new releases from your active services (via TMDB). Separate tabs for Explore, Movies, and TV Shows.
- **Inputs & shortcuts.** Direct access to HDMI ports (with auto device brand detection for PlayStation, Xbox, Switch, Apple TV, Fire TV), Live TV and Settings.
- **Weather and forecast.** Real-time weather, hourly forecast, sunrise and sunset from Open-Meteo.
- **Day and night modes.** Automatic theme adaptation based on local sunrise and sunset.
- **Screensaver.** High-resolution backdrop photos with a clock display when idle.
- **Safe & reversible.** Runs as a standard webOS application via Developer Mode. Does not root, alter system partitions, or affect factory firmware.

## Install

Requires an LG TV running webOS 3.0 or newer and a computer on the same local network.

### 1. On the TV
1. Open the LG Content Store and install the **Developer Mode** app.
2. Sign in with a free [LG Developer account](https://webostv.developer.lge.com).
3. Turn **Dev Mode Status** ON (the TV will restart).
4. Re-open Developer Mode and turn **Key Server** ON. Note the IP address and passphrase displayed.

### 2. On your Computer
1. Clone the repository:
   ```bash
   git clone https://github.com/fernandodimas/custom-webos && cd custom-webos
   ```
2. Build the `.ipk` package:
   ```bash
   ./build.sh
   ```
   *(The first run creates `config.properties`. Set your city, coordinates, and TMDB key if desired).*
3. Install onto the TV:
   ```bash
   python3 webos/install.py <TV_IP_ADDRESS>
   ```
   Enter the passphrase shown on your TV screen. Future installs and updates will reuse the generated key without prompting again.

### 3. Sync TV apps and icons (recommended)
To pull your TV's installed apps and custom icons:
```bash
python3 webos/sync_apps.py <TV_IP_ADDRESS>
python3 tools/prepare_icons.py webos/icons_raw
python3 webos/build.py && python3 webos/install.py <TV_IP_ADDRESS>
```

### 4. Quick Access
On your LG TV, with Custom webOS Home open, press and hold any number key (e.g. `1`) on your remote control to map it as a Quick Access shortcut.

Developer Mode lasts ~40 days: open the Developer Mode app periodically and click **EXTEND**. To uninstall, run `python3 webos/install.py <TV_IP_ADDRESS> --uninstall`.

## Settings

Configuration options in `config.properties`:

| Key | Description | Default |
|---|---|---|
| `tmdb_key` | Free TMDB API key for trending picks | empty |
| `tmdb_region` | Two-letter country code for provider catalog | `US` |
| `latitude`, `longitude` | Location coordinates for weather and sunset | New York |
| `city` | City name displayed on weather card | `Weather` |
| `language` | Interface language (`auto`, `pt`, `en`, `es`, `de`, `ru`) | `auto` |
| `show_crypto` | Show crypto ticker quotes | `false` |
| `currency` | Currency for quotes (`USD`, `EUR`, `BRL`, etc.) | `USD` |
| `temperature` | Temperature unit (`C`, `F`, `auto`) | `auto` |

### TMDB API Key
Get a free key in two minutes at [themoviedb.org](https://www.themoviedb.org/signup) under Settings → API. Paste the key or read access token into `tmdb_key=`.

## How it works

- **Pure Web App (`web/`):** Built with Vanilla HTML5, CSS and ES5 JavaScript optimized for LG's Chromium runtime across webOS versions.
- **Native Luna Bus (`web/tv.js`):** Interacts with LG's service bus (`com.webos.applicationManager`, `com.webos.service.eim`) to launch apps, list inputs, and switch sources without native binaries.
- **Self-contained Packager (`webos/build.py`):** Bundles web assets into standard `.ipk` (ar archive) without requiring heavy webOS SDK installations.

## Privacy

No user data collection, telemetry, or external accounts required. All requests (TMDB, Open-Meteo) are made directly from the TV to public endpoints.

## Credits & License

- Built upon work from [Free My TV](https://github.com/simbasjungles/free-my-tv) and [FreeMyTvWebOS](https://github.com/danielthejoker18/FreeMyTvWebOS).
- Uses [The Movie Database (TMDB)](https://www.themoviedb.org/) API (not endorsed or certified by TMDB).
- Weather by [Open-Meteo.com](https://open-meteo.com/) (CC BY 4.0).
- Icons: [Material Symbols](https://fonts.google.com/icons) (Apache 2.0).
- Font: [Inter](https://rsms.me/inter/) (SIL OFL 1.1).
- License: [MIT](LICENSE).
