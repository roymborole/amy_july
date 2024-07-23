#backup app.py

from flask import Flask, request, render_template
import os
import yfinance as yf
import pandas as pd
import requests
from anthropic import Anthropic
import os
import anthropic
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend, which doesn't require a GUI
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from pyngrok import ngrok
import re
import json




# Set up Anthropic client
ANTHROPIC_API_KEY = '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'
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)


# Initialize Flask app
app = Flask(__name__, static_folder='static')



def get_financial_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        df = yf.download(ticker, start='2020-01-01', end='2024-07-01')

        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()

        def compute_rsi(data, window=14):
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))

        df['RSI'] = compute_rsi(df)

        def compute_bollinger_bands(data, window=20, num_std=2):
            rolling_mean = data['Close'].rolling(window=window).mean()
            rolling_std = data['Close'].rolling(window=window).std()
            upper_band = rolling_mean + (rolling_std * num_std)
            lower_band = rolling_mean - (rolling_std * num_std)
            return rolling_mean, upper_band, lower_band

        df['SMA20'], df['UpperBand'], df['LowerBand'] = compute_bollinger_bands(df)

        financials = stock.financials.iloc[:, 0]  # Get the most recent year

        raw_data = {
            'company_name': info.get('longName', ticker),
            'close_price': df['Close'].iloc[-1],
            'change_percent': ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
            'date': df.index[-1].strftime('%Y-%m-%d'),
            'SMA50': df['SMA50'].iloc[-1],
            'SMA200': df['SMA200'].iloc[-1],
            'RSI': df['RSI'].iloc[-1],
            'UpperBand': df['UpperBand'].iloc[-1],
            'LowerBand': df['LowerBand'].iloc[-1],
            'SMA20': df['SMA20'].iloc[-1],
            'Diluted EPS': info.get('trailingEps'),
            'Total Revenue': financials.get('Total Revenue'),
            'Operating Revenue': financials.get('Operating Revenue'),
            'Basic EPS': info.get('trailingEps'),  # Using trailingEps as a proxy for Basic EPS
            'Total Expenses': financials.get('Total Expenses'),
            'Net Interest Income': financials.get('Net Interest Income'),
            'Interest Expense': financials.get('Interest Expense'),
            'Interest Income': financials.get('Interest Income'),
            'Net Income': financials.get('Net Income'),
            'Normalized Income': financials.get('Normalized Income'),
            
        }

        # Create charts
        charts = {
            'price_sma': create_chart(df, 'price_sma', ticker),
            'rsi': create_chart(df, 'rsi', ticker),
            'bollinger': create_chart(df, 'bollinger', ticker)
        }
        raw_data['charts'] = charts

        return raw_data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None
    # Function to generate analysis report using Anthropic

def create_chart(df, chart_type):
    plt.figure(figsize=(14, 7))
    
    if chart_type == 'price_sma':
        plt.plot(df.index, df['Close'], label='Close Price')
        plt.plot(df.index, df['SMA50'], label='50-day SMA')
        plt.plot(df.index, df['SMA200'], label='200-day SMA')
        plt.title(f'{df.columns.name} Stock Price and Moving Averages')
    elif chart_type == 'rsi':
        plt.plot(df.index, df['RSI'], label='RSI', color='purple')
        plt.axhline(70, color='r', linestyle='--')
        plt.axhline(30, color='r', linestyle='--')
        plt.title('Relative Strength Index (RSI)')
    elif chart_type == 'bollinger':
        plt.plot(df.index, df['Close'], label='Close Price')
        plt.plot(df.index, df['SMA20'], label='20-day SMA')
        plt.plot(df.index, df['UpperBand'], label='Upper Bollinger Band', linestyle='--')
        plt.plot(df.index, df['LowerBand'], label='Lower Bollinger Band', linestyle='--')
        plt.title('Bollinger Bands')
    
    plt.legend()
    plt.tight_layout()
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()  # Close the figure to free up memory
    return base64.b64encode(img.getvalue()).decode()

