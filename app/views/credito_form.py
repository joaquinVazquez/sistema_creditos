from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QDoubleSpinBox, QSpinBox, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer

class CreditoForm(QDialog):
    def __init__(self, rfc, nombre, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Otorgar Nuevo Crédito")
        self.setFixedWidth(450) # Ancho unificado con el módulo de cobro
        
        self.rfc = rfc
        self.nombre = nombre
        
        self.setup_ui()
        
        # UX ZERO-CLICK: Pone el cursor en el monto inmediatamente
        QTimer.singleShot(0, self.preparar_input)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 1. Ancla Visual (Header de Contexto)
        lbl_info = QLabel(f"<div style='font-size: 16px;'>"
                          f"<b style='color:#0078D7;'>Autorizar Crédito a:</b><br>"
                          f"<span style='font-size: 18px; color:#333333;'>{self.nombre}</span><br>"
                          f"<span style='font-size: 13px; color:#6c757d;'>RFC: {self.rfc}</span>"
                          f"</div>")
        lbl_info.setStyleSheet("background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; margin-bottom: 15px;")
        layout.addWidget(lbl_info)

        # 2. Formulario Principal
        form = QFormLayout()
        form.setSpacing(15)

        # INPUT MONTO
        self.spn_monto = QDoubleSpinBox()
        self.spn_monto.setMaximum(500000.00) 
        self.spn_monto.setMinimum(0.00)
        self.spn_monto.setValue(0.00)
        self.spn_monto.setPrefix("$ ")
        self.spn_monto.setDecimals(2)
        self.spn_monto.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.spn_monto.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.spn_monto.setStyleSheet("""
            QDoubleSpinBox {
                font-size: 24px; font-weight: bold; padding: 8px; 
                color: #0078D7; border: 2px solid #0078D7; border-radius: 8px; background-color: #ffffff;
            }
            QDoubleSpinBox:focus { background-color: #f0f8ff; border: 2px solid #ff8c00; }
        """)

        # INPUT TASA
        self.spn_tasa = QDoubleSpinBox()
        self.spn_tasa.setSuffix(" %")
        self.spn_tasa.setDecimals(2)
        self.spn_tasa.setMaximum(100.00)
        self.spn_tasa.setValue(10.00)
        self.spn_tasa.setStyleSheet("font-size: 16px; padding: 6px; border-radius: 4px; border: 1px solid #ced4da;")

        # ==========================================
        # INPUT PLAZOS + ATAJOS RÁPIDOS
        # ==========================================
        layout_plazos = QHBoxLayout()
        
        self.spn_plazos = QSpinBox()
        self.spn_plazos.setSuffix(" Semanas")
        self.spn_plazos.setMinimum(1)
        self.spn_plazos.setMaximum(156)
        self.spn_plazos.setValue(17) # Inicia en la primera base
        self.spn_plazos.setStyleSheet("font-size: 16px; padding: 6px; border-radius: 4px; border: 1px solid #ced4da;")
        
        layout_plazos.addWidget(self.spn_plazos)

        # Botones de Atajo (17, 34 y 52 Semanas)
        estilo_atajo = "background-color: #e9ecef; color: #495057; font-weight: bold; border: 1px solid #ced4da; padding: 5px; border-radius: 4px;"
        
        btn_17 = QPushButton("17 Sem")
        btn_17.setStyleSheet(estilo_atajo)
        btn_17.clicked.connect(lambda: self.spn_plazos.setValue(17))
        
        btn_34 = QPushButton("34 Sem")
        btn_34.setStyleSheet(estilo_atajo)
        btn_34.clicked.connect(lambda: self.spn_plazos.setValue(34))
        
        btn_52 = QPushButton("52 Sem")
        btn_52.setStyleSheet(estilo_atajo)
        btn_52.clicked.connect(lambda: self.spn_plazos.setValue(52))

        layout_plazos.addWidget(btn_17)
        layout_plazos.addWidget(btn_34)
        layout_plazos.addWidget(btn_52)
        # ==========================================

        # Ensamblar formulario
        lbl_monto = QLabel("<b>Monto a Financiar:</b>")
        lbl_monto.setStyleSheet("font-size: 14px;")
        form.addRow(lbl_monto, self.spn_monto)
        
        lbl_tasa = QLabel("<b>Tasa de Interés:</b>")
        lbl_tasa.setStyleSheet("font-size: 14px;")
        form.addRow(lbl_tasa, self.spn_tasa)
        
        lbl_plazo = QLabel("<b>Plazo de Pago:</b>")
        lbl_plazo.setStyleSheet("font-size: 14px;")
        form.addRow(lbl_plazo, layout_plazos) # Insertamos el layout completo aquí

        layout.addLayout(form)

        # 3. Botón de Acción Principal
        self.btn_guardar = QPushButton("Autorizar y Generar Crédito")
        self.btn_guardar.setStyleSheet("""
            QPushButton { background-color: #ff8c00; color: white; font-weight: bold; font-size: 16px; padding: 15px; margin-top: 10px; border-radius: 8px; }
            QPushButton:hover { background-color: #e07b00; }
        """)
        self.btn_guardar.clicked.connect(self.accept)

        layout.addWidget(self.btn_guardar)

    def preparar_input(self):
        """Poka-Yoke visual: Listo para teclear el monto de inmediato."""
        self.spn_monto.setFocus()
        self.spn_monto.selectAll()

    def get_data(self):
        """Retorna el diccionario de datos para el controlador."""
        return {
            "rfc": self.rfc,
            "monto": self.spn_monto.value(),
            "tasa": self.spn_tasa.value(),
            "plazos": self.spn_plazos.value()
        }