# image-processing
To automatically get the last hour of metadata, first generate a refresh token by running generate_refresh_tok and authorize it@stargazer-farm.com. After that the script will use the refresh token.
My understanding is that this approach is needed since google photos does not support service accounts.

# Generate kml overlays from google shared albums
I wasn't able to download any images that included gps info via the api even though their documentation indicates if your camera put the gps coordinates on, one should have access. I am given a message that gps location put on by a camera cannot be overwritten so I think Google Photos just does not give gps info. It is possible to cownload albums with gps locatin if done manually from https://takeout.google.com/.