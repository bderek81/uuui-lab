import argparse
from collections import deque

class Clause:
    sep = " v "

    def __init__(self, raw_clause: str, sos=False, parents: 'tuple[Clause]' = None):
        self.literals = frozenset(raw_clause.split(Clause.sep))
        self.sos = sos
        self.nil = not raw_clause
        self.parents = parents
    
    def __repr__(self):
        return "NIL" if self.nil else Clause.sep.join(self.literals)
    
    def __eq__(self, other: 'Clause'):
        return self.literals == other.literals
    
    def __hash__(self):
        return hash(self.literals)
    
    def negation(self):
        return {Clause(negate(literal), True) for literal in self.literals}
    
    def is_tautology(self):
        for literal in self.literals:
            if negate(literal) in self.literals:
                return True

        return False

def negate(literal: str):
    return f"~{literal}" if literal[0] != '~' else literal[1:]

def remove_redundant(clauses: 'set[Clause]'):
    for c1 in clauses:
        redundant = False
        for c2 in clauses:
            if c2.literals < c1.literals:
                redundant = True
                break
        if redundant: continue
        yield c1

def remove_irrelevant(clauses: 'set[Clause]'):
    return set(filter(lambda clause: not clause.is_tautology(), clauses))

def select_clauses(clauses: 'set[Clause]'):
    visited = set()
    for c1 in clauses:
        visited.add(c1)
        for c2 in filter(lambda c: c not in visited, clauses):
            if not (c1.sos or c2.sos): continue

            for literal in c1.literals:
                if negate(literal) in c2.literals:
                    yield (c1, c2)
                    break

def resolve(c1: Clause, c2: Clause):
    c1_res_literals = set(c1.literals)

    res_by = None
    for lit in c1.literals:
        if negate(lit) in c2.literals:
            if res_by is not None: return None
            res_by = lit
            c1_res_literals.remove(res_by)
    
    c2_res_literals = set(c2.literals)
    c2_res_literals.remove(negate(res_by))
    
    raw_clause = Clause.sep.join(c1_res_literals.union(c2_res_literals))
    return Clause(raw_clause, True, (c1, c2))

def print_dashed_ln(len=15): print('=' * len)

def print_resolution_result(
    input_clauses: 'deque[Clause]',
    goal: Clause,
    resolvent: Clause,
):
    def indexed_clause(index: int, clause: Clause):
        indexed_clause = f"{index}. {clause}"
        if clause.parents:
            parent_index = sorted(map(lambda p: clause_index[p], clause.parents))
            indexed_clause += f" ({parent_index[0]}, {parent_index[1]})"
        return indexed_clause
    
    conclusion = resolvent is not None
    if not conclusion:
        for index, clause in enumerate(input_clauses, start=1):
            print(indexed_clause(index, clause))
    else:
        input_clauses = deque()
        goal_negation, goal_negation_clauses = goal.negation(), deque()
        other_clauses = deque()

        queue = deque([resolvent])
        while queue:
            clause = queue.popleft()
            if clause.parents:
                if not clause.nil: other_clauses.appendleft(clause)
                queue.extend(clause.parents)
            elif clause in goal_negation:
                goal_negation_clauses.appendleft(clause)
            else:
                input_clauses.appendleft(clause)
        
        input_clauses = deque(dict.fromkeys(input_clauses))
        goal_negation_clauses = deque(dict.fromkeys(goal_negation_clauses))
        other_clauses = deque(dict.fromkeys(other_clauses))
        
        input_clauses.extend(goal_negation_clauses)
        clause_index = {clause: i for i, clause in enumerate(input_clauses, 1)}
        next_i = len(clause_index) + 1
        clause_index.update({clause: i for i, clause in enumerate(other_clauses, next_i)})
        next_i = len(clause_index) + 1

        for clause in input_clauses:
            print(indexed_clause(clause_index[clause], clause))
        print_dashed_ln()
        for clause in other_clauses:
            print(indexed_clause(clause_index[clause], clause))
        print(indexed_clause(next_i, resolvent))
    print_dashed_ln()
    print(f"[CONCLUSION]: {goal} is {'true' if conclusion else 'unknown'}")

def resolution(clauses: 'set[Clause]', goal: Clause):
    input_clauses = deque(clauses)

    goal_negation = goal.negation()
    input_clauses.extend(goal_negation)
    clauses.update(goal_negation)

    clauses = set(remove_redundant(remove_irrelevant(clauses)))

    new = set()
    while True:
        for (c1, c2) in select_clauses(clauses):
            resolvent = resolve(c1, c2)
            if resolvent is not None:
                if resolvent.nil: return input_clauses, goal, resolvent
                new.add(resolvent)
        if new.issubset(clauses): return input_clauses, goal, None

        clauses.update(new)

def cooking(clauses: 'set[Clause]', user_cmds):
    print(f"Constructed with knowledge:")
    for clause in clauses:
        print(f"{clause}")

    for (clause, cmd) in user_cmds:
        print(f"User's command: {clause} {cmd}")

        if cmd == '?':
            print_resolution_result(*resolution(clauses.copy(), clause))
        elif cmd == '+':
            clauses.add(clause)
            print(f"Added {clause}")
        elif cmd == '-':
            clauses.remove(clause)
            print(f"removed {clause}")

def lines(file):
    return [line.rstrip().lower() for line in open(file) if line[0] != '#']

def input_clauses(lines):
    return {Clause(line) for line in lines[:-1]}, Clause(lines[-1])

def input_user_cmds(lines):
    return (
        (Clause(raw_clause), cmd)
        for raw_clause, cmd in map(lambda l: l.rsplit(maxsplit = 1), lines)
    )

def parse_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="task", required=True)

    parser_resolution = subparsers.add_parser("resolution")
    parser_resolution.add_argument("clauses")

    parser_cooking = subparsers.add_parser("cooking")
    parser_cooking.add_argument("clauses")
    parser_cooking.add_argument("user_cmds")

    return parser.parse_args()

def main():
    args = parse_arguments()

    clauses, goal = input_clauses(lines(args.clauses))

    if args.task == "resolution":
        # print(goal)
        print_resolution_result(*resolution(clauses, goal))
    elif args.task == "cooking":
        user_cmds = input_user_cmds(lines(args.user_cmds))
        clauses.add(goal)
        cooking(clauses, user_cmds)

if __name__ == "__main__":
    main()
