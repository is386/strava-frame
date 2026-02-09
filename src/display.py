from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as PILImage
from typing import List, Dict

# =========================
# Fonts and colors
# =========================
HEADER_FONT = ImageFont.truetype("assets/segoeuib.ttf", 28)
YEAR_METRIC_VALUE_FONT = ImageFont.truetype("assets/segoeui.ttf", 48)
LABEL_FONT = ImageFont.truetype("assets/segoeui.ttf", 16)
LATEST_TITLE_FONT = ImageFont.truetype("assets/segoeuib.ttf", 22)
METRIC_VALUE_FONT = ImageFont.truetype("assets/segoeui.ttf", 32)
DATE_FONT = ImageFont.truetype("assets/segoeui.ttf", 16)
LEFT_CARD_TITLE_FONT = ImageFont.truetype("assets/segoeuib.ttf", 22)

STRAVA_ORANGE = "#FC4C02"
BG_COLOR = "#FAFAFA"
TEXT_COLOR = "#000000"
LABEL_COLOR = "#888888"
CARD_COLOR = "#FFFFFF"

# =========================
# Layout constants
# =========================
MARGIN_LEFT = 10
MARGIN_RIGHT = 10
MARGIN_TOP = 10
MARGIN_BOTTOM = 10
INNER_PADDING = 12
CARD_SPACING = 15


# =========================
# Card helper
# =========================
def draw_card(draw: ImageDraw.Draw, x0, y0, x1, y1, radius=8, fill=CARD_COLOR):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)
    border_color = "#E0E0E0"
    draw.rounded_rectangle(
        [x0, y0, x1, y1], radius=radius, outline=border_color, width=1
    )


# =========================
# Header
# =========================
def draw_header(draw: ImageDraw.Draw, width: int, header_height: int):
    draw.rectangle([(0, 0), (width, header_height)], fill=STRAVA_ORANGE)
    title = "Strava Dashboard"
    bbox = draw.textbbox((0, 0), title, font=HEADER_FONT)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (width - text_w) // 2
    text_y = (header_height - text_h) // 2 - bbox[1]
    draw.text((text_x, text_y), title, font=HEADER_FONT, fill=BG_COLOR)


# =========================
# Metric drawer
# =========================
def draw_metric(
    draw: ImageDraw.Draw, center_x: int, y: int, number, label, show_dec=True
):
    num_text = f"{number:.2f}" if show_dec else str(number)
    num_bbox = draw.textbbox((0, 0), num_text, font=YEAR_METRIC_VALUE_FONT)
    num_w = num_bbox[2] - num_bbox[0]
    num_h = num_bbox[3] - num_bbox[1]
    num_x = center_x - num_w // 2
    draw.text(
        (num_x, y), num_text, font=YEAR_METRIC_VALUE_FONT, fill=TEXT_COLOR
    )

    label_bbox = draw.textbbox((0, 0), label, font=LABEL_FONT)
    label_w = label_bbox[2] - label_bbox[0]
    label_x = center_x - label_w // 2
    label_y = y + num_h + 20
    draw.text((label_x, label_y + 5), label, font=LABEL_FONT, fill=LABEL_COLOR)


