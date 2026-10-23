# Custom webOS Home: notes for Claude

A lightweight, ad-free custom home launcher for LG webOS TVs.

The app is built as a pure web app (`web/`) in HTML, CSS and ES5 JavaScript, packed into a webOS package (`CustomWebOS-webos.ipk`) via `webos/build.py` (or `./build.sh`).
It installs onto LG TVs through webOS Developer Mode via `webos/install.py` without requiring LG webOS SDK tools.

The website (fernandodimas.github.io/custom-webos) is in `docs/`: static HTML, CSS and JS. A push to `main` publishes it to GitHub Pages (`.github/workflows/pages.yml`). `docs/index.html` (English) and `docs/pt/index.html` (Brazilian Portuguese) are the same page in two languages.

## Installing on an LG TV (webOS)

On LG it's an app, installed through LG's Developer Mode, and changes nothing permanent on the TV: LG's stock home screen remains intact, and Custom webOS Home opens with a long press of a number key (Quick Access).

1. **Ask** for the TV's IP address and city (if not provided). Tools: Python 3 and OpenSSH (`ssh`, `ssh-keygen`), standard on macOS, Linux and Windows 10+.
2. **On the TV** (done by user): LG Content Store → *Developer Mode* → sign in with a free LG developer account (webostv.developer.lge.com) → *Dev Mode Status* ON (TV restarts) → *Key Server* ON. It displays the TV's IP address and passphrase.
3. **Settings:** edit `config.properties` (or run `./build.sh` which generates it from `config.example.properties`). Fill in latitude, longitude, city, and TMDB key.
4. **The TMDB key:** Free at themoviedb.org → Settings → API. Paste it after `tmdb_key=` in `config.properties`.
5. **Build:** `./build.sh` (or `python3 webos/build.py`) → creates `CustomWebOS-webos.ipk`.
6. **Install:** the first run requires the passphrase shown on the TV:
   `python3 webos/install.py <IP>`
   This creates an SSH key in `~/.ssh/customwebos_webos_<IP>`. Future updates run with the same command without reprompting.
7. **Sync real TV apps and icons:**
   `python3 webos/sync_apps.py <IP>`
   `python3 tools/prepare_icons.py webos/icons_raw`
   `python3 webos/build.py && python3 webos/install.py <IP>`
8. **Pinning:** On the TV, with Custom webOS Home open, hold down a number key (e.g., `1`) to bind it to Quick Access.

## Project Structure

- `web/`: The web application that runs on the TV.
  - `web/index.html`: Main stage layout.
  - `web/home.css`: 1080p styling, glassmorphism, responsive navigation.
  - `web/home.js`: Main UI logic, navigation, shelf, drawer, tabs, focus manager.
  - `web/tv.js`: webOS service bus integration (Luna calls for launch, inputs, apps).
  - `web/data.js`: Weather (Open-Meteo), TMDB recommendations, crypto quotes.
  - `web/strings.js`: Multi-language translations.
  - `web/fonts/`: Bundled Inter font.
  - `web/symbols/`: Icon glyphs used for UI and HDMI inputs.
- `webos/`: webOS package scripts.
  - `webos/appinfo.json`: webOS app manifest.
  - `webos/build.py`: Packages web/ into an `.ipk` archive.
  - `webos/install.py`: Deploys `.ipk` to the TV over SSH Developer Mode.
  - `webos/sync_apps.py`: Pulls installed apps list and icons from the TV.
- `tools/`:
  - `tools/webapp.py`: Packaging helper for reading config and web files.
  - `tools/prepare_icons.py`: Processes raw TV icons to transparent monochrome glyphs.
  - `tools/make_device_symbols.py`: Generates HDMI brand icons.
  - `tools/make_art.py`: Generates app logo and web banner art.
- `docs/`: Website published to GitHub Pages.
