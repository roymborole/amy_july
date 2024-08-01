# news_analysis.py

import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from config import anthropic_client

def get_recent_stock_news_urls(ticker_symbol, days=7):
    ticker = yf.Ticker(ticker_symbol)
    news = ticker.news
    seven_days_ago = datetime.now() - timedelta(days=days)
    
    recent_news_urls = [
        item['link'] for item in news
        if datetime.fromtimestamp(item['providerPublishTime']) > seven_days_ago
    ]
    
    return recent_news_urls

def scrape_article_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        article_content = ""
        paragraphs = soup.find_all('p')
        for paragraph in paragraphs:
            article_content += paragraph.get_text() + "\n"

        return article_content.strip()

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def get_news_summary(ticker):
    news_urls = get_recent_stock_news_urls(ticker)
    all_content = ""
    
    for url in news_urls:
        content = scrape_article_content(url)
        if content:
            all_content += content + "\n\n"
    
    prompt = f"""Summarize the following news articles about {ticker}. Focus on the most important points and data points and their potential impact on the stock. Do not list the points, but rather let them flow in the style of an essay. Write in a fluid and well thought out manner. The text should not exceed 1000 words and be less than 500 words, conclude the text in a casual way. After your conclusion do not add any more text. DO NOT ASK if I have any need for any clarification or have additional questions. Do not add anything after your conclusion.

    {all_content}

    """
    
    try:
        message = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0,
            system="You are a journalist writing insightful business news. Provide a well thought out balanced  summary of recent news articles about a given company.",
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
            news_summary = ' '.join([item.text for item in message.content if hasattr(item, 'text')])
        else:
            news_summary = message.content

        return news_summary

    except Exception as e:
        return f"Error generating news summary: {str(e)}"