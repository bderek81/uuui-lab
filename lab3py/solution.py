import argparse, csv
from collections import Counter
from math import inf, log2

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
            map(lambda x: (x, IG(D, x, y)), X),
            key=lambda x_ig: (-x_ig[1], x_ig[0])
        )
        print_information_gain(IG_Dx)
        x = IG_Dx[0][0]

        node = Node(x)
        for v in V(x, D):
            D_xv = list(filter(lambda row: row[x] == v, D))
            X_x = list(filter(lambda x_i: x_i != x, X))

            t = self.id3(D_xv, D, X_x, y, depth+1)
            node.subtrees.append((v, t))
        return node

    def fit(self, data: str):
        D = input_csv(data)
        fields = list(D[0].keys())
        X, y = sorted(fields[:-1]), fields[-1]

        self.tree = self.id3(D, D, X, y)
        print("[BRANCHES]:")
        print_branches(self.tree)
    
    @staticmethod
    def decide(tree: 'Leaf | Node', row: dict):
        if type(tree) == Leaf: return tree.value

        for v, t in tree.subtrees:
            if row[tree.feature] == v:
                return ID3.decide(t, row)

    def predict(self, data: str):
        D = input_csv(data)
        y = list(D[0].keys())[-1]
        
        labels = sorted(V(y, D))
        label_index = {l_i: i for i, l_i in enumerate(labels)}
        
        predictions = "[PREDICTIONS]:"
        correct, total = 0, len(D)
        confusion_matrix = [[0 for _ in labels] for _ in labels]
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
    return sorted(
        Counter(iterable).most_common(),
        key=lambda v_cnt: (-v_cnt[1], v_cnt[0])
    )[0][0]

def V(x: str, D: 'list[dict]'):
    return {row[x] for row in D}

def entropy(D: 'list[dict]', y: str):
    pmf_y = map(
        lambda cnt: cnt / len(D),
        Counter(row[y] for row in D).values()
    )

    return -sum(P_yi * log2(P_yi) for P_yi in pmf_y)

def IG(D: 'list[dict]', x: str, y: str):
    sigma = 0
    for v in V(x, D):
        D_xv = list(filter(lambda row: row[x] == v, D))
        sigma += len(D_xv) / len(D) * entropy(D_xv, y)
    
    return entropy(D, y) - sigma

def print_information_gain(IG_Dx: 'list[tuple[float, str]]'):
    print(' '.join(map(lambda x_ig: f"IG({x_ig[0]})={x_ig[1]:.4f}", IG_Dx)))

def print_branches(tree: 'Leaf | Node', string="", level=1):
    if type(tree) == Leaf:
        print(f"{string} {tree.value}")
        return
    
    for v, t in tree.subtrees:
        print_branches(t, ' '.join((string, f"{level}:{tree.feature}={v}")), level+1)

def print_confusion_matrix(confusion_matrix: 'list[list[int]]'):
    print("[CONFUSION_MATRIX]:")
    for row in confusion_matrix: print(*row)

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
