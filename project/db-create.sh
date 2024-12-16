#!/bin/bash

create () {
  rm -rf migrations/
  rm app.db

  flask db init
  flask db migrate -m "Initial migration"
  flask db upgrade
}

create