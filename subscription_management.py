from flask import url_for
from models import PendingSubscription, Subscription
from extensions import db
from config import postmark
import secrets
import logging
from sqlalchemy.exc import IntegrityError

def create_subscription(email, asset_name):
    existing_sub = Subscription.query.filter_by(email=email, asset_name=asset_name).first()
    if existing_sub and existing_sub.confirmed:
        return "already_subscribed"

    confirmation_token = secrets.token_urlsafe(32)
    pending_sub = PendingSubscription(email=email, asset_name=asset_name, confirmation_token=confirmation_token)
    db.session.add(pending_sub)
    db.session.commit()
    
    send_confirmation_email(email, asset_name, confirmation_token)
    return "confirmation_sent"

def send_confirmation_email(email, asset_name, confirmation_token):
    confirmation_link = url_for('confirm_subscription_route', token=confirmation_token, _external=True)
    try:
        postmark.emails.send(
            From='info@100-x.club',
            To=email,
            Subject='Confirm your subscription',
            HtmlBody=f'''
            <html>
            <body>
                <h2>Confirm your subscription</h2>
                <p>Please confirm your subscription to weekly reports for {asset_name} by clicking on this link:</p>
                <p><a href="{confirmation_link}">{confirmation_link}</a></p>
            </body>
            </html>
            ''',
            TextBody=f'Please confirm your subscription to weekly reports for {asset_name} by clicking on this link: {confirmation_link}'
        )
        logging.info(f"Confirmation email sent to {email} for {asset_name}")
    except Exception as e:
        logging.error(f"Failed to send confirmation email to {email} for {asset_name}. Error: {str(e)}")

def confirm_subscription(token):
    pending_sub = PendingSubscription.query.filter_by(confirmation_token=token).first()
    if pending_sub:
        try:
            existing_sub = Subscription.query.filter_by(email=pending_sub.email, asset_name=pending_sub.asset_name).first()
            
            if existing_sub:
                # If subscription exists, just update the confirmed status
                existing_sub.confirmed = True
            else:
                # If it doesn't exist, create a new subscription
                new_sub = Subscription(email=pending_sub.email, asset_name=pending_sub.asset_name, confirmed=True)
                db.session.add(new_sub)
            
            # Delete the pending subscription
            db.session.delete(pending_sub)
            db.session.commit()
            logging.info(f"Subscription confirmed for {pending_sub.email} - {pending_sub.asset_name}")
            return "subscription_confirmed"
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"Error confirming subscription: {str(e)}")
            return "error"
        except Exception as e:
            db.session.rollback()
            logging.error(f"Unexpected error confirming subscription: {str(e)}")
            return "error"
    return "invalid_token"

def get_active_subscriptions():
    return Subscription.query.filter_by(confirmed=True).all()

def unsubscribe(email, asset_name):
    subscription = Subscription.query.filter_by(email=email, asset_name=asset_name).first()
    if subscription:
        db.session.delete(subscription)
        db.session.commit()
        logging.info(f"Unsubscribed {email} from {asset_name}")
        return True
    return False

def get_user_subscriptions(email):
    return Subscription.query.filter_by(email=email, confirmed=True).all()