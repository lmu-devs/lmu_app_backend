#!/bin/bash

set -e

# Configuration
BACKUP_DIR="/root/backups"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="lmu_app_backup_$DATE.sql"
COMPRESSED_FILE="$BACKUP_FILE.gz"
RCLONE_REMOTE="backend-sync"
RCLONE_PATH="lmu_app_backups"
RCLONE_CONFIG="/root/.config/rclone/rclone.conf"
RETENTION_DAYS=7

# Script directory for loading .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment variables
if [ -f "$PROJECT_DIR/.env" ]; then
    source "$PROJECT_DIR/.env"
else
    echo "Error: .env file not found at $PROJECT_DIR/.env"
    exit 1
fi

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Create PostgreSQL dump from Docker container
echo "[$(date)] Starting database backup..."
echo "Using Docker container 'db_cms' for backup..."
docker exec db_cms pg_dump \
    -U "$POSTGRES_USER" \
    "$POSTGRES_DB" > "$BACKUP_DIR/$BACKUP_FILE"

# Check if backup was created successfully
if [ ! -s "$BACKUP_DIR/$BACKUP_FILE" ]; then
    echo "Error: Backup file is empty or was not created"
    exit 1
fi

# Compress the backup
echo "[$(date)] Compressing backup..."
gzip -f "$BACKUP_DIR/$BACKUP_FILE"

# Upload to Google Drive using rclone
echo "[$(date)] Uploading to Google Drive..."
rclone --config "$RCLONE_CONFIG" copy "$BACKUP_DIR/$COMPRESSED_FILE" "$RCLONE_REMOTE:$RCLONE_PATH/" --progress

# Clean up local backups older than retention period
echo "[$(date)] Cleaning up old local backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -type f -name "lmu_app_backup_*.sql.gz" -mtime +$RETENTION_DAYS -exec rm -v {} \;

# Clean up remote backups older than retention period using rclone
echo "[$(date)] Cleaning up old remote backups (older than $RETENTION_DAYS days)..."
rclone --config "$RCLONE_CONFIG" delete --min-age "${RETENTION_DAYS}d" "$RCLONE_REMOTE:$RCLONE_PATH/" --verbose

echo "[$(date)] Backup completed successfully!"
echo "Backup file: $COMPRESSED_FILE"