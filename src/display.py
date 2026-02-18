import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as PILImage
from typing import List, Dict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "..", "assets")

WIDTH, HEIGHT = 800, 480

BASE_WIDTH, BASE_HEIGHT = 800, 480
SCALE = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)


def sc(value: float) -> int:
    return round(value * SCALE)


HEADER_HEIGHT = sc(75)
BOTTOM_ROW_HEIGHT = sc(149)
GRAPH_BOTTOM_OFFSET = sc(175)
MARGIN = sc(10)
INNER_PADDING = sc(12)
CARD_SPACING = sc(15)
TITLE_BOTTOM_PADDING = sc(14)
BAR_LABEL_THRESHOLD = sc(25)

LEFT_COLUMN_WIDTH_RATIO = 3
STREAK_CARD_WIDTH_RATIO = 4

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

LIGHT_ACCENT_COLOR = "#FC4C02"
LIGHT_BG_COLOR = "#FAFAFA"
LIGHT_TEXT_COLOR = "#000000"
LIGHT_LABEL_COLOR = "#888888"
LIGHT_CARD_COLOR = "#FFFFFF"
LIGHT_BORDER_COLOR = "#E0E0E0"

DARK_ACCENT_COLOR = "#fa8b5c"
DARK_BG_COLOR = "#1A1A1A"
DARK_TEXT_COLOR = "#E0E0E0"
DARK_LABEL_COLOR = "#999999"
DARK_CARD_COLOR = "#2b2b2b"
DARK_BORDER_COLOR = "#404040"

ACCENT_COLOR = LIGHT_ACCENT_COLOR
BG_COLOR = LIGHT_BG_COLOR
TEXT_COLOR = LIGHT_TEXT_COLOR
LABEL_COLOR = LIGHT_LABEL_COLOR
CARD_COLOR = LIGHT_CARD_COLOR
BORDER_COLOR = LIGHT_BORDER_COLOR

FONT_BOLD_SMALL = ImageFont.truetype(os.path.join(ASSETS_DIR, "segoeuib.ttf"), sc(16))
FONT_BOLD_MEDIUM = ImageFont.truetype(os.path.join(ASSETS_DIR, "segoeuib.ttf"), sc(22))
FONT_BOLD_LARGE = ImageFont.truetype(os.path.join(ASSETS_DIR, "segoeuib.ttf"), sc(28))
FONT_BOLD_XLARGE = ImageFont.truetype(os.path.join(ASSETS_DIR, "segoeuib.ttf"), sc(48))

FONT_REGULAR_SMALL = ImageFont.truetype(os.path.join(ASSETS_DIR, "segoeui.ttf"), sc(16))
FONT_REGULAR_MEDIUM = ImageFont.truetype(
    os.path.join(ASSETS_DIR, "segoeui.ttf"), sc(32)
)
FONT_REGULAR_LARGE = ImageFont.truetype(os.path.join(ASSETS_DIR, "segoeui.ttf"), sc(48))


def text_size(draw: ImageDraw.Draw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_text_centered(
    draw: ImageDraw.Draw, text: str, font, center_x: int, y: int, color: str
):
    bbox = draw.textbbox((0, 0), text, font=font)
    x = center_x - (bbox[2] - bbox[0]) // 2 - bbox[0]
    draw.text((x, y), text, font=font, fill=color)


def draw_card(draw: ImageDraw.Draw, x0: int, y0: int, x1: int, y1: int):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=sc(8), fill=CARD_COLOR)
    draw.rounded_rectangle(
        [x0, y0, x1, y1], radius=sc(8), outline=BORDER_COLOR, width=1
    )


def draw_header(draw: ImageDraw.Draw):
    draw.rectangle([(0, 0), (WIDTH, HEADER_HEIGHT)], fill=ACCENT_COLOR)
    w, h = text_size(draw, "Strava Dashboard", FONT_BOLD_LARGE)
    x = (WIDTH - w) // 2
    y = (HEADER_HEIGHT - h) // 2 + sc(5)
    draw.text((x, y), "Strava Dashboard", font=FONT_BOLD_LARGE, fill=BG_COLOR)


