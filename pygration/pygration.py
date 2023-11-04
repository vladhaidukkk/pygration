import os
from time import time
from pathlib import Path
from math import floor

import psycopg2


def create(name, *, directory):
    file = Path(directory, f"{floor(time())}_{name}.sql")
    with open(file, "w") as file_obj:
        file_obj.write("-- UP\n\n\n-- DOWN\n\n")


def _get_query(file, *, section):
    section = section.lower()
    record = False
    query_lines = []
    with open(file) as file_obj:
        for line in file_obj:
            if record:
                if section == "up" and line.lower().startswith("-- down"):
                    record = False
                    break
                query_lines.append(line)
            else:
                record = line.lower().startswith(f"-- {section}")
                continue
    return "".join(query_lines).strip()


def migrate(*, provider, directory, username, password, host, port, database,
            schema=None):
    if schema is None:
        schema = "public"

    queries = []
    for entry in sorted(os.scandir(directory), key=lambda e: e.name):
        if entry.is_file() and entry.name.endswith(".sql"):
            queries.append(_get_query(entry, section="up"))

    match provider:
        case "postgresql":
            conn = psycopg2.connect(f"postgres://{username}:{password}"
                                    f"@{host}:{port}/{database}")
            cur = conn.cursor()
            cur.execute(f"SET search_path TO {schema}")
            for query in queries:
                cur.execute(query)
            conn.commit()
            cur.close()
            conn.close()


def rollback(*, provider, directory, username, password, host, port, database,
             schema=None):
    if schema is None:
        schema = "public"

    queries = []
    for entry in sorted(os.scandir(directory), key=lambda e: e.name,
                        reverse=True):
        if entry.is_file() and entry.name.endswith(".sql"):
            queries.append(_get_query(entry, section="down"))

    match provider:
        case "postgresql":
            conn = psycopg2.connect(f"postgres://{username}:{password}"
                                    f"@{host}:{port}/{database}")
            cur = conn.cursor()
            cur.execute(f"SET search_path TO {schema}")
            for query in queries:
                cur.execute(query)
            conn.commit()
            cur.close()
            conn.close()
