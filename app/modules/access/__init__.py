from flask import Blueprint

bp = Blueprint('access', __name__)

from app.modules.access import routes
