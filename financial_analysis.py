from config import yf
from crypto_analysis import get_crypto_data, crypto_mapping
from fuzzywuzzy import process
from company_data import COMPANIES
import yfinance as yf
from datetime import datetime, timedelta
from ticker_utils import get_ticker_from_name 
import traceback
import pandas as pd

def format_financial_number(number, currency_symbol='$'):
    if number is None:
        return 'N/A'
    
    abs_number = abs(number)
    sign = '-' if number < 0 else ''
    
    if abs_number >= 1e9:
        formatted = f"{sign}{currency_symbol}{abs_number / 1e9:.1f}B"
    elif abs_number >= 1e6:
        formatted = f"{sign}{currency_symbol}{abs_number / 1e6:.1f}M"
    elif abs_number >= 1e3:
        formatted = f"{sign}{currency_symbol}{abs_number / 1e3:.1f}K"
    else:
        formatted = f"{sign}{currency_symbol}{abs_number:.2f}"
    
    return formatted
    
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
        
        # Determine the currency
        is_south_african = ticker.endswith('.JO')
        is_european = ticker.endswith('.DE')
        is_uk = ticker.endswith('.L')
        is_canadian = ticker.endswith('.TO')
        
        if is_south_african:
            currency_symbol = 'R'
        elif is_european:
            currency_symbol = '€'
        elif is_uk:
            currency_symbol = '£'
        elif is_canadian:
            currency_symbol = 'C$'
        else:
            currency_symbol = '$'
        
        def format_with_currency(value):
            if value is None:
                return 'N/A'
            if is_south_african:
                value = value / 100
            return f"{currency_symbol}{value:.2f}"

        print("Calculating technical indicators")
        try:
            df['SMA50'] = df['Close'].rolling(window=50).mean()
            df['SMA200'] = df['Close'].rolling(window=200).mean()
            df['RSI'] = compute_rsi(df)
            df['SMA20'], df['UpperBand'], df['LowerBand'] = compute_bollinger_bands(df)
            df['Percentage_Change'] = (df['Close'] / df['Close'].iloc[0] - 1) * 100
        except Exception as e:
            print(f"Error calculating technical indicators: {str(e)}")
            df['SMA50'] = df['SMA200'] = df['RSI'] = df['SMA20'] = df['UpperBand'] = df['LowerBand'] = df['Percentage_Change'] = None

        print("Fetching financial data")
        financials = stock.financials
        current_year = financials.iloc[:, 0] if not financials.empty else pd.Series()
        previous_year = financials.iloc[:, 1] if not financials.empty and financials.shape[1] > 1 else pd.Series()

        def calculate_yoy_change(current, previous):
            if pd.notna(current) and pd.notna(previous) and previous != 0:
                return ((current - previous) / abs(previous)) * 100
            return None

        print("Preparing financial data dictionary")
        financial_data = {
            'asset_name': info.get('longName', ticker),
            'close_price': format_with_currency(df['Close'].iloc[-1] if not df.empty else None),
            'change_percent': ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100 if not df.empty else None,
            'market_cap': format_financial_number(info.get('marketCap'), currency_symbol),
            'date': df.index[-1].strftime('%Y-%m-%d') if not df.empty else None,
            'SMA50': format_with_currency(df['SMA50'].iloc[-1] if not df.empty and 'SMA50' in df else None),
            'SMA200': format_with_currency(df['SMA200'].iloc[-1] if not df.empty and 'SMA200' in df else None),
            'RSI': df['RSI'].iloc[-1] if not df.empty and 'RSI' in df else None,
            'UpperBand': format_with_currency(df['UpperBand'].iloc[-1] if not df.empty and 'UpperBand' in df else None),
            'LowerBand': format_with_currency(df['LowerBand'].iloc[-1] if not df.empty and 'LowerBand' in df else None),
            'SMA20': format_with_currency(df['SMA20'].iloc[-1] if not df.empty and 'SMA20' in df else None),
            'previous_close': format_with_currency(info.get('previousClose')),
            'day_low': format_with_currency(info.get('dayLow')),
            'day_high': format_with_currency(info.get('dayHigh')),
            'year_low': format_with_currency(info.get('fiftyTwoWeekLow')),
            'year_high': format_with_currency(info.get('fiftyTwoWeekHigh')),
            'avg_volume': info.get('averageVolume'),
            'pe_ratio': info.get('trailingPE'),
            'dividend_yield': info.get('dividendYield'),
            'Diluted EPS': format_with_currency(info.get('trailingEps')),
            'Total Revenue': format_financial_number(current_year.get('Total Revenue'), currency_symbol),
            'Total Revenue_yoy_change': calculate_yoy_change(current_year.get('Total Revenue'), previous_year.get('Total Revenue')),
            'Operating Revenue': format_financial_number(current_year.get('Total Revenue'), currency_symbol),
            'Operating Revenue_yoy_change': calculate_yoy_change(current_year.get('Total Revenue'), previous_year.get('Total Revenue')),
            'Total Expenses': format_financial_number(current_year.get('Total Expenses'), currency_symbol),
            'Total Expenses_yoy_change': calculate_yoy_change(current_year.get('Total Expenses'), previous_year.get('Total Expenses')),
            'Net Interest Income': format_financial_number(current_year.get('Net Income'), currency_symbol),
            'Net Interest Income_yoy_change': calculate_yoy_change(current_year.get('Net Income'), previous_year.get('Net Income')),
            'Interest Expense': format_financial_number(current_year.get('Interest Expense'), currency_symbol),
            'Interest Expense_yoy_change': calculate_yoy_change(current_year.get('Interest Expense'), previous_year.get('Interest Expense')),
            'Interest Income': format_financial_number(current_year.get('Interest Income'), currency_symbol),
            'Interest Income_yoy_change': calculate_yoy_change(current_year.get('Interest Income'), previous_year.get('Interest Income')),
            'Net Income': format_financial_number(current_year.get('Net Income'), currency_symbol),
            'Net Income_yoy_change': calculate_yoy_change(current_year.get('Net Income'), previous_year.get('Net Income')),
            'Normalized Income': format_financial_number(current_year.get('Net Income'), currency_symbol),
            'Normalized Income_yoy_change': calculate_yoy_change(current_year.get('Net Income'), previous_year.get('Net Income')),
        }
        
        if not df.empty:
            financial_data['historical_data'] = df
            financial_data['price_history'] = {
                'dates': df.index.strftime('%Y-%m-%d').tolist(),
                'percentage_changes': df['Percentage_Change'].tolist() if 'Percentage_Change' in df else []
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
        else:
            print("No historical data available, skipping performance calculations")

        return financial_data

    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        print(traceback.format_exc())
        return None