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
        """Consume el endpoint POST /clientes."""
        payload = {
            "rfc": rfc,
            "nombre_completo": nombre,
            "telefono": telefono,
            "direccion": direccion,
            "foto_path": foto_path,
            "ine_path": ine_path
        }
        try:
            respuesta = requests.post(self.base_url, json=payload, headers=self.headers, timeout=10)
            if respuesta.status_code in (200, 201):
                return True
                
            print(f"[API HTTP {respuesta.status_code}] Error al guardar: {respuesta.text}")
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED POST CLIENTE]: {e}")
            return False

    def obtener_expediente(self, rfc):
        """Consume el endpoint GET /clientes/{rfc} para extraer rutas físicas."""
        try:
            respuesta = requests.get(f"{self.base_url}/{rfc}", headers=self.headers, timeout=10)
            if respuesta.status_code == 200:
                cliente = respuesta.json()
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
                return (cliente.get("rfc"), cliente.get("nombre_completo"), cliente.get("telefono"))
            return None
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED GET CLIENTE RFC]: {e}")
            return None

    def actualizar_cliente(self, rfc_original, datos_nuevos):
        """Consume el endpoint PUT o PATCH /clientes/{rfc}."""
        # Adaptamos el diccionario 'datos_nuevos' al formato JSON esperado
        payload = {
            "rfc": datos_nuevos.get('rfc'),
            "nombre_completo": datos_nuevos.get('nombre'),
            "telefono": datos_nuevos.get('telefono')
        }
        # Filtramos valores None para no sobreescribir datos accidentalmente
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            respuesta = requests.put(f"{self.base_url}/{rfc_original}", json=payload, headers=self.headers, timeout=10)
            if respuesta.status_code == 200:
                return True
                
            print(f"[API HTTP {respuesta.status_code}] Error al actualizar: {respuesta.text}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED PUT CLIENTE]: {e}")
            return False