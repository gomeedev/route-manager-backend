from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas as pdf_canvas
from io import BytesIO
from django.utils import timezone
import os


class EncabezadoPaginado:
    """
    Clase para manejar el encabezado y numero de pagina en cada hoja
    """
    def __init__(self, logo_path):
        self.logo_path = logo_path
        
    def en_pagina(self, canvas, doc):
        """
        Funcion que se ejecuta en cada pagina para agregar encabezado y numero
        """
        canvas.saveState()
        
        # Dimensiones de la pagina
        ancho_pagina = letter[0]
        alto_pagina = letter[1]
        
        # Configuracion del encabezado - MAS ANCHO
        margen_lateral = 0.5 * inch
        ancho_total_header = ancho_pagina - (2 * margen_lateral)
        alto_header = 0.85 * inch
        y_inicio_header = alto_pagina - 0.75 * inch
        
        # Division: 20% para logo, 80% para texto
        ancho_seccion_logo = ancho_total_header * 0.20
        ancho_seccion_texto = ancho_total_header * 0.80
        
        # Dibujar borde exterior completo
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(1.2)
        canvas.rect(margen_lateral, y_inicio_header - alto_header, 
                   ancho_total_header, alto_header, stroke=1, fill=0)
        
        # Linea divisoria vertical entre logo y texto
        x_division = margen_lateral + ancho_seccion_logo
        canvas.line(x_division, y_inicio_header - alto_header,
                   x_division, y_inicio_header)
        
        # Insertar logo del SENA
        try:
            if self.logo_path and os.path.exists(self.logo_path):
                canvas.drawImage(self.logo_path, 
                               margen_lateral + 0.08 * inch,
                               y_inicio_header - alto_header + 0.08 * inch,
                               width=ancho_seccion_logo - 0.16 * inch,
                               height=alto_header - 0.16 * inch,
                               preserveAspectRatio=True,
                               mask='auto')
            else:
                # Si no existe el logo, dibujar placeholder
                canvas.setFillColor(colors.lightgrey)
                canvas.rect(margen_lateral + 0.08 * inch,
                           y_inicio_header - alto_header + 0.08 * inch,
                           ancho_seccion_logo - 0.16 * inch,
                           alto_header - 0.16 * inch,
                           fill=1, stroke=0)
                canvas.setFillColor(colors.black)
                canvas.setFont("Times-Bold", 9)
                canvas.drawCentredString(margen_lateral + ancho_seccion_logo/2,
                                       y_inicio_header - alto_header/2,
                                       "SENA")
        except Exception as e:
            print(f"Error cargando logo: {e}")
            # Dibujar placeholder en caso de error
            canvas.setFillColor(colors.lightgrey)
            canvas.rect(margen_lateral + 0.08 * inch,
                       y_inicio_header - alto_header + 0.08 * inch,
                       ancho_seccion_logo - 0.16 * inch,
                       alto_header - 0.16 * inch,
                       fill=1, stroke=0)
        
        # Texto del encabezado - CENTRADO EN SECCION DE TEXTO
        canvas.setFillColor(colors.black)
        canvas.setFont("Times-Bold", 12)
        
        # Calcular centro de la seccion de texto
        x_centro_texto = x_division + (ancho_seccion_texto / 2)
        
        # Linea 1: Servicio Nacional de Aprendizaje
        y_linea1 = y_inicio_header - 0.30 * inch
        canvas.drawCentredString(x_centro_texto, y_linea1, 
                                "Servicio Nacional de Aprendizaje")
        
        # Linea 2: Centro de Gestion de Mercados, Logistica y Tecnologias de la Informacion
        y_linea2 = y_inicio_header - 0.55 * inch
        canvas.drawCentredString(x_centro_texto, y_linea2,
                                "Centro de Gestion de Mercados, Logistica y")
        
        # Linea 3: Continuacion
        y_linea3 = y_inicio_header - 0.72 * inch
        canvas.drawCentredString(x_centro_texto, y_linea3,
                                "Tecnologias de la Informacion.")
        
        # Numero de pagina en esquina superior derecha
        canvas.setFont("Times-Roman", 10)
        numero_pagina = canvas.getPageNumber()
        canvas.drawRightString(ancho_pagina - margen_lateral,
                              alto_pagina - 0.45 * inch,
                              f"{numero_pagina}")
        
        canvas.restoreState()


