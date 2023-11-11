import os
from math import floor
from pathlib import Path
from time import time

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


def migrate(
    *,
    provider,
    directory,
    username,
    password,
    host,
    port,
    database,
    schema=None,
    one=False,
    id_=None,
):
    if schema is None:
        schema = "public"

    match provider:
        case "postgresql":
            conn = psycopg2.connect(
                user=username,
                password=password,
                host=host,
                port=port,
                database=database,
            )
            with conn:
                with conn.cursor() as cur:
                    cur.execute(f"SET search_path TO {schema}")
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS _pygration_migrations (
                            id BIGINT PRIMARY KEY,
                            name TEXT NOT NULL,
                            executed_at TIMESTAMP DEFAULT NOW() NOT NULL
                        );
                    """
                    )
                    cur.execute("SELECT * FROM _pygration_migrations;")
                    existing_mids = [m[0] for m in cur.fetchall()]

                    new_migrations = []
                    for entry in sorted(os.scandir(directory), key=lambda e: e.name):
                        if entry.is_file() and entry.name.endswith(".sql"):
                            mid, name = entry.name[:-4].split("_", 1)
                            mid = int(mid)
                            if mid not in existing_mids:
                                new_migrations.append(
                                    {
                                        "id": mid,
                                        "name": name,
                                        "query": _get_query(entry, section="up"),
                                    }
                                )
                                if one:
                                    break
                                elif id_ == mid:
                                    break

                    for m in new_migrations:
                        cur.execute(m["query"])
                        cur.execute(
                            f"""
                            INSERT INTO _pygration_migrations (id, name)
                            VALUES ({m["id"]}, '{m["name"]}');
                        """
                        )
            conn.close()


def rollback(
    *,
    provider,
    directory,
    username,
    password,
    host,
    port,
    database,
    schema=None,
    one=False,
    id_=None,
):
    if schema is None:
        schema = "public"

    match provider:
        case "postgresql":
            conn = psycopg2.connect(
                user=username,
                password=password,
                host=host,
                port=port,
                database=database,
            )
            with conn:
                with conn.cursor() as cur:
                    cur.execute(f"SET search_path TO {schema}")
                    cur.execute("SELECT * FROM _pygration_migrations;")
                    existing_mids = [m[0] for m in cur.fetchall()]

                    rollbacks = []
                    for entry in sorted(
                        os.scandir(directory), key=lambda e: e.name, reverse=True
                    ):
                        if entry.is_file() and entry.name.endswith(".sql"):
                            mid = entry.name.split("_", 1)[0]
                            mid = int(mid)
                            if mid in existing_mids:
                                rollbacks.append(
                                    {
                                        "id": mid,
                                        "query": _get_query(entry, section="down"),
                                    }
                                )
                                if one:
                                    break
                                elif id_ == mid:
                                    break

                    for r in rollbacks:
                        cur.execute(r["query"])
                        cur.execute(
                            f"""
                            DELETE FROM _pygration_migrations
                            WHERE id = {r["id"]};
                        """
                        )
            conn.close()


def print_details(*, provider, username, password, host, port, database, schema=None):
    if schema is None:
        schema = "public"

    match provider:
        case "postgresql":
            conn = psycopg2.connect(
                user=username,
                password=password,
                host=host,
                port=port,
                database=database,
            )
            with conn:
                with conn.cursor() as cur:
                    cur.execute(f"SET search_path TO {schema}")
                    cur.execute("SELECT * FROM _pygration_migrations;")
                    migrations = cur.fetchall()

                    id_col_width = len(str(migrations[-1][0]))
                    name_col_width = len(max(migrations, key=lambda m: len(m[1]))[1])
                    header = (
                        f"{'ID'.ljust(id_col_width)} | "
                        f"{'NAME'.ljust(name_col_width)} | "
                        f"EXECUTED AT"
                    )
                    records = [
                        (
                            f"{str(m[0]).ljust(id_col_width)} | "
                            f"{m[1].ljust(name_col_width)} | "
                            f"{m[2]:%Y-%m-%d}"
                        )
                        for m in migrations
                    ]
                    header_width = len(header)
                    record_width = len(max(records, key=len))
                    if header_width > record_width:
                        details_width = header_width
                    else:
                        details_width = record_width

                    print(header)
                    print("-" * details_width)
                    for record in records:
                        print(record)
            conn.close()
