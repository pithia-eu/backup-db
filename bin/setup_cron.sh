#!/bin/bash

# Path to the script
SCRIPT_PATH="/home/ubuntu/backup-db/bin/backup_db.sh"

# Path to the log file
LOGFILE_PATH="/home/ubuntu/backup-db/log/backup_db.log"

# Check if the backup script file exists
if [ ! -f "$SCRIPT_PATH" ]; then
  echo "Backup script not found at $SCRIPT_PATH"
  exit 1
fi

# Check if the backup script is executable
if [ ! -x "$SCRIPT_PATH" ]; then
  echo "Backup script at $SCRIPT_PATH is not executable"
  exit 1
fi

# Check if the log file exists
if [ ! -f "$LOGFILE_PATH" ]; then
  echo "Log file not found at $LOGFILE_PATH"
  exit 1
fi

# Check if the log file is writable
if [ ! -w "$LOGFILE_PATH" ]; then
  echo "Log file at $LOGFILE_PATH is not writable"
  exit 1
fi

# Check for existing cron job
if crontab -l 2>/dev/null | grep -q "$SCRIPT_PATH >> $LOGFILE_PATH 2>&1"; then
    echo "Cron job already exists"
else
    echo "Adding cron job"
    (crontab -l 2>/dev/null ; echo "0 0 * * * $SCRIPT_PATH >> $LOGFILE_PATH 2>&1") | crontab -
fi