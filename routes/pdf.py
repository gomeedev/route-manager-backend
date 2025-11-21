# routes/pdf.py
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from django.utils import timezone


def generar_pdf_ruta(ruta):
    """
    Genera PDF con toda la información de la ruta y lo sube a Supabase.
    Retorna URL del PDF.
    """

    # Crear buffer en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch)


    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=TA_CENTER,
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=10,
        spaceBefore=15
    )

    # Elementos del PDF
    elements = []
    

    header_table = Table(
        [[Paragraph("<b>CENTRO DE BIOTECNOLOGÍA AGROPECUARIA</b>", styles['Normal'])]],
        colWidths=[6.5 * inch]
    )
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e3a8a')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e40af'))
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Route Manager", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    # ---------- SECCIÓN 1 ----------
    elements.append(Paragraph("1. Datos Principales de la Ruta", section_style))

    datos_ruta = [
        ['Código Manifiesto:', ruta.codigo_manifiesto],
        ['Estado:', ruta.estado],
        ['Fecha Creación:', ruta.fecha_creacion.strftime('%d/%m/%Y %H:%M')],
        ['Fecha Inicio:', ruta.fecha_inicio.strftime('%d/%m/%Y %H:%M') if ruta.fecha_inicio else 'N/A'],
        ['Fecha Cierre:', ruta.fecha_fin.strftime('%d/%m/%Y %H:%M') if ruta.fecha_fin else 'N/A'],
        ['Distancia Total:', f"{ruta.distancia_total_km} km" if ruta.distancia_total_km else 'N/A'],
        ['Tiempo Estimado:', f"{ruta.tiempo_estimado_minutos} min" if ruta.tiempo_estimado_minutos else 'N/A']
    ]

    tabla_ruta = Table(datos_ruta, colWidths=[2 * inch, 4.5 * inch])
    tabla_ruta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0f2fe')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(tabla_ruta)
    elements.append(Spacer(1, 0.2 * inch))

    # ---------- SECCIÓN 2 ----------
    elements.append(Paragraph("2. Información del Conductor", section_style))

    if ruta.conductor:
        c = ruta.conductor.conductor
        datos_conductor = [
            ['Nombre:', f"{c.nombre} {c.apellido}"],
            ['Documento:', f"{c.tipo_documento} {c.documento}"],
            ['Teléfono:', c.telefono_movil],
            ['Correo:', c.correo],
            ['Estado Operativo:', ruta.conductor.estado]
        ]
    else:
        datos_conductor = [['Conductor:', 'No asignado']]

    tabla_conductor = Table(datos_conductor, colWidths=[2 * inch, 4.5 * inch])
    tabla_conductor.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0f2fe')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(tabla_conductor)
    elements.append(Spacer(1, 0.2 * inch))

    # ---------- SECCIÓN 3 ----------
    elements.append(Paragraph("3. Vehículo Usado", section_style))

    if ruta.vehiculo:
        datos_vehiculo = [
            ['Placa:', ruta.vehiculo.placa],
            ['Tipo:', ruta.vehiculo.tipo],
            ['Estado:', ruta.vehiculo.estado]
        ]
    else:
        datos_vehiculo = [['Vehículo:', 'No asignado']]

    tabla_vehiculo = Table(datos_vehiculo, colWidths=[2 * inch, 4.5 * inch])
    tabla_vehiculo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0f2fe')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(tabla_vehiculo)
    elements.append(Spacer(1, 0.2 * inch))

    # ---------- SECCIÓN 4 ----------
    elements.append(Paragraph("4. Métricas de Paquetes", section_style))

    metricas = [
        ['Total de Paquetes:', str(ruta.total_paquetes)],
        ['Paquetes Entregados:', str(ruta.paquetes_entregados)],
        ['Paquetes Fallidos:', str(ruta.paquetes_fallidos)],
        ['Tasa de Éxito:', f"{(ruta.paquetes_entregados / ruta.total_paquetes * 100):.1f}%"
                             if ruta.total_paquetes > 0 else 'N/A']
    ]

    tabla_metricas = Table(metricas, colWidths=[2 * inch, 4.5 * inch])
    tabla_metricas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0f2fe')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(tabla_metricas)
    elements.append(Spacer(1, 0.3 * inch))

    # ---------- DETALLE DE PAQUETES ----------
    elements.append(Paragraph("Detalle de Paquetes", section_style))

    paquetes_data = [['#', 'Cliente', 'Dirección', 'Estado', 'Orden']]

    for p in ruta.paquetes.all().order_by('orden_entrega'):
        paquetes_data.append([
            str(p.id_paquete),
            f"{p.cliente.nombre} {p.cliente.apellido}",
            p.direccion_entrega[:30] + '...' if len(p.direccion_entrega) > 30 else p.direccion_entrega,
            p.estado_paquete,
            str(p.orden_entrega) if p.orden_entrega else 'N/A'
        ])

    tabla_paquetes = Table(paquetes_data, colWidths=[0.5 * inch, 1.5 * inch, 2.5 * inch, 1 * inch, 0.8 * inch])
    tabla_paquetes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(tabla_paquetes)

    # ----------- GENERAR PDF -----------
    doc.build(elements)
    buffer.seek(0)
    return buffer
