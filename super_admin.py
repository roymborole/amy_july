from flask import Blueprint, request, session, redirect, url_for, flash, render_template, jsonify
from functools import wraps
from werkzeug.utils import secure_filename
import os
from anthropic import Anthropic
from flask import Blueprint, request, session, redirect, url_for, flash, render_template, jsonify, current_app
from functools import wraps
from werkzeug.utils import secure_filename
import os
from macroeconomic_analysis import generate_macroeconomic_analysis, save_analysis_to_database, get_saved_analysis

# Initialize Blueprint
super_admin_bp = Blueprint('super_admin', __name__, url_prefix='/super-admin')


SUPER_ADMIN_USERNAME = os.getenv('SUPER_ADMIN_USERNAME')
SUPER_ADMIN_PASSWORD = os.getenv('SUPER_ADMIN_PASSWORD')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

# Middleware
def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_super_admin'):
            flash('Super admin access required.', 'error')
            return redirect(url_for('super_admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@super_admin_bp.route('/login')('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == SUPER_ADMIN_USERNAME and password == SUPER_ADMIN_PASSWORD:
            session['is_super_admin'] = True
            return redirect(url_for('super_admin.dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('super_admin/login.html')

@super_admin_bp.route('/dashboard')
@super_admin_required
def dashboard():
    analyses = get_all_analyses()  # Implement this function
    return render_template('super_admin/dashboard.html', analyses=analyses)

@super_admin_bp.route('/upload', methods=['GET', 'POST'])
@super_admin_required
def upload_analysis():
    if request.method == 'POST':
        file = request.files['file']
        stock_ticker = request.form['stock_ticker']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            text = convert_word_to_text(file_path)
            analysis_id = save_to_database(stock_ticker, text)
            
            flash('Analysis uploaded successfully', 'success')
            return redirect(url_for('super_admin.dashboard'))
        
        flash('Invalid file', 'error')
    
    return render_template('super_admin/upload.html')

@super_admin_bp.route('/api/macroeconomic-analysis', methods=['POST'])
@super_admin_required
def generate_macroeconomic_analysis():
    data = request.json
    macro_text = get_macro_analysis(data['analysis_id'])
    technical_analysis = generate_technical_analysis(data['ticker'])
    
    prompt = f"""
    Analyze the following macroeconomic analysis and technical analysis for {data['ticker']}:

    Macroeconomic Analysis:
    {macro_text}

    Technical Analysis:
    {technical_analysis}

    Provide a comprehensive macroeconomic analysis that incorporates insights from both the uploaded macroeconomic document and the technical analysis.
    """
    
    response = anthropic.completions.create(
        model="claude-2",
        prompt=prompt,
        max_tokens_to_sample=2000,
    )
    
    return jsonify({'analysis': response.completion})

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'doc', 'docx'}

def convert_word_to_text(file_path):
    # Implement Word to text conversion here
    pass

def save_to_database(stock_ticker, text):
    # Implement database saving logic here
    pass

def get_all_analyses():
    # Implement fetching all analyses from the database
    pass

def get_macro_analysis(analysis_id):
    # Implement fetching specific analysis from the database
    pass

def generate_technical_analysis(ticker):
    # Implement technical analysis generation here
    pass




# ... (keep the existing imports and setup) ...

@super_admin_bp.route('/api/macroeconomic-analysis', methods=['POST'])
@super_admin_required
def api_macroeconomic_analysis():
    data = request.json
    ticker = data['ticker']
    analysis_id = data['analysis_id']
    
    # Check if we have a recent saved analysis
    saved_analysis = get_saved_analysis(ticker)
    if saved_analysis:
        return jsonify({'analysis': saved_analysis})
    
    # Generate new analysis
    analysis = generate_macroeconomic_analysis(analysis_id, ticker)
    
    # Save the new analysis
    save_analysis_to_database(ticker, analysis)
    
    return jsonify({'analysis': analysis})
