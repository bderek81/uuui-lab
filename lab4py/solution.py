import argparse, numpy as np
from heapq import nlargest
from itertools import islice

class NeuralNet:
    def __init__(self, layers: 'tuple[int]', init_weights=True):
        self.layers = layers
        self.mse = np.inf
        if not init_weights: return
        self.weights = [
            np.random.normal(0, 0.01, (prev_layer, layer))
            for prev_layer, layer in zip(layers, islice(layers, 1, None))
        ]
        self.biases = [
            np.random.normal(0, 0.01, layer)
            for layer in islice(layers, 1, None)
        ]
    
    def __lt__(self, other: 'NeuralNet'):
        return self.fit() < other.fit()
    
    def fit(self):
        return 1 / (max(self.mse, 1e-9))
    
    def NN(self, x):
        for i in range(len(self.weights)):
            x = x @ self.weights[i] + self.biases[i]
            if i == len(self.weights) - 1:
                break
            x = sigmoid(x)
        return x.T[0]

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def evaluate(net: NeuralNet, x, y):
    return np.mean(np.square(y - net.NN(x)))

def cross_mutate_evaluate(p1: NeuralNet, p2: NeuralNet, p: float, K: float, x, y):
    child = NeuralNet(p1.layers, False)
    child.weights = [
        (w1 + w2) / 2 + \
            np.random.normal(0, K, w1.shape) * np.random.binomial(1, p, w1.shape)
        for w1, w2 in zip(p1.weights, p2.weights)
    ]
    child.biases = [
        (b1 + b2) / 2 + \
            np.random.normal(0, K, b1.shape) * np.random.binomial(1, p, b1.shape)
        for b1, b2 in zip(p1.biases, p2.biases)
    ]
    child.mse = evaluate(child, x, y)

    return child

def select(P: 'list[NeuralNet]', size: int, p_sel: 'list[float]'):
    return np.random.choice(P, size, False, p_sel)

def genetic_algorithm(
        P: 'list[NeuralNet]', x, y,
        elitism: int, p: float, K: float, iter: int
    ):
    for net in P: net.mse = evaluate(net, x, y)
    for i in range(1, iter + 1):
        new_P = nlargest(elitism, P)

        sigma = sum(net.fit() for net in P)
        p_sel = [net.fit() / sigma for net in P]
        new_P.extend(
            cross_mutate_evaluate(*select(P, 2, p_sel), p, K, x, y)
            for _ in range(len(P) - elitism)
        )

        P = new_P

        if i % 2000 == 0:
            print(f"[Train error @{i}]: {max(P).mse:.6f}")
    return max(P)

def make_population(layers: 'tuple[int]', popsize: int):
    return [NeuralNet(layers) for _ in range(popsize)]

def input_csv(file: str):
    x_y = np.array([
        list(map(float, line.split(',')))
        for line in islice(open(file), 1, None)
    ])

    return x_y[:,:-1], x_y[:,-1]

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

    np.random.seed(3)
    x_train, y_train = input_csv(args.train)
    x_test, y_test = input_csv(args.test)

    layers = len(x_train[0]), *map(int, args.nn[:-1].split('s')), 1
    net = genetic_algorithm(
        make_population(layers, args.popsize), 
        x_train, y_train, args.elitism, 
        args.p, args.K, args.iter
    )
    print(f"[Test error]: {evaluate(net, x_test, y_test):.6f}")

if __name__ == "__main__":
    main()
