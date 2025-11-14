from config.supabase_client import supabase
from .models import Usuario
from django.contrib.auth.models import AnonymousUser

class SupabaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Para /admin, dejar que AuthenticationMiddleware maneje
        if request.path.startswith("/admin"):
            return self.get_response(request)
        
        # Extraer token
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '').strip()
        
        if token:
            try:
                user_data = supabase.auth.get_user(token)
                supabase_uid = user_data.user.id
                
                try:
                    usuario = Usuario.objects.select_related('rol', 'empresa').get(
                        supabase_uid=supabase_uid
                    )
                    request.user = usuario
                    # Evitar que AuthenticationMiddleware sobrescriba
                    request._cached_user = usuario
                except Usuario.DoesNotExist:
                    request.user = AnonymousUser()
            except Exception as e:
                print(f"Token inválido: {str(e)}")
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        
        return self.get_response(request)
    