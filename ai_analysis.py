from config import anthropic_client
import json

def create_table_row(label, value, tooltip):
    return f"""
    <tr>
        <td><span data-tooltip="{tooltip}">{label}</span></td>
        <td>{value}</td>
    </tr>
    """

def format_large_number(value):
    if value is None:
        return 'N/A'
    if isinstance(value, (int, float)):
        if value >= 1e12:
            return f"${value/1e12:.2f}T"
        elif value >= 1e9:
            return f"${value/1e9:.2f}B"
        elif value >= 1e6:
            return f"${value/1e6:.2f}M"
        else:
            return f"${value:,.2f}"
    return str(value)

def format_value(value, is_currency=True, decimals=2):
    if value is None:
        return 'N/A'
    if is_currency:
        return f"${value:,.{decimals}f}" if isinstance(value, (int, float)) else value
    return f"{value:.{decimals}f}" if isinstance(value, (int, float)) else value

def get_analysis_report(raw_data, company_name):
    summarized_data = {
        'company_name': company_name,
        'close_price': raw_data.get('close_price'),
        'change_percent': raw_data.get('change_percent'),
        'date': raw_data.get('date'),
        'SMA50': raw_data.get('SMA50'),
        'SMA200': raw_data.get('SMA200'),
        'RSI': raw_data.get('RSI'),
        'UpperBand': raw_data.get('UpperBand'),
        'LowerBand': raw_data.get('LowerBand'),
        'SMA20': raw_data.get('SMA20'),
        'Diluted EPS': raw_data.get('Diluted EPS'),
        'Total Revenue': raw_data.get('Total Revenue'),
        'Operating Revenue': raw_data.get('Operating Revenue'),
        'Basic EPS': raw_data.get('Basic EPS'),
        'Total Expenses': raw_data.get('Total Expenses'),
        'Net Interest Income': raw_data.get('Net Interest Income'),
        'Interest Expense': raw_data.get('Interest Expense'),
        'Interest Income': raw_data.get('Interest Income'),
        'Net Income': raw_data.get('Net Income'),
        'Normalized Income': raw_data.get('Normalized Income'),
        'market_cap': raw_data.get('market_cap')
        
    }
    
    prompt = f"""
    Create a comprehensive technical analysis report for {company_name} based on the following summarized data:
    {json.dumps(summarized_data, indent=2)}

    Include the following sections:
    Overview: Introduce the stock and provide a brief background on the company. (Do not Print a Heading)
    Technical Analysis: (Do not Print a Heading)
       - Simple Moving Averages (50-day and 200-day)
       - Relative Strength Index (RSI)
       - Bollinger Bands
    Financial Analysis: Discuss the provided financial indicators: Market Cap, Operating Revenue, Total Expenses, Interest Expense, Interest Income, Basic EPS, Net Income
    Summary: Synthesize insights from all indicators.
    Investment Outlook: Based on the technical and financial analysis.

    Format the report with appropriate HTML structure.
    Maintain a professional yet engaging tone throughout, balancing analytical insights with accessibility for a general investor audience.
    Start the output with the Title, do no not start the output with the words "Here's a comprehensive technical analysis report....."
    """

    try:
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            temperature=0,
            system="You are a talkative, financial analyst. Provide your insight in a technical analysis report.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        if isinstance(message.content, list):
            ai_generated_content = ' '.join([item.text for item in message.content if hasattr(item, 'text')])
        else:
            ai_generated_content = message.content

       
        
        table_css = """
        <style>
            h3 {
                font-family: 'Anton', sans-serif;
                font-size: 30px;
                text-align: center;
                font-weight: bold;
                color: white;
                margin-top: 40px;
                margin-bottom: 20px;
            }
            table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                margin: 20px auto;
                border-radius: 10px;
                overflow: hidden;
            }
            th, td {
                border: 1px solid white;
                padding: 10px;
                text-align: left;
                font-family: 'Roboto', sans-serif;
            }
            th {
                background-color: #C1FF72;
                color: black;
                font-weight: bold;
            }
            tr:not(:first-child) td {
                background-color: #D9D9D9;
                color: black;
            }
            .financial-table td:first-child {
                background-color: #C1FF72;
                color: black;
            }
        </style>
        """

        technical_table = f""""
        <h3>Key Indicators</h3>
        <table>
            <tr>
                <th>Date</th>
                <th>Closing Price</th>
                <th><span data-tooltip="Relative Strength Index: A momentum indicator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions.">RSI</span></th>
                <th><span data-tooltip="50-day Simple Moving Average: The average closing price over the last 50 trading days.">50-day SMA</span></th>
                <th><span data-tooltip="200-day Simple Moving Average: The average closing price over the last 200 trading days.">200-day SMA</span></th>
            </tr>
            <tr>
                <td>{summarized_data['date']}</td>
                <td>{format_value(summarized_data['close_price'])}</td>
                <td>{format_value(summarized_data['RSI'], is_currency=False)}</td>
                <td>{format_value(summarized_data['SMA50'])}</td>
                <td>{format_value(summarized_data['SMA200'])}</td>
            </tr>
        </table>
        """

        bollinger_table = f"""
        <h3>Bollinger Bands</h3>
        <table>
            <tr>
                <th><span data-tooltip="Upper Bollinger Band: Two standard deviations above the 20-day SMA.">Upper Band</span></th>
                <th><span data-tooltip="Middle Bollinger Band: The 20-day Simple Moving Average.">Middle Band</span></th>
                <th><span data-tooltip="Lower Bollinger Band: Two standard deviations below the 20-day SMA.">Lower Band</span></th>
            </tr>
            <tr>
                <td>{format_value(summarized_data['UpperBand'])}</td>
                <td>{format_value(summarized_data['SMA20'])}</td>
                <td>{format_value(summarized_data['LowerBand'])}</td>
            </tr>
        </table>
        """

        financial_table = """
    <h3>Financial Analysis</h3>
    <table class="financial-table">
    """
        financial_table += f"""
        <tr><td><span data-tooltip="The total market value of a company's outstanding shares."><strong>Market Cap</strong></span></td><td class="convertible" data-value="{summarized_data['market_cap']}">{format_large_number(summarized_data['market_cap'])}</td></tr>
        <tr><td><span data-tooltip="The total amount of income generated by the sale of goods or services related to the company's primary operations."><strong>Total Revenue</strong></span></td><td class="convertible" data-value="{summarized_data['Total Revenue']}">{summarized_data['Total Revenue']}</td></tr>
        <tr><td><span data-tooltip="Revenue generated from a company's core business operations."><strong>Operating Revenue</strong></span></td><td class="convertible" data-value="{summarized_data['Operating Revenue']}">{summarized_data['Operating Revenue']}</td></tr>
        <tr><td><span data-tooltip="Earnings Per Share: The portion of a company's profit allocated to each outstanding share of common stock."><strong>Basic EPS</strong></span></td><td class="convertible" data-value="{summarized_data['Basic EPS']}">{format_value(summarized_data['Basic EPS'])}</td></tr>
        <tr><td><span data-tooltip="The total costs incurred by a company in its operations."><strong>Total Expenses</strong></span></td><td class="convertible" data-value="{summarized_data['Total Expenses']}">{summarized_data['Total Expenses']}</td></tr>
        <tr><td><span data-tooltip="The difference between the revenue generated from a bank's assets and the expenses associated with paying its liabilities."><strong>Net Interest Income</strong></span></td><td class="convertible" data-value="{summarized_data['Net Interest Income']}">{summarized_data['Net Interest Income']}</td></tr>
        <tr><td><span data-tooltip="The cost incurred by a company for borrowed funds."><strong>Interest Expense</strong></span></td><td class="convertible" data-value="{summarized_data['Interest Expense']}">{summarized_data['Interest Expense']}</td></tr>
        <tr><td><span data-tooltip="The amount earned by an entity's investments in interest-bearing assets."><strong>Interest Income</strong></span></td><td class="convertible" data-value="{summarized_data['Interest Income']}">{summarized_data['Interest Income']}</td></tr>
        <tr><td><span data-tooltip="The company's total earnings or profit."><strong>Net Income</strong></span></td><td class="convertible" data-value="{summarized_data['Net Income']}">{summarized_data['Net Income']}</td></tr>
        <tr><td><span data-tooltip="A company's economic performance adjusted for unusual, non-recurring or one-time influences."><strong>Normalized Income</strong></span></td><td class="convertible" data-value="{summarized_data['Normalized Income']}">{summarized_data['Normalized Income']}</td></tr>
        """
        financial_table += "</table>"
        
        report_content = f"""
    <link rel="stylesheet" href="{{ url_for('static', filename='css/tooltips.css') }}">
    <script src="{{ url_for('static', filename='js/tooltips.js') }}"></script>
    <link href="https://fonts.googleapis.com/css2?family=Anton:wght@300;400;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/css/styles.css">
    {table_css}

    {technical_table}
    {bollinger_table}
    {financial_table}
    
    <h3 style="color: white;">Technical Analysis</h3>
    <h4 style="color: white; text-align: center;">Simple Moving Averages (SMA)</h4>
    <div class="ai-analysis">
    <!-- AI-generated content about SMA -->
    </div>
    [PRICE_SMA_CHART]

    <h4 style="color: white; text-align: center;">Relative Strength Index (RSI)</h4>
    <div class="ai-analysis">
    <!-- AI-generated content about RSI -->
    </div>
    [RSI_CHART]

    <h4 style="color: white; text-align: center;">Bollinger Bands</h4>
    <div class="ai-analysis">
    <!-- AI-generated content about Bollinger Bands -->
    </div>
    [BOLLINGER_CHART]

<div class="ai-analysis">
{ai_generated_content}
</div>
"""
        return report_content
    except Exception as e:
        return f"<div class='error'>Error generating report: {str(e)}</div>"
    
