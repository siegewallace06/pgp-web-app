"""
Main blueprint for the PGP Web Application
"""
from app.main import routes
from flask import Blueprint

bp = Blueprint('main', __name__)
