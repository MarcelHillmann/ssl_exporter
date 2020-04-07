#!/usr/bin/env bash
pip3 install --user nose nose-cover3
nosetests -c .build/nose.cfg
sonar-scanner