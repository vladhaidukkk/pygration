import argparse
import os
import pathlib
import re
import tomllib

from dotenv import load_dotenv

import pygration

load_dotenv()


class Config:
    DEFAULTS = ["pygration.toml", "pyproject.toml"]

    def __init__(self, file=None):
        if file is None:
            for default in Config.DEFAULTS:
                if os.path.exists(default):
                    file = default
                    break
            else:
                raise FileNotFoundError(
                    f"neither {' nor '.join(Config.DEFAULTS)} exist"
                )

        try:
            with open(file, "rb") as file_obj:
                if file == Config.DEFAULTS[-1]:
                    tool_table = tomllib.load(file_obj).get("tool", {})
                    self._config = tool_table.get("pygration", {})
                else:
                    self._config = tomllib.load(file_obj)
        except FileNotFoundError:
            raise FileNotFoundError(f"configuration file '{file}' doesn't " f"exist")

    @staticmethod
    def _inject_env_var(value):
        if m := re.match(r"^\${(?P<var>.+)}$", value):
            return os.getenv(m.group("var"))
        return value

    @property
    def provider(self):
        return self._config.get("provider")

    @property
    def dir(self):
        return self._config.get("dir")

    @property
    def username(self):
        value = self._config.get("connection", {}).get("username")
        return value and self._inject_env_var(value)

    @property
    def password(self):
        value = self._config.get("connection", {}).get("password")
        return value and self._inject_env_var(value)

    @property
    def host(self):
        value = self._config.get("connection", {}).get("host")
        return value and self._inject_env_var(value)

    @property
    def port(self):
        value = self._config.get("connection", {}).get("port")
        return value and self._inject_env_var(value)

    @property
    def database(self):
        value = self._config.get("connection", {}).get("database")
        return value and self._inject_env_var(value)

    @property
    def schema(self):
        value = self._config.get("connection", {}).get("schema")
        return value and self._inject_env_var(value)


def create_parser():
    parser = argparse.ArgumentParser(
        prog="pygration",
        description="Python database migrations manager",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=pathlib.Path,
        help=f"pygration config (default: {', '.join(Config.DEFAULTS)})",
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

    migrate = subparsers.add_parser(
        "migrate",
        help="apply migrations",
        description="Apply migrations",
        epilog="Priority of options: --one over --id. If no option is "
        "specified, all migrations will be applied",
    )
    migrate.add_argument(
        "-o",
        "--one",
        action="store_true",
        help="apply one migration",
    )
    migrate.add_argument(
        "-i",
        "--id",
        type=int,
        help="apply migrations up to the specified id",
    )

    rollback = subparsers.add_parser(
        "rollback",
        help="rollback migrations",
        description="Rollback migrations",
        epilog="Priority of options: --one over --id. If no option is "
        "specified, all migrations will be rolled back",
    )
    rollback.add_argument(
        "-o",
        "--one",
        action="store_true",
        help="rollback only the previous migration",
    )
    rollback.add_argument(
        "-i",
        "--id",
        type=int,
        help="rollback migrations up to the specified id",
    )

    subparsers.add_parser(
        "details",
        help="display details about migrations",
        description="Display details about migrations",
    )

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
                    parser.error(f"directory '{config.dir}' doesn't exist")
            case "migrate":
                pygration.migrate(
                    provider=config.provider,
                    directory=config.dir,
                    username=config.username,
                    password=config.password,
                    host=config.host,
                    port=config.port,
                    database=config.database,
                    schema=config.schema,
                    one=args.one,
                    id_=args.id,
                )
            case "rollback":
                pygration.rollback(
                    provider=config.provider,
                    directory=config.dir,
                    username=config.username,
                    password=config.password,
                    host=config.host,
                    port=config.port,
                    database=config.database,
                    schema=config.schema,
                    one=args.one,
                    id_=args.id,
                )
            case "details":
                pygration.print_details(
                    provider=config.provider,
                    username=config.username,
                    password=config.password,
                    host=config.host,
                    port=config.port,
                    database=config.database,
                    schema=config.schema,
                )


if __name__ == "__main__":
    main()
