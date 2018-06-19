#!/bin/bash

if [ "$1" = "prod" ]
then
    docker build -t extractive .
    docker run -d -p 5000:5000 extractive
else
    python3 -m pip install --user -r requirements.txt
    python3 server.py
fi