def get_analysis_report(raw_data, company_name):
    # Ensure company_name is available, fallback to ticker if not
    company = company_name or raw_data.get('company_name') or raw_data.get('ticker', 'Unknown Company')
    
 # Prepare a summarized version of the raw_data
    summarized_data = {
        'close_price': raw_data.get('close_price'),
        'SMA50': raw_data.get('SMA50'),
        'SMA200': raw_data.get('SMA200'),
        'RSI': raw_data.get('RSI'),
        'UpperBand': raw_data.get('UpperBand'),
        'LowerBand': raw_data.get('LowerBand'),
        'date': raw_data.get('date'),
        # Adding the new financial indicators
        'Diluted EPS': raw_data.get('Diluted EPS'),
        'Total Revenue': raw_data.get('Total Revenue'),
        'Operating Revenue': raw_data.get('Operating Revenue'),
        'Basic EPS': raw_data.get('Basic EPS'),
        'Total Expenses': raw_data.get('Total Expenses'),
        'Net Interest Income': raw_data.get('Net Interest Income'),
        'Interest Expense': raw_data.get('Interest Expense'),
        'Interest Income': raw_data.get('Interest Income'),
        'Net Income': raw_data.get('Net Income'),
        'Normalized Income': raw_data.get('Normalized Income')
    }
    
    prompt = f"""
    Create a comprehensive technical analysis report for {company} based on the following summarized data:
    {json.dumps(summarized_data, indent=2)}
    
    Include the following sections:
    1. An overview section introducing the stock with a brief background on the company and the date of analysis.
    2. A detailed analysis of key technical indicators including:
       - Simple Moving Averages (50-day and 200-day)
       - Relative Strength Index (RSI)
       - Bollinger Bands
    3. A summary section that synthesizes the insights from all indicators
    4. an indepth discussion on the following indicators: Total Revenue, Operating Revenue, Basic EPS, Total Expenses, Net Interest Income, Interest Expense, Interest Income, Net Income, Normalized Income
    4. An investment outlook based on the comprehensive analysis
    5. A brief disclaimer

    Include the following chart placeholders in your report:
    [PRICE_SMA_CHART]
    [RSI_CHART]
    [BOLLINGER_CHART]

    Format the report with appropriate HTML structure.
    Do not give the report a heading.
    Maintain a professional yet engaging tone throughout, balancing analytical insights with accessibility for a general investor audience. Start the report at Overview do not include the words "Here's a comprehensive technical analysis report for The Boeing Company based on the provided data"
    """

    try:
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=3000,
            temperature=0,
            system="You are a world-class financial analyst. Provide a technical analysis report.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        # Check if content is a list and join it if so
        if isinstance(message.content, list):
            report = ' '.join([item.text for item in message.content if hasattr(item, 'text')])
        else:
            report = message.content

        # Replace chart placeholders
        for chart_type, chart_data in raw_data.get('charts', {}).items():
            placeholder = f'[{chart_type.upper()}_CHART]'
            chart_html = f'<img src="data:image/png;base64,{chart_data}" alt="{chart_type} chart" style="max-width: 100%; height: auto;">'
            report = report.replace(placeholder, chart_html)

        return report
    except Exception as e:
        return f"<div class='error'>Error generating report: {str(e)}</div>"    

def create_chart(df, chart_type, ticker):
    plt.figure(figsize=(10, 6))
    
    if chart_type == 'price_sma':
        plt.plot(df.index, df['Close'], label='Close Price')
        plt.plot(df.index, df['SMA50'], label='50-day SMA')
        plt.plot(df.index, df['SMA200'], label='200-day SMA')
        plt.title(f'{ticker} Stock Price and Moving Averages')
    elif chart_type == 'rsi':
        plt.plot(df.index, df['RSI'], label='RSI', color='purple')
        plt.axhline(70, color='r', linestyle='--')
        plt.axhline(30, color='r', linestyle='--')
        plt.title(f'{ticker} Relative Strength Index (RSI)')
    elif chart_type == 'bollinger':
        plt.plot(df.index, df['Close'], label='Close Price')
        plt.plot(df.index, df['SMA20'], label='20-day SMA')
        plt.plot(df.index, df['UpperBand'], label='Upper Bollinger Band', linestyle='--')
        plt.plot(df.index, df['LowerBand'], label='Lower Bollinger Band', linestyle='--')
        plt.title(f'{ticker} Bollinger Bands')
    
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Price' if chart_type != 'rsi' else 'RSI')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

def generate_rsi_chart(data, filename):
    
    pass

def generate_bollinger_chart(data, filename):
    
    pass

