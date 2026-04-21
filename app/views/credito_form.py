# app/views/credito_form.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox, QPushButton, QLabel
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox, QComboBox, QPushButton, QLabel
from PyQt6.QtCore import Qt

class CreditoForm(QDialog):
    def __init__(self, rfc, nombre, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Otorgar Crédito - Planes Semanales")
        self.setFixedWidth(400)
        
        self.rfc_cliente = rfc 
        
        # Diccionario de Planes Financieros: {Nombre: (Semanas, Tasa%)}
        self.planes = {
            "Corto": (17, 16.0),
            "Estándar": (34, 28.0),
            "Extendido": (52, 36.0)
        }
        
        self.setup_ui(nombre)
        self.calcular_proyeccion() # Ejecutar cálculo inicial

    def setup_ui(self, nombre):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        lbl_cliente = QLabel(f"<b>Cliente:</b> {nombre}<br><b>RFC:</b> {self.rfc_cliente}")
        layout.addWidget(lbl_cliente)

        # Monto a financiar
        self.spn_monto = QDoubleSpinBox()
        self.spn_monto.setMaximum(1000000.00)
        self.spn_monto.setPrefix("$ ")
        # UX Reactiva: Si cambia el monto, recalcular
        self.spn_monto.valueChanged.connect(self.calcular_proyeccion)

        # Selector de Planes
        self.cmb_planes = QComboBox()
        for plan, datos in self.planes.items():
            semanas, tasa = datos
            self.cmb_planes.addItem(f"{plan} ({semanas} sem - {tasa}%)", plan)
        # UX Reactiva: Si cambia el plan, recalcular
        self.cmb_planes.currentIndexChanged.connect(self.calcular_proyeccion)

        # Etiquetas de solo lectura para la proyección financiera
        self.lbl_cuota = QLabel("$ 0.00")
        self.lbl_cuota.setStyleSheet("color: #28a745; font-weight: bold; font-size: 14px;")
        
        self.lbl_total = QLabel("$ 0.00")
        self.lbl_total.setStyleSheet("color: #d9534f; font-weight: bold; font-size: 14px;")

        form.addRow("Monto Original:", self.spn_monto)
        form.addRow("Plan Financiero:", self.cmb_planes)
        form.addRow("Cuota Semanal:", self.lbl_cuota)
        form.addRow("Total a Pagar:", self.lbl_total)

        self.btn_guardar = QPushButton("Confirmar y Generar")
        self.btn_guardar.setStyleSheet("background-color: #ff8c00; color: white; font-weight: bold; padding: 8px;")
        self.btn_guardar.clicked.connect(self.accept)

        layout.addLayout(form)
        layout.addWidget(self.btn_guardar)

    def calcular_proyeccion(self):
        """Calcula el interés y la cuota en tiempo real para UX visual."""
        monto = self.spn_monto.value()
        if monto == 0:
            self.lbl_cuota.setText("$ 0.00")
            self.lbl_total.setText("$ 0.00")
            return

        nombre_plan = self.cmb_planes.currentData()
        semanas, tasa = self.planes[nombre_plan]

        interes = monto * (tasa / 100.0)
        total_pagar = monto + interes
        cuota_semanal = total_pagar / semanas

        self.lbl_total.setText(f"$ {total_pagar:,.2f}")
        self.lbl_cuota.setText(f"$ {cuota_semanal:,.2f}")

    def get_data(self):
        """Empaqueta los datos para el controlador."""
        nombre_plan = self.cmb_planes.currentData()
        semanas, tasa = self.planes[nombre_plan]
        return {
            "rfc": self.rfc_cliente,
            "monto": self.spn_monto.value(),
            "tasa": tasa,
            "plazos": semanas
        }
    
    def obtener_historial_por_rfc(self, rfc_cliente):
        """Obtiene todos los créditos históricos de un cliente."""
        conn = self.db.connect()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT cr.id, cr.fecha_otorgamiento, cr.monto_original, 
                       cr.tasa_interes_global, cr.plazos_semanas, cr.saldo_restante, cr.estado
                FROM creditos cr
                JOIN clientes cl ON cr.cliente_id = cl.id
                WHERE cl.rfc = %s
                ORDER BY cr.fecha_otorgamiento DESC, cr.id DESC
            """
            cursor.execute(query, (rfc_cliente,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[ERROR SQL] No se pudo obtener el historial: {e}")
            return []
        finally:
            conn.close()