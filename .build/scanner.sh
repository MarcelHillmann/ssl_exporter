#!/usr/bin/env bash
[ -d reports ] && rm -rf reports
mkdir reports
[ ! -f .coverage ] && rm -rf .coverage
python3.7 --version
exit 99
pip3 install --user -r requirements.txt > /dev/null 2>&1
nosetests -c .build/nose.cfg
sonar-scanner
cat reports/junit.xml