def get_analysis_report(raw_data, company_name):
    try:
        # Prepare summarized data
        summarized_data = {
            'close_price': raw_data.get('close_price'),
            'SMA50': raw_data.get('SMA50'),
            'SMA200': raw_data.get('SMA200'),
            'RSI': raw_data.get('RSI'),
            'UpperBand': raw_data.get('UpperBand'),
            'LowerBand': raw_data.get('LowerBand'),
            'MiddleBand': raw_data.get('MiddleBand'),
            'date': raw_data.get('date'),
            'Diluted EPS': raw_data.get('Diluted EPS'),
            'Total Revenue': raw_data.get('Total Revenue'),
            'Operating Revenue': raw_data.get('Operating Revenue'),
            'Basic EPS': raw_data.get('Basic EPS'),
            'Total Expenses': raw_data.get('Total Expenses'),
            'Net Interest Income': raw_data.get('Net Interest Income'),
            'Interest Expense': raw_data.get('Interest Expense'),
            'Interest Income': raw_data.get('Interest Income'),
            'Net Income': raw_data.get('Net Income'),
            'Normalized Income': raw_data.get('Normalized Income')
        }

        # Generate report content using Anthropic API
        prompt = f"""
        Create a comprehensive technical analysis report for {company_name} based on the following summarized data:
        {json.dumps(summarized_data, indent=2)}

        Include the following sections:
        1. An overview section introducing the stock with a brief background on the company and the date of analysis.
        2. A detailed analysis of key technical indicators including:
           - Simple Moving Averages (50-day and 200-day)
           - Relative Strength Index (RSI)
           - Bollinger Bands
        3. An in-depth discussion on the following financial indicators:
            Total Revenue, Operating Revenue, Basic EPS, Total Expenses, Net Interest Income,
            Interest Expense, Interest Income, Net Income, Normalized Income
        4. A summary section that synthesizes the insights from all indicators
        5. An investment outlook based on the comprehensive analysis
        6. A brief disclaimer

        Format the report with appropriate HTML structure.
        Maintain a professional yet engaging tone throughout, balancing analytical insights with accessibility for a general investor audience.
        """

        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=3000,
            temperature=0,
            system="You are a world-class financial analyst. Provide a technical analysis report.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        if isinstance(message.content, list):
            report_content = ' '.join([item.text for item in message.content if hasattr(item, 'text')])
        else:
            report_content = message.content

        report_content += "\n\n[PRICE_SMA_CHART]\n\n[RSI_CHART]\n\n[BOLLINGER_CHART]"
        # Prepare HTML for tables
        technical_table = f"""
        <table>
            <tr>
                <th>Date</th>
                <th>Closing Price</th>
                <th>RSI</th>
                <th>50-day SMA</th>
                <th>200-day SMA</th>
            </tr>
            <tr>
                <td>{summarized_data['date']}</td>
                <td>{summarized_data['close_price']}</td>
                <td>{summarized_data['RSI']}</td>
                <td>{summarized_data['SMA50']}</td>
                <td>{summarized_data['SMA200']}</td>
            </tr>
        </table>
        """

        bollinger_table = f"""
        <table>
            <tr>
                <th>Upper Band</th>
                <th>Middle Band</th>
                <th>Lower Band</th>
            </tr>
            <tr>
                <td>{summarized_data['UpperBand']}</td>
                <td>{summarized_data['MiddleBand']}</td>
                <td>{summarized_data['LowerBand']}</td>
            </tr>
        </table>
        """

        financial_table = f"""
        <table>
            <tr><th>Indicator</th><th>Value</th></tr>
            <tr><td>Total Revenue</td><td>{summarized_data['Total Revenue']}</td></tr>
            <tr><td>Operating Revenue</td><td>{summarized_data['Operating Revenue']}</td></tr>
            <tr><td>Basic EPS</td><td>{summarized_data['Basic EPS']}</td></tr>
            <tr><td>Total Expenses</td><td>{summarized_data['Total Expenses']}</td></tr>
            <tr><td>Net Interest Income</td><td>{summarized_data['Net Interest Income']}</td></tr>
            <tr><td>Interest Expense</td><td>{summarized_data['Interest Expense']}</td></tr>
            <tr><td>Interest Income</td><td>{summarized_data['Interest Income']}</td></tr>
            <tr><td>Net Income</td><td>{summarized_data['Net Income']}</td></tr>
            <tr><td>Normalized Income</td><td>{summarized_data['Normalized Income']}</td></tr>
        </table>
        """

        # Wrap the report content in proper HTML structure
        html_report = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{company_name} Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f0f0f0; }}
                .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                h1, h2 {{ color: #333; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="container">
        <img src="https://i.ibb.co/85y8KJc" alt="Header 1" style="width: 100%; height: auto;">
        
                
                <h1>Technical Analysis for {company_name}</h1>
                
                {technical_table}
                
                <br>
                
                {bollinger_table}
            
                
                <h2>Financial Indicators</h2>
                
                {financial_table}
                
                <img src="https://i.ibb.co/BsCXLfB" alt="Header 2" style="width: 100%; height: auto;">
        
                <div id="analysis">
                    {report_content}
                </div>
            </div>
        </body>
        </html>
        """

        # Generate and save RSI and Bollinger charts
        rsi_chart_path = f"images/{company_name}_rsi_chart.png"
        bollinger_chart_path = f"images/{company_name}_bollinger_chart.png"

        generate_rsi_chart(raw_data, f"static/{rsi_chart_path}")
        generate_bollinger_chart(raw_data, f"static/{bollinger_chart_path}")

        # Replace placeholders with actual chart images
        html_report = html_report.replace('[RSI_CHART]', f'<img src="{{ url_for("static", filename="{rsi_chart_path}") }}" alt="RSI Chart" style="width: 100%; height: auto;">')
        html_report = html_report.replace('[BOLLINGER_CHART]', f'<img src="{{ url_for("static", filename="{bollinger_chart_path}") }}" alt="Bollinger Bands Chart" style="width: 100%; height: auto;">')

        return html_report

    except Exception as e:
        # Handle any exceptions that occur during report generation
        error_message = f"An error occurred while generating the report: {str(e)}"
        return f"<div class='error'>{error_message}</div>"

    return report_content 

from flask import jsonify

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("POST request received")
        stock_ticker = request.form.get('stock_ticker')
        print(f"Stock ticker: {stock_ticker}")
        if not stock_ticker:
            print("Missing stock_ticker")
            return "Missing stock ticker", 400
        return render_template('loading.html', stock_ticker=stock_ticker)
    
    # Define list of FAANG stocks and top crypto tokens
    symbols = ['META', 'AAPL', 'AMZN', 'NFLX', 'GOOGL', 'BTC-USD', 'ETH-USD', 'USDT-USD', 'BNB-USD', 'ADA-USD']

    stocks = []
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            stocks.append({
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'logo': f"{symbol.lower().replace('-usd', '')}-logo.png",
                'change': info.get('regularMarketChangePercent', 0) * 100
            })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    return render_template('index.html', stocks=stocks)

@app.route('/generate_report', methods=['POST'])
def generate_report():
    print("Generate report route accessed")
    stock_ticker = request.form.get('stock_ticker')
    print(f"Received stock ticker: {stock_ticker}")
    if not stock_ticker:
        print("Missing stock ticker in generate_report")
        return jsonify({'error': 'Missing stock ticker'}), 400
    try:
        print(f"Fetching financial data for {stock_ticker}")
        raw_data = get_financial_data(stock_ticker)
        print("Generating analysis report")
        report_html = get_analysis_report(raw_data, stock_ticker)
        print("Report generated successfully")
        return jsonify({'report': report_html})
    except Exception as e:
        print(f"Error in generate_report: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        stock_ticker = request.form['stock_ticker']
    else:
        stock_ticker = request.args.get('stock_ticker')
    
    if not stock_ticker:
        return redirect(url_for('index'))

    raw_data = get_financial_data(stock_ticker)
    if not raw_data:
        return render_template('error.html', message="Unable to fetch data for the given stock/crypto symbol.")

    report_content = get_analysis_report(raw_data, raw_data['company_name'])
    
    # Replace placeholders with actual chart images
    for chart_type, chart_data in raw_data['charts'].items():
        placeholder = f'[{chart_type.upper()}_CHART]'
        chart_html = f'<img src="data:image/png;base64,{chart_data}" alt="{chart_type} chart" style="max-width: 100%; height: auto;">'
        report_content = report_content.replace(placeholder, chart_html)

    return render_template('report.html', 
                           report_content=report_content, 
                           company_name=raw_data['company_name'],
                           raw_data=raw_data)
if __name__ == '__main__':
    # Check if running in debug mode
    if app.debug:
        # Get the ngrok auth token from environment variable
        ngrok_auth_token = os.environ.get("NGROK_AUTH_TOKEN")
        if ngrok_auth_token:
            ngrok.set_auth_token(ngrok_auth_token)
        else:
            print("NGROK_AUTH_TOKEN not found. Please set it as an environment variable.")
            exit(1)

        # Start ngrok
        try:
            public_url = ngrok.connect(4040)
            print(f' * ngrok tunnel "{public_url}" -> "http://127.0.0.1:4040"')
        except Exception as e:
            print(f"An error occurred while connecting to ngrok: {str(e)}")
            exit(1)

    # Run the Flask app
    app.run(host='127.0.0.1', port=4040)