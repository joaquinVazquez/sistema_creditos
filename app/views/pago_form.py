from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer

class PagoForm(QDialog):
    def __init__(self, id_credito, saldo_actual, nombre_cliente, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Abono")
        self.setFixedWidth(450) # Hacemos la ventana más ancha para las fuentes grandes
        
        self.id_credito = id_credito
        self.saldo_actual = float(saldo_actual)
        self.nombre_cliente = nombre_cliente
        
        self.setup_ui()
        
        # UX ZERO-CLICK: Dispara el foco automáticamente tras renderizar la ventana
        QTimer.singleShot(0, self.preparar_input)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 1. Cabecera de Información (Fuente más grande y clara)
        lbl_info = QLabel(f"<div style='font-size: 16px;'>"
                          f"<b style='color:#0078D7;'>Cliente:</b> {self.nombre_cliente}<br>"
                          f"<b style='color:#d9534f;'>Deuda Total:</b> $ {self.saldo_actual:,.2f}"
                          f"</div>")
        lbl_info.setStyleSheet("background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6;")
        layout.addWidget(lbl_info)

        lbl_instruccion = QLabel("<b>Ingrese la cantidad a cobrar:</b>")
        lbl_instruccion.setStyleSheet("font-size: 14px; margin-top: 10px;")
        layout.addWidget(lbl_instruccion)

        # 2. Layout del Input y Botón de Liquidar
        layout_input = QHBoxLayout()

        # INPUT ESTILO PUNTO DE VENTA
        self.spn_monto = QDoubleSpinBox()
        self.spn_monto.setMaximum(self.saldo_actual) 
        self.spn_monto.setMinimum(0.00) 
        self.spn_monto.setValue(0.00)   
        self.spn_monto.setPrefix("$ ")
        self.spn_monto.setDecimals(2)
        
        # UX: Ocultar flechitas inútiles y alinear números a la derecha
        self.spn_monto.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.spn_monto.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # UX: Fuente Gigante e Indicadores Visuales (Verde para dinero)
        self.spn_monto.setStyleSheet("""
            QDoubleSpinBox {
                font-size: 28px; 
                font-weight: bold; 
                padding: 10px; 
                color: #28a745; 
                border: 2px solid #28a745;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #0078D7;
                background-color: #f0f8ff;
            }
        """)

        # BOTÓN LIQUIDAR
        self.btn_liquidar = QPushButton("Liquidar\nDeuda")
        self.btn_liquidar.setFixedSize(100, 60) # Altura fija para alinearse con el input gigante
        self.btn_liquidar.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold; font-size: 14px; border-radius: 8px;")
        self.btn_liquidar.clicked.connect(self.autollenar_saldo)

        layout_input.addWidget(self.spn_monto)
        layout_input.addWidget(self.btn_liquidar)
        layout.addLayout(layout_input)

        # 3. Botón de Procesar Pago
        self.btn_guardar = QPushButton("Procesar Pago e Imprimir Recibo")
        self.btn_guardar.setStyleSheet("background-color: #343a40; color: white; font-weight: bold; font-size: 16px; padding: 15px; margin-top: 15px; border-radius: 8px;")
        self.btn_guardar.clicked.connect(self.accept)

        layout.addWidget(self.btn_guardar)

    def preparar_input(self):
        """UX Poka-Yoke: Coloca el cursor y selecciona los ceros inmediatamente."""
        self.spn_monto.setFocus()
        self.spn_monto.selectAll()

    def autollenar_saldo(self):
        """Copia el saldo total y devuelve el foco al input por si el cajero quiere corregir."""
        self.spn_monto.setValue(self.saldo_actual)
        self.spn_monto.setFocus()

    def get_monto(self):
        return self.spn_monto.value()