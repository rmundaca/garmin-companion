#!/bin/sh

APKG_PATH="/usr/local/AppCentral/garmin-companion"
cd "$APKG_PATH" || exit 1

mkdir -p data/tokens
LOG_FILE="$APKG_PATH/data/install.log"

# Data moved aside by pre-install.sh during an upgrade: restore it to data/.
# The aside copy is only deleted if the restore succeeded.
TRANSIT_DIR="/volume1/.garmin-companion-upgrade"
if [ -f "$TRANSIT_DIR/app.db" ]; then
    if cp -a "$TRANSIT_DIR/." data/; then
        rm -rf "$TRANSIT_DIR"
        RESTORED="data restored from $TRANSIT_DIR"
    else
        RESTORED="ERROR restoring data; still in $TRANSIT_DIR"
    fi
fi

echo "=== Garmin Companion install: $(date) ===" > "$LOG_FILE"
[ -n "$RESTORED" ] && echo "$RESTORED" >> "$LOG_FILE"

# 1. Ensure Entware and system PATH
export PATH="/opt/bin:/opt/sbin:$PATH"

# 2. Check for (or auto-install) Python 3.11 from Entware
if [ -x "/opt/bin/opkg" ]; then
    echo "[1/4] Checking Python 3.11 in Entware..." >> "$LOG_FILE"
    if [ ! -x "/opt/bin/python3" ] || [ ! -x "/opt/bin/pip3" ]; then
        echo "Installing python3, pip, openssl and sqlite3 via opkg..." >> "$LOG_FILE"
        /opt/bin/opkg install --force-space python3 python3-pip python3-openssl python3-sqlite3 >> "$LOG_FILE" 2>&1
    fi

    # Ensure virtualenv
    if [ ! -x "/opt/bin/virtualenv" ] && [ -x "/opt/bin/pip3" ]; then
        echo "Installing virtualenv with Entware pip3..." >> "$LOG_FILE"
        /opt/bin/pip3 install --no-cache-dir virtualenv >> "$LOG_FILE" 2>&1
    fi
fi

# 3. Find a Python >= 3.10 binary
PYTHON_EXE=""
if [ -x "/opt/bin/python3" ]; then
    PYTHON_EXE="/opt/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PY_VER=$(python3 -c 'import sys; print(sys.version_info.major * 10 + sys.version_info.minor)' 2>/dev/null)
    if [ -n "$PY_VER" ] && [ "$PY_VER" -ge 310 ]; then
        PYTHON_EXE="python3"
    fi
fi

if [ -z "$PYTHON_EXE" ]; then
    echo "ERROR: No Python >= 3.10 found." >> "$LOG_FILE"
    exit 1
fi

echo "[2/4] Python found: $PYTHON_EXE ($($PYTHON_EXE --version 2>&1))" >> "$LOG_FILE"

# 4. Create (or recreate) the virtual environment if missing
if [ ! -x "venv/bin/python" ]; then
    echo "[3/4] Creating virtual environment..." >> "$LOG_FILE"
    rm -rf venv
    if [ -x "/opt/bin/virtualenv" ]; then
        /opt/bin/virtualenv -p "$PYTHON_EXE" venv >> "$LOG_FILE" 2>&1
    else
        "$PYTHON_EXE" -m venv venv >> "$LOG_FILE" 2>&1
    fi
fi

# 5. Install 32-bit (i686) compatible dependencies
if [ -f "requirements.txt" ] && [ -x "venv/bin/pip" ]; then
    echo "[4/4] Installing dependencies into venv..." >> "$LOG_FILE"
    ./venv/bin/pip install --upgrade pip >> "$LOG_FILE" 2>&1
    # Remove conflicting Pydantic v2 packages if present
    ./venv/bin/pip uninstall -y pydantic-settings >> "$LOG_FILE" 2>&1 || true
    ./venv/bin/pip install --no-cache-dir -r requirements.txt >> "$LOG_FILE" 2>&1
fi

# Owner only (the user the app runs as): data/ holds the Garmin tokens and secret.key
chmod -R u+rwX,go-rwx data/
echo "=== Install completed successfully: $(date) ===" >> "$LOG_FILE"

exit 0
