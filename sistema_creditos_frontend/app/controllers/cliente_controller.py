# app/controllers/cliente_controller.py
import requests

# 1. Endpoint centralizado
API_BASE_URL = "https://sistema-creditos-tw1k.onrender.com"

class ClienteController:
    def __init__(self, token: str):
        """
        Inyección de dependencias: El controlador ahora requiere el token JWT 
        para autenticar las peticiones HTTP contra la API.
        """
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.base_url = f"{API_BASE_URL}/api/v1/clientes"

    def obtener_todos(self):
        """Consume el endpoint GET /clientes y formatea para la tabla (UI)."""
        try:
            respuesta = requests.get(self.base_url, headers=self.headers, timeout=15)
            
            if respuesta.status_code == 200:
                clientes = respuesta.json()
                # Compatibilidad inversa: Transformamos el JSON a la lista de tuplas que espera PyQt6
                return [(c.get("rfc"), c.get("nombre_completo"), c.get("telefono"), c.get("created_at")) for c in clientes]
            
            print(f"[API HTTP {respuesta.status_code}] Error al obtener clientes: {respuesta.text}")
            return []
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED GET CLIENTES]: {e}")
            return []

    def guardar_cliente(self, rfc, nombre, telefono, direccion=None, foto_path=None, ine_path=None):
        payload = {
            "rfc": rfc,
            "nombre_completo": nombre,
            "telefono": telefono,
            "direccion": direccion,
            "foto_path": foto_path,
            "ine_path": ine_path
        }
        try:
            respuesta = requests.post(f"{self.base_url}/", json=payload, headers=self.headers, timeout=10)
            
            if respuesta.status_code == 201:
                return "EXITO"
            elif respuesta.status_code == 409:
                return "DUPLICADO" # Detectó el choque de RFC
            else:
                print(f"[ERROR SERVIDOR]: {respuesta.text}")
                return "ERROR"
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED POST CLIENTE]: {e}")
            return "ERROR"

    def obtener_expediente(self, rfc):
        """Consume el endpoint GET /clientes/{rfc} para extraer rutas físicas."""
        try:
            respuesta = requests.get(f"{self.base_url}/{rfc}", headers=self.headers, timeout=10)
            if respuesta.status_code == 200:
                cliente = respuesta.json()
                # Protección: Si el backend envía una lista, evitamos el crash
                if isinstance(cliente, list):
                    return (None, None) 
                
                # Si en el futuro el backend envía un diccionario con las fotos
                if isinstance(cliente, dict):
                    return (cliente.get("foto_path"), cliente.get("ine_path"))
            return None
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED GET EXPEDIENTE]: {e}")
            return None

    def eliminar_cliente(self, rfc):
        """Consume el endpoint DELETE /clientes/{rfc} (que ejecuta el Soft Delete en backend)."""
        try:
            respuesta = requests.delete(f"{self.base_url}/{rfc}", headers=self.headers, timeout=10)
            if respuesta.status_code == 200:
                return True
                
            print(f"[API HTTP {respuesta.status_code}] Error al eliminar: {respuesta.text}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED DELETE CLIENTE]: {e}")
            return False

    def obtener_cliente_por_rfc(self, rfc):
        """Consume el endpoint GET /clientes/{rfc} para prellenar formularios."""
        try:
            respuesta = requests.get(f"{self.base_url}/{rfc}", headers=self.headers, timeout=10)
            if respuesta.status_code == 200:
                cliente = respuesta.json()
                if isinstance(cliente, dict):
                    return (
                        cliente.get("rfc"), 
                        cliente.get("nombre_completo"), 
                        cliente.get("telefono"),
                        cliente.get("direccion") # <-- CRÍTICO: Descargar la dirección
                    )
            return None
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED GET CLIENTE RFC]: {e}")
            return None

    def actualizar_cliente(self, rfc_original, datos_nuevos):
        """Consume el endpoint PUT /clientes/{rfc}."""
        payload = {
            "rfc": datos_nuevos.get('rfc'),
            "nombre_completo": datos_nuevos.get('nombre'),
            "telefono": datos_nuevos.get('telefono'),
            "direccion": datos_nuevos.get('direccion'), # <-- CRÍTICO: Enviar la dirección
            "foto_path": datos_nuevos.get('foto'),
            "ine_path": datos_nuevos.get('ine')
        }
        # Filtramos None para no borrar fotos si no se subió una nueva
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            respuesta = requests.put(f"{self.base_url}/{rfc_original}", json=payload, headers=self.headers, timeout=10)
            return respuesta.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED PUT CLIENTE]: {e}")
            return False