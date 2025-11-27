from groq import Groq
from django.conf import settings
from django.db.models import Sum, Count, Q, F
from decimal import Decimal

from packages.models import Cliente, Paquete
from routes.models import Ruta, EntregaPaquete
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
        
        # Estadísticas de clientes
        clientes_stats = Cliente.objects.annotate(
            total_paquetes=Count('paquetes'),
            total_valor=Sum('paquetes__valor_declarado'),
            paquetes_entregados=Count('paquetes', filter=Q(paquetes__estado_paquete='Entregado')),
            paquetes_fallidos=Count('paquetes', filter=Q(paquetes__estado_paquete='Fallido'))
        ).order_by('-total_valor')[:10]  # Top 10 clientes
        
        # Estadísticas de paquetes
        paquetes_stats = {
            'total': Paquete.objects.count(),
            'pendientes': Paquete.objects.filter(estado_paquete='Pendiente').count(),
            'en_ruta': Paquete.objects.filter(estado_paquete='En ruta').count(),
            'entregados': Paquete.objects.filter(estado_paquete='Entregado').count(),
            'fallidos': Paquete.objects.filter(estado_paquete='Fallido').count(),
            'valor_total': Paquete.objects.aggregate(total=Sum('valor_declarado'))['total'] or Decimal('0'),
            'por_tipo': list(Paquete.objects.values('tipo_paquete').annotate(cantidad=Count('id_paquete')))
        }
        
        # Estadísticas de rutas
        rutas_stats = {
            'total': Ruta.objects.count(),
            'completadas': Ruta.objects.filter(estado='Completada').count(),
            'en_curso': Ruta.objects.filter(estado='En ruta').count(),
            'fallidas': Ruta.objects.filter(estado='Fallida').count(),
            'distancia_total': Ruta.objects.aggregate(total=Sum('distancia_total_km'))['total'] or Decimal('0'),
            'tiempo_total': Ruta.objects.aggregate(total=Sum('tiempo_estimado_minutos'))['total'] or 0
        }
        
        # Estadísticas de vehículos
        vehiculos_stats = {
            'total': Vehiculo.objects.count(),
            'disponibles': Vehiculo.objects.filter(estado='Disponible').count(),
            'en_ruta': Vehiculo.objects.filter(estado='En ruta').count(),
            'por_tipo': list(Vehiculo.objects.values('tipo').annotate(cantidad=Count('id_vehiculo')))
        }
        
        conductores_stats = Driver.objects.select_related('conductor', 'vehiculo').annotate(
            rutas_completadas=Count('rutas', filter=Q(rutas__estado='Completada')),
            rutas_fallidas=Count('rutas', filter=Q(rutas__estado='Fallida')),
            total_distancia=Sum('rutas__distancia_total_km', filter=Q(rutas__estado='Completada')),
            paquetes_entregados=Sum('rutas__paquetes_entregados', filter=Q(rutas__estado='Completada'))
        ).order_by('-rutas_completadas')[:10]  # Top 10 conductores
        
        drivers_general = {
            'total': Driver.objects.count(),
            'disponibles': Driver.objects.filter(estado='Disponible').count(),
            'asignados': Driver.objects.filter(estado='Asignado').count(),
            'en_ruta': Driver.objects.filter(estado='En ruta').count(),
            'no_disponibles': Driver.objects.filter(estado='No disponible').count()
        }
        
        # Construir contexto en texto
        contexto = f"""
DATOS DEL SISTEMA DE GESTIÓN DE RUTAS - BOGOTÁ, COLOMBIA

=== CLIENTES (Top 10 por valor generado) ===
"""
        for idx, cliente in enumerate(clientes_stats, 1):
            contexto += f"""
{idx}. {cliente.nombre} {cliente.apellido}
   - Total paquetes: {cliente.total_paquetes}
   - Valor total generado: ${cliente.total_valor:,.2f} COP
   - Entregados: {cliente.paquetes_entregados} | Fallidos: {cliente.paquetes_fallidos}
   - Correo: {cliente.correo}
   - Teléfono: {cliente.telefono_movil}
"""

        contexto += f"""
=== ESTADÍSTICAS DE PAQUETES ===
- Total de paquetes: {paquetes_stats['total']}
- Pendientes: {paquetes_stats['pendientes']}
- En ruta: {paquetes_stats['en_ruta']}
- Entregados: {paquetes_stats['entregados']}
- Fallidos: {paquetes_stats['fallidos']}
- Valor total declarado: ${paquetes_stats['valor_total']:,.2f} COP

Distribución por tipo:
"""
        for tipo in paquetes_stats['por_tipo']:
            contexto += f"- {tipo['tipo_paquete']}: {tipo['cantidad']} paquetes\n"

        contexto += f"""
=== ESTADÍSTICAS DE RUTAS ===
- Total rutas: {rutas_stats['total']}
- Completadas: {rutas_stats['completadas']}
- En curso: {rutas_stats['en_curso']}
- Fallidas: {rutas_stats['fallidas']}
- Distancia total recorrida: {rutas_stats['distancia_total']:,.2f} km
- Tiempo total estimado: {rutas_stats['tiempo_total']:,} minutos ({rutas_stats['tiempo_total']//60:.0f} horas)

=== ESTADÍSTICAS DE VEHÍCULOS ===
- Total vehículos: {vehiculos_stats['total']}
- Disponibles: {vehiculos_stats['disponibles']}
- En ruta: {vehiculos_stats['en_ruta']}

Distribución por tipo:
"""
        for tipo in vehiculos_stats['por_tipo']:
            contexto += f"- {tipo['tipo']}: {tipo['cantidad']} vehículos\n"
        
        contexto += f"""
=== ESTADÍSTICAS DE CONDUCTORES ===
- Total conductores: {drivers_general['total']}
- Disponibles: {drivers_general['disponibles']}
- Asignados a ruta: {drivers_general['asignados']}
- En ruta activa: {drivers_general['en_ruta']}
- No disponibles: {drivers_general['no_disponibles']}

=== CONDUCTORES (Top 10 por rutas completadas) ===
"""
        for idx, driver in enumerate(conductores_stats, 1):
            vehiculo_info = f"{driver.vehiculo.tipo} - {driver.vehiculo.placa}" if driver.vehiculo else "Sin vehículo asignado"
            contexto += f"""
{idx}. {driver.conductor.nombre} {driver.conductor.apellido}
   - Estado: {driver.estado}
   - Vehículo: {vehiculo_info}
   - Rutas completadas: {driver.rutas_completadas or 0}
   - Rutas fallidas: {driver.rutas_fallidas or 0}
   - Paquetes entregados: {driver.paquetes_entregados or 0}
   - Distancia total recorrida: {driver.total_distancia or 0:.2f} km
   - Teléfono: {driver.conductor.telefono_movil}
"""
        
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
2. Si no tienes la información, dilo claramente
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
                temperature=0.3,  # Respuestas más determinísticas
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