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

    conn = psycopg2.connect(f"postgres://{username}:{password}"
                            f"@{host}:{port}/{database}")
    cur = conn.cursor()
    cur.execute(f"SET search_path TO {schema}")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS _pygration_migrations (
            id BIGINT PRIMARY KEY,
            name TEXT NOT NULL,
            executed_at TIMESTAMP DEFAULT NOW() NOT NULL
        );
    """)
    cur.execute("SELECT * FROM _pygration_migrations")
    migrations = cur.fetchall()
    existing_ids = [m[0] for m in migrations]

    new_migrations = []
    for entry in sorted(os.scandir(directory), key=lambda e: e.name):
        if entry.is_file() and entry.name.endswith(".sql"):
            mid, name = entry.name[:-4].split("_", 1)
            if int(mid) not in existing_ids:
                new_migrations.append({
                    "id": mid,
                    "name": name,
                    "query": _get_query(entry, section="up"),
                })

    match provider:
        case "postgresql":
            for m in new_migrations:
                cur.execute(m["query"])
                cur.execute(f"""
                    INSERT INTO _pygration_migrations (id, name)
                    VALUES ({m["id"]}, '{m["name"]}');
                """)
            conn.commit()

    cur.close()
    conn.close()


def rollback(*, provider, directory, username, password, host, port, database,
             schema=None):
    if schema is None:
        schema = "public"

    conn = psycopg2.connect(f"postgres://{username}:{password}"
                            f"@{host}:{port}/{database}")
    cur = conn.cursor()
    cur.execute(f"SET search_path TO {schema}")

    cur.execute("SELECT * FROM _pygration_migrations")
    migrations = cur.fetchall()
    existing_ids = [m[0] for m in migrations]

    rollbacks = []
    for entry in sorted(os.scandir(directory), key=lambda e: e.name,
                        reverse=True):
        if entry.is_file() and entry.name.endswith(".sql"):
            mid = entry.name.split("_", 1)[0]
            if int(mid) in existing_ids:
                rollbacks.append({
                    "id": mid,
                    "query": _get_query(entry, section="down"),
                })

    match provider:
        case "postgresql":
            for r in rollbacks:
                cur.execute(r["query"])
                cur.execute(f"""
                    DELETE FROM _pygration_migrations WHERE id = {r["id"]};
                """)
            conn.commit()

    cur.close()
    conn.close()
