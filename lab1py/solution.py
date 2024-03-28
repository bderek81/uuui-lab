import argparse
from collections import deque
import heapq
from math import isclose

class Node:
    def __init__(self, state: str, g: float, parent: 'Node', heuristic_value=0.0):
        self.state = state
        self.g = g
        self.parent = parent
        self.f = g + heuristic_value
    
    def __lt__(self, other: 'Node'):
        if isclose(self.f, other.f):
            return self.state < other.state
        
        return self.f < other.f

def print_search_result(found_solution: bool, states_visited: int, n: Node):
    print(f"[FOUND_SOLUTION]: {'yes' if found_solution else 'no'}")
    if not found_solution: return
    
    total_cost = n.g
    path = deque()
    while n is not None:
        path.appendleft(n.state)
        n = n.parent
    
    print(f"[STATES_VISITED]: {states_visited}")
    print(f"[PATH_LENGTH]: {len(path)}")
    print(f"[TOTAL_COST]: {total_cost:.1f}")
    print(f"[PATH]: {' => '.join(path)}")

def breadth_first_search(s0: str, succ: dict, goal: set):
    initial = Node(s0, 0.0, None)
    open = deque([initial])
    closed = set()

    n = None
    found_solution = False
    while open:
        n = open.popleft()
        if n.state in goal:
            found_solution = True
            break
        closed.add(n.state)

        for m in sorted(succ[n.state]):
            if m[0] not in closed:
                open.append(Node(m[0], n.g + m[1], n))
    
    return found_solution, len(closed), n

def uniform_cost_search(s0: str, succ: dict, goal: set):
    initial = Node(s0, 0.0, None)
    open = [initial]
    closed = set()

    n = None
    found_solution = False
    while open:
        n = heapq.heappop(open)
        if n.state in goal:
            found_solution = True
            break
        closed.add(n.state)

        for m in succ[n.state]:
            if m[0] not in closed:
                heapq.heappush(open, Node(m[0], n.g + m[1], n))
    
    return found_solution, len(closed), n

def a_star_search(s0: str, succ: dict, goal: set, h: dict):
    initial = Node(s0, 0.0, None, h[s0])
    open, open_dict = [initial], {initial.state: initial.g}
    closed = dict()

    n = None
    found_solution = False
    while open:
        n = heapq.heappop(open)
        open_dict.pop(n.state, None)
        if n.state in goal:
            found_solution = True
            break
        closed[n.state] = n.g

        for m in succ[n.state]:
            if m[0] in closed:
                if closed[m[0]] < n.g + m[1]: continue
                else: del closed[m[0]]
            if m[0] in open_dict:
                if open_dict[m[0]] < n.g + m[1]: continue
                else: del open_dict[m[0]]
            
            heapq.heappush(open, Node(m[0], n.g + m[1], n, h[m[0]]))
            open_dict[m[0]] = n.g + m[1]
    
    return found_solution, len(closed), n

def check_optimistic(succ: dict, goal: set, h: dict):
    conclusion = True
    for s in sorted(succ):
        _, _, n = uniform_cost_search(s, succ, goal)
        h_star = n.g
        condition = h[s] <= h_star

        print(
            f"[CONDITION]: [{'OK' if condition else 'ERR'}] "
            f"h({s}) <= h*: "
            f"{h[s]:.1f} <= {h_star:.1f}"
        )

        conclusion &= condition

    print(f"[CONCLUSION]: Heuristic is {'' if conclusion else 'not '}optimistic.")

def check_consistent(succ: dict, h: dict):
    conclusion = True
    for s1 in sorted(succ):
        for s2, c in succ[s1]:
            condition = h[s1] <= h[s2] + c

            print(
                f"[CONDITION]: [{'OK' if condition else 'ERR'}] "
                f"h({s1}) <= h({s2}) + c: "
                f"{h[s1]:.1f} <= {h[s2]:.1f} + {c:.1f}"
            )
            
            conclusion &= condition
    
    print(f"[CONCLUSION]: Heuristic is {'' if conclusion else 'not '}consistent.")

def lines(file):
    return (line.rstrip() for line in open(file) if line[0] != '#')

def input_state_space(lines):
    s0 = next(lines)
    goal = set(next(lines).split())
    succ = dict()
    for state, trans in map(lambda l: l.split(':'), lines):
        succ[state] = [
            (next_state, float(cost))
            for next_state,cost in map(lambda t: t.split(','), trans.split())
        ]
    
    return s0, succ, goal

def input_heuristic(lines):
    return {
        state: float(heuristic_value) 
        for state, heuristic_value in map(lambda l: l.split(':'), lines)
    }

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

    s0, succ, goal = input_state_space(lines(args.ss))
    if args.h: h = input_heuristic(lines(args.h))

    if args.alg == "bfs":
        print(f"# BFS")
        print_search_result(*breadth_first_search(s0, succ, goal))
    elif args.alg == "ucs":
        print(f"# UCS")
        print_search_result(*uniform_cost_search(s0, succ, goal))
    elif args.alg == "astar":
        print(f"# A-STAR {args.h}")
        print_search_result(*a_star_search(s0, succ, goal, h))
    
    if args.check_optimistic:
        print(f"# HEURISTIC-OPTIMISTIC {args.h}")
        check_optimistic(succ, goal, h)
    
    if args.check_consistent:
        print(f"# HEURISTIC-CONSISTENT {args.h}")
        check_consistent(succ, h)

if __name__ == "__main__":
    main()
