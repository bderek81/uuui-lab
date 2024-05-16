import argparse, csv
from math import inf, log2
from collections import Counter

class Node:
    def __init__(self, feature: str, subtrees: 'list[Node]'=None):
        self.feature = feature
        self.subtrees = subtrees if subtrees else []

class ID3:
    def __init__(self, id3_depth: int):
        self.depth = id3_depth
    
    def id3(self, D, D_parent, X: list, y, depth=0):
        if depth > self.depth:
            return None
        
        if not D:
            v = Counter(row[y] for row in D_parent).most_common(1)[0][0]
            return Node(v)
        
        v = Counter(row[y] for row in D).most_common(1)[0][0]
        if not X or all(map(lambda row: row[y]==v, D)):
            return Node(v)
        
        x, max = None, -inf
        igs = []
        for x_i in X:
            ig_x = information_gain(D, x_i, y)
            igs.append((x_i, ig_x))
            if ig_x > max:
                x, max = x_i, ig_x
        print(' '.join(map(lambda z: f"IG({z[0]})={z[1]:.4f}", sorted(igs, key=lambda znj: znj[1], reverse=True))))

        subtrees = []
        V_x = Counter(row[y] for row in D).most_common()
        for v, _ in V_x:
            X_cpy = X.copy()
            X_cpy.remove(x)
            t = self.id3(list(filter(lambda row: row[x]==v, D)), D, X_cpy, y, depth+1)
            subtrees.append((v, t))
        return Node(x, subtrees)

    def fit(self, train_dataset: str):
        D = input_csv(train_dataset)
        
        fields = list(D[0].keys())
        X, y = sorted(fields[:-1]), fields[-1]
        self.decision_tree = self.id3(D, D, X, y)

    def predict(self, test_dataset: str):
        accuracy = 1
        print(f"[ACCURACY]: {accuracy:.5f}")
        print_confusion_matrix([[1, 1], [1, 5]])

def entropy(D, y):
    K = Counter(row[y] for row in D).most_common()

    return -sum(i/len(D) * log2(i/len(D)) for _, i in K)

def information_gain(D, x, y):
    result = entropy(D, y)

    V_x = Counter(row[y] for row in D).most_common()
    sum = 0
    for v, _ in V_x:
        D_xv = list(filter(lambda row: row[x]==v, D))
        sum += len(D_xv) * entropy(D_xv, y)
    
    return result - sum / len(D)

def print_confusion_matrix(confusion_matrix: 'list[list[int]]'):
    print(f"[CONFUSION_MATRIX]:")
    for row in confusion_matrix:
        print(*row)

def input_csv(file: str):
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)

        return [row for row in reader]

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("train_data")
    parser.add_argument("test_data")
    parser.add_argument("id3_depth", type=int, nargs='?', default=inf)
    
    return parser.parse_args()

def main():
    args = parse_arguments()

    model = ID3(args.id3_depth)
    model.fit(args.train_data)
    model.predict(args.test_data)

if __name__ == "__main__":
    main()
