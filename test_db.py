from app.open_db_connection import get_db_connection

def main():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    print("Tables en base:", tables)
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
