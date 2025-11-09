from config.supabase_client import supabase
from .models import Usuario
from django.contrib.auth.models import AnonymousUser

class SupabaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        
        # Evitar interferir con el panel de administración
        if request.path.startswith("/admin"):
            return self.get_response(request)
        
        # Extraer token del header Authorization
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '').strip()
        
        # Si hay token, validar
        if token:
            try:
                # Validar token con Supabase
                user_data = supabase.auth.get_user(token)
                supabase_uid = user_data.user.id
                
                # Buscar usuario en Django
                request.user = Usuario.objects.get(supabase_uid=supabase_uid)
            except Exception:
                # Token inválido o usuario no existe
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        
        respuesta = self.get_response(request)
        return respuesta
    