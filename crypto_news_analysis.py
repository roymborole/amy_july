# crypto_news_analysis.py

from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from config import anthropic_client, CRYPTOCOMPARE_API_KEY

def get_recent_crypto_news(crypto_symbol, days=7):
    url = f"https://min-api.cryptocompare.com/data/v2/news/?categories={crypto_symbol}&api_key={CRYPTOCOMPARE_API_KEY}"
    response = requests.get(url)
    news_data = response.json()

    if news_data['Response'] == 'Error':
        print(f"Error fetching news for {crypto_symbol}: {news_data['Message']}")
        return []

    seven_days_ago = datetime.now() - timedelta(days=days)
    
    recent_news = [
        item for item in news_data['Data']
        if datetime.fromtimestamp(item['published_on']) > seven_days_ago
    ]
    
    return recent_news

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

def get_crypto_news_summary(crypto_symbol):
    news_items = get_recent_crypto_news(crypto_symbol)
    all_content = ""
    
    for item in news_items:
        content = item['body']  # CryptoCompare API provides the content directly
        if content:
            all_content += content + "\n\n"
    
    prompt = f"""Human: Summarize the following news articles about {crypto_symbol}. Focus on the most important points and data points and their potential impact on the cryptocurrency. Provide a fluid and exciting newsletter, the text should not exceed 800 words and be less than 500 words, conclude the text the way you would conclude a newsletter.

    {all_content}

A: Here's a summary of the recent news articles about {crypto_symbol}:

"""
    
    response = anthropic_client.completions.create(
        model="claude-3-5-sonnet-20240620",
        prompt=prompt,
        max_tokens=2000,
        stop_sequences=["\n\nHuman:"]
    )
    
    return response.completion

# Additional function to get detailed news data
def get_detailed_crypto_news(crypto_symbol, days=7):
    news_items = get_recent_crypto_news(crypto_symbol, days)
    detailed_news = []

    for item in news_items:
        detailed_news.append({
            'title': item['title'],
            'url': item['url'],
            'body': item['body'],
            'source': item['source'],
            'published_on': datetime.fromtimestamp(item['published_on']).strftime('%Y-%m-%d %H:%M:%S')
        })

    return detailed_news