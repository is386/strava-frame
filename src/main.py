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
from render import (
    generate_image,
    generate_sleep_image,
    Renderer,
    DARK_TEXT_COLOR,
    LIGHT_TEXT_COLOR,
)
from data import refresh_streak
from datetime import datetime
from PIL import ImageTk

was_sleeping = True
tk_root = None
tk_label = None
tk_photo = None
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
    refresh_btn.place_forget()
    fullscreen_btn.place_forget()
    loading_label.place(relx=0.5, rely=0.5, anchor="center")
    tk_root.update_idletasks()


def _read_window_dimensions() -> tuple[int, int]:
    """Return the actual current window dimensions from tkinter."""
    tk_root.update_idletasks()
    return tk_root.winfo_width(), tk_root.winfo_height()


def toggle_fullscreen(event=None) -> None:
    global current_width, current_height

    is_fullscreen = not tk_root.attributes("-fullscreen")
    tk_root.attributes("-fullscreen", is_fullscreen)

    tk_root.after(100, _on_resize_settled)


def _on_resize_settled() -> None:
    """Called after a short delay so the WM has finished resizing the window."""
    global current_width, current_height
    current_width, current_height = _read_window_dimensions()
    refresh_dashboard()


def refresh_dashboard() -> None:
    show_loading()
    tk_root.after(1000, update_dashboard)


def update_button_position() -> None:
    if is_sleep_mode():
        return

    header = Renderer(current_width, current_height).header_height
    button_size = int(header * 0.55)
    margin = max(6, int(header * 0.13))
    font_size = max(10, int(button_size * 0.5))
    button_y = header - button_size

    refresh_btn.config(font=("Arial", font_size))
    fullscreen_btn.config(font=("Arial", font_size))

    refresh_btn.place(
        x=current_width - button_size - margin,
        y=button_y,
        width=button_size,
        height=button_size,
    )
    fullscreen_btn.place(
        x=margin,
        y=button_y,
        width=button_size,
        height=button_size,
    )


def update_dashboard() -> None:
    global tk_photo, was_sleeping

    if is_sleep_mode():
        was_sleeping = True
        img = generate_sleep_image(current_width, current_height)
        refresh_btn.place_forget()
        fullscreen_btn.place_forget()
    else:
        if was_sleeping:
            was_sleeping = False
            refresh_streak()
        img = generate_image(current_width, current_height)
        update_button_position()

    tk_photo = ImageTk.PhotoImage(img)
    tk_label.config(image=tk_photo)
    if loading_label and loading_label.winfo_ismapped():
        loading_label.place_forget()
    tk_root.after(REFRESH_TIME, update_dashboard)


def run_dashboard() -> None:
    global tk_root, tk_label, refresh_btn, fullscreen_btn, loading_label
    global current_width, current_height

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
    refresh_btn = tk.Button(
        frame, text="⟳", command=refresh_dashboard, **shared_btn_config
    )
    fullscreen_btn = tk.Button(
        frame, text="⤢", command=toggle_fullscreen, **shared_btn_config
    )

    tk_root.update_idletasks()
    current_width, current_height = _read_window_dimensions()

    update_dashboard()
    tk_root.mainloop()


run_dashboard()
