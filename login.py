# login.py
from flask import Blueprint, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from flask_sqlalchemy import SQLAlchemy
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from models import db, User  # Import db and User from models.py

auth = Blueprint('auth', __name__)

google_bp = make_google_blueprint(
    client_id="your-client-id",
    client_secret="your-client-secret",
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", 
           "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_to="index"  
)

def init_auth(app):
    app.register_blueprint(auth)
    app.register_blueprint(google_bp, url_prefix="/login")
    # Remove the init_db(app) call from here

@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    try:
        resp = blueprint.session.get("/oauth2/v1/userinfo")
        if resp.ok:
            account_info = resp.json()
            email = account_info["email"]
            
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=email)
                db.session.add(user)
                db.session.commit()
            
            session['user_id'] = user.id
        
        return False
    except OAuth2Error as e:
        print(f"OAuth2Error: {str(e)}")
        return False

@auth.route('/login')
def login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return redirect(url_for("index"))

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

def get_db():
    return db