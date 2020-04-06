@echo off
nosetests -c nose.cfg
REM sonar > reports\scan.log 2>&1
rm -rf /.coverage