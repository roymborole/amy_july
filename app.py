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
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, render_template, jsonify, redirect, url_for, session, send_from_directory
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from login import init_auth, google_bp, get_db, User
import warnings
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
import yfinance as yf
from news_analysis import get_news_summary
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from price_prediction import run_prediction
from price_prediction import run_prediction
import torch
import json 
from flask import request, jsonify
from models import User, db, TempSubscription, Subscription
import uuid
from postmarker.core import PostmarkClient
from flask import request, jsonify
import threading
from comparison_analysis import compare_assets, generate_comparison_report
from mixpanel import Mixpanel
from datetime import datetime, timedelta
import time
from flask_login import login_user
from werkzeug.security import generate_password_hash
import mixpanel
from ticker_utils import get_ticker_from_name 
from price_prediction import run_prediction
from dotenv import load_dotenv
load_dotenv()


# ... (rest of the imports and app setup)

mp_eu = mixpanel.Mixpanel(
  "bfc13708c14264e73210551e942a0063",
  consumer=mixpanel.Consumer(api_host="api-eu.mixpanel.com"),
)


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

warnings.filterwarnings('ignore', category=Warning)

app = Flask(__name__, static_folder='static', static_url_path='/static')
postmark = PostmarkClient(server_token='4b36353e-54d7-49a6-b572-fa56e8675c4a')
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['SECRET_KEY'] = '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'  # Change this!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

generated_reports = {}

db.init_app(app)

init_auth(app)

with app.app_context():
    db.create_all()


@app.route('/crypto_predict/<crypto_name>')
def crypto_predict(crypto_name):
    prediction_data = run_crypto_prediction(crypto_name)
    if prediction_data is None:
        return render_template('error.html', message=f"Unable to generate prediction for {crypto_name}.")
    
    return render_template('crypto_prediction_report.html', 
                           asset_name=crypto_name,
                           prediction_data=prediction_data)

@app.route('/montage')
def montage():
    comparisons = {
        1: { 'stock1': 'AMD', 'stock2': 'NVDA' },
        2: { 'stock1': 'AAPL', 'stock2': 'MSFT' },
        3: { 'stock1': 'GOOGL', 'stock2': 'META' },
        4: { 'stock1': 'TSLA', 'stock2': 'F' },
        5: { 'stock1': 'AMZN', 'stock2': 'WMT' }
    }
    return render_template('montage.html', comparisons=comparisons)

@app.route('/crypto_news/<crypto_name>')
def display_crypto_news(crypto_name):
    news_summary = get_crypto_news_summary(crypto_name)
    detailed_news = get_detailed_crypto_news(crypto_name)
    return render_template('crypto_news.html', 
                           crypto_name=crypto_name, 
                           news_summary=news_summary,
                           detailed_news=detailed_news)

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
    mp_eu.track(session.get('user_id', 'Anonymous'), 'Search', {
       'page': request.path,
        'ip': get_client_ip(),
        'user_agent': request.user_agent.string,
        'referrer': request.referrer
    })
    
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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('signup'))

        # Create new user
        new_user = User(
            email=email,
            name=name,
            password=generate_password_hash(password, method='sha256')
        )

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Log the user in
        login_user(new_user)

        # Track the signup event in Mixpanel
        mp_eu.track(new_user.id, 'Sign Up', {
            'ip': get_client_ip(),
            'user_agent': request.user_agent.string,
            'email': email,
            'name': name
        })

        # Set user properties in Mixpanel
        mp_eu.people_set(new_user.id, {
            '$email': email,
            '$name': name,
            'sign_up_date': datetime.datetime.now().isoformat()
        })

        flash('Account created successfully')
        return redirect(url_for('index'))

    # If it's a GET request, just render the signup form
    return render_template('signup.html')

