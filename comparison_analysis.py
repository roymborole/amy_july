from financial_analysis import get_financial_data
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from comparison_ai_analysis import generate_comparison_summary

def create_table_row_with_tooltip(label, value1, value2, tooltip):
    return f"""
    <tr>
        <td><span data-tooltip="{tooltip}"><strong>{label}</strong></span></td>
        <td>{value1}</td>
        <td>{value2}</td>
    </tr>
    """

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

    comparison_data['performance'] = {
        'asset1': data1.get('performance', {}),
        'asset2': data2.get('performance', {})
    }

    return comparison_data

def generate_performance_overview(comparison_data):
    overview = "<h3>Performance Overview</h3>"
    overview += '<table class="performance-table">'
    overview += f'<tr><th>Return</th><th>{comparison_data["asset1"]["asset_name"]}</th><th>{comparison_data["asset2"]["asset_name"]}</th><th>S&P 500</th></tr>'

    for period in ['YTD', '1-Year', '3-Year']:
        overview += '<tr>'
        overview += f'<td>{period}</td>'
        for asset in ['asset1', 'asset2']:
            if comparison_data['performance'][asset].get(period):
                value = comparison_data['performance'][asset][period]['stock']
                overview += f'<td>{format_value(value, "performance")}%</td>'
            else:
                overview += '<td>N/A</td>'
        
        # S&P 500 performance (using asset1's data, assuming it's the same for both)
        if comparison_data['performance']['asset1'].get(period):
            sp500_value = comparison_data['performance']['asset1'][period]['sp500']
            overview += f'<td>{format_value(sp500_value, "performance")}%</td>'
        else:
            overview += '<td>N/A</td>'
        
        overview += '</tr>'

    overview += '</table>'
    return overview

def generate_key_statistics_table(comparison_data):
    table = "<h3>Key Statistics</h3>"
    table += "<table>"
    table += f"<tr><th>Metric</th><th>{comparison_data['asset1']['asset_name']}</th><th>{comparison_data['asset2']['asset_name']}</th></tr>"

    metrics = [
        ('previous_close', 'Previous Close', "The stock's closing price from the previous trading day."),
        ('day_low', 'Day Range', "The lowest and highest prices at which the stock has traded during the current trading day."),
        ('year_low', '52 Week Range', "The lowest and highest prices at which the stock has traded over the past 52 weeks."),
        ('avg_volume', 'Average Volume', "The average number of shares traded daily over a specific period, typically 30 days."),
        ('pe_ratio', 'P/E Ratio', "Price-to-Earnings Ratio. A valuation ratio of a company's current share price compared to its earnings per share."),
        ('dividend_yield', 'Dividend Yield', "The annual dividend payment as a percentage of the stock's current price.")
    ]

    for key, display_name, tooltip in metrics:
        value1 = comparison_data['asset1'].get(key, 'N/A')
        value2 = comparison_data['asset2'].get(key, 'N/A')
        
        if key == 'day_low':
            value1 = f"{format_value(comparison_data['asset1'].get('day_low', 'N/A'), key)} - {format_value(comparison_data['asset1'].get('day_high', 'N/A'), key)}"
            value2 = f"{format_value(comparison_data['asset2'].get('day_low', 'N/A'), key)} - {format_value(comparison_data['asset2'].get('day_high', 'N/A'), key)}"
        elif key == 'year_low':
            value1 = f"{format_value(comparison_data['asset1'].get('year_low', 'N/A'), key)} - {format_value(comparison_data['asset1'].get('year_high', 'N/A'), key)}"
            value2 = f"{format_value(comparison_data['asset2'].get('year_low', 'N/A'), key)} - {format_value(comparison_data['asset2'].get('year_high', 'N/A'), key)}"
        elif key == 'dividend_yield':
            value1 = format_value(value1, key, percentage=True)
            value2 = format_value(value2, key, percentage=True)
        else:
            value1 = format_value(value1, key)
            value2 = format_value(value2, key)
        
        table += create_table_row_with_tooltip(display_name, value1, value2, tooltip)

    table += "</table>"
    return table

def generate_performance_overview_chart(comparison_data):
    plt.figure(figsize=(10, 6), facecolor='#393939')
    ax = plt.gca()
    ax.set_facecolor('#393939')
    
    periods = ['YTD', '1-Year', '3-Year']
    asset1_returns = [comparison_data['performance']['asset1'].get(period, {}).get('stock', 0) for period in periods]
    asset2_returns = [comparison_data['performance']['asset2'].get(period, {}).get('stock', 0) for period in periods]
    sp500_returns = [comparison_data['performance']['asset1'].get(period, {}).get('sp500', 0) for period in periods]

    x = range(len(periods))
    width = 0.25

    # Changed colors here
    plt.bar([i - width for i in x], asset1_returns, width, label=comparison_data['asset1']['asset_name'], color='pink')
    plt.bar(x, asset2_returns, width, label=comparison_data['asset2']['asset_name'], color='purple')
    plt.bar([i + width for i in x], sp500_returns, width, label='S&P 500', color='yellow')

    plt.xlabel('Time Period', color='white')
    plt.ylabel('Return (%)', color='white')
    plt.title('Performance Overview', color='white')
    plt.xticks(x, periods, color='white')
    plt.yticks(color='white')
    plt.legend(facecolor='#393939', edgecolor='white', labelcolor='white')

    # Change spine colors to white
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    # Adjust layout to prevent cutoff
    plt.tight_layout()
  
    chart = f"""
    <div class="chart-container">
        <h4 style="color: white; margin-bottom: 15px;">Performance Overview</h4>
        <img src='data:image/png;base64,{plt_to_base64()}' alt='Performance Overview' style="max-width: 100%; height: auto;" />
    </div>
    """
    return chart

