from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


def render(
    total_mileage,
    weekly_mileage,
    activities,
    mileage_per_month,
    latest_activity,
):
    # =========================
    # Display configuration
    # =========================
    WIDTH, HEIGHT = 800, 480
    HEADER_HEIGHT = 60
    OUTPUT_FILE = "dashboard_preview.png"

    # =========================
    # Create grayscale canvas
    # =========================
    img = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    # =========================
    # Header background
    # =========================
    draw.rectangle([(0, 0), (WIDTH, HEADER_HEIGHT)], fill=0)

    # =========================
    # Load fonts
    # =========================
    header_font = ImageFont.truetype("assets/segoeuib.ttf", 28)
    mileage_font = ImageFont.truetype("assets/segoeui.ttf", 48)
    label_font = ImageFont.truetype("assets/segoeui.ttf", 16)

    # =========================
    # Header text (centered)
    # =========================
    now = datetime.now()
    title = f"Strava Dashboard {now.year}"
    bbox = draw.textbbox((0, 0), title, font=header_font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (WIDTH - text_w) // 2
    text_y = (HEADER_HEIGHT - text_h) // 2 - bbox[1]
    draw.text((text_x, text_y), title, font=header_font, fill=255)

    # =========================
    # Layout configuration
    # =========================
    LEFT_COLUMN_WIDTH = WIDTH // 3
    COLUMN_CENTER_X = LEFT_COLUMN_WIDTH // 2
    START_Y = HEADER_HEIGHT + 25
    METRIC_SPACING = (HEIGHT - HEADER_HEIGHT) / 3

    # =========================
    # Helper: draw stacked metric
    # =========================
    def draw_metric(center_x, y, number, label, show_dec=True):
        if show_dec:
            num_text = f"{number:.2f}"
        else:
            num_text = str(number)

        num_bbox = draw.textbbox((0, 0), num_text, font=mileage_font)
        num_w = num_bbox[2] - num_bbox[0]
        num_h = num_bbox[3] - num_bbox[1]

        num_x = center_x - num_w // 2
        draw.text((num_x, y), num_text, font=mileage_font, fill=0)

        label_bbox = draw.textbbox((0, 0), label, font=label_font)
        label_w = label_bbox[2] - label_bbox[0]
        label_x = center_x - label_w // 2
        label_y = y + num_h + 22

        draw.text((label_x, label_y), label, font=label_font, fill=128)

    # =========================
    # Draw stacked metrics (left column)
    # =========================
    draw_metric(COLUMN_CENTER_X, START_Y, total_mileage, "Miles")
    draw_metric(
        COLUMN_CENTER_X,
        START_Y + METRIC_SPACING,
        weekly_mileage,
        "Miles per Week",
    )
    draw_metric(
        COLUMN_CENTER_X,
        START_Y + 2 * METRIC_SPACING,
        activities,
        "Activities",
        show_dec=False,
    )

    # =========================
    # Vertical divider between columns
    # =========================
    divider_x = LEFT_COLUMN_WIDTH
    draw.line(
        [(divider_x, HEADER_HEIGHT + 10), (divider_x, HEIGHT - 20)],
        fill=180,
        width=1,
    )

    # =========================
    # Right column layout
    # =========================
    RIGHT_WIDTH = WIDTH - LEFT_COLUMN_WIDTH - 40
    TOP_HEIGHT = (HEIGHT - HEADER_HEIGHT - 40) // 2

    # =========================
    # Draw bar graph (top half of right column) with label
    # =========================
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
    bar_width = RIGHT_WIDTH // 12 - 8  # space between bars
    max_value = max(mileage_per_month) if mileage_per_month else 1
    max_value = 1 if max_value == 0 else max_value
    bar_max_height = TOP_HEIGHT - 30  # leave padding at top and bottom

    # Top of graph area
    GRAPH_TOP = HEADER_HEIGHT + 5  # just below header

    # Draw graph label (title)
    graph_label = "Monthly Mileage"
    label_bbox = draw.textbbox((0, 0), graph_label, font=label_font)
    label_w = label_bbox[2] - label_bbox[0]
    label_h = label_bbox[3] - label_bbox[1]
    label_x = LEFT_COLUMN_WIDTH + 20 + (RIGHT_WIDTH - label_w) // 2
    label_y = GRAPH_TOP
    draw.text((label_x, label_y), graph_label, font=label_font, fill=128)

    # Bars start a fixed distance below the title
    BAR_TOP_MARGIN = 5  # space between title and bars
    bar_top_start = label_y + label_h + BAR_TOP_MARGIN
    bar_max_height = (
        TOP_HEIGHT - (bar_top_start - GRAPH_TOP) - 10
    )  # leave bottom padding
    GRAPH_BOTTOM = bar_top_start + bar_max_height

    # Draw bars
    for i, val in enumerate(mileage_per_month):
        bar_height = int((val / max_value) * bar_max_height)
        x0 = LEFT_COLUMN_WIDTH + 25 + i * (bar_width + 8)
        x1 = x0 + bar_width
        bar_bottom = GRAPH_BOTTOM
        bar_top = bar_bottom - bar_height
        draw.rectangle([x0, bar_top, x1, bar_bottom], fill=0)

        # Month label
        month_bbox = draw.textbbox((0, 0), months[i], font=label_font)
        month_w = month_bbox[2] - month_bbox[0]
        month_x = x0 + (bar_width - month_w) // 2
        month_y = bar_bottom + 2
        draw.text((month_x, month_y), months[i], font=label_font, fill=128)

    # =========================
    # Horizontal divider under the graph
    # =========================
    LABEL_MARGIN = 4  # same as month label margin
    divider_y = (
        GRAPH_BOTTOM + LABEL_MARGIN + label_h + 15
    )  # below the month labels
    draw.line(
        [(LEFT_COLUMN_WIDTH + 20, divider_y), (WIDTH - 20, divider_y)],
        fill=180,
        width=1,
    )

    # =========================
    # Draw latest activity title in bottom half
    # =========================
    latest_title_font = ImageFont.truetype(
        "assets/segoeuib.ttf", 22
    )  # bold font
    title_text = latest_activity.get("title", "")

    # Compute position: left-aligned in right column, top of bottom half
    bottom_half_top = divider_y + 10  # small padding below divider
    title_x = LEFT_COLUMN_WIDTH + 25  # small padding from left edge
    title_y = bottom_half_top

    # Get title bounding box
    title_bbox = draw.textbbox((0, 0), title_text, font=latest_title_font)
    draw.text((title_x, title_y), title_text, font=latest_title_font, fill=0)

    # =========================
    # Draw latest activity date under the title
    # =========================
    date_text = latest_activity.get("date", "")  # string like "February 7"
    date_font = ImageFont.truetype("assets/segoeui.ttf", 18)
    date_x = title_x  # same left alignment as title
    date_y = (
        title_y + (title_bbox[3] - title_bbox[1]) + 7
    )  # 5 pixels below title

    draw.text((date_x, date_y), date_text, font=date_font, fill=128)

    # Font for metric values
    metric_value_font = ImageFont.truetype("assets/segoeui.ttf", 36)
    label_font_small = label_font  # already defined

    # Metrics to display
    metrics = [
        ("Distance", f"{latest_activity.get('miles', 0):.2f} mi"),
        ("Time", latest_activity.get("time", "0:00")),
        ("Pace", latest_activity.get("pace", "0:00")),
    ]

    # Horizontal layout
    panel_left = LEFT_COLUMN_WIDTH + 25  # left-align with title
    spacing_between_blocks = 60  # horizontal space between metric blocks
    vertical_padding = 16  # space between value and label

    # Compute width of each block
    block_widths = []
    for label, value in metrics:
        value_text = (
            f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
        )
        value_bbox = draw.textbbox((0, 0), value_text, font=metric_value_font)
        value_w = value_bbox[2] - value_bbox[0]
        label_bbox = draw.textbbox((0, 0), label, font=label_font_small)
        label_w = label_bbox[2] - label_bbox[0]
        block_widths.append(max(value_w, label_w))

    # Compute x positions of each block (left edges)
    x_positions = []
    current_x = panel_left
    for w in block_widths:
        x_positions.append(current_x)
        current_x += w + spacing_between_blocks

    # Vertical placement
    panel_top = date_y + 15
    panel_bottom = HEIGHT - 20
    panel_height = panel_bottom - panel_top

    # Draw metrics
    block_tops = []
    block_bottoms = []
    for i, (label, value) in enumerate(metrics):
        x = x_positions[i]
        value_text = (
            f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
        )
        value_bbox = draw.textbbox((0, 0), value_text, font=metric_value_font)
        value_h = value_bbox[3] - value_bbox[1]
        label_bbox = draw.textbbox((0, 0), label, font=label_font_small)
        label_h = label_bbox[3] - label_bbox[1]

        block_height = value_h + vertical_padding + label_h
        y_top = panel_top + (panel_height - block_height) // 2
        y_bottom = y_top + block_height
        block_tops.append(y_top)
        block_bottoms.append(y_bottom)

        # Draw value
        draw.text((x, y_top), value_text, font=metric_value_font, fill=0)
        # Draw label
        draw.text(
            (x + 1, y_top + value_h + vertical_padding),
            label,
            font=label_font_small,
            fill=128,
        )

    # Draw vertical dividers between blocks
    for i in range(len(metrics) - 1):
        # Divider x: halfway between the right edge of block i and left edge
        # of block i+1
        x0 = (
            x_positions[i]
            + block_widths[i]
            + (x_positions[i + 1] - (x_positions[i] + block_widths[i])) // 2
        )
        # Divider height: a bit shorter than block height so it doesn't
        # overlap text
        y0 = block_tops[i] + 5
        y1 = block_bottoms[i] + 10
        draw.line([(x0, y0), (x0, y1)], fill=180, width=1)

    # =========================
    # Save preview
    # =========================
    img.save(OUTPUT_FILE)
    print(f"Saved {OUTPUT_FILE}")
