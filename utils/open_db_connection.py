import pymysql
from utils.config import DB_CONFIG

def get_db_connection():
    print(f"DEBUG: Tentative de connexion à la BDD {DB_CONFIG['host']}:{DB_CONFIG['port']} ...")
    try:
        print(DB_CONFIG)
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
        print("DEBUG: Connexion réussie à la base de données.")
        return connection
    except pymysql.MySQLError as e:
        print(f"ERREUR: Échec de connexion à la base de données : {e}")
        raise  # Relance l’exception pour ne pas masquer l’erreur