def format_value(value, metric, percentage=False, color_code=False):
    def format_large_number(num):
        if num >= 1e12:  # Trillion
            return f"${num/1e12:.2f}T"
        elif num >= 1e9:  # Billion
            return f"${num/1e9:.2f}B"
        elif num >= 1e6:  # Million
            return f"${num/1e6:.2f}M"
        else:
            return f"${num:,.2f}"

    if value == 'N/A':
        return 'N/A'

    if isinstance(value, (int, float)):
        if metric == 'market_cap':
            return format_large_number(value)
        elif metric in ['close_price', 'Total Revenue', 'Operating Revenue', 'Total Expenses',
                        'Net Interest Income', 'Interest Expense', 'Interest Income', 'Net Income', 'Normalized Income']:
            return format_large_number(value)
        elif metric in ['change_percent', 'percentage'] or percentage:
            formatted_value = f"{value:.2f}%"
            if color_code:
                color = 'green' if value > 0 else 'red' if value < 0 else 'black'
                return f'<span style="color: {color};">{formatted_value}</span>'
            return formatted_value
        elif metric in ['Diluted EPS', 'Basic EPS', 'previous_close', 'day_low', 'day_high', 'year_low', 'year_high']:
            return f"${value:.2f}"
        elif metric == 'avg_volume':
            return f"{value:,.0f}"
        elif metric == 'pe_ratio':
            return f"{value:.2f}"
        else:
            return f"{value:.2f}"
    
    return str(value)

def generate_comparison_report(comparison_data):
    if not comparison_data:
        return "Unable to generate comparison report due to missing data."

    asset1_name = comparison_data['asset1']['asset_name']
    asset2_name = comparison_data['asset2']['asset_name']

    report = f"""
    <style>
        .comparison-report {{
            font-family: Roboto, sans-serif;
            color: black;
            line-height: 1.6;  
            background-color: #393939;
            padding: 20px;
        }}
        .comparison-report h2, .comparison-report h3, .comparison-report h4 {{
            color: #ffffff;
            text-align: center;
            margin-top: 30px;
            margin-bottom: 20px;
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
            background-color: #C1FF72;
            font-weight: bold;
        }}
        .comparison-report td {{
            background-color: #D9D9D9;
        }}
        .comparison-report .chart-container {{
            text-align: center;
            margin-bottom: 30px;
            background-color: #393939;
            margin-top: 30px;
        }}
        .comparison-report .chart-container img {{
            max-width: 100%;
            height: auto;
            background-color: #393939;
            border-radius: 10px;
            margin-top: 30px;
            margin-bottom: 30px;
        }}
        .performance-table {{
            margin: 0 auto;
            border-collapse: collapse;
            width: 80%;
        }}
        .performance-table th, .performance-table td {{
            padding: 10px;
            text-align: left;
            border: 1px solid white;
            font-family: 'Roboto', sans-serif;
            color: black;
        }}
        .performance-table th {{
            background-color: #C1FF72;
            font-weight: bold;
        }}
        .performance-table td {{
            background-color: #D9D9D9;
        }}
        .ai-summary {{
            text-align: center;
            font-family: 'Roboto', sans-serif;
            color: #ffffff;
            background-color: #393939;
            margin-bottom: 30px;
            margin-top: 30px;
        }}
        .report-content {{
            display: flex;
            flex-direction: column;
            gap: 40px;  /* Adds space between flex items */
        }}
        .chart-container {{
            text-align: center;
            background-color: #393939;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            margin-top: 30px;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            background-color: #393939;
            border-radius: 10px;
            margin-bottom: 30px;
            margin-top: 30px;
        }}
        .summary-container {{
            background-color: #393939;
            padding: 20px;
            border-radius: 10px;
        }}
    </style>
    <div class="comparison-report">
        <h2>Comparison Report: {asset1_name} vs {asset2_name}</h2>
    """

    report += f"""
        <div class="chart-container">
            <h3>Performance Overview</h3>
            {generate_performance_overview_chart(comparison_data)}
        </div>
    """

    ai_summary = generate_comparison_summary(comparison_data)
    report += f"""
    <h3>Summary of Comparison</h3>
    <div class="ai-summary">
        {ai_summary}
    </div>
    """

    report += generate_key_statistics_table(comparison_data)
    report += generate_performance_table(comparison_data)
    report += generate_performance_overview(comparison_data)

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

    report += """
        </div>  <!-- Close report-content div -->
    </div>  <!-- Close comparison-report div -->
    """

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

