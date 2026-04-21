# app/views/dashboard_view.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from app.controllers.cliente_controller import ClienteController
from app.views.cliente_form import ClienteForm
from PyQt6.QtWidgets import QMessageBox
from app.controllers.credito_controller import CreditoController
from app.views.credito_form import CreditoForm
from app.controllers.pago_controller import PagoController
from app.views.pago_form import PagoForm

class DashboardView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Créditos - Panel de Control")
        self.setMinimumSize(800, 600)
        self.controller = ClienteController()
        self.controller = ClienteController()
        self.credito_controller = CreditoController() # NUEVO
        
        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        # Contenedor principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Botón para futuro Insertar
        self.btn_nuevo = QPushButton("Nuevo Cliente")
        self.btn_nuevo.setFixedWidth(150)
        self.btn_nuevo.setStyleSheet("background-color: #28a745; color: white; padding: 5px;")
        self.btn_nuevo.clicked.connect(self.abrir_formulario_cliente)

        self.btn_credito = QPushButton("Otorgar Crédito")
        self.btn_credito.setStyleSheet("background-color: #ff8c00; color: white; padding: 5px;")
        self.btn_credito.clicked.connect(self.abrir_formulario_credito)

        self.btn_cobrar = QPushButton("Cobrar / Estado Cuenta")
        self.btn_cobrar.setStyleSheet("background-color: #28a745; color: white; padding: 5px;")
        self.btn_cobrar.clicked.connect(self.gestionar_pagos)
        layout.addWidget(self.btn_cobrar)
        
        layout.addWidget(self.btn_nuevo)
        layout.addWidget(self.btn_credito) # Agrégalo debajo del botón de nuevo cliente
        
        # Tabla de datos
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["RFC", "Nombre Completo", "Teléfono", "Fecha de Registro"])
        # UX: Hacer que la tabla ocupe todo el ancho disponible
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Solo lectura

        layout.addWidget(self.btn_nuevo)
        layout.addWidget(self.tabla)

    def cargar_datos(self):
        """Consulta al controlador y dibuja los datos en la tabla."""
        clientes = self.controller.obtener_todos()
        self.tabla.setRowCount(len(clientes))

        for fila_idx, cliente in enumerate(clientes):
            for col_idx, dato in enumerate(cliente):
                item = QTableWidgetItem(str(dato))
                self.tabla.setItem(fila_idx, col_idx, item)

    def abrir_formulario_cliente(self):
        # 2. Todo lo que va adentro debe tener 4 espacios extra (un nivel más de indentación)
        dialogo = ClienteForm(self)
        
        if dialogo.exec():
            datos = dialogo.get_data()
            
            if not datos['rfc'] or not datos['nombre']:
                QMessageBox.warning(self, "Error", "RFC y Nombre son obligatorios.")
                return

            exito = self.controller.guardar_cliente(
                datos['rfc'], datos['nombre'], datos['telefono'], datos['direccion']
            )

            if exito:
                QMessageBox.information(self, "Éxito", "Cliente registrado correctamente.")
                self.cargar_datos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar al cliente.")

    def abrir_formulario_credito(self):
        """Detecta qué cliente está seleccionado y abre el modal de crédito."""
        fila = self.tabla.currentRow()
        
        # UX: Validar que el usuario haya hecho clic en alguna fila
        if fila == -1:
            QMessageBox.warning(self, "Atención", "Por favor seleccione un cliente de la tabla primero.")
            return

        # Extraer RFC y Nombre de la celda visual
        rfc = self.tabla.item(fila, 0).text()
        nombre = self.tabla.item(fila, 1).text()

        dialogo = CreditoForm(rfc, nombre, self)
        if dialogo.exec():
            datos = dialogo.get_data()
            
            # Validar que no preste $0.00
            if datos['monto'] <= 0:
                QMessageBox.warning(self, "Error", "El monto debe ser mayor a cero.")
                return

            exito = self.credito_controller.crear_credito(
                datos['rfc'], datos['monto'], datos['tasa'], datos['plazos']
            )

            if exito:
                QMessageBox.information(self, "Éxito", "Crédito generado y calculado correctamente.")
            else:
                QMessageBox.critical(self, "Error", "No se pudo generar el crédito.")

    def gestionar_pagos(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Atención", "Seleccione un cliente para ver sus deudas.")
            return

        rfc = self.tabla.item(fila, 0).text()
        pago_ctrl = PagoController()
        creditos = pago_ctrl.obtener_creditos_cliente(rfc)

        if not creditos:
            QMessageBox.information(self, "Sin Deuda", "Este cliente no tiene créditos activos con saldo pendiente.")
            return

        # Para simplificar el MVP, tomamos el crédito más antiguo con saldo
        # En una versión avanzada, mostraríamos una lista para elegir cuál crédito pagar
        id_credito, monto_orig, saldo, estado, fecha = creditos[0]

        dialogo = PagoForm(id_credito, saldo, self)
        if dialogo.exec():
            monto_abono = dialogo.get_monto()
            if monto_abono <= 0: return

            # Nota: usuario_id=1 por ahora (Admin), en el futuro vendrá del Login
            if pago_ctrl.registrar_pago(id_credito, 1, monto_abono):
                QMessageBox.information(self, "Éxito", "Pago registrado y saldo actualizado.")
                self.cargar_datos() # Refrescar
            else:
                QMessageBox.critical(self, "Error", "Error al procesar el pago.")