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

def generate_comparison_summary(comparison_data):
    if not client:
        return "Unable to generate AI summary due to API configuration issues."

    asset1 = comparison_data['asset1']
    asset2 = comparison_data['asset2']

    system_prompt = "You are a financial analyst tasked with comparing two stocks."
    
    human_prompt = f"""Compare the following two stocks: {asset1['asset_name']} and {asset2['asset_name']}.
    Provide an insightful and analytical summary of the comparison, focusing on highlighting the differences in performance between the two stocks. The summary should not exceed 700 words, START THE REPORT AS FINANCIAL ANALYST WOULD, DO NOT START WITH THE WORDS "Here is a X-WORD comparison.

    {asset1['asset_name']} Data:
    Close Price: {asset1['close_price']}
    Change Percent: {asset1['change_percent']}%
    RSI: {asset1['RSI']}
    50-day SMA: {asset1['SMA50']}
    200-day SMA: {asset1['SMA200']}
    YTD Return: {asset1['performance']['YTD']['stock']}%
    1-Year Return: {asset1['performance']['1-Year']['stock']}%
    3-Year Return: {asset1['performance']['3-Year']['stock']}%

    {asset2['asset_name']} Data:
    Close Price: {asset2['close_price']}
    Change Percent: {asset2['change_percent']}%
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

    Highlight performance differences, technical indicators, and how they compare to the S&P 500. Include insights on potential reasons for any significant differences and what these differences might indicate about the stocks' future performance."""

    try:
        response = client.completions.create(
            model="claude-2",
            prompt=f"{system_prompt}\n\nHuman: {human_prompt}\n\nAssistant:",
            max_tokens_to_sample=800,
            temperature=0.7
        )
        return response.completion
    except Exception as e:
        print(f"Error generating comparison summary: {str(e)}")
        return f"Unable to generate AI summary at this time. Error: {str(e)}"