def generate_table(title, metrics, comparison_data):
    table = f"<h3>{title}</h3>"
    table += "<table>"
    if title == "Financial Metrics":
        table += f"<tr><th>Metric</th><th>{comparison_data['asset1']['asset_name']}</th><th>Y/Y Change</th><th>{comparison_data['asset2']['asset_name']}</th><th>Y/Y Change</th></tr>"
    else:
        table += f"<tr><th>Metric</th><th>{comparison_data['asset1']['asset_name']}</th><th>{comparison_data['asset2']['asset_name']}</th></tr>"

    tooltips = {
        'close_price': "The most recent closing price of the stock.",
        'change_percent': "The percentage change in the stock's price since the previous trading day.",
        'market_cap': "The total market value of a company's outstanding shares.",
        'RSI': "Relative Strength Index: A momentum indicator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions.",
        'SMA50': "50-day Simple Moving Average: The average closing price over the last 50 trading days.",
        'SMA200': "200-day Simple Moving Average: The average closing price over the last 200 trading days.",
        'UpperBand': "Upper Bollinger Band: Two standard deviations above the 20-day SMA.",
        'LowerBand': "Lower Bollinger Band: Two standard deviations below the 20-day SMA.",
        'SMA20': "20-day Simple Moving Average: The average closing price over the last 20 trading days.",
        'Diluted EPS': "Diluted Earnings Per Share: A company's profit divided by its number of common shares outstanding.",
        'Total Revenue': "The total amount of income generated by the sale of goods or services related to the company's primary operations.",
        'Operating Revenue': "Revenue generated from a company's core business operations.",
        'Basic EPS': "Basic Earnings Per Share: The portion of a company's profit allocated to each outstanding share of common stock.",
        'Total Expenses': "The total costs incurred by a company in its operations.",
        'Net Interest Income': "The difference between the revenue generated from a bank's assets and the expenses associated with paying its liabilities.",
        'Interest Expense': "The cost incurred by a company for borrowed funds.",
        'Interest Income': "The amount earned by an entity's investments in interest-bearing assets.",
        'Net Income': "The company's total earnings or profit.",
        'Normalized Income': "A company's economic performance adjusted for unusual, non-recurring or one-time influences."
    }

    for metric in metrics:
        if isinstance(metric, tuple):
            key, display_name = metric
        else:
            key = display_name = metric
        
        tooltip = tooltips.get(key, "")
        
        if key in comparison_data['asset1'] and key in comparison_data['asset2']:
            table += "<tr>"
            table += f'<td><span data-tooltip="{tooltip}"><strong>{display_name}</strong></span></td>'
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

    def setup_chart(title, xlabel, ylabel):
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#393939')
        ax.set_facecolor('#393939')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        plt.title(title, color='white')
        plt.xlabel(xlabel, color='white')
        plt.ylabel(ylabel, color='white')
        return ax

    # Price chart
    ax = setup_chart('Price Comparison', 'Date', 'Price')
    ax.plot(data1['historical_data'].index, data1['historical_data']['Close'], label=data1['asset_name'])
    ax.plot(data2['historical_data'].index, data2['historical_data']['Close'], label=data2['asset_name'])
    plt.legend(facecolor='#393939', edgecolor='white', labelcolor='white')
    charts['Price Comparison'] = plt_to_base64()

    # Volume chart
    ax = setup_chart('Volume Comparison', 'Date', 'Volume')
    ax.plot(data1['historical_data'].index, data1['historical_data']['Volume'], label=data1['asset_name'])
    ax.plot(data2['historical_data'].index, data2['historical_data']['Volume'], label=data2['asset_name'])
    plt.legend(facecolor='#393939', edgecolor='white', labelcolor='white')
    charts['Volume Comparison'] = plt_to_base64()

    # RSI chart
    ax = setup_chart('RSI Comparison', 'Date', 'RSI')
    ax.plot(data1['historical_data'].index, data1['historical_data']['RSI'], label=data1['asset_name'])
    ax.plot(data2['historical_data'].index, data2['historical_data']['RSI'], label=data2['asset_name'])
    plt.legend(facecolor='#393939', edgecolor='white', labelcolor='white')
    charts['RSI Comparison'] = plt_to_base64()

    # Moving Average chart
    ax = setup_chart('Moving Average Comparison', 'Date', 'Price')
    ax.plot(data1['historical_data'].index, data1['historical_data']['SMA50'], label=f"{data1['asset_name']} 50-day MA")
    ax.plot(data1['historical_data'].index, data1['historical_data']['SMA200'], label=f"{data1['asset_name']} 200-day MA")
    ax.plot(data2['historical_data'].index, data2['historical_data']['SMA50'], label=f"{data2['asset_name']} 50-day MA")
    ax.plot(data2['historical_data'].index, data2['historical_data']['SMA200'], label=f"{data2['asset_name']} 200-day MA")
    plt.legend(facecolor='#393939', edgecolor='white', labelcolor='white')
    charts['Moving Average Comparison'] = plt_to_base64()

    return charts