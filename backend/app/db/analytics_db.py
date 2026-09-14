import os
import math
import re
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

class SQLiteStdDevSamp:
    def __init__(self):
        self.values = []

    def step(self, value):
        if value is not None:
            self.values.append(float(value))

    def finalize(self):
        n = len(self.values)
        if n < 2:
            return 0.0
        mean = sum(self.values) / n
        variance = sum((x - mean) ** 2 for x in self.values) / (n - 1)
        return math.sqrt(variance)

class SQLiteVariance:
    def __init__(self):
        self.values = []

    def step(self, value):
        if value is not None:
            self.values.append(float(value))

    def finalize(self):
        n = len(self.values)
        if n < 2:
            return 0.0
        mean = sum(self.values) / n
        return sum((x - mean) ** 2 for x in self.values) / (n - 1)

def register_sqlite_aggregates(dbapi_connection):
    """Registers STDDEV_SAMP and VARIANCE aggregate functions on a raw SQLite connection."""
    if hasattr(dbapi_connection, "create_aggregate"):
        dbapi_connection.create_aggregate("stddev_samp", 1, SQLiteStdDevSamp)
        dbapi_connection.create_aggregate("variance", 1, SQLiteVariance)

def get_sql_file_path() -> str:
    """Returns absolute path to sql/analytics_views.sql."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    return os.path.join(base_dir, "sql", "analytics_views.sql")

def initialize_analytics_views(db: Session):
    """Executes the DDL statements in analytics_views.sql to create all 7 views."""
    sql_file = get_sql_file_path()
    if not os.path.exists(sql_file):
        raise FileNotFoundError(f"Analytics views SQL file not found at {sql_file}")

    with open(sql_file, "r") as f:
        raw_sql = f.read()

    # Determine backend dialect
    bind = db.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    if is_sqlite:
        # Register aggregates on underlying raw DBAPI connection if SQLite
        raw_conn = bind.raw_connection()
        register_sqlite_aggregates(raw_conn.driver_connection)

    # Split statements by semicolon
    statements = [stmt.strip() for stmt in raw_sql.split(";") if stmt.strip()]

    for stmt in statements:
        # Ignore comments-only blocks
        non_comment_lines = [l for l in stmt.splitlines() if not l.strip().startswith("--")]
        clean_stmt = "\n".join(non_comment_lines).strip()
        if not clean_stmt:
            continue

        if is_sqlite:
            # Handle SQLite compatibility for CREATE OR REPLACE VIEW
            match = re.search(r"CREATE\s+OR\s+REPLACE\s+VIEW\s+([a-zA-Z0-9_]+)", clean_stmt, re.IGNORECASE)
            if match:
                view_name = match.group(1)
                db.execute(text(f"DROP VIEW IF EXISTS {view_name}"))
                clean_stmt = re.sub(
                    r"CREATE\s+OR\s+REPLACE\s+VIEW\s+" + re.escape(view_name),
                    f"CREATE VIEW {view_name}",
                    clean_stmt,
                    flags=re.IGNORECASE
                )

        db.execute(text(clean_stmt))

    db.commit()
