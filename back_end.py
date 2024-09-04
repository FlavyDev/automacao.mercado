from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from twilio.rest import Client
import os

app = Flask(__name__)

# Configurações do Twilio
account_sid = 'your_account_sid'
auth_token = 'your_auth_token'
client = Client(account_sid, auth_token)

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
            for index, row in df.iterrows():
                produto = row['Nome do Produto']
                preco = row['Preço']
                mensagem = f'O produto {produto} está disponível por R${preco:.2f}.'

                message = client.messages.create(
                    body=mensagem,
                    from_='whatsapp:+557999772540',  # Número do Twilio WhatsApp
                    to='whatsapp:+5579999019286'  # Número do destinatário
                )

            return 'Mensagens enviadas com sucesso!'

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)

