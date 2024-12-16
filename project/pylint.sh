#!/bin/bash

# Runs Pylint-Flask locally

pylintFlask () {
	pylint --load-plugins pylint_flask_sqlalchemy pylint_flask $(git ls-files -- '*.py' ':!:migrations/')
}

pylintFlask
