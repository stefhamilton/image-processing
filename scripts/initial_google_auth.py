import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

admin_creds = "/Users/stefanhamilton/dev/image-processing/scripts/credentials_google_admin.json"

# Define the required scopes
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]

# Start the OAuth 2.0 flow
flow = InstalledAppFlow.from_client_secrets_file(
    client_secrets_file=admin_creds,
    scopes=SCOPES,
    redirect_uri="urn:ietf:wg:oauth:2.0:oob",
)
credentials = flow.run_local_server(port=58242)

# Save the credentials to a file for future use
credential_file = "credentials_admin.json"
with open(credential_file, "w") as f:
    json.dump(
        {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "token_uri": credentials.token_uri,
            "scopes": credentials.scopes,
        },
        f,
    )
