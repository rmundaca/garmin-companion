#!/bin/sh

APKG_PATH="/usr/local/AppCentral/garmin-companion"

# Stop the service if running
if [ -f "$APKG_PATH/CONTROL/start-stop.sh" ]; then
    "$APKG_PATH/CONTROL/start-stop.sh" stop
fi

# Back up the database before uninstalling. With WAL, data may live in app.db-wal:
# copy all three files together into a timestamped folder so they can be restored as-is.
if [ -f "$APKG_PATH/data/app.db" ]; then
    BACKUP_DIR="/volume1/home/garmin-companion-backup/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    for f in app.db app.db-wal app.db-shm; do
        [ -f "$APKG_PATH/data/$f" ] && cp "$APKG_PATH/data/$f" "$BACKUP_DIR/$f"
    done
    echo "Database backed up to $BACKUP_DIR"
fi

exit 0
