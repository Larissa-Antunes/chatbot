from flask import Flask, render_template, request
import google.generativeai as genai
from dotenv import load_dotenv
import os
import uuid
import glob

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

UPLOAD_FOLDER = 'C:\\Users\\larissa.camargo\\Documents\\Curso Alura\\chatbot\\dados'
caminho_imagem_enviada = None

# Função para carregar as informações da loja virtual
def carregar_informacoes_loja():
    informacoes_loja = ""
    for arquivo in glob.glob(os.path.join(UPLOAD_FOLDER, "*.txt")):  
        with open(arquivo, 'r', encoding='utf-8') as f:
            informacoes_loja += f.read() + "\n"
    return informacoes_loja

informacoes_loja = carregar_informacoes_loja()

def bot(prompt):
    try:
        system = "Você é um assistente de e-commerce."
        contexto = f"Informações da loja:\n{informacoes_loja}\n"
        user = f"{system}\n{contexto}\nUsuário: {prompt}"
        
        # Iniciando uma sessão de chat
        chat_session = modelo.start_chat(history=[])
        response = chat_session.send_message(user)
        
        resposta = response.text
        return resposta

    except Exception as erro:
        return f"Erro no Gemini: {erro}"

@app.route('/upload_imagem', methods=['POST'])
def upload_imagem():
    global caminho_imagem_enviada
    if 'imagem' in request.files:
        imagem_enviada = request.files['imagem']

        nome_arquivo = str(uuid.uuid4()) + os.path.splitext(imagem_enviada.filename)[1]
        caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        imagem_enviada.save(caminho_arquivo)
        caminho_imagem_enviada = caminho_arquivo

        return 'Imagem recebida com sucesso!', 200
    return 'Nenhum arquivo foi enviado', 400

@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.json["msg"]
    resposta = bot(prompt)
    return resposta

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)