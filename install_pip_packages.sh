#!/usr/bin/env bash
unzip -o packages.zip -d packages
python3.6 -m pip install --no-index --find-links packages -r requirements_prod.txt