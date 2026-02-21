import tkinter as tk
import traceback
import sys
from pathlib import Path
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
from render import (
    generate_image,
    generate_sleep_image,
    Renderer,
    DARK_TEXT_COLOR,
    LIGHT_TEXT_COLOR,
)
from datetime import datetime
from PIL import ImageTk

tk_root = None
tk_label = None
tk_photo = None
exit_btn = None
refresh_btn = None
fullscreen_btn = None
loading_label = None
current_width = WIDTH
current_height = HEIGHT


def is_sleep_mode() -> bool:
    hour = datetime.now().hour
    return SLEEP_MODE_ENABLED and (hour >= SLEEP_MODE_START or hour < SLEEP_MODE_END)


def show_loading() -> None:
    tk_label.config(image="")
    exit_btn.place_forget()
    refresh_btn.place_forget()
    fullscreen_btn.place_forget()
    loading_label.place(relx=0.5, rely=0.5, anchor="center")
    tk_root.update_idletasks()


def read_window_dimensions() -> tuple[int, int]:
    tk_root.update_idletasks()
    return tk_root.winfo_width(), tk_root.winfo_height()


def toggle_fullscreen(event=None) -> None:
    is_fullscreen = not tk_root.attributes("-fullscreen")
    tk_root.attributes("-fullscreen", is_fullscreen)
    show_loading()
    tk_root.after(1000, on_resize_settled)


def on_resize_settled() -> None:
    global current_width, current_height
    current_width, current_height = read_window_dimensions()
    tk_root.after(1000, update_dashboard)


def refresh_dashboard() -> None:
    show_loading()
    tk_root.after(1000, update_dashboard)


def update_button_position() -> None:
    header = Renderer(current_width, current_height).header_height
    button_size = int(header * 0.55)
    font_size = max(10, int(button_size * 0.5))
    button_y = header - button_size

    exit_btn.place(
        x=current_width - button_size,
        y=button_y,
        width=button_size,
        height=button_size,
    )

    if is_sleep_mode():
        exit_btn.config(font=("Arial", font_size), bg="#000000")
        refresh_btn.place_forget()
        fullscreen_btn.place_forget()
        return

    exit_btn.config(font=("Arial", font_size), bg=ACCENT_COLOR)
    refresh_btn.config(font=("Arial", font_size))
    fullscreen_btn.config(font=("Arial", font_size))

    refresh_btn.place(
        x=current_width - (2 * button_size),
        y=button_y,
        width=button_size,
        height=button_size,
    )
    fullscreen_btn.place(
        x=current_width - (3 * button_size),
        y=button_y,
        width=button_size,
        height=button_size,
    )


def update_dashboard() -> None:
    global tk_photo

    if is_sleep_mode():
        img = generate_sleep_image(current_width, current_height)
    else:
        img = generate_image(current_width, current_height)

    update_button_position()
    tk_photo = ImageTk.PhotoImage(img)
    tk_label.config(image=tk_photo)
    if loading_label and loading_label.winfo_ismapped():
        loading_label.place_forget()
    tk_root.after(REFRESH_TIME, update_dashboard)


def handle_exception(exc_type, exc_value, exc_traceback):
    error_message = "".join(
        traceback.format_exception(exc_type, exc_value, exc_traceback)
    )
    print(error_message, file=sys.stderr)

    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_filename = logs_dir / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    with open(log_filename, "w") as f:
        f.write(error_message)

    sys.exit(1)


def run_dashboard() -> None:
    global tk_root, tk_label, refresh_btn, fullscreen_btn, exit_btn, loading_label
    global current_width, current_height

    tk_root = tk.Tk()
    tk_root.report_callback_exception = handle_exception

    tk_root.title("")
    tk_root.geometry(f"{WIDTH}x{HEIGHT}")
    tk_root.resizable(False, False)
    tk_root.attributes("-fullscreen", FULL_SCREEN)
    tk_root.config(cursor="none")

    frame = tk.Frame(tk_root)
    frame.pack(expand=True, fill="both")

    tk_label = tk.Label(frame)
    tk_label.pack(expand=True)

    loading_label = tk.Label(
        frame,
        text="Loading...",
        font=("Arial", 48),
        bg=tk_root.cget("bg"),
        fg="#000000",
    )
    loading_label.place(relx=0.5, rely=0.5, anchor="center")

    shared_btn_config = dict(
        font=("Arial", 20),
        bg=ACCENT_COLOR,
        fg=LIGHT_TEXT_COLOR if DARK_MODE else DARK_TEXT_COLOR,
        borderwidth=0,
        relief="flat",
        padx=0,
        pady=0,
        highlightthickness=0,
    )

    exit_btn = tk.Button(frame, text="✕", command=tk_root.destroy, **shared_btn_config)
    refresh_btn = tk.Button(
        frame, text="⟳", command=refresh_dashboard, **shared_btn_config
    )
    fullscreen_btn = tk.Button(
        frame, text="⤢", command=toggle_fullscreen, **shared_btn_config
    )

    tk_root.update_idletasks()
    current_width, current_height = read_window_dimensions()

    update_dashboard()
    tk_root.mainloop()


if __name__ == "__main__":
    try:
        run_dashboard()
    except Exception:
        handle_exception(*sys.exc_info())
