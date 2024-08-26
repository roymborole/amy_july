import os
import json
from anthropic import Anthropic
import pandas as pd
from flask import current_app
from financial_analysis import get_financial_data
import PyPDF2
import logging
from docx import Document
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_macroeconomic_analysis(ticker):
    try:
        ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
        if not ANTHROPIC_API_KEY:
            logger.error("Anthropic API key not found in environment variables.")
            return None, "API key not configured."

        anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

        financial_data = get_financial_data(ticker)
        if not financial_data:
            logger.error(f"Unable to fetch financial data for {ticker}")
            return None, f"Unable to fetch financial data for {ticker}"

        summarized_data = summarize_financial_data(financial_data)

        macro_files = get_macro_files(ticker)
        if not macro_files:
            logger.warning(f"No macroeconomic analysis files found for {ticker}.")
            return None, f"No macroeconomic analysis files found for {ticker}."

        macro_analysis = process_macro_files(macro_files)

        prompt = generate_prompt(ticker, macro_analysis, summarized_data)

        response = anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            temperature=0,
            system="You are a financial analyst specializing in macroeconomic trends and their impact on individual stocks. Provide your insight in a comprehensive analysis report.",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        analysis = format_response(response, summarized_data)

        return analysis, None
    except Exception as e:
        logger.exception(f"Error in generate_macroeconomic_analysis for {ticker}: {str(e)}")
        return None, str(e)

def summarize_financial_data(financial_data):
    return {
        'asset_name': financial_data.get('asset_name', ''),
        'symbol': financial_data.get('symbol', ''),
        'current_price': financial_data.get('current_price'),
        'change_percent': financial_data.get('change_percent'),
        'market_cap': financial_data.get('market_cap'),
        'pe_ratio': financial_data.get('pe_ratio'),
        'eps': financial_data.get('eps'),
        'dividend_yield': financial_data.get('dividend_yield'),
        'volume': financial_data.get('volume'),
        'average_volume': financial_data.get('average_volume'),
        'high_52_week': financial_data.get('high_52_week'),
        'low_52_week': financial_data.get('low_52_week'),
        'SMA50': financial_data.get('SMA50'),
        'SMA200': financial_data.get('SMA200'),
        'RSI': financial_data.get('RSI'),
        'relative_performance': financial_data.get('relative_performance')
    }

def get_macro_files(ticker):
    return [os.path.join('uploads', f) for f in os.listdir('uploads') 
            if f.startswith(f"{ticker.upper()}_") and f.endswith(('.txt', '.pdf', '.doc', '.docx', '.rtf'))]

def process_macro_files(macro_files):
    macro_analysis = ""
    for macro_file in macro_files:
        file_ext = os.path.splitext(macro_file)[1].lower()
        try:
            if file_ext in ['.txt', '.rtf']:
                with open(macro_file, 'r', encoding='utf-8') as file:
                    macro_analysis += file.read() + "\n\n"
            elif file_ext == '.pdf':
                macro_analysis += process_pdf(macro_file)
            elif file_ext in ['.doc', '.docx']:
                macro_analysis += process_docx(macro_file)
        except Exception as e:
            logger.error(f"Error reading file {macro_file}: {str(e)}")
    return macro_analysis

def process_pdf(file_path):
    content = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            content += page.extract_text() + "\n\n"
    return content

def process_docx(file_path):
    content = ""
    doc = Document(file_path)
    for para in doc.paragraphs:
        content += para.text + "\n"
    return content

def generate_prompt(ticker, macro_analysis, summarized_data):
    return f"""
    Given the technical analysis document and the quarterly results summary for {ticker}, please generate a comprehensive macroeconomic analysis that incorporates the following elements:

    Macroeconomic Analysis:
    {macro_analysis}

    Summarized Financial Data:
    {json.dumps(summarized_data, indent=2)}

    Provide a comprehensive report that combines insights from both the macroeconomic analysis and the financial data. 
    Format your response in HTML with the following structure:

    <div style="color: black;">
        <h2>1. Executive Summary</h2>
        [Provide a concise overview of key findings and highlight significant macroeconomic implications]

        <h2>2. Integration of Technical and Fundamental Analysis</h2>
        [Analyze alignment or divergence of technical indicators and fundamental data, discuss discrepancies]

        <h2>3. Macroeconomic Context</h2>
        [Place findings in broader economic landscape, discuss relevant economic indicators]

        <h2>4. Industry-Specific Trends</h2>
        [Identify and analyze industry trends, compare to overall macroeconomic conditions]

        <h2>5. Global Economic Factors</h2>
        [Examine global economic events, geopolitical factors, trade relations, and market dynamics]

        <h2>6. Forward-Looking Analysis</h2>
        [Provide projections for future economic conditions and discuss potential scenarios]

        <h2>7. Risk Assessment</h2>
        [Identify and assess key economic risks]

        <h2>8. Policy Implications</h2>
        [Discuss impact of current or potential economic policies]

        <h2>9. Comparative Analysis</h2>
        [Compare findings to historical data, highlight unique aspects of current situation]

        <h2>10. Actionable Insights</h2>
        [Provide specific, data-driven recommendations and suggest areas for further research]

    </div>

    Ensure that all text is in black color and subheadings use h2 tags for bold formatting. The analysis should be comprehensive, insightful, and provide a unique perspective that goes beyond a simple combination of the input documents. The goal is to deliver actionable intelligence that gives analysts a competitive edge in understanding the macroeconomic landscape.
    """

def format_response(response, summarized_data):
    if isinstance(response.content, list):
        analysis = ' '.join([item.text for item in response.content if hasattr(item, 'text')])
    else:
        analysis = response.content

    analysis = analysis.replace("Here is a comprehensive macroeconomic analysis report for", "")
    analysis = analysis.replace("that integrates the provided financial data and macroeconomic analysis:", "")
    analysis = f'<h1>Comprehensive Macroeconomic Analysis for {summarized_data["asset_name"]}</h1>\n' + analysis.strip()
    
    return analysis

def save_macroeconomic_analysis(ticker, content):
    try:
        os.makedirs('uploads', exist_ok=True)
        filename = f"{ticker.upper()}_macro_analysis.txt"
        with open(os.path.join('uploads', filename), 'w', encoding='utf-8') as file:
            file.write(content)
        logger.info(f"Macroeconomic analysis saved for {ticker}")
    except Exception as e:
        logger.exception(f"Error saving macroeconomic analysis for {ticker}: {str(e)}")

def get_available_macro_analyses():
    try:
        return [filename.split('_')[0] for filename in os.listdir('uploads') if filename.endswith('_macro_analysis.txt')]
    except Exception as e:
        logger.exception(f"Error getting available macro analyses: {str(e)}")
        return []