# =========================
# Left Column Card
# =========================
def draw_left_column(
    draw: ImageDraw.Draw,
    total_mileage,
    weekly_mileage,
    activities,
    width,
    height,
    header_height,
):
    left_width = width // 3
    card_x0 = MARGIN_LEFT
    card_y0 = header_height + MARGIN_TOP
    card_x1 = left_width - MARGIN_RIGHT + 5
    card_y1 = height - MARGIN_BOTTOM
    draw_card(draw, card_x0, card_y0, card_x1, card_y1)

    # ----- Title -----
    year_text = f"{datetime.now().year} Stats"
    title_bbox = draw.textbbox((0, 0), year_text, font=LEFT_CARD_TITLE_FONT)

    title_x = card_x0 + INNER_PADDING
    title_y = card_y0 + INNER_PADDING
    draw.text(
        (title_x, title_y),
        year_text,
        font=LEFT_CARD_TITLE_FONT,
        fill=TEXT_COLOR,
    )

    # ----- Metrics -----
    # Measure title height
    title_h = title_bbox[3] - title_bbox[1]

    # Reserve space for title + breathing room
    TITLE_BOTTOM_PADDING = 14
    metrics_top = title_y + title_h + TITLE_BOTTOM_PADDING

    # Compute available height correctly
    metrics_height = card_y1 - metrics_top - INNER_PADDING
    section_height = metrics_height / 3
    center_x = (card_x0 + card_x1) // 2

    metrics = [
        (total_mileage, "Miles"),
        (weekly_mileage, "Miles per Week"),
        (activities, "Activities"),
    ]

    for i, (value, label) in enumerate(metrics):
        num_text = f"{value:.2f}" if i != 2 else str(value)
        num_bbox = draw.textbbox((0, 0), num_text, font=YEAR_METRIC_VALUE_FONT)
        num_h = num_bbox[3] - num_bbox[1]

        label_bbox = draw.textbbox((0, 0), label, font=LABEL_FONT)
        label_h = label_bbox[3] - label_bbox[1]

        block_height = num_h + 20 + label_h

        section_top = metrics_top + i * section_height
        section_center_y = section_top + section_height / 2
        block_top_y = section_center_y - block_height / 2

        draw_metric(
            draw,
            center_x,
            block_top_y - 10,
            value,
            label,
            show_dec=(i != 2),
        )

    # Horizontal dividers between metric sections
    for i in range(1, 3):
        y = metrics_top + i * section_height
        draw.line(
            [
                (card_x0 + INNER_PADDING + 20, y),
                (card_x1 - INNER_PADDING - 20, y),
            ],
            fill="#E0E0E0",
            width=1,
        )

    return left_width


