import argparse, csv, numpy as np

def input_csv(file: str) -> 'list[dict]':
    return [row for row in csv.DictReader(open(file))]

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--train")
    parser.add_argument("--test")
    parser.add_argument("--nn")
    parser.add_argument("--popsize", type=int)
    parser.add_argument("--elitism", type=int)
    parser.add_argument("--p", type=float)
    parser.add_argument("--K", type=float)
    parser.add_argument("--iter", type=int)    
    
    return parser.parse_args()

def main():
    args = parse_arguments()

if __name__ == "__main__":
    main()
