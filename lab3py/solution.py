import argparse, csv
from math import inf, log2
from collections import Counter

class Leaf:
    def __init__(self, value: str):
        self.value = value

class Node:
    def __init__(self, feature: str):
        self.feature = feature
        self.subtrees = []

class ID3:
    def __init__(self, id3_depth: int):
        self.depth = id3_depth
    
    def id3(self, 
        D: 'list[dict]', D_parent: 'list[dict]',
        X: 'list[str]', y: str, depth=1
    ):
        if depth > self.depth:
            v = most_common(row[y] for row in D)
            return Leaf(v)

        if not D:
            v = most_common(row[y] for row in D_parent)
            return Leaf(v)
        
        v = most_common(row[y] for row in D)
        if not X or all(map(lambda row: row[y] == v, D)):
            return Leaf(v)
        
        IG_Dx = sorted(
            map(lambda x: (IG(D, x, y), x), X),
            key=lambda ig_x: (-ig_x[0], ig_x[1])
        )
        print_information_gain(IG_Dx)
        x = IG_Dx[0][1]

        node = Node(x)
        V_x = {row[x] for row in D}
        for v in V_x:
            D_xv = list(filter(lambda row: row[x] == v, D))
            X_x = list(filter(lambda x_i: x_i != x, X))
            t = self.id3(D_xv, D, X_x, y, depth+1)
            node.subtrees.append((v, t))
        return node

    def fit(self, train_dataset: str):
        D = input_csv(train_dataset)
        fields = list(D[0].keys())
        X, y = sorted(fields[:-1]), fields[-1]

        self.tree = self.id3(D, D, X, y)
        print("[BRANCHES]:")
        print_branches(self.tree)
    
    @staticmethod
    def decide(tree: 'Leaf | Node', row: dict):
        if type(tree) == Leaf:
            return tree.value

        for v, t in tree.subtrees:
            if row[tree.feature] == v:
                return ID3.decide(t, row)

    def predict(self, test_dataset: str):
        D = input_csv(test_dataset)
        y = list(D[0].keys())[-1]
        
        labels = sorted({row[y] for row in D})
        confusion_matrix = [[0 for _ in labels] for _ in labels]
        label_index = {l_i: i for i, l_i in enumerate(labels)}
        
        predictions = "[PREDICTIONS]:"
        correct, total = 0, len(D)
        for row in D:
            decision = ID3.decide(self.tree, row)
            if decision is None:
                decision = most_common(row[y] for row in D)
            
            predictions += f" {decision}"
            correct += decision == row[y]
            confusion_matrix[label_index[row[y]]][label_index[decision]] += 1
        
        print(predictions)
        print(f"[ACCURACY]: {correct / total:.5f}")
        print_confusion_matrix(confusion_matrix)

def most_common(iterable):
    e_cnt = Counter(iterable).most_common()
    return sorted(filter(lambda z: z[1] == e_cnt[0][1], e_cnt))[0][0]

def entropy(D: 'list[dict]', y: str):
    pmf_y = map(
        lambda cnt: cnt / len(D),
        Counter(row[y] for row in D).values()
    )

    return -sum(P_yi * log2(P_yi) for P_yi in pmf_y)

def IG(D: 'list[dict]', x: str, y: str):
    sum = 0
    V_x = {row[x] for row in D}
    for v in V_x:
        D_xv = list(filter(lambda row: row[x] == v, D))
        sum += len(D_xv) * entropy(D_xv, y)
    
    return entropy(D, y) - sum / len(D)

def print_information_gain(IG_Dx: 'list[tuple[float, str]]'):
    print(' '.join(map(lambda ig_x: f"IG({ig_x[1]})={ig_x[0]:.4f}", IG_Dx)))

def print_branches(tree: 'Leaf | Node', string="", level=1):
    if type(tree) == Leaf:
        print(f"{string} {tree.value}")
        return
    
    for v, t in tree.subtrees:
        print_branches(t, ' '.join((string, f"{level}:{tree.feature}={v}")), level+1)

def print_confusion_matrix(confusion_matrix: 'list[list[int]]'):
    print("[CONFUSION_MATRIX]:")
    for row in confusion_matrix:
        print(*row)

def input_csv(file: str) -> 'list[dict]':
    return [row for row in csv.DictReader(open(file))]

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
