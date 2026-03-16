"""
ETSolar ERP - Database Clear Script

Clears all data from the database.

Usage:
  python -m scripts.clear_db               # Truncate all tables (keeps schema)
  python -m scripts.clear_db --drop-tables  # Drop all tables entirely
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from sqlalchemy import text
from app.db.database import engine


def get_all_table_names(conn):
    """Get all user tables from the database directly (not from model metadata)."""
    result = conn.execute(text(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
    ))
    return [row[0] for row in result]


def get_all_enum_types(conn):
    """Get all user-defined enum types."""
    result = conn.execute(text(
        "SELECT t.typname FROM pg_type t "
        "JOIN pg_namespace n ON t.typnamespace = n.oid "
        "WHERE t.typtype = 'e' AND n.nspname = 'public'"
    ))
    return [row[0] for row in result]


def clear_db(drop_tables: bool = False):
    if drop_tables:
        print("⚠️  Dropping ALL tables and types from the database...")
        confirm = input("Type 'yes' to confirm: ").strip().lower()
        if confirm != "yes":
            print("Aborted.")
            return

        with engine.begin() as conn:
            tables = get_all_table_names(conn)
            if not tables:
                print("No tables found. Database is already empty.")
                return

            # Drop all tables with CASCADE
            tables_sql = ", ".join(f'"{t}"' for t in tables)
            conn.execute(text(f"DROP TABLE IF EXISTS {tables_sql} CASCADE"))
            print(f"✓ Dropped {len(tables)} tables:")
            for t in tables:
                print(f"   • {t}")

            # Drop enum types too
            enums = get_all_enum_types(conn)
            for enum_name in enums:
                conn.execute(text(f'DROP TYPE IF EXISTS "{enum_name}" CASCADE'))
            if enums:
                print(f"✓ Dropped {len(enums)} enum types:")
                for e in enums:
                    print(f"   • {e}")

        print("\n✅ All tables dropped successfully.")
        return

    # ── Truncate mode ──────────────────────────────────────────
    print("⚠️  Clearing ALL data from the database (tables will remain)...")
    confirm = input("Type 'yes' to confirm: ").strip().lower()
    if confirm != "yes":
        print("Aborted.")
        return

    with engine.begin() as conn:
        tables = get_all_table_names(conn)
        if not tables:
            print("No tables found.")
            return

        tables_sql = ", ".join(f'"{t}"' for t in tables)
        conn.execute(text(
            f"TRUNCATE TABLE {tables_sql} RESTART IDENTITY CASCADE"
        ))
        print(f"✅ Cleared {len(tables)} tables:")
        for t in tables:
            print(f"   • {t}")


if __name__ == "__main__":
    drop_tables = "--drop-tables" in sys.argv
    try:
        clear_db(drop_tables=drop_tables)
    except Exception as e:
        print(f"\n❌ Clear failed: {e}")
        raise
