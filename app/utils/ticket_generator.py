import os
from datetime import datetime
from fpdf import FPDF

# Directorio de salida
RECIBOS_DIR = "media/recibos"

def generar_ticket_pago(rfc_cliente, nombre_cliente, monto_abono, saldo_restante):
    """Genera un recibo en formato ticket (80mm) y devuelve la ruta física."""
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