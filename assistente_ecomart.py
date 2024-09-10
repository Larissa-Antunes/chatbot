import google.generativeai as genai
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from selecionar_persona import *
import json
from tools_ecomart import *


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


contexto = carrega("dados/ecomart.txt")

def criar_lista_ids():
    lista_ids_arquivos = []

    file_dados = api_key.files.create(
        file=open("dados/dados_ecomart.txt", "rb"),
        purpose="assistants"
    )
    lista_ids_arquivos.append(file_dados.id)

    file_politicas = api_key.files.create(
        file=open("dados/políticas_ecomart.txt", "rb"),
        purpose="assistants"
    )
    lista_ids_arquivos.append(file_politicas.id)

    file_produtos = api_key.files.create(
        file=open("dados/produtos_ecomart.txt","rb"),
        purpose="assistants"
    )

    lista_ids_arquivos.append(file_produtos.id)

    return lista_ids_arquivos

def pegar_json():
    filename = "assistentes.json"
    
    if not os.path.exists(filename):
        thread_id = criar_thread()
        file_id_list = criar_lista_ids()
        assistant_id = criar_assistente(file_id_list)
        data = {
            "assistant_id": assistant_id.id,
            "thread_id": thread_id.id,
            "file_ids": file_id_list
        }

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("Arquivo 'assistentes.json' criado com sucesso.")
    
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("Arquivo 'assistentes.json' não encontrado.")


def criar_thread():
    return api_key.beta.threads.create()

def criar_assistente(file_ids=[]):
    assistente = api_key.beta.assistants.create(
        name="Atendente EcoMart",
        instructions = f"""
                Você é um chatbot de atendimento a clientes de um e-commerce. 
                Você não deve responder perguntas que não sejam dados do ecommerce informado!
                Além disso, acesse os arquivos associados a você e a thread para responder as perguntas.
                """,
        model = modelo,
        tools= minhas_tools,
        file_ids = file_ids
    )
    return assistente

