#! /bin/sh
echo "Setup to run virtual environment,"
echo "Run the app"
echo "Can be rerun without any issues."
echo "---------------------------------------------------------------------------"

if [ -d ".env" ];
then
	echo "Enabling virtual environment"
else
	echo ".env file not found. Please run local_setup.sh first."
	exit N
fi

# Activate virtual environment
. .env/bin/activate

# Run the python file
export ENV=development
python3 app.py

# Work done. Deactivate the virtual environment
deactivate
