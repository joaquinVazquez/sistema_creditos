# main.py
import sys
from PyQt6.QtWidgets import QApplication
from app.views.login_view import LoginWindow

# Arquitectura UI: Hoja de estilos global (Single Source of Truth)
ESTILO_GLOBAL = """
/* Fondo general de la aplicación y tipografía */
QWidget {
    background-color: #f4f6f9;
    font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
    color: #333333;
}

/* Cajas de texto y selectores (Inputs) */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 6px;
    font-size: 13px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus {
    border: 1px solid #80bdff;
    background-color: #fffdfa;
}

/* Botones genéricos (Los colores específicos se mantienen en cada vista) */
QPushButton {
    border-radius: 4px;
    padding: 8px 15px;
    font-weight: bold;
    font-size: 13px;
    border: none;
}
QPushButton:hover {
    background-color: rgba(0, 0, 0, 0.1); /* Efecto hover genérico */
}

/* Tablas de Datos */
QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f8f9fa;
    gridline-color: #e9ecef;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    font-size: 13px;
}
QHeaderView::section {
    background-color: #2c3e50;
    color: #ffffff;
    padding: 8px;
    border: none;
    font-weight: bold;
    font-size: 13px;
}

/* Cuadros de Diálogo (Modales) */
QDialog {
    background-color: #ffffff;
}
"""

def main():
    app = QApplication(sys.argv)
    
    # Inyectar el diseño a toda la aplicación
    app.setStyleSheet(ESTILO_GLOBAL)
    
    ventana_login = LoginWindow()
    ventana_login.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()