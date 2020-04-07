#!/usr/bin/env bash
[ -d reports ] && rm -rf reports
mkdir reports
[ ! -f .coverage ] && rm -rf .coverage
pip3 install --user -r .build/requirements.txt # > /dev/null 2>&1
nosetests -c .build/nose.cfg
sonar-scanner
