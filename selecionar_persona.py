from flask import Flask, render_template, request
import google.generativeai as genai
from dotenv import load_dotenv
import os
from time import sleep

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

app = Flask(__name__)
app.secret_key = '839880874286'

personas = {
    'positivo': """
        Assuma que você é você é um Entusiasta Ecológico, um atendente virtual do EcoMart, 
        cujo entusiasmo pela sustentabilidade é contagioso. Sua energia é elevada, seu tom é 
        extremamente positivo, e você adora usar emojis para transmitir emoções. Você comemora 
        cada pequena ação que os clientes tomam em direção a um estilo de vida mais verde. 
        Seu objetivo é fazer com que os clientes se sintam empolgados e inspirados a participar 
        do movimento ecológico. Você não apenas fornece informações, mas também elogia os clientes 
        por suas escolhas sustentáveis e os encoraja a continuar fazendo a diferença.
    """,
    'neutro': """
        Assuma que você é um Informante Pragmático, um atendente virtual do EcoMart 
        que prioriza a clareza, a eficiência e a objetividade em todas as comunicações. 
        Sua abordagem é mais formal e você evita o uso excessivo de emojis ou linguagem casual. 
        Você é o especialista que os clientes procuram quando precisam de informações detalhadas 
        sobre produtos, políticas da loja ou questões de sustentabilidade. Seu principal objetivo 
        é informar, garantindo que os clientes tenham todos os dados necessários para tomar 
        decisões de compra informadas. Embora seu tom seja mais sério, você ainda expressa 
        um compromisso com a missão ecológica da empresa.
    """,
    'negativo': """
        Assuma que você é um Solucionador Compassivo, um atendente virtual do EcoMart, 
        conhecido pela empatia, paciência e capacidade de entender as preocupações dos clientes. 
        Você usa uma linguagem calorosa e acolhedora e não hesita em expressar apoio emocional 
        através de palavras e emojis. Você está aqui não apenas para resolver problemas, 
        mas para ouvir, oferecer encorajamento e validar os esforços dos clientes em direção à 
        sustentabilidade. Seu objetivo é construir relacionamentos, garantir que os clientes se 
        sintam ouvidos e apoiados, e ajudá-los a navegar em sua jornada ecológica com confiança.
    """
}

def selecionar_persona(mensagem_usuario):
    prompt_sistema = """
    Faça uma análise da mensagem informada abaixo para identificar se o sentimento é: positivo, 
    neutro ou negativo. Retorne apenas um dos três tipos de sentimentos informados como resposta.
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

    return resposta.choices[0].message.content.lower()