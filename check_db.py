from app.database import DatabaseConnection

def escanear_tablas():
    db = DatabaseConnection()
    conn = db.connect()
    if not conn:
        return print("No se pudo conectar a la BD.")
    
    try:
        cursor = conn.cursor()
        
        # Obtener columnas de la tabla creditos
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'creditos';")
        cols_creditos = [row[0] for row in cursor.fetchall()]
        print(f"-> Columnas en CREDITOS: {cols_creditos}")
        
        # Obtener columnas de la tabla pagos
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'pagos';")
        cols_pagos = [row[0] for row in cursor.fetchall()]
        print(f"-> Columnas en PAGOS: {cols_pagos}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    escanear_tablas()
