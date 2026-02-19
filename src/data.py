import logging
from config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
from stravalib.client import Client
from stravalib.model import SummaryActivity
from datetime import datetime, timedelta
from typing import Tuple
from requests.exceptions import RequestException

logging.getLogger("stravalib").setLevel(logging.ERROR)

METERS_PER_MILE = 1609.344

activities_cache = []
streak_cache = -1


def get_strava_client() -> Client:
    client = Client()
    tokens = client.refresh_access_token(
        client_id=STRAVA_CLIENT_ID,
        client_secret=STRAVA_CLIENT_SECRET,
        refresh_token=STRAVA_REFRESH_TOKEN,
    )
    client.access_token = tokens["access_token"]
    return client


def meters_to_miles(meters: float) -> float:
    return meters / METERS_PER_MILE


def seconds_to_timestamp(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{secs:02}"
    return f"{minutes:02}:{secs:02}"


def calculate_pace(meters: float, seconds: int) -> int:
    seconds_per_mile = seconds / meters_to_miles(meters)
    return round(seconds_per_mile)


def calculate_streak(activities: list[SummaryActivity]) -> int:
    if not activities:
        return 0

    def week_start(date: datetime) -> datetime:
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


def get_all_activities() -> list[SummaryActivity]:
    return list(get_strava_client().get_activities())


def get_ytd_activities() -> list[SummaryActivity]:
    jan_first = datetime(year=datetime.now().year, month=1, day=1)
    return list(get_strava_client().get_activities(after=jan_first))


def parse_latest_activity(activities: list[SummaryActivity]) -> dict:
    if not activities:
        return {
            "miles": 0,
            "time": "00:00",
            "pace": "00:00",
            "title": "Error",
            "date": "Zerouary 0",
        }

    activity = activities[-1]
    return {
        "miles": round(meters_to_miles(activity.distance), 2),
        "time": seconds_to_timestamp(activity.moving_time),
        "pace": seconds_to_timestamp(
            calculate_pace(activity.distance, activity.moving_time)
        ),
        "title": activity.name,
        "date": activity.start_date.strftime("%B %-d"),
    }


def parse_yearly_data(
    activities: list[SummaryActivity],
) -> Tuple[int, float, float, list[float]]:
    total_miles = 0.0
    miles_per_month = [0.0] * 12

    for activity in activities:
        miles = meters_to_miles(activity.distance)
        total_miles += miles
        miles_per_month[activity.start_date.month - 1] += miles

    miles_per_month = [round(m, 2) for m in miles_per_month]
    weeks_ytd = datetime.now().isocalendar().week

    return (
        len(activities),
        round(total_miles, 2),
        round(total_miles / weeks_ytd, 2),
        miles_per_month,
    )


def refresh_streak():
    global streak_cache
    try:
        streak_cache = calculate_streak(get_all_activities())
    except (RuntimeError, RequestException) as e:
        print(f"Failed to fetch streak: {e}")


def refresh_activities() -> Tuple[int, float, float, list[float], dict]:
    global activities_cache
    try:
        activities_cache = get_ytd_activities()
    except (RuntimeError, RequestException) as e:
        print(e)
    latest_activity = parse_latest_activity(activities_cache)
    total_activities, total_miles, avg_weekly_miles, miles_per_month = (
        parse_yearly_data(activities_cache)
    )
    return (
        total_activities,
        total_miles,
        avg_weekly_miles,
        list(miles_per_month),
        latest_activity,
    )
