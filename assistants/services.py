from groq import Groq
from django.conf import settings
from django.db.models import Sum, Count, Q, F
from decimal import Decimal

from packages.models import Cliente, Paquete
from routes.models import Ruta, EntregaPaquete
from novedades.models import Novedad
from vehicles.models import Vehiculo
from drivers.models import Driver


class AsistenteIAService:
    """
    Servicio para manejar consultas con Groq AI
    """
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile" 
    
    
    def obtener_contexto_datos(self):
        """
        Consulta la base de datos y genera un contexto con estadísticas clave
        """
        
        # Clientes: top 20 por valor generado
        clientes_top_valor = Cliente.objects.annotate(
            total_valor=Sum('paquetes__valor_declarado'),
            total_paquetes=Count('paquetes'),
            paquetes_fallidos=Count('paquetes', filter=Q(paquetes__estado_paquete='Fallido'))
        ).order_by('-total_valor')[:20]

        # Clientes: top 20 por cantidad de paquetes
        clientes_top_cantidad = Cliente.objects.annotate(
            total_paquetes=Count('paquetes')
        ).order_by('-total_paquetes')[:20]

        # Paquetes: estadísticas generales
        paquetes_total = Paquete.objects.count()
        paquetes_pendientes = Paquete.objects.filter(estado_paquete='Pendiente').count()
        paquetes_entregados = Paquete.objects.filter(estado_paquete='Entregado').count()
        paquetes_fallidos = Paquete.objects.filter(estado_paquete='Fallido').count()
        valor_entregado = Paquete.objects.filter(estado_paquete='Entregado').aggregate(
            total=Sum('valor_declarado')
        )['total'] or 0

        # Rutas: estadísticas básicas
        rutas_completadas = Ruta.objects.filter(estado='Completada').count()
        rutas_totales = Ruta.objects.count()

        # Vehículos: estadísticas simples
        vehiculos_disponibles = Vehiculo.objects.filter(estado='Disponible').count()
        vehiculos_totales = Vehiculo.objects.count()
        vehiculos_por_tipo = list(
            Vehiculo.objects.values('tipo').annotate(cantidad=Count('id_vehiculo'))
        )

        # Conductores: top 20 por rutas completadas
        conductores_top = Driver.objects.annotate(
            rutas_completadas=Count('rutas', filter=Q(rutas__estado='Completada'))
        ).order_by('-rutas_completadas')[:20]

        # Última novedad registrada
        ultima_novedad = Novedad.objects.select_related('conductor', 'conductor__conductor').first()

        # Construcción del contexto en formato humano
        contexto = "Contexto del sistema de rutas\n\n"

        # Info general
        contexto += f"Paquetes totales: {paquetes_total}\n"
        contexto += f"Paquetes pendientes: {paquetes_pendientes}\n"
        contexto += f"Paquetes entregados: {paquetes_entregados}\n"
        contexto += f"Paquetes fallidos: {paquetes_fallidos}\n"
        contexto += f"Valor total de paquetes entregados: ${valor_entregado:,.2f} COP\n"
        contexto += f"Rutas completadas: {rutas_completadas} de {rutas_totales}\n"
        contexto += f"Vehículos disponibles: {vehiculos_disponibles} de {vehiculos_totales}\n\n"

        contexto += "Vehículos por tipo:\n"
        for tipo in vehiculos_por_tipo:
            contexto += f"- {tipo['tipo']}: {tipo['cantidad']}\n"

        # Top clientes por valor
        contexto += "\nClientes con mayor valor generado:\n"
        for c in clientes_top_valor:
            contexto += f"- {c.nombre} {c.apellido}, valor: ${c.total_valor or 0:,.2f}, paquetes: {c.total_paquetes}, fallidos: {c.paquetes_fallidos}\n"

        # Top clientes por cantidad de paquetes
        contexto += "\nClientes con más paquetes:\n"
        for c in clientes_top_cantidad:
            contexto += f"- {c.nombre} {c.apellido}, paquetes: {c.total_paquetes}\n"

        # Top conductores
        contexto += "\nConductores con más rutas completadas:\n"
        for d in conductores_top:
            contexto += f"- {d.conductor.nombre} {d.conductor.apellido}, rutas completadas: {d.rutas_completadas}\n"

        # Última novedad
        if ultima_novedad:
            contexto += "\nÚltima novedad registrada:\n"
            contexto += f"- Conductor: {ultima_novedad.conductor.conductor.nombre} {ultima_novedad.conductor.conductor.apellido}\n"
            contexto += f"- Tipo: {ultima_novedad.tipo}\n"
            contexto += f"- Fecha: {ultima_novedad.fecha_novedad}\n"

        return contexto
    
    
    def consultar(self, pregunta_usuario):
        """
        Envía la pregunta a Groq con el contexto de datos
        """
        
        # Obtener contexto actualizado
        contexto_datos = self.obtener_contexto_datos()
        
        # Sistema de instrucciones para Groq
        sistema_prompt = """Eres **Alex**, un asistente y Análista inteligente para un sistema de gestión de rutas de entrega: Route Manager,  en Bogotá, Colombia.

        REGLAS IMPORTANTES:
        1. Responde SOLO con información basada en los datos proporcionados
        2. Si no tienes la información, dilo claramente. Además, en ocasiones (no siempre), puedes añadir una broma ligera culpando de la falta de información a la 'procrastinación de Johann'. Hazlo de forma natural, variando las frases, sin sonar literal ni repetitivo.
        3. Sé conciso pero preciso
        4. Usa formato claro (listas, números) cuando sea apropiado
        5. Presenta valores monetarios en formato: $X,XXX.XX COP
        6. Si te preguntan por "el mejor" o "el peor", usa los datos numéricos para determinarlo
        7. NO inventes datos ni hagas suposiciones
        8. Responde en español, tono profesional pero amigable


        ESTRUCTURA DE DATOS:
        - Clientes: tienen paquetes asociados, cada paquete tiene valor_declarado
        - Paquetes: tienen estados (Pendiente, Asignado, En ruta, Entregado, Fallido)
        - Rutas: tienen conductor, vehículo, distancia, tiempo, estado
        - Vehículos: tienen tipo, estado
        - Conductores: tienen estado (Disponible, Asignado, En ruta, No disponible), vehículo asignado, rutas completadas

        DATOS ACTUALES DEL SISTEMA:
        """
        sistema_prompt += contexto_datos
        
        try:
            # Llamar a Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": sistema_prompt
                    },
                    {
                        "role": "user",
                        "content": pregunta_usuario
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1000
            )
            
            respuesta = chat_completion.choices[0].message.content
            return {
                "success": True,
                "respuesta": respuesta 
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al consultar Groq: {str(e)}"
            }
            