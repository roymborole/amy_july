
import yfinance as yf
from fuzzywuzzy import process
from company_data import COMPANIES
import time
import requests

def get_ticker_from_name(name, max_retries=3, delay=2):
    print(f"Trying to get ticker for: {name}")  # Debug print
    
    # Convert input to lowercase for case-insensitive matching
    name_lower = name.lower()
    
    # Check if the name is an exact match in the COMPANIES dictionary
    if name_lower in COMPANIES:
        ticker = COMPANIES[name_lower]
        print(f"Resolved ticker from exact match: {ticker}")  # Debug print
        return ticker
    
    # Check if the input is already a valid ticker in our COMPANIES dictionary
    for company, ticker in COMPANIES.items():
        if name.upper() == ticker:
            print(f"Input is already a valid ticker: {ticker}")  # Debug print
            return ticker
    
    # If not an exact match, try fuzzy matching
    match = process.extractOne(name_lower, COMPANIES.keys())
    if match and match[1] >= 80:  # 80 is the similarity threshold, adjust as needed
        ticker = COMPANIES[match[0]]
        print(f"Resolved ticker from fuzzy match: {ticker}")  # Debug print
        return ticker

    # If no match found in COMPANIES, try yfinance with retries
    for attempt in range(max_retries):
        try:
            ticker_obj = yf.Ticker(name)
            info = ticker_obj.info
            if 'symbol' in info:
                ticker = info['symbol']
                print(f"Resolved ticker from yfinance: {ticker}")  # Debug print
                return ticker
        except requests.exceptions.RequestException as e:
            print(f"Connection error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                print("Max retries reached. Falling back to alternative method.")
        except Exception as e:
            print(f"Error finding ticker for {name}: {str(e)}")
            break

    # If all else fails, return the input (it might already be a valid ticker)
    print(f"Unable to resolve ticker, returning input: {name}")  # Debug print
    return name