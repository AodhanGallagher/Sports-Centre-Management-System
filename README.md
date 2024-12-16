# COMP2931 Software Engineering Project

## Installation

### Dependencies / Pre-requisites
- Anaconda (Conda package manager)
- Python (Any Python interpreter)
- Bash / Zsh shell


Clone repository or download release from release page:

```
https://github.com/uol-feps-soc-comp2913-2223s2-classroom/project-squad08.git
```

Run installation script.
This will transition you to a Python 3.6.13 virtual environment as well as set environment variables for Flask.

```
chmod 755 install.sh
source install.sh
```

To run the project, go to the app directory and run the Flask application
```
cd app/
flask run
```

### Debugging installation issues

The primary issue you may encounter will be due to the virtual environment.
If the Flask app fails to run, you may not be in this environment. To check, follow the below commands:
```
python3 --version
```
You should see Python version 3.6.13

When in the interpreter, to check if Flask is recognised, type the following command:
```
from flask import Flask
```
You should see no errors. If there is, you may need to re-run the installation script.

## Running the project
Go to the project directory and run the Flask application
```
cd project/
flask run
```

This will start the Flask server. To view the website, go to this URL on your browser of choice
```
http://127.0.0.1:5000/login
```
If this doesn't work, please check the flask.log file in the project directory.

## Development Team
- Mayur
- Connor
- Alex
- Jibran
- Kieran
- Aodhan