# =========================
# Monthly Graph Card
# =========================
def draw_monthly_graph(
    draw: ImageDraw.Draw,
    mileage_per_month: List[int],
    left_width: int,
    width: int,
    header_height: int,
    total_height: int,  # pass in full image height
):
    months = [
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

    # Card coordinates
    card_x0 = left_width + MARGIN_LEFT
    card_y0 = header_height + MARGIN_TOP
    card_x1 = width - MARGIN_RIGHT
    # Graph takes up most of the height, leaving room for latest activity card
    card_y1 = total_height - 175  # leave ~140px for latest activity
    draw_card(draw, card_x0, card_y0, card_x1, card_y1)

    # Inner area
    inner_x0 = card_x0
    inner_x1 = card_x1
    inner_y0 = card_y0 + INNER_PADDING
    inner_y1 = card_y1 - INNER_PADDING

    # Title (left-aligned, same style as latest activity title)
    graph_label = "Monthly Mileage"
    title_bbox = draw.textbbox((0, 0), graph_label, font=LATEST_TITLE_FONT)
    title_h = title_bbox[3] - title_bbox[1]

    title_x = inner_x0 + INNER_PADDING - 2
    title_y = inner_y0
    draw.text(
        (title_x, title_y),
        graph_label,
        font=LATEST_TITLE_FONT,
        fill=TEXT_COLOR,
    )

    # Bar area
    BAR_TOP_MARGIN = INNER_PADDING + 10
    bars_top = title_y + title_h + BAR_TOP_MARGIN
    bars_bottom = inner_y1 - 20  # leave space for month labels
    bar_max_height = bars_bottom - bars_top

    num_bars = len(mileage_per_month)
    total_spacing = (inner_x1 - inner_x0) * 0.3
    spacing = total_spacing / (num_bars + 1)
    bar_width = ((inner_x1 - inner_x0) - total_spacing) / num_bars

    max_value = max(mileage_per_month) if mileage_per_month else 1
    max_value = 1 if max_value == 0 else max_value

    for i, val in enumerate(mileage_per_month):
        bar_height = int((val / max_value) * bar_max_height)
        x0 = inner_x0 + spacing + i * (bar_width + spacing)
        x1 = x0 + bar_width
        bar_bottom = bars_bottom
        bar_top = bar_bottom - bar_height
        draw.rounded_rectangle(
            [x0, bar_top, x1, bar_bottom], radius=2, fill=STRAVA_ORANGE
        )

        # Month label
        month_bbox = draw.textbbox((0, 0), months[i], font=LABEL_FONT)
        month_w = month_bbox[2] - month_bbox[0]
        month_x = x0 + (bar_width - month_w) // 2
        month_y = bar_bottom + 4
        draw.text(
            (month_x, month_y), months[i], font=LABEL_FONT, fill=LABEL_COLOR
        )

    return card_y1


# =========================
# Latest Activity Card
# =========================
def draw_latest_activity(
    draw: ImageDraw.Draw,
    latest_activity: Dict,
    left_width: int,
    width: int,
    top_offset: int,
):
    # Card coordinates
    card_x0 = left_width + MARGIN_LEFT
    card_y0 = top_offset + CARD_SPACING
    card_x1 = width - MARGIN_RIGHT
    card_y1 = card_y0 + 149  # make this shorter, adjust as needed
    draw_card(draw, card_x0, card_y0, card_x1, card_y1)

    # Inner area
    inner_x0 = card_x0 + INNER_PADDING
    inner_y0 = card_y0 + INNER_PADDING
    inner_y1 = card_y1 - INNER_PADDING

    # Title and date
    title_text = latest_activity.get("title", "")
    draw.text(
        (inner_x0, inner_y0),
        title_text,
        font=LATEST_TITLE_FONT,
        fill=TEXT_COLOR,
    )
    title_bbox = draw.textbbox((0, 0), title_text, font=LATEST_TITLE_FONT)
    date_text = latest_activity.get("date", "")
    date_y = inner_y0 + (title_bbox[3] - title_bbox[1]) + 6
    draw.text((inner_x0, date_y), date_text, font=DATE_FONT, fill=LABEL_COLOR)

    # Metrics (Distance, Time, Pace)
    metrics = [
        ("Distance", f"{latest_activity.get('miles',0):.2f} mi"),
        ("Time", latest_activity.get("time", "0:00")),
        ("Pace", latest_activity.get("pace", "0:00")),
    ]

    spacing_between_blocks = 60
    vertical_padding = 8
    panel_top = date_y + 10
    panel_bottom = inner_y1
    panel_height = panel_bottom - panel_top

    block_widths, x_positions = [], []
    current_x = inner_x0
    for label, value in metrics:
        value_text = (
            f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
        )
        value_bbox = draw.textbbox((0, 0), value_text, font=METRIC_VALUE_FONT)
        label_bbox = draw.textbbox((0, 0), label, font=LABEL_FONT)
        block_width = max(
            value_bbox[2] - value_bbox[0], label_bbox[2] - label_bbox[0]
        )
        block_widths.append(block_width)
        x_positions.append(current_x)
        current_x += block_width + spacing_between_blocks

    for i, (label, value) in enumerate(metrics):
        x = x_positions[i]
        value_text = (
            f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
        )
        value_bbox = draw.textbbox((0, 0), value_text, font=METRIC_VALUE_FONT)
        label_bbox = draw.textbbox((0, 0), label, font=LABEL_FONT)
        value_h = value_bbox[3] - value_bbox[1]
        label_h = label_bbox[3] - label_bbox[1]
        block_height = value_h + vertical_padding + label_h
        y_top = panel_top + (panel_height - block_height) // 2
        draw.text(
            (x, y_top), value_text, font=METRIC_VALUE_FONT, fill=TEXT_COLOR
        )
        draw.text(
            (x + 1, y_top + value_h + vertical_padding + 8),
            label,
            font=LABEL_FONT,
            fill=LABEL_COLOR,
        )

    # Draw vertical dividers between metrics
    for i in range(len(metrics) - 1):
        x0 = (
            x_positions[i]
            + block_widths[i]
            + (x_positions[i + 1] - (x_positions[i] + block_widths[i])) // 2
        )
        draw.line(
            [(x0, panel_top + 30), (x0, panel_bottom - 5)],
            fill="#E0E0E0",
            width=1,
        )


# =========================
# Main render
# =========================
def render(
    total_mileage: int,
    weekly_mileage: int,
    activities: int,
    mileage_per_month: List[int],
    latest_activity: Dict,
    black=False,
) -> PILImage:

    WIDTH, HEIGHT = 800, 480
    HEADER_HEIGHT = 60

    if black:
        global STRAVA_ORANGE
        STRAVA_ORANGE = TEXT_COLOR

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw_header(draw, WIDTH, HEADER_HEIGHT)
    left_width = draw_left_column(
        draw,
        total_mileage,
        weekly_mileage,
        activities,
        WIDTH,
        HEIGHT,
        HEADER_HEIGHT,
    )
    graph_bottom = draw_monthly_graph(
        draw, mileage_per_month, left_width, WIDTH, HEADER_HEIGHT, HEIGHT
    )
    draw_latest_activity(
        draw, latest_activity, left_width, WIDTH, top_offset=graph_bottom
    )

    return img
