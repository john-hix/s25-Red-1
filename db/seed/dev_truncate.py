from psycopg2 import sql

from common.database_engine import DBEngine

engine: DBEngine = DBEngine()
session = engine.get_session()
conn = session.connection().connection

try:
    conn.autocommit = True
    cur = conn.cursor()

    # Fetch all table names from the public schema, which is the only
    # one that CueCode uses.
    cur.execute(
        """
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public';
    """
    )
    tables = cur.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"Truncating table: {table_name}")
        cur.execute(
            sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE;").format(
                sql.Identifier(table_name)
            )
        )
        conn.commit()

    print("All tables truncated.")

finally:
    cur.close()
    conn.close()
