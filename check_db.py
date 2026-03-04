import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BeautyVibe.settings')
django.setup()

from django.db import connection

def check_table_info(table_name):
    with connection.cursor() as cursor:
        # Check column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"Columns for {table_name}:")
        for col in columns:
            print(f"  {col[1]}: type={col[2]}, notnull={col[3]}, pk={col[5]}")
        
        # Check actual SQL used to create table
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        sql = cursor.fetchone()
        if sql:
            print(f"\nCreate SQL for {table_name}:\n{sql[0]}")

check_table_info('Products_product')
