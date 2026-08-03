import os
import shutil

# Rutas dinámicas seguras (Apunta a Documentos/SistemaCreditos/media/clientes)
HOME_DIR = os.path.expanduser("~")
BASE_DIR = os.path.join(HOME_DIR, "Documents", "SistemaCreditos")
MEDIA_DIR = os.path.join(BASE_DIR, "media", "clientes")

def guardar_archivo_cliente(rfc, origen_path, tipo_doc):
    """Copia un archivo a la carpeta segura en Documentos organizada por RFC."""
    if not origen_path: return None
    
    # Crear carpeta del cliente si no existe
    destino_dir = os.path.join(MEDIA_DIR, rfc)
    os.makedirs(destino_dir, exist_ok=True)
    
    # Obtener extensión original y crear nombre único
    ext = os.path.splitext(origen_path)[1]
    nombre_archivo = f"{tipo_doc}{ext}"
    destino_path = os.path.join(destino_dir, nombre_archivo)
    
    try:
        shutil.copy2(origen_path, destino_path)
        return destino_path
    except Exception as e:
        print(f"Error al guardar archivo: {e}")
        return None