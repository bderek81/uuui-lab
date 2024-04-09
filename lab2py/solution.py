import argparse
from collections import deque

class Clause:
    sep = " v "

    def __init__(self, raw_clause: str, sos=False, parents: 'tuple[Clause]'=None):
        self.literals = frozenset(raw_clause.split(Clause.sep))
        self.sos = sos
        self.parents = parents
        self.nil = not raw_clause
    
    def __eq__(self, other: 'Clause'):
        return self.literals == other.literals
    
    def __hash__(self):
        return hash(self.literals)
    
    def __repr__(self):
        return Clause.sep.join(self.literals) if not self.nil else "NIL"
    
    def negation(self):
        return {Clause(negated(lit), sos=True) for lit in self.literals}
    
    def is_tautology(self):
        return any(negated(lit) in self.literals for lit in self.literals)

def negated(lit: str):
    return f"~{lit}" if lit[0] != '~' else lit[1:]

def remove_redundant(clauses: 'set[Clause]', other: 'set[Clause]'):
    return {c for c in clauses if not any(c0.literals < c.literals for c0 in other)}

def remove_irrelevant(clauses: 'set[Clause]'):
    return {c for c in clauses if not c.is_tautology()}

def select_clauses(clauses: 'set[Clause]'):
    visited = set()
    for c1 in clauses:
        visited.add(c1)
        for c2 in filter(lambda c: c not in visited, clauses):
            if not (c1.sos or c2.sos): continue # set-of-support strategy

            if any(negated(lit) in c2.literals for lit in c1.literals):
                yield (c1, c2)

def resolve(c1: Clause, c2: Clause):
    res_by = None
    for lit in c1.literals:
        if negated(lit) in c2.literals:
            if res_by is not None: return None
            res_by = lit

    res_literals = set(c1.literals.union(c2.literals))
    res_literals.remove(res_by)
    res_literals.remove(negated(res_by))
    
    raw_clause = Clause.sep.join(res_literals)
    return Clause(raw_clause, sos=True, parents=(c1, c2))

def resolution(clauses: 'set[Clause]', goal: Clause):
    input_clauses, goal_negation = deque(clauses), goal.negation()
    input_clauses.extend(goal_negation)

    clauses.update(goal_negation)
    clauses = remove_irrelevant(clauses) # deletion strategy
    clauses = remove_redundant(clauses, clauses)
    new = set()
    while True:
        for (c1, c2) in select_clauses(clauses):
            resolvent = resolve(c1, c2)
            if resolvent is not None:
                if resolvent.nil: return input_clauses, goal, resolvent
                new.add(resolvent)
        new = remove_redundant(new, clauses)
        clauses = remove_redundant(clauses, new)
        if new.issubset(clauses): return input_clauses, goal, None

        clauses.update(new)
        new.clear()

def print_dashed_ln(len=15): print('=' * len)

def print_resolution_result(input_clauses: 'deque[Clause]', goal: Clause, resolvent: Clause):
    def print_indexed(clauses: 'deque[Clause]'):
        for c in clauses:
            indexed_c = f"{clause_index[c]}. {c}"
            if c.parents:
                parent_index = sorted(clause_index[p] for p in c.parents)
                indexed_c += f" ({parent_index[0]}, {parent_index[1]})"
            print(indexed_c)
    
    conclusion = resolvent is not None
    if not conclusion:
        clause_index = {c: i for i, c in enumerate(input_clauses, 1)}
    else:
        input_clauses, derived_clauses = deque(), deque()

        queue = deque([resolvent])
        while queue:
            clause = queue.popleft()
            if clause.parents:
                derived_clauses.appendleft(clause)
                queue.extend(clause.parents)
            elif clause.sos:
                input_clauses.append(clause)
            else:
                input_clauses.appendleft(clause)
        
        input_clauses = deque(dict.fromkeys(input_clauses))
        clause_index = {c: i for i, c in enumerate(input_clauses, 1)}

        derived_clauses = deque(dict.fromkeys(derived_clauses))
        clause_index.update(
            {c: i for i, c in enumerate(derived_clauses, len(clause_index) + 1)}
        )

    print_indexed(input_clauses)
    print_dashed_ln()
    if conclusion:
        print_indexed(derived_clauses)
        print_dashed_ln()
    print(f"[CONCLUSION]: {goal} is {'true' if conclusion else 'unknown'}\n")

def cooking(clauses: 'set[Clause]', user_cmds):
    print(f"Constructed with knowledge:")
    print(*clauses, sep='\n')

    for (clause, cmd) in user_cmds:
        print(f"User's command: {clause} {cmd}")

        if cmd == '?':
            print_resolution_result(*resolution(clauses.copy(), clause))
        elif cmd == '+':
            clauses.add(clause)
            print(f"Added {clause}\n")
        elif cmd == '-':
            clauses.remove(clause)
            print(f"removed {clause}\n")

def lines(file):
    return [line.rstrip().lower() for line in open(file) if line[0] != '#']

def input_clauses(lines: 'list[str]'):
    return {Clause(line) for line in lines[:-1]}, Clause(lines[-1])

def input_user_cmds(lines: 'list[str]'):
    return (
        (Clause(raw_clause), cmd)
        for raw_clause, cmd in map(lambda l: l.rsplit(maxsplit=1), lines)
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
        print_resolution_result(*resolution(clauses, goal))
    elif args.task == "cooking":
        user_cmds = input_user_cmds(lines(args.user_cmds))
        clauses.add(goal)
        cooking(clauses, user_cmds)

if __name__ == "__main__":
    main()
