from flask import Blueprint

main = Blueprint('chatbot', __name__)

from .routes import *
