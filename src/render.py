import os
import data
from data import refresh_activities
from config import ACCENT_COLOR, DARK_MODE
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as PILImage
from typing import List, Dict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "..", "assets")

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

LIGHT_BG_COLOR = "#FAFAFA"
LIGHT_TEXT_COLOR = "#000000"
LIGHT_LABEL_COLOR = "#888888"
LIGHT_CARD_COLOR = "#FFFFFF"
LIGHT_BORDER_COLOR = "#E0E0E0"

DARK_BG_COLOR = "#1A1A1A"
DARK_TEXT_COLOR = "#E0E0E0"
DARK_LABEL_COLOR = "#999999"
DARK_CARD_COLOR = "#2B2B2B"
DARK_BORDER_COLOR = "#404040"


class Renderer:
    BASE_WIDTH = 800
    BASE_HEIGHT = 480

    LEFT_COLUMN_WIDTH_RATIO = 3
    STREAK_CARD_WIDTH_RATIO = 4

    def __init__(
        self,
        width: int,
        height: int,
        accent_color: str = ACCENT_COLOR,
        dark_mode: bool = DARK_MODE,
    ):
        self.width = width
        self.height = height
        self.accent_color = accent_color
        self.dark_mode = dark_mode

        self.scale = min(width / self.BASE_WIDTH, height / self.BASE_HEIGHT)

        self.header_height = self._sc(75)
        self.bottom_row_height = self._sc(149)
        self.graph_bottom_offset = self._sc(175)
        self.margin = self._sc(10)
        self.inner_padding = self._sc(12)
        self.card_spacing = self._sc(15)
        self.title_bottom_padding = self._sc(14)
        self.bar_label_threshold = self._sc(25)

        if dark_mode:
            self.bg_color = DARK_BG_COLOR
            self.text_color = DARK_TEXT_COLOR
            self.label_color = DARK_LABEL_COLOR
            self.card_color = DARK_CARD_COLOR
            self.border_color = DARK_BORDER_COLOR
        else:
            self.bg_color = LIGHT_BG_COLOR
            self.text_color = LIGHT_TEXT_COLOR
            self.label_color = LIGHT_LABEL_COLOR
            self.card_color = LIGHT_CARD_COLOR
            self.border_color = LIGHT_BORDER_COLOR

        self.font_bold_small = ImageFont.truetype(
            os.path.join(ASSETS_DIR, "segoeuib.ttf"), self._sc(16)
        )
        self.font_bold_medium = ImageFont.truetype(
            os.path.join(ASSETS_DIR, "segoeuib.ttf"), self._sc(22)
        )
        self.font_bold_large = ImageFont.truetype(
            os.path.join(ASSETS_DIR, "segoeuib.ttf"), self._sc(28)
        )
        self.font_bold_xlarge = ImageFont.truetype(
            os.path.join(ASSETS_DIR, "segoeuib.ttf"), self._sc(48)
        )
        self.font_regular_small = ImageFont.truetype(
            os.path.join(ASSETS_DIR, "segoeui.ttf"), self._sc(16)
        )
        self.font_regular_medium = ImageFont.truetype(
            os.path.join(ASSETS_DIR, "segoeui.ttf"), self._sc(32)
        )
        self.font_regular_large = ImageFont.truetype(
            os.path.join(ASSETS_DIR, "segoeui.ttf"), self._sc(48)
        )

    def _sc(self, value: float) -> int:
        return round(value * self.scale)

    def _text_size(self, draw: ImageDraw.Draw, text: str, font) -> tuple[int, int]:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def _draw_text_centered(
        self, draw: ImageDraw.Draw, text: str, font, center_x: int, y: int, color: str
    ):
        bbox = draw.textbbox((0, 0), text, font=font)
        x = center_x - (bbox[2] - bbox[0]) // 2 - bbox[0]
        draw.text((x, y), text, font=font, fill=color)

    def _draw_card(self, draw: ImageDraw.Draw, x0: int, y0: int, x1: int, y1: int):
        draw.rounded_rectangle(
            [x0, y0, x1, y1], radius=self._sc(8), fill=self.card_color
        )
        draw.rounded_rectangle(
            [x0, y0, x1, y1], radius=self._sc(8), outline=self.border_color, width=1
        )

    def _colorize_icon(self, icon: Image.Image, hex_color: str) -> Image.Image:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        icon = icon.convert("RGBA")
        pixels = icon.load()
        for y in range(icon.height):
            for x in range(icon.width):
                pr, pg, pb, pa = pixels[x, y]
                brightness = (pr + pg + pb) / 3
                pixels[x, y] = (r, g, b, int((1 - brightness / 255) * pa))
        return icon

    def _draw_header(self, draw: ImageDraw.Draw):
        draw.rectangle(
            [(0, 0), (self.width, self.header_height)], fill=self.accent_color
        )
        w, h = self._text_size(draw, "Strava Dashboard", self.font_bold_large)
        x = (self.width - w) // 2
        y = (self.header_height - h) // 2 + self._sc(5)
        draw.text(
            (x, y), "Strava Dashboard", font=self.font_bold_large, fill=self.bg_color
        )

    def _draw_stat(
        self,
        draw: ImageDraw.Draw,
        value,
        label: str,
        center_x: int,
        y: int,
        decimal: bool,
    ):
        value_text = f"{value:.2f}" if decimal else str(value)
        _, value_h = self._text_size(draw, value_text, self.font_regular_large)
        self._draw_text_centered(
            draw, value_text, self.font_regular_large, center_x, y, self.text_color
        )
        self._draw_text_centered(
            draw,
            label,
            self.font_regular_small,
            center_x,
            y + value_h + self._sc(25),
            self.label_color,
        )

    def _draw_left_column(
        self, draw: ImageDraw.Draw, total_mileage, weekly_mileage, activities
    ) -> int:
        left_width = self.width // self.LEFT_COLUMN_WIDTH_RATIO
        x0 = self.margin
        y0 = self.header_height + self.margin
        x1 = left_width - self.margin + self._sc(5)
        y1 = self.height - self.margin
        self._draw_card(draw, x0, y0, x1, y1)

        title = f"{datetime.now().year} Stats"
        title_x = x0 + self.inner_padding
        title_y = y0 + self.inner_padding
        draw.text(
            (title_x, title_y), title, font=self.font_bold_medium, fill=self.text_color
        )

        _, title_h = self._text_size(draw, title, self.font_bold_medium)
        metrics_top = title_y + title_h + self.title_bottom_padding
        section_h = (y1 - metrics_top - self.inner_padding) / 3
        center_x = (x0 + x1) // 2

        stats = [
            (total_mileage, "Miles", True),
            (weekly_mileage, "Miles per Week", True),
            (activities, "Activities", False),
        ]

        for i, (value, label, decimal) in enumerate(stats):
            value_text = f"{value:.2f}" if decimal else str(value)
            _, value_h = self._text_size(draw, value_text, self.font_regular_large)
            _, label_h = self._text_size(draw, label, self.font_regular_small)
            block_h = value_h + self._sc(20) + label_h
            section_center_y = metrics_top + i * section_h + section_h / 2
            self._draw_stat(
                draw,
                value,
                label,
                center_x,
                section_center_y - block_h / 2 - self._sc(10),
                decimal,
            )

        for i in range(1, 3):
            y = metrics_top + i * section_h
            draw.line(
                [
                    (x0 + self.inner_padding + self._sc(20), y),
                    (x1 - self.inner_padding - self._sc(20), y),
                ],
                fill=self.border_color,
                width=1,
            )

        return left_width

    def _draw_monthly_graph(
        self, draw: ImageDraw.Draw, mileage_per_month: List[float], left_width: int
    ) -> int:
        x0 = left_width + self.margin
        y0 = self.header_height + self.margin
        x1 = self.width - self.margin
        y1 = self.height - self.graph_bottom_offset
        self._draw_card(draw, x0, y0, x1, y1)

        inner_y0 = y0 + self.inner_padding
        inner_y1 = y1 - self.inner_padding

        title_x = x0 + self.inner_padding - self._sc(2)
        draw.text(
            (title_x, inner_y0),
            "Monthly Mileage",
            font=self.font_bold_medium,
            fill=self.text_color,
        )
        _, title_h = self._text_size(draw, "Monthly Mileage", self.font_bold_medium)

        bars_top = inner_y0 + title_h + self.inner_padding + self._sc(10)
        bars_bottom = inner_y1 - self._sc(20)
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
                [bx0, bar_top, bx1, bars_bottom],
                radius=self._sc(2),
                fill=self.accent_color,
            )

            if val > 0:
                val_text = str(round(val))
                val_w, _ = self._text_size(draw, val_text, self.font_bold_small)
                val_x = bx0 + (bar_width - val_w) // 2
                if bar_h > self.bar_label_threshold:
                    draw.text(
                        (val_x, bar_top + self._sc(4)),
                        val_text,
                        font=self.font_bold_small,
                        fill=self.bg_color,
                    )
                else:
                    draw.text(
                        (val_x, bar_top - self._sc(14)),
                        val_text,
                        font=self.font_bold_small,
                        fill=self.text_color,
                    )

            month_w, _ = self._text_size(draw, MONTHS[i], self.font_regular_small)
            month_x = bx0 + (bar_width - month_w) // 2
            draw.text(
                (month_x, bars_bottom + self._sc(4)),
                MONTHS[i],
                font=self.font_regular_small,
                fill=self.label_color,
            )

        return y1

    def _draw_streak(
        self,
        draw: ImageDraw.Draw,
        img: Image.Image,
        streak: int,
        left_width: int,
        top_offset: int,
    ):
        right_area_width = self.width - self.margin - (left_width + self.margin)
        area_x0 = (
            self.width
            - self.margin
            - right_area_width // self.STREAK_CARD_WIDTH_RATIO
            + self.card_spacing
        )
        area_x1 = self.width - self.margin
        area_y0 = top_offset + self.card_spacing
        area_y1 = area_y0 + self.bottom_row_height
        area_w = area_x1 - area_x0

        fire_raw = Image.open(os.path.join(ASSETS_DIR, "fire.png")).convert("RGBA")

        label_w, label_h = self._text_size(draw, "Weeks", self.font_bold_small)
        label_y = area_y1 - self.inner_padding - label_h
        fire_zone_h = label_y - self._sc(4) - area_y0
        if fire_zone_h <= 0:
            return

        fire_scale = fire_zone_h / fire_raw.height
        fire_w = int(fire_raw.width * fire_scale)
        fire_h = int(fire_raw.height * fire_scale)
        fire_img = self._colorize_icon(
            fire_raw.resize((fire_w, fire_h), Image.Resampling.LANCZOS),
            self.accent_color,
        )

        img.paste(
            fire_img,
            (area_x0 + (area_w - fire_w) // 2, area_y0 + (fire_zone_h - fire_h) // 2),
            fire_img,
        )

        streak_text = str(streak)
        streak_w, streak_h = self._text_size(draw, streak_text, self.font_bold_xlarge)
        text_x = area_x0 + (area_w - streak_w) // 2
        text_y = area_y0 + (fire_zone_h - streak_h) // 2 + self._sc(5)
        draw.text(
            (text_x, text_y),
            streak_text,
            font=self.font_bold_xlarge,
            fill=self.bg_color,
        )

        label_x = area_x0 + (area_w - label_w) // 2
        draw.text(
            (label_x, label_y),
            "Weeks",
            font=self.font_bold_small,
            fill=self.accent_color,
        )

    def _draw_latest_activity(
        self,
        draw: ImageDraw.Draw,
        img: Image.Image,
        activity: Dict,
        left_width: int,
        top_offset: int,
    ):
        right_area_width = self.width - self.margin - (left_width + self.margin)
        x0 = left_width + self.margin
        y0 = top_offset + self.card_spacing
        x1 = self.width - self.margin - right_area_width // self.STREAK_CARD_WIDTH_RATIO
        y1 = y0 + self.bottom_row_height
        self._draw_card(draw, x0, y0, x1, y1)

        inner_x = x0 + self.inner_padding
        inner_y0 = y0 + self.inner_padding
        inner_y1 = y1 - self.inner_padding

        title = activity.get("title", "")
        if len(title) > 23:
            title = title[:23].rstrip() + "..."
        draw.text(
            (inner_x, inner_y0), title, font=self.font_bold_medium, fill=self.text_color
        )
        _, title_h = self._text_size(draw, title, self.font_bold_medium)

        pr = activity.get("pr")
        if pr:
            medal_raw = Image.open(os.path.join(ASSETS_DIR, "medal.png")).convert(
                "RGBA"
            )
            medal_h = self._sc(36)
            medal_w = int(medal_raw.width * (medal_h / medal_raw.height))
            medal_img = medal_raw.resize((medal_w, medal_h), Image.Resampling.LANCZOS)
            pr_w, _ = self._text_size(draw, pr, self.font_regular_small)
            block_w = max(medal_w, pr_w)
            block_left = x1 - self.inner_padding - block_w
            img.paste(
                medal_img,
                (block_left + (block_w - medal_w) // 2, inner_y0),
                medal_img,
            )
            draw.text(
                (block_left + (block_w - pr_w) // 2, inner_y0 + medal_h),
                pr,
                font=self.font_regular_small,
                fill=self.label_color,
            )

        date_y = inner_y0 + title_h + self._sc(6)
        draw.text(
            (inner_x, date_y + self._sc(5)),
            activity.get("date", ""),
            font=self.font_regular_small,
            fill=self.label_color,
        )

        metrics = [
            ("Distance (mi)", f"{activity.get('miles', 0):.2f}"),
            ("Time", activity.get("time", "0:00")),
            ("Pace", activity.get("pace", "0:00")),
        ]

        section_padding = self._sc(12)
        panel_top = date_y + self._sc(10)
        panel_h = inner_y1 - panel_top

        section_widths = []
        for label, value in metrics:
            value_w, _ = self._text_size(draw, str(value), self.font_regular_medium)
            label_w, _ = self._text_size(draw, label, self.font_regular_small)
            section_widths.append(max(value_w, label_w) + section_padding * 2)

        x_cursor = inner_x
        for i, (label, value) in enumerate(metrics):
            value_w, value_h = self._text_size(
                draw, str(value), self.font_regular_medium
            )
            _, label_h = self._text_size(draw, label, self.font_regular_small)
            block_h = value_h + self._sc(8) + label_h
            y_top = panel_top + (panel_h - block_h) // 2
            x = x_cursor + (section_padding if i > 0 else 1)

            draw.text(
                (x, y_top),
                str(value),
                font=self.font_regular_medium,
                fill=self.text_color,
            )
            draw.text(
                (x, y_top + value_h + self._sc(16)),
                label,
                font=self.font_regular_small,
                fill=self.label_color,
            )

            x_cursor += section_widths[i]

            if i < len(metrics) - 1:
                draw.line(
                    [
                        (x_cursor, panel_top + self._sc(30)),
                        (x_cursor, inner_y1 - self._sc(5)),
                    ],
                    fill=self.border_color,
                    width=1,
                )

    def render(
        self,
        total_mileage: float,
        weekly_mileage: float,
        activities: int,
        mileage_per_month: List[float],
        latest_activity: Dict,
        streak: int = 0,
    ) -> PILImage:
        img = Image.new("RGB", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)

        self._draw_header(draw)
        left_width = self._draw_left_column(
            draw, total_mileage, weekly_mileage, activities
        )
        graph_bottom = self._draw_monthly_graph(draw, mileage_per_month, left_width)
        self._draw_latest_activity(
            draw, img, latest_activity, left_width, top_offset=graph_bottom
        )
        self._draw_streak(draw, img, streak, left_width, top_offset=graph_bottom)

        return img


def generate_image(width: int, height: int) -> PILImage:
    (
        total_activities,
        total_miles,
        avg_weekly_miles,
        miles_per_month,
        latest_activity,
    ) = refresh_activities()
    renderer = Renderer(width, height)
    return renderer.render(
        total_miles,
        avg_weekly_miles,
        total_activities,
        miles_per_month,
        latest_activity,
        data.streak_cache,
    )


def generate_sleep_image(width: int, height: int) -> PILImage:
    return Image.new("RGB", (width, height), color="black")
