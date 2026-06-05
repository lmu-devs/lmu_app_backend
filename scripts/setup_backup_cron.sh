#!/bin/bash

# Setup script for database backup cron job
# This script adds a cron job to run db_backup.sh at 02:00 every night

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/db_backup.sh"
LOG_FILE="/var/log/db_backup.log"

# Ensure backup script is executable
chmod +x "$BACKUP_SCRIPT"

# Create log file if it doesn't exist
sudo touch "$LOG_FILE"
sudo chmod 666 "$LOG_FILE"

# Define the cron job entry
# Runs at 02:00 every day
CRON_JOB="0 2 * * * $BACKUP_SCRIPT >> $LOG_FILE 2>&1"

# Check if cron job already exists
EXISTING_CRON=$(crontab -l 2>/dev/null | grep -F "$BACKUP_SCRIPT" || true)

if [ -n "$EXISTING_CRON" ]; then
    echo "Cron job already exists:"
    echo "$EXISTING_CRON"
    read -p "Do you want to replace it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing cron job and add new one
        (crontab -l 2>/dev/null | grep -v -F "$BACKUP_SCRIPT"; echo "$CRON_JOB") | crontab -
        echo "Cron job updated successfully!"
    else
        echo "Keeping existing cron job."
        exit 0
    fi
else
    # Add new cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Cron job added successfully!"
fi

echo ""
echo "Current crontab:"
crontab -l

echo ""
echo "Backup will run at 02:00 every night."
echo "Logs will be written to: $LOG_FILE"
echo ""
echo "To test the backup manually, run:"
echo "  $BACKUP_SCRIPT"
echo ""
echo "To view logs:"
echo "  tail -f $LOG_FILE"
