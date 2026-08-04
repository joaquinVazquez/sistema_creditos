import os
from datetime import datetime
from fpdf import FPDF

# Rutas dinámicas seguras (Apunta a Documentos/SistemaCreditos/media/recibos)
HOME_DIR = os.path.expanduser("~")
BASE_DIR = os.path.join(HOME_DIR, "Documents", "SistemaCreditos")
RECIBOS_DIR = os.path.join(BASE_DIR, "media", "recibos")
CREDITOS_DIR = os.path.join(BASE_DIR, "media", "creditos")

def generar_ticket_pago(rfc_cliente, nombre_cliente, monto_abono, saldo_restante):
    """Genera un recibo en formato ticket (80mm) y devuelve la ruta física segura."""
    os.makedirs(RECIBOS_DIR, exist_ok=True)
    
    fecha_actual = datetime.now()
    folio = fecha_actual.strftime("%Y%m%d%H%M%S")
    fecha_str = fecha_actual.strftime("%d/%m/%Y %H:%M")
    
    # Formato Ticket: 80mm de ancho x 150mm de alto
    pdf = FPDF(orientation='P', unit='mm', format=(80, 150))
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=5)
    
    # Cabecera
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 5, "SISTEMA DE CREDITOS", ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, "Comprobante de Abono", ln=True, align='C')
    pdf.cell(0, 5, "-" * 30, ln=True, align='C')
    
    # Datos de la transacción
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 5, f"Folio: {folio}", ln=True, align='L')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"Fecha: {fecha_str}", ln=True, align='L')
    pdf.cell(0, 5, f"Cliente: {nombre_cliente}", ln=True, align='L')
    pdf.cell(0, 5, f"RFC: {rfc_cliente}", ln=True, align='L')
    
    pdf.cell(0, 5, "-" * 30, ln=True, align='C')
    
    # Montos
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 6, "Abono Recibido:", align='L')
    pdf.cell(0, 6, f"$ {monto_abono:,.2f}", ln=True, align='R')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(30, 6, "Saldo Restante:", align='L')
    pdf.cell(0, 6, f"$ {saldo_restante:,.2f}", ln=True, align='R')
    
    pdf.cell(0, 5, "-" * 30, ln=True, align='C')
    
    # Pie de página
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, "Gracias por su pago.", ln=True, align='C')
    pdf.cell(0, 5, "Este documento es un comprobante interno.", ln=True, align='C')
    
    # Guardar archivo
    nombre_archivo = f"RECIBO_{rfc_cliente}_{folio}.pdf"
    ruta_pdf = os.path.join(RECIBOS_DIR, nombre_archivo)
    pdf.output(ruta_pdf)
    
    return ruta_pdf

def generar_ticket_credito(datos_credito: dict):
    """Genera un comprobante de crédito en formato ticket (80mm) y devuelve la ruta."""
    os.makedirs(CREDITOS_DIR, exist_ok=True)
    
    fecha_actual = datetime.now()
    # Si no viene un folio en el diccionario, generamos uno por marca de tiempo
    folio = datos_credito.get("folio", fecha_actual.strftime("%Y%m%d%H%M%S"))
    fecha_str = fecha_actual.strftime("%d/%m/%Y %H:%M")
    
    # Formato Ticket: 80mm de ancho x 160mm de alto
    pdf = FPDF(orientation='P', unit='mm', format=(80, 160))
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=5)
    
    # Cabecera
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 5, "SISTEMA DE CREDITOS", ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, "Comprobante de Desembolso", ln=True, align='C')
    pdf.cell(0, 5, "-" * 30, ln=True, align='C')
    
    # Datos de la transacción
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 5, f"Folio: {folio}", ln=True, align='L')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"Fecha: {fecha_str}", ln=True, align='L')
    pdf.cell(0, 5, f"Cliente: {datos_credito.get('cliente', 'N/A')}", ln=True, align='L')
    
    pdf.cell(0, 5, "-" * 30, ln=True, align='C')
    
    # Desglose Financiero
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "DESGLOSE FINANCIERO", ln=True, align='C')
    
    pdf.set_font("Arial", '', 9)
    pdf.cell(35, 5, "Monto Solicitado:", align='L')
    pdf.cell(0, 5, f"$ {datos_credito.get('monto_prestado', 0):,.2f}", ln=True, align='R')
    
    pdf.cell(35, 5, "Interes Aplicado:", align='L')
    pdf.cell(0, 5, f"{datos_credito.get('tasa_interes', 0)} %", ln=True, align='R')
    
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(35, 6, "Total a Pagar:", align='L')
    pdf.cell(0, 6, f"$ {datos_credito.get('total_pagar', 0):,.2f}", ln=True, align='R')
    
    pdf.set_font("Arial", '', 9)
    pdf.cell(35, 5, f"Esquema ({datos_credito.get('cuotas', 0)} pagos):", align='L')
    pdf.cell(0, 5, "cuotas de", ln=True, align='R')
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, f"$ {datos_credito.get('monto_cuota', 0):,.2f}", ln=True, align='R')
    
    pdf.cell(0, 5, "-" * 30, ln=True, align='C')
    
    # Pie de página
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, "Revise su plan de pagos.", ln=True, align='C')
    pdf.cell(0, 5, "Conserve este ticket para aclaraciones.", ln=True, align='C')
    
    # Guardar archivo
    nombre_archivo = f"CREDITO_{folio}.pdf"
    ruta_pdf = os.path.join(CREDITOS_DIR, nombre_archivo)
    pdf.output(ruta_pdf)
    
    return ruta_pdf