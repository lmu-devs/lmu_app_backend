#!/bin/bash

# Configuration
BACKUP_DIR="/root/backups"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="lmu_app_backup_$DATE.sql"
COMPRESSED_FILE="$BACKUP_FILE.gz"

# Load environment variables
source .env

# Ensure backup directory exists
mkdir -p $BACKUP_DIR

# Create PostgreSQL dump
echo "Creating database backup..."
PGPASSWORD=$POSTGRES_PASSWORD pg_dump \
    -h localhost \
    -p 5432 \
    -U $POSTGRES_USER \
    $POSTGRES_DB > "$BACKUP_DIR/$BACKUP_FILE"

# Compress the backup
echo "Compressing backup..."
gzip -f "$BACKUP_DIR/$BACKUP_FILE"

# Upload to Google Drive using rclone
echo "Uploading to Google Drive..."
rclone copy "$BACKUP_DIR/$COMPRESSED_FILE" lmu_app_backend_gdrive:lmu_app_backups/

# Clean up local backups older than 7 days
echo "Cleaning up old local backups..."
find $BACKUP_DIR -type f -name "lmu_app_backup_*.sql.gz" -mtime +7 -exec rm {} \;

# Clean up remote backups older than 30 days using rclone
echo "Cleaning up old remote backups..."
rclone delete --min-age 30d lmu_app_backend_gdrive:lmu_app_backups/

echo "Backup completed successfully!"