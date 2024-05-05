import argparse, csv, math

class ID3:
    def fit(train_dataset):
        pass

    def predict(test_dataset):
        pass

def input_csv(csvfile: str):
    with open(csvfile) as csvfile:
        dict_reader = csv.DictReader(csvfile)

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("train_data")
    parser.add_argument("test_data")
    parser.add_argument("id3_depth", type=int, nargs='?', default=float("inf"))
    
    return parser.parse_args()

def main():
    args = parse_arguments()

if __name__ == "__main__":
    main()
