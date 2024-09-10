#!/bin/bash

# Set the name of your venv
VENV_NAME=venv

# Navigate to project directory
cd /home/ubuntu/backup-db

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

# Start DB back up
python backup_db.py