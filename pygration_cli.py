import argparse
import tomllib
import pathlib
import os

import pygration


class Config:
    DEFAULTS = ["pygration.toml", "pyproject.toml"]

    def __init__(self, file=None):
        if file is None:
            for default in Config.DEFAULTS:
                if os.path.exists(default):
                    file = default
                    break
            else:
                raise FileNotFoundError(f"neither {
                    " nor ".join(Config.DEFAULTS)
                } exist")

        try:
            with open(file, "rb") as file_obj:
                if file == Config.DEFAULTS[-1]:
                    tool_table = tomllib.load(file_obj).get("tool", {})
                    self._config = tool_table.get("pygration", {})
                else:
                    self._config = tomllib.load(file_obj)
        except FileNotFoundError:
            raise FileNotFoundError(f"configuration file '{file}' doesn't "
                                    f"exist")

    @property
    def dir(self):
        return self._config.get("dir")


def create_parser():
    parser = argparse.ArgumentParser(
        prog="pygration",
        description="Python database migrations manager",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=pathlib.Path,
        help=f"pygration config (default: {", ".join(Config.DEFAULTS)})",
    )
    subparsers = parser.add_subparsers(
        title="Commands",
        dest="command",
        # required=True, # todo: uncomment
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
        parser.error(str(err))
    else:
        match args.command:
            case "create":
                try:
                    pygration.create(args.name, directory=config.dir)
                except FileNotFoundError:
                    parser.error(
                        f"directory '{config.dir}' doesn't exist"
                    )


if __name__ == "__main__":
    main()
