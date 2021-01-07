import os
import pickle
import re
from datetime import timedelta


from dotenv import load_dotenv

import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
import googleapiclient.discovery

from discord.ext import commands

Playlists = {
    "chill - baka brigade" : "PLXfw-OhAIheTakyvLpf50BN9xQqhhJiN7",
    "vibe" : "PLXfw-OhAIheRIwSuBzbva5nzRxCMftKz1",
    "Programming_music" : "PLXfw-OhAIheQt4cVnX5MpPjOBy4-pXVs7",
    "EDM": "PLXfw-OhAIheShH-C1eiLmOy7ARW3iMbSB",
    "Folk": "PLXfw-OhAIheRTx637DsQ8xKvNMq8h9TU1",
    "Bass boosted": "PLXfw-OhAIheR1vbjC3x7vEPeTIYhYu5RP"
  }

class youtube_api(commands.Cog):
  """
  Contains commands to call the Youtube API
  """

  api_service_name = "youtube"
  api_version = "v3"

  def oauth2():
    """
    Calls the Youtube API using OAuth 2.0 
    Requirements:
      token.pickle - stores login credentials (will be created if not present)
      client_secrets.json - OAuth 2.0 client ID (Will fail if not present)
    """
    credentials = None
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    #for debug mode
    '''
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file('client_secrets.json', scopes=scopes)
    flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
    credentials = flow.credentials
    print(credentials.to_json())
    return googleapiclient.discovery.build(youtube_api.api_service_name, youtube_api.api_version, credentials=credentials)
    '''
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

    return googleapiclient.discovery.build(youtube_api.api_service_name, youtube_api.api_version, credentials=credentials)
    

  def key():
    """
    Calls the Youtube API using a key
    Requirements:
      .env - containing a API key with the prefix YT_API_KEY
    """
    load_dotenv()
    api_key = os.getenv("YT_API_KEY")

    return googleapiclient.discovery.build(youtube_api.api_service_name, youtube_api.api_version, developerKey=api_key)


  def playlist_items(playlistId: str):
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

  def remove_video(playlistId: str, videoId: str):
    """
    Removes a video from a playlist
    Parameters:
      playlistId: str - the playlist's ID
      videoId: str - the video's ID
    """
    youtube = youtube_api.oauth2()
    long_video_id = youtube_api.find_video_from_playlist(playlistId=playlistId, videoId=videoId)['id']

    if long_video_id == None:
      return "No Video found"

    request = youtube.playlistItems().delete(id=long_video_id)

    return request.execute()

  def find_video_from_playlist(playlistId: str, videoId: str):
    """
    Returns json about a video from a playlist
    Parameters:
      playlistId: str - the playlist's ID
      videoId: str - the video's ID
    """
    playlist = youtube_api.playlist_items(playlistId)
    for item in playlist["items"]:
      if item["snippet"]["resourceId"]["videoId"] == videoId:
        return item
    return None 

  def find_video(videoId: str):
    """
    Returns json on a video
    Parameters:
      videoId: str - the videos ID
    """
    youtube = youtube_api.key()
    request = youtube.videos().list(
        part="snippet,contentDetails",
        id=videoId
    )
    return request.execute()

  def find_playlist(playlistId: str):
    """
    Returns a json object with the playlists information
    Parameters:
      playlistId: str - the playlist's ID
    """
    youtube = youtube_api.oauth2()
    request = youtube.playlists().list(
        part="snippet",
        id=playlistId
    )
    return request.execute()

  def get_local_playlist_key(index: int):
    """
    Returns a playlist key
    Parameters:
      index: int - index of playlist key
    """
    return list(Playlists)[index]

  def get_playlist_length(playlistId: str):
    """
    Returns the playlist lenght
    Parameters:
      playlistId: str - the playlist's ID
    """
    youtube = youtube_api.key()
    hours_pattern = re.compile(r'(\d+)H')
    minutes_pattern = re.compile(r'(\d+)M')
    seconds_pattern = re.compile(r'(\d+)S')

    total_seconds = 0


    nextPageToken = None
    while True:
        pl_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId="PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU",
            maxResults=100,
            pageToken=nextPageToken
        )

        pl_response = pl_request.execute()

        vid_ids = []
        for item in pl_response['items']:
            vid_ids.append(item['contentDetails']['videoId'])

        vid_request = youtube.videos().list(
            part="contentDetails",
            id=','.join(vid_ids)
        )

        vid_response = vid_request.execute()

        for item in vid_response['items']:
            duration = item['contentDetails']['duration']

            hours = hours_pattern.search(duration)
            minutes = minutes_pattern.search(duration)
            seconds = seconds_pattern.search(duration)

            hours = int(hours.group(1)) if hours else 0
            minutes = int(minutes.group(1)) if minutes else 0
            seconds = int(seconds.group(1)) if seconds else 0

            video_seconds = timedelta(
                hours=hours,
                minutes=minutes,
                seconds=seconds
            ).total_seconds()

            total_seconds += video_seconds

        nextPageToken = pl_response.get('nextPageToken')

        if not nextPageToken:
            break

    total_seconds = int(total_seconds)

    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return f'{hours}:{minutes}:{seconds}'
  
"""
default_playlist = Playlists['chill_baka_brigade']
default_song = "CPhXKak_bHw"

if __name__=="__main__":
  #print(youtube_api.remove_video(default_playlist, default_song))
  print(youtube_api.remove_video(playlistId=default_playlist, videoId=default_song))
"""
