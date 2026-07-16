# app/views/login_view.py
import requests
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

from app.views.dashboard_view import DashboardView

# 1. Definición del Servidor (Endpoint de Producción)
API_BASE_URL = "https://sistema-creditos-tw1k.onrender.com"

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Créditos - Acceso")
        self.setFixedSize(350, 250) 
        # Arquitectura limpia: Eliminamos self.controller. La vista ya no gestiona lógica de negocio.
        self.setup_ui()

    def setup_ui(self):
        """Construye y organiza los elementos visuales (Widgets)"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_titulo = QLabel("Bienvenido al Sistema")
        self.lbl_titulo.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 15px;")
        
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Contraseña")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.btn_ingresar = QPushButton("Ingresar")
        self.btn_ingresar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ingresar.setStyleSheet("background-color: #0078D7; color: white; padding: 8px; border-radius: 4px;")
        
        self.txt_password.returnPressed.connect(self.btn_ingresar.click)
        self.txt_usuario.returnPressed.connect(self.btn_ingresar.click)
        self.btn_ingresar.clicked.connect(self.validar_acceso)

        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.txt_usuario)
        layout.addWidget(self.txt_password)
        layout.addWidget(self.btn_ingresar)

        self.setLayout(layout)

    def validar_acceso(self):
        """Envía credenciales a la API de FastAPI mediante HTTP POST"""
        username = self.txt_usuario.text().strip()
        password = self.txt_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error de Validación", "Por favor ingrese usuario y contraseña.")
            return

        try:
            # 2. Configuración del Payload
            # FastAPI (OAuth2) espera los datos en formato Form-Data, por eso usamos 'data=' y no 'json='
            payload = {
                "username": username,
                "password": password
            }

            # 3. Petición a la Nube (Ajusta el endpoint '/login' si tu router tiene otro prefijo)
            # Timeout de 10s para evitar que la interfaz se congele indefinidamente si falla la red
            respuesta = requests.post(f"{API_BASE_URL}/api/v1/auth/login", data=payload, timeout=60)


            # 4. Evaluación de la Respuesta
            if respuesta.status_code == 200:
                datos = respuesta.json()
                token = datos.get("access_token")
                
                # Deuda Técnica a resolver: Tu DashboardView actual espera (usuario_id, rol_id).
                # En un entorno JWT real, esos datos van dentro del token o los pides a un endpoint /me.
                # Por ahora le pasamos parámetros fijos para no romper el inicio del Dashboard.
                self.dashboard = DashboardView(usuario_id=1, rol_id=1)
                # En la siguiente iteración deberás pasarle el token: self.dashboard = DashboardView(token)
                
                self.dashboard.show()
                self.close()
            else:
                print(f"[DEBUG RESPUESTA]: {respuesta.status_code} | {respuesta.text}")
                QMessageBox.warning(self, "Acceso Denegado", "El usuario no existe, está inactivo o la contraseña es incorrecta.")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error de Red", f"Fallo en la comunicación con el servidor:\n{e}")