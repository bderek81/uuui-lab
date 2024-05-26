import argparse, numpy as np
from heapq import nlargest
from itertools import islice

class NeuralNet:
    def __init__(self, layers: 'tuple[int]', init_weights=True):
        self.layers = layers
        self.mse = np.inf
        if not init_weights: return
        self.weights = np.asarray([
            np.random.normal(0, 0.01, (layer, prev_layer))
            for prev_layer, layer in zip(layers, islice(layers, 1, None))
        ], dtype=object)
        self.biases = np.asarray([
            np.random.normal(0, 0.01, layer)
            for layer in islice(layers, 1, None)
        ], dtype=object)
    
    def __lt__(self, other: 'NeuralNet'):
        return self.fit() < other.fit()
    
    def fit(self):
        return 1 / (self.mse + 0.001)
    
    def NN(self, x: 'list[float]'):
        x = np.array(x)
        for i, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            x = weight @ x + bias
            if i == len(self.weights) - 1:
                break
            x = sigmoid(x)
        return x[0]

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def evaluate(net: NeuralNet, data: 'list[list[float]]'):
    return sum((y - net.NN(x))**2 for *x, y in data) / len(data)

def cross_mutate_evaluate(p1: NeuralNet, p2: NeuralNet, p: float, K: float, data: 'list[list[float]]'):
    child = NeuralNet(p1.layers, False)
    child.weights = (p1.weights + p2.weights) / 2 \
        + np.random.normal(0, K, p1.weights.shape) * np.random.binomial(1, p, p1.weights.shape)
    child.biases = (p1.biases + p2.biases) / 2  \
        + np.random.normal(0, K, p1.biases.shape) * np.random.binomial(1, p, p1.biases.shape)
    child.mse = evaluate(child, data)

    return child

def genetic_algorithm(
        P: 'list[NeuralNet]', data: 'list[list[float]]',
        elitism: int, p: float, K: float, iter: int
    ):
    for net in P:
        net.mse = evaluate(net, data)
    for i in range(1, iter + 1):
        if i % 2000 == 0:
            print(f"[Train error @{i}]: {max(P).mse:.6f}")
        
        sigma = sum(net.fit() for net in P)
        selection = [net.fit() / sigma for net in P]

        new_P = nlargest(elitism, P)
        new_P.extend(
            cross_mutate_evaluate(
                *np.random.choice(P, 2, False, selection), p, K, data
            )
            for _ in range(len(P) - elitism)
        )

        P = new_P.copy()
    return max(P)

def make_population(layers: 'tuple[int]', popsize: int):
    return [NeuralNet(layers) for _ in range(popsize)]

def input_csv(file: str):
    return [
        list(map(float, line.split(',')))
        for line in islice(open(file), 1, None)
    ]

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

    train = input_csv(args.train)
    test = input_csv(args.test)

    layers = len(train[0]) - 1, *map(int, args.nn[:-1].split('s')), 1
    net = genetic_algorithm(
        make_population(layers, args.popsize), train,
        args.elitism, args.p, args.K, args.iter
    )

    print(f"[Test error]: {evaluate(net, test):.6f}")

if __name__ == "__main__":
    main()
