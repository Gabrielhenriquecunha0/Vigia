
    # colocar a chave no arquivo ENV, utilizar os comandos no terminal antes de iniciar para funcionar:
    #  pip install grog    
    #  pip install flask     
    #  pip install flask-cors 
    #  pip install python-dotenv duckduckgo-search  
    #  pip install duckduckgo_search 
    # coloque a chave api, entre as aspas no arquvio ".env" 
    # Link pra gerar a chave:    https://console.groq.com/keys


    # Iniciar o main 
    


import sys
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv 


load_dotenv()


diretorio_atual = os.path.dirname(os.path.abspath(__file__))
if diretorio_atual not in sys.path:
    sys.path.append(diretorio_atual)

try:
    from ia_service import IAService 
    from promptmestre import PromptMestre
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("DICA: Verifique se os arquivos ia_service.py e promptmestre.py estão na mesma pasta.")
    sys.exit(1)


app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)


ia_engine = IAService()
config_prompt = PromptMestre()


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/ask', methods=['POST'])
def ask():
    dados = request.json
    pergunta = dados.get("message")

    if not pergunta:
        return jsonify({"response": "Manda uma dúvida sobre hardware!"}), 400

    try:
      
        system_instructions = config_prompt.get_prompt()
        historico = [{"role": "user", "content": pergunta}]
        resposta_final = ia_engine.enviar_mensagem(historico, system_instructions)       
        return jsonify({"response": resposta_final})

    except Exception as e:
        print(f"Erro no servidor: {e}")
        return jsonify({"response": f"Deu ruim aqui: {str(e)}"}), 500

if __name__ == '__main__':
    print("Servidor rodando em http://127.0.0.1:5000")
    app.run(port=5000, debug=True)

