#!/bin/sh

# Garmin Companion requires Python >= 3.10 for modern Garmin authentication.
# On 32-bit Asustor NAS models (e.g. AS-202TE) the system Python is 3.7, so
# Entware from App Central is required to provide Python 3.11.

export PATH="/opt/bin:/opt/sbin:$PATH"

HAS_MODERN_PY=0
if command -v python3 >/dev/null 2>&1; then
    PY_VER=$(python3 -c 'import sys; print(sys.version_info.major * 10 + sys.version_info.minor)' 2>/dev/null)
    if [ -n "$PY_VER" ] && [ "$PY_VER" -ge 310 ]; then
        HAS_MODERN_PY=1
    fi
fi

if [ "$HAS_MODERN_PY" -eq 0 ] && [ ! -x "/opt/bin/opkg" ] && [ ! -x "/opt/bin/python3" ]; then
    echo "=================================================================="
    echo "ERROR: Garmin Companion requires Python 3.10 or later."
    echo "On this NAS model, you must install 'Entware' from App Central"
    echo "before installing this package."
    echo "=================================================================="
    exit 1
fi

# ADM deletes the whole app folder on upgrade (data/ included): move it aside and
# post-install.sh puts it back after the new version is unpacked.
APKG_PATH="/usr/local/AppCentral/garmin-companion"
TRANSIT_DIR="/volume1/.garmin-companion-upgrade"
if [ -f "$APKG_PATH/data/app.db" ]; then
    # Stop the app so the DB copy is consistent (with WAL, data may live in app.db-wal)
    [ -f "$APKG_PATH/CONTROL/start-stop.sh" ] && /bin/sh "$APKG_PATH/CONTROL/start-stop.sh" stop >/dev/null 2>&1
    rm -rf "$TRANSIT_DIR"
    mkdir -p "$TRANSIT_DIR"
    if ! cp -a "$APKG_PATH/data/." "$TRANSIT_DIR/"; then
        echo "ERROR: could not move data aside to $TRANSIT_DIR; upgrade aborted."
        exit 1
    fi
fi

exit 0
