import json
import re
import urllib.parse

def parse_llm_json(raw_output: str) -> dict:
    """Parses JSON from LLM output using regex."""
    match = re.search(r"\{.*\}", raw_output, re.DOTALL)
    if not match:
        raise ValueError(f"Could not find JSON in response: {raw_output}")
    try:
        data = json.loads(match.group())
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON: {e}")

import requests
from bs4 import BeautifulSoup

def get_image_urls(image_query: str) -> list:
    """Fetches up to 5 image URLs from top search engine results based on the query."""
    if not image_query or not isinstance(image_query, str) or image_query.lower() == "not available":
        return []
    
    # We use Bing Images as it does not aggressively block headless Python requests like Google
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(image_query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    try:
        html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html, 'html.parser')
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and 'OIP' in src:
                images.append(src)
                if len(images) == 5:
                    break
        return images
    except Exception as e:
        print(f"Error fetching images: {e}")
        return []

import os
import base64
import textwrap
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

def generate_flowchart_img(flowchart_data) -> str:
    """Generates a Base64 PNG flowchart image from LLM output steps using Matplotlib.
    Boxes auto-size to fit full text with wrapping. No truncation."""
    steps = []
    if isinstance(flowchart_data, list):
        steps = [str(s).strip() for s in flowchart_data if str(s).strip()]
    elif isinstance(flowchart_data, str):
        if '->' in flowchart_data:
            steps = [s.strip() for s in flowchart_data.split('->') if s.strip()]
        elif '\n' in flowchart_data:
            steps = [s.strip('- \t') for s in flowchart_data.split('\n') if s.strip('- \t')]
        else:
            steps = [flowchart_data]

    if not steps:
        return ""

    try:
        # --- Layout config ---
        BOX_W = 5.0          # inches, fixed width for all boxes
        FONT_SIZE = 10
        CHARS_PER_LINE = 42  # wrap at this many chars
        LINE_H = 0.28        # height per wrapped line (inches)
        PAD_V = 0.22         # vertical padding inside box
        ARROW_H = 0.45       # space for arrow between boxes
        MARGIN_X = 1.0       # left/right margin
        TITLE_BAND = 0.2     # small top margin (no title text in image)
        MARGIN_BOTTOM = 0.3  # space at bottom

        # Build all labels (Start, steps..., End)
        all_labels = ["START"] + [f"{i+1}. {s}" for i, s in enumerate(steps)] + ["END"]
        all_is_terminal = [True] + [False]*len(steps) + [True]

        # Pre-calculate wrapped lines & box heights for each node
        wrapped = []
        box_heights = []
        for label in all_labels:
            lines = textwrap.wrap(label, width=CHARS_PER_LINE) or [label]
            wrapped.append(lines)
            h = len(lines) * LINE_H + 2 * PAD_V
            box_heights.append(max(h, 0.5))

        # Total figure height — title band + all boxes + arrows + bottom margin
        total_h = TITLE_BAND + sum(box_heights) + ARROW_H * (len(all_labels) - 1) + MARGIN_BOTTOM
        fig_w = BOX_W + 2 * MARGIN_X
        fig_h = max(total_h, 3.0)

        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        ax.set_xlim(0, fig_w)
        ax.set_ylim(0, fig_h)
        ax.axis('off')
        fig.patch.set_facecolor('#F0F4FF')

        # Colors
        TERMINAL_COLOR = '#4F46E5'   # indigo for start/end
        BOX_COLOR = '#FFFFFF'
        BORDER_COLOR = '#6366F1'
        TEXT_COLOR_TERM = '#FFFFFF'
        TEXT_COLOR_BOX = '#1E1B4B'
        ARROW_COLOR = '#4F46E5'

        cx = fig_w / 2  # horizontal center
        y_cursor = fig_h - TITLE_BAND  # start below the reserved top margin

        box_centers_y = []  # center y of each box for arrow drawing

        for i, (lines, bh, is_term) in enumerate(zip(wrapped, box_heights, all_is_terminal)):
            top_y = y_cursor
            bot_y = top_y - bh
            center_y = (top_y + bot_y) / 2
            box_centers_y.append(center_y)

            left_x = cx - BOX_W / 2

            if is_term:
                # Rounded pill / terminal shape
                fancy = FancyBboxPatch(
                    (left_x, bot_y), BOX_W, bh,
                    boxstyle="round,pad=0.12",
                    linewidth=2,
                    edgecolor=TERMINAL_COLOR,
                    facecolor=TERMINAL_COLOR,
                    zorder=3
                )
                ax.add_patch(fancy)
                txt_color = TEXT_COLOR_TERM
            else:
                # Rectangular box with border
                fancy = FancyBboxPatch(
                    (left_x, bot_y), BOX_W, bh,
                    boxstyle="round,pad=0.05",
                    linewidth=1.5,
                    edgecolor=BORDER_COLOR,
                    facecolor=BOX_COLOR,
                    zorder=3
                )
                ax.add_patch(fancy)
                txt_color = TEXT_COLOR_BOX

            # Text: center all wrapped lines
            label_text = '\n'.join(lines)
            ax.text(
                cx, center_y, label_text,
                ha='center', va='center',
                fontsize=FONT_SIZE,
                color=txt_color,
                fontweight='bold' if is_term else 'normal',
                wrap=False,
                zorder=4,
                multialignment='center'
            )

            y_cursor = bot_y  # move down

            # Draw arrow to next box
            if i < len(all_labels) - 1:
                arrow_top = bot_y
                arrow_bot = bot_y - ARROW_H
                ax.annotate(
                    '', 
                    xy=(cx, arrow_bot + 0.04),
                    xytext=(cx, arrow_top),
                    arrowprops=dict(
                        arrowstyle='->', 
                        color=ARROW_COLOR, 
                        lw=2,
                        mutation_scale=16
                    ),
                    zorder=2
                )
                y_cursor = arrow_bot

        plt.tight_layout(pad=0.1)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close(fig)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode('utf-8')
        return b64

    except Exception as e:
        print(f"Error generating flowchart: {e}")
        import traceback; traceback.print_exc()
        return ""
