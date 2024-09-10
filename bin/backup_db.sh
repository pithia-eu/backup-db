#!/bin/bash

# The name of the venv
VENV_NAME=venv

# Explicitly select Python version
PYTHON_VERSION=python3.9
echo "Python version is: $PYTHON_VERSION"

# Navigate to project directory and exit if it fails
cd /home/ubuntu/backup-db || exit

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
        exit
    fi
else
    echo "Virtual environment doesn't exist. Stop execution."
    exit
fi

# Start DB backup
"$PYTHON_VERSION" "source/backup.py"

if [ $? -eq 0 ]
then
    echo "Backup executed successfully."
else
    echo "Failed to execute backup. Stop execution."
    exit
fi