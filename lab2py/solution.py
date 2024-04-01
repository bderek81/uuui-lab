import argparse

class Clause:
    sep = " v "

    def __init__(self, raw_clause: str):
        self.literals = raw_clause.split(Clause.sep)
    
    def __repr__(self):
        return Clause.sep.join(self.literals)

def resolution(clauses: 'list[Clause]'):
    pass

def cooking(clauses: 'list[Clause]', user_cmds):
    print(f"Constructed with knowledge:")
    for clause in clauses:
        print(f"{clause}")

    for user_cmd in user_cmds:
        print(f"User's command: {user_cmd[0]} {user_cmd[1]}")

        if user_cmd[1] == '?':
            pass
        elif user_cmd[1] == '+':
            print(f"Added {user_cmd[0]}")
        elif user_cmd[1] == '-':
            print(f"removed {user_cmd[0]}")

def lines(file):
    return (line.rstrip().lower() for line in open(file) if line[0] != '#')

def input_clauses(lines):
    return [Clause(line) for line in lines]

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

    clauses = input_clauses(lines(args.clauses))

    if args.task == "resolution":
        resolution(clauses)
    elif args.task == "cooking":
        user_cmds = input_user_cmds(lines(args.user_cmds))
        cooking(clauses, user_cmds)

if __name__ == "__main__":
    main()
