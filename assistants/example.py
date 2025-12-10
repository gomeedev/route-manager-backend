from groq import Groq
from django.conf import settings
from packages.models import Paquete


class ExampleAssistant:
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
        
    
    def obtener_paquetes(self):        
        paquetes_info = {
            'total': Paquete.objects.count(),
            'fallidos': Paquete.objects.filter(estado_paquete="Fallido").count(),
        }
        
        return paquetes_info
        

    def consultar(self, question):

        contexto = f"""
        Eres un asistente de AI llamado Alex, tu objetivo es ayudar a los usuarios a comprender facilmente el stock de la aplicacion.

        Actualmente solo contamos con el total de paquetes y son:
        {self.obtener_paquetes()}
        """

        messages = [
            {"role": "system", "content": contexto}
        ]

        messages.append({
            "role": "user",
            "content": question
        })


        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.4
        )
        
        # Esto reemplazo al codigo cometado de abajo
        assistant_message = chat_completion.choices[0].message
        print(assistant_message)
        
        messages.append(assistant_message)
        
        response = chat_completion.choices[0].message.content

        messages.append({
            "role": "assistant",
            "content": response
        }) 
        
        return response
    