# app/controllers/credito_controller.py
import requests

API_BASE_URL = "https://sistema-creditos-tw1k.onrender.com"

class CreditoController:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.base_url = f"{API_BASE_URL}/api/v1/creditos"

    def crear_credito(self, rfc_cliente, monto, tasa_global, plazos_semanas):
        payload = {
            "rfc_cliente": rfc_cliente,
            "monto": monto,
            "tasa_global": tasa_global,
            "plazos_semanas": plazos_semanas
        }
        try:
            respuesta = requests.post(self.base_url, json=payload, headers=self.headers, timeout=10)
            if respuesta.status_code in (200, 201): return True
            print(f"[API HTTP {respuesta.status_code}] Error al crear crédito: {respuesta.text}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED POST CRÉDITO]: {e}")
            return False

    def obtener_historial_por_rfc(self, rfc_cliente):
        try:
            respuesta = requests.get(f"{self.base_url}/historial/{rfc_cliente}", headers=self.headers, timeout=10)
            if respuesta.status_code == 200:
                creditos = respuesta.json()
                return [(c.get("id"), c.get("fecha_inicio"), c.get("monto_original"), c.get("tasa_interes_global"), c.get("plazos_semanas"), c.get("saldo_actual"), c.get("estado")) for c in creditos]
            return []
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED GET HISTORIAL]: {e}")
            return []

    def obtener_pagos_por_credito(self, credito_id):
        try:
            respuesta = requests.get(f"{self.base_url}/{credito_id}/pagos", headers=self.headers, timeout=10)
            if respuesta.status_code == 200:
                pagos = respuesta.json()
                return [(p.get("id"), p.get("fecha"), p.get("monto"), p.get("username")) for p in pagos]
            return []
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED GET PAGOS]: {e}")
            return []
        
    def obtener_metricas_dashboard(self):
        """
        Consume el endpoint de métricas operativas del Dashboard.
        Retorna la tupla exacta requerida por la UI: (capital, ingresos, clientes)
        """
        # Suponiendo que la ruta original de KPIs en tu backend era esta:
        endpoint = f"{API_BASE_URL}/api/v1/dashboard/metricas"
        
        try:
            respuesta = requests.get(endpoint, headers=self.headers, timeout=10)
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                return (
                    float(datos.get("capital_activo", 0.0)), 
                    float(datos.get("ingresos_hoy", 0.0)), 
                    int(datos.get("clientes_activos", 0))
                )
                
            print(f"[API HTTP {respuesta.status_code}] Error obteniendo KPIs: {respuesta.text}")
            return (0.0, 0.0, 0)
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR RED GET KPIs]: {e}")
            return (0.0, 0.0, 0)