from flask import Blueprint

main = Blueprint('feedback', __name__)

from .routes import *
