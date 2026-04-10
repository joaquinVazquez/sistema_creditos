# app/views/login_view.py
import bcrypt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from app.database import DatabaseConnection
from app.views.dashboard_view import DashboardView

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Créditos - Acceso")
        self.setFixedSize(350, 250) # UX: Tamaño fijo para ventanas de login
        self.setup_ui()

    def setup_ui(self):
        """Construye y organiza los elementos visuales (Widgets)"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Titulo
        self.lbl_titulo = QLabel("Bienvenido al Sistema")
        self.lbl_titulo.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 15px;")
        
        # Inputs
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Contraseña")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password) # UX: Enmascarar texto
        
        # Botón
        self.btn_ingresar = QPushButton("Ingresar")
        self.btn_ingresar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ingresar.setStyleSheet("background-color: #0078D7; color: white; padding: 8px; border-radius: 4px;")
        
        # UX: Conectar la tecla Enter al botón
        self.txt_password.returnPressed.connect(self.btn_ingresar.click)
        self.txt_usuario.returnPressed.connect(self.btn_ingresar.click)

        # Arquitectura: Conectar la Señal del clic con el Slot de validación
        self.btn_ingresar.clicked.connect(self.validar_acceso)

        # Agregar todo al Layout
        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.txt_usuario)
        layout.addWidget(self.txt_password)
        layout.addWidget(self.btn_ingresar)

        self.setLayout(layout)

    def validar_acceso(self):
        """Regla de Negocio: Valida las credenciales contra PostgreSQL"""
        username = self.txt_usuario.text().strip()
        password = self.txt_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error de Validación", "Por favor ingrese usuario y contraseña.")
            return

        db = DatabaseConnection()
        conn = db.connect()
        if not conn:
            QMessageBox.critical(self, "Error de Red", "No se pudo conectar a la base de datos.")
            return

        try:
            cursor = conn.cursor()
            # Buscamos el hash almacenado para ese usuario
            cursor.execute("SELECT password_hash FROM usuarios WHERE username = %s AND activo = TRUE", (username,))
            resultado = cursor.fetchone()

            if resultado:
                hash_guardado = resultado[0]
                # Comparamos la contraseña plana con el hash de la BD usando bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), hash_guardado.encode('utf-8')):
                    # UX: Mostrar el panel principal y destruir el login
                    self.dashboard = DashboardView()
                    self.dashboard.show()
                    self.close()
                else:
                    QMessageBox.warning(self, "Acceso Denegado", "Contraseña incorrecta.")
            else:
                QMessageBox.warning(self, "Acceso Denegado", "El usuario no existe o está inactivo.")

        except Exception as e:
            QMessageBox.critical(self, "Error de Sistema", f"Ocurrió un error: {e}")
        finally:
            conn.close()