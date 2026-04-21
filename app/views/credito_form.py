# app/views/credito_form.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox, QPushButton, QLabel

class CreditoForm(QDialog):
    def __init__(self, rfc, nombre, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Otorgar Nuevo Crédito")
        self.setFixedWidth(350)
        
        # Guardamos el RFC para enviarlo al controlador después
        self.rfc_cliente = rfc 
        
        self.setup_ui(nombre)

    def setup_ui(self, nombre):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # UX: Mostrar a quién le estamos prestando (Solo Lectura)
        lbl_cliente = QLabel(f"<b>Cliente:</b> {nombre}<br><b>RFC:</b> {self.rfc_cliente}")
        lbl_cliente.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(lbl_cliente)

        # Inputs con tipos de datos estrictos (evita que escriban letras en números)
        self.spn_monto = QDoubleSpinBox()
        self.spn_monto.setMaximum(1000000.00) # Límite de 1 millón
        self.spn_monto.setPrefix("$ ")
        
        self.spn_tasa = QDoubleSpinBox()
        self.spn_tasa.setSuffix(" %")
        
        self.spn_plazos = QSpinBox()
        self.spn_plazos.setMinimum(1)
        self.spn_plazos.setMaximum(120) # Hasta 10 años
        self.spn_plazos.setSuffix(" meses")

        form.addRow("Monto a prestar:", self.spn_monto)
        form.addRow("Tasa Mensual:", self.spn_tasa)
        form.addRow("Plazo:", self.spn_plazos)

        self.btn_guardar = QPushButton("Generar Crédito")
        self.btn_guardar.setStyleSheet("background-color: #ff8c00; color: white; font-weight: bold; padding: 5px;")
        self.btn_guardar.clicked.connect(self.accept)

        layout.addLayout(form)
        layout.addWidget(self.btn_guardar)

    def get_data(self):
        return {
            "rfc": self.rfc_cliente,
            "monto": self.spn_monto.value(),
            "tasa": self.spn_tasa.value(),
            "plazos": self.spn_plazos.value()
        }