def generar_pdf_ruta(ruta, logo_path="static/images/logo_sena.png"):
    """
    Genera PDF con toda la informacion de la ruta
    Retorna buffer con el PDF generado
    
    Parametros:
    - ruta: Objeto de la ruta con toda su informacion
    - logo_path: Ruta local al logo del SENA (por defecto: static/images/logo_sena.png)
    """

    # Crear buffer en memoria
    buffer = BytesIO()
    
    # Configurar documento con margenes AUMENTADOS para que el contenido no se coma
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        topMargin=1.6 * inch,  # AUMENTADO para dejar espacio al header
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch
    )

    # Estilos estilo APA - Times New Roman, negro, tamano 12
    styles = getSampleStyleSheet()
    
    # Estilo para titulo principal
    titulo_principal = ParagraphStyle(
        'TituloPrincipal',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=16,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=24,
        spaceBefore=12
    )
    
    # Estilo para encabezados de seccion (Nivel 1)
    encabezado_nivel1 = ParagraphStyle(
        'EncabezadoNivel1',
        parent=styles['Heading2'],
        fontName='Times-Bold',
        fontSize=12,
        textColor=colors.black,
        alignment=TA_LEFT,
        spaceAfter=6,
        spaceBefore=12
    )
    
    # Estilo para sub-encabezados (Nivel 2)
    encabezado_nivel2 = ParagraphStyle(
        'EncabezadoNivel2',
        parent=styles['Heading3'],
        fontName='Times-BoldItalic',
        fontSize=12,
        textColor=colors.black,
        alignment=TA_LEFT,
        spaceAfter=6,
        spaceBefore=6
    )
    
    # Estilo para texto normal
    texto_normal = ParagraphStyle(
        'TextoNormal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=11,
        textColor=colors.black,
        alignment=TA_JUSTIFY,
        leading=14
    )

    # Elementos del PDF
    elements = []

    # Titulo del documento
    elements.append(Paragraph("Route Manager", titulo_principal))
    elements.append(Paragraph("Informe de Ruta de Entrega", encabezado_nivel2))
    elements.append(Spacer(1, 0.3 * inch))

    # Seccion 1: Datos Principales de la Ruta
    elements.append(Paragraph("1. Datos Principales de la Ruta", encabezado_nivel1))
    elements.append(Spacer(1, 0.1 * inch))

    datos_ruta = [
        ['Codigo Manifiesto:', ruta.codigo_manifiesto],
        ['Estado:', ruta.estado],
        ['Fecha Creacion:', ruta.fecha_creacion.strftime('%d/%m/%Y %H:%M')],
        ['Fecha Inicio:', ruta.fecha_inicio.strftime('%d/%m/%Y %H:%M') if ruta.fecha_inicio else 'N/A'],
        ['Fecha Cierre:', ruta.fecha_fin.strftime('%d/%m/%Y %H:%M') if ruta.fecha_fin else 'N/A'],
        ['Distancia Total:', f"{ruta.distancia_total_km} km" if ruta.distancia_total_km else 'N/A'],
        ['Tiempo Estimado:', f"{ruta.tiempo_estimado_minutos} min" if ruta.tiempo_estimado_minutos else 'N/A']
    ]

    tabla_ruta = Table(datos_ruta, colWidths=[2.2 * inch, 4.3 * inch])
    tabla_ruta.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    elements.append(tabla_ruta)
    elements.append(Spacer(1, 0.2 * inch))

    # Seccion 2: Informacion del Conductor
    elements.append(Paragraph("2. Informacion del Conductor", encabezado_nivel1))
    elements.append(Spacer(1, 0.1 * inch))

    if ruta.conductor:
        c = ruta.conductor.conductor
        datos_conductor = [
            ['Nombre:', f"{c.nombre} {c.apellido}"],
            ['Documento:', f"{c.tipo_documento} {c.documento}"],
            ['Telefono:', c.telefono_movil],
            ['Correo:', c.correo],
            ['Estado Operativo:', ruta.conductor.estado]
        ]
    else:
        datos_conductor = [['Conductor:', 'No asignado']]

    tabla_conductor = Table(datos_conductor, colWidths=[2.2 * inch, 4.3 * inch])
    tabla_conductor.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    elements.append(tabla_conductor)
    elements.append(Spacer(1, 0.2 * inch))

    # Seccion 3: Vehiculo Usado
    elements.append(Paragraph("3. Vehiculo Usado", encabezado_nivel1))
    elements.append(Spacer(1, 0.1 * inch))

    if ruta.vehiculo:
        datos_vehiculo = [
            ['Placa:', ruta.vehiculo.placa],
            ['Tipo:', ruta.vehiculo.tipo],
            ['Estado:', ruta.vehiculo.estado]
        ]
    else:
        datos_vehiculo = [['Vehiculo:', 'No asignado']]

    tabla_vehiculo = Table(datos_vehiculo, colWidths=[2.2 * inch, 4.3 * inch])
    tabla_vehiculo.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    elements.append(tabla_vehiculo)
    elements.append(Spacer(1, 0.2 * inch))

    # Seccion 4: Metricas de Paquetes
    elements.append(Paragraph("4. Metricas de Paquetes", encabezado_nivel1))
    elements.append(Spacer(1, 0.1 * inch))

    metricas = [
        ['Total de Paquetes:', str(ruta.total_paquetes)],
        ['Paquetes Entregados:', str(ruta.paquetes_entregados)],
        ['Paquetes Fallidos:', str(ruta.paquetes_fallidos)],
        ['Tasa de Exito:', f"{(ruta.paquetes_entregados / ruta.total_paquetes * 100):.1f}%"
                             if ruta.total_paquetes > 0 else 'N/A']
    ]

    tabla_metricas = Table(metricas, colWidths=[2.2 * inch, 4.3 * inch])
    tabla_metricas.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    elements.append(tabla_metricas)
    elements.append(Spacer(1, 0.3 * inch))

    # Detalle de Paquetes
    elements.append(Paragraph("4.1. Detalle de Paquetes", encabezado_nivel2))
    elements.append(Spacer(1, 0.1 * inch))

    paquetes_data = [['No.', 'Cliente', 'Direccion', 'Estado', 'Orden']]

    for p in ruta.paquetes.all().order_by('orden_entrega'):
        paquetes_data.append([
            str(p.id_paquete),
            f"{p.cliente.nombre} {p.cliente.apellido}",
            p.direccion_entrega[:35] + '...' if len(p.direccion_entrega) > 35 else p.direccion_entrega,
            p.estado_paquete,
            str(p.orden_entrega) if p.orden_entrega else 'N/A'
        ])

    tabla_paquetes = Table(paquetes_data, colWidths=[0.5 * inch, 1.8 * inch, 2.5 * inch, 1 * inch, 0.7 * inch])
    tabla_paquetes.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    elements.append(tabla_paquetes)

    # Generar PDF con encabezado personalizado
    encabezado = EncabezadoPaginado(logo_path)
    doc.build(elements, onFirstPage=encabezado.en_pagina, onLaterPages=encabezado.en_pagina)
    
    buffer.seek(0)
    return buffer