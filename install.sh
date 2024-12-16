#!/bin/bash

setup () {

	conda activate py36
	conda init bash
	python3 -m venv penv
	source penv/bin/activate
	
	pip install --upgrade pip
	pip install -r requirements.txt
	echo "installed!"
}

environment () {
	export FLASK_APP=run.py
	export FLASK_ENV=development
}

setup
environment
