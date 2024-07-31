#!/bin/bash

echo "Setup to create virtual environment,"
echo "Install required python libraries."
echo "Can be rerun without any issues."
echo "---------------------------------------------------------------------------"

if [ -d ".env" ] && [ "$(ls -A .env)" ]; then
    echo ".env folder already exists and is not empty. Installing using pip"
else
    echo "Creating .env and installing using pip"
    python3 -m venv .env
fi

# Activate virtual environment
source .env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install packages
pip install -r requirements.txt

# Work done. Deactivate the virtual environment
deactivate
