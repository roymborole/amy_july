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
from pyngrok import ngrok
import json
from flask import Flask, request, render_template, jsonify, redirect, url_for


ANTHROPIC_API_KEY = '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'
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

CRYPTOCOMPARE_API_URL = "https://min-api.cryptocompare.com/data/"
CRYPTOCOMPARE_API_KEY = os.getenv("e03c9d9161bf847ab28f002dda9664571e691f5ee7a2209e774b490597217bab")
    
START_DATE = '2020-01-01'
END_DATE = '2024-07-16'

