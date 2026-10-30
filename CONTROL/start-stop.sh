#!/bin/sh
PKG="garmin-companion"
PORT=8095

export PATH="/opt/bin:/opt/sbin:$PATH"

APKG_PATH="/usr/local/AppCentral/garmin-companion"
PID_FILE="/var/run/garmin-companion.pid"
LAUNCHER_PID_FILE="/var/run/$PKG.launcher.pid"
LOG_FILE="$APKG_PATH/data/app.log"
SELF="$APKG_PATH/CONTROL/start-stop.sh"

# Max wait for Entware and the port after a NAS reboot (5 s attempts)
LAUNCH_TRIES=36

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] start-stop: $*" >> "$LOG_FILE"
}

# The venv points to /opt/bin/python3.11: at NAS boot, Entware (/opt) may not be mounted yet.
# ADM's Python 3.7 is not usable, so there is no fallback: just wait.
find_python() {
    if [ -x "$APKG_PATH/venv/bin/python" ]; then
        echo "$APKG_PATH/venv/bin/python"
    elif [ -x "/opt/bin/python3" ]; then
        echo "/opt/bin/python3"
    fi
}

# Alive and it is our uvicorn (after a reboot the saved PID may belong to another process)
pid_is_app() {
    [ -n "$1" ] && kill -0 "$1" 2>/dev/null && grep -q uvicorn "/proc/$1/cmdline" 2>/dev/null
}

launcher_running() {
    [ -f "$LAUNCHER_PID_FILE" ] && kill -0 "$(cat "$LAUNCHER_PID_FILE")" 2>/dev/null
}

is_running() {
    [ -f "$PID_FILE" ] && pid_is_app "$(cat "$PID_FILE")"
}

port_listening() {
    netstat -ltn 2>/dev/null | grep -q ":$PORT "
}

# Runs in the background: does not block ADM startup and retries until uvicorn is listening
launch() {
    cd "$APKG_PATH" || exit 1
    i=0
    while [ $i -lt $LAUNCH_TRIES ]; do
        i=$((i + 1))
        PYTHON_BIN=$(find_python)
        if [ -z "$PYTHON_BIN" ]; then
            [ $i -eq 1 ] && log "waiting for Entware Python..."
            sleep 5
            continue
        fi

        # Single worker, no access log: minimal RAM and idle disks
        "$PYTHON_BIN" -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" \
            --workers 1 --no-access-log >> "$LOG_FILE" 2>&1 &
        PID=$!
        echo "$PID" > "$PID_FILE"

        # Up to 60 s to import and open the port (slow CPU); if it dies first, retry
        t=0
        while [ $t -lt 60 ]; do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            if port_listening; then
                log "started with PID $PID (attempt $i)"
                rm -f "$LAUNCHER_PID_FILE"
                return 0
            fi
            sleep 1
            t=$((t + 1))
        done
        if kill -0 "$PID" 2>/dev/null; then
            # Still alive but netstat did not confirm the port: assume started
            log "started with PID $PID (port unconfirmed)"
            rm -f "$LAUNCHER_PID_FILE"
            return 0
        fi
        log "uvicorn exited during startup (attempt $i); retrying in 5 s"
        rm -f "$PID_FILE"
        sleep 5
    done
    log "failed to start after $LAUNCH_TRIES attempts"
    rm -f "$LAUNCHER_PID_FILE"
    return 1
}

start() {
    echo "Starting $PKG..."
    if is_running || launcher_running; then
        echo "$PKG is already running."
        return 0
    fi
    cd "$APKG_PATH" || exit 1
    mkdir -p data
    rm -f "$PID_FILE"

    # Minimal rotation: keep a single previous log once it exceeds 5 MB
    if [ -f "$LOG_FILE" ] && [ "$(wc -c < "$LOG_FILE")" -gt 5242880 ]; then
        mv -f "$LOG_FILE" "$LOG_FILE.1"
    fi

    nohup /bin/sh "$SELF" _launch > /dev/null 2>&1 &
    echo $! > "$LAUNCHER_PID_FILE"
    echo "$PKG starting in background (see $LOG_FILE)."
}

stop() {
    echo "Stopping $PKG..."
    if launcher_running; then
        kill -15 "$(cat "$LAUNCHER_PID_FILE")" 2>/dev/null
    fi
    rm -f "$LAUNCHER_PID_FILE"
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if pid_is_app "$PID"; then
            kill -15 "$PID"
            sleep 2
            kill -0 "$PID" 2>/dev/null && kill -9 "$PID"
        fi
        rm -f "$PID_FILE"
        echo "$PKG stopped."
    else
        echo "PID file not found. Process may not be running."
    fi
}

status() {
    if is_running; then
        echo "$PKG is running (PID: $(cat "$PID_FILE"))."
        exit 0
    fi
    if launcher_running; then
        echo "$PKG is starting."
        exit 0
    fi
    echo "$PKG is stopped."
    exit 1
}

case "$1" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 1; start ;;
    status) status ;;
    _launch) launch; exit $? ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0