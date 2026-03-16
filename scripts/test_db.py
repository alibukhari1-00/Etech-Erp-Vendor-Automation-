"""
ETSolar ERP - Database Connection Test

Verifies the database connection is working.
Run: python -m scripts.test_db  (from backend/)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.db.database import engine

if __name__ == "__main__":
    try:
        connection = engine.connect()
        print("✅ Database connected successfully")
        connection.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
