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

# news_analysis.py

def get_news_summary(ticker):
    news_urls = get_recent_stock_news_urls(ticker)
    all_content = ""
    
    for url in news_urls:
        content = scrape_article_content(url)
        if content:
            all_content += content + "\n\n"
    
    prompt = f"""Human: Summarize the following news articles about {ticker}. Focus on the most important points and data points and their potential impact on the stock. Provide a fluid and excitine newsletter, the text should not exceed 800 words and be less than 500 words, conclude the text the way you would conclude a newsletter.

    {all_content}

Assistant: Here's a summary of the recent news articles about {ticker}:

"""
    
    response = anthropic_client.completions.create(
        model="claude-2",
        prompt=prompt,
        max_tokens_to_sample=2000,
        stop_sequences=["\n\nHuman:"]
    )
    
    return response.completion