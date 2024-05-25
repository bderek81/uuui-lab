import argparse, numpy as np
from heapq import nsmallest
from itertools import islice
from random import random, sample

class NeuralNet:
    def __init__(self, layers: 'tuple[int]', init_wb=True):
        self.layers = layers
        self.weights = [None for _ in range(len(self.layers) - 1)]
        self.biases = [None for _ in range(len(self.layers) - 1)]
        self.init_weights_biases() if init_wb else None
        self.mse = np.inf
    
    def __lt__(self, other: 'NeuralNet'):
        return self.mse < other.mse
    
    def init_weights_biases(self):
        for i in range(len(self.weights)):
            self.weights[i] = np.random.normal(0, 0.01, (self.layers[i + 1], self.layers[i]))
            self.biases[i] = np.random.normal(0, 0.01, self.layers[i + 1])
    
    def NN(self, x: 'list[float]'):
        x = np.array(x)
        for i, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            x = np.matmul(weight, x) + bias
            if i == len(self.weights) - 1:
                break
            x = sigmoid(x)
        return x

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def evaluate(P: 'list[NeuralNet]', data: 'list[list[float]]'):
    for neural_net in P:
        neural_net.mse = sum(
            np.square(y - neural_net.NN(x))
            for *x, y in data
        ) / len(data)

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
    for i in range(iter):
        if (i + 1) % 2000 == 0:
            print(f"[Train error @{i + 1}]: {nsmallest(1, P)[0].mse[0]:.6f}")
        
        new_P = nsmallest(elitism, P)
        while len(new_P) < len(P):
            child = cross(*sample(P, 2))
            new_P.append(child)
        
        for neural_net in P:
            for weight, bias in zip(neural_net.weights, neural_net.biases):
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
    print(f"[Test error]: {nsmallest(1, P)[0].mse[0]:.6f}")

if __name__ == "__main__":
    main()
