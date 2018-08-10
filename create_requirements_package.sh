#!/usr/bin/env bash
#pkg-resources is a bug in linux
pip freeze | grep -v "pkg-resources" > requirements_prod.txt
pip download -r requirements_prod.txt -d ./packages
if [ -d packages ]; then
	cd packages
	find . -name "*.pyc" -delete
	find . -name "*.egg-info" | xargs rm -rf
	zip -9mrv packages.zip .
	mv packages.zip ..
	cd ..
	rm -rf packages
fi
