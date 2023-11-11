# Pygration

Pygration is a powerful and easy-to-use database migration library, designed to
simplify the process of managing and applying database schema changes. Whether
you're working on a small project or a large-scale application, Pygration
provides a robust solution for versioning and applying database migrations
seamlessly.

## Installation

To install Pygration, you will need to have Python and pip installed on your
system. Run this command:

```bash
pip install -i https://test.pypi.org/simple/ pygration
```

_It is important to note that this package is published on TestPyPI._

## Supported Databases

Right now Pygration allows to work only with PostgreSQL.

## Configuration

The first thing you need to do is to create a configuration file. This can be
either `pygration.toml` or `pyproject.toml`.

Pygration needs to know 3 things: where to store migrations, which database you
use, and how to connect to it.

Example of configuration in **pygration.toml** with all options:

```toml
provider = "postgresql"
dir = "migrations"

[connection]
username = "..."
password = "..."
host = "..."
port = "..."
database = "..."
schema = "..."  # by default it's `public`
```

If you have env variables with values to connect to the database, you can insert
them directly into the configuration:

```toml
[connection]
username = "${DB_USER}"
password = "${DB_PASSWORD}"
host = "${DB_HOST}"
port = "${DB_PORT}"
database = "${DB_NAME}"
```

If you prefer to save the configuration in **pyproject.toml**, you can do so:

```toml
[tool.pygration]
provider = "postgresql"
dir = "migrations"

[tool.pygration.connection]
username = "${DB_USER}"
password = "${DB_PASSWORD}"
host = "${DB_HOST}"
port = "${DB_HOST}"
database = "${DB_PORT}"
```

If for some reason you need a different configuration file, you can
specify it with the optional `--config` parameter:

```shell
pygration --config custom_config.toml
```

## CLI Usage

Pygration has four commands: `create`, `migrate`, `rollback` and `details`.

To create a migration file, use `create` command:

```bash
pygration create <name>
```

It creates a SQL file for the migration. Inside this file you can find 2
sections: UP and DOWN. The UP section is responsible for creating something in
the database, and the DOWN section is responsible for deleting:

```sql
-- UP
CREATE TABLE person
(
    id            BIGSERIAL PRIMARY KEY,
    email         TEXT UNIQUE NOT NULL,
    first_name    TEXT        NOT NULL,
    last_name     TEXT        NOT NULL,
    date_of_birth DATE
);

-- DOWN
DROP TABLE person;
```

To execute all migrations, use `migrate` command:

```bash
pygration migrate
```

With this command, you can execute a single migration or all migrations up to
the specified ID. Learn more about this:

```shell
pygration migrate --help
```

To roll back all migrations, use `rollback` command:

```bash
pygration rollback
```

With this command, you also can roll back only a single migration or all
migrations up to the specified ID. Learn more about this:

```shell
pygration rollback --help
```

To see details about executed migrations, use `details` command:

```shell
pygration details
```

## Package Usage

The main purpose of this library is to be used as a CLI, but you can also use
parts of it in your code. All you need to do is import `pygration`:

```python
import pygration

provider = "postgresql"
directory = "migrations"

db_user = "..."
db_pass = "..."
db_host = "..."
db_port = "..."
db_name = "..."
db_schema = "..."

pygration.create("name", directory=directory)

pygration.migrate(
    provider=provider,
    directory=directory,
    username=db_user,
    password=db_pass,
    host=db_host,
    port=db_port,
    database=db_name,
    schema=db_schema,
    one=False,
    id_=None,
)

pygration.rollback(
    provider=provider,
    directory=directory,
    username=db_user,
    password=db_pass,
    host=db_host,
    port=db_port,
    database=db_name,
    schema=db_schema,
    one=False,
    id_=None,
)

pygration.print_details(
    provider=provider,
    username=db_user,
    password=db_pass,
    host=db_host,
    port=db_port,
    database=db_name,
    schema=db_schema,
)
```
