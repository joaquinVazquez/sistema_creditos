# app/views/dashboard_view.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from app.controllers.cliente_controller import ClienteController
from app.views.cliente_form import ClienteForm
from PyQt6.QtWidgets import QMessageBox

class DashboardView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Créditos - Panel de Control")
        self.setMinimumSize(800, 600)
        self.controller = ClienteController()
        
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