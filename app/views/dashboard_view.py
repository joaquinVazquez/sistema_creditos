# app/views/dashboard_view.py
import csv
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QFileDialog, QLabel, 
                             QLineEdit, QFrame, QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

# Importación de Controladores (ORM)
from app.controllers.cliente_controller import ClienteController
from app.controllers.credito_controller import CreditoController
from app.controllers.pago_controller import PagoController

# Importación de Vistas (Modales)
from app.views.cliente_form import ClienteForm
from app.views.credito_form import CreditoForm
from app.views.pago_form import PagoForm
from app.views.historial_view import HistorialView
from app.utils.ticket_generator import generar_ticket_pago

class DashboardView(QMainWindow):
    def __init__(self, usuario_id=1, rol_id=1):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión de Créditos - Panel de Control")
        self.setMinimumSize(1000, 650)
        
        self.usuario_id = usuario_id
        self.rol_id = rol_id
        
        # Instancia de Controladores ORM
        self.cliente_ctrl = ClienteController()
        self.credito_ctrl = CreditoController()
        self.pago_ctrl = PagoController()
        
        self.setup_ui()
        self.aplicar_rbac()
        self.cargar_datos()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # --- Encabezado ---
        self.lbl_titulo = QLabel("Panel de Control Operativo")
        self.lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; background: transparent;")
        self.main_layout.addWidget(self.lbl_titulo)

        # --- PANEL ANALÍTICO (KPIs) ---
        self.layout_kpis = QHBoxLayout()
        self.layout_kpis.setSpacing(20)

        self.card_capital = self.crear_card_kpi("CAPITAL EN CALLE", "$ 0.00", "#0078D7")
        self.card_ingresos = self.crear_card_kpi("INGRESOS HOY", "$ 0.00", "#28a745")
        self.card_clientes = self.crear_card_kpi("CLIENTES ACTIVOS", "0", "#6f42c1")

        self.layout_kpis.addWidget(self.card_capital)
        self.layout_kpis.addWidget(self.card_ingresos)
        self.layout_kpis.addWidget(self.card_clientes)
        self.main_layout.addLayout(self.layout_kpis)

        # --- Barra Superior de Acciones ---
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
        self.layout_botones.addStretch()
        self.main_layout.addLayout(self.layout_botones)

        # --- Barra de Búsqueda ---
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("🔍 Buscar cliente por RFC o Nombre...")
        self.txt_buscar.setStyleSheet("font-size: 14px; padding: 8px; margin-bottom: 5px;")
        self.txt_buscar.textChanged.connect(self.filtrar_tabla)
        self.main_layout.addWidget(self.txt_buscar)

        # --- ZONA CENTRAL (Tabla + Perfil) ---
        self.layout_central = QHBoxLayout()
        
        # 1. Tabla Principal
        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["RFC", "Nombre Completo", "Teléfono", "Fecha Registro"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setStyleSheet("font-weight: bold; background-color: #343a40; color: white;")
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla.setStyleSheet("QTableWidget::item:selected { background-color: #0078D7; color: white; }")
        self.tabla.itemSelectionChanged.connect(self.actualizar_panel_perfil)
        self.layout_central.addWidget(self.tabla, stretch=4)

        # 2. Panel Biométrico Lateral
        self.panel_perfil = QWidget()
        self.panel_perfil.setFixedWidth(220)
        self.panel_perfil.setStyleSheet("background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 5px;")
        layout_perfil = QVBoxLayout(self.panel_perfil)
        layout_perfil.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl_titulo_perfil = QLabel("<b>Expediente</b>")
        lbl_titulo_perfil.setStyleSheet("border: none; font-size: 14px; color: #495057;")
        lbl_titulo_perfil.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_foto = QLabel("Sin Selección")
        self.lbl_foto.setFixedSize(160, 160)
        self.lbl_foto.setStyleSheet("background-color: #f8f9fa; border: 1px dashed #ced4da; border-radius: 4px; font-size: 12px; color: #adb5bd;")
        self.lbl_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_abrir_expediente = QPushButton("📂 Abrir Expediente")
        self.btn_abrir_expediente.setStyleSheet("background-color: #343a40; color: white; padding: 6px; font-size: 12px;")
        self.btn_abrir_expediente.clicked.connect(self.abrir_carpeta_windows)
        self.btn_abrir_expediente.setVisible(False)

        self.btn_editar_cliente = QPushButton("✏️ Editar Cliente")
        self.btn_editar_cliente.setStyleSheet("background-color: #ffc107; color: #212529; padding: 6px; font-size: 12px; font-weight: bold;")
        self.btn_editar_cliente.clicked.connect(self.abrir_edicion_cliente)
        self.btn_editar_cliente.setVisible(False)
        
        self.btn_eliminar_cliente = QPushButton("🗑️ Eliminar / Baja")
        self.btn_eliminar_cliente.setStyleSheet("background-color: #dc3545; color: white; padding: 6px; font-size: 12px; font-weight: bold;")
        self.btn_eliminar_cliente.clicked.connect(self.eliminar_cliente_con_candado)
        self.btn_eliminar_cliente.setVisible(False)
        
        layout_perfil.addWidget(lbl_titulo_perfil)
        layout_perfil.addWidget(self.lbl_foto, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_perfil.addWidget(self.btn_abrir_expediente)
        layout_perfil.addWidget(self.btn_editar_cliente)
        layout_perfil.addWidget(self.btn_eliminar_cliente)
        self.layout_central.addWidget(self.panel_perfil, stretch=1)

        self.main_layout.addLayout(self.layout_central)

        # --- Barra Inferior ---
        self.layout_inferior = QHBoxLayout()
        self.btn_exportar = QPushButton("Exportar Base a CSV")
        self.btn_exportar.setStyleSheet("background-color: #6c757d; color: white;")
        self.btn_exportar.clicked.connect(self.exportar_csv)
        self.layout_inferior.addStretch()
        self.layout_inferior.addWidget(self.btn_exportar)
        self.main_layout.addLayout(self.layout_inferior)

    def aplicar_rbac(self):
        if self.rol_id != 1:
            self.btn_exportar.setVisible(False)
            self.btn_otorgar_credito.setEnabled(False)
            self.setWindowTitle("Sistema de Créditos - Módulo de Operaciones")

    def cargar_datos(self):
        clientes = self.cliente_ctrl.obtener_todos()
        self.tabla.setRowCount(len(clientes))
        for i, cliente in enumerate(clientes):
            for j, dato in enumerate(cliente):
                self.tabla.setItem(i, j, QTableWidgetItem(str(dato)))
        self.actualizar_kpis()

    def filtrar_tabla(self, texto):
        texto = texto.lower()
        for fila in range(self.tabla.rowCount()):
            mostrar_fila = False
            for columna in (0, 1):
                item = self.tabla.item(fila, columna)
                if item and texto in item.text().lower():
                    mostrar_fila = True
                    break
            self.tabla.setRowHidden(fila, not mostrar_fila)

    def abrir_formulario_cliente(self):
        dialogo = ClienteForm(self)
        if dialogo.exec():
            d = dialogo.get_data()
            if not d.get('rfc') or not d.get('nombre'):
                QMessageBox.warning(self, "Operación Abortada", "El RFC y Nombre Completo son obligatorios.")
                return

            exito = self.cliente_ctrl.guardar_cliente(
                rfc=d['rfc'], nombre=d['nombre'], telefono=d['telefono'],
                direccion=d['direccion'], foto_path=d['foto'], ine_path=d['ine']
            )
            
            if exito:
                QMessageBox.information(self, "Éxito", "Expediente de cliente registrado correctamente.")
                self.cargar_datos()
            else:
                QMessageBox.critical(self, "Error de Inserción", "No se pudo guardar el cliente. Revisa los logs.")

    def abrir_formulario_credito(self):
        fila = self.tabla.currentRow()
        if fila == -1: return QMessageBox.warning(self, "Atención", "Seleccione un cliente primero.")
        rfc, nombre = self.tabla.item(fila, 0).text(), self.tabla.item(fila, 1).text()
        
        dialogo = CreditoForm(rfc, nombre, self)
        if dialogo.exec():
            d = dialogo.get_data()
            if d['monto'] <= 0:
                QMessageBox.warning(self, "Operación Rechazada", "El monto a financiar debe ser mayor a $0.00.")
                return

            if self.credito_ctrl.crear_credito(d['rfc'], d['monto'], d['tasa'], d['plazos']):
                QMessageBox.information(self, "Éxito", "Crédito generado con éxito.")
                self.cargar_datos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo procesar el crédito.")

    def gestionar_pagos(self):
        fila = self.tabla.currentRow()
        if fila == -1: return QMessageBox.warning(self, "Atención", "Seleccione un cliente primero.")
        
        rfc = self.tabla.item(fila, 0).text()
        nombre_cliente = self.tabla.item(fila, 1).text()
        creditos_activos = self.pago_ctrl.obtener_creditos_cliente(rfc)

        if not creditos_activos: 
            return QMessageBox.information(self, "Sin Deuda", "El cliente no tiene saldos pendientes.")

        id_credito, monto_orig, saldo_actual, estado, fecha = creditos_activos[0]
        saldo_actual = float(saldo_actual)
        cuota_sugerida, semana_actual = self.pago_ctrl.obtener_metricas_cobro(id_credito)

        dialogo = PagoForm(
            id_credito=id_credito, saldo_actual=saldo_actual, 
            nombre_cliente=nombre_cliente, cuota_semanal=cuota_sugerida, 
            semana_actual=semana_actual, parent=self
        )
        
        if dialogo.exec():
            monto_abono = float(dialogo.get_monto())
            if monto_abono <= 0 or monto_abono > saldo_actual:
                QMessageBox.warning(self, "Error Operativo", "Monto inválido. No puede ser 0 ni mayor al saldo restante.")
                return

            if self.pago_ctrl.registrar_pago(id_credito, self.usuario_id, monto_abono):
                nuevo_saldo = saldo_actual - monto_abono
                ruta_ticket = generar_ticket_pago(rfc, nombre_cliente, monto_abono, nuevo_saldo)
                
                QMessageBox.information(self, "Éxito", "Abono procesado. Generando comprobante...")
                self.cargar_datos()
                try:
                    os.startfile(os.path.abspath(ruta_ticket))
                except Exception as e:
                    print(f"Error al abrir PDF: {e}")
            else:
                QMessageBox.critical(self, "Error", "Fallo al registrar el abono en la base de datos.")

    def abrir_historial(self):
        fila = self.tabla.currentRow()
        if fila == -1: return QMessageBox.warning(self, "Atención", "Seleccione un cliente para ver su historial.")
        rfc, nombre = self.tabla.item(fila, 0).text(), self.tabla.item(fila, 1).text()
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
                    writer.writerow([self.tabla.item(r, c).text() for c in range(self.tabla.columnCount())])
            QMessageBox.information(self, "Éxito", "Reporte generado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al exportar: {e}")

    def actualizar_panel_perfil(self):
        fila = self.tabla.currentRow()
        if fila == -1: return
        
        rfc = self.tabla.item(fila, 0).text()
        expediente = self.cliente_ctrl.obtener_expediente(rfc)
        
        self.btn_abrir_expediente.setVisible(True)
        self.btn_editar_cliente.setVisible(True)
        self.btn_eliminar_cliente.setVisible(True)
        
        self.lbl_foto.clear()
        self.lbl_foto.setText("Sin Foto")

        if expediente:
            foto_path = expediente[0]
            if foto_path and os.path.exists(foto_path):
                pixmap = QPixmap(foto_path)
                pixmap_escalado = pixmap.scaled(
                    self.lbl_foto.size(), 
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.lbl_foto.setPixmap(pixmap_escalado)

    def abrir_carpeta_windows(self):
        fila = self.tabla.currentRow()
        if fila == -1: return
        rfc = self.tabla.item(fila, 0).text()
        ruta_directorio = os.path.join(os.getcwd(), "media", "clientes", rfc)
        
        if os.path.exists(ruta_directorio):
            os.startfile(ruta_directorio)
        else:
            QMessageBox.warning(self, "Expediente Incompleto", f"Aún no hay documentos físicos para el cliente {rfc}.")

    def crear_card_kpi(self, titulo, valor_init, color):
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background-color: white; border-left: 5px solid {color}; border-radius: 8px; padding: 10px; }}")
        layout = QVBoxLayout(card)
        
        lbl_tit = QLabel(titulo)
        lbl_tit.setStyleSheet("color: #6c757d; font-size: 11px; font-weight: bold; border:none;")
        
        lbl_val = QLabel(valor_init)
        lbl_val.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold; border:none;")
        
        layout.addWidget(lbl_tit)
        layout.addWidget(lbl_val)
        card.lbl_valor = lbl_val
        return card

    def actualizar_kpis(self):
        capital, ingresos, clientes = self.credito_ctrl.obtener_metricas_dashboard()
        self.card_capital.lbl_valor.setText(f"$ {capital:,.2f}")
        self.card_ingresos.lbl_valor.setText(f"$ {ingresos:,.2f}")
        self.card_clientes.lbl_valor.setText(str(clientes))

    def abrir_edicion_cliente(self):
        fila = self.tabla.currentRow()
        if fila == -1: return
        rfc_actual = self.tabla.item(fila, 0).text()
        datos_completos = self.cliente_ctrl.obtener_cliente_por_rfc(rfc_actual)
        
        if not datos_completos:
            QMessageBox.critical(self, "Error", "No se pudo leer el registro del cliente.")
            return

        formulario = ClienteForm(self)
        formulario.cargar_datos_edicion(datos_completos)

        if formulario.exec():
            nuevos_datos = formulario.get_data()
            nuevo_rfc = nuevos_datos['rfc']
            
            if not nuevo_rfc or not nuevos_datos['nombre']:
                QMessageBox.warning(self, "Operación Abortada", "El RFC y Nombre son obligatorios.")
                return

            exito = self.cliente_ctrl.actualizar_cliente(rfc_actual, nuevos_datos)
            
            if exito:
                if rfc_actual != nuevo_rfc:
                    ruta_base = os.path.abspath("expedientes")
                    ruta_vieja = os.path.join(ruta_base, rfc_actual)
                    ruta_nueva = os.path.join(ruta_base, nuevo_rfc)
                    
                    if os.path.exists(ruta_vieja):
                        try:
                            os.rename(ruta_vieja, ruta_nueva)
                        except Exception as e:
                            print(f"[ERROR OS] No se pudo renombrar carpeta: {e}")

                QMessageBox.information(self, "Éxito", "Expediente actualizado correctamente.")
                self.cargar_datos()
                self.tabla.clearSelection()
                self.lbl_foto.clear()
                self.lbl_foto.setText("Sin Selección")
                self.btn_abrir_expediente.setVisible(False)
                self.btn_editar_cliente.setVisible(False)
                self.btn_eliminar_cliente.setVisible(False)
            else:
                QMessageBox.critical(self, "Error de BD", "No se pudo actualizar el registro.")

    def eliminar_cliente_con_candado(self):
        fila = self.tabla.currentRow()
        if fila == -1: return
        rfc = self.tabla.item(fila, 0).text()
        nombre = self.tabla.item(fila, 1).text()

        texto, ok = QInputDialog.getText(
            self, "CANDADO DE SEGURIDAD",
            f"Está a punto de eliminar a:\n{nombre}\n\n"
            f"Esto borrará su expediente y todo su historial financiero.\n"
            f"Para confirmar, escriba la palabra ELIMINAR en mayúsculas:"
        )

        if ok and texto == "ELIMINAR":
            exito = self.cliente_ctrl.eliminar_cliente(rfc)
            if exito:
                QMessageBox.information(self, "Operación Exitosa", f"El cliente {nombre} ha sido eliminado del sistema.")
                self.cargar_datos()
                self.btn_abrir_expediente.setVisible(False)
                self.btn_editar_cliente.setVisible(False)
                self.btn_eliminar_cliente.setVisible(False)
                self.lbl_foto.clear()
                self.lbl_foto.setText("Sin Selección")
            else:
                QMessageBox.critical(self, "Error de Integridad", "No se pudo eliminar al cliente. Es posible que tenga créditos activos.")
        elif ok and texto != "ELIMINAR":
            QMessageBox.warning(self, "Operación Cancelada", "Palabra de seguridad incorrecta.")