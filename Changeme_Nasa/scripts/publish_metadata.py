"""Publish the four local DuckDB metadata tables and provision the API reader."""

import argparse
import getpass
import secrets
from pathlib import Path

import duckdb
import psycopg
from psycopg import sql


TABLES = {
    "experiment_catalog": 263,
    "experiment_conditions": 735,
    "saffire_channel_units": 377,
    "cygnus_channel_units": 11,
}
TYPES = {"VARCHAR": "text", "DOUBLE": "double precision", "BIGINT": "bigint", "BOOLEAN": "boolean"}
ROLE = "combuslab_reader"
SCHEMA = "combuslab"


def publish(args):
    role = sql.Identifier(ROLE)
    schema = sql.Identifier(SCHEMA)
    password = getpass.getpass("Supabase admin password: ")
    reader_password = secrets.token_urlsafe(32)
    env = args.env
    if env.exists():
        raise SystemExit(f"Existing configuration: {env}")
    ca = args.ca.read_text(encoding="utf-8").strip()
    local = duckdb.connect(str(args.duckdb), read_only=True)
    with local, psycopg.connect(host=args.host, user=args.admin_user, port=5432, dbname="postgres",
                                password=password, sslmode="verify-full", sslrootcert=str(args.ca.resolve()),
                                connect_timeout=12) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(10417263)")
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (ROLE,))
            if cursor.fetchone():
                raise RuntimeError(f"Existing database role: {ROLE}")
            cursor.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(role, sql.Literal(reader_password)))
            cursor.execute(sql.SQL("CREATE SCHEMA {}").format(schema))
            cursor.execute(sql.SQL("GRANT USAGE ON SCHEMA {}, public TO {}").format(schema, role))
            for name, expected in TABLES.items():
                table = sql.Identifier(SCHEMA, name)
                definitions = [
                    sql.SQL("{} {}").format(sql.Identifier(column), sql.SQL(TYPES[kind]))
                    for column, kind, *_ in local.execute(f"DESCRIBE {name}").fetchall()
                ]
                if name == "experiment_catalog":
                    definitions.append(sql.SQL("PRIMARY KEY (experiment_id)"))
                cursor.execute(sql.SQL("CREATE TABLE {} ({})").format(table, sql.SQL(", ").join(definitions)))
                with cursor.copy(sql.SQL("COPY {} FROM STDIN").format(table)) as copy:
                    for row in local.execute(f"SELECT * FROM {name}").fetchall():
                        copy.write_row(row)
                cursor.execute(sql.SQL("SELECT count(*) FROM {}").format(table))
                if cursor.fetchone()[0] != expected:
                    raise RuntimeError(f"Unexpected count for {name}")
                cursor.execute(sql.SQL("GRANT SELECT ON {} TO {}").format(table, role))
                print(f"{name}: {expected}", flush=True)
            cursor.execute("CREATE INDEX experiment_conditions_experiment_idx ON combuslab.experiment_conditions (experiment_id)")
            cursor.execute(sql.SQL("GRANT SELECT ON public.nasa_synchronized TO {}").format(role))
            cursor.execute(sql.SQL(
                "CREATE POLICY combuslab_reader_select ON public.nasa_synchronized FOR SELECT TO {} USING (true)"
            ).format(role))
    project = args.admin_user.split(".", 1)[1]
    with env.open("x", encoding="utf-8") as file:
        file.write(f"COMBUSLAB_DB_HOST={args.host}\nCOMBUSLAB_DB_USER={ROLE}.{project}\n"
                   f"COMBUSLAB_DB_PASSWORD={reader_password}\n"
                   f'COMBUSLAB_DB_CA="{ca}"\n')
    print("Metadata committed. Local reader configuration created.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--admin-user", required=True)
    parser.add_argument("--ca", required=True, type=Path)
    parser.add_argument("--duckdb", required=True, type=Path)
    parser.add_argument("--env", required=True, type=Path)
    publish(parser.parse_args())
