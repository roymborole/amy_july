from config import yf
from crypto_analysis import get_crypto_data, crypto_mapping
from fuzzywuzzy import process
from company_data import COMPANIES
import yfinance as yf
from datetime import datetime, timedelta
from ticker_utils import get_ticker_from_name 
import traceback
import pandas as pd

def format_financial_number(number):
    if number is None:
        return 'N/A'
    if abs(number) >= 1e9:
        return f"${number / 1e9:.3f}B"
    elif abs(number) >= 1e6:
        return f"${number / 1e6:.3f}M"
    else:
        return f"${number:.2f}"
    
def calculate_return(data, period):
    end_price = data['Close'].iloc[-1]
    start_price = data['Close'].iloc[0]
    return ((end_price - start_price) / start_price) * 100

def get_sp500_data():
    sp500 = yf.Ticker("^GSPC")
    return sp500.history(period="2y")

def compute_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_bollinger_bands(data, window=20, num_std=2):
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return rolling_mean, upper_band, lower_band

def calculate_return(data, period):
    end_price = data['Close'].iloc[-1]
    start_price = data['Close'].iloc[0]
    return ((end_price - start_price) / start_price) * 100

def get_sp500_data():
    sp500 = yf.Ticker("^GSPC")
    return sp500.history(period="2y")

def get_financial_data(name_or_ticker):
    print(f"Starting get_financial_data for {name_or_ticker}")
    ticker = get_ticker_from_name(name_or_ticker)
    
    if ticker == name_or_ticker and ticker not in COMPANIES.values():
        print(f"Unable to find ticker for {name_or_ticker}")
        return None
    
    try:
        print(f"Fetching data for ticker: {ticker}")
        stock = yf.Ticker(ticker)
        
        print("Fetching stock info")
        info = stock.info
        if not info:
            print(f"No info found for {ticker}")
            return None

        print("Downloading historical data")
        df = yf.download(ticker, start='2020-01-01', end=datetime.now().strftime('%Y-%m-%d'))

        if df.empty:
            print(f"No historical data found for ticker {ticker}")
            return None
        
        print("Calculating technical indicators")
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        df['RSI'] = compute_rsi(df)
        df['SMA20'], df['UpperBand'], df['LowerBand'] = compute_bollinger_bands(df)

        print("Fetching financial data")
        financials = stock.financials
        if not financials.empty:
                current_year = financials.iloc[:, 0]
                previous_year = financials.iloc[:, 1] if financials.shape[1] > 1 else pd.Series()

        def calculate_yoy_change(current, previous):
            if pd.notna(current) and pd.notna(previous) and previous != 0:
                return ((current - previous) / abs(previous)) * 100
            return None

        print("Preparing financial data dictionary")
        financial_data = {
            'asset_name': info.get('longName', ticker),
            'close_price': df['Close'].iloc[-1],
            'change_percent': ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
            'market_cap': info.get('marketCap'),
            'date': df.index[-1].strftime('%Y-%m-%d'),
            'SMA50': df['SMA50'].iloc[-1],
            'SMA200': df['SMA200'].iloc[-1],
            'RSI': df['RSI'].iloc[-1],
            'UpperBand': df['UpperBand'].iloc[-1],
            'LowerBand': df['LowerBand'].iloc[-1],
            'SMA20': df['SMA20'].iloc[-1],
            'Diluted EPS': info.get('trailingEps'),
            'Total Revenue': format_financial_number(current_year.get('Total Revenue')),
            'Total Revenue_yoy_change': calculate_yoy_change(current_year.get('Total Revenue'), previous_year.get('Total Revenue')),
            'Operating Revenue': format_financial_number(current_year.get('Total Revenue')),
            'Operating Revenue_yoy_change': calculate_yoy_change(current_year.get('Total Revenue'), previous_year.get('Total Revenue')),
            'Total Expenses': format_financial_number(current_year.get('Total Expenses')),
            'Total Expenses_yoy_change': calculate_yoy_change(current_year.get('Total Expenses'), previous_year.get('Total Expenses')),
            'Net Interest Income': format_financial_number(current_year.get('Net Income')),
            'Net Interest Income_yoy_change': calculate_yoy_change(current_year.get('Net Income'), previous_year.get('Net Income')),
            'Interest Expense': format_financial_number(current_year.get('Interest Expense')),
            'Interest Expense_yoy_change': calculate_yoy_change(current_year.get('Interest Expense'), previous_year.get('Interest Expense')),
            'Interest Income': format_financial_number(current_year.get('Interest Income')),
            'Interest Income_yoy_change': calculate_yoy_change(current_year.get('Interest Income'), previous_year.get('Interest Income')),
            'Net Income': format_financial_number(current_year.get('Net Income')),
            'Net Income_yoy_change': calculate_yoy_change(current_year.get('Net Income'), previous_year.get('Net Income')),
            'Normalized Income': format_financial_number(current_year.get('Net Income')),
            'Normalized Income_yoy_change': calculate_yoy_change(current_year.get('Net Income'), previous_year.get('Net Income')),
            
            'historical_data': df
            
    }

        print("Calculating performance data")
        today = datetime.now()
        ytd_start = datetime(today.year, 1, 1)
        one_year_ago = today - timedelta(days=365)
        three_years_ago = today - timedelta(days=3*365)

        sp500_data = get_sp500_data()

        df.index = df.index.tz_localize(None)
        sp500_data.index = sp500_data.index.tz_localize(None)

        performance_data = {
            'YTD': {
                'stock': calculate_return(df.loc[ytd_start:], 'YTD'),
                'sp500': calculate_return(sp500_data.loc[ytd_start:], 'YTD')
            },
            '1-Year': {
                'stock': calculate_return(df.loc[one_year_ago:], '1-Year'),
                'sp500': calculate_return(sp500_data.loc[one_year_ago:], '1-Year')
            },
            '3-Year': {
                'stock': calculate_return(df.loc[three_years_ago:], '3-Year'),
                'sp500': calculate_return(sp500_data.loc[three_years_ago:], '3-Year')
            }
        }

        financial_data['performance'] = performance_data

        print("Financial data preparation complete")
        return financial_data

    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        print(traceback.format_exc())
        return None
   




        