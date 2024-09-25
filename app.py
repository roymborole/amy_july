from logging import FileHandler
from config import Flask, request, render_template, jsonify, redirect, url_for, os, ngrok
from financial_analysis import get_financial_data
from crypto_analysis import get_crypto_data, crypto_mapping
from ai_analysis import get_analysis_report
from visualization import create_chart
from flask import Flask, request, render_template, jsonify, redirect, url_for, send_from_directory
from crypto_prediction import run_crypto_prediction
from crypto_analysis import get_crypto_data, crypto_mapping
from crypto_ai_analysis import get_crypto_analysis_report
from crypto_news_analysis import get_crypto_news_summary, get_detailed_crypto_news
from crypto_comparison import compare_cryptos, generate_crypto_comparison_report
from flask import request, jsonify, flash
import postmarker
from postmarker.core import PostmarkClient
from rabbitmq_config import get_rabbitmq_connection, get_channel
import smtplib
from email.mime.text import MIMEText
from markupsafe import Markup
from flask import Flask, request, render_template, jsonify, redirect, url_for, session, send_from_directory, current_app
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from werkzeug.middleware.proxy_fix import ProxyFix
from login import init_auth, auth_bp
import warnings
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
import yfinance as yf
from news_analysis import get_news_summary
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from price_prediction import run_prediction
import torch
import json 
from models import User, TempSubscription, Subscription
import uuid
from postmarker.core import PostmarkClient
import threading
from comparison_analysis import compare_assets, generate_comparison_report
from datetime import datetime, timedelta
import time
from flask_login import login_user
from werkzeug.security import generate_password_hash
from ticker_utils import get_ticker_from_name 
from price_prediction import run_prediction
import os
from extensions import db, celery, migrate, init_extensions, Migrate, init_celery, make_celery, Celery,redis_client, get_redis_url
from dotenv import load_dotenv
from models import User, TempSubscription, Subscription
from logging.handlers import RotatingFileHandler
import sentry_sdk
from flask import Flask
from flask_mail import Mail, Message
from models import Subscription
import secrets
from models import PendingSubscription
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from sqlalchemy.exc import IntegrityError
from weekly_reports import send_weekly_reports
from subscription_management import create_subscription, confirm_subscription, unsubscribe, get_user_subscriptions
from pytz import timezone
from flask import Flask
from config import Config
from functools import partial
from celery_worker import send_weekly_reports
from trie import Trie
import time
from celery import Celery
from apscheduler.schedulers.background import BackgroundScheduler
from extensions import init_extensions, init_celery, make_celery, get_redis_url
from company_data import COMPANIES
from flask import send_file, make_response, request, current_app
import pdfkit
import logging
from werkzeug.utils import secure_filename
import os
import pandas as pd
from macroeconomic_analysis import generate_macroeconomic_analysis, save_macroeconomic_analysis, get_available_macro_analyses
import traceback
import asyncio
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_wtf import csrf
from models import User, Role
from flask_security import Security, SQLAlchemyUserDatastore
from flask_wtf.csrf import CSRFProtect
from contentful_utils import get_top_stories
from flask_cors import CORS
from flask import Flask, request, Response
import requests
import markdown2
import html 

user_datastore = SQLAlchemyUserDatastore(db, User, Role)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    CORS(app)
    app.config['DEBUG'] = True
    app.config.from_object(Config)

 

    load_dotenv()

    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['GA_TRACKING_ID'] = os.environ.get('GA_TRACKING_ID')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///your_database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')
    app.config['POSTMARK_SERVER_TOKEN'] = os.getenv('POSTMARK_SERVER_TOKEN')
    app.config['CELERY_BROKER_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    app.config['MAIL_SERVER'] = 'smtp.postmarkapp.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('POSTMARK_API_TOKEN')
    app.config['MAIL_PASSWORD'] = os.environ.get('POSTMARK_API_TOKEN')
    app.config['SECURITY_EMAIL_SENDER'] = 'reports@100-x.club'
    app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'security/login.html'
    app.config['SECURITY_REGISTER_USER_TEMPLATE'] = 'security/register.html'
    app.config['SECURITY_POST_REGISTER_VIEW'] = '/'
    app.config['WTF_CSRF_ENABLED'] = False

    # Flask-Security settings
    app.config['SECURITY_EMAIL_SENDER'] = 'reports@100-x.club'
    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_CONFIRMABLE'] = True
    app.config['SECURITY_RECOVERABLE'] = True
    app.config['SECURITY_CHANGEABLE'] = True

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    csrf = CSRFProtect(app)

    redis_url = get_redis_url()
    
    app.config.update(
        CELERY_BROKER_URL=redis_url,
        CELERY_RESULT_BACKEND=redis_url,
        broker_url=redis_url,
        result_backend=redis_url
    )

    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    init_celery(app)
    celery_app = make_celery(app)
    celery.conf.update(app.config)

    setup_done = False
    
    @app.before_request
    def setup_periodic_tasks():
        nonlocal setup_done
        if not setup_done:
            send_weekly_reports.apply_async()
            setup_done = True
            
    init_extensions(app)
    mail = Mail(app)
    csrf = CSRFProtect(app)
    security = Security(app, user_datastore)
    
    


    # Start the scheduler
    if not scheduler.running:
        scheduler.start()

    return app, celery

app, celery = create_app()

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='app.log')

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
scheduler.add_job(
        func=partial(send_weekly_reports, app),  # Use partial to pass app
        trigger=CronTrigger(
            day_of_week='fri',
            hour=15,
            minute=30,
            timezone=timezone('GMT')
        ),
        id='send_weekly_reports',
        name='Send weekly reports every Friday at 15:30 GMT',
        replace_existing=True
    )
