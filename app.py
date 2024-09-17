'''
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# Rota principal para exibir o formulário de upload
@app.route('/')
def index():
    return render_template('index.html')

# Rota para processar o upload e gerar o link de compartilhamento
@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Verifica se o arquivo foi enviado
        if 'file' not in request.files:
            return 'Nenhum arquivo foi enviado'
        file = request.files['file']
        if file.filename == '':
            return 'Nenhum arquivo selecionado'
        if file:
            # Salva o arquivo no servidor
            filepath = os.path.join('uploads', file.filename)
            file.save(filepath)

            # Lê o CSV
            df = pd.read_csv(filepath)

            # Gerar a mensagem de compartilhamento com os dados do CSV
            mensagem = "Confira os produtos disponíveis:\n"
            for index, row in df.iterrows():
                mensagem += f"{row['Nome do Produto']}: R${row['Preço']:.2f}\n"

            # Codificar a mensagem para URL
            mensagem_compartilhamento = mensagem.replace(' ', '%20').replace('\n', '%0A')

            # Renderizar o template com o link de compartilhamento
            return render_template('share.html', mensagem_compartilhamento=mensagem_compartilhamento)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
'''
from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import openai
import time

app = Flask(__name__)

def make_openai_request(mensagem):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente de marketing."},
                {"role": "user", "content": f"Crie uma mensagem de marketing para o seguinte conteúdo: {mensagem}"}
            ]
        )
        return response
    except openai.error.RateLimitError:
        print("Limite de requisições atingido. Aguardando 60 segundos...")
        time.sleep(60)  # Espera 1 minuto antes de tentar novamente
        return make_openai_request(mensagem)  # Tenta novamente
    except Exception as e:
        return {"error": str(e)}

# Configuração da API do OpenAI
# Verifique se a variável de ambiente está sendo lida
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    print("Chave de API não encontrada")
else:
    openai.api_key = api_key
    print("Chave de API configurada corretamente")

# Rota principal para exibir o formulário de upload
@app.route('/')
def index():
    return render_template('index.html')

# Rota para processar o upload e gerar o link de compartilhamento
@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Verifica se o arquivo foi enviado
        if 'file' not in request.files:
            return 'Nenhum arquivo foi enviado'
        file = request.files['file']
        if file.filename == '':
            return 'Nenhum arquivo selecionado'
        if file:
            # Salva o arquivo no servidor
            filepath = os.path.join('uploads', file.filename)
            file.save(filepath)

            # Lê o CSV
            df = pd.read_csv(filepath)

            # Gerar a mensagem de compartilhamento com os dados do CSV
            mensagem = "Confira os produtos disponíveis:\n"
            for index, row in df.iterrows():
                mensagem += f"{row['Nome do Produto']}: R${row['Preço']:.2f}\n"

            # Chamar a API do ChatGPT para melhorar a mensagem usando a função make_openai_request
            response = make_openai_request(mensagem)

            # Verifica se houve erro
            if 'error' in response:
                return jsonify({"error": response['error']}), 500

            # Obter a resposta gerada pelo ChatGPT
            mensagem_dinamica = response['choices'][0]['message']['content'].strip()

            # Codificar a mensagem para URL
            mensagem_compartilhamento = mensagem_dinamica.replace(' ', '%20').replace('\n', '%0A')

            # Renderizar o template com o link de compartilhamento
            return render_template('share.html', mensagem_compartilhamento=mensagem_compartilhamento)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
