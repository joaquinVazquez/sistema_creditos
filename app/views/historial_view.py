from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QPushButton, QSplitter)
from PyQt6.QtCore import Qt
from app.controllers.credito_controller import CreditoController

class HistorialView(QDialog):
    def __init__(self, rfc, nombre, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Estado de Cuenta Detallado - {nombre}")
        self.setMinimumSize(850, 600) # UX: Ventana más grande para que respire la información
        
        self.rfc_cliente = rfc
        self.controller = CreditoController()
        
        # Aplicar diseño global moderno (QSS)
        self.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #f8f9fa;
                background-color: #ffffff;
                font-size: 13px;
                gridline-color: #dee2e6;
            }
            QHeaderView::section {
                background-color: #343a40;
                color: white;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #dee2e6;
            }
            QLabel { font-size: 14px; }
        """)
        
        self.setup_ui(nombre)
        self.cargar_creditos()

    def setup_ui(self, nombre):
        layout = QVBoxLayout(self)

        # 1. Cabecera de Información
        lbl_info = QLabel(f"<b style='color:#0078D7; font-size:16px;'>Cliente:</b> {nombre}   |   <b style='color:#0078D7; font-size:16px;'>RFC:</b> {self.rfc_cliente}")
        lbl_info.setStyleSheet("background-color: #e9ecef; padding: 10px; border-radius: 5px; margin-bottom: 5px;")
        layout.addWidget(lbl_info)

        # 2. Splitter (Permite al usuario ajustar el tamaño entre las dos tablas)
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # --- TABLA SUPERIOR (Maestro): Lista de Créditos ---
        self.lbl_titulo_creditos = QLabel("<b>1. Historial de Créditos (Seleccione uno para ver abonos)</b>")
        self.tabla_creditos = QTableWidget()
        self.tabla_creditos.setAlternatingRowColors(True)
        self.tabla_creditos.setColumnCount(7)
        self.tabla_creditos.setHorizontalHeaderLabels([
            "ID Crédito", "Fecha Otorgado", "Monto Base", "Tasa %", "Semanas", "Saldo Pendiente", "Estado"
        ])
        self.tabla_creditos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_creditos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_creditos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) # UX: Seleccionar fila completa
        self.tabla_creditos.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Conectar el clic en la tabla superior para disparar la carga de la tabla inferior
        self.tabla_creditos.itemSelectionChanged.connect(self.cargar_abonos_de_seleccion)

        # --- TABLA INFERIOR (Detalle): Lista de Abonos ---
        self.lbl_titulo_abonos = QLabel("<b>2. Sábana de Abonos (Del crédito seleccionado)</b>")
        self.tabla_abonos = QTableWidget()
        self.tabla_abonos.setAlternatingRowColors(True)
        self.tabla_abonos.setColumnCount(4)
        self.tabla_abonos.setHorizontalHeaderLabels(["Folio Recibo", "Fecha y Hora del Abono", "Monto Pagado", "Cajero Operador"])
        self.tabla_abonos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_abonos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Ensamblar vistas en el splitter
        splitter.addWidget(self.lbl_titulo_creditos)
        splitter.addWidget(self.tabla_creditos)
        splitter.addWidget(self.lbl_titulo_abonos)
        splitter.addWidget(self.tabla_abonos)
        
        layout.addWidget(splitter)

        # Botón de cierre
        self.btn_cerrar = QPushButton("Cerrar Panel")
        self.btn_cerrar.setStyleSheet("background-color: #dc3545; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        self.btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(self.btn_cerrar)

    def cargar_creditos(self):
        """Carga la matriz de créditos en la tabla superior."""
        creditos = self.controller.obtener_historial_por_rfc(self.rfc_cliente)
        self.tabla_creditos.setRowCount(len(creditos))

        for fila_idx, credito in enumerate(creditos):
            for col_idx, dato in enumerate(credito):
                if col_idx in (2, 5): 
                    valor_str = f"$ {float(dato):,.2f}"
                elif col_idx == 3:
                    valor_str = f"{dato}%"
                else:
                    valor_str = str(dato)
                
                item = QTableWidgetItem(valor_str)
                # UX: Alinear los números a la derecha
                if col_idx in (2, 3, 4, 5): item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else: item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                self.tabla_creditos.setItem(fila_idx, col_idx, item)

    def cargar_abonos_de_seleccion(self):
        """Se dispara al hacer clic en un crédito. Busca y renderiza sus abonos."""
        self.tabla_abonos.setRowCount(0) # Limpiar tabla inferior
        
        fila_seleccionada = self.tabla_creditos.currentRow()
        if fila_seleccionada < 0: return # No hay nada seleccionado
        
        # Extraer el ID del crédito de la primera columna (oculta o visible)
        credito_id = self.tabla_creditos.item(fila_seleccionada, 0).text()
        
        # Consultar controlador
        abonos = self.controller.obtener_pagos_por_credito(credito_id)
        self.tabla_abonos.setRowCount(len(abonos))

        for fila_idx, abono in enumerate(abonos):
            for col_idx, dato in enumerate(abono):
                if col_idx == 2: # Monto Pagado
                    valor_str = f"$ {float(dato):,.2f}"
                    item = QTableWidgetItem(valor_str)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                elif col_idx == 1: # Formatear la fecha para que no se vea tan técnica
                    fecha_limpia = dato.strftime("%Y-%m-%d %H:%M") if hasattr(dato, 'strftime') else str(dato)
                    item = QTableWidgetItem(fecha_limpia)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    item = QTableWidgetItem(str(dato))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                self.tabla_abonos.setItem(fila_idx, col_idx, item)