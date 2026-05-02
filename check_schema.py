import sqlite3
import os

db_path = 'instance/ncp_cdk.db'
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"\nAll tables in database ({len(tables)} total):")
for table in tables:
    print(f"  {table[0]}")

print("\n" + "="*50 + "\n")

# Check each table's schema
for table_name in ['child_disabilities', 'child', 'disability_subcategory', 'disability_category', 'user']:
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    if columns:
        print(f"{table_name} columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    else:
        print(f"{table_name}: TABLE DOES NOT EXIST")
    print()

conn.close()
