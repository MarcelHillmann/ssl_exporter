#!/usr/bin/env bash
pip install --user nose nose-cover3
nosetests -c nose.cfg
sonar-scanner