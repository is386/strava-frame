import logging
import re
from config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
from stravalib.client import Client
from stravalib.model import SummaryActivity
from datetime import datetime, timedelta
from typing import Tuple, TypedDict

logging.getLogger("stravalib").setLevel(logging.ERROR)


class LatestActivity(TypedDict):
    miles: float
    time: str
    pace: str
    title: str
    date: datetime
    medal: str | None


METERS_PER_MILE = 1609.34
streak_cache = -1
latest_activity_cache: LatestActivity = {}
latest_activity_cache


def format_effort_name(name: str) -> str:
    name = name.strip()

    if name == "Half-Marathon":
        return "13.1mi"
    if name == "Marathon":
        return "26.2mi"

    if re.match(r"^\d+m$", name):
        return name

    if re.match(r"^\d+K$", name):
        return name

    match = re.match(r"^(\d+)\s+miles?$", name, re.IGNORECASE)
    if match:
        return f"{match.group(1)}mi"

    return name


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
    miles = meters_to_miles(meters)
    if miles == 0:
        return 0
    seconds_per_mile = seconds / miles
    return round(seconds_per_mile)


def week_start(date: datetime) -> datetime:
    if date.tzinfo is not None:
        date = date.replace(tzinfo=None)
    return (date - timedelta(days=date.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )


def streak_cache_is_stale() -> bool:
    date = latest_activity_cache.get("date")
    if date is None:
        return False
    previous_week = week_start(datetime.now()) - timedelta(weeks=1)
    return week_start(date) < previous_week


def calculate_streak(activities: list[SummaryActivity]) -> int:
    if not activities:
        return 0

    active_weeks = set(week_start(a.start_date_local) for a in activities)
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


def get_pr(activity: SummaryActivity) -> str | None:
    if not activity.pr_count:
        return None
    detailed = get_strava_client().get_activity(activity.id)
    gold_efforts = [e for e in (detailed.best_efforts or []) if e.pr_rank == 1]
    if not gold_efforts:
        return None
    best = max(gold_efforts, key=lambda e: e.distance or 0)
    return format_effort_name(best.name)


def parse_latest_activity(activities: list[SummaryActivity]) -> LatestActivity:
    global new_activity_exists, latest_activity_cache

    if not activities:
        latest_activity_cache = {
            "miles": 0,
            "time": "00:00",
            "pace": "00:00",
            "title": "No Activity",
            "date": datetime.now(),
            "medal": None,
        }
        return latest_activity_cache

    activity = activities[-1]

    new_activity_exists = activity.id != latest_activity_cache.get("id")
    if not new_activity_exists:
        return latest_activity_cache

    distance = activity.distance or 0
    moving_time = activity.moving_time or 0
    miles = meters_to_miles(distance)
    pace = calculate_pace(distance, moving_time)

    latest_activity_cache = {
        "id": activity.id,
        "miles": round(miles, 2),
        "time": seconds_to_timestamp(moving_time),
        "pace": seconds_to_timestamp(pace) if pace > 0 else "00:00",
        "title": activity.name,
        "date": activity.start_date_local,
        "pr": get_pr(activity),
    }
    return latest_activity_cache


def parse_yearly_data(
    activities: list[SummaryActivity],
) -> Tuple[int, float, float, list[float]]:
    total_miles = 0.0
    miles_per_month = [0.0] * 12

    for activity in activities:
        miles = meters_to_miles(activity.distance or 0)
        total_miles += miles
        miles_per_month[activity.start_date_local.month - 1] += miles

    miles_per_month = [round(m, 2) for m in miles_per_month]
    weeks_ytd = max(1, datetime.now().isocalendar().week)

    return (
        len(activities),
        round(total_miles, 2),
        round(total_miles / weeks_ytd, 2),
        miles_per_month,
    )


def refresh_activities() -> Tuple[int, float, float, list[float], LatestActivity, int]:
    global streak_cache, new_activity_exists

    activities = get_ytd_activities()

    latest_activity = parse_latest_activity(activities)
    total_activities, total_miles, avg_weekly_miles, miles_per_month = (
        parse_yearly_data(activities)
    )

    if new_activity_exists:
        new_activity_exists = False
        streak_cache = calculate_streak(get_all_activities())
    elif streak_cache_is_stale():
        streak_cache = 0

    return (
        total_activities,
        total_miles,
        avg_weekly_miles,
        list(miles_per_month),
        latest_activity,
        streak_cache,
    )
