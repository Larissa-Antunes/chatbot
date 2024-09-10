from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import os
from io import BytesIO
import base64
from helpers import encodar_imagem

load_dotenv()

# Configurando a chave da API do Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A chave da API do Gemini não foi encontrada. Verifique o arquivo .env.")
print("Chave da API do Gemini encontrada com sucesso.")
genai.configure(api_key=api_key)

# Configuração do modelo do Gemini
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "max_output_tokens": 2048,
}

modelo = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash",
    generation_config=generation_config,
)

# Função para redimensionar a imagem
def redimensionar_imagem(caminho_imagem, largura_max=500):
    imagem = Image.open(caminho_imagem)
    
    # Se a imagem tiver 4 canais (RGBA), converta para RGB
    if imagem.mode == 'RGBA':
        imagem = imagem.convert('RGB')

    proporcao = largura_max / float(imagem.size[0])
    altura_nova = int((float(imagem.size[1]) * proporcao))
    imagem = imagem.resize((largura_max, altura_nova), Image.Resampling.LANCZOS)
    
    # Salvando a imagem redimensionada em um buffer de memória
    buffer = BytesIO()
    imagem.save(buffer, format="JPEG")
    return buffer

# Função para converter a imagem para base64
def encodar_imagem_base64(buffer):
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')

# Função para analisar a imagem
def analisar_imagem(caminho_imagem):
    prompt = """
        Assuma que você é um assistente de chatbot e que provavelmente o usuário está enviando a foto de
        um produto. Faça uma análise dele, e se for um produto com defeito, emita um parecer. Assuma que você sabe e
        processou uma imagem com o Vision e a resposta será informada no formato de saída.

        # FORMATO DA RESPOSTA
       
        Minha análise para imagem consiste em: Parecer com indicações do defeito ou descrição do produto (se não houver defeito)

        ## Descreva a imagem:
    """

    # Redimensionando a imagem para reduzir o tamanho
    buffer = redimensionar_imagem(caminho_imagem)
    
    # Convertendo a imagem redimensionada para base64
    imagem_base64 = encodar_imagem_base64(buffer)

    # Preparando o prompt com a imagem em base64
    prompt_com_imagem = f"{prompt}\n[Imagem: data:image/jpeg;base64,{imagem_base64}]"

    # Enviando o prompt para o modelo do Gemini
    resposta = genai.generate_text(
        model=modelo,
        prompt=prompt_com_imagem,
        **generation_config
    )

    # Retornando a resposta gerada
    return resposta['candidates'][0]['output']

print(analisar_imagem("dados/new_caneca.png"))
