from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .services import AsistenteIAService
from .example import ExampleAssistant


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def consultar_asistente(request):
    """
    Endpoint para consultas al asistente de IA
    
    POST /api/v1/asistente/consultar/
    Body: {"pregunta": "¿Quién es el cliente que más paquetes ha pedido?"}
    """
    
    # Validar que sea admin (ajusta según tu lógica de roles)
    # if request.user.rol.nombre_rol != "admin":
    #     return Response(
    #         {"error": "Solo administradores pueden usar el asistente"},
    #         status=status.HTTP_403_FORBIDDEN
    #     )
    
    pregunta = request.data.get('pregunta')
    
    if not pregunta:
        return Response(
            {"error": "Debes enviar una 'pregunta' en el body"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Llamar al servicio
    servicio = AsistenteIAService()
    resultado = servicio.consultar(pregunta)
    
    if resultado['success']:
        return Response({
            "pregunta": pregunta,
            "respuesta": resultado['respuesta']
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {"error": resultado['error']},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        

@api_view(["POST"])
def example_assistant(request):
    if request.method == "POST":
        
        pregunta = request.data.get('pregunta')
        
        model_example = ExampleAssistant()
        resultado = model_example.consultar(pregunta)
        
        return Response ({
            "query": pregunta,
            "response": resultado
        })
        
    return Response ({"error": "Debe proporcionar un método valido"})