import argparse
from collections import deque
import heapq

class Node:
    def __init__(self, state, g, parent, heuristic_value=0.0):
        self.state = state
        self.g = g
        self.parent = parent
        self.heuristic_value = heuristic_value
    
    def __lt__(self, other):
        return self.g + self.heuristic_value < other.g + other.heuristic_value

def print_search_result(found_solution: bool, n: Node, closed: set):
    if not found_solution:
        print(f"[FOUND_SOLUTION]: no")
        return
    
    total_cost = n.g
    path = []
    while n is not None:
        path.append(n.state)
        n = n.parent
    
    print(f"[FOUND_SOLUTION]: yes")
    print(f"[STATES_VISITED]: {len(closed)}")
    print(f"[PATH_LENGTH]: {len(path)}")
    print(f"[TOTAL_COST]: {total_cost}")
    print(f"[PATH]: {' => '.join(reversed(path))}")

def breadth_first_search(s0, succ, goal):
    open = deque([Node(s0, 0.0, None)])
    closed = set()

    n = None
    found_solution = False
    while open:
        n = open.popleft()
        if n.state in goal:
            found_solution = True
            break
        closed.add(n.state)

        for m in succ[n.state]:
            if m[0] not in closed:
                open.append(Node(m[0], n.g + m[1], n))
    
    return found_solution, n, closed

def uniform_cost_search(s0, succ, goal):
    open = [Node(s0, 0.0, None)]
    heapq.heapify(open)
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
    
    return found_solution, n, closed

def a_star_search(s0, succ, goal, h):
    open = [Node(s0, 0.0, None)]
    heapq.heapify(open)
    closed = set()

    n = None
    found_solution = False
    while open:
        n = heapq.heappop(open)
        if n.state in goal:
            found_solution = True
            break
        closed.add(n)

        for m in succ[n.state]:
            m_ = next(filter(
                lambda c: c.state == m[0],
                closed
            ), None)
            if m_ is None:
                m_ = next(filter(
                    lambda o: o.state == m[0],
                    open
                ), None)
            
            # if exists m' such that:
            if m_ is not None:
                if m_.g < n.g + m[1]: continue
                else:
                    if m_ in closed: closed.remove(m_)
                    else:
                        open.remove(m_)
                        heapq.heapify(open)
            
            heapq.heappush(open, Node(m[0], n.g + m[1], n, h[m[0]]))
    
    return found_solution, n, closed

def check_optimistic(succ, goal, h):
    conclusion = True

    for s in sorted(succ.keys()):
        _, n, _ = uniform_cost_search(s, succ, goal)
        h_star = n.g
        condition = h[s] <= h_star

        print(
                f"[CONDITION]: [{'OK' if condition else 'ERR'}] "
                f"h({s}) <= h*: "
                f"{h[s]} <= {h_star}"
            )

        conclusion &= condition

    print(f"[CONCLUSION]: Heuristic is {'' if conclusion else 'not '}optimistic.")

def check_consistent(succ, h):
    conclusion = True
    for s1 in sorted(succ.keys()):
        for s2, c in succ[s1]:
            condition = h[s1] <= h[s2] + c
            print(
                f"[CONDITION]: [{'OK' if condition else 'ERR'}] "
                f"h({s1}) <= h({s2}) + c: "
                f"{h[s1]} <= {h[s2]} + {c}"
            )
            conclusion &= condition
    
    print(f"[CONCLUSION]: Heuristic is {'' if conclusion else 'not '}consistent.")

def get_lines(file):
    with open(file) as f:
        return list(map(
            lambda l: l.strip(),
            filter(lambda line: line[0] != '#', f.readlines())
        ))

def input_state_space(ss):
    lines = get_lines(ss)

    succ = dict()
    
    s0 = lines[0]
    goal = set(lines[1].split())
    for line in lines[2:]:
        state, dests = line.split(':')

        succ[state] = []
        for dest in dests.split():
            s,d = dest.split(',')
            d = float(d)
            succ[state].append((s,d))
    
    return s0, succ, goal

def input_heuristic(h):
    lines = get_lines(h)

    heuristic = dict()
    for state, heuristic_value in map(lambda l: l.split(':'), lines):
        heuristic[state] = float(heuristic_value)

    return heuristic

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
    if args.h: h = input_heuristic(args.h)

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
    elif args.check_consistent:
        print(f"# HEURISTIC-CONSISTENT {args.h}")
        check_consistent(succ, h)

if __name__ == "__main__":
    main()