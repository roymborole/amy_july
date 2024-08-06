#config.py

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