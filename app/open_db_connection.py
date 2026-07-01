import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    """Ouvre une connexion vers la base MySQL."""
    connection = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        port=DB_CONFIG['port']
    )
    return connection
