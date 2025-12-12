from typing import Any, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager
from dotenv import load_dotenv


load_dotenv()

DBNAME = os.getenv("PG_DB")
DBUSER = os.getenv("PG_USER")
DBPASS = os.getenv("PG_PASS")
DBHOST = os.getenv("PG_HOST")
DBPORT = os.getenv("PG_PORT")


class Database:
    """Simple DB wrapper for PostgreSQL (transaction + parameterized queries)."""
    def __init__(self, dsn: Optional[str] = None):
        if dsn:
            self.dsn = dsn
        else:
            self.dsn = f"dbname={DBNAME} user={DBUSER} password={DBPASS} host={DBHOST} port={DBPORT}"

    @contextmanager
    def get_conn(self):
        conn = psycopg2.connect(self.dsn)
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def transaction(self):
        with self.get_conn() as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def fetchall(self, query: str, params: tuple = ()) -> List[dict]:
        with self.get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def fetchone(self, query: str, params: tuple = ()) -> Optional[dict]:
        with self.get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchone()

    def execute(self, query: str, params: tuple = ()) -> None:
        with self.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)

    def execute_returning(self, query: str, params: tuple = ()) -> Any:
        with self.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute(query + " RETURNING id", params)
                return cur.fetchone()[0]
