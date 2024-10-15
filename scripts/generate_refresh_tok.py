import json
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

def get_refresh_token(client_secret_file, scopes):
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
    credentials = flow.run_local_server(port=0)
    return credentials.refresh_token

def store_refresh_token(refresh_token, refresh_token_file):
    with open(refresh_token_file, "w") as f:
        json.dump({"refresh_token": refresh_token}, f)

if __name__ == "__main__":
    SCOPES = [
        "https://www.googleapis.com/auth/photoslibrary.readonly",
        "https://www.googleapis.com/auth/bigquery",
        "openid",
    ]
    
    client_secret_file = os.getenv("CLIENT_SECRET_FILE")
    refresh_token_file = os.getenv("REFRESH_TOKEN_FILE")
    
    refresh_token = get_refresh_token(client_secret_file, SCOPES)
    store_refresh_token(refresh_token, refresh_token_file)
    print("Refresh token saved to", refresh_token_file)
