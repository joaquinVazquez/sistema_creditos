from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton
from app.controllers.credito_controller import CreditoController

class HistorialView(QDialog):
    def __init__(self, rfc, nombre, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Historial de Créditos - {nombre}")
        self.setMinimumSize(700, 400)
        
        self.rfc_cliente = rfc
        self.controller = CreditoController()
        
        self.setup_ui(nombre)
        self.cargar_historial()

    def setup_ui(self, nombre):
        layout = QVBoxLayout(self)

        # Encabezado
        lbl_info = QLabel(f"<b>Cliente:</b> {nombre} | <b>RFC:</b> {self.rfc_cliente}")
        lbl_info.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(lbl_info)

        # Tabla de Historial
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Folio", "Fecha Otorgado", "Monto Base", "Tasa %", "Semanas", "Saldo Pendiente", "Estado"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Solo lectura
        
        layout.addWidget(self.tabla)

        # Botón de cierre
        self.btn_cerrar = QPushButton("Cerrar Historial")
        self.btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(self.btn_cerrar)

    def cargar_historial(self):
        """Llena la tabla con los datos del controlador."""
        creditos = self.controller.obtener_historial_por_rfc(self.rfc_cliente)
        self.tabla.setRowCount(len(creditos))

        for fila_idx, credito in enumerate(creditos):
            for col_idx, dato in enumerate(credito):
                # Formatear montos con signo de pesos si es la columna 2 o 5
                if col_idx in (2, 5): 
                    valor_str = f"$ {float(dato):,.2f}"
                elif col_idx == 3: # Tasa
                    valor_str = f"{dato}%"
                else:
                    valor_str = str(dato)
                    
                item = QTableWidgetItem(valor_str)
                self.tabla.setItem(fila_idx, col_idx, item)