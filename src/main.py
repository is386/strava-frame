import tkinter as tk
from config import (
    REFRESH_TIME,
    SLEEP_MODE_ENABLED,
    SLEEP_MODE_START,
    SLEEP_MODE_END,
    ACCENT_COLOR,
    HEIGHT,
    WIDTH,
    DARK_MODE,
    FULL_SCREEN,
)
from display import (
    generate_image,
    generate_sleep_image,
    DARK_TEXT_COLOR,
    LIGHT_TEXT_COLOR,
    HEADER_HEIGHT,
)
from data import refresh_streak
from datetime import datetime
from PIL import ImageTk, Image


was_sleeping = True
tk_root = None
tk_label = None
tk_photo = None
refresh_btn = None
fullscreen_btn = None


def is_sleep_mode() -> bool:
    hour = datetime.now().hour
    return SLEEP_MODE_ENABLED and (hour >= SLEEP_MODE_START or hour < SLEEP_MODE_END)


def toggle_fullscreen(event=None) -> None:
    current = tk_root.attributes("-fullscreen")
    tk_root.attributes("-fullscreen", not current)
    tk_root.after(1000, update_dashboard)


def update_button_position(event=None) -> None:
    if is_sleep_mode():
        return

    window_width = tk_root.winfo_width()
    window_height = tk_root.winfo_height()

    if window_width <= 1 or window_height <= 1:
        tk_root.after(100, update_button_position)
        return

    scale = min(window_width / WIDTH, window_height / HEIGHT)

    button_size = int(40 * scale)
    font_size = max(12, int(20 * scale))
    margin = int(10 * scale)

    scaled_width = int(WIDTH * scale)
    scaled_height = int(HEIGHT * scale)
    x_offset = (window_width - scaled_width) // 2
    y_offset = (window_height - scaled_height) // 2

    button_y = y_offset + (HEADER_HEIGHT - button_size)

    refresh_btn.config(font=("Arial", font_size))
    fullscreen_btn.config(font=("Arial", font_size))

    refresh_btn.place(
        x=x_offset + scaled_width - button_size - margin,
        y=button_y,
        width=button_size,
        height=button_size,
    )
    fullscreen_btn.place(
        x=x_offset + margin,
        y=button_y,
        width=button_size,
        height=button_size,
    )


def update_dashboard() -> None:
    global tk_photo, was_sleeping

    if is_sleep_mode():
        was_sleeping = True
        img = generate_sleep_image()
        refresh_btn.place_forget()
        fullscreen_btn.place_forget()
    else:
        if was_sleeping:
            was_sleeping = False
            refresh_streak()
        img = generate_image()
        update_button_position()

    window_width = tk_root.winfo_width()
    window_height = tk_root.winfo_height()

    if window_width > 1 and window_height > 1:
        scale = min(window_width / img.width, window_height / img.height)
        img = img.resize(
            (int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS
        )

    tk_photo = ImageTk.PhotoImage(img)
    tk_label.config(image=tk_photo)
    tk_root.after(REFRESH_TIME, update_dashboard)


def run_dashboard() -> None:
    global tk_root, tk_label, refresh_btn, fullscreen_btn

    tk_root = tk.Tk()
    tk_root.title("")
    tk_root.geometry(f"{WIDTH}x{HEIGHT}")
    tk_root.resizable(False, False)
    tk_root.attributes("-fullscreen", FULL_SCREEN)
    tk_root.config(cursor="none")

    tk_root.bind("<Escape>", lambda e: tk_root.destroy())

    frame = tk.Frame(tk_root)
    frame.pack(expand=True, fill="both")

    tk_label = tk.Label(frame)
    tk_label.pack(expand=True)

    fg_color = LIGHT_TEXT_COLOR if DARK_MODE else DARK_TEXT_COLOR

    shared_btn_config = dict(
        font=("Arial", 20),
        bg=ACCENT_COLOR,
        fg=fg_color,
        borderwidth=0,
        relief="flat",
        padx=0,
        pady=0,
        highlightthickness=0,
    )
    refresh_btn = tk.Button(
        frame, text="⟳", command=update_dashboard, **shared_btn_config
    )
    fullscreen_btn = tk.Button(
        frame, text="⤢", command=toggle_fullscreen, **shared_btn_config
    )

    tk_root.update_idletasks()
    update_dashboard()
    tk_root.mainloop()


run_dashboard()
