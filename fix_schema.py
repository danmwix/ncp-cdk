"""
Fix the child_disabilities table schema:
Migrate from disability_id (to disability_category) 
to disability_subcategory_id (to disability_subcategory)

This script preserves all existing user/child data and relinks disabilities.
"""
import sqlite3

db_path = 'instance/ncp_cdk.db'

print(f"Migrating database schema: {db_path}\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Step 1: Save existing relationships
    print("Step 1: Reading existing disability assignments...")
    cursor.execute("SELECT child_id, disability_id FROM child_disabilities;")
    old_relationships = cursor.fetchall()
    print(f"  Found {len(old_relationships)} relationships:")
    for child_id, disability_id in old_relationships:
        print(f"    Child {child_id} -> Disability Category {disability_id}")
    
    # Step 2: Get the first subcategory for each category
    print("\nStep 2: Finding subcategories for each category...")
    cursor.execute("""
        SELECT DISTINCT dc.id, ds.id 
        FROM disability_category dc 
        LEFT JOIN disability_subcategory ds ON dc.id = ds.category_id 
        WHERE ds.id IS NOT NULL
        ORDER BY dc.id, ds.id
    """)
    category_to_subcategory = {}
    for row in cursor.fetchall():
        category_id, subcategory_id = row
        if category_id not in category_to_subcategory:
            category_to_subcategory[category_id] = subcategory_id
    
    print(f"  Mapping:")
    for cat_id, subcat_id in category_to_subcategory.items():
        cursor.execute("SELECT name FROM disability_category WHERE id = ?", (cat_id,))
        cat_name = cursor.fetchone()[0]
        cursor.execute("SELECT name FROM disability_subcategory WHERE id = ?", (subcat_id,))
        subcat_name = cursor.fetchone()[0]
        print(f"    Category {cat_id} ({cat_name}) -> Subcategory {subcat_id} ({subcat_name})")
    
    # Step 3: Drop the old table
    print("\nStep 3: Dropping old child_disabilities table...")
    cursor.execute("DROP TABLE IF EXISTS child_disabilities;")
    conn.commit()
    print("  ✓ Dropped old table")
    
    # Step 4: Create new table with correct schema
    print("\nStep 4: Creating new child_disabilities table...")
    cursor.execute("""
        CREATE TABLE child_disabilities (
            child_id INTEGER NOT NULL,
            disability_subcategory_id INTEGER NOT NULL,
            PRIMARY KEY (child_id, disability_subcategory_id),
            FOREIGN KEY (child_id) REFERENCES child (id),
            FOREIGN KEY (disability_subcategory_id) REFERENCES disability_subcategory (id)
        );
    """)
    conn.commit()
    print("  ✓ Created new table with correct schema")
    
    # Step 5: Reinsert relationships with subcategories
    print("\nStep 5: Relinking disabilities to new subcategories...")
    for child_id, old_disability_id in old_relationships:
        new_subcategory_id = category_to_subcategory.get(old_disability_id)
        if new_subcategory_id:
            cursor.execute(
                "INSERT INTO child_disabilities (child_id, disability_subcategory_id) VALUES (?, ?)",
                (child_id, new_subcategory_id)
            )
            print(f"  Child {child_id}: Category {old_disability_id} -> Subcategory {new_subcategory_id}")
        else:
            print(f"  ERROR: No subcategory found for disability {old_disability_id}")
    
    conn.commit()
    
    # Step 6: Verify
    print("\nStep 6: Verifying new schema...")
    cursor.execute("PRAGMA table_info(child_disabilities);")
    columns = cursor.fetchall()
    print(f"  Columns: {[col[1] for col in columns]}")
    
    cursor.execute("SELECT COUNT(*) FROM child_disabilities;")
    count = cursor.fetchone()[0]
    print(f"  Total relationships: {count}")
    
    cursor.execute("SELECT child_id, disability_subcategory_id FROM child_disabilities;")
    print(f"  New relationships:")
    for child_id, subcat_id in cursor.fetchall():
        cursor.execute("SELECT name FROM disability_subcategory WHERE id = ?", (subcat_id,))
        subcat_name = cursor.fetchone()[0]
        print(f"    Child {child_id} -> Subcategory {subcat_id} ({subcat_name})")
    
    print("\n✅ Database schema migrated successfully!")
    
except Exception as e:
    print(f"\n❌ Error during migration: {e}")
    conn.rollback()
    raise

finally:
    conn.close()
