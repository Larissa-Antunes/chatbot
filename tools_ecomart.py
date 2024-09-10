from flask import Flask,render_template, request, Response
import google.generativeai as genai
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from selecionar_documento import *
from selecionar_persona import *

load_dotenv()

# Configurando a chave da API do Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A chave da API do Gemini não foi encontrada. Verifique o arquivo .env.")
if api_key:
    print("Chave da API do Gemini encontrada com sucesso: " + api_key)
genai.configure(api_key=api_key)

# Configuração do modelo do Gemini
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "max_output_tokens": 2048,
    "response_mime_type": "text/plain",
}
# Inicializando o modelo do Gemini  
modelo = genai.GenerativeModel(
    model_name="models/gemini-1.5-pro",
    generation_config=generation_config,
)


minhas_tools = [
    {"type": "retrieval"},
    {
      "type": "function",
            "function": {
            "name": "validar_codigo_promocional",
            "description": "Valide um código promocional com base nas diretrizes de Descontos e Promoções da empresa",
            "parameters": {
                "type": "object",
                "properties": {
                    "codigo": {
                        "type": "string",
                        "description": "O código promocional, no formato, CUPOM_XX. Por exemplo: CUPOM_ECO",
                    },
                    "validade": {
                        "type": "string",
                        "description": f"A validade do cupom, caso seja válido e esteja associado as políticas. No formato DD/MM/YYYY.",
                    },
                },
                "required": ["codigo", "validade"],
            }
        }
    }
    
]

def validar_codigo_promocional(argumentos):
    codigo = argumentos.get("codigo")
    validade = argumentos.get("validade")

    return f"""
        
        # Formato de Resposta
        
        {codigo} com validade: {validade}. 
        Ainda, diga se é válido ou não para o usuário.

        """

minhas_funcoes = {
    "validar_codigo_promocional": validar_codigo_promocional,
}