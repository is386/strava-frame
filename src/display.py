from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as PILImage
from typing import List, Dict


HEADER_FONT = ImageFont.truetype("assets/segoeuib.ttf", 28)
YEAR_METRIC_VALUE_FONT = ImageFont.truetype("assets/segoeui.ttf", 48)
LABEL_FONT = ImageFont.truetype("assets/segoeui.ttf", 16)
LATEST_TITLE_FONT = ImageFont.truetype("assets/segoeuib.ttf", 22)
METRIC_VALUE_FONT = ImageFont.truetype("assets/segoeui.ttf", 36)
DATE_FONT = ImageFont.truetype("assets/segoeui.ttf", 18)


def draw_header(draw: ImageDraw.Draw, width: int, header_height: int):
    draw.rectangle([(0, 0), (width, header_height)], fill=0)
    now = datetime.now()
    title = f"Strava Dashboard {now.year}"
    bbox = draw.textbbox((0, 0), title, font=HEADER_FONT)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (width - text_w) // 2
    text_y = (header_height - text_h) // 2 - bbox[1]
    draw.text((text_x, text_y), title, font=HEADER_FONT, fill=255)


def draw_metric(
    draw: ImageDraw.Draw, center_x: int, y: int, number, label, show_dec=True
):
    if show_dec:
        num_text = f"{number:.2f}"
    else:
        num_text = str(number)

    num_bbox = draw.textbbox((0, 0), num_text, font=YEAR_METRIC_VALUE_FONT)
    num_w = num_bbox[2] - num_bbox[0]
    num_h = num_bbox[3] - num_bbox[1]
    num_x = center_x - num_w // 2
    draw.text((num_x, y), num_text, font=YEAR_METRIC_VALUE_FONT, fill=0)

    label_bbox = draw.textbbox((0, 0), label, font=LABEL_FONT)
    label_w = label_bbox[2] - label_bbox[0]
    label_x = center_x - label_w // 2
    label_y = y + num_h + 22
    draw.text((label_x, label_y), label, font=LABEL_FONT, fill=128)


def draw_left_column(
    draw: ImageDraw.Draw,
    total_mileage,
    weekly_mileage,
    activities,
    width,
    header_height,
    height,
):
    LEFT_COLUMN_WIDTH = width // 3
    COLUMN_CENTER_X = LEFT_COLUMN_WIDTH // 2
    START_Y = header_height + 25
    METRIC_SPACING = (height - header_height) / 3

    draw_metric(draw, COLUMN_CENTER_X, START_Y, total_mileage, "Miles")
    draw_metric(
        draw,
        COLUMN_CENTER_X,
        START_Y + METRIC_SPACING,
        weekly_mileage,
        "Miles per Week",
    )
    draw_metric(
        draw,
        COLUMN_CENTER_X,
        START_Y + 2 * METRIC_SPACING,
        activities,
        "Activities",
        show_dec=False,
    )

    # Vertical divider
    divider_x = LEFT_COLUMN_WIDTH
    draw.line(
        [(divider_x, header_height + 10), (divider_x, height - 20)],
        fill=180,
        width=1,
    )

    return LEFT_COLUMN_WIDTH


