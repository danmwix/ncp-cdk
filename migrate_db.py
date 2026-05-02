import sqlite3

DB_PATH = r'C:\Users\user\Desktop\ncp-cdk\instance\ncp_cdk.db'

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('Checking current schema...')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f'Tables found: {tables}')

    if 'child_disabilities' in tables:
        cursor.execute('PRAGMA table_info(child_disabilities);')
        columns = [row[1] for row in cursor.fetchall()]
        print(f'child_disabilities columns: {columns}')

        if 'disability_subcategory_id' not in columns:
            print('Column missing. Fixing...')
            cursor.execute('DROP TABLE IF EXISTS child_disabilities;')
            cursor.execute('''
                CREATE TABLE child_disabilities (
                    child_id INTEGER NOT NULL,
                    disability_subcategory_id INTEGER NOT NULL,
                    PRIMARY KEY (child_id, disability_subcategory_id),
                    FOREIGN KEY (child_id) REFERENCES child(id),
                    FOREIGN KEY (disability_subcategory_id) REFERENCES disability_subcategory(id)
                );
            ''')
            print('Done! Table recreated correctly.')
        else:
            print('Column already exists. No fix needed.')
    else:
        print('Table missing. Creating...')
        cursor.execute('''
            CREATE TABLE child_disabilities (
                child_id INTEGER NOT NULL,
                disability_subcategory_id INTEGER NOT NULL,
                PRIMARY KEY (child_id, disability_subcategory_id),
                FOREIGN KEY (child_id) REFERENCES child(id),
                FOREIGN KEY (disability_subcategory_id) REFERENCES disability_subcategory(id)
            );
        ''')
        print('Done!')

    conn.commit()
    conn.close()
    print('Migration complete!')

if __name__ == '__main__':
    migrate()
