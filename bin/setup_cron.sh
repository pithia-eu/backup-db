#!/bin/bash

# Path to the script
SCRIPT_PATH="/home/ubuntu/backup-db/bin/backup_db.sh"

# Path to the log file
LOGFILE_PATH="/home/ubuntu/backup-db/log/backup_db.log"

# Add the cron job
(crontab -l ; echo "0 0 * * * $SCRIPT_PATH >> $LOGFILE_PATH 2>&1") | crontab -