from datetime import datetime
import mixpanel
from flask import request, current_app
import os
from dotenv import load_dotenv

load_dotenv()

mixpanel_client = None

def init_mixpanel(app):
    global mixpanel_client
    project_token = app.config.get('MIXPANEL_PROJECT_TOKEN') or os.getenv('MIXPANEL_PROJECT_TOKEN')
    if project_token:
        mixpanel_client = mixpanel.Mixpanel(project_token)
    else:
        app.logger.warning("Mixpanel project token not found. Mixpanel tracking will be disabled.")

def send_to_mixpanel(user, event_name, event_properties=None):
    if not mixpanel_client:
        current_app.logger.warning("Mixpanel client not initialized. Skipping event tracking.")
        return

    if event_properties is None:
        event_properties = {}

    user_id = user.id if user and user.is_authenticated else 'anonymous'
    
    # Add common properties
    event_properties.update({
        'ip': request.remote_addr,
        'user_agent': request.user_agent.string,
        # Add any other common properties you want to track
    })

    # Send the event to Mixpanel
    try:
        mixpanel_client.track(user_id, event_name, event_properties)
        current_app.logger.info(f"Sent event to Mixpanel: {event_name}")
    except Exception as e:
        current_app.logger.error(f"Failed to send event to Mixpanel: {str(e)}")

def track_event(user, event_name, properties=None):
    if properties is None:
        properties = {}

    properties['timestamp'] = datetime.utcnow().isoformat()
    
    send_to_mixpanel(user, event_name, properties)

def track_macro_analysis(user, ticker):
    track_event(user, 'generate_macro_analysis', {'ticker': ticker})

def track_generate_macro(user):
    track_event(user, 'generate_macro')

def track_crypto_comparison(user, crypto1, crypto2):
    track_event(user, 'crypto_comparison', {'crypto1': crypto1, 'crypto2': crypto2})

def track_compare_assets(user, asset1, asset2):
    track_event(user, 'compare_assets', {'asset1': asset1, 'asset2': asset2})

def track_loading_news(user, name_or_ticker):
    track_event(user, 'loading_news', {'name_or_ticker': name_or_ticker})

def track_generate_report(user):
    track_event(user, 'generate_report')

def track_display_comparison(user, asset1, asset2):
    track_event(user, 'display_comparison', {'asset1': asset1, 'asset2': asset2})

def track_check_report(user, name_or_ticker):
    track_event(user, 'check_report', {'name_or_ticker': name_or_ticker})

def track_loading(user, name_or_ticker):
    track_event(user, 'loading', {'name_or_ticker': name_or_ticker})