import json
from google_auth_oauthlib.flow import InstalledAppFlow

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
    
    client_secret_file = "/Users/stefanhamilton/dev/image-processing/scripts/credentials.json"
    refresh_token_file = "/Users/stefanhamilton/dev/image-processing/scripts/refresh_token.json"
    
    refresh_token = get_refresh_token(client_secret_file, SCOPES)
    store_refresh_token(refresh_token, refresh_token_file)
    print("Refresh token saved to", refresh_token_file)
