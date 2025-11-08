import os
from anthropic import Anthropic

# Inicializa el cliente con la API key (debe estar en variables de entorno)
client = Anthropic(api_key=os.getenv("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"))

def preguntar_a_claude(prompt: str) -> str:
    """
    Envía un mensaje al modelo Claude 3.5 Haiku y devuelve su respuesta.
    """
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=300,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[0].text
