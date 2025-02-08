import os
import asyncio
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import replicate
import httpx

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

async def send_message(chat_id, text):
    """Asynchronously send a message to Telegram."""
    try:
        url = f'{BASE_URL}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
        return response
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

@app.route('/')
async def index():
    return 'Processor is running!'

@app.route('/process', methods=['POST'])
async def process_task():
    """Asynchronously process the AI task."""
    try:
        # Parse JSON data from the request
        data = request.get_json(force=True)
        chat_id = data['chat_id']
        prompt = data['prompt']

        # Since replicate.run is blocking, run it in a thread.
        response = await asyncio.to_thread(
            replicate.run,
            "deepseek-ai/deepseek-math-7b-instruct:8328993709e75f2e6417d9ac24a1330961545f6d05d1ab13cdfdd21c00cb1a6e",
            input={
                "text": prompt,
                "max_new_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9
            }
        )

        # Process the response (convert to string)
        if isinstance(response, (list, tuple)):
            final_response = ''.join(str(x) for x in response)
        else:
            final_response = str(response)

        # Send the result back to the user via Telegram
        if final_response.strip():
            await send_message(chat_id, final_response.strip())
        else:
            await send_message(chat_id, "Désolé, je n'ai pas pu générer une réponse.")

        return jsonify({'status': 'ok'})

    except Exception as e:
        print(f"Error processing task: {e}")
        # If we have the chat_id, attempt to notify the user about the error.
        if 'chat_id' in locals():
            await send_message(chat_id, "Désolé, une erreur s'est produite lors du traitement de votre demande.")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # Note: For production, consider using an async server (like Hypercorn or Uvicorn)
    # to serve your Flask app. The built-in development server is not intended for production use.
    app.run(port=5001, debug=True)
