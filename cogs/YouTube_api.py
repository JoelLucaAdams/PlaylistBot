from dotenv import load_dotenv
import os
import pickle
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
import googleapiclient.discovery 

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

api_service_name = "youtube"
api_version = "v3"
# Used for api key only
'''
load_dotenv()
api_key = os.getenv("YT_API_KEY")
youtube = build(api_service_name, api_version, developerKey=api_key)
'''

credentials = None

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


youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)


"""request = youtube.playlistItems().list(
  part="snippet", playlistId="PLXfw-OhAIheQ8ZVi5E_ZAYDuw7hHscH5s"
)
"""
request = youtube.playlistItems().insert(
        part="snippet",
        body={
          "snippet": {
            "playlistId": "PLXfw-OhAIheQ8ZVi5E_ZAYDuw7hHscH5s",
            "position": 0,
            "resourceId": {
              "kind": "youtube#video",
              "videoId": "lekfZs1jJH0"
            }
          }
        }
    )

response = request.execute()

print(response)