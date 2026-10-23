#!/usr/bin/env bash
# Build script for Custom webOS Home on LG webOS TV.
# Generates CustomWebOS-webos.ipk ready for Developer Mode installation.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$ROOT/webos/build.py" "$@"
