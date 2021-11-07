import os
import requests

class Refresh:
    def __init__(self):
        # Your Spotify Refresh Token Here
        self.refresh_token = os.environ['SPOTIFY_REFRESH_TOKEN']
        #? Encode to Base64 - "{YOUR_CLIENT_IF}:{YOUR_CLIENT_SECRET}"
        #? Encode it from: https://www.base64encode.org/
        self.client = "base64(client_id:client_secret)"

    def refresh(self):

        query  = 'https://accounts.spotify.com/api/token'
        # Requests a new access token
        response = requests.post(query, 
        data  = {
            "grant_type": "refresh_token",
            "refresh_token" : self.refresh_token
            },
        headers = {
            "Authorization" : "Basic " + self.client
        }
        )

        json = response.json()
        access_token = json['access_token']
        return access_token


