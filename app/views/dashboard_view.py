import csv
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QFileDialog, QLabel, QLineEdit)
from PyQt6.QtCore import Qt

# Importación de Controladores
from app.controllers.cliente_controller import ClienteController
from app.controllers.credito_controller import CreditoController
from app.controllers.pago_controller import PagoController

# Importación de Vistas (Modales)
from app.views.cliente_form import ClienteForm
from app.views.credito_form import CreditoForm
from app.views.pago_form import PagoForm
from app.views.historial_view import HistorialView

class DashboardView(QMainWindow):
    def __init__(self, usuario_id=1, rol_id=1):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión de Créditos - Panel de Control")
        self.setMinimumSize(900, 600)
        
        # Propagación de Sesión y Roles
        self.usuario_id = usuario_id
        self.rol_id = rol_id
        
        # Inicialización de Controladores
        self.cliente_ctrl = ClienteController()
        self.credito_ctrl = CreditoController()
        self.pago_ctrl = PagoController()
        
        self.setup_ui()
        self.aplicar_rbac()
        self.cargar_datos()

    def setup_ui(self):
        """Define la interfaz siguiendo principios de UX y jerarquía visual."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Le damos márgenes amplios al layout principal para que respire
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # --- Encabezado ---
        self.lbl_titulo = QLabel("Panel de Control Operativo")
        self.lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; background: transparent;")
        self.main_layout.addWidget(self.lbl_titulo)

        # --- Barra Superior de Acciones (Layout Horizontal) ---
        self.layout_botones = QHBoxLayout()
        self.layout_botones.setSpacing(10)
        
        self.btn_nuevo_cliente = QPushButton("Nuevo Cliente")
        self.btn_nuevo_cliente.setStyleSheet("background-color: #0078D7; color: white;")
        self.btn_nuevo_cliente.clicked.connect(self.abrir_formulario_cliente)

        self.btn_otorgar_credito = QPushButton("Otorgar Crédito")
        self.btn_otorgar_credito.setStyleSheet("background-color: #ff8c00; color: white;")
        self.btn_otorgar_credito.clicked.connect(self.abrir_formulario_credito)

        self.btn_cobrar = QPushButton("Cobrar Abono")
        self.btn_cobrar.setStyleSheet("background-color: #28a745; color: white;")
        self.btn_cobrar.clicked.connect(self.gestionar_pagos)

        self.btn_historial = QPushButton("Estado de Cuenta")
        self.btn_historial.setStyleSheet("background-color: #17a2b8; color: white;")
        self.btn_historial.clicked.connect(self.abrir_historial)

        self.layout_botones.addWidget(self.btn_nuevo_cliente)
        self.layout_botones.addWidget(self.btn_otorgar_credito)
        self.layout_botones.addWidget(self.btn_cobrar)
        self.layout_botones.addWidget(self.btn_historial)
        self.layout_botones.addStretch() # Empuja los botones a la izquierda

        # --- Barra de Búsqueda Dinámica ---
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("🔍 Buscar cliente por RFC o Nombre...")
        self.txt_buscar.setStyleSheet("font-size: 14px; padding: 8px; margin-bottom: 5px;")
        self.txt_buscar.textChanged.connect(self.filtrar_tabla) # UX: Reacciona a cada tecla
        
        self.main_layout.addLayout(self.layout_botones)
        self.main_layout.addWidget(self.txt_buscar)

        # --- Tabla Principal ---
        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True) # Activa el diseño cebra
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["RFC", "Nombre Completo", "Teléfono", "Fecha Registro"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # --- Barra Inferior (Utilidades) ---
        self.layout_inferior = QHBoxLayout()
        self.btn_exportar = QPushButton("Exportar Base a CSV")
        self.btn_exportar.setStyleSheet("background-color: #6c757d; color: white;")
        self.btn_exportar.clicked.connect(self.exportar_csv)
        self.layout_inferior.addStretch() # Empuja el botón a la derecha
        self.layout_inferior.addWidget(self.btn_exportar)

        # Ensamblar Layout Principal
        self.main_layout.addLayout(self.layout_botones)
        self.main_layout.addWidget(self.tabla)
        self.main_layout.addLayout(self.layout_inferior)

    def aplicar_rbac(self):
        """Restricción de interfaz según rol."""
        if self.rol_id != 1: # Si no es ADMIN
            self.btn_exportar.setVisible(False)
            self.btn_otorgar_credito.setEnabled(False) # Un cajero solo cobra, no presta
            self.setWindowTitle("Sistema de Créditos - Módulo de Operaciones")

    def cargar_datos(self):
        """Refresca la información de la tabla desde la BD."""
        clientes = self.cliente_ctrl.obtener_todos()
        self.tabla.setRowCount(len(clientes))
        for i, cliente in enumerate(clientes):
            for j, dato in enumerate(cliente):
                self.tabla.setItem(i, j, QTableWidgetItem(str(dato)))

    def abrir_formulario_cliente(self):
        dialogo = ClienteForm(self)
        if dialogo.exec():
            d = dialogo.get_data()
            
            # Validación de UX: Obligar a poner RFC
            if not d['rfc'] or not d['nombre']:
                QMessageBox.warning(self, "Error", "RFC y Nombre son obligatorios.")
                return

            # Inyectamos los nuevos campos de foto e ine al controlador
            exito = self.cliente_ctrl.guardar_cliente(
                d['rfc'], 
                d['nombre'], 
                d['telefono'], 
                d['direccion'], 
                d['foto'], 
                d['ine']
            )

            if exito:
                QMessageBox.information(self, "Éxito", "Expediente de cliente registrado.")
                self.cargar_datos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar el expediente.")

    def abrir_formulario_credito(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Atención", "Seleccione un cliente primero.")
            return
        
        rfc = self.tabla.item(fila, 0).text()
        nombre = self.tabla.item(fila, 1).text()
        
        dialogo = CreditoForm(rfc, nombre, self)
        if dialogo.exec():
            d = dialogo.get_data()
            if self.credito_ctrl.crear_credito(d['rfc'], d['monto'], d['tasa'], d['plazos']):
                QMessageBox.information(self, "Éxito", "Crédito generado con éxito.")
            else:
                QMessageBox.critical(self, "Error", "No se pudo procesar el crédito.")

    def gestionar_pagos(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Atención", "Seleccione un cliente primero.")
            return

        rfc = self.tabla.item(fila, 0).text()
        creditos_activos = self.pago_ctrl.obtener_creditos_cliente(rfc)

        if not creditos_activos:
            QMessageBox.information(self, "Sin Deuda", "El cliente no tiene saldos pendientes.")
            return

        id_credito, monto_orig, saldo, estado, fecha = creditos_activos[0]
        dialogo = PagoForm(id_credito, saldo, self)
        if dialogo.exec():
            monto = dialogo.get_monto()
            if self.pago_ctrl.registrar_pago(id_credito, self.usuario_id, monto):
                QMessageBox.information(self, "Éxito", "Abono procesado correctamente.")
                self.cargar_datos()

    def abrir_historial(self):
        """Abre la ventana de historial detallado."""
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Atención", "Seleccione un cliente para ver su historial.")
            return

        rfc = self.tabla.item(fila, 0).text()
        nombre = self.tabla.item(fila, 1).text()

        self.ventana_historial = HistorialView(rfc, nombre, self)
        self.ventana_historial.exec()

    def exportar_csv(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar Datos", "", "CSV Files (*.csv)")
        if not ruta: return
        try:
            with open(ruta, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                headers = [self.tabla.horizontalHeaderItem(i).text() for i in range(self.tabla.columnCount())]
                writer.writerow(headers)
                for r in range(self.tabla.rowCount()):
                    row_data = [self.tabla.item(r, c).text() for c in range(self.tabla.columnCount())]
                    writer.writerow(row_data)
            QMessageBox.information(self, "Éxito", "Reporte generado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al exportar: {e}")

    def filtrar_tabla(self, texto):
        """Filtra visualmente las filas del QTableWidget en tiempo real."""
        texto = texto.lower()
        for fila in range(self.tabla.rowCount()):
            mostrar_fila = False
            # Iterar solo por las columnas 0 (RFC) y 1 (Nombre)
            for columna in (0, 1):
                item = self.tabla.item(fila, columna)
                if item and texto in item.text().lower():
                    mostrar_fila = True
                    break
            
            # Ocultar la fila si no hay coincidencia
            self.tabla.setRowHidden(fila, not mostrar_fila)