@echo off
set JMBAG=0036542918

set lab=1
mkdir autograder\solutions\%JMBAG%
zip -r autograder\solutions\%JMBAG%\%JMBAG%.zip lab%lab%py\*

cd autograder
python autograder.py lab%lab%
cd ..