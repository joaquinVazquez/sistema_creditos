# main.py
import sys
from PyQt6.QtWidgets import QApplication
from app.views.login_view import LoginWindow

def main():
    # 1. Crear la instancia de la aplicación (Requisito obligatorio de PyQt)
    app = QApplication(sys.argv)
    
    # 2. Instanciar y mostrar nuestra vista de Login
    ventana_login = LoginWindow()
    ventana_login.show()
    
    # 3. Iniciar el bucle de eventos (Mantiene la ventana abierta esperando clics)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()