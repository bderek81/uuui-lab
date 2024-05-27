@echo off
copy lab4py\solution.py extra_lab4 /y
cd extra_lab4

@echo on
python solution.py --train sine_train.txt --test sine_test.txt --nn 5s --popsize 10 --elitism 1 --p 0.1 --K 0.1 --iter 10000
python solution.py --train sine_train.txt --test sine_test.txt --nn 20s --popsize 20 --elitism 1 --p 0.7 --K 0.1 --iter 10000

python solution.py --train rastrigin_train.txt --test rastrigin_test.txt --nn 5s --popsize 10 --elitism 1 --p 0.3 --K 0.5 --iter 10000
python solution.py --train rastrigin_train.txt --test rastrigin_test.txt --nn 20s --popsize 20 --elitism 1 --p 0.1 --K 0.5 --iter 10000

python solution.py --train rosenbrock_train.txt --test rosenbrock_test.txt --nn 5s --popsize 10 --elitism 1 --p 0.5 --K 4. --iter 10000
python solution.py --train rosenbrock_train.txt --test rosenbrock_test.txt --nn 5s5s --popsize 20 --elitism 1 --p 0.5 --K 1. --iter 10000
python solution.py --train rosenbrock_train.txt --test rosenbrock_test.txt --nn 20s --popsize 20 --elitism 3 --p 0.5 --K 10. --iter 10000

@echo off
cd ..
