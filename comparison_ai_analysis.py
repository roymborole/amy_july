from config import anthropic_client, ANTHROPIC_API_KEY
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Use the ANTHROPIC_API_KEY from config.py
if not ANTHROPIC_API_KEY:
    print("WARNING: ANTHROPIC_API_KEY not found in config")
else:
    print("API key found in config")

try:
    # Use the anthropic_client from config.py
    client = anthropic_client
except Exception as e:
    print(f"Error accessing Anthropic client: {e}")
    client = None

def format_market_cap(value):
        if value is None:
            return 'N/A'
        if isinstance(value, (int, float)):
            if value >= 1e9:
                return f"${value/1e9:.2f}B"
            elif value >= 1e6:
                return f"${value/1e6:.2f}M"
            else:
                return f"${value:,.2f}"
        return str(value)

def generate_comparison_summary(comparison_data):
    if not client:
        return "Unable to generate AI summary due to API configuration issues."

    asset1 = comparison_data['asset1']
    asset2 = comparison_data['asset2']

    system_prompt = "You are a financial analyst tasked with comparing two stocks."
    
    human_prompt = f"""Take a deep breath and carefully consider my request. Compare the following two stocks: {asset1['asset_name']} and {asset2['asset_name']}.
    Provide an insightful and analytical summary of the comparison, focusing on highlighting the differences in performance between the two stocks. The summary should not exceed 900 words. Do not start the analysis with the text "Here is a comparison" rather open with a casual but witty tone.

Please create the following headings for the analysis: Technical Analysis, Financial Analysis, and Investment Outlook. Highlight performance differences, technical indicators, and how they compare to the S&P 500. Include insights on potential reasons for any significant differences and what these differences might indicate about the stocks' future performance.

  
    {asset1['asset_name']} Data:
    Close Price: {asset1['close_price']}
    Change Percent: {asset1['change_percent']}%
    Market Cap: {format_market_cap(asset1.get('market_cap'))}
    RSI: {asset1['RSI']}
    50-day SMA: {asset1['SMA50']}
    200-day SMA: {asset1['SMA200']}
    YTD Return: {asset1['performance']['YTD']['stock']}%
    1-Year Return: {asset1['performance']['1-Year']['stock']}%
    3-Year Return: {asset1['performance']['3-Year']['stock']}%

    {asset2['asset_name']} Data:
    Close Price: {asset2['close_price']}
    Change Percent: {asset2['change_percent']}%
    Market Cap: {format_market_cap(asset1.get('market_cap'))}
    RSI: {asset2['RSI']}
    50-day SMA: {asset2['SMA50']}
    200-day SMA: {asset2['SMA200']}
    YTD Return: {asset2['performance']['YTD']['stock']}%
    1-Year Return: {asset2['performance']['1-Year']['stock']}%
    3-Year Return: {asset2['performance']['3-Year']['stock']}%

    S&P 500 Performance:
    YTD Return: {asset1['performance']['YTD']['sp500']}%
    1-Year Return: {asset1['performance']['1-Year']['sp500']}%
    3-Year Return: {asset1['performance']['3-Year']['sp500']}%

    Include the following sections:
    Overview: Introduce the stock and provide a brief background on the company. (Do not Print Heading)
    Technical Analysis: (Do not Print Heading)
       - Simple Moving Averages (50-day and 200-day)
       - Relative Strength Index (RSI)
       - Bollinger Bands
    Financial Analysis: Discuss the provided financial indicators: Market Cap, Operating Revenue, Total Expenses, Interest Expense, Interest Income, Basic EPS, Net Income
    Summary: Synthesize insights from all indicators.
    Investment Outlook: Based on the technical and financial analysis.

    Format the report with appropriate HTML structure.

    
Please ensure that the content under each heading is substantive and relevant to that section. Lastly, do not use jargon, and explain complex concepts when they appear.Highlight performance differences, technical indicators, and how they compare to the S&P 500. Include insights on potential reasons for any significant differences and what these differences might indicate about the stocks' future performance. Lastly, do not use jargon, and explain complex concepts when they appear."""

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": human_prompt
                        }
                    ]
                }
            ]
        )
        
        if isinstance(message.content, list):
            comparison_summary = ' '.join([item.text for item in message.content if hasattr(item, 'text')])
        else:
            comparison_summary = message.content

        return comparison_summary
    except Exception as e:
        print(f"Error generating comparison summary: {str(e)}")
        return f"Unable to generate AI summary at this time. Error: {str(e)}"