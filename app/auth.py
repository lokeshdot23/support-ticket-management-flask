from app.config import Config
from google_auth_oauthlib.flow import Flow
from flask import Blueprint, redirect, request, session, jsonify
import os
import requests
# Local development only.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


auth = Blueprint("auth", __name__, url_prefix="/api/auth")


SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]


REDIRECT_URI = "http://127.0.0.1:5000/api/auth/google/callback"


def create_google_flow(**kwargs):

    return Flow.from_client_config(
        {
            "web": {
                "client_id": Config.GOOGLE_CLIENT_ID,
                "client_secret": Config.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [
                    REDIRECT_URI
                ]
            }
        },
        scopes=SCOPES,
        **kwargs
    )


@auth.route("/google")
def google_login():

    flow = create_google_flow()

    flow.redirect_uri = REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )

    # Save BOTH values because the callback is a new request.
    session["oauth_state"] = state
    session["oauth_code_verifier"] = flow.code_verifier

    return redirect(authorization_url)


@auth.route("/google/callback")
def google_callback():

    state = session.get("oauth_state")
    code_verifier = session.get("oauth_code_verifier")

    if not state:
        return jsonify({
            "error": "OAuth state missing"
        }), 400

    if not code_verifier:
        return jsonify({
            "error": "OAuth code verifier missing"
        }), 400

    flow = create_google_flow(
        state=state,
        code_verifier=code_verifier
    )

    flow.redirect_uri = REDIRECT_URI

    flow.fetch_token(
        authorization_response=request.url
    )

    credentials = flow.credentials

    # Get user information from Google
    response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={
            "Authorization": f"Bearer {credentials.token}"
        }
    )

    if response.status_code != 200:
        return jsonify({
            "error": "Failed to get Google user information"
        }), 400

    google_user = response.json()

    # Remove temporary OAuth data
    session.pop("oauth_state", None)
    session.pop("oauth_code_verifier", None)

    return jsonify({
        "message": "Google authentication successful",
        "google_user": google_user
    })
