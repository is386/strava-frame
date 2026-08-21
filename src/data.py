import requests
from config import INTERVALS_API_KEY, INTERVALS_ATHLETE_ID, STREAK_CARRYOVER
from datetime import datetime, timedelta
from typing import TypedDict
from tenacity import retry, stop_after_attempt, wait_exponential
from collections import defaultdict


class LatestActivity(TypedDict):
    miles: float
    time: str
    pace: str
    title: str
    date: datetime


API_BASE = "https://intervals.icu/api/v1"
METERS_PER_MILE = 1609.34
RUN_TYPES = {"Run", "VirtualRun"}
CADENCE_MULTIPLIER = 2
HISTORY_DAYS = 365


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


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=2, max=32))
def fetch_runs(oldest: datetime, newest: datetime) -> list[dict]:
    response = requests.get(
        f"{API_BASE}/athlete/{INTERVALS_ATHLETE_ID}/activities",
        auth=("API_KEY", INTERVALS_API_KEY),
        params={
            "oldest": oldest.strftime("%Y-%m-%d"),
            "newest": newest.strftime("%Y-%m-%d"),
        },
        timeout=30,
    )
    response.raise_for_status()

    runs = []
    for activity in response.json():
        if activity.get("type") not in RUN_TYPES:
            continue
        activity["start_date_local"] = datetime.fromisoformat(
            activity["start_date_local"]
        )
        runs.append(activity)

    runs.sort(key=lambda activity: activity["start_date_local"])
    return runs


def calculate_streak(runs: list[dict], window_start: datetime) -> int:
    if not runs:
        return 0

    active_weeks = set(week_start(run["start_date_local"]) for run in runs)
    current_week = week_start(datetime.now())

    if current_week not in active_weeks:
        current_week -= timedelta(weeks=1)

    streak = 0
    while current_week in active_weeks:
        streak += 1
        current_week -= timedelta(weeks=1)

    if streak and current_week < week_start(window_start):
        streak += STREAK_CARRYOVER

    return streak


def parse_latest_activity(runs: list[dict]) -> LatestActivity:
    if not runs:
        return {
            "miles": 0,
            "time": "00:00",
            "pace": "00:00",
            "title": "No Activity",
            "date": datetime.now(),
        }

    activity = runs[-1]
    distance = activity.get("distance") or 0
    moving_time = activity.get("moving_time") or 0
    pace = calculate_pace(distance, moving_time)

    return {
        "miles": round(meters_to_miles(distance), 2),
        "time": seconds_to_timestamp(moving_time),
        "pace": seconds_to_timestamp(pace) if pace > 0 else "00:00",
        "title": activity.get("name") or "Untitled",
        "date": activity["start_date_local"],
    }


def parse_yearly_data(
    runs: list[dict],
) -> tuple[
    int, float, float, list[float], list[float], list[float], list[float], list[float]
]:
    total_miles = 0.0
    miles_per_month = [0.0] * 12
    pace_trend = []
    cadence_trend = []
    heart_rate_trend = []

    weekly_miles_map = defaultdict(float)

    for activity in runs:
        distance = activity.get("distance") or 0
        moving_time = activity.get("moving_time") or 0
        start_date = activity["start_date_local"]

        miles = meters_to_miles(distance)
        total_miles += miles

        # Monthly
        miles_per_month[start_date.month - 1] += miles

        # Weekly (ISO year + week prevents collisions across years)
        iso_year, iso_week, _ = start_date.isocalendar()
        weekly_miles_map[(iso_year, iso_week)] += miles

        # Trends
        if distance and moving_time:
            pace_trend.append(calculate_pace(distance, moving_time))

        cadence = activity.get("average_cadence")
        if cadence:
            cadence_trend.append(cadence * CADENCE_MULTIPLIER)

        heart_rate = activity.get("average_heartrate")
        if heart_rate and heart_rate > 120:
            heart_rate_trend.append(heart_rate)

    # Final formatting
    miles_per_month = [round(m, 2) for m in miles_per_month]

    # Sort weeks chronologically and extract values
    weekly_mileage_trend = [
        round(weekly_miles_map[k], 2) for k in sorted(weekly_miles_map)
    ]
    weeks_ytd = max(1, datetime.now().isocalendar().week)

    return (
        len(runs),
        round(total_miles, 2),
        round(total_miles / weeks_ytd, 2),
        miles_per_month,
        pace_trend,
        weekly_mileage_trend,
        cadence_trend,
        heart_rate_trend,
    )


def refresh_activities() -> tuple[
    int,
    float,
    float,
    list[float],
    list[float],
    list[float],
    list[float],
    list[float],
    LatestActivity,
    int,
]:
    now = datetime.now()
    window_start = now - timedelta(days=HISTORY_DAYS)

    all_runs = fetch_runs(window_start, now)
    ytd_runs = [run for run in all_runs if run["start_date_local"].year == now.year]

    latest_activity = parse_latest_activity(ytd_runs)
    (
        total_activities,
        total_miles,
        avg_weekly_miles,
        miles_per_month,
        pace_trend,
        weekly_mileage_trend,
        cadence_trend,
        heart_rate_trend,
    ) = parse_yearly_data(ytd_runs)

    streak = calculate_streak(all_runs, window_start)

    return (
        total_activities,
        total_miles,
        avg_weekly_miles,
        list(miles_per_month),
        pace_trend,
        weekly_mileage_trend,
        cadence_trend,
        heart_rate_trend,
        latest_activity,
        streak,
    )
