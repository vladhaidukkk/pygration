import argparse
import tomllib
import pathlib

import pygration


DEFAULT_CONFIG = "pygration.toml"


class Config:
    def __init__(self, file):
        with open(file, "rb") as file_obj:
            self._config = tomllib.load(file_obj)

    @property
    def directory(self):
        return self._config.get("directory")


def create_parser():
    parser = argparse.ArgumentParser(
        prog="pygration",
        description="Python database migrations manager",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=pathlib.Path,
        default=DEFAULT_CONFIG,
        help=f"pygration config (default: {DEFAULT_CONFIG})",
    )
    subparsers = parser.add_subparsers(
        title="Commands",
        dest="command",
        required=True,
    )

    create = subparsers.add_parser(
        "create",
        help="create a migration",
        description="Create a migration",
    )
    create.add_argument("name", help="migration name")

    # migrate = subparsers.add_parser(
    #     "migrate",
    #     help="apply migrations",
    #     description="Apply migrations",
    # )
    # rollback = subparsers.add_parser(
    #     "rollback",
    #     help="rollback migrations",
    #     description="Rollback migrations",
    # )
    # info = subparsers.add_parser(
    #     "info",
    #     help="display info about migrations",
    #     description="Display info about migrations",
    # )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        config = Config(args.config)
    except FileNotFoundError as err:
        parser.error(f"configuration file '{err.filename}' doesn't exist")
    else:
        match args.command:
            case "create":
                try:
                    pygration.create(args.name, directory=config.directory)
                except FileNotFoundError:
                    parser.error(
                        f"directory '{config.directory}' doesn't exist"
                    )


if __name__ == "__main__":
    main()
