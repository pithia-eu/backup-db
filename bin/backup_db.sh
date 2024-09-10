#!/bin/bash

# The name of the venv
VENV_NAME=venv

# Explicitly select Python version
PYTHON_VERSION=python3.9
echo "Python version is: $PYTHON_VERSION"

# Define your script's directory
DIR="/home/ubuntu/backup-db"

# Check if the directory exists
if [ ! -d "$DIR" ]; then
  echo "Directory $DIR does not exist. Stopping execution."
  exit 1
fi

# Navigate to project directory
cd "$DIR" || exit 1

# Check if the venv exists
if [ -d "$VENV_NAME" ]
then
    # Activate the venv
    source $VENV_NAME/bin/activate
    if type -a $PYTHON_VERSION >/dev/null 2>&1
    then
        echo "Virtual environment activated successfully."
    else
        echo "The required Python version doesn't exist in the virtual environment. Stop execution."
        exit 1
    fi
else
    echo "Virtual environment doesn't exist. Stop execution."
    exit 1
fi

# Define your backup script's path
BACKUP_SCRIPT="source/backup.py"

# Check if the backup script exists
if [ ! -f "$BACKUP_SCRIPT" ]; then
  echo "Backup script $BACKUP_SCRIPT does not exist. Stopping execution."
  exit 1
fi

# Start DB backup
if "$PYTHON_VERSION" "$BACKUP_SCRIPT"
then
    echo "Backup executed successfully."
else
    echo "Failed to execute backup. Stop execution."
    exit 1
fi