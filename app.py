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



app = Flask(__name__, static_url_path='/static')

app.config['SECRET_KEY'] = 'Summer@2023_July'
#socketio = SocketIO(app)

translator = Translator()
spell = SpellChecker()

# Set up OpenAI API credentials
openai.api_key = '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'

received_messages = []  # To store received WhatsApp messages
whatsapp_messages = []
instagram_messages = []
facebook_messages = []


@app.route('/', methods=['POST'])
def webhook():
 #   if request.method == 'POST':
 #       print("Data received from Webhook is: ", request.json)
 #       return "Webhook received!"

    #data = request.get_json()
    
    data = request.json
    print("here:", data)
    # Validate the data structure before accessing keys
    #if 'message' in data and 'text' in data['message']: 
    if 'channel' in data:
            channel = data['channel']
            message = data['text']
            sender = data['from']
           

    #return jsonify({'status': 'success'})
    # Store the message in the appropriate list based on the channel
            if channel == 'whatsapp':
               whatsapp_messages.append({'channel':channel, 'sender': sender, 'message': message, 'replied': False})
            elif channel == 'instagram':
                 instagram_messages.append({'channel':channel, 'sender': sender, 'message': message, 'replied': False})
            elif channel == 'facebook' or channel == 'messenger':
                 facebook_messages.append({'channel':'facebook', 'sender': sender, 'message': message, 'replied': False})
           # socketio.emit('new_message', {'channel':channel, 'sender': sender, 'message': message}, broadcast=True)

    #received_messages.append({'sender': sender, 'message': message})
    #received_messages.append({'sender': sender, 'message': message, 'replied': False})
    print("whats:",whatsapp_messages)
    print("insta:",instagram_messages)
    print("face:",facebook_messages)
    #return jsonify({'status': 'success'})
    return jsonify({'status': 'success'})
    #else:
    #    return jsonify({'status': 'error', 'message': 'Invalid data format'}), 400

@app.route('/get_messages', methods=['GET'])
def get_messages():
    #if request.method == 'GET': 
     #   return jsonify(received_messages)
    all_messages = whatsapp_messages + instagram_messages + facebook_messages
    return jsonify(all_messages)

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
            for message in received_messages:
                if message['sender'] == sender and not message['replied']:
                    message['replied'] = True
                    break

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
    app.run(port=5000)
