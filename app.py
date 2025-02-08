from flask import Flask, request, jsonify
import requests
import os
import replicate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

def send_message(chat_id, text):
    """Send message to Telegram"""
    try:
        url = f'{BASE_URL}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(url, json=payload)
        return response
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

@app.route('/')
def index():
    return 'Processor is running!'

@app.route('/process', methods=['POST'])
def process_task():
    """Process AI tasks"""
    try:
        data = request.get_json(force=True)
        chat_id = data['chat_id']
        prompt = data['prompt']
        
        # Get AI response
        response = replicate.run(
            "deepseek-ai/deepseek-math-7b-instruct:8328993709e75f2e6417d9ac24a1330961545f6d05d1ab13cdfdd21c00cb1a6e",
            input={
                "text": prompt,
                "max_new_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9
            }
        )
        
        # Process response
        if isinstance(response, (list, tuple)):
            final_response = ''.join(str(x) for x in response)
        else:
            final_response = str(response)
            
        # Send response back to user
        if final_response.strip():
            send_message(chat_id, final_response.strip())
        else:
            send_message(chat_id, "Désolé, je n'ai pas pu générer une réponse.")
            
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"Error processing task: {e}")
        if chat_id:
            send_message(chat_id, "Désolé, une erreur s'est produite lors du traitement de votre demande.")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(port=5001, debug=True)