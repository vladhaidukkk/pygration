import argparse


def create_parser():
    parser = argparse.ArgumentParser(
        prog="pygration",
        description="Python database migrations manager",
    )
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    create = subparsers.add_parser(
        "create",
        help="create a migration",
        description="Create a migration",
    )
    migrate = subparsers.add_parser(
        "migrate",
        help="apply migrations",
        description="Apply migrations",
    )
    rollback = subparsers.add_parser(
        "rollback",
        help="rollback migrations",
        description="Rollback migrations",
    )
    info = subparsers.add_parser(
        "info",
        help="display info about migrations",
        description="Display info about migrations",
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    main()
