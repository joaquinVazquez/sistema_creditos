import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QFileDialog, QLabel
from app.utils.file_handler import guardar_archivo_cliente

class ClienteForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Expediente Digital de Cliente")
        self.setFixedWidth(500)
        self.paths = {"foto": None, "ine": None, "domicilio": None, "contrato": None}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        lbl_header = QLabel("Registro de Expediente Digital")
        lbl_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #0078D7; margin-bottom: 10px;")
        layout.addWidget(lbl_header)
        
        # 1. Declaración de inputs
        self.txt_rfc = QLineEdit()
        self.txt_nombre = QLineEdit()
        
        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("Ej. 9671234567")

        # CORRECCIÓN: Creación del input físico para Dirección
        self.txt_direccion = QLineEdit()
        self.txt_direccion.setPlaceholderText("Ej. Av. Central 123, Centro")

        # Botones para seleccionar archivos
        self.btn_foto = QPushButton("Seleccionar Foto")
        self.btn_foto.clicked.connect(lambda: self.seleccionar_archivo("foto"))
        
        self.btn_ine = QPushButton("Cargar INE (PDF/JPG)")
        self.btn_ine.clicked.connect(lambda: self.seleccionar_archivo("ine"))

        # 2. Ensamblado del layout
        form.addRow("RFC:", self.txt_rfc)
        form.addRow("Nombre Completo:", self.txt_nombre)
        form.addRow("Teléfono:", self.txt_telefono)
        form.addRow("Dirección:", self.txt_direccion) # Inyectado a la vista
        form.addRow("Fotografía:", self.btn_foto)
        form.addRow("Identificación (INE):", self.btn_ine)

        # Botón principal
        self.btn_guardar = QPushButton("Guardar Expediente")
        self.btn_guardar.setStyleSheet("background-color: #0078D7; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.btn_guardar.clicked.connect(self.accept)

        layout.addLayout(form)
        layout.addWidget(self.btn_guardar)

        # ==========================================
        # UX OPTIMIZATION: Tab Order & Hotkeys
        # ==========================================
        self.txt_rfc.setFocus()
        
        self.btn_guardar.setDefault(True)
        self.btn_guardar.setAutoDefault(True)

        # La ruta estricta ahora encuentra todos los objetos
        self.setTabOrder(self.txt_rfc, self.txt_nombre)
        self.setTabOrder(self.txt_nombre, self.txt_telefono)
        self.setTabOrder(self.txt_telefono, self.txt_direccion)
        self.setTabOrder(self.txt_direccion, self.btn_guardar)

    def seleccionar_archivo(self, tipo):
        file_path, _ = QFileDialog.getOpenFileName(self, f"Seleccionar {tipo}")
        if file_path:
            self.paths[tipo] = file_path
            sender = self.sender()
            sender.setText("✅ Archivo Cargado")

    def get_data(self):
        rfc = self.txt_rfc.text().strip().upper()
        return {
            "rfc": rfc,
            "nombre": self.txt_nombre.text().strip(),
            "foto": guardar_archivo_cliente(rfc, self.paths["foto"], "foto"),
            "ine": guardar_archivo_cliente(rfc, self.paths["ine"], "ine"),
            "telefono": self.txt_telefono.text().strip(),
            # CORRECCIÓN: Extrae el valor dinámico tecleado en lugar de ""
            "direccion": self.txt_direccion.text().strip() 
        }
    
    def cargar_datos_edicion(self, datos):
        """Pre-llena el formulario y cambia la semántica visual para edición."""
        # Se asume que el controlador envía la tupla completa del cliente
        self.txt_rfc.setText(str(datos[0]) if datos[0] else "")
        self.txt_nombre.setText(str(datos[1]) if datos[1] else "")
        self.txt_telefono.setText(str(datos[2]) if datos[2] else "")
        
        # Validación de longitud por si la base de datos devuelve menos índices
        if len(datos) > 3:
            self.txt_direccion.setText(str(datos[3]) if datos[3] else "")
        
        self.setWindowTitle("Editar Expediente del Cliente")
        self.btn_guardar.setText("Actualizar Datos")
        self.btn_guardar.setStyleSheet("background-color: #ffc107; color: #212529; font-weight: bold; padding: 10px; border-radius: 5px;")