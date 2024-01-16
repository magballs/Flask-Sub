#----- flask app written in python -----#

from flask import Flask, request
#from flask_socketio import SocketIO # Removed for now
import logging
import os # pulling in sensitive info from /.bashrc
from logging.handlers import RotatingFileHandler # log fucking everything!
import hmac # encoding bullshit - love it!
import hashlib # 

app = Flask(__name__)

#app = Flask(__name__)
#socketio = SocketIO(app)

# Twitch EventSub webhook secret:
webhook_secret = os.environ.get('EVENTSUB_SECRET')

# Ensure logs directory exists
logs_dir = '/home/pi/logs'
os.makedirs(logs_dir, exist_ok=True)

# Setup logging
log_file_path = os.path.join(logs_dir, 'flask_app.log')
handler = RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

def verify_signature(request):
    message_id = request.headers.get('Twitch-EventSub-Message-Id', '')
    timestamp = request.headers.get('Twitch-EventSub-Message-Timestamp', '')
    signature_header = request.headers.get('Twitch-Eventsub-Message-Signature', '')
    # Concatenate the message ID, timestamp and request body - requirement from twitch
    message = message_id + timestamp + request.get_data(as_text=True)
    if signature_header:
        # Generate HMAC hexdigest using the concatenated message
        expected_signature = "sha256=" + hmac.new(
            webhook_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256
        ).hexdigest()
        # Compare hexdigest signatures
        return hmac.compare_digest(expected_signature, signature_header)
    return False

@app.route('/')
def index():
    return "Say hello to my giant Flask!"

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    app.logger.info(f"Received {request.method} request to /webhook with query params: {request.args}")
    expected_signature = None # Initialize expected_signature to None
    
    try:
        signature_header = request.headers.get('Twitch-Eventsub-Message-Signature')

        if request.method == 'GET':
            if verify_signature(request):
                # signature is valid - proceed
                challenge = request.args.get('hub.challenge')
                app.logger.info('GET request received with challenge parameter')
                if challenge:
                    app.logger.info('Received Twitch challenge for webhook verification')
                    return '', 200
                else:
                    app.logger.warning('GET request to webhook without challenge parameter')
                    return 'This endpoint is for twitch webhook verification.', 400
            else:
                # Log the correct expected signature for debugging
                expected_signature = "sha256=" + hmac.new(
                    webhook_secret.encode('utf-8'), request.data, hashlib.sha256
                ).hexdigest()
                app.logger.warning(f'Expected Signature: {expected_signature}')
                app.logger.warning('Invalid Twitch EventSub Signature')
                app.logger.warning(f'Signature Header: {signature_header}')
                app.logger.warning(f'Request Data: {request.data}')
                return 'Invalid signature', 403

        elif request.method == 'POST':
            signature_header = request.headers.get('Twitch-Eventsub-Message-Signature')
            if verify_signature(request):
                print("POST request received")
                app.logger.info('Received POST request to webhook')
                # Handle the incoming webhook data
                data = request.json
                #socketio.emit('twitchevent', data) # Removing for now
                # What processing logic would I use here?
                return '', 200 # Is this where the invalid signature appears?
            else:
                # Log the correct expected signature for debugging
                message_id = request.headers.get('Twitch-EventSub-Message-Id', '')
                timestamp = request.headers.get('Twitch-EventSub-Message-Timestamp', '')
                message = message_id + timestamp + request.get_data(as_text=True)
                expected_signature = "sha256=" + hmac.new(
                    webhook_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256
                ).hexdigest()
                app.logger.warning(f'Expected Signature: {expected_signature}')
                app.logger.warning('Invalid Twitch EventSub Signature')
                app.logger.warning(f'Signature Header: {signature_header}')
                app.logger.warning(f'Request Data: {request.data}')
                return 'Invalid signature', 403

    except Exception as e:
        app.logger.error(f'Error in webhook route: {e}', exc_info=True)
        return 'Internal Server Error', 500

    return 'Invalid request', 400

#if __name__ == '__main__':
#        socketio.run(app, host='0.0.0.0', port=5000) Removing socketIO at this point in time to focus on issues with valid twitch signature
#----- End of flask app -----#
