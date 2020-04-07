#!/usr/bin/env bash
pip3 install --user -r requirements.txt &&\
mkdir reports &&\
nosetests -c .build/nose.cfg &&\
sonar-scanner
ls -AlhX