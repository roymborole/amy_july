import logging
from flask import render_template
from financial_analysis import get_financial_data
from ai_analysis import get_analysis_report
from visualization import create_chart
from ticker_utils import get_ticker_from_name
from models import Subscription
from extensions import db
import postmarker
from postmarker.core import PostmarkClient
import time
import os

postmark = PostmarkClient(server_token=os.getenv('POSTMARK_SERVER_TOKEN'))

def generate_weekly_report(asset_name):
    try:
        ticker = get_ticker_from_name(asset_name)
        if ticker:
            raw_data = get_financial_data(ticker)
            if raw_data:
                report_content = get_analysis_report(raw_data, asset_name)
                
                charts = {
                    'price_sma': create_chart(raw_data['historical_data'], 'price_sma', asset_name),
                    'rsi': create_chart(raw_data['historical_data'], 'rsi', asset_name),
                    'bollinger': create_chart(raw_data['historical_data'], 'bollinger', asset_name)
                }
                
                for chart_type, chart_data in charts.items():
                    placeholder = f'[{chart_type.upper()}_CHART]'
                    chart_html = f'<img src="data:image/png;base64,{chart_data}" alt="{chart_type} chart" style="max-width: 100%; height: auto;">'
                    report_content = report_content.replace(placeholder, chart_html)
                
                return report_content
            else:
                return f"Unable to fetch data for {asset_name}."
        else:
            return f"Unable to find ticker for {asset_name}."
    except Exception as e:
        logging.error(f"Error generating weekly report for {asset_name}: {str(e)}")
        return f"Error generating weekly report for {asset_name}."

def send_weekly_report_email(email, asset_name, report_content):
    try:
        postmark.emails.send(
            From='reports@100-x.club', 
            To=email,
            Subject=f'Weekly Report for {asset_name}',
            HtmlBody=render_template('weekly_report_email.html', 
                                     asset_name=asset_name, 
                                     report_content=report_content)
        )
        logging.info(f"Weekly report for {asset_name} sent to {email}")
    except Exception as e:
        logging.error(f"Failed to send weekly report for {asset_name} to {email}. Error: {str(e)}")

def process_weekly_reports():
    logging.info("Starting to process weekly reports")
    subscriptions = Subscription.query.filter_by(confirmed=True).all()
    for subscription in subscriptions:
        report_content = generate_weekly_report(subscription.asset_name)
        send_weekly_report_email(subscription.email, subscription.asset_name, report_content)
    logging.info("Finished processing weekly reports")


def send_weekly_reports(app):
    with app.app_context():
        process_weekly_reports()