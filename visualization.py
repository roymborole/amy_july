
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
import io
from io import BytesIO
import pandas as pd

def create_chart(data, chart_type, ticker):
    plt.figure(figsize=(10, 6), facecolor='none')
    ax = plt.axes()
    ax.set_facecolor('none')
    
    if isinstance(data, pd.DataFrame):
        df = data
    else:
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
    
    if chart_type == 'price_sma':
        plt.plot(df.index, df['Close'], label='Close Price')
        if 'SMA50' in df.columns:
            plt.plot(df.index, df['SMA50'], label='50-day SMA')
        if 'SMA200' in df.columns:
            plt.plot(df.index, df['SMA200'], label='200-day SMA')
        plt.title(f'{ticker} Price and Moving Averages')
    elif chart_type == 'rsi':
        if 'RSI' in df.columns:
            plt.plot(df.index, df['RSI'], label='RSI', color='purple')
            plt.axhline(70, color='r', linestyle='--')
            plt.axhline(30, color='r', linestyle='--')
            plt.title(f'{ticker} Relative Strength Index (RSI)')
        else:
            plt.text(0.5, 0.5, 'RSI data not available', ha='center', va='center')
    elif chart_type == 'bollinger':
        plt.plot(df.index, df['Close'], label='Close Price')
        if 'SMA20' in df.columns:
            plt.plot(df.index, df['SMA20'], label='20-day SMA')
        if 'UpperBand' in df.columns and 'LowerBand' in df.columns:
            plt.plot(df.index, df['UpperBand'], label='Upper Bollinger Band', linestyle='--')
            plt.plot(df.index, df['LowerBand'], label='Lower Bollinger Band', linestyle='--')
        plt.title(f'{ticker} Bollinger Bands')
    
    plt.legend()

    plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tick_params(colors='gray')
    plt.xlabel('Date', color='gray')
    plt.ylabel('Price' if chart_type != 'rsi' else 'RSI', color='gray')
    
    img = BytesIO()
    plt.savefig(img, format='png', transparent=True)
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_comparison_chart(data1, data2, column, name1, name2):
    if isinstance(data1.get(column), pd.Series) and isinstance(data2.get(column), pd.Series):
        plt.figure(figsize=(10, 6), facecolor='none')
        ax = plt.axes()
        ax.set_facecolor('none')
        plt.plot(data1[column].index, data1[column], label=name1)
        plt.plot(data2[column].index, data2[column], label=name2)
        plt.title(f'{column} Comparison')
        plt.xlabel('Date')
        plt.ylabel(column)
        plt.legend()
        
        plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
        plt.tick_params(colors='gray')
        
        img = BytesIO()
        plt.savefig(img, format='png', transparent=True)
        img.seek(0)
        chart = base64.b64encode(img.getvalue()).decode()
        plt.close()
        return chart
    return None