import re
from datetime import datetime

import streamlit as st
import html
from typing import Iterable
from humanize import naturalsize
from streamlit.delta_generator import DeltaGenerator
from streamlit_js_eval import streamlit_js_eval
from streamlit_timeago import time_ago


def heading_with_value(heading: str, secondary_text: str, level: int = 2, font_weight: int = 800):
    """Heading with additional text in grey"""
    heading = html.escape(heading)
    secondary_text = html.escape(secondary_text)
    st.html(
        f'<h{level} style="font-weight: {font_weight}">{heading}&nbsp;&nbsp;<span style="font-weight: 200; color: #888888;">{secondary_text}</span></h{level}>'
    )


def subheading_with_value(heading: str, secondary_text: str, level: int = 3, font_weight: int = 600):
    return heading_with_value(heading, secondary_text, level=level, font_weight=font_weight)


def iter_progress(iterable: Iterable, text=None, total=None, **kwargs):
    """Tqdm-like wrapper that iterates over an iterable and shows a streamlit progress bar"""
    progress_bar = st.progress(0)
    if total is None:
        total = len(iterable)
    for i, item in enumerate(iterable):
        progress_bar.progress(i / total, text=text, **kwargs)
        yield item
    progress_bar.empty()


def get_approx_screen_width():
    try:
        return max(800, streamlit_js_eval(js_expressions="window.innerWidth"))
    except Exception as e:
        print("Failed to get screen width:", e)
        return 800


def approx_max_width(max_width, center=False):
    approx_content_width = get_approx_screen_width() - 150 - 100
    st.write(approx_content_width)
    if approx_content_width < max_width:
        # full-width
        return st.columns([1])[0]
    relative_width = max_width / approx_content_width
    padding = 1 - relative_width
    if center:
        return st.columns([padding / 2, relative_width, padding / 2])[1]
    else:
        return st.columns([relative_width, padding])[0]


def wrapped_columns(n: int, wrap=4, divider=False, **kwargs) -> list[DeltaGenerator]:
    """Create n columns, wrapping them every `wrap` columns. Each row will always have `wrap` columns

    :return: flat list of n columns
    """
    assert isinstance(n, int), "n must be an integer"
    rows = n // wrap + (1 if n % wrap > 0 else 0)
    columns = []
    for row in range(rows):
        if row != 0 and divider:
            st.divider()
        for c in st.columns(wrap, **kwargs):
            if len(columns) == n:
                break
            columns.append(c)
    return columns


def confirm_download_button(data, **kwargs):
    size_suffix = f" ({naturalsize(len(data))})" if len(data) > 1024 * 1024 else ""
    st.download_button("Confirm download" + size_suffix, type="primary", data=data, **kwargs)


def highlight_query(text: str, query: str) -> str:
    """Highlight all occurrences of query in text with **:primary-background[query]**"""
    if not text or not query or not query.strip():
        return text
    return re.sub(
        re.escape(query),
        lambda match: f" **:primary-background[{match.group(0)}]** ",
        text,
        flags=re.IGNORECASE,
    )


def refresh_button(key: str, text="Refresh"):
    with st.container(horizontal=True, vertical_alignment="center"):
        just_refreshed = st.button(f":material/refresh: {text}", key=f"refresh-{key}")
        with st.container(width=400):
            iframe_key = f"refreshed-{key}"
            # css to avoid margin below iframe
            st.html(
                """<style>
                   .st-key-KEY iframe { display: block; }
                   </style>""".replace("KEY", iframe_key)
            )
            time_ago(datetime.now(), prefix="Refreshed", key=iframe_key, flash=just_refreshed)