@app.route('/logout')
def logout():
    start_time = session.get('login_time')
    if start_time:
        time_on_site = time.time() - start_time
        mp_eu.track(session.get('user_id'), 'Logout', {
            'time_on_site': time_on_site
        })
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
        
        
        mp_eu.track(session.get('user_id', 'Anonymous'), 'Prediction Generated', {
            'asset_name': name_or_ticker,
            'generation_time': generation_time,
            'ip': get_client_ip(),
            'user_agent': request.user_agent.string

            
        })

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
    if request.method == 'POST':
        name_or_ticker = request.form.get('name_or_ticker')
        if not name_or_ticker:
            return "Missing input", 400
        mp_eu.track(session.get('user_id', 'Asset Search'), 'Asset Search', {
            'asset_name': name_or_ticker
        })
        
        return redirect(url_for('display_report', name_or_ticker=name_or_ticker))
    
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if not google.authorized:
        # Track login attempt
        mp_eu.track('Anonymous', 'Login Attempt', {
            'method': 'Google'
        })
        return redirect(url_for("google.login"))
    
    # If the user is already logged in, track this event
    user_info = google.get("/oauth2/v2/userinfo").json()
    user_id = user_info['id']
    mp_eu.track(user_id, 'Login Success', {
        'method': 'Google'
    })
    
    # Set or update user properties
    mp_eu.people_set(user_id, {
        '$email': user_info.get('email'),
        '$name': user_info.get('name'),
        'last_login': datetime.datetime.now().isoformat()
    })
    session['login_time'] = time.time()
    return redirect(url_for("index"))

@app.route('/generate_report', methods=['POST'])
def generate_report():
    start_time = time.time()
    name_or_ticker = request.form.get('name_or_ticker')
    if not name_or_ticker:
        return jsonify({'error': 'Missing input'}), 400
    
    try:
        if name_or_ticker.lower() in crypto_mapping:
            raw_data = get_crypto_data(name_or_ticker)
            report_content = get_crypto_analysis_report(raw_data, raw_data['asset_name'])
            asset_type = 'Cryptocurrency'
        else:
            ticker = get_ticker_from_name(name_or_ticker)
            if ticker:
                raw_data = get_financial_data(ticker)
                report_content = get_analysis_report(raw_data, raw_data['asset_name'])
                asset_type = 'Stock'
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
        
        end_time = time.time()
        generation_time = end_time - start_time
    
        # Track report generation
        print("Tracking report generation in Mixpanel")  # Debug print
        mp_eu.track(session.get('user_id', 'Anonymous'), 'Report Generated', {
            'asset_name': raw_data['asset_name'],
            'asset_type': asset_type
            
        })
        
        return jsonify({'report': report_content})
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in generate_report: {str(e)}")
        print(f"Traceback: {error_traceback}")
        
        # Track error
        mp_eu.track(session.get('user_id', 'Anonymous'), 'Report Generation Error', {
            'asset_name': name_or_ticker,
            'error_message': str(e)
        })
        
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

@app.route('/compare', methods=['POST'])
def compare():
    asset1 = request.form.get('asset1')
    asset2 = request.form.get('asset2')
    if not asset1 or not asset2:
        return "Missing input", 400
    return redirect(url_for('display_comparison', asset1=asset1, asset2=asset2))

@app.route('/comparison/<asset1>/<asset2>')
def display_comparison(asset1, asset2):
    comparison_data = compare_assets(asset1, asset2)
    if comparison_data is None:
        return render_template('error.html', message=f"Unable to fetch data for comparison between {asset1} and {asset2}.")
    
    report_content = generate_comparison_report(comparison_data)
    return render_template('comparison_report.html', 
                           asset1=asset1, 
                           asset2=asset2, 
                           report_content=report_content)

@app.route('/api/compare', methods=['POST'])
def api_compare():
    asset1 = request.json['asset1']
    asset2 = request.json['asset2']
    comparison_data = compare_assets(asset1, asset2)
    return jsonify(comparison_data)

