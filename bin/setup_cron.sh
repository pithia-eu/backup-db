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
echo "Checking if all dependencies are installed"
for cmd in "${dependencies[@]}"
do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd is not installed or not in PATH" >&2
    exit 1
  fi
done

# Cron daemon checking
echo "Checking if cron daemon runs"
if ! pgrep cron >/dev/null 2>&1; then
  echo "Cron daemon is not running" >&2
  exit 1
fi

# Check if the directories exist and create them if they do not
echo "Checking if required directories exist"
for directory in "$DIR" "${SCRIPT_PATH%/*}" "${LOGFILE_PATH%/*}"; do
  if [ ! -d "$directory" ]; then
    echo "$directory does not exist. Creating now..."
    mkdir -p "$directory"
    if [ $? -ne 0 ]; then
      echo "Failed to create directory $directory." >&2
      exit 1
    fi
  fi
done

# Check if the backup script file exists
echo "Checking if the backup script exist"
if [ ! -f "$SCRIPT_PATH" ]; then
  echo "Backup script not found at $SCRIPT_PATH" >&2
  exit 1
fi

# Always set the backup script as executable
echo "Checking if the backup script at $SCRIPT_PATH is executable"
chmod +x "$SCRIPT_PATH"
if [ $? -ne 0 ]; then
  echo "Failed to set backup script as executable." >&2
  exit 1
fi

# Check if the log file exists, if not create it
echo "Checking if the the log file exist"
if [ ! -f "$LOGFILE_PATH" ]; then
  echo "Log file not found at $LOGFILE_PATH, creating now..."
  touch "$LOGFILE_PATH"
  if [ $? -ne 0 ]; then
    echo "Failed to create log file." >&2
    exit 1
  fi
fi

# Always set the log file as writable
echo "Checking if the log file at $LOGFILE_PATH is writable"
chmod +w "$LOGFILE_PATH"
if [ $? -ne 0 ]; then
  echo "Failed to set log file as writable." >&2
  exit 1
fi

# Check for existing cron job
echo "Checking if the  cron job exist"
croncmd="$SCRIPT_PATH >> $LOGFILE_PATH 2>&1"
cronjob="0 0 * * * $croncmd"
if ! (crontab -l 2>/dev/null | grep -Fq "$croncmd"); then
  echo "Adding cron job"
  (crontab -l 2>/dev/null ; echo "$cronjob") | crontab -
  if [ $? -ne 0 ]; then
    echo "Failed to add a cron job." >&2
    exit 1
  fi
fi

echo "Backuo cron job setup completed"