def draw_monthly_graph(
    draw: ImageDraw.Draw,
    mileage_per_month: List[int],
    left_column_width: int,
    width: int,
    header_height: int,
):
    RIGHT_WIDTH = width - left_column_width - 40
    TOP_HEIGHT = (480 - header_height - 40) // 2
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

    bar_width = RIGHT_WIDTH // 12 - 8
    max_value = max(mileage_per_month) if mileage_per_month else 1
    max_value = 1 if max_value == 0 else max_value
    GRAPH_TOP = header_height + 5

    # Graph title
    graph_label = "Monthly Mileage"
    label_bbox = draw.textbbox((0, 0), graph_label, font=LABEL_FONT)
    label_w = label_bbox[2] - label_bbox[0]
    label_h = label_bbox[3] - label_bbox[1]
    label_x = left_column_width + 20 + (RIGHT_WIDTH - label_w) // 2
    label_y = GRAPH_TOP
    draw.text((label_x, label_y), graph_label, font=LABEL_FONT, fill=128)

    # Bars start
    BAR_TOP_MARGIN = 5
    bar_top_start = label_y + label_h + BAR_TOP_MARGIN
    bar_max_height = TOP_HEIGHT - (bar_top_start - GRAPH_TOP) - 10
    GRAPH_BOTTOM = bar_top_start + bar_max_height

    for i, val in enumerate(mileage_per_month):
        bar_height = int((val / max_value) * bar_max_height)
        x0 = left_column_width + 25 + i * (bar_width + 8)
        x1 = x0 + bar_width
        bar_bottom = GRAPH_BOTTOM
        bar_top = bar_bottom - bar_height
        draw.rectangle([x0, bar_top, x1, bar_bottom], fill=0)

        # Month label
        month_bbox = draw.textbbox((0, 0), months[i], font=LABEL_FONT)
        month_w = month_bbox[2] - month_bbox[0]
        month_x = x0 + (bar_width - month_w) // 2
        month_y = bar_bottom + 2
        draw.text((month_x, month_y), months[i], font=LABEL_FONT, fill=128)

    # Horizontal divider
    LABEL_MARGIN = 4
    divider_y = GRAPH_BOTTOM + LABEL_MARGIN + label_h + 15
    draw.line(
        [(left_column_width + 20, divider_y), (width - 20, divider_y)],
        fill=180,
        width=1,
    )
    return divider_y


def draw_latest_activity(
    draw: ImageDraw.Draw,
    latest_activity: Dict,
    left_column_width: int,
    divider_y: int,
    width: int,
    height: int,
):
    bottom_half_top = divider_y + 10
    title_x = left_column_width + 25
    title_y = bottom_half_top

    # Title
    title_text = latest_activity.get("title", "")
    title_bbox = draw.textbbox((0, 0), title_text, font=LATEST_TITLE_FONT)
    draw.text((title_x, title_y), title_text, font=LATEST_TITLE_FONT, fill=0)

    # Date
    date_text = latest_activity.get("date", "")
    date_y = title_y + (title_bbox[3] - title_bbox[1]) + 7
    draw.text((title_x, date_y), date_text, font=DATE_FONT, fill=128)

    # Metrics
    metrics = [
        ("Distance", f"{latest_activity.get('miles', 0):.2f} mi"),
        ("Time", latest_activity.get("time", "0:00")),
        ("Pace", latest_activity.get("pace", "0:00")),
    ]

    panel_left = title_x
    spacing_between_blocks = 60
    vertical_padding = 16
    panel_top = date_y + 15
    panel_bottom = height - 20
    panel_height = panel_bottom - panel_top

    # Compute block widths and positions
    block_widths, x_positions = [], []
    current_x = panel_left
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

    block_tops, block_bottoms = [], []
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
        y_bottom = y_top + block_height
        block_tops.append(y_top)
        block_bottoms.append(y_bottom)

        # Draw value and label
        draw.text((x, y_top), value_text, font=METRIC_VALUE_FONT, fill=0)
        draw.text(
            (x + 1, y_top + value_h + vertical_padding),
            label,
            font=LABEL_FONT,
            fill=128,
        )

    # Vertical dividers between blocks
    for i in range(len(metrics) - 1):
        x0 = (
            x_positions[i]
            + block_widths[i]
            + (x_positions[i + 1] - (x_positions[i] + block_widths[i])) // 2
        )
        y0 = block_tops[i] + 5
        y1 = block_bottoms[i] + 10
        draw.line([(x0, y0), (x0, y1)], fill=180, width=1)


def render(
    total_mileage: int,
    weekly_mileage: int,
    activities: int,
    mileage_per_month: List[int],
    latest_activity: Dict,
) -> PILImage:
    WIDTH, HEIGHT = 800, 480
    HEADER_HEIGHT = 60

    img = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    draw_header(draw, WIDTH, HEADER_HEIGHT)
    left_column_width = draw_left_column(
        draw,
        total_mileage,
        weekly_mileage,
        activities,
        WIDTH,
        HEADER_HEIGHT,
        HEIGHT,
    )
    divider_y = draw_monthly_graph(
        draw, mileage_per_month, left_column_width, WIDTH, HEADER_HEIGHT
    )
    draw_latest_activity(
        draw, latest_activity, left_column_width, divider_y, WIDTH, HEIGHT
    )

    return img
