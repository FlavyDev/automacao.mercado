#~/Documentos/IFS/projeto_eng_software/automacao_mercado/.venv/bin/python

from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import requests 
import os

app = Flask(__name__) #__name__

# Configurações da API do WhatsApp Business
whatsapp_api_url = 'https://graph.facebook.com/v17.0/your_phone_number_id/messages'
access_token = 'your_access_token'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST': 
        # Verifica se o arquivo foi enviado
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            # Salva o arquivo no servidor
            filepath = os.path.join('uploads', file.filename)
            file.save(filepath)

            # Leitura do CSV e envio de mensagens
            df = pd.read_csv(filepath)
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            for index, row in df.iterrows():
                produto = row['Nome do Produto']
                preco = row['Preço']
                mensagem = f'O produto {produto} está disponível por R${preco:.2f}.'
                
                data = {
                    "messaging_product": "whatsapp",
                    "to": "55XXXXXXXXX",  # Número do destinatário
                    "type": "text",
                    "text": {
                        "body": mensagem
                    }
                }

                response = requests.post(whatsapp_api_url, json=data, headers=headers)
                if response.status_code != 200:
                    return f'Erro ao enviar mensagem: {response.text}'

            return 'Mensagens enviadas com sucesso!'

if __name__ == '_main_':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)

