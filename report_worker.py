import json
from rabbitmq_config import get_rabbitmq_connection, get_channel
from financial_analysis import get_financial_data
from crypto_analysis import get_crypto_data, crypto_mapping
from ai_analysis import get_analysis_report
from crypto_ai_analysis import get_crypto_analysis_report
from visualization import create_chart
import time
from mixpanel import Mixpanel
from ticker_utils import get_ticker_from_name

mp_eu = Mixpanel("your_mixpanel_token")

def callback(ch, method, properties, body):
    data = json.loads(body)
    name_or_ticker = data['name_or_ticker']
    user_id = data['user_id']
    print(f"Received request for {name_or_ticker}")
    
    start_time = time.time()
    
    try:
        if name_or_ticker.lower() in crypto_mapping:
            raw_data = get_crypto_data(name_or_ticker)
            report_content = get_crypto_analysis_report(raw_data, raw_data['asset_name'])
            asset_type = 'Cryptocurrency'
        else:
            ticker = get_ticker_from_name(name_or_ticker)
            if ticker:
                raw_data = get_financial_data(ticker)
                report_content = get_analysis_report(raw_data, raw_data['asset_name'])
                asset_type = 'Stock'
            else:
                raise ValueError('Unable to find a matching stock or cryptocurrency.')

        if not raw_data:
            raise ValueError('Unable to fetch data for the given input.')

        if 'asset_name' not in raw_data:
            raw_data['asset_name'] = name_or_ticker.capitalize()

        charts = {
            'price_sma': create_chart(raw_data['historical_data'], 'price_sma', name_or_ticker),
            'rsi': create_chart(raw_data['historical_data'], 'rsi', name_or_ticker),
            'bollinger': create_chart(raw_data['historical_data'], 'bollinger', name_or_ticker)
        }
        raw_data['charts'] = charts

        for chart_type, chart_data in charts.items():
            placeholder = f'[{chart_type.upper()}_CHART]'
            chart_html = f'<img src="data:image/png;base64,{chart_data}" alt="{chart_type} chart" style="max-width: 100%; height: auto;">'
            report_content = report_content.replace(placeholder, chart_html)

        end_time = time.time()
        generation_time = end_time - start_time

        # Track report generation
        mp_eu.track(user_id, 'Report Generated', {
            'asset_name': raw_data['asset_name'],
            'asset_type': asset_type,
            'generation_time': generation_time
        })

        # Store the report in a database or file system
        # For now, we'll just print it
        print(f"Generated report for {name_or_ticker}")

    except Exception as e:
        print(f"Error generating report for {name_or_ticker}: {str(e)}")
        mp_eu.track(user_id, 'Report Generation Error', {
            'asset_name': name_or_ticker,
            'error_message': str(e)
        })

def start_worker():
    connection = get_rabbitmq_connection()
    channel = get_channel(connection)
    channel.queue_declare(queue='report_requests')
    channel.basic_consume(queue='report_requests', on_message_callback=callback, auto_ack=True)
    print('Worker is waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    start_worker()