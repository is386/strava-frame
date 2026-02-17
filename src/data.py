import os
import logging
from dotenv import load_dotenv
from stravalib.client import Client
from stravalib.model import SummaryActivity
from datetime import datetime, timedelta
from typing import Tuple

logging.getLogger("stravalib").setLevel(logging.ERROR)


def meters_to_miles(meters: int) -> float:
    return meters / 1609.344


def seconds_to_timestamp(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{secs:02}"
    else:
        return f"{minutes:02}:{secs:02}"


def calculate_pace(meters: int, seconds: int) -> int:
    miles = meters_to_miles(meters)
    seconds_per_mile = seconds / miles
    return round(seconds_per_mile)


def calculate_streak(activities: list[SummaryActivity]) -> int:
    if not activities:
        return 0

    def week_start(date: datetime) -> datetime:
        # Strip tzinfo so everything is naive local-equivalent
        date = date.replace(tzinfo=None)
        return (date - timedelta(days=date.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    active_weeks = set(week_start(a.start_date) for a in activities)

    current_week = week_start(datetime.now())

    if current_week not in active_weeks:
        current_week -= timedelta(weeks=1)

    streak = 0
    while current_week in active_weeks:
        streak += 1
        current_week -= timedelta(weeks=1)  
    return streak


def get_all_strava_activities() -> list[SummaryActivity]:
    load_dotenv()
    STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
    STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
    STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

    client = Client()
    tokens = client.refresh_access_token(
        client_id=STRAVA_CLIENT_ID,
        client_secret=STRAVA_CLIENT_SECRET,
        refresh_token=STRAVA_REFRESH_TOKEN,
    )
    client.access_token = tokens["access_token"]

    return list(client.get_activities())


def get_yearly_strava_activities() -> list[SummaryActivity]:
    load_dotenv()
    STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
    STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
    STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

    client = Client()
    tokens = client.refresh_access_token(
        client_id=STRAVA_CLIENT_ID,
        client_secret=STRAVA_CLIENT_SECRET,
        refresh_token=STRAVA_REFRESH_TOKEN,
    )
    client.access_token = tokens["access_token"]

    now = datetime.now()
    jan_first = datetime(year=now.year, month=1, day=1)
    activities_iterator = client.get_activities(after=jan_first)
    return list(activities_iterator)


def parse_latest_activity(activities: list[SummaryActivity]) -> dict:
    if len(activities) == 0:
        return {
            "miles": 0,
            "time": "00:00",
            "pace": "00:00",
            "title": "Error",
            "date": "Zerouary 0",
        }

    latest_activity = activities[-1]
    return {
        "miles": round(meters_to_miles(latest_activity.distance), 2),
        "time": seconds_to_timestamp(latest_activity.moving_time),
        "pace": seconds_to_timestamp(
            calculate_pace(latest_activity.distance, latest_activity.moving_time)
        ),
        "title": latest_activity.name,
        "date": latest_activity.start_date.strftime("%B %-d"),
    }


def parse_yearly_data(
    activities: list[SummaryActivity],
) -> Tuple[int, float, float, list[float]]:
    total_activities = len(activities)
    total_mileage = 0.0
    mileage_per_month = [0.0] * 12

    for activity in activities:
        mileage = meters_to_miles(activity.distance)
        total_mileage += mileage
        mileage_per_month[activity.start_date.month - 1] += mileage

    mileage_per_month = [round(m, 2) for m in mileage_per_month]
    weeks_ytd = datetime.now().isocalendar().week

    return (
        total_activities,
        round(total_mileage, 2),
        round(total_mileage / weeks_ytd, 2),
        mileage_per_month,
    )
