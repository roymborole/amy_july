import os
import yfinance as yf
import pandas as pd
import requests
from anthropic import Anthropic
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import postmarker
from postmarker.core import PostmarkClient
from pyngrok import ngrok
import json
from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask import Blueprint, render_template
from flask_security import login_required

try:
    from pyngrok import ngrok
except ImportError:
    ngrok = None
    
from dotenv import load_dotenv
load_dotenv()  # This loads the variables from .env

postmark = PostmarkClient(server_token=os.getenv('POSTMARK_SERVER_TOKEN'))

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set in the environment variables")

CRYPTOCOMPARE_API_KEY = os.getenv('CRYPTOCOMPARE_API_KEY')
if not CRYPTOCOMPARE_API_KEY:
    raise ValueError("CRYPTOCOMPARE_API_KEY is not set in the environment variables")

# Create the Anthropic client after loading the API key
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

START_DATE = '2020-01-01'
END_DATE = '2024-07-16'


class Config:
   
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    WTF_CSRF_ENABLED = True
    
    # Celery configurations
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///your_database.db'
    GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = os.environ.get('API_KEY') 
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/path/to/upload/folder')
    


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/protected')
@login_required
def protected():
    return "This is a protected page"