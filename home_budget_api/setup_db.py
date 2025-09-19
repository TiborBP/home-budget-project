# setup_db.py
import sys
import os
import subprocess
import psycopg2
from psycopg2 import sql

def main():
    if len(sys.argv) != 2:
        print("Usage: python setup_db.py <superuser_password>")
        sys.exit(1)

    super_pass = sys.argv[1]

    super_conn_info = {
        "host": "localhost",
        "dbname": "postgres",
        "user": "postgres",
        "password": super_pass,
        "port": 5432
    }

    db_name = "home_budget"
    db_user = "home_budget_user"
    db_pass = "home_budget"

    conn = psycopg2.connect(**super_conn_info)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", [db_name])
    if not cur.fetchone():
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"Database '{db_name}' created")
    else:
        print(f"Database '{db_name}' already exists")

    cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname = %s", [db_user])
    if not cur.fetchone():
        cur.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(db_user)), [db_pass])
        print(f"User '{db_user}' created")
    else:
        print(f"User '{db_user}' already exists")

    cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
        sql.Identifier(db_name),
        sql.Identifier(db_user)
    ))

    cur.close()
    conn.close()
    db_conn_info = {
        "host": "localhost",
        "dbname": db_name,
        "user": "postgres",
        "password": super_pass,
        "port": 5432
    }
    conn = psycopg2.connect(**db_conn_info)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON SCHEMA public TO {}").format(sql.Identifier(db_user)))
    cur.execute(sql.SQL("ALTER SCHEMA public OWNER TO {}").format(sql.Identifier(db_user)))
    cur.execute(sql.SQL("GRANT USAGE, CREATE ON SCHEMA public TO {}").format(sql.Identifier(db_user)))

    cur.close()
    conn.close()

    print(f"Database '{db_name}' is ready with user '{db_user}'")

    print("Running Alembic migrations...")
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
        cwd=project_root
    )
    print("Database setup complete!")

if __name__ == "__main__":
    main()
