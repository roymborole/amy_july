# crypto_analysis.py
import requests
import pandas as pd
from config import CRYPTOCOMPARE_API_KEY
from datetime import datetime
import numpy as np
import time


def get_crypto_list(max_retries=3, delay=5):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "sparkline": False
    }
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            crypto_data = response.json()
            return {coin['symbol'].upper(): coin['id'] for coin in crypto_data}
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to fetch cryptocurrency list after all attempts")
                return {}

# Fetch the crypto list
fetched_crypto_mapping = get_crypto_list()

# Combine with our manual mapping for common alternative names
manual_mapping = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'Ethereum (Cryptocurrency)': 'ETH',
    'litecoin': 'LTC',
    'ripple': 'XRP',
    'dogecoin': 'DOGE',
    'cardano': 'ADA',
    'polkadot': 'DOT',
    'chainlink': 'LINK',
    'stellar': 'XLM',
    'monero': 'XMR',
    'tether': 'USDT',
    'binance coin': 'BNB',
    'usd coin': 'USDC',
    'solana': 'SOL',
    'avalanche': 'AVAX',
    'polygon': 'MATIC',
    'uniswap': 'UNI',
    'cosmos': 'ATOM',
    'algorand': 'ALGO',
    'filecoin': 'FIL',
}

# Combine both mappings
crypto_mapping = {**manual_mapping, **fetched_crypto_mapping}

def get_crypto_data(crypto_name):
    symbol = crypto_mapping.get(crypto_name.lower(), crypto_name.upper())
    
    url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={symbol}&tsym=USD&limit=365&api_key={CRYPTOCOMPARE_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data['Response'] == 'Error':
            print(f"API returned an error: {data.get('Message', 'Unknown error')}")
            return None

        # Rest of your function...

    except requests.RequestException as e:
        print(f"Error fetching data for {crypto_name}: {str(e)}")
        return None

    prices = data['Data']['Data']
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(prices)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    df.rename(columns={'close': 'Close', 'open': 'Open', 'high': 'High', 'low': 'Low', 'volumefrom': 'Volume'}, inplace=True)

    # Calculate indicators
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    df['SMA20'] = df['Close'].rolling(window=20).mean()

    # Calculate RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Calculate Bollinger Bands
    df['MiddleBand'] = df['Close'].rolling(window=20).mean()
    df['UpperBand'] = df['MiddleBand'] + (df['Close'].rolling(window=20).std() * 2)
    df['LowerBand'] = df['MiddleBand'] - (df['Close'].rolling(window=20).std() * 2)

    # Calculate additional indicators
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()

    # MACD
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # OBV
    df['OBV'] = (df['Close'].diff() > 0).astype(int) * df['Volume']
    df['OBV'] = df['OBV'].cumsum()

    # VWAP
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()

    # ATR
    df['TR'] = pd.concat([df['High'] - df['Low'], 
                      abs(df['High'] - df['Close'].shift()), 
                      abs(df['Low'] - df['Close'].shift())], axis=1).max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()

    # Standard Deviation
    df['STDDEV'] = df['Close'].rolling(window=20).std()

    ytd_start = df.index[0]
    ytd_end = df.index[-1]
    ytd_performance = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100

    return {
        'asset_name': f"{crypto_name.capitalize()} (Cryptocurrency)",
        'Open': df['Open'].iloc[-1],
        'High': df['High'].iloc[-1],
        'Low': df['Low'].iloc[-1],
        'Close': df['Close'].iloc[-1],
        'Volume': df['Volume'].iloc[-1],
        'SMA50': df['SMA50'].iloc[-1],
        'SMA200': df['SMA200'].iloc[-1],
        'EMA12': df['EMA12'].iloc[-1],
        'EMA26': df['EMA26'].iloc[-1],
        'RSI': df['RSI'].iloc[-1],
        'UpperBand': df['UpperBand'].iloc[-1],
        'LowerBand': df['LowerBand'].iloc[-1],
        'MACD': df['MACD'].iloc[-1],
        'MACD_Signal': df['MACD_Signal'].iloc[-1],
        'OBV': df['OBV'].iloc[-1],
        'VWAP': df['VWAP'].iloc[-1],
        'ATR': df['ATR'].iloc[-1],
        'STDDEV': df['STDDEV'].iloc[-1],
        'date': df.index[-1].strftime('%Y-%m-%d'),
        'historical_data': df,
        'performance': {
            'YTD': {
                'stock': ytd_performance
            }
        }
    }
def compare_cryptos(crypto1, crypto2):
    data1 = get_crypto_data(crypto1)
    data2 = get_crypto_data(crypto2)
    
    if data1 is None or data2 is None:
        return None
    
    comparison = {
        'names': [data1['asset_name'], data2['asset_name']],
        'current_prices': [data1['Close'], data2['Close']],
        'volumes': [data1['Volume'], data2['Volume']],
        'SMA50': [data1['SMA50'], data2['SMA50']],
        'SMA200': [data1['SMA200'], data2['SMA200']],
        'RSI': [data1['RSI'], data2['RSI']],
        'MACD': [data1['MACD'], data2['MACD']],
        'volatility': [data1['STDDEV'], data2['STDDEV']],
        'historical_data': [data1['historical_data'], data2['historical_data']]
    }
    
    return comparison

def generate_crypto_comparison_report(comparison_data):
    report = f"<h2>Comparison: {comparison_data['names'][0]} vs {comparison_data['names'][1]}</h2>"
    
    report += "<table><tr><th>Metric</th><th>{}</th><th>{}</th></tr>".format(comparison_data['names'][0], comparison_data['names'][1])
    
    metrics = ['current_prices', 'volumes', 'SMA50', 'SMA200', 'RSI', 'MACD', 'volatility']
    for metric in metrics:
        report += "<tr><td>{}</td><td>{:.2f}</td><td>{:.2f}</td></tr>".format(
            metric.capitalize(),
            comparison_data[metric][0],
            comparison_data[metric][1]
        )
    
    report += "</table>"
    
    # Add performance comparison
    for i in range(2):
        df = comparison_data['historical_data'][i]
        returns = df['Close'].pct_change()
        report += f"<h3>{comparison_data['names'][i]} Performance</h3>"
        report += f"Daily Return: {returns.mean():.2%}<br>"
        report += f"Volatility: {returns.std():.2%}<br>"
        report += f"Sharpe Ratio: {returns.mean() / returns.std():.2f}<br>"
    
    return report

def get_crypto_news(crypto_name):
    symbol = crypto_mapping.get(crypto_name.lower(), crypto_name.upper())
    url = f"https://min-api.cryptocompare.com/data/v2/news/?categories={symbol}&api_key={CRYPTOCOMPARE_API_KEY}"
    response = requests.get(url)
    news_data = response.json()
    
    if news_data['Response'] == 'Error':
        return None
    
    news_items = news_data['Data'][:5]  # Get the latest 5 news items
    formatted_news = []
    
    for item in news_items:
        formatted_news.append({
            'title': item['title'],
            'url': item['url'],
            'body': item['body'],
            'published_on': datetime.fromtimestamp(item['published_on']).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return formatted_news