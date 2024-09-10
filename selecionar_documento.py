import google.generativeai as genai
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *

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

politicas_ecomart = carrega('dados/políticas_ecomart.txt')
dados_ecomart = carrega('dados/dados_ecomart.txt')
produtos_ecomart = carrega('dados/produtos_ecomart.txt')

def selecionar_documento(resposta_openai):
    if "políticas" in resposta_openai:
        return dados_ecomart + "\n" + politicas_ecomart
    elif "produtos" in resposta_openai:
        return dados_ecomart + "\n" + produtos_ecomart
    else:
        return dados_ecomart 

def selecionar_contexto(mensagem_usuario):
    prompt_sistema = f"""
    A empresa EcoMart possui três documentos principais que detalham diferentes aspectos do negócio:

    #Documento 1 "\n {dados_ecomart} "\n"
    #Documento 2 "\n" {politicas_ecomart} "\n"
    #Documento 3 "\n" {produtos_ecomart} "\n"

    Avalie o prompt do usuário e retorne o documento mais indicado para ser usado no contexto da resposta. Retorne dados se for o Documento 1, políticas se for o Documento 2 e produtos se for o Documento 3. 

    """

    resposta = api_key.chat.completions.create(
        model=modelo,
        messages=[
            {
                "role": "system",
                "content": prompt_sistema
            },
            {
                "role": "user",
                "content" : mensagem_usuario
            }
        ],
        temperature=1,
    )

    contexto = resposta.choices[0].message.content.lower()

    return contexto