def draw_stat(
    draw: ImageDraw.Draw, value, label: str, center_x: int, y: int, decimal: bool
):
    value_text = f"{value:.2f}" if decimal else str(value)
    _, value_h = text_size(draw, value_text, FONT_REGULAR_LARGE)
    draw_text_centered(draw, value_text, FONT_REGULAR_LARGE, center_x, y, TEXT_COLOR)
    draw_text_centered(
        draw, label, FONT_REGULAR_SMALL, center_x, y + value_h + sc(25), LABEL_COLOR
    )


def draw_left_column(
    draw: ImageDraw.Draw, total_mileage, weekly_mileage, activities
) -> int:
    left_width = WIDTH // LEFT_COLUMN_WIDTH_RATIO
    x0 = MARGIN
    y0 = HEADER_HEIGHT + MARGIN
    x1 = left_width - MARGIN + sc(5)
    y1 = HEIGHT - MARGIN
    draw_card(draw, x0, y0, x1, y1)

    title = f"{datetime.now().year} Stats"
    title_x = x0 + INNER_PADDING
    title_y = y0 + INNER_PADDING
    draw.text((title_x, title_y), title, font=FONT_BOLD_MEDIUM, fill=TEXT_COLOR)

    _, title_h = text_size(draw, title, FONT_BOLD_MEDIUM)
    metrics_top = title_y + title_h + TITLE_BOTTOM_PADDING
    section_h = (y1 - metrics_top - INNER_PADDING) / 3
    center_x = (x0 + x1) // 2

    stats = [
        (total_mileage, "Miles", True),
        (weekly_mileage, "Miles per Week", True),
        (activities, "Activities", False),
    ]

    for i, (value, label, decimal) in enumerate(stats):
        value_text = f"{value:.2f}" if decimal else str(value)
        _, value_h = text_size(draw, value_text, FONT_REGULAR_LARGE)
        _, label_h = text_size(draw, label, FONT_REGULAR_SMALL)
        block_h = value_h + sc(20) + label_h
        section_center_y = metrics_top + i * section_h + section_h / 2
        draw_stat(
            draw,
            value,
            label,
            center_x,
            section_center_y - block_h / 2 - sc(10),
            decimal,
        )

    for i in range(1, 3):
        y = metrics_top + i * section_h
        draw.line(
            [(x0 + INNER_PADDING + sc(20), y), (x1 - INNER_PADDING - sc(20), y)],
            fill=BORDER_COLOR,
            width=1,
        )

    return left_width


def draw_monthly_graph(
    draw: ImageDraw.Draw, mileage_per_month: List[float], left_width: int
) -> int:
    x0 = left_width + MARGIN
    y0 = HEADER_HEIGHT + MARGIN
    x1 = WIDTH - MARGIN
    y1 = HEIGHT - GRAPH_BOTTOM_OFFSET
    draw_card(draw, x0, y0, x1, y1)

    inner_y0 = y0 + INNER_PADDING
    inner_y1 = y1 - INNER_PADDING

    title_x = x0 + INNER_PADDING - sc(2)
    draw.text(
        (title_x, inner_y0), "Monthly Mileage", font=FONT_BOLD_MEDIUM, fill=TEXT_COLOR
    )
    _, title_h = text_size(draw, "Monthly Mileage", FONT_BOLD_MEDIUM)

    bars_top = inner_y0 + title_h + INNER_PADDING + sc(10)
    bars_bottom = inner_y1 - sc(20)
    bar_max_height = bars_bottom - bars_top

    num_bars = len(mileage_per_month)
    total_spacing = (x1 - x0) * 0.3
    spacing = total_spacing / (num_bars + 1)
    bar_width = ((x1 - x0) - total_spacing) / num_bars
    max_val = max(mileage_per_month) if mileage_per_month else 1
    max_val = max_val or 1

    for i, val in enumerate(mileage_per_month):
        bar_h = int((val / max_val) * bar_max_height)
        bx0 = x0 + spacing + i * (bar_width + spacing)
        bx1 = bx0 + bar_width
        bar_top = bars_bottom - bar_h
        draw.rounded_rectangle(
            [bx0, bar_top, bx1, bars_bottom], radius=sc(2), fill=ACCENT_COLOR
        )

        if val > 0:
            val_text = str(round(val))
            val_w, _ = text_size(draw, val_text, FONT_BOLD_SMALL)
            val_x = bx0 + (bar_width - val_w) // 2
            if bar_h > BAR_LABEL_THRESHOLD:
                draw.text(
                    (val_x, bar_top + sc(4)),
                    val_text,
                    font=FONT_BOLD_SMALL,
                    fill=BG_COLOR,
                )
            else:
                draw.text(
                    (val_x, bar_top - sc(14)),
                    val_text,
                    font=FONT_BOLD_SMALL,
                    fill=TEXT_COLOR,
                )

        month_w, _ = text_size(draw, MONTHS[i], FONT_REGULAR_SMALL)
        month_x = bx0 + (bar_width - month_w) // 2
        draw.text(
            (month_x, bars_bottom + sc(4)),
            MONTHS[i],
            font=FONT_REGULAR_SMALL,
            fill=LABEL_COLOR,
        )

    return y1


