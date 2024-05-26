import argparse, numpy as np
from heapq import nsmallest
from itertools import islice
from random import random, sample

class NeuralNet:
    def __init__(self, layers: 'tuple[int]', init_weights=True):
        self.layers = layers
        self.mse = np.inf
        if not init_weights: return
        self.weights = [
            np.random.normal(0, 0.01, (layer, prev_layer))
            for prev_layer, layer in zip(layers, islice(layers, 1, None))
        ]
        self.biases = [
            np.random.normal(0, 0.01, layer)
            for layer in islice(layers, 1, None)
        ]
    
    def __lt__(self, other: 'NeuralNet'):
        return self.mse < other.mse
    
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

def evaluate(P: 'list[NeuralNet]', data: 'list[list[float]]'):
    for net in P:
        net.mse = sum((y - net.NN(x))**2 for *x, y in data) / len(data)

def cross(p1: NeuralNet, p2: NeuralNet):
    child = NeuralNet(p1.layers, False)
    child.weights = [(w1 + w2) / 2 for w1, w2 in zip(p1.weights, p2.weights)]
    child.biases = [(b1 + b2) / 2 for b1, b2 in zip(p1.biases, p2.biases)]

    return child

def genetic_algorithm(
        P: 'list[NeuralNet]', data: 'list[list[float]]',
        elitism: int, p: float, K: float, iter: int
    ):
    evaluate(P, data)
    for i in range(1, iter + 1):
        if i % 2000 == 0:
            print(f"[Train error @{i}]: {min(P).mse:.6f}")
        
        new_P = nsmallest(elitism, P)
        while len(new_P) < len(P):
            child = cross(*sample(P, 2))
            new_P.append(child)
        
        for net in new_P:
            for weight, bias in zip(net.weights, net.biases):
                weight += np.random.normal(0, K, size=weight.shape) * (random() < p)
                bias += np.random.normal(0, K, size=bias.shape) * (random() < p)

        P = new_P.copy()
        evaluate(P, data)
    return P

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
    P = genetic_algorithm(
        make_population(layers, args.popsize), train,
        args.elitism, args.p, args.K, args.iter
    )

    evaluate(P, test)
    print(f"[Test error]: {min(P).mse:.6f}")

if __name__ == "__main__":
    main()
