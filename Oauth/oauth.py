# oauth2.py

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
import requests

import os

# Replace these with your actual OAuth credentials
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# OAuth2 Scheme
oauth2_scheme_google = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

async def google_oauth(code: str):
    """Authenticate user with Google OAuth"""
    token_url = "https://oauth2.googleapis.com/token"
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    # Exchange code for access token
    response = requests.post(
        token_url,
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": "YOUR_REDIRECT_URI",  # Replace with your redirect URI
            "grant_type": "authorization_code"
        },
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid Google authorization code.")
    
    token_data = response.json()
    access_token = token_data.get("access_token")

    # Fetch user info
    user_info_response = requests.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"})
    user_info = user_info_response.json()
    
    return user_info


async def facebook_oauth(access_token: str):
    """Authenticate user with Facebook OAuth"""
    user_info_url = f"https://graph.facebook.com/me?access_token={access_token}&fields=id,name,email"

    response = requests.get(user_info_url)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid Facebook access token.")
    
    user_info = response.json()
    return user_info