from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt

class PagoForm(QDialog):
    def __init__(self, id_credito, saldo_actual, nombre_cliente, cuota_semanal=0.0, semana_actual=1, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Terminal de Cobro")
        self.setFixedWidth(400)
        
        # Estado local
        self.id_credito = id_credito
        self.saldo_actual = float(saldo_actual)
        self.nombre_cliente = nombre_cliente
        self.cuota_semanal = float(cuota_semanal)
        self.semana_actual = int(semana_actual)
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # --- PANEL INFORMATIVO ---
        lbl_header = QLabel(f"Cobro a: {self.nombre_cliente}")
        lbl_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;")
        
        lbl_saldo = QLabel(f"Saldo Pendiente: ${self.saldo_actual:,.2f}")
        lbl_saldo.setStyleSheet("font-size: 14px; font-weight: bold; color: #dc3545;")
        
        lbl_semana = QLabel(f"Semana a Pagar: #{self.semana_actual}")
        lbl_semana.setStyleSheet("font-size: 14px; color: #0078D7; font-weight: bold;")
        
        lbl_cuota = QLabel(f"Cuota Sugerida: ${self.cuota_semanal:,.2f}")
        lbl_cuota.setStyleSheet("font-size: 14px; color: #28a745; font-weight: bold; margin-bottom: 10px;")

        layout.addWidget(lbl_header)
        layout.addWidget(lbl_saldo)
        layout.addWidget(lbl_semana)
        layout.addWidget(lbl_cuota)

        # --- INPUT ESTANDARIZADO ---
        self.txt_monto = QLineEdit()
        # Autocompletar con la cuota sugerida para acelerar el cobro
        self.txt_monto.setText(f"{self.cuota_semanal:.2f}" if self.cuota_semanal > 0 else "")
        self.txt_monto.setPlaceholderText("0.00")
        self.txt_monto.setStyleSheet("font-size: 20px; padding: 5px; font-weight: bold;")

        form.addRow("Monto a Recibir ($):", self.txt_monto)

        self.btn_guardar = QPushButton("Procesar Pago")
        self.btn_guardar.setStyleSheet("background-color: #28a745; color: white; padding: 12px; font-weight: bold; font-size: 14px; border-radius: 5px;")
        self.btn_guardar.clicked.connect(self.accept)

        layout.addLayout(form)
        layout.addWidget(self.btn_guardar)

        # ==========================================
        # UX OPTIMIZATION: Tab Order & Hotkeys
        # ==========================================
        self.txt_monto.setFocus()
        self.txt_monto.selectAll() # Selecciona el texto por defecto para sobreescribirlo rápido si es un abono parcial
        
        self.btn_guardar.setDefault(True)
        self.btn_guardar.setAutoDefault(True)

    def get_monto(self):
        monto_str = self.txt_monto.text().strip().replace(',', '')
        try:
            return float(monto_str)
        except ValueError:
            return 0.0