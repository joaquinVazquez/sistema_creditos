# app/controllers/pago_controller.py
import requests

API_BASE_URL = "https://sistema-creditos-tw1k.onrender.com"

class PagoController:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
    def obtener_creditos_cliente(self, rfc):
        try:
            # Apunta a la ruta exacta que creamos en credito_router.py
            endpoint = f"{API_BASE_URL}/api/v1/creditos/cliente/{rfc}/activos"
            respuesta = requests.get(endpoint, headers=self.headers, timeout=10)
            if respuesta.status_code == 200:
                creditos = respuesta.json()
                return [(c.get("id"), c.get("monto_original"), c.get("saldo_actual"), c.get("estado"), c.get("fecha_inicio")) for c in creditos]
            return []
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED GET CRÉDITOS ACTIVOS]: {e}")
            return []

    def obtener_metricas_cobro(self, id_credito):
        try:
            # Apunta a la ruta de métricas
            endpoint = f"{API_BASE_URL}/api/v1/creditos/{id_credito}/metricas"
            respuesta = requests.get(endpoint, headers=self.headers, timeout=10)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                return float(datos.get("cuota_semanal", 0.0)), int(datos.get("semana_actual", 1))
            return 0.0, 1
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED GET METRICAS]: {e}")
            return 0.0, 1

    def registrar_pago(self, credito_id, monto):
        payload = {
            "credito_id": credito_id,
            "monto": float(monto)
        }
        try:
            # Apunta a la ruta de pagos
            endpoint = f"{API_BASE_URL}/api/v1/pagos/"
            respuesta = requests.post(endpoint, json=payload, headers=self.headers, timeout=10)
            if respuesta.status_code in (200, 201): return True
            print(f"[API HTTP {respuesta.status_code}] Error al registrar pago: {respuesta.text}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED POST PAGO]: {e}")
            return False