#!/bin/bash

 # This will make script fail on first error
set -euo pipefail

# Project directory
DIR="/home/ubuntu/backup-db"

# Path to the script
SCRIPT_PATH="$DIR/bin/backup_db.sh"

# Path to the log file
LOGFILE_PATH="$DIR/log/backup_db.log"

# List of commands which our script is dependent on
declare -a dependencies=("crontab" "mkdir" "touch" "pgrep" "chmod")

# Check for dependencies
for cmd in "${dependencies[@]}"
do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd is not installed or not in PATH" >&2
    exit 1
  fi
done

# Crontab and Cron daemon checking
if ! command -v crontab >/dev/null 2>&1; then
  echo "Crontab is not installed or not in PATH" >&2
  exit 1
fi
if ! pgrep cron >/dev/null 2>&1; then
  echo "Cron daemon is not running" >&2
  exit 1
fi

# Check if the directories exist and create them if they do not
for directory in "$DIR" "${SCRIPT_PATH%/*}" "${LOGFILE_PATH%/*}"; do
  if [ ! -d "$directory" ]; then
    echo "$directory does not exist. Creating now..."
  fi
  mkdir -p "$directory"
done

# Check if the backup script file exists
if [ ! -f "$SCRIPT_PATH" ]; then
  echo "Backup script not found at $SCRIPT_PATH" >&2
  exit 1
fi

# Always set the backup script as executable
echo "Ensure backup script at $SCRIPT_PATH is executable"
chmod +x "$SCRIPT_PATH"

# Check if the log file exists, if not create it
if [ ! -f "$LOGFILE_PATH" ]; then
  echo "Log file not found at $LOGFILE_PATH, creating now..."
fi
touch "$LOGFILE_PATH"

# Always set the log file as writable
echo "Ensure log file at $LOGFILE_PATH is writable"
chmod +w "$LOGFILE_PATH"

# Check for existing cron job
croncmd="$SCRIPT_PATH >> $LOGFILE_PATH 2>&1"
cronjob="0 0 * * * $croncmd"
if ! (crontab -l 2>/dev/null | grep -Fq "$croncmd"); then
  echo "Adding cron job"
  (crontab -l 2>/dev/null ; echo "$cronjob") | crontab -
fi