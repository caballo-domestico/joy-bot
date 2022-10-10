#. venv/bin/activate

sudo apt-get install software-properties-common
sudo apt-add-repository universe
sudo apt-get update
sudo apt-get install python3-pip
pip install boto3
sudo apt install python3-flask
flask run
export FLASK_APP=app
export FLASK_ENV=development
flask run
