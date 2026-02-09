import argparse
from requests.exceptions import RequestException
from display import render
from data import (
    get_yearly_strava_activities,
    parse_latest_activity,
    parse_yearly_data,
)
import tkinter as tk
from PIL import ImageTk

activities_cache = []
tk_root = None
tk_label = None
tk_photo = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b",
        "--black",
        action="store_true",
        help="Use black accent color instead of orange",
    )
    parser.add_argument(
        "-f",
        "--fullscreen",
        action="store_true",
        help="Toggle fullscreen mode",
    )
    parser.add_argument(
        "-i",
        "--ink",
        action="store_true",
        help="Render dashboard for E-Ink displays",
    )
    return parser.parse_args()


args = parse_args()


def fetch_and_parse_activities():
    global activities_cache
    try:
        activities = get_yearly_strava_activities()
        activities_cache = activities
    except (RuntimeError, RequestException):
        activities = activities_cache
    latest_activity = parse_latest_activity(activities)
    total_activities, total_mileage, avg_weekly_mileage, mileage_per_month = (
        parse_yearly_data(activities)
    )
    return (
        total_activities,
        total_mileage,
        avg_weekly_mileage,
        list(mileage_per_month),
        latest_activity,
    )


def generate_image():
    (
        total_activities,
        total_mileage,
        avg_weekly_mileage,
        mileage_per_month,
        latest_activity,
    ) = fetch_and_parse_activities()
    img = render(
        total_mileage,
        avg_weekly_mileage,
        total_activities,
        mileage_per_month,
        latest_activity,
        args.black,
    )
    return img


def update_tk_dashboard():
    global tk_root, tk_label, tk_photo
    img = generate_image()
    tk_photo = ImageTk.PhotoImage(img)
    tk_label.config(image=tk_photo)
    tk_root.after(15 * 60 * 1000, update_tk_dashboard)


def run_tk_dashboard():
    global tk_root, tk_label
    tk_root = tk.Tk()
    tk_root.title("")
    tk_root.resizable(False, False)
    tk_root.attributes("-fullscreen", args.fullscreen)
    tk_root.config(cursor="none")
    tk_root.bind("<Escape>", lambda e: tk_root.destroy())
    tk_label = tk.Label(tk_root)
    tk_label.pack(expand=True)
    update_tk_dashboard()
    tk_root.mainloop()


def run_ink_dashboard():
    img = generate_image()
    img = img.convert("L")
    THRESHOLD = 210
    img = img.point(lambda p: 255 if p > THRESHOLD else 0, mode="1")
    print("E-Ink dashboard updated (todo).")


if args.ink:
    run_ink_dashboard()
else:
    run_tk_dashboard()
