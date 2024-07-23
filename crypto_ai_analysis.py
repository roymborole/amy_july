# crypto_ai_analysis.py
from config import anthropic_client, json

def format_value(value, is_currency=True, decimals=2):
    if value is None:
        return 'N/A'
    if is_currency:
        return f"${value:,.{decimals}f}" if isinstance(value, (int, float)) else value
    return f"{value:.{decimals}f}" if isinstance(value, (int, float)) else value

def get_crypto_analysis_report(raw_data, crypto_name):
    # Prepare a summarized version of the raw_data
    summarized_data = {
        'crypto_name': crypto_name,
        'open_price': raw_data.get('Open'),
        'high_price': raw_data.get('High'),
        'low_price': raw_data.get('Low'),
        'close_price': raw_data.get('Close'),
        'volume': raw_data.get('Volume'),
        'SMA50': raw_data.get('SMA50'),
        'SMA200': raw_data.get('SMA200'),
        'EMA12': raw_data.get('EMA12'),
        'EMA26': raw_data.get('EMA26'),
        'RSI': raw_data.get('RSI'),
        'UpperBand': raw_data.get('UpperBand'),
        'LowerBand': raw_data.get('LowerBand'),
        'MACD': raw_data.get('MACD'),
        'MACD_Signal': raw_data.get('MACD_Signal'),
        'OBV': raw_data.get('OBV'),
        'VWAP': raw_data.get('VWAP'),
        'ATR': raw_data.get('ATR'),
        'STDDEV': raw_data.get('STDDEV'),
        'date': raw_data.get('date'),
    }
    
    prompt = f"""
    Create a comprehensive technical analysis report for the cryptocurrency {crypto_name} based on the following summarized data:
    {json.dumps(summarized_data, indent=2)}

    Include the following sections:
    1. Overview: Introduce the cryptocurrency and provide a brief background.
    2. Price Analysis: Discuss the Open, High, Low, and Close prices.
    3. Volume Analysis: Analyze the trading volume and its implications.
    4. Technical Indicators:
       - Simple Moving Averages (50-day and 200-day)
       - Exponential Moving Averages (12-day and 26-day)
       - Relative Strength Index (RSI)
       - Bollinger Bands
       - MACD (Moving Average Convergence Divergence)
       - On-Balance Volume (OBV)
       - Volume Weighted Average Price (VWAP)
       - Average True Range (ATR)
       - Standard Deviation
    5. Market Sentiment: Provide insights on the overall market sentiment for this cryptocurrency.
    6. Comparative Analysis: Briefly compare this cryptocurrency's performance to major cryptocurrencies like Bitcoin and Ethereum.
    7. Summary: Synthesize insights from all indicators.
    8. Investment Outlook: Based on the technical analysis.

    Format the report with appropriate HTML structure.
    Maintain a professional yet engaging tone throughout, balancing analytical insights with accessibility for a general cryptocurrency investor audience.
    """

    try:
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            temperature=0,
            system="You are a cryptocurrency expert and technical analyst. Provide your insight in a technical analysis report for the given cryptocurrency.",
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

        price_table = f"""
        <table>
            <tr>
                <th>Indicator</th>
                <th>Value</th>
            </tr>
            <tr><td>Date</td><td>{raw_data['date']}</td></tr>
            <tr><td>Open</td><td>{format_value(raw_data['Open'])}</td></tr>
            <tr><td>High</td><td>{format_value(raw_data['High'])}</td></tr>
            <tr><td>Low</td><td>{format_value(raw_data['Low'])}</td></tr>
            <tr><td>Close</td><td>{format_value(raw_data['Close'])}</td></tr>
            <tr><td>Volume</td><td>{format_value(raw_data['Volume'], is_currency=False)}</td></tr>
        </table>
        """

        technical_table = f"""
        <table>
            <tr>
                <th>Indicator</th>
                <th>Value</th>
            </tr>
            <tr><td>SMA50</td><td>{format_value(raw_data['SMA50'])}</td></tr>
            <tr><td>SMA200</td><td>{format_value(raw_data['SMA200'])}</td></tr>
            <tr><td>EMA12</td><td>{format_value(raw_data['EMA12'])}</td></tr>
            <tr><td>EMA26</td><td>{format_value(raw_data['EMA26'])}</td></tr>
            <tr><td>RSI</td><td>{format_value(raw_data['RSI'], is_currency=False)}</td></tr>
            <tr><td>Upper Bollinger Band</td><td>{format_value(raw_data['UpperBand'])}</td></tr>
            <tr><td>Lower Bollinger Band</td><td>{format_value(raw_data['LowerBand'])}</td></tr>
            <tr><td>MACD</td><td>{format_value(raw_data['MACD'], is_currency=False)}</td></tr>
            <tr><td>MACD Signal</td><td>{format_value(raw_data['MACD_Signal'], is_currency=False)}</td></tr>
            <tr><td>OBV</td><td>{format_value(raw_data['OBV'], is_currency=False)}</td></tr>
            <tr><td>VWAP</td><td>{format_value(raw_data['VWAP'])}</td></tr>
            <tr><td>ATR</td><td>{format_value(raw_data['ATR'])}</td></tr>
            <tr><td>Standard Deviation</td><td>{format_value(raw_data['STDDEV'], is_currency=False)}</td></tr>
        </table>
        """

        report_content = f"""
        {table_css}
        <h1>Cryptocurrency Analysis Report for {crypto_name}</h1>
        
        <h2>Price and Volume Data</h2>
        {price_table}
        
        <h2>Technical Indicators</h2>
        {technical_table}
        
        <h2>Analysis</h2>
        <div class="ai-analysis">
        {ai_generated_content}
        </div>

        <h2>Charts</h2>
        <h3>Price and Moving Averages</h3>
        [PRICE_SMA_CHART]

        <h3>Relative Strength Index (RSI)</h3>
        [RSI_CHART]

        <h3>Bollinger Bands</h3>
        [BOLLINGER_CHART]
        """
        return report_content
    except Exception as e:
        return f"<div class='error'>Error generating cryptocurrency report: {str(e)}</div>"