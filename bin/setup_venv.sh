#!/bin/bash

# Name of the venv
VENV_NAME=venv

# Python version
PYTHON_VERSION=python3
echo "Python version is: $PYTHON_VERSION"

# Project directory
DIR="/home/ubuntu/backup-db"

# Requirements file
REQUIREMENTS=requirements.txt

# Check if the directory exists
if [ ! -d "$DIR" ]; then
  echo "Directory $DIR does not exist. Stopping execution."
  exit 1
fi

# Navigate to project directory
cd "$DIR" || {
  echo "Cannot navigate to directory $DIR. Stopping execution."
  exit 1
}


# check if requirements file exists
if [ ! -f "$REQUIREMENTS" ]; then
    echo "Requirements file not found!"
    exit 1
fi

# create a new venv if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    $PYTHON_VERSION -m venv $VENV_NAME
fi

# activate the venv
source $VENV_NAME/bin/activate

# Update pip to the latest version
$PYTHON_VERSION -m pip install --upgrade pip

# update the requirements
$PYTHON_VERSION -m pip install -r $REQUIREMENTS --upgrade

echo "Setup (or update) completed."