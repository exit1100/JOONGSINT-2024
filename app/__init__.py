# app/__init__.py
from flask import Flask

app = Flask(__name__)

# Configuration
app.config.from_object('config')

# Import modules
from app import views, models, forms

# Create database tables
models.init_db()
