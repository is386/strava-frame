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
days_ytd = (now - jan_first).days + 1
weeks_ytd = days_ytd / 7

activities_iterator = client.get_activities(after=jan_first)
activities = list(activities_iterator)

latest_activity = {
  'miles': activities[-1].distance / 1609.344,
  'seconds': activities[-1].moving_time
}

total_activities = len(activities)
total_mileage = 0
mileage_per_month = [0] * 12

for activity in activities:
  mileage = activity.distance / 1609.344
  total_mileage += mileage
  mileage_per_month[activity.start_date.month-1] += mileage

print(total_activities, total_mileage, total_mileage / weeks_ytd, latest_activity, mileage_per_month)