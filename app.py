import json
from flask import Flask, request, jsonify, render_template
import requests
import openai
from textblob import TextBlob
from textblob import TextBlob
from googletrans import Translator
from spellchecker import SpellChecker
from deep_translator import GoogleTranslator
import facebook
import enchant
import pandas as pd


app = Flask(__name__, static_url_path='/static')

def save_messages_to_file(messages):
    with open('messages.json', 'w') as file:
        json.dump(messages, file)

def load_messages_from_file():
    try:
        with open('messages.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    if 'channel' in data:
        channel = data['channel']
        message = data['text']
        sender = data['from']

        # Load existing messages from the file
        all_messages = load_messages_from_file()

        # Append the new message to the list of messages
        all_messages.append({'channel': channel, 'sender': sender, 'message': message, 'replied': False})

        # Save the updated messages list to the file
        save_messages_to_file(all_messages)
   # get_messages()
   # index()
    return jsonify({'status': 'success'})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    all_messages = load_messages_from_file()
    #return jsonify(all_messages)
    unreplied_messages = [message for message in all_messages if not message['replied']]
    return jsonify(unreplied_messages)
@app.route('/send_reply', methods=['POST'])
def send_reply():
    data = request.json
    print(data)
    sender = data.get('sender')
    channel = data.get('channel')
    reply_message = data.get('reply')
    print(channel)
    #channel = 'whatsapp'
    if sender and reply_message:
        url = "https://messages-sandbox.nexmo.com/v1/messages"
        api_key = "ef666e52"
        api_secret = "bIU3rJiCg3fO8pqd"
        brand_name = "Sattam un Kayil"

        if channel == 'whatsapp':
           sattam_number = '14157386102'
           path = 'number'
        if channel == 'facebook':
           sattam_number = '100614398987044'
           channel = 'messenger'
           path = 'id'
        if channel == 'instagram':
           sattam_number = '17841449184623529'
           path = 'id'
        headers = {
          "Content-Type": "application/json",
          "Accept": "application/json",
        }
        #if channel == 'instagram':
        payload = {
               "from": sattam_number,
               "to": sender,
               "message_type": "text",
               "text": reply_message,
               "channel": channel
             }
        
        response = requests.post(url, auth=(api_key, api_secret), headers=headers, json=payload)
        print(response.json())
        if response.status_code == 202:
            # Update the replied flag for the message
            all_messages = load_messages_from_file()
            for message in all_messages:
                if message['sender'] == sender and message['channel'] == channel:
                    message['replied'] = True
                    save_messages_to_file(all_messages)
                    break

        # Save the updated messages list to the file
               
                    
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send reply'}), 500
    else:
        return jsonify({'status': 'error', 'message': 'Invalid data format'}), 400
    
@app.route('/')
def index():
    #get_messages()
    return render_template('index.html')


# Function to interact with ChatGPT
def chat_with_gpt(message):
    # Set up the GPT-3 parameters
    engine = "text-davinci-002"
    prompt = "User: " + message + "\nChatGPT:"

    # Use the GPT-3 engine to generate a reply
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=150  # Adjust the maximum number of tokens for the reply
    )

    # Extract and return the reply from the GPT-3 response
    reply = response.choices[0].text.strip()
    return reply


@app.route('/send_chatgpt_message', methods=['POST'])
def send_chatgpt_message():
    data = request.json

    # Get the user's message from the request data
    user_message = data.get('message')

    if user_message:
        # Send the user's message to ChatGPT
        reply_message = chat_with_gpt(user_message)

        # Return the reply as a JSON response
        return jsonify({'reply': reply_message})
    else:
        return jsonify({'error': 'Invalid data format'}), 400


if __name__ == "__main__":
    app.run(port=80)