import argparse, csv
from math import inf, log2
from collections import Counter

class Leaf:
    def __init__(self, value: str):
        self.value = value

class Node:
    def __init__(self, feature: str, subtrees: 'list[Node]'=None):
        self.feature = feature
        self.subtrees = subtrees if subtrees else []

class ID3:
    def __init__(self, id3_depth: int):
        self.depth = id3_depth
    
    def id3(self, D, D_parent, X: 'list[str]', y: str, depth=0):
        if depth > self.depth:
            return None
        
        if not D:
            v = Counter(row[y] for row in D_parent).most_common(1)[0][0]
            return Leaf(v)
        
        v = Counter(row[y] for row in D).most_common(1)[0][0]
        if not X or all(map(lambda row: row[y]==v, D)):
            return Leaf(v)
        
        x, max = None, -inf
        igs = []
        for x_i in X:
            ig_x = information_gain(D, x_i, y)
            igs.append((x_i, ig_x))
            if ig_x > max:
                x, max = x_i, ig_x
        print(' '.join(map(lambda z: f"IG({z[0]})={z[1]:.4f}", sorted(igs, key=lambda znj: znj[1], reverse=True))))

        V_x = Counter(row[x] for row in D).most_common()
        subtrees = []
        for v, _ in V_x:
            X_cpy = X.copy()
            X_cpy.remove(x)
            t = self.id3(list(filter(lambda row: row[x]==v, D)), D, X_cpy, y, depth+1)
            subtrees.append((v, t)) if t is not None else None
        return Node(x, subtrees)

    def fit(self, train_dataset: str):
        D = input_csv(train_dataset)
        
        fields = list(D[0].keys())
        X, y = sorted(fields[:-1]), fields[-1]
        self.decision_tree = self.id3(D, D, X, y)
        print(f"[BRANCHES]:")
        ID3.print_branches(self.decision_tree)
    
    @staticmethod
    def print_branches(decision_tree: 'Leaf | Node', string: str="", level=1):
        if type(decision_tree) == Leaf:
            print(f"{string} {decision_tree.value}")
            return
        
        for v, t in decision_tree.subtrees:
            string_cpy = string
            string += f"{' ' if level>1 else ''}{level}:{decision_tree.feature}={v}"
            ID3.print_branches(t, string, level+1)
            string = string_cpy
    
    @staticmethod
    def decide(decision_tree: 'Leaf | Node', row: dict):
        if type(decision_tree) == Leaf:
            return decision_tree.value

        for v, t in decision_tree.subtrees:
            if row[decision_tree.feature]==v:
                return ID3.decide(t, row)

    def predict(self, test_dataset: str):
        D = input_csv(test_dataset)
        y = list(D[0].keys())[-1]
        
        labels = sorted({row[y] for row in D})
        confusion_matrix = [[0 for _ in labels] for _ in labels]
        index_dict = {x: i for i, x in enumerate(labels)}
        
        correct, total = 0, len(D)
        predictions = "[PREDICTIONS]:"
        for row in D:
            decision = ID3.decide(self.decision_tree, row)
            if decision is None:
                decision = sorted(Counter(row[y] for row in D).most_common(), key=lambda z: z[0])[0][0]
            
            correct += decision==row[y]
            confusion_matrix[index_dict[row[y]]][index_dict[decision]] += 1
            predictions += f" {decision}"
        print(predictions)
        print(f"[ACCURACY]: {correct / total:.5f}")
        print_confusion_matrix(confusion_matrix)

def entropy(D: list, y: str):
    K = Counter(row[y] for row in D).most_common()

    return -sum(i/len(D) * log2(i/len(D)) for _, i in K)

def information_gain(D: list, x: str, y: str):
    V_x = Counter(row[x] for row in D).most_common()
    sum = 0
    for v, _ in V_x:
        D_xv = list(filter(lambda row: row[x]==v, D))
        sum += len(D_xv) * entropy(D_xv, y)
    
    return entropy(D, y) - sum / len(D)

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
