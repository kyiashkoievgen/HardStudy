from flask import Blueprint

hs = Blueprint('hs', __name__)

from . import views
