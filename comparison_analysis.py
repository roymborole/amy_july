from financial_analysis import get_financial_data
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from comparison_ai_analysis import generate_comparison_summary

def compare_assets(asset1, asset2):
    data1 = get_financial_data(asset1)
    data2 = get_financial_data(asset2)
    
    if not data1 or not data2:
        return None

    comparison_data = {
        'asset1': data1,
        'asset2': data2
    }
    comparison_data['charts'] = generate_comparison_charts(data1, data2)

    return comparison_data


def generate_comparison_report(comparison_data):
    if not comparison_data:
        return "Unable to generate comparison report due to missing data."

    asset1_name = comparison_data['asset1']['asset_name']
    asset2_name = comparison_data['asset2']['asset_name']

    report = f"""
    <style>
        .comparison-report {{
            font-family: Arial, sans-serif;
            color: #333;
            line-height: 1.6;
        }}
        .comparison-report h2, .comparison-report h3, .comparison-report h4 {{
            color: #FF69B4;  /* Bright Pink */
            text-align: center;
            margin-top: 30px;
        }}
        .comparison-report table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        .comparison-report th, .comparison-report td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .comparison-report th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        .comparison-report .chart-container {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .comparison-report .chart-container img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
    <div class="comparison-report">
        <h2>Comparison Report: {asset1_name} vs {asset2_name}</h2>
    """

    ai_summary = generate_comparison_summary(comparison_data)
    report += f"""
    <h3>Summary of Comparison</h3>
    <div class="ai-summary">
        {ai_summary}
    </div>
    """

    # Performance Comparison
    report += generate_performance_table(comparison_data)

    # Price Information
    price_metrics = [('close_price', 'Close Price'), ('change_percent', 'Percentage Change'), ('market_cap', 'Market Cap')]
    report += generate_table("Price Information", price_metrics, comparison_data)

    # Technical Indicators
    technical_indicators = ['RSI', 'SMA50', 'SMA200', 'UpperBand', 'LowerBand', 'SMA20']
    report += generate_table("Technical Indicators", technical_indicators, comparison_data)

    # Financial Metrics
    financial_metrics = ['Diluted EPS', 'Total Revenue', 'Operating Revenue', 'Basic EPS', 'Total Expenses', 
                         'Net Interest Income', 'Interest Expense', 'Interest Income', 'Net Income', 'Normalized Income']
    report += generate_table("Financial Metrics", financial_metrics, comparison_data)
    # Charts
    report += "<h3>Comparison Charts</h3>"
    for chart_name, chart_data in comparison_data['charts'].items():
        report += f"""
        <div class="chart-container">
            <h4>{chart_name}</h4>
            <img src='data:image/png;base64,{chart_data}' alt='{chart_name}' />
        </div>
        """

    report += "</div>"  # Close comparison-report div
    return report

def generate_performance_table(comparison_data):
    table = "<h3>Performance Comparison</h3>"
    table += "<table>"
    table += f"<tr><th>Period</th><th>{comparison_data['asset1']['asset_name']}</th><th>{comparison_data['asset2']['asset_name']}</th><th>S&P 500</th></tr>"

    for period in ['YTD', '1-Year', '3-Year']:
        table += "<tr>"
        table += f"<td>{period}</td>"
        table += f"<td>{format_value(comparison_data['asset1']['performance'][period]['stock'], 'performance')}%</td>"
        table += f"<td>{format_value(comparison_data['asset2']['performance'][period]['stock'], 'performance')}%</td>"
        table += f"<td>{format_value(comparison_data['asset1']['performance'][period]['sp500'], 'performance')}%</td>"
        table += "</tr>"

    table += "</table>"
    return table

def format_value(value, metric, color_code=False):
    def format_large_number(num):
        if num >= 1e12:  # Trillion
            return f"${num/1e12:.2f}T"
        elif num >= 1e9:  # Billion
            return f"${num/1e9:.2f}B"
        elif num >= 1e6:  # Million
            return f"${num/1e6:.2f}M"
        else:
            return f"${num:,.2f}"

    if isinstance(value, (int, float)):
        if metric == 'market_cap':
            return format_large_number(value)
        elif metric in ['close_price', 'Total Revenue', 'Operating Revenue', 'Total Expenses',
                        'Net Interest Income', 'Interest Expense', 'Interest Income', 'Net Income', 'Normalized Income']:
            return format_large_number(value)
        elif metric in ['change_percent', 'percentage']:
            formatted_value = f"{value:.2f}%"
            if color_code:
                color = 'green' if value > 0 else 'red' if value < 0 else 'black'
                return f'<span style="color: {color};">{formatted_value}</span>'
            return formatted_value
        elif metric in ['Diluted EPS', 'Basic EPS']:
            return f"${value:.2f}"
        else:
            return f"{value:.2f}"
    elif value == 'N/A':
        return value
    return str(value)

