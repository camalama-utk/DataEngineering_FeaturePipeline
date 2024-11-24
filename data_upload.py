import os
import time
import psycopg2
import csv

# Database connection details
DB_CONFIG = {
    'dbname': 'postgres', #your dbname
    'user': 'postgres', #your user name
    'password': 'book', #your password
    'host': 'localhost',
    'port': '5432',
}

# Directory to monitor
WATCH_DIR = '/Users/laneslawson/group_project_data' #change to your directory

# Function to load CSV into the database
def load_csv_to_db(filepath):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # Define table name and columns (ensure your table matches the CSV structure)
        table_name = 'group_project_data'
        with open(filepath, 'r') as file:
            next(file)  # Skip the header row if it exists
            cursor.copy_expert(f"""
                COPY {table_name} 
                FROM STDIN WITH CSV HEADER;
            """, file)
        conn.commit()
        print(f"Loaded {filepath} into {table_name}")
    except Exception as e:
        conn.rollback()
        print(f"Error loading {filepath}: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to monitor directory
def monitor_directory():
    processed_files = set()

    while True:
        files = [f for f in os.listdir(WATCH_DIR) if f.endswith('.csv')]
        new_files = set(files) - processed_files

        for file in new_files:
            filepath = os.path.join(WATCH_DIR, file)
            load_csv_to_db(filepath)
            processed_files.add(file)

        time.sleep(60)  # Check for new files every 60 seconds

if __name__ == '__main__':
    monitor_directory()


