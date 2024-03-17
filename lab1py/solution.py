import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--alg")
    parser.add_argument("--ss")
    parser.add_argument("--h")
    parser.add_argument("--check-optimistic")
    parser.add_argument("--check-consistent")
    
    return parser.parse_args()

def main():
    args = parse_arguments()

if __name__ == "__main__":
    main()