def colorize_icon(icon: Image.Image, hex_color: str) -> Image.Image:
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    icon = icon.convert("RGBA")
    pixels = icon.load()
    for y in range(icon.height):
        for x in range(icon.width):
            pr, pg, pb, pa = pixels[x, y]
            brightness = (pr + pg + pb) / 3
            pixels[x, y] = (r, g, b, int((1 - brightness / 255) * pa))
    return icon


def draw_streak(
    draw: ImageDraw.Draw,
    img: Image.Image,
    streak: int,
    left_width: int,
    top_offset: int,
):
    right_area_width = WIDTH - MARGIN - (left_width + MARGIN)
    area_x0 = (
        WIDTH - MARGIN - right_area_width // STREAK_CARD_WIDTH_RATIO + CARD_SPACING
    )
    area_x1 = WIDTH - MARGIN
    area_y0 = top_offset + CARD_SPACING
    area_y1 = area_y0 + BOTTOM_ROW_HEIGHT
    area_w = area_x1 - area_x0
    area_h = area_y1 - area_y0

    fire_raw = Image.open(os.path.join(ASSETS_DIR, "fire.png")).convert("RGBA")
    fire_colored = colorize_icon(fire_raw, ACCENT_COLOR)

    label_w, label_h = text_size(draw, "Weeks", FONT_BOLD_SMALL)
    label_y = area_y1 - INNER_PADDING - label_h
    fire_zone_h = label_y - sc(4) - area_y0

    fire_scale = fire_zone_h / fire_colored.height
    fire_w = int(fire_colored.width * fire_scale)
    fire_h = int(fire_colored.height * fire_scale)
    fire_img = fire_colored.resize((fire_w, fire_h), Image.Resampling.LANCZOS)

    img.paste(
        fire_img,
        (area_x0 + (area_w - fire_w) // 2, area_y0 + (fire_zone_h - fire_h) // 2),
        fire_img,
    )

    streak_text = str(streak)
    streak_w, streak_h = text_size(draw, streak_text, FONT_BOLD_XLARGE)
    text_x = area_x0 + (area_w - streak_w) // 2
    text_y = area_y0 + (fire_zone_h - streak_h) // 2 + sc(5)
    draw.text((text_x, text_y), streak_text, font=FONT_BOLD_XLARGE, fill=BG_COLOR)

    label_x = area_x0 + (area_w - label_w) // 2
    draw.text((label_x, label_y), "Weeks", font=FONT_BOLD_SMALL, fill=ACCENT_COLOR)


def draw_latest_activity(
    draw: ImageDraw.Draw, activity: Dict, left_width: int, top_offset: int
):
    right_area_width = WIDTH - MARGIN - (left_width + MARGIN)
    x0 = left_width + MARGIN
    y0 = top_offset + CARD_SPACING
    x1 = WIDTH - MARGIN - right_area_width // STREAK_CARD_WIDTH_RATIO
    y1 = y0 + BOTTOM_ROW_HEIGHT
    draw_card(draw, x0, y0, x1, y1)

    inner_x = x0 + INNER_PADDING
    inner_y0 = y0 + INNER_PADDING
    inner_y1 = y1 - INNER_PADDING

    title = activity.get("title", "")
    draw.text((inner_x, inner_y0), title, font=FONT_BOLD_MEDIUM, fill=TEXT_COLOR)
    _, title_h = text_size(draw, title, FONT_BOLD_MEDIUM)

    date_y = inner_y0 + title_h + sc(6)
    draw.text(
        (inner_x, date_y + sc(5)),
        activity.get("date", ""),
        font=FONT_REGULAR_SMALL,
        fill=LABEL_COLOR,
    )

    metrics = [
        ("Distance (mi)", f"{activity.get('miles', 0):.2f}"),
        ("Time", activity.get("time", "0:00")),
        ("Pace", activity.get("pace", "0:00")),
    ]

    section_padding = sc(12)
    panel_top = date_y + sc(10)
    panel_h = inner_y1 - panel_top

    section_widths = []
    for label, value in metrics:
        value_w, _ = text_size(draw, str(value), FONT_REGULAR_MEDIUM)
        label_w, _ = text_size(draw, label, FONT_REGULAR_SMALL)
        section_widths.append(max(value_w, label_w) + section_padding * 2)

    x_cursor = inner_x
    for i, (label, value) in enumerate(metrics):
        value_w, value_h = text_size(draw, str(value), FONT_REGULAR_MEDIUM)
        _, label_h = text_size(draw, label, FONT_REGULAR_SMALL)
        block_h = value_h + sc(8) + label_h
        y_top = panel_top + (panel_h - block_h) // 2
        x = x_cursor + (section_padding if i > 0 else 1)

        draw.text((x, y_top), str(value), font=FONT_REGULAR_MEDIUM, fill=TEXT_COLOR)
        draw.text(
            (x, y_top + value_h + sc(16)),
            label,
            font=FONT_REGULAR_SMALL,
            fill=LABEL_COLOR,
        )

        x_cursor += section_widths[i]

        if i < len(metrics) - 1:
            draw.line(
                [(x_cursor, panel_top + sc(30)), (x_cursor, inner_y1 - sc(5))],
                fill=BORDER_COLOR,
                width=1,
            )


def render(
    total_mileage: float,
    weekly_mileage: float,
    activities: int,
    mileage_per_month: List[float],
    latest_activity: Dict,
    streak: int = 0,
    color: str = "",
    dark_mode: bool = False,
) -> PILImage:
    global ACCENT_COLOR, BG_COLOR, TEXT_COLOR, LABEL_COLOR, CARD_COLOR, BORDER_COLOR

    if dark_mode:
        ACCENT_COLOR, BG_COLOR, TEXT_COLOR, LABEL_COLOR, CARD_COLOR, BORDER_COLOR = (
            DARK_ACCENT_COLOR,
            DARK_BG_COLOR,
            DARK_TEXT_COLOR,
            DARK_LABEL_COLOR,
            DARK_CARD_COLOR,
            DARK_BORDER_COLOR,
        )

    if color:
        ACCENT_COLOR = color

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw_header(draw)
    left_width = draw_left_column(draw, total_mileage, weekly_mileage, activities)
    graph_bottom = draw_monthly_graph(draw, mileage_per_month, left_width)
    draw_latest_activity(draw, latest_activity, left_width, top_offset=graph_bottom)
    draw_streak(draw, img, streak, left_width, top_offset=graph_bottom)

    return img


def render_sleep_mode() -> PILImage:
    return Image.new("RGB", (WIDTH, HEIGHT), color="black")
