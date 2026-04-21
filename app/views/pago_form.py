from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton, QLabel, QMessageBox

class PagoForm(QDialog):
    def __init__(self, credito_id, saldo_pendiente, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Abono")
        self.credito_id = credito_id
        self.saldo_max = saldo_pendiente
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        lbl_info = QLabel(f"<b>Crédito ID:</b> {self.credito_id}<br><b>Saldo Pendiente:</b> ${self.saldo_max}")
        layout.addWidget(lbl_info)

        form = QFormLayout()
        self.spn_pago = QDoubleSpinBox()
        self.spn_pago.setMaximum(float(self.saldo_max)) # Poka-Yoke: No puede pagar más de lo que debe
        self.spn_pago.setPrefix("$ ")
        
        form.addRow("Monto del Abono:", self.spn_pago)
        layout.addLayout(form)

        self.btn_confirmar = QPushButton("Confirmar Pago")
        self.btn_confirmar.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        self.btn_confirmar.clicked.connect(self.accept)
        layout.addWidget(self.btn_confirmar)

    def get_monto(self):
        return self.spn_pago.value()