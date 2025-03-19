import psycopg2

# 連接 PostgreSQL
DATABASE_URL = "postgresql://workout_tracker_db_60zc_user:NNQ3GgiFQfyegkZh7W9LSSxdgQ5uQiGl@dpg-cvbsmpqj1k6c73e1n3og-a.oregon-postgres.render.com/workout_tracker_db_60zc"
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

def print_table_data(cursor, table_name):
    """查詢並顯示表的所有欄位名稱及數據"""
    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]  # 獲取欄位名稱

    print(f"\n✅ {table_name.upper()} 表的數據：")
    print(column_names)  # 列印欄位名稱
    for row in rows:
        print(row)

# 檢查 `users` 表內的數據
print_table_data(cursor, "users")

# 檢查 `todos` 表內的數據
print_table_data(cursor, "todos")

cursor.close()
conn.close()
