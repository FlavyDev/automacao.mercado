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
from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import os
from openai import OpenAI
import time


# Configuração da API do OpenAI
# Verifique se a variável de ambiente está sendo lida
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    print("Chave de API não encontrada")
else:
    print("Chave de API configurada corretamente")


client = OpenAI(api_key=api_key)


app = Flask(__name__)

def make_openai_request(mensagem):
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente útil."},
            {"role": "user", "content": mensagem}
        ])
        return response
    except OpenAI.OpenAIError as e:
        # Lidar com exceções específicas da OpenAI
        print(f"Ocorreu um erro: {e}")
    except Exception as e:
        # Lidar com outras exceções
        print(f"Erro inesperado: {e}")

# mexi aqui
# Função para gerar a lista de produtos a partir do CSV
def gerar_lista_produtos(filepath):
    df = pd.read_csv(filepath)
    mensagem = "Confira os produtos disponíveis:\n"
    for index, row in df.iterrows():
        mensagem += f"{row['Nome do Produto']}: R${row['Preço']:.2f}\n"
    return mensagem

# mexi aqui


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
        
        descricao = request.form['descricao']  # Captura a descrição fornecida pelo usuário

        if file:
            # Salva o arquivo no servidor
            filepath = os.path.join('uploads', file.filename)
            file.save(filepath)
                        
            # Gera a lista de produtos a partir do CSV
            lista_produtos = gerar_lista_produtos(filepath)
            '''
            # Lê o CSV
            df = pd.read_csv(filepath)

             # Gerar a mensagem de compartilhamento com os dados do CSV
            mensagem = "Confira os produtos disponíveis:\n"
            for index, row in df.iterrows():
                mensagem += f"{row['Nome do Produto']}: R${row['Preço']:.2f}\n"
                '''

            # Incorporar a descrição fornecida pelo usuário
            mensagem_final = f"{descricao}\n\n{lista_produtos}" #mesagem mexi aqui

            # Chamar a API do ChatGPT para melhorar a mensagem usando a função make_openai_request
            response = make_openai_request(mensagem_final)

            # Verifica se houve erro
            if 'error' in response:
                return jsonify({"error": response.error}), 500
            
            # Obter a resposta gerada pelo ChatGPT
            mensagem_dinamica = response.choices[0].message.content.strip()
            
            '''
            # Codificar a mensagem para URL
            mensagem_compartilhamento = mensagem_dinamica.replace(' ', '%20').replace('\n', '%0A')
            '''

            # Exibe a mensagem para revisão
            return render_template('review.html', mensagem_dinamica=mensagem_dinamica, descricao=descricao, filename=file.filename)

# Rota para lidar com a ação de enviar ou gerar nova mensagem
@app.route('/processar_mensagem', methods=['POST'])
def processar_mensagem():
    acao = request.form['acao']
    descricao = request.form['descricao']
    filename = request.form['filename']

    filepath = os.path.join('uploads', filename)

    # Gera a lista de produtos novamente a partir do CSV
    lista_produtos = gerar_lista_produtos(filepath)

    mensagem_teste = f"{descricao}\n\n{lista_produtos}"

    if acao == 'enviar':
        # Se a ação for enviar, usa a mensagem atual
        mensagem_compartilhamento = request.form['mensagem_dinamica'].replace(' ', '%20').replace('\n', '%0A')
        return render_template('share.html', mensagem_compartilhamento=mensagem_compartilhamento)
    elif acao == 'gerar_nova':
        # Se a ação for gerar nova, recria a mensagem incluindo a lista de produtos
        response = make_openai_request(mensagem_teste)
        if 'error' in response:
            return jsonify({"error": response.error}), 500
        mensagem_dinamica = response.choices[0].message.content.strip()
        
        # Exibe a nova mensagem gerada
        return render_template('review.html', mensagem_dinamica=mensagem_dinamica, descricao=descricao, filename=filename)


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
