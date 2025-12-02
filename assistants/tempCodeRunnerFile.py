from groq import Groq

from django.conf import settings



client = Groq(api_key=settings.GROQ_API_KEY)


chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Por que se vio la necesidad de crear la emergente ingeniria en IA",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)