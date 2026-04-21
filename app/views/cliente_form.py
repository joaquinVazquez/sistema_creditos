from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox

class ClienteForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Nuevo Cliente")
        self.setFixedWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_rfc = QLineEdit()
        self.txt_nombre = QLineEdit()
        self.txt_telefono = QLineEdit()
        self.txt_direccion = QTextEdit()
        self.txt_direccion.setMaximumHeight(80)

        form.addRow("RFC:", self.txt_rfc)
        form.addRow("Nombre Completo:", self.txt_nombre)
        form.addRow("Teléfono:", self.txt_telefono)
        form.addRow("Dirección:", self.txt_direccion)

        self.btn_guardar = QPushButton("Guardar Cliente")
        self.btn_guardar.setStyleSheet("background-color: #0078D7; color: white; font-weight: bold; padding: 5px;")
        self.btn_guardar.clicked.connect(self.accept) # Intentar cerrar con éxito

        layout.addLayout(form)
        layout.addWidget(self.btn_guardar)

    def get_data(self):
        """Extrae los datos limpios del formulario."""
        return {
            "rfc": self.txt_rfc.text().strip().upper(),
            "nombre": self.txt_nombre.text().strip(),
            "telefono": self.txt_telefono.text().strip(),
            "direccion": self.txt_direccion.toPlainText().strip()
        }