scheduler.start()

from celery_worker import send_weekly_reports


if __name__ == '__main__':
    app.run()

sentry_sdk.init(
    dsn="https://199427486a2a2238cc49d3b3f7e4a971@o4507667288031232.ingest.us.sentry.io/4507667290521600",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

def setup_logging(app):
    # Set up file logging
    file_handler = RotatingFileHandler("app.log", maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

app.config['GA_TRACKING_ID'] = os.environ.get('GA_TRACKING_ID')
postmark = PostmarkClient(server_token=os.getenv('POSTMARK_SERVER_TOKEN'))
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
setup_logging(app)


load_dotenv()


generated_reports = {}

from flask_migrate import Migrate

migrate = Migrate(app, db)

migrate.init_app(app, db)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

warnings.filterwarnings('ignore', category=Warning)

with app.app_context():
    db.drop_all()
    db.create_all()
    if not user_datastore.find_user(email="admin@example.com"):
        user_datastore.create_user(email="admin@example.com", password="password", fs_uniquifier=str(uuid.uuid4()))
    db.session.commit()

file_handler = FileHandler("app.log")
file_handler.setLevel(logging.INFO)

# Add the handler to your app's logger
app.logger.addHandler(file_handler)

# Use this to log
app.logger.info("This is a log message")

def publish_to_queue(queue_name, message):
    connection = get_rabbitmq_connection()
    channel = get_channel(connection)
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    connection.close()


company_trie = Trie()  #what the fuck is this?
for company, ticker in COMPANIES.items():
    company_trie.insert(company, ticker)

from flask import render_template, abort
from contentful import Client
import os
from datetime import datetime

contentful_client = Client(
    space_id=os.environ.get('CONTENTFUL_SPACE_ID'),
    access_token=os.environ.get('CONTENTFUL_ACCESS_TOKEN')
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/blog')
def blog():
    try:
        # Make the simplest possible query
        entries = contentful_client.entries()
        
        # Log the number of entries and their content types
        print(f"Fetched {len(entries)} entries")
        for entry in entries:
            print(f"Entry ID: {entry.sys['id']}, Content Type: {entry.sys['content_type'].id}")
        
        return render_template('blog.html', posts=entries)
    except Exception as e:
        error_msg = f"Error fetching entries: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg)  # Print to console for immediate visibility
        return render_template('error.html', error=error_msg), 500


def markdown_render(content):
    # Convert Markdown to HTML
    html = markdown2.markdown(content, extras=['tables', 'fenced-code-blocks'])
    # Replace double underscores with strong tags
    html = html.replace('__', '<strong>', 1).replace('__', '</strong>', 1)
    return Markup(html)

# Register the filter with your Flask app
app.jinja_env.filters['markdown_render'] = markdown_render

def render_rich_text(content):
    if not content or not isinstance(content, dict):
        return ''

    def render_node(node):
        if node['nodeType'] == 'text':
            text = html.escape(node['value'])
            if node.get('marks'):
                for mark in node['marks']:
                    if mark['type'] == 'bold':
                        text = f'<strong>{text}</strong>'
                    elif mark['type'] == 'italic':
                        text = f'<em>{text}</em>'
            return text
        elif node['nodeType'] == 'paragraph':
            return '<p>' + ''.join(render_node(child) for child in node.get('content', [])) + '</p>'
        elif node['nodeType'] == 'heading-1':
            return '<h1>' + ''.join(render_node(child) for child in node.get('content', [])) + '</h1>'
        elif node['nodeType'] == 'heading-2':
            return '<h2>' + ''.join(render_node(child) for child in node.get('content', [])) + '</h2>'
        elif node['nodeType'] == 'embedded-asset-block':
            if 'data' in node and 'target' in node['data']:
                file_url = node['data']['target']['fields']['file']['url']
                return f'<img src="https:{file_url}" alt="Embedded asset" class="img-fluid">'
        elif node['nodeType'] == 'unordered-list':
            return '<ul>' + ''.join(f'<li>{render_node(item)}</li>' for item in node.get('content', [])) + '</ul>'
        elif node['nodeType'] == 'ordered-list':
            return '<ol>' + ''.join(f'<li>{render_node(item)}</li>' for item in node.get('content', [])) + '</ol>'
        elif node['nodeType'] == 'list-item':
            return ''.join(render_node(child) for child in node.get('content', []))
        else:
            return ''

    return Markup(''.join(render_node(node) for node in content.get('content', [])))

app.jinja_env.filters['render_rich_text'] = render_rich_text

@app.route('/blog/post/<post_id>')
def blog_post(post_id):
    try:
        entry = contentful_client.entry(post_id)
        return render_template('blog_post.html', post=entry)
    except Exception as e:
        error_msg = f"Error fetching blog post: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        app.logger.error(error_msg)
        return render_template('error.html', error=error_msg), 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

from flask_security import user_registered
from flask import flash

@user_registered.connect_via(app)
def user_registered_sighandler(app, user, **kwargs):
    flash('Thank you for registering! You have been successfully logged in.', 'success')
    
@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    prefix = request.args.get('prefix', '').lower()
    matches = company_trie.search_prefix(prefix)
    return jsonify([{'name': name, 'ticker': ticker} for name, ticker in matches[:10]])


@app.route('/crypto_predict/<crypto_name>')
def crypto_predict(crypto_name):
    prediction_data = run_crypto_prediction(crypto_name)
    if prediction_data is None:
        return render_template('error.html', message=f"Unable to generate prediction for {crypto_name}.")
    
    return render_template('crypto_prediction_report.html', 
                           asset_name=crypto_name,
                           prediction_data=prediction_data)

@app.route('/')
def home():
    try:
        # Fetch the latest blog post
        latest_post = contentful_client.entries({
            'content_type': 'Blog Posts',  # Replace with your actual content type ID
            'order': '-sys.createdAt',   # Order by creation date, most recent first
            'limit': 1                   # Limit to 1 entry (the latest)
        })
        
        if latest_post:
            latest_post = latest_post[0]  # Get the first (and only) entry
        else:
            latest_post = None
        
        return render_template('horse.html', post=latest_post)
    except Exception as e:
        error_msg = f"Error fetching latest blog post: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg)  # Print to console for immediate visibility
        return render_template('horse.html', post=None) 

@app.route('/scrib')
def scrib():
    return render_template('scrib.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Your signup logic here
    return render_template('signup.html')
    
@app.route('/crypto_news/<crypto_name>')
def display_crypto_news(crypto_name):
    news_summary = get_crypto_news_summary(crypto_name)
    detailed_news = get_detailed_crypto_news(crypto_name)
    return render_template('crypto_news.html', 
                           crypto_name=crypto_name, 
                           news_summary=news_summary,
                           detailed_news=detailed_news)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/crypto_report/<crypto_name>')
def display_crypto_report(crypto_name):
    if crypto_name.lower() not in crypto_mapping:
        return render_template('error.html', message=f"Unable to find data for cryptocurrency {crypto_name}.")
    
    raw_data = get_crypto_data(crypto_name)
    report_content = get_crypto_analysis_report(raw_data, raw_data['asset_name'])
    
    charts = {
        'price_sma': create_chart(raw_data['historical_data'], 'price_sma', crypto_name),
        'rsi': create_chart(raw_data['historical_data'], 'rsi', crypto_name),
        'bollinger': create_chart(raw_data['historical_data'], 'bollinger', crypto_name)
        
    }
    
    return render_template('crypto_report.html', 
                           asset_name=raw_data['asset_name'],
                           raw_data=raw_data,
                           charts=charts,
                           report_content=report_content)

@app.route('/gym')
def gym():
    return render_template('gym.html')

@app.route('/dummy')
def dummy():
    return render_template('dummy.html')

@app.route('/ias')
def ias():
    return render_template('ias.html')

@app.route('/scusy')
def scusy():
    return render_template('scusy.html')

@app.route('/technical_analysis')
def technical_analysis():
    return render_template('technical_analysis.html')

@app.route('/investment_analysis')
def investment_analysis():
    return render_template('investment_analysis.html')

@app.route('/ias_loading/<ticker>')
def ias_loading(ticker):
    return render_template('ias_loading.html', ticker=ticker)

@app.route('/ias_report/<name_or_ticker>')
def ias_report(name_or_ticker):
     return render_template('ias_report.html', ticker=ticker)

@app.route('/glossary')
def glossary():
    return render_template('glossary.html')

import os
from flask import Flask, send_from_directory


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')



@app.route('/upload_macro', methods=['GET', 'POST'])
def upload_macro():
    if request.method == 'POST':
        ticker = request.form['ticker'].upper()
        content = request.form['content']
        files = request.files.getlist('files')

        uploaded_files = []

        if content:
            save_macroeconomic_analysis(ticker, content)
            uploaded_files.append(f"{ticker}_macro_analysis.txt")

        if files:
            for file in files:
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file_ext = os.path.splitext(filename)[1]
                    if file_ext not in ['.txt', '.pdf', '.doc', '.docx', '.rtf']:
                        continue
                    
                    new_filename = f"{ticker}_{filename}"
                    file_path = os.path.join('uploads', new_filename)
                    file.save(file_path)
                    uploaded_files.append(new_filename)

        if uploaded_files:
            message = f"Files uploaded successfully for {ticker}: {', '.join(uploaded_files)}"
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': 'No files were uploaded. Please enter text or upload files.'})

    return render_template('upload_macro.html')

@app.route('/stock_reports')
def stock_reports():
    return render_template('netflix_style.html')

@app.route('/netflix_style')
def netflix_style():
    stocks = [
        {'name': 'Facebook', 'ticker': 'FB', 'image': 'facebook_logo.png'},
        {'name': 'Tesla', 'ticker': 'TSLA', 'image': 'tesla_logo.png'},
        {'name': 'Spotify', 'ticker': 'SPOT', 'image': 'spotify_logo.png'},
        {'name': 'Microsoft', 'ticker': 'MSFT', 'image': 'microsoft_logo.png'},
        {'name': 'Amazon', 'ticker': 'AMZN', 'image': 'amazon_logo.png'},
        {'name': 'Apple', 'ticker': 'AAPL', 'image': 'apple_logo.png'},
    ]
    return render_template('netflix_style.html', stocks=stocks)

@app.route('/macro_boomin')
def macro_boomin():
    companies = get_available_macro_analyses()
    return render_template('macro_boomin.html', companies=companies)

def handle_nan(data):
    if isinstance(data, dict):
        return {k: handle_nan(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [handle_nan(v) for v in data]
    elif isinstance(data, float) and np.isnan(data):
        return None
    else:
        return data
    

@app.route('/generate_macro_analysis/<ticker>')
def generate_macro_analysis_route(ticker):
    try:
        analysis, error = generate_macroeconomic_analysis(ticker)
        if error:
            return jsonify({'error': str(error)})
        
        financial_data = get_financial_data(ticker)
        if not financial_data:
            return jsonify({'error': 'Unable to fetch financial data', 'analysis': analysis})
        
        historical_data = financial_data.get('historical_data')
        if isinstance(historical_data, pd.DataFrame) and not historical_data.empty:
            historical_data = historical_data.reset_index().replace({np.nan: None}).to_dict('records')
        else:
            historical_data = []
        
        # Handle NaN values in the entire financial_data dictionary
        financial_data = handle_nan(financial_data)
        
        return jsonify({
            'analysis': analysis,
            'historical_data': historical_data,
            'financial_data': financial_data
        })
    except Exception as e:
        app.logger.exception(f"Unexpected error during macro analysis for {ticker}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
    

def get_ticker_from_name(input_str):
    # Check if input is already a ticker
    if input_str.upper() in COMPANIES.values():
        return input_str.upper()
    
    # Check if input is a full company name
    for name, ticker in COMPANIES.items():
        if name.lower() == input_str.lower():
            return ticker
    
    # If not found, return the input as is
    return input_str


csrf = CSRFProtect(app)

@app.route('/generate_macro', methods=['POST'])
@csrf.exempt
def generate_macro():
    input_str = request.form['ticker']
    ticker = get_ticker_from_name(input_str)
    app.logger.info(f"Generating macroeconomic analysis for input: {input_str}, resolved ticker: {ticker}")

    try:
        # Get financial data
        financial_data = get_financial_data(ticker)
        app.logger.info(f"Financial data retrieved: {financial_data}")

        if not financial_data:
            app.logger.error(f"Failed to retrieve financial data for {ticker}")
            return jsonify({'error': f"Unable to retrieve financial data for {ticker}"}), 400

        # Generate macroeconomic analysis
        analysis, error = generate_macroeconomic_analysis(ticker)
        
        if error:
            app.logger.error(f"Error generating macroeconomic analysis for {ticker}: {error}")
            return jsonify({'error': error}), 400

        if analysis is None:
            app.logger.warning(f"No macroeconomic analysis generated for {ticker}")
            analysis = "No macroeconomic analysis available for this asset."
        else:
            app.logger.info(f"Analysis generated: {analysis[:100]}...")  # Log first 100 chars of analysis

        # Get performance data and price history
        performance_data = financial_data.get('performance', {})
        price_history = financial_data.get('price_history', {})

        app.logger.info(f"Successfully processed macroeconomic data for {ticker}")
        return jsonify({
            'analysis': analysis,
            'performance': performance_data,
            'price_history': price_history
        })

    except Exception as e:
        app.logger.exception(f"Unexpected error during macro generation for {ticker}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

csrf.exempt(generate_macro)
    
@app.route('/macroeconomic_analysis')
def macroeconomic_analysis():
    return render_template('macroeconomic_analysis.html')

@app.route('/available_analyses')
def available_analyses():
    analyses = get_available_macro_analyses()
    return render_template('available_analyses.html', analyses=analyses)

@app.route('/crypto_compare', methods=['POST'])
def crypto_compare():
    crypto1 = request.form.get('crypto1')
    crypto2 = request.form.get('crypto2')
    if not crypto1 or not crypto2:
        return "Missing input", 400
    return redirect(url_for('display_crypto_comparison', crypto1=crypto1, crypto2=crypto2))

@app.route('/crypto_comparison/<crypto1>/<crypto2>')
def display_crypto_comparison(crypto1, crypto2):
    comparison_data = compare_cryptos(crypto1, crypto2)
    if comparison_data is None:
        return render_template('error.html', message=f"Unable to fetch data for comparison between {crypto1} and {crypto2}.")
    
    report_content = generate_crypto_comparison_report(comparison_data)
    return render_template('crypto_comparison_report.html', 
                           crypto1=crypto1, 
                           crypto2=crypto2, 
                           report_content=report_content)

@app.route('/compare/<asset1>/<asset2>')
def compare_assets_route(asset1, asset2):
    comparison_data = compare_assets(asset1, asset2)
    if comparison_data is None:
        return render_template('error.html', message=f"Unable to fetch data for comparison between {asset1} and {asset2}.")
    
    report_content = generate_comparison_report(comparison_data)
    return render_template('comparison_report.html', 
                           asset1=asset1, 
                           asset2=asset2, 
                           report_content=report_content)
def get_client_ip():
    return request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)


@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    
    # Perform the search
    search_results = []

    # Check if it's a cryptocurrency
    if query.lower() in crypto_mapping:
        search_results.append({
            'name': query,
            'type': 'Cryptocurrency',
            'symbol': crypto_mapping[query.lower()]
        })
    
    # Check if it's a stock
    stock_ticker = get_ticker_from_name(query)
    if stock_ticker:
        search_results.append({
            'name': query,
            'type': 'Stock',
            'symbol': stock_ticker
        })
    
    # If no results found
    if not search_results:
        search_results.append({
            'name': query,
            'type': 'Unknown',
            'symbol': 'N/A'
        })

    return jsonify({'results': search_results})



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/generate_price_prediction/<name_or_ticker>')
def get_price_prediction(name_or_ticker):
    start_time = time.time()
    name_or_ticker = request.form.get('name_or_ticker')

    print(f"Received request for: {name_or_ticker}")
    if not name_or_ticker or name_or_ticker.lower() == 'null':
        return jsonify({'error': 'Invalid input'}), 400
    
    ticker = get_ticker_from_name(name_or_ticker)
    print(f"Resolved ticker: {ticker}")
    
    if not ticker:
        return jsonify({'error': 'Unable to find ticker'}), 400
    
    prediction_result = run_prediction(ticker)
    if prediction_result:
        response = {
            'symbol': prediction_result['symbol'],
            'current_price': prediction_result['current_price'],
            'predicted_price': prediction_result['predicted_price'],
            'confidence_interval': {
                'lower': prediction_result['ci_lower'],
                'upper': prediction_result['ci_upper']
            },
            'prediction_date': prediction_result['prediction_date'],
            'display_date_range': prediction_result['display_date_range']
        } 
        end_time = time.time()
        generation_time = end_time - start_time

        return jsonify(response)
    else:
        return jsonify({'error': 'Failed to generate prediction'}), 500

@app.route('/loading_news/<name_or_ticker>')
def loading_news(name_or_ticker):
    return render_template('loading_news.html', asset_name=name_or_ticker)

@app.route('/news/<name_or_ticker>')
def display_news(name_or_ticker):
    ticker = get_ticker_from_name(name_or_ticker)
    if not ticker:
        return render_template('error.html', message=f"Unable to find ticker for {name_or_ticker}.")
    
    news_summary = get_news_summary(ticker)
    return render_template('news.html', asset_name=name_or_ticker, news_summary=news_summary)

@app.route('/', methods=['GET', 'POST'])
def index():
    app.logger.info("Index route accessed")
    
    if request.method == 'POST':
        app.logger.info("POST request received")
        name_or_ticker = request.form.get('name_or_ticker')
        
        if not name_or_ticker:
            app.logger.warning("Missing input")
            return "Missing input", 400
        
        app.logger.info(f"Searching for asset: {name_or_ticker}")
        
        # Check if we have cached data in Redis
        cached_data = redis_client.get(name_or_ticker)
        if cached_data:
            app.logger.info(f"Cache hit for {name_or_ticker}")
            # If we have cached data, you might want to use it or update it
            # For now, we'll just log it and continue with the normal flow
            cached_data = json.loads(cached_data)
            app.logger.info(f"Cached data: {cached_data}")
        else:
            app.logger.info(f"Cache miss for {name_or_ticker}")
        
        return redirect(url_for('display_report', name_or_ticker=name_or_ticker))
    
    app.logger.info("Rendering index.html")
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    user_info = google.get("/oauth2/v2/userinfo").json()
    user_id = user_info['id']
    
    session['user_id'] = user_id
    session['login_time'] = time.time()
    return redirect(url_for("index"))

@app.route('/generate_report', methods=['POST'])
def generate_report():
    start_time = time.time()
    name_or_ticker = request.form.get('name_or_ticker')
    if not name_or_ticker:
        return jsonify({'error': 'Missing input'}), 400

    try:
        # Instead of generating the report here, publish a message to RabbitMQ
        publish_to_queue('report_requests', json.dumps({
            'name_or_ticker': name_or_ticker,
            'user_id': session.get('user_id', 'Anonymous')
        }))

        end_time = time.time()
        queue_time = end_time - start_time

        return jsonify({'message': 'Report generation request submitted. Please check back later for results.'}), 202

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in generate_report: {str(e)}")
        print(f"Traceback: {error_traceback}")

        return jsonify({'error': str(e), 'traceback': error_traceback}), 500


@app.route('/compare', methods=['GET', 'POST'])
def compare():
    if request.method == 'POST':
        asset1 = request.form.get('asset1')
        asset2 = request.form.get('asset2')
    else:
        asset1 = request.args.get('asset1')
        asset2 = request.args.get('asset2')

    if not asset1 or not asset2:
        return "Missing input", 400

    return redirect(url_for('display_comparison', asset1=asset1, asset2=asset2))

@app.route('/compare/<asset1>/<asset2>')
def display_comparison(asset1, asset2):
    comparison_data = compare_assets(asset1, asset2)
    if comparison_data:
        report = generate_comparison_report(comparison_data)
        return render_template('comparison_report.html', report=report)
    else:
        return render_template('error.html', message="Unable to generate comparison report.")
    

@app.route('/api/compare', methods=['POST'])
def api_compare():
    asset1 = request.json['asset1']
    asset2 = request.json['asset2']
    comparison_data = compare_assets(asset1, asset2)
    return jsonify(comparison_data)

csrf = CSRFProtect(app)

@app.route('/send_report', methods=['POST'])
@csrf.exempt
def send_report():
    try:
        data = request.get_json()
        email = data.get('email')
        asset_name = data.get('asset_name')
        report_content = data.get('report_content')

        if not email or not asset_name or not report_content:
            return jsonify({'message': 'Missing required data'}), 400

        postmark.emails.send(
            From='reports@100-x.club',
            To=email,
            Subject=f'Analysis Report for {asset_name}',
            HtmlBody=f"""
            <html>
            <body>
                <h1>Analysis Report for {asset_name}</h1>
                {report_content}
            </body>
            </html>
            """
        )
        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error in send_report: {str(e)}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500

def generate_report_background(name_or_ticker):
    try:
        if name_or_ticker.lower() in crypto_mapping:
            raw_data = get_crypto_data(name_or_ticker)
            report_content = get_crypto_analysis_report(raw_data, raw_data['asset_name'])
        else:
            ticker = get_ticker_from_name(name_or_ticker)
            if ticker:
                raw_data = get_financial_data(ticker)
                report_content = get_analysis_report(raw_data, raw_data['asset_name'])
            else:
                generated_reports[name_or_ticker] = {'error': f"Unable to find a matching stock or cryptocurrency for {name_or_ticker}."}
                return

        if not raw_data:
            generated_reports[name_or_ticker] = {'error': f"Unable to fetch data for {name_or_ticker}. Please check the input and try again."}
            return
        
        charts = {
            'price_sma': create_chart(raw_data['historical_data'], 'price_sma', name_or_ticker),
            'rsi': create_chart(raw_data['historical_data'], 'rsi', name_or_ticker),
            'bollinger': create_chart(raw_data['historical_data'], 'bollinger', name_or_ticker),
        }
        
        for chart_type, chart_data in charts.items():
            placeholder = f'[{chart_type.upper()}_CHART]'
            chart_html = f'<img src="data:image/png;base64,{chart_data}" alt="{chart_type} chart" class="chart">'
            report_content = report_content.replace(placeholder, chart_html)

        generated_reports[name_or_ticker] = {
            'asset_name': raw_data['asset_name'],
            'raw_data': raw_data,
            'charts': charts,
            'report_content': report_content
        }
    except Exception as e:
        print(f"Error generating report for {name_or_ticker}: {str(e)}")
        generated_reports[name_or_ticker] = {'error': str(e)}

@app.route('/check_report/<name_or_ticker>')
def check_report(name_or_ticker):
    if name_or_ticker in generated_reports:
        if 'error' in generated_reports[name_or_ticker]:
            return jsonify({'status': 'error', 'message': generated_reports[name_or_ticker]['error']})
        return jsonify({'status': 'ready'})
    return jsonify({'status': 'processing'})

@app.route('/report/<name_or_ticker>')
def display_report(name_or_ticker):
    if name_or_ticker.lower() in crypto_mapping:
        raw_data = get_crypto_data(name_or_ticker)
    else:
        raw_data = get_financial_data(name_or_ticker)

    if not raw_data:
        return render_template('error.html', message=f"Unable to fetch data for {name_or_ticker}. Please check the input and try again.")

    charts = {}
    if 'historical_data' in raw_data:
        charts = {
            'price_sma': create_chart(raw_data['historical_data'], 'price_sma', name_or_ticker),
            'rsi': create_chart(raw_data['historical_data'], 'rsi', name_or_ticker),
            'bollinger': create_chart(raw_data['historical_data'], 'bollinger', name_or_ticker)
        }
    else:
        print("No historical data available for charts")

    report_content = get_analysis_report(raw_data, raw_data['asset_name'])

    for chart_type, chart_data in charts.items():
        placeholder = f'[{chart_type.upper()}_CHART]'
        chart_html = f'<img src="data:image/png;base64,{chart_data}" alt="{chart_type} chart" class="chart">'
        report_content = report_content.replace(placeholder, chart_html)

    return render_template('report.html', 
                           asset_name=raw_data['asset_name'],
                           raw_data=raw_data,
                           charts=charts,
                           report_content=report_content)
    
@app.route('/process_report/<name_or_ticker>')
def process_report(name_or_ticker):
    try:
        if name_or_ticker.lower() in crypto_mapping:
            raw_data = get_crypto_data(name_or_ticker)
            report_content = get_crypto_analysis_report(raw_data, raw_data['asset_name'])
        else:
            raw_data = get_financial_data(name_or_ticker)
            if raw_data is None:
                return render_template('error.html', message=f"Unable to fetch data for {name_or_ticker}. Please check the input and try again.")
            report_content = get_analysis_report(raw_data, raw_data['asset_name'])

        if 'asset_name' not in raw_data:
            raw_data['asset_name'] = name_or_ticker.capitalize()
        
        charts = {
            'price_sma': create_chart(raw_data['historical_data'], 'price_sma', name_or_ticker),
            'rsi': create_chart(raw_data['historical_data'], 'rsi', name_or_ticker),
            'bollinger': create_chart(raw_data['historical_data'], 'bollinger', name_or_ticker)
        }
        
        for chart_type, chart_data in charts.items():
            placeholder = f'[{chart_type.upper()}_CHART]'
            chart_html = f'<img src="data:image/png;base64,{chart_data}" alt="{chart_type} chart" class="chart">'
            report_content = report_content.replace(placeholder, chart_html)

        return render_template('report.html', 
                               asset_name=raw_data['asset_name'],
                               raw_data=raw_data,
                               charts=charts,
                               report_content=report_content)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in process_report: {str(e)}")
        print(f"Traceback: {error_traceback}")
        return render_template('error.html', message=f"An error occurred while generating the report: {str(e)}")
    
@app.route('/loading_prediction/<name_or_ticker>')
def loading_prediction(name_or_ticker):
    if name_or_ticker.lower() in crypto_mapping:
        return render_template('loading_crypto_prediction.html', asset_name=name_or_ticker)
    else:
        return render_template('loading_stock_prediction.html', asset_name=name_or_ticker)
    
@app.route('/loading_crypto_prediction/<crypto_name>')
def loading_crypto_prediction(crypto_name):
    return render_template('loading_crypto_prediction.html', asset_name=crypto_name)
        
def get_prediction_data(name_or_ticker):
    prediction_result = run_prediction(name_or_ticker)
    if prediction_result:
        return {
            "current_price": prediction_result["current_price"],
            "predicted_price": prediction_result["predicted_price"],
            "prediction_date": prediction_result["prediction_date"],
            "ci_lower": prediction_result["ci_lower"],
            "ci_upper": prediction_result["ci_upper"],
            "plot_prediction": prediction_result["plot_prediction"],
            "plot_full": prediction_result["plot_full"],
            "analyst_recommendations": prediction_result["analyst_recommendations"]
        }
    return None

@app.route('/predict/<name_or_ticker>')
def predict(name_or_ticker):
    if name_or_ticker.lower() in crypto_mapping:
        # Handle cryptocurrency prediction
        prediction_data = run_crypto_prediction(name_or_ticker)
        if prediction_data is None:
            return render_template('error.html', message=f"Unable to generate prediction for cryptocurrency {name_or_ticker}.")
        
        return render_template('crypto_prediction_report.html', 
                               asset_name=name_or_ticker,
                               prediction_data=prediction_data)
    else:
        # Handle stock prediction
        prediction_data = run_prediction(name_or_ticker)
        if prediction_data is None:
            return render_template('error.html', message=f"Unable to generate prediction for stock {name_or_ticker}.")
        
        return render_template('prediction_report.html', 
                               asset_name=name_or_ticker,
                               prediction_data=prediction_data)
    
@app.route('/prediction/<name_or_ticker>')
def display_prediction(name_or_ticker):
    prediction_data = get_prediction_data(name_or_ticker)
    if not prediction_data:
        return render_template('error.html', message=f"Unable to fetch prediction data for {name_or_ticker}. Please check the input and try again.")
    
    return render_template('prediction_report.html', 
                           asset_name=name_or_ticker,
                           prediction_data=prediction_data)


@app.route('/about')
def about():
    return render_template('aboutus.html')

@app.route('/ns')
def ns():
    return render_template('ns.html') #test file

@app.route('/works')
def works():
    return render_template('works.html') #How it works route 

@app.route('/horse')
def horse():
    return render_template('horse.html') #now she's index.

@app.route('/send_comparison_report', methods=['POST'])
@csrf.exempt
def send_comparison_report():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'message': 'Invalid JSON'}), 400

        email = data.get('email')
        asset1 = data.get('asset1')
        asset2 = data.get('asset2')
        report_content = data.get('report_content')

        if not email or not asset1 or not asset2 or not report_content:
            return jsonify({'message': 'Missing required data'}), 400

    
        postmark.emails.send(
            From='reports@100-x.club',
            To=email,
            Subject=f'Comparison Report: {asset1} vs {asset2}',
            HtmlBody=f"""
            <html>
            <body>
                <h1>Comparison Report: {asset1} vs {asset2}</h1>
                {report_content}
            </body>
            </html>
            """
        )
        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error in send_comparison_report: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'message': f'Server error: {str(e)}'}), 500


@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    email = request.json.get('email')
    asset_name = request.json.get('asset_name')
    
    if not email or not asset_name:
        return jsonify({'error': 'Email and asset name are required'}), 400
    
    result = create_subscription(email, asset_name)
    if result == "already_subscribed":
        return jsonify({'message': 'You are already subscribed to this asset.'}), 200
    elif result == "confirmation_sent":
        return jsonify({'message': 'Subscription request received. Please check your email for confirmation.'}), 200
    else:
        return jsonify({'error': 'An error occurred while processing your subscription.'}), 500

@app.route('/confirm_subscription/<token>')
def confirm_subscription_route(token):
    result = confirm_subscription(token)
    if result == "subscription_confirmed":
        return 'Subscription confirmed. You will now receive weekly reports.'
    elif result == "error":
        return 'An error occurred while confirming your subscription. Please try again or contact support.', 500
    else:
        return 'Invalid or expired confirmation link.', 400

@app.route('/test_weekly_reports')
def test_weekly_reports():
    send_weekly_reports(app)
    return "Weekly reports sending process initiated (check logs for details)"

@app.route('/subscription_success')
def subscription_success():
    return render_template('subscription_success.html')

@app.route('/jodi')
def jodi():
    return render_template('jodi.html')

@app.route('/aaa')
def aaa():
    return render_template('aaa.html')


@app.route('/ta_staging')
def ta_staging():
    return render_template('ta_staging.html')

@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/export-pdf/<report_type>', methods=['POST'])
def export_pdf(report_type):
    try:
        url = request.json['url']
        
        # Configure pdfkit options
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        
        # Generate PDF
        pdf = pdfkit.from_url(url, False, options=options)
        
        # Create a response
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={report_type}_report.pdf'
        
        return response

    except Exception as e:
        current_app.logger.error(f"Error generating PDF: {str(e)}")
        return make_response(jsonify({"error": "Failed to generate PDF"}), 500)

@app.route('/terms_of_service')
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route('/loading/<name_or_ticker>')
def loading(name_or_ticker):
    if name_or_ticker not in generated_reports:
        # Start the report generation in a background thread
        thread = threading.Thread(target=generate_report_background, args=(name_or_ticker,))
        thread.start()
    return render_template('loading.html', name_or_ticker=name_or_ticker)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        message = request.form['message']

        try:
            postmark.emails.send(
                From='info@100-x.club',
                To='mothei@borole.com',
                Subject='Contact Us Form Submission',
                HtmlBody=f"""
                <html>
                <body>
                    <h2>New Contact Form Submission</h2>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Phone:</strong> {phone}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Message:</strong> {message}</p>
                </body>
                </html>
                """
            )
            return redirect(url_for('contact'))
        except Exception as e:
            print(f"Failed to send email: {e}")
            return jsonify({'error': 'Failed to send email'}), 500

    return render_template('contact.html')

@app.route('/get_report/<name_or_ticker>')
def get_report(name_or_ticker):
    try:
        if name_or_ticker.lower() in crypto_mapping:
            raw_data = get_crypto_data(name_or_ticker)
            report_content = get_crypto_analysis_report(raw_data, raw_data['asset_name'])
        else:
            ticker = get_ticker_from_name(name_or_ticker)
            if ticker:
                raw_data = get_financial_data(ticker)
                report_content = get_analysis_report(raw_data, raw_data['asset_name'])
            else:
                return jsonify({'error': 'Unable to find a matching stock or cryptocurrency.'}), 400

        if not raw_data:
            return jsonify({'error': 'Unable to fetch data for the given input.'}), 400
        
        if 'asset_name' not in raw_data:
            raw_data['asset_name'] = name_or_ticker.capitalize()
        
        charts = {
            'price_sma': create_chart(raw_data['historical_data'], 'price_sma', name_or_ticker),
            'rsi': create_chart(raw_data['historical_data'], 'rsi', name_or_ticker),
            'bollinger': create_chart(raw_data['historical_data'], 'bollinger', name_or_ticker)
        }
        raw_data['charts'] = charts
        
        for chart_type, chart_data in charts.items():
            placeholder = f'[{chart_type.upper()}_CHART]'
            chart_html = f'<img src="data:image/png;base64,{chart_data}" alt="{chart_type} chart" style="max-width: 100%; height: auto;">'
            report_content = report_content.replace(placeholder, chart_html)

        header1_url = url_for('static', filename='Header1.png')
        header2_url = url_for('static', filename='Header2.png')
        report_content = f'<img src="{header1_url}" alt="Header 1" class="header-image">\n' + report_content
        report_content += f'\n<img src="{header2_url}" alt="Header 2" class="header-image">'
        
        return render_template('report.html', 
                               asset_name=raw_data['asset_name'],
                               raw_data=raw_data,
                               charts=charts,
                               report_content=report_content)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in get_report: {str(e)}")
        print(f"Traceback: {error_traceback}")
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500
    
if __name__ == '__main__':
     with app.app_context():
        db.create_all()
        if app.debug:
            ngrok_auth_token = os.environ.get("NGROK_AUTH_TOKEN")
        if ngrok_auth_token:
            ngrok.set_auth_token(ngrok_auth_token)
            try:
                public_url = ngrok.connect(4040)
                print(f' * ngrok tunnel "{public_url}" -> "http://127.0.0.1:4040"')
            except Exception as e:
                print(f"An error occurred while connecting to ngrok: {str(e)}")
                exit(1)
        else:
            print("NGROK_AUTH_TOKEN not found. Please set it as an environment variable.")
            exit(1)

        app.run(host='127.0.0.1', port=4040)