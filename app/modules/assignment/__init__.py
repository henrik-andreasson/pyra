from flask import Blueprint

bp = Blueprint('assignment', __name__)

from app.modules.assignment import routes
