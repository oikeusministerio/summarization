#!/bin/bash

if [ "$1" = "prod" ]
then
    docker build -t extractive .
    docker run extractive
else
    python3.5 -m pip install --user -r requirements.txt
    flaskswagger server:app --out-dir static/
fi
