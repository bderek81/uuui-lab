@echo off
set JMBAG=0036542918

set lab=1
set grader=autograder

mkdir %grader%\solutions\%JMBAG%
zip -r %grader%\solutions\%JMBAG%\%JMBAG%.zip lab%lab%py

cd %grader%
echo grader: %grader%
python autograder.py lab%lab%
cd ..