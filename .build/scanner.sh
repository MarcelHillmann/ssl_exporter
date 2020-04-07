#!/usr/bin/env bash
pip3 install --user -r requirements.txt
nosetests -c .build/nose.cfg
sonar-scanner