def generate_table(title, metrics, comparison_data):
    table = f"<h3>{title}</h3>"
    table += "<table>"
    if title == "Financial Metrics":
        table += f"<tr><th>Metric</th><th>{comparison_data['asset1']['asset_name']}</th><th>Y/Y Change</th><th>{comparison_data['asset2']['asset_name']}</th><th>Y/Y Change</th></tr>"
    else:
        table += f"<tr><th>Metric</th><th>{comparison_data['asset1']['asset_name']}</th><th>{comparison_data['asset2']['asset_name']}</th></tr>"

    for metric in metrics:
        if isinstance(metric, tuple):
            key, display_name = metric
        else:
            key = display_name = metric
        
        if key in comparison_data['asset1'] and key in comparison_data['asset2']:
            table += "<tr>"
            table += f"<td>{display_name}</td>"
            value1 = comparison_data['asset1'][key]
            value2 = comparison_data['asset2'][key]
            table += f"<td>{format_value(value1, key)}</td>"
            if title == "Financial Metrics":
                change1 = comparison_data['asset1'].get(f'{key}_yoy_change', 'N/A')
                change2 = comparison_data['asset2'].get(f'{key}_yoy_change', 'N/A')
                table += f"<td>{format_value(change1, 'percentage', color_code=True)}</td>"
                table += f"<td>{format_value(value2, key)}</td>"
                table += f"<td>{format_value(change2, 'percentage', color_code=True)}</td>"
            else:
                table += f"<td>{format_value(value2, key)}</td>"
            table += "</tr>"

    table += "</table>"
    return table

def plt_to_base64():
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate_comparison_charts(data1, data2):
    charts = {}

    # Price chart
    plt.figure(figsize=(10, 6))
    plt.plot(data1['historical_data'].index, data1['historical_data']['Close'], label=data1['asset_name'])
    plt.plot(data2['historical_data'].index, data2['historical_data']['Close'], label=data2['asset_name'])
    plt.title('Price Comparison')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    charts['Price Comparison'] = plt_to_base64()

    # Volume chart
    plt.figure(figsize=(10, 6))
    plt.plot(data1['historical_data'].index, data1['historical_data']['Volume'], label=data1['asset_name'])
    plt.plot(data2['historical_data'].index, data2['historical_data']['Volume'], label=data2['asset_name'])
    plt.title('Volume Comparison')
    plt.xlabel('Date')
    plt.ylabel('Volume')
    plt.legend()
    charts['Volume Comparison'] = plt_to_base64()

    # RSI chart
    plt.figure(figsize=(10, 6))
    plt.plot(data1['historical_data'].index, data1['historical_data']['RSI'], label=data1['asset_name'])
    plt.plot(data2['historical_data'].index, data2['historical_data']['RSI'], label=data2['asset_name'])
    plt.title('RSI Comparison')
    plt.xlabel('Date')
    plt.ylabel('RSI')
    plt.legend()
    charts['RSI Comparison'] = plt_to_base64()

    # Moving Average chart
    plt.figure(figsize=(10, 6))
    plt.plot(data1['historical_data'].index, data1['historical_data']['SMA50'], label=f"{data1['asset_name']} 50-day MA")
    plt.plot(data1['historical_data'].index, data1['historical_data']['SMA200'], label=f"{data1['asset_name']} 200-day MA")
    plt.plot(data2['historical_data'].index, data2['historical_data']['SMA50'], label=f"{data2['asset_name']} 50-day MA")
    plt.plot(data2['historical_data'].index, data2['historical_data']['SMA200'], label=f"{data2['asset_name']} 200-day MA")
    plt.title('Moving Average Comparison')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    charts['Moving Average Comparison'] = plt_to_base64()

    return charts