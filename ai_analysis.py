from config import anthropic_client
import json

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
    # Prepare a summarized version of the raw_data
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
    1. Overview: Introduce the stock and provide a brief background on the company.
    2. Technical Analysis:
       - Simple Moving Averages (50-day and 200-day)
       - Relative Strength Index (RSI)
       - Bollinger Bands
    3. Financial Analysis: Discuss the provided financial indicators: Market Cap, Operating Revenue, Total Expenses, Interest Expense, Interest Income, Basic EPS, Net Income
    4. Summary: Synthesize insights from all indicators.
    5. Investment Outlook: Based on the technical and financial analysis.

    Format the report with appropriate HTML structure.
    Maintain a professional yet engaging tone throughout, balancing analytical insights with accessibility for a general investor audience.
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

        # Add CSS for tables
        table_css = """
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
                font-weight: bold;
            }
        </style>
        """

        # Create HTML tables
        technical_table = f"""
        <table>
            <tr>
                <th>Date</th>
                <th>Closing Price</th>
                <th>RSI</th>
                <th>50-day SMA</th>
                <th>200-day SMA</th>
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
        <table>
            <tr>
                <th>Upper Band</th>
                <th>Middle Band</th>
                <th>Lower Band</th>
            </tr>
            <tr>
                <td>{format_value(summarized_data['UpperBand'])}</td>
                <td>{format_value(summarized_data['SMA20'])}</td>
                <td>{format_value(summarized_data['LowerBand'])}</td>
            </tr>
        </table>
        """

        financial_table = f"""
        <table>
            <tr><th>Indicator</th><th>Value</th></tr>
            <tr><td>Market Cap</td><td>{format_large_number(summarized_data['market_cap'])}</td></tr>
            <tr><td>Total Revenue</td><td>{summarized_data['Total Revenue']}</td></tr>
            <tr><td>Operating Revenue</td><td>{summarized_data['Operating Revenue']}</td></tr>
            <tr><td>Basic EPS</td><td>{format_value(summarized_data['Basic EPS'])}</td></tr>
            <tr><td>Total Expenses</td><td>{summarized_data['Total Expenses']}</td></tr>
            <tr><td>Net Interest Income</td><td>{summarized_data['Net Interest Income']}</td></tr>
            <tr><td>Interest Expense</td><td>{summarized_data['Interest Expense']}</td></tr>
            <tr><td>Interest Income</td><td>{summarized_data['Interest Income']}</td></tr>
            <tr><td>Net Income</td><td>{summarized_data['Net Income']}</td></tr>
            <tr><td>Normalized Income</td><td>{summarized_data['Normalized Income']}</td></tr>
        </table>
        """

        report_content = f"""
        {table_css}
        
        
        <h2>Key Indicators</h2>
        {technical_table}

        <h2>Bollinger Bands</h3>
        {bollinger_table}
        
        <h2>Financial Analysis</h2>
        {financial_table}
        <div class="ai-analysis">
        <!-- AI-generated content about Financial Analysis -->
        </div>
        
        <h2>Technical Analysis</h2>
        <h3>Simple Moving Averages (SMA)</h3>
        <div class="ai-analysis">
        <!-- AI-generated content about SMA -->
        </div>
        [PRICE_SMA_CHART]

        <h3>Relative Strength Index (RSI)</h3>
        <div class="ai-analysis">
        <!-- AI-generated content about RSI -->
        </div>
        [RSI_CHART]

        <h3>Bollinger Bands</h3>
        <div class="ai-analysis">
        <!-- AI-generated content about Bollinger Bands -->
        </div>
        [BOLLINGER_CHART]

          <h2>Overview</h2>
        <div class="ai-analysis">
        {ai_generated_content}
        </div>
        """

        return report_content
    except Exception as e:
        return f"<div class='error'>Error generating report: {str(e)}</div>"
    
