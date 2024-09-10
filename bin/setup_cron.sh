#!/bin/bash

# Project directory
DIR="/home/ubuntu/backup-db"

# Path to the script
SCRIPT_PATH="$DIR/bin/backup_db.sh"

# Path to the log file
LOGFILE_PATH="$DIR/log/backup_db.log"

# Fail fast if crontab is not installed
if ! command -v crontab >/dev/null 2>&1; then
  echo "Crontab is not installed or not in PATH" >&2
  exit 1
fi

# Check for cron daemon running
if ! pgrep cron >/dev/null 2>&1; then
  echo "Cron daemon is not running" >&2
  exit 1
fi

# Check if the directories exist and create them if they do not
for directory in "$DIR" "${SCRIPT_PATH%/*}" "${LOGFILE_PATH%/*}"; do
  if [ ! -d "$directory" ]; then
    echo "$directory does not exist. Creating now..."
    mkdir -p "$directory"
  fi
done

# Check if the backup script file exists
if [ ! -f "$SCRIPT_PATH" ]; then
  echo "Backup script not found at $SCRIPT_PATH" >&2
  exit 1
fi

# Check if the backup script is executable
if [ ! -x "$SCRIPT_PATH" ]; then
  echo "Backup script at $SCRIPT_PATH is not executable" >&2
  chmod +x "$SCRIPT_PATH"
fi

# Check if the log file exists, if not create it
if [ ! -f "$LOGFILE_PATH" ]; then
  echo "Log file not found at $LOGFILE_PATH, creating now..."
  touch "$LOGFILE_PATH"
fi

# Check if the log file is writable
if [ ! -w "$LOGFILE_PATH" ]; then
  echo "Log file at $LOGFILE_PATH is not writable, changing permissions now..."
  chmod +w "$LOGFILE_PATH"
fi

# Check for existing cron job
if crontab -l 2>/dev/null | grep -q "$SCRIPT_PATH >> $LOGFILE_PATH 2>&1"; then
    echo "Cron job already exists"
else
    echo "Adding cron job"
    (crontab -l 2>/dev/null ; echo "0 0 * * * $SCRIPT_PATH >> $LOGFILE_PATH 2>&1") | crontab -
fi