#!/usr/bin/env bash
[ ! -d reports ] && mkdir reports
pip3 install --user -r requirements.txt
nosetests -c .build/nose.cfg
sonar-scanner -X
ls -AlhX