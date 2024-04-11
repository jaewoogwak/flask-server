from config import *
from flask import Flask, jsonify
from flask_cors import CORS
from apps.main import main as main_blueprint
from apps.chatbot import main as chatbot_blueprint
from apps.feedback import main as feedback_blueprint

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(main_blueprint, url_prefix = '/upload')
app.register_blueprint(chatbot_blueprint, url_prefix = '/chatbot')
app.register_blueprint(feedback_blueprint, url_prefix = '/feedback')

address = '0.0.0.0'

if __name__ == '__main__':
    app.run(debug=True, host=address, port=5000)