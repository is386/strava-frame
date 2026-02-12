import argparse
import tkinter as tk
from requests.exceptions import RequestException
from display import render, render_sleep_mode, STRAVA_ORANGE
from data import (
    get_yearly_strava_activities,
    parse_latest_activity,
    parse_yearly_data,
)
from PIL import ImageTk, Image
from datetime import datetime

SLEEP_MODE_START = 21
SLEEP_MODE_END = 6
REFRESH_TIME = 15 * 60 * 1000

activities_cache = []
tk_root = None
tk_label = None
tk_photo = None
is_first_update = True

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Strava Frame",
        epilog="Keyboard shortcuts: F11 = toggle fullscreen | Escape = quit"
        + " | r = refresh",
    )
    parser.add_argument(
        "-b",
        "--black",
        action="store_true",
        help="use black accent color instead of orange",
    )
    parser.add_argument(
        "-f",
        "--fullscreen",
        action="store_true",
        help="run in fullscreen mode",
    )
    return parser.parse_args()


def fetch_and_parse_activities():
    global activities_cache
    try:
        activities = get_yearly_strava_activities()
        activities_cache = activities
    except (RuntimeError, RequestException) as e:
        print(e)
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


def update_dashboard():
    global tk_root, tk_label, tk_photo, is_first_update

    now = datetime.now()

    if not is_first_update and (now.hour > SLEEP_MODE_START or now.hour < SLEEP_MODE_END):
        img = render_sleep_mode()
    else:    
        img = generate_image()

    window_width = tk_root.winfo_width()
    window_height = tk_root.winfo_height()

    if window_width > 1 and window_height > 1:
        img_width, img_height = img.size
        scale_w = window_width / img_width
        scale_h = window_height / img_height
        scale = min(scale_w, scale_h)

        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    tk_photo = ImageTk.PhotoImage(img)
    tk_label.config(image=tk_photo)

    if is_first_update:
        is_first_update = False
        tk_root.after(5000, update_dashboard)
    else:
        tk_root.after(REFRESH_TIME, update_dashboard)


def update_button_position(event=None):
    global tk_root, refresh_btn
    
    window_height = tk_root.winfo_height()
    if window_height <= 1:
        tk_root.after(100, update_button_position)
        return
        
    scale = window_height / 480
    button_size = int(40 * scale)
    font_size = max(12, int(20 * scale))
    
    margin = int(10 * scale)
    
    refresh_btn.config(font=("Arial", font_size))
    
    refresh_btn.place(x=tk_root.winfo_width() - button_size - margin, 
                     y=margin, 
                     width=button_size, 
                     height=button_size)


def toggle_fullscreen(event=None):
    global tk_root
    current = tk_root.attributes("-fullscreen")
    tk_root.attributes("-fullscreen", not current)


def run_dashboard():
    global tk_root, tk_label, refresh_btn
    tk_root = tk.Tk()
    tk_root.title("")
    tk_root.resizable(False, False)
    tk_root.attributes("-fullscreen", args.fullscreen)
    tk_root.config(cursor="none")

    tk_root.bind("<Escape>", lambda e: tk_root.destroy())
    tk_root.bind("<F11>", toggle_fullscreen)
    tk_root.bind("<r>", lambda e: update_dashboard())

    frame = tk.Frame(tk_root)
    frame.pack(expand=True, fill='both')
    
    tk_label = tk.Label(frame)
    tk_label.pack(expand=True)
    
    btn_color = 'black' if args.black else STRAVA_ORANGE
    refresh_btn = tk.Button(frame, text="⟳", command=update_dashboard,
                        font=("Arial", 20), bg=btn_color, fg='white',
                        borderwidth=0, relief='flat', padx=0, pady=0,
                        highlightthickness=0)
    
    tk_root.bind("<Configure>", update_button_position)
    
    tk_root.after(100, update_button_position)
    
    update_dashboard()
    tk_root.mainloop()


args = parse_args()
run_dashboard()
