import yfinance as yf
from datetime import datetime

CURRENCY_MAPPING = {
    '.L': 'GBP',   # UK stocks
    '.DE': 'EUR',  # German stocks
    '.JO': 'ZAR',  # South African stocks
    'DEFAULT': 'USD'  # Default to USD for other stocks
}

def get_currency_for_ticker(ticker):
    for suffix, currency in CURRENCY_MAPPING.items():
        if ticker.endswith(suffix):
            return currency
    return CURRENCY_MAPPING['DEFAULT']

def get_exchange_rate(from_currency, to_currency='USD'):
    if from_currency == to_currency:
        return 1
    
    ticker = f"{from_currency}{to_currency}=X"
    try:
        currency_pair = yf.Ticker(ticker)
        return currency_pair.history(period="1d")['Close'].iloc[-1]
    except Exception as e:
        print(f"Error fetching exchange rate for {ticker}: {str(e)}")
        return None

def convert_currency(amount, from_currency, to_currency='USD'):
    if from_currency == to_currency:
        return amount
    
    exchange_rate = get_exchange_rate(from_currency, to_currency)
    if exchange_rate is None:
        return None
    
    return amount * exchange_rate

def format_currency(amount, currency):
    currency_symbols = {
        'USD': '$',
        'GBP': '£',
        'EUR': '€',
        'ZAR': 'R'
    }
    symbol = currency_symbols.get(currency, '')
    
    if amount is None:
        return 'N/A'
    if abs(amount) >= 1e9:
        return f"{symbol}{amount / 1e9:.3f}B"
    elif abs(amount) >= 1e6:
        return f"{symbol}{amount / 1e6:.3f}M"
    else:
        return f"{symbol}{amount:.2f}"

def convert_and_format(value, from_currency, to_currency):
    if value is None:
        return None, 'N/A'
    try:
        converted_value = convert_currency(value, from_currency, to_currency)
        return converted_value, format_currency(converted_value, to_currency)
    except Exception as e:
        print(f"Error in convert_and_format: {str(e)}")
        return None, 'Error'