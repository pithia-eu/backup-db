#!/bin/bash

# The name of then venv
VENV_NAME=venv

# Store the found Python versions in an array
mapfile -t VERSIONS < <(/usr/bin/env -i bash -c "compgen -c python" | grep -E '^python[2-3].[0-9]+$' | sort -V)

# Select the latest version
PYTHON_VERSION=${VERSIONS[-1]}
echo "Python version is: $PYTHON_VERSION"

# Navigate to project directory and exit if it fails
cd /home/ubuntu/backup-db || exit

# Activate the venv
source $VENV_NAME/bin/activate

# Check if activation was successful
if [ $? -eq 0 ]
then
  echo "Virtual environment activated successfully."
else
  echo "Failed to activate virtual environment. Stop execution."
  exit
fi

# Start DB backup
$PYTHON_VERSION source/backup.py