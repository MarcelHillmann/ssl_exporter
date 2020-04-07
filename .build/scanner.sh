#!/usr/bin/env bash
[ -d reports ] && rm -rf reports
mkdir reports
[ ! -f .coverage ] && rm -rf .coverage
pip3 install --user -r requirements.txt
nosetests -c .build/nose.cfg
env
sleep 2s
sonar-scanner -X
ls -AlhX