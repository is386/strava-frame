import argparse
from requests.exceptions import RequestException
from display import render
from time import sleep
from data import (
    get_yearly_strava_activities,
    parse_latest_activity,
    parse_yearly_data,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--preview",
        action="store_true",
        help="Generate preview image",
    )
    parser.add_argument(
        "-b",
        "--black",
        action="store_true",
        help="Use black accent color instead of orange",
    )
    parser.add_argument(
        "-i",
        "--ink",
        action="store_true",
        help="Render dashboard for E-Ink displays",
    )
    return parser.parse_args()


activities_cache = []

while True:
    args = parse_args()

    try:
        activities = get_yearly_strava_activities()
        activities_cache = activities
    except (RuntimeError, RequestException):
        activities = activities_cache

    latest_activity = parse_latest_activity(activities)
    (
        total_activities,
        total_mileage,
        avg_weekly_mileage,
        mileage_per_month,
    ) = parse_yearly_data(activities)

    img = render(
        total_mileage,
        avg_weekly_mileage,
        total_activities,
        list(mileage_per_month),
        latest_activity,
        args.black,
    )

    if args.ink:
        img = img.convert("L")
        THRESHOLD = 210
        img = img.point(lambda p: 255 if p > THRESHOLD else 0, mode="1")

    if args.preview:
        img.save("preview.png")

    sleep(15 * 60)
