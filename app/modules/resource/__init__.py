from flask import Blueprint

bp = Blueprint('resource', __name__)

from app.modules.resource import routes
