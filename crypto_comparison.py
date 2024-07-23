# crypto_comparison.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from crypto_analysis import get_crypto_data, crypto_mapping
from datetime import datetime, timedelta

def compare_cryptos(crypto1, crypto2):
    data1 = get_crypto_data(crypto1)
    data2 = get_crypto_data(crypto2)
    
    if data1 is None or data2 is None:
        return None
    
    # Calculate additional metrics
    for data in [data1, data2]:
        df = data['historical_data']
        data['daily_returns'] = df['Close'].pct_change()
        data['volatility'] = data['daily_returns'].std() * np.sqrt(365)  # Annualized volatility
        data['sharpe_ratio'] = (data['daily_returns'].mean() * 365) / (data['daily_returns'].std() * np.sqrt(365))  # Assuming risk-free rate of 0
    
    comparison = {
        'names': [data1['asset_name'], data2['asset_name']],
        'current_prices': [data1['Close'], data2['Close']],
        'volumes': [data1['Volume'], data2['Volume']],
        'market_caps': [data1.get('market_cap', 'N/A'), data2.get('market_cap', 'N/A')],
        'SMA50': [data1['SMA50'], data2['SMA50']],
        'SMA200': [data1['SMA200'], data2['SMA200']],
        'RSI': [data1['RSI'], data2['RSI']],
        'MACD': [data1['MACD'], data2['MACD']],
        'volatility': [data1['volatility'], data2['volatility']],
        'sharpe_ratio': [data1['sharpe_ratio'], data2['sharpe_ratio']],
        'historical_data': [data1['historical_data'], data2['historical_data']]
    }
    
    return comparison

def generate_comparison_chart(comparison_data):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Price chart
    ax1.plot(comparison_data['historical_data'][0].index, comparison_data['historical_data'][0]['Close'], label=comparison_data['names'][0])
    ax1.plot(comparison_data['historical_data'][1].index, comparison_data['historical_data'][1]['Close'], label=comparison_data['names'][1])
    ax1.set_title('Price Comparison')
    ax1.set_ylabel('Price (USD)')
    ax1.legend()
    
    # Volume chart
    ax2.bar(comparison_data['historical_data'][0].index, comparison_data['historical_data'][0]['Volume'], alpha=0.5, label=comparison_data['names'][0])
    ax2.bar(comparison_data['historical_data'][1].index, comparison_data['historical_data'][1]['Volume'], alpha=0.5, label=comparison_data['names'][1])
    ax2.set_title('Volume Comparison')
    ax2.set_ylabel('Volume')
    ax2.legend()
    
    plt.tight_layout()
    
    # Convert plot to base64 string
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    plt.close()
    
    return img_str

def generate_crypto_comparison_report(comparison_data):
    report = f"<h2>Comparison: {comparison_data['names'][0]} vs {comparison_data['names'][1]}</h2>"
    
    report += "<table><tr><th>Metric</th><th>{}</th><th>{}</th></tr>".format(comparison_data['names'][0], comparison_data['names'][1])
    
    metrics = ['current_prices', 'volumes', 'market_caps', 'SMA50', 'SMA200', 'RSI', 'MACD', 'volatility', 'sharpe_ratio']
    for metric in metrics:
        report += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            metric.replace('_', ' ').capitalize(),
            f"{comparison_data[metric][0]:.2f}" if isinstance(comparison_data[metric][0], (int, float)) else comparison_data[metric][0],
            f"{comparison_data[metric][1]:.2f}" if isinstance(comparison_data[metric][1], (int, float)) else comparison_data[metric][1]
        )
    
    report += "</table>"
    
    # Add performance comparison
    for i in range(2):
        df = comparison_data['historical_data'][i]
        returns = df['Close'].pct_change()
        report += f"<h3>{comparison_data['names'][i]} Performance</h3>"
        report += f"Daily Return: {returns.mean():.2%}<br>"
        report += f"Volatility: {returns.std():.2%}<br>"
        report += f"Sharpe Ratio: {comparison_data['sharpe_ratio'][i]:.2f}<br>"
    
    # Add comparison chart
    chart_img = generate_comparison_chart(comparison_data)
    report += f"<h3>Comparison Chart</h3><img src='data:image/png;base64,{chart_img}' alt='Comparison Chart'>"
    
    return report

def get_correlated_cryptos(crypto_symbol, top_n=5):
    # This function would require data for multiple cryptocurrencies
    # For simplicity, we'll return a mock result
    mock_correlations = {
        'BTC': ['ETH', 'LTC', 'XRP', 'BCH', 'ADA'],
        'ETH': ['BTC', 'LTC', 'XRP', 'LINK', 'DOT'],
        'DOGE': ['SHIB', 'BTC', 'ETH', 'LTC', 'ADA']
    }
    return mock_correlations.get(crypto_symbol, [])[:top_n]

if __name__ == "__main__":
    crypto1 = input("Enter the first cryptocurrency symbol: ")
    crypto2 = input("Enter the second cryptocurrency symbol: ")
    
    comparison_data = compare_cryptos(crypto1, crypto2)
    if comparison_data:
        report = generate_crypto_comparison_report(comparison_data)
        print(report)
    else:
        print("Unable to generate comparison. Please check the cryptocurrency symbols and try again.")