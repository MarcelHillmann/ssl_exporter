@echo off
nosetests -c nose.cfg
sonar
REM > reports\scan.log 2>&1