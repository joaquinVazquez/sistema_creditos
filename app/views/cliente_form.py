from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QPushButton, QFileDialog, QLabel
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

        self.txt_rfc = QLineEdit()
        self.txt_nombre = QLineEdit()

        lbl_header = QLabel("Registro de Expediente Digital")
        lbl_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #0078D7; margin-bottom: 10px;")
        layout.addWidget(lbl_header)
        
        # Botones para seleccionar archivos
        self.btn_foto = QPushButton("Seleccionar Foto")
        self.btn_foto.clicked.connect(lambda: self.seleccionar_archivo("foto"))
        
        self.btn_ine = QPushButton("Cargar INE (PDF/JPG)")
        self.btn_ine.clicked.connect(lambda: self.seleccionar_archivo("ine"))

        form.addRow("RFC:", self.txt_rfc)
        form.addRow("Nombre:", self.txt_nombre)
        form.addRow("Fotografía:", self.btn_foto)
        form.addRow("Identificación (INE):", self.btn_ine)

        self.btn_guardar = QPushButton("Guardar Expediente Completo")
        self.btn_guardar.setStyleSheet("background-color: #0078D7; color: white; padding: 10px;")
        self.btn_guardar.clicked.connect(self.accept)

        layout.addLayout(form)
        layout.addWidget(self.btn_guardar)

    def seleccionar_archivo(self, tipo):
        file_path, _ = QFileDialog.getOpenFileName(self, f"Seleccionar {tipo}")
        if file_path:
            self.paths[tipo] = file_path
            # Feedback visual simple en el botón
            sender = self.sender()
            sender.setText("✅ Archivo Cargado")

    def get_data(self):
        rfc = self.txt_rfc.text().strip().upper()
        # Procesar archivos físicamente antes de retornar los datos
        return {
            "rfc": rfc,
            "nombre": self.txt_nombre.text().strip(),
            "foto": guardar_archivo_cliente(rfc, self.paths["foto"], "foto"),
            "ine": guardar_archivo_cliente(rfc, self.paths["ine"], "ine"),
            "telefono": "", # Mantener consistencia con tu controlador
            "direccion": ""
        }