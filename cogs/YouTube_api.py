import os
import pickle

from dotenv import load_dotenv

import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
import googleapiclient.discovery

from discord.ext import commands

class youtube_api():
  """
  Contains commands to call the Youtube API
  """

  def oauth2():
    """
    Calls the Youtube API using OAuth 2.0 
    Requirements:
      token.pickle - stores login credentials (will be created if not present)
      client_secrets.json - OAuth 2.0 client ID (Will fail if not present)
    """
    api_service_name = "youtube"
    api_version = "v3"
    credentials = None
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    # token.pickle stores the user's credentials from previously successful logins
    if os.path.exists('token.pickle'):
        print('Loading Credentials From File...')
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file('client_secrets.json', scopes=scopes)
            flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)

    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)


  def key():
    """
    Calls the Youtube API using a key
    Requirements:
      .env - containing a API key with the prefix YT_API_KEY
    """
    load_dotenv()
    api_service_name = "youtube"
    api_version = "v3"
    api_key = os.getenv("YT_API_KEY")

    return googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)


  def playlist(playlistId: str):
    """
    Responds with a list of items in the playlist
    Parameters:
      playlistId: str - the playlist's ID
    """
    youtube = youtube_api.oauth2()
    
    request = youtube.playlistItems().list(
      part="snippet", playlistId=playlistId
      )

    return request.execute()

  def add_video(playlistId: str, videoId: str):
    """
    Adds a new video to a playlist
    Parameters:
      playlistId: str - the playlist's ID
      videoId: str - the video's ID
    """
    youtube = youtube_api.oauth2()

    request = youtube.playlistItems().insert(
            part="snippet",
            body={
              "snippet": {
                "playlistId": playlistId,
                "resourceId": {
                  "kind": "youtube#video",
                  "videoId": videoId
                }
              }
            }
        )

    return request.execute()

default_playlist = "PLXfw-OhAIheRIwSuBzbva5nzRxCMftKz1"
default_song = "CPhXKak_bHw"

if __name__=="__main__":
  print(youtube_api.add_video(default_playlist, default_song))