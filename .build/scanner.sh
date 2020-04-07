#!/usr/bin/env bash
[ -d reports ] && rm -rf reports
mkdir reports
[ ! -f .coverage ] && rm -rf .coverage
alias python3=/usr/local/bin/python3.7
pip3.7 install --user -r requirements.txt > /dev/null 2>&1
nosetests -c .build/nose.cfg
sonar-scanner
cat reports/junit.xml