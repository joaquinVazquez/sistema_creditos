# app/views/login_view.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

# Importamos el controlador ORM en lugar del gestor de base de datos obsoleto
from app.controllers.usuario_controller import UsuarioController
from app.views.dashboard_view import DashboardView

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Créditos - Acceso")
        self.setFixedSize(350, 250) # UX: Tamaño fijo
        self.controller = UsuarioController() # Instanciación del controlador central
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
        """Delega la validación al controlador ORM y maneja la transición de vistas"""
        username = self.txt_usuario.text().strip()
        password = self.txt_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error de Validación", "Por favor ingrese usuario y contraseña.")
            return

        try:
            # 1. Petición al controlador (retorna un objeto Usuario de SQLAlchemy o None)
            usuario_valido = self.controller.autenticar_usuario(username, password)

            # 2. Evaluación de estado
            if usuario_valido:
                # 3. Transición inyectando propiedades del objeto al Dashboard
                # (Nota técnica: asegúrate de que tu modelo Usuario tenga el atributo 'rol_id',
                # de lo contrario ajusta a 'usuario_valido.rol')
                self.dashboard = DashboardView(usuario_valido.id, getattr(usuario_valido, 'rol_id', 1))
                self.dashboard.show()
                self.close()
            else:
                QMessageBox.warning(self, "Acceso Denegado", "El usuario no existe, está inactivo o la contraseña es incorrecta.")

        except Exception as e:
            QMessageBox.critical(self, "Error de Sistema", f"Fallo en la comunicación con el core de datos:\n{e}")