import os
import json
from anthropic import Anthropic
import pandas as pd
from flask import current_app
from financial_analysis import get_financial_data
import PyPDF2
from docx import Document


def generate_macroeconomic_analysis(ticker):
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

    # Get financial data
    financial_data = get_financial_data(ticker)
    
    if not financial_data:
        return None, f"Unable to fetch financial data for {ticker}"
    
    # Summarize financial data
    summarized_data = {
        'asset_name': financial_data.get('asset_name', ticker),
        'symbol': financial_data.get('symbol', ticker),
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
    
    if 'historical_data' in financial_data and isinstance(financial_data['historical_data'], pd.DataFrame):
        recent_data = financial_data['historical_data'].tail(30).to_dict(orient='records')
        summarized_data['recent_historical_data'] = recent_data

    # Get the macroeconomic analysis file for the ticker
    macro_files = []
    for file in os.listdir('uploads'):
        if file.startswith(f"{ticker.upper()}_") and file.endswith(('.txt', '.pdf', '.doc', '.docx', '.rtf')):
            macro_files.append(os.path.join('uploads', file))
    
    if not macro_files:
        return None, f"No macroeconomic analysis files found for {ticker}."
    
    macro_analysis = ""
    for macro_file in macro_files:
        file_ext = os.path.splitext(macro_file)[1].lower()
        try:
            if file_ext in ['.txt', '.rtf']:
                with open(macro_file, 'r', encoding='utf-8') as file:
                    macro_analysis += file.read() + "\n\n"
            elif file_ext == '.pdf':
                with open(macro_file, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        macro_analysis += page.extract_text() + "\n\n"
            elif file_ext in ['.doc', '.docx']:
                doc = Document(macro_file)
                macro_analysis += "\n".join([para.text for para in doc.paragraphs]) + "\n\n"
        except Exception as e:
            return None, f"Error reading file {macro_file} for {ticker}: {str(e)}"
        
    # Prepare the prompt for the LLM
    prompt = f"""
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

    try:
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
        
        if isinstance(response.content, list):
            analysis = ' '.join([item.text for item in response.content if hasattr(item, 'text')])
        else:
            analysis = response.content

        # Remove the introductory text and add the desired heading
        analysis = analysis.replace("Here is a comprehensive macroeconomic analysis report for", "")
        analysis = analysis.replace("that integrates the provided financial data and macroeconomic analysis:", "")
        analysis = f'<h1>Comprehensive Macroeconomic Analysis for {summarized_data["asset_name"]}</h1>\n' + analysis.strip()

        return analysis, None
    except Exception as e:
        return None, str(e)

def save_macroeconomic_analysis(ticker, content):
    os.makedirs('uploads', exist_ok=True)
    filename = f"{ticker.upper()}_macro_analysis.txt"
    with open(os.path.join('uploads', filename), 'w', encoding='utf-8') as file:
        file.write(content)
        
def get_available_macro_analyses():
    analyses = []
    for filename in os.listdir('uploads'):
        if filename.endswith('_macro_analysis.txt'):
            ticker = filename.split('_')[0]
            analyses.append(ticker)
    return analyses

def get_available_macro_analyses():
    analyses = []
    for filename in os.listdir('uploads'):
        if filename.endswith('_macro_analysis.txt'):
            ticker = filename.split('_')[0]
            analyses.append(ticker)
    return analyses