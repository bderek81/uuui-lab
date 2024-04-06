import argparse

class Clause:
    sep = " v "

    def __init__(self, raw_clause: str, sos=False):
        self.literals = frozenset(raw_clause.split(Clause.sep))
        self.sos = sos
    
    def __repr__(self):
        return Clause.sep.join(self.literals)
    
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

def print_dashed_ln(len=15): print('=' * len)

def negate(literal: str):
    return f"~{literal}" if literal[0] != '~' else literal[1:]

def remove_redundant(clauses: 'set[Clause]'):
    non_redundant_clauses = set()

    for c1 in clauses:
        redundant = False
        for c2 in clauses:
            if c2.literals < c1.literals:
                redundant = True
                break
        if redundant: continue
        non_redundant_clauses.add(c1)
    
    return set(non_redundant_clauses)

def remove_irrelevant(clauses: 'set[Clause]'):
    return set(filter(lambda clause: not clause.is_tautology(), clauses))

def select_clauses(clauses: 'set[Clause]'):
    selected = set()

    for c1 in clauses:
        for c2 in filter(lambda c: c != c1 and c not in selected, clauses):
            if not (c1.sos or c2.sos): continue

            select = False
            for literal in c1.literals:
                if negate(literal) in c2.literals:
                    select = True
                    break
            
            if select:
                selected.add(c1)
                yield (c1, c2)

def resolve(c1: Clause, c2: Clause):
    resolvents = set()
    
    res_literals = set()
    for literal in c1.literals:
        if negate(literal) not in c2.literals:
            res_literals.add(literal)
    for literal in c2.literals:
        if negate(literal) not in c1.literals:
            res_literals.add(literal)
    raw_clause = Clause.sep.join(res_literals)
    resolvent = Clause(raw_clause, True) if raw_clause else None

    resolvents.add(resolvent)
    
    return resolvents

def print_resolution_result(goal, conclusion):
    print(f"[CONCLUSION]: {goal} is {'true' if conclusion else 'unknown'}")

def resolution(clauses: 'set[Clause]', goal: Clause):
    goal_negation = goal.negation()
    clauses.update(goal_negation)

    clauses = remove_redundant(clauses)
    clauses = remove_irrelevant(clauses)

    new = set()

    # TODO
    """ for i, clause_i in enumerate(clauses, start=1):
        print(f"{i}. {clause_i}")
    print_dashed_ln() """

    resolved = set()
    while True:
        # clauses = remove_redundant(clauses)
        for (c1, c2) in select_clauses(clauses):
            if frozenset({c1, c2}) in resolved: continue

            resolvents = resolve(c1, c2)

            resolved.add(frozenset({c1, c2}))
            if None in resolvents: return goal, True
            new.update(resolvents)
        if new.issubset(clauses): return goal, False

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
        print_resolution_result(*resolution(clauses, goal))
    elif args.task == "cooking":
        user_cmds = input_user_cmds(lines(args.user_cmds))
        clauses.add(goal)
        cooking(clauses, user_cmds)

if __name__ == "__main__":
    main()
