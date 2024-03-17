import argparse

class Node:
    def __init__(self, state, depth):
        self.state = state
        self.depth = depth

def breadthFirstSearch(s0, succ, goal):
    pass

def uniformCostSearch(s0, succ, goal):
    pass

def aStarSearch(s0, succ, goal, h):
    pass

def input_state_space(path_to_ss):
    with open(f"files/{path_to_ss}") as ss_file:
        lines = list(filter(lambda x: x[0] != '#', ss_file.readlines()))
    
    s0 = lines[0]
    goal = set(lines[1].split())

    succ = dict()
    for line in lines[2:]:
        state, dests = line.split(':')

        succ[state] = []
        for dest in dests.split():
            s,d = dest.split(',')
            succ[state].append((s,d))
    
    return s0, succ, goal

def input_heuristic(path_to_h):
    return None

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--alg")
    parser.add_argument("--ss")
    parser.add_argument("--h")
    parser.add_argument("--check-optimistic", action="store_true")
    parser.add_argument("--check-consistent", action="store_true")
    
    return parser.parse_args()

def main():
    args = parse_arguments()

    s0, succ, goal = input_state_space(args.ss)

    if args.h:
        h = input_heuristic(args.h)

    if args.alg == "bfs":
        breadthFirstSearch(s0, succ, goal)
    elif args.alg == "ucs":
        uniformCostSearch(s0, succ, goal)
    elif args.alg == "astar":
        aStarSearch(s0, succ, goal, h)

if __name__ == "__main__":
    main()