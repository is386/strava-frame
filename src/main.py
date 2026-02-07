import os
from dotenv import load_dotenv
from stravalib.client import Client
from datetime import datetime

load_dotenv()

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

client = Client()

tokens = client.refresh_access_token(
    client_id=STRAVA_CLIENT_ID,
    client_secret=STRAVA_CLIENT_SECRET,
    refresh_token=STRAVA_REFRESH_TOKEN
)
client.access_token = tokens['access_token']

now = datetime.now()
jan_first = datetime(year=now.year, month=1, day=1)

activities_iterator = client.get_activities(after=jan_first)
activities = list(activities_iterator)
