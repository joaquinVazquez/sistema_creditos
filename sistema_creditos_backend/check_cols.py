from app.database import DatabaseConnection

def revisar_columnas():
    db = DatabaseConnection()
    conn = db.connect()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'clientes';")
        columnas = [row[0] for row in cursor.fetchall()]
        print(f"\n✅ COLUMNAS REALES DE LA TABLA CLIENTES: {columnas}\n")
    finally:
        conn.close()

if __name__ == "__main__":
    revisar_columnas()