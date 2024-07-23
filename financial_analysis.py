from config import yf
from crypto_analysis import get_crypto_data, crypto_mapping
from fuzzywuzzy import process
from company_data import COMPANIES
import yfinance as yf
from datetime import datetime, timedelta
from ticker_utils import get_ticker_from_name  # Import from the new file

def calculate_return(data, period):
    end_price = data['Close'].iloc[-1]
    start_price = data['Close'].iloc[0]
    return ((end_price - start_price) / start_price) * 100

def get_sp500_data():
    sp500 = yf.Ticker("^GSPC")
    return sp500.history(period="2y")

def get_financial_data(name_or_ticker):
    ticker = get_ticker_from_name(name_or_ticker)
    
    if ticker == name_or_ticker and ticker not in COMPANIES.values():
        print(f"Unable to find ticker for {name_or_ticker}")
        return None
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        df = yf.download(ticker, start='2020-01-01', end=datetime.now().strftime('%Y-%m-%d'))

        if df.empty:
            raise ValueError(f"No data found for ticker {ticker}")
    
        stock = yf.Ticker(ticker)
        info = stock.info
        df = yf.download(ticker, start='2020-01-01', end='2024-07-01')

        if df.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()

        def compute_rsi(data, window=14):
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))

        df['RSI'] = compute_rsi(df)

        def compute_bollinger_bands(data, window=20, num_std=2):
            rolling_mean = data['Close'].rolling(window=window).mean()
            rolling_std = data['Close'].rolling(window=window).std()
            upper_band = rolling_mean + (rolling_std * num_std)
            lower_band = rolling_mean - (rolling_std * num_std)
            return rolling_mean, upper_band, lower_band

        df['SMA20'], df['UpperBand'], df['LowerBand'] = compute_bollinger_bands(df)

        financials = stock.financials.iloc[:, 0]  # Get the most recent year

        financial_data = {
            'asset_name': info.get('longName', ticker),
            'close_price': df['Close'].iloc[-1],
            'change_percent': ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
            'date': df.index[-1].strftime('%Y-%m-%d'),
            'SMA50': df['SMA50'].iloc[-1],
            'SMA200': df['SMA200'].iloc[-1],
            'RSI': df['RSI'].iloc[-1],
            'UpperBand': df['UpperBand'].iloc[-1],
            'LowerBand': df['LowerBand'].iloc[-1],
            'SMA20': df['SMA20'].iloc[-1],
            'Diluted EPS': info.get('trailingEps'),
            'Total Revenue': financials.get('Total Revenue'),
            'Operating Revenue': financials.get('Total Revenue'),
            'Basic EPS': info.get('trailingEps'),
            'Total Expenses': financials.get('Total Expenses'),
            'Net Interest Income': financials.get('Net Income'),
            'Interest Expense': financials.get('Interest Expense'),
            'Interest Income': financials.get('Interest Income'),
            'Net Income': financials.get('Net Income'),
            'Normalized Income': financials.get('Net Income'),
            'historical_data': df
        }

        today = datetime.now()
        ytd_start = datetime(today.year, 1, 1)
        one_year_ago = today - timedelta(days=365)
        three_years_ago = today - timedelta(days=3*365)

        sp500_data = get_sp500_data()

        # Ensure all datetime indices are timezone-naive
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

       
        print("Final financial data:", financial_data)
        return financial_data

    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return None

   




        