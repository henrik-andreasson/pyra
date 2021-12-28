from flask import Blueprint

bp = Blueprint('role', __name__)

from app.modules.role import routes
