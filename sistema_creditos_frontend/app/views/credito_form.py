from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QDoubleSpinBox, QSpinBox, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer

class CreditoForm(QDialog):
    def __init__(self, rfc, nombre, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Autorización de Crédito")
        self.setFixedWidth(480)
        
        self.rfc = rfc
        self.nombre = nombre
        
        # Mapeo de reglas de negocio: Plazo -> Tasa sugerida
        self.REGLAS_TASAS = {17: 16.0, 34: 28.0, 52: 36.0}
        
        self.setup_ui()
        QTimer.singleShot(0, self.preparar_input)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 1. Header de Contexto
        lbl_info = QLabel(f"<div style='font-size: 15px;'>"
                          f"<b style='color:#0078D7;'>Cliente:</b> {self.nombre}<br>"
                          f"<span style='color:#6c757d;'>RFC: {self.rfc}</span>"
                          f"</div>")
        lbl_info.setStyleSheet("background-color: #f8f9fa; padding: 12px; border-radius: 8px; border: 1px solid #dee2e6;")
        layout.addWidget(lbl_info)

        # 2. Formulario de Captura
        form = QFormLayout()
        form.setSpacing(12)

        # MONTO
        self.spn_monto = QDoubleSpinBox()
        self.spn_monto.setMaximum(500000.0)
        self.spn_monto.setPrefix("$ ")
        self.spn_monto.setDecimals(2)
        self.spn_monto.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.spn_monto.setStyleSheet("font-size: 20px; font-weight: bold; color: #0078D7; padding: 5px;")
        self.spn_monto.valueChanged.connect(self.actualizar_calculos) # Escucha cambios

        # PLAZOS CON ATAJOS
        layout_plazos = QHBoxLayout()
        self.spn_plazos = QSpinBox()
        self.spn_plazos.setRange(1, 156)
        self.spn_plazos.setValue(17)
        self.spn_plazos.setSuffix(" Sem")
        self.spn_plazos.valueChanged.connect(self.actualizar_calculos) # Escucha cambios
        
        layout_plazos.addWidget(self.spn_plazos)

        # Botones de Atajo (Inyectan tasa automáticamente)
        for p in [17, 34, 52]:
            btn = QPushButton(f"{p}")
            btn.setFixedWidth(40)
            btn.setStyleSheet("background-color: #e9ecef; font-weight: bold; padding: 5px;")
            btn.clicked.connect(lambda ch, val=p: self.aplicar_plazo_base(val))
            layout_plazos.addWidget(btn)

        # TASA
        self.spn_tasa = QDoubleSpinBox()
        self.spn_tasa.setSuffix(" %")
        self.spn_tasa.setValue(16.0) # Inicia con la tasa de 17 semanas
        self.spn_tasa.valueChanged.connect(self.actualizar_calculos) # Escucha cambios

        form.addRow("<b>Monto a Financiar:</b>", self.spn_monto)
        form.addRow("<b>Plazo de Pago:</b>", layout_plazos)
        form.addRow("<b>Tasa de Interés:</b>", self.spn_tasa)
        layout.addLayout(form)

        # 3. PANEL DE PROYECCIÓN (Resultados Dinámicos)
        self.frame_resumen = QFrame()
        self.frame_resumen.setStyleSheet("background-color: #eef6ff; border: 2px solid #0078D7; border-radius: 8px;")
        layout_resumen = QVBoxLayout(self.frame_resumen)
        
        self.lbl_pago_semanal = QLabel("Pago Semanal: <b>$ 0.00</b>")
        self.lbl_total_pagar = QLabel("Total a Pagar: <b>$ 0.00</b>")
        
        self.lbl_pago_semanal.setStyleSheet("font-size: 18px; color: #004a8b; border: none;")
        self.lbl_total_pagar.setStyleSheet("font-size: 14px; color: #555; border: none;")
        
        layout_resumen.addWidget(self.lbl_pago_semanal)
        layout_resumen.addWidget(self.lbl_total_pagar)
        layout.addWidget(self.frame_resumen)

        # 4. Botón de Acción
        self.btn_guardar = QPushButton("Autorizar y Generar Crédito")
        self.btn_guardar.setStyleSheet("background-color: #ff8c00; color: white; font-weight: bold; font-size: 16px; padding: 12px; margin-top: 10px; border-radius: 8px;")
        self.btn_guardar.clicked.connect(self.accept)
        layout.addWidget(self.btn_guardar)

    def aplicar_plazo_base(self, plazo):
        """Aplica el plazo y la tasa correspondiente de forma atómica."""
        self.spn_plazos.setValue(plazo)
        if plazo in self.REGLAS_TASAS:
            self.spn_tasa.setValue(self.REGLAS_TASAS[plazo])
        self.actualizar_calculos()

    def actualizar_calculos(self):
        """Motor de cálculo en tiempo real."""
        monto = self.spn_monto.value()
        tasa_porc = self.spn_tasa.value() / 100
        semanas = self.spn_plazos.value()

        if semanas > 0:
            total = monto * (1 + tasa_porc)
            semanal = total / semanas
            
            self.lbl_pago_semanal.setText(f"Pago Semanal: <b style='font-size: 22px;'>$ {semanal:,.2f}</b>")
            self.lbl_total_pagar.setText(f"Monto Total con Interés: <b>$ {total:,.2f}</b>")
        else:
            self.lbl_pago_semanal.setText("Pago Semanal: <b>$ 0.00</b>")

    def preparar_input(self):
        self.spn_monto.setFocus()
        self.spn_monto.selectAll()

    def get_data(self):
        return {
            "rfc": self.rfc,
            "monto": self.spn_monto.value(),
            "tasa": self.spn_tasa.value(),
            "plazos": self.spn_plazos.value()
        }