@app.route('/send_report', methods=['POST'])
def send_report():
    data = request.json
    email = data.get('email')
    asset_name = data.get('asset_name')
    report_content = data.get('report_content')

    if not email or not asset_name or not report_content:
        return jsonify({'message': 'Missing required data'}), 400

    try:
        postmark.emails.send(
            From='roy@borole.com',
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
        print(f"Error sending email: {str(e)}")
        return jsonify({'message': 'Failed to send email'}), 500

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
            'bollinger': create_chart(raw_data['historical_data'], 'bollinger', name_or_ticker)
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
    if name_or_ticker not in generated_reports:
        return render_template('error.html', message=f"Report for {name_or_ticker} not found. Please try generating the report again.")
    
    report_data = generated_reports[name_or_ticker]
    if 'error' in report_data:
        return render_template('error.html', message=report_data['error'])
    
    return render_template('report.html', 
                           asset_name=report_data['asset_name'],
                           raw_data=report_data['raw_data'],
                           charts=report_data['charts'],
                           report_content=report_data['report_content'])
    
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

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/about')
def about():
    return render_template('aboutus.html')

@app.before_request
def track_visit():
    if request.endpoint != 'static':  # Don't track requests for static files
        mp_eu.track(session.get('user_id', 'Anonymous'), 'Butt Stuff', {
            'page': request.path,
            'ip': get_client_ip(),
            'user_agent': request.user_agent.string,
            'referrer': request.referrer
        })

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    email = request.json.get('email')
    asset_name = request.json.get('asset_name')
    
    if not email or not asset_name:
        return jsonify({'error': 'Email and asset name are required'}), 400
    
    confirmation_token = str(uuid.uuid4())
    
    temp_sub = TempSubscription(email=email, asset_name=asset_name, confirmation_token=confirmation_token)
    db.session.add(temp_sub)
    db.session.commit()
    
    # Call email confirmation module here
    send_confirmation_email(email, asset_name, confirmation_token)
    
    return jsonify({'message': 'Subscription request received. Please check your email for confirmation.'}), 200

@app.route('/send_comparison_report', methods=['POST'])
def send_comparison_report():
    data = request.json
    email = data.get('email')
    asset1 = data.get('asset1')
    asset2 = data.get('asset2')
    report_content = data.get('report_content')

    if not email or not asset1 or not asset2 or not report_content:
        return jsonify({'message': 'Missing required data'}), 400

    try:
        postmark.emails.send(
            From='roy@borole.com',
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
        print(f"Error sending email: {str(e)}")
        return jsonify({'message': 'Failed to send email'}), 500

def send_confirmation_email(email, asset_name, confirmation_token):
    confirmation_link = url_for('confirm_subscription', token=confirmation_token, _external=True)
    
    postmark.emails.send(
        From='roy@borole.com',
        To=email,
        Subject='Confirm your subscription to 100x weekly reports',
        HtmlBody=f'''Please confirm that you want to subscribe to receive weekly email reports on {asset_name} from 100x.
        
        Click here to confirm: {confirmation_link}
        
        If you did not request this subscription, please ignore this email.'''
    )
from models import Subscription

@app.route('/confirm_subscription/<token>')
def confirm_subscription(token):
    temp_sub = TempSubscription.query.filter_by(confirmation_token=token).first()
    
    if temp_sub is None:
        return render_template('error.html', message='Invalid or expired confirmation link'), 400
    
    new_sub = Subscription(email=temp_sub.email, asset_name=temp_sub.asset_name)
    db.session.add(new_sub)
    db.session.delete(temp_sub)
    db.session.commit()
    
    return redirect(url_for('subscription_success', asset_name=new_sub.asset_name))

@app.route('/subscription_success')
def subscription_success():
    return render_template('subscription_success.html')

def generate_weekly_report(asset_name):
    # Placeholder for report generation logic
    return f"Weekly report for {asset_name}"

def send_weekly_report(email, asset_name, report_content):
    postmark.emails.send(
        From='roy@borole.com',
        To=email,
        Subject=f'100x Weekly Report: {asset_name}',
        HtmlBody=render_template('report_email.html', asset_name=asset_name, report_content=report_content)
    )


@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

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
                From='roy@borole.com',
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


app = Flask(__name__)



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        message = request.form['message']

        # Prepare the email
        recipient = 'roy@borole.com'
        subject = 'Contact Us Form Submission'
        body = f"Name: {name}\nPhone: {phone}\nEmail: {email}\nMessage: {message}"
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = email
        msg['To'] = recipient

        # Send the email
        try:
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login('your-email@example.com', 'your-email-password')
                server.sendmail(email, recipient, msg.as_string())
            return redirect(url_for('contact'))
        except Exception as e:
            print(f"Failed to send email: {e}")

    return render_template('contact.html')

print(app.url_map)
