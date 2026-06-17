from __future__ import annotations

import base64
import html
import json
import textwrap
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image


APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "data" / "payment_data.json"
APP_ICON_FILE = APP_DIR / "assets" / "app-icon.png"
APPLE_TOUCH_ICON_FILE = APP_DIR / "assets" / "apple-touch-icon.png"
FAVICON_FILE = APP_DIR / "assets" / "favicon.png"
LOGIN_BG_FILE = APP_DIR / "assets" / "login-sunset.png"
LOGIN_COVER_FILE = APP_DIR / "assets" / "login-cover-reference.jpg"
LOGIN_COVER_MOBILE_FILE = APP_DIR / "assets" / "login-cover-mobile.jpg"
LOGIN_COVER_IPAD_FILE = APP_DIR / "assets" / "login-cover-ipad.jpg"

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_ABBR = ["M", "T", "W", "T", "F", "S", "S"]
ROUTINE_SECTIONS = ["Morning Reset", "Workout", "Nutrition", "Self Care", "Evening Reset"]
MANTRAS = [
    "I do not need motivation. I need consistency.",
    "Small habits. Big results.",
    "Emotions do not decide my routine.",
    "I only have to keep one more promise today.",
    "Future me is watching, and she is proud.",
]
EMERGENCY_RESPONSES = {
    "I do not want to go to the gym": "You do not have to crush the workout. You only have to show up.",
    "I do not want to run": "Start with your shoes. Five minutes still counts as keeping the promise.",
    "I feel anxious": "Pause. Drink water. Breathe slowly. Then choose the tiniest next step.",
    "I want to skip my routine": "Do the 50% version. Discipline can be soft and still be real.",
    "I feel sad": "You are allowed to feel it. One small habit is enough to protect tomorrow's Gina.",
}

DEFAULT_ROUTINE_ACTIVITIES = [
    {"Name": "Make bed", "Section": "Morning Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": False, "Notes": ""},
    {"Name": "Ice face", "Section": "Morning Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": True, "Notes": ""},
    {"Name": "Water + creatine", "Section": "Morning Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": True, "Notes": ""},
    {"Name": "Vitamins", "Section": "Morning Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": False, "Notes": ""},
    {"Name": "High protein breakfast", "Section": "Morning Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": True, "Notes": ""},
    {"Name": "Hypopressives", "Section": "Morning Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": True, "Notes": ""},
    {"Name": "Review day plan", "Section": "Morning Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": False, "Notes": "2 min"},
    {"Name": "Legs lower body", "Section": "Workout", "Days": [0, 2, 4], "Non-negotiable": True, "Notes": ""},
    {"Name": "Arms + cardio", "Section": "Workout", "Days": [1, 3], "Non-negotiable": True, "Notes": ""},
    {"Name": "Long run", "Section": "Workout", "Days": [5], "Non-negotiable": True, "Notes": ""},
    {"Name": "Recovery walk", "Section": "Workout", "Days": [6], "Non-negotiable": False, "Notes": ""},
    {"Name": "Water goal", "Section": "Nutrition", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": True, "Notes": ""},
    {"Name": "Protein goal", "Section": "Nutrition", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": True, "Notes": ""},
    {"Name": "Hair mask", "Section": "Self Care", "Days": [0, 2, 4], "Non-negotiable": False, "Notes": ""},
    {"Name": "Sauna", "Section": "Self Care", "Days": [0, 2, 4], "Non-negotiable": False, "Notes": ""},
    {"Name": "Red light mask", "Section": "Self Care", "Days": [0, 2, 4], "Non-negotiable": False, "Notes": "PM"},
    {"Name": "Nails", "Section": "Self Care", "Days": [6], "Non-negotiable": False, "Notes": ""},
    {"Name": "Meal prep", "Section": "Self Care", "Days": [6], "Non-negotiable": False, "Notes": ""},
    {"Name": "Last meal before 8:00 PM", "Section": "Evening Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": True, "Notes": ""},
    {"Name": "Magnesium", "Section": "Evening Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": True, "Notes": ""},
    {"Name": "Skincare", "Section": "Evening Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": False, "Notes": ""},
    {"Name": "Prepare gym clothes", "Section": "Evening Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": False, "Notes": ""},
    {"Name": "Read 10 pages", "Section": "Evening Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": False, "Notes": ""},
    {"Name": "Sleep early", "Section": "Evening Reset", "Days": [0, 1, 2, 3, 4, 5, 6], "Non-negotiable": True, "Notes": ""},
]


DEFAULT_DATA = {
    "settings": {
        "pay_date": date.today().isoformat(),
        "cash_now": 0.0,
        "reserve": 0.0,
        "groceries": 0.0,
        "sofi": 0.0,
        "mom_debt": 2444342.74,
        "mom_first": True,
        "debts_first": True,
        "strategy": "APR mas alto",
    },
    "cards": [
        {"Tarjeta": "Victoria Secret", "APR %": 31.24, "Cupo": 1000.0, "Saldo": 0.0, "Dia pago": 20, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": ""},
        {"Tarjeta": "Amex Blue", "APR %": 29.24, "Cupo": 1000.0, "Saldo": 893.0, "Dia pago": 9, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": ""},
        {"Tarjeta": "TD", "APR %": 27.24, "Cupo": 1200.0, "Saldo": 1213.0, "Dia pago": 22, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": ""},
        {"Tarjeta": "Amex Amazon", "APR %": 26.49, "Cupo": 2100.0, "Saldo": 2819.0, "Dia pago": 20, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": ""},
        {"Tarjeta": "Discover", "APR %": 26.49, "Cupo": 3000.0, "Saldo": 2851.0, "Dia pago": 15, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": ""},
        {"Tarjeta": "Apple", "APR %": 26.24, "Cupo": 2000.0, "Saldo": 739.0, "Dia pago": 30, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": ""},
        {"Tarjeta": "Chase", "APR %": 0.0, "Cupo": 2500.0, "Saldo": 2052.0, "Dia pago": 8, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": "0% APR promo"},
        {"Tarjeta": "Bancolombia", "APR %": 0.0, "Cupo": 0.0, "Saldo": 1700000.0, "Dia pago": 3, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": "COP"},
    ],
    "expenses": [
        {"Categoria": "Colombia", "Nombre": "Mom allowance", "Cuenta/Tarjeta": "Checking", "Monto quincena": 85.0, "Tipo": "Fixed", "Incluir": False, "Notas": ""},
        {"Categoria": "Colombia", "Nombre": "New apartment", "Cuenta/Tarjeta": "Bancolombia", "Monto quincena": 420.0, "Tipo": "Fixed", "Incluir": False, "Notas": "Set aside each paycheck"},
        {"Categoria": "Colombia", "Nombre": "Don Guillermo rent", "Cuenta/Tarjeta": "Checking", "Monto quincena": 440.0, "Tipo": "Fixed", "Incluir": False, "Notas": "Send full amount at month end"},
        {"Categoria": "Zelle", "Nombre": "Innago / rent", "Cuenta/Tarjeta": "Checking", "Monto quincena": 1051.0, "Tipo": "Fixed", "Incluir": False, "Notas": "Set aside each paycheck"},
        {"Categoria": "Zelle", "Nombre": "Gym", "Cuenta/Tarjeta": "Checking", "Monto quincena": 80.0, "Tipo": "Fixed", "Incluir": False, "Notas": ""},
        {"Categoria": "TD", "Nombre": "Apple Bill / Cloud", "Cuenta/Tarjeta": "TD", "Monto quincena": 10.0, "Tipo": "Auto debit", "Incluir": False, "Notas": ""},
        {"Categoria": "TD", "Nombre": "Google Play / Gmail", "Cuenta/Tarjeta": "TD", "Monto quincena": 4.0, "Tipo": "Auto debit", "Incluir": False, "Notas": ""},
        {"Categoria": "Amex Amazon", "Nombre": "Amazon Prime", "Cuenta/Tarjeta": "Amex Amazon", "Monto quincena": 15.0, "Tipo": "Auto debit", "Incluir": False, "Notas": ""},
    ],
    "personal_debts": [
        {"Name": "Mom", "Amount": 2444342.74, "Priority": 1, "Include": True, "Notes": ""},
    ],
    "history": [],
    "routine": {
        "activities": DEFAULT_ROUTINE_ACTIVITIES,
        "completions": {},
        "future_me": {},
        "mantra_index": 0,
    },
}


APP_DISPLAY_NAME = "GM"


st.set_page_config(page_title=APP_DISPLAY_NAME, page_icon=Image.open(FAVICON_FILE), layout="wide")


def image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def inject_app_icon_links() -> None:
    icon_version = str(int(max(APP_ICON_FILE.stat().st_mtime, APPLE_TOUCH_ICON_FILE.stat().st_mtime, FAVICON_FILE.stat().st_mtime)))
    icon = f"/app/static/favicon.png?v={icon_version}"
    app_icon = f"/app/static/app-icon.png?v={icon_version}"
    apple_icon = f"/app/static/apple-touch-icon.png?v={icon_version}"
    manifest = {
        "name": APP_DISPLAY_NAME,
        "short_name": APP_DISPLAY_NAME,
        "description": "Routine and money planner",
        "start_url": ".",
        "scope": ".",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#ffffff",
        "icons": [
            {"src": "/app/static/apple-touch-icon.png", "sizes": "180x180", "type": "image/png", "purpose": "any maskable"},
            {"src": "/app/static/app-icon.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }
    st.markdown(
        f"""
        <link rel="icon" type="image/png" href="{icon}">
        <link rel="apple-touch-icon" href="{apple_icon}">
        <meta name="apple-mobile-web-app-title" content="{APP_DISPLAY_NAME}">
        <meta name="application-name" content="{APP_DISPLAY_NAME}">
        <meta name="theme-color" content="#ffffff">
        """,
        unsafe_allow_html=True,
    )
    components.html(
        f"""
        <script>
        (() => {{
            const head = window.parent.document.head;
            const removeExisting = [
                'link[rel="icon"]',
                'link[rel="shortcut icon"]',
                'link[rel="apple-touch-icon"]',
                'link[rel="manifest"]',
                'meta[name="apple-mobile-web-app-title"]',
                'meta[name="application-name"]',
                'meta[name="theme-color"]'
            ];
            removeExisting.forEach((selector) => {{
                head.querySelectorAll(selector).forEach((element) => element.remove());
            }});

            const addElement = (tag, attrs) => {{
                const element = window.parent.document.createElement(tag);
                Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, value));
                head.appendChild(element);
                return element;
            }};

            addElement('link', {{ rel: 'icon', type: 'image/png', sizes: '32x32', href: {json.dumps(icon)} }});
            addElement('link', {{ rel: 'shortcut icon', type: 'image/png', href: {json.dumps(icon)} }});
            addElement('link', {{ rel: 'apple-touch-icon', sizes: '180x180', href: {json.dumps(apple_icon)} }});
            addElement('meta', {{ name: 'apple-mobile-web-app-title', content: {json.dumps(APP_DISPLAY_NAME)} }});
            addElement('meta', {{ name: 'application-name', content: {json.dumps(APP_DISPLAY_NAME)} }});
            addElement('meta', {{ name: 'theme-color', content: '#ffffff' }});

            if (window.parent.__myNestEggManifestUrl) {{
                URL.revokeObjectURL(window.parent.__myNestEggManifestUrl);
            }}
            const manifest = {json.dumps(manifest)};
            const blob = new Blob([JSON.stringify(manifest)], {{ type: 'application/manifest+json' }});
            const manifestUrl = URL.createObjectURL(blob);
            window.parent.__myNestEggManifestUrl = manifestUrl;
            addElement('link', {{ rel: 'manifest', href: manifestUrl }});
            window.parent.document.title = {json.dumps(APP_DISPLAY_NAME)};
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def inject_girlie_theme() -> None:
    login_bg = image_data_uri(LOGIN_BG_FILE)
    login_cover = image_data_uri(LOGIN_COVER_FILE)
    login_cover_mobile = image_data_uri(LOGIN_COVER_MOBILE_FILE)
    login_cover_ipad = image_data_uri(LOGIN_COVER_IPAD_FILE)
    st.markdown(
        """
        <style>
        :root {
            --login-bg: url('__LOGIN_BG__');
            --login-cover: url('__LOGIN_COVER__');
            --login-cover-mobile: url('__LOGIN_COVER_MOBILE__');
            --login-cover-ipad: url('__LOGIN_COVER_IPAD__');
        }

        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,650;0,9..144,750;1,9..144,650;1,9..144,750&family=Fugaz+One&family=Inter:wght@400;500;600;700;800;900&display=swap');

        :root {
            --baby-blue: #d9f7ff;
            --lilac: #c7a4ff;
            --salmon: #ff9f8f;
            --butter: #ffe875;
            --neon-pink: #ff3cac;
            --neon-blue: #8feeff;
            --neon-lime: #c7ff3d;
            --ink: #3f2b58;
            --soft-card: rgba(255, 255, 255, .72);
            --font-display: "Fraunces", Georgia, serif;
            --font-fugaz: "Fugaz One", "Inter", sans-serif;
            --font-script: "Fraunces", Georgia, serif;
            --font-ui: "Inter", "Segoe UI", Arial, sans-serif;
            --font-apple: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 6%, rgba(255, 232, 117, .16), transparent 24%),
                radial-gradient(circle at 92% 4%, rgba(255, 159, 143, .12), transparent 28%),
                linear-gradient(180deg, #fffdfb 0%, #fffaf7 48%, #fffdfb 100%);
            color: var(--ink);
            font-family: var(--font-ui);
        }

        .stApp:has(.girlie-login) {
            min-height: 100vh;
            background: var(--login-cover), #ffffff;
            background-size: auto 100%;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }

        .stApp:has(.girlie-login) [data-testid="stHeader"] {
            display: none;
        }

        .stApp:has(.girlie-login) #MainMenu,
        .stApp:has(.girlie-login) footer,
        .stApp:has(.girlie-login) [data-testid="stToolbar"],
        .stApp:has(.girlie-login) [data-testid="stDecoration"],
        .stApp:has(.girlie-login) [data-testid="stStatusWidget"],
        .stApp:has(.girlie-login) [data-testid="stActionButton"] {
            display: none !important;
        }

        .stApp:has(.girlie-login) .block-container {
            max-width: 100vw;
            padding: 0;
        }

        .block-container {
            padding-top: 1.15rem;
            padding-bottom: 3rem;
        }

        .stApp h1, .stApp h2, .stApp h3, .stApp h4,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4 {
            color: var(--ink) !important;
            letter-spacing: 0;
            font-family: var(--font-display) !important;
            font-weight: 750 !important;
        }

        .stApp h1,
        [data-testid="stMarkdownContainer"] h1 {
            font-size: clamp(2.1rem, 5vw, 3.8rem) !important;
        }

        p, label, input, textarea, [data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] {
            font-family: var(--font-ui);
        }

        [data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.68);
            backdrop-filter: blur(14px);
        }

        [data-testid="stMetric"],
        [data-testid="stDataFrame"],
        [data-testid="stExpander"],
        div[data-testid="stFileUploader"],
        div[data-testid="stDownloadButton"] {
            border: 1px solid rgba(63, 43, 88, 0.10);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.66);
            box-shadow: none;
        }

        .credit-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(245px, 1fr));
            gap: .85rem;
            margin: .55rem 0 1rem;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: .85rem;
            margin: .4rem 0 1rem;
        }

        .summary-card {
            border: 1px solid rgba(63, 43, 88, 0.10);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.52);
            box-shadow: none;
            padding: .95rem 1rem;
            min-width: 0;
        }

        .summary-label {
            color: rgba(63, 43, 88, .72);
            font-size: .86rem;
            margin-bottom: .35rem;
        }

        .summary-value {
            color: #1f2937;
            font-family: var(--font-ui);
            font-size: clamp(1.25rem, 2.4vw, 1.65rem);
            line-height: 1.1;
            font-weight: 600;
            white-space: nowrap;
        }

        .field-card-head {
            display: flex;
            align-items: center;
            gap: .55rem;
            margin-bottom: .25rem;
        }

        .section-title {
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            color: #3f2b58;
            font-family: var(--font-display);
            font-size: clamp(1.35rem, 2.5vw, 1.72rem);
            font-weight: 800;
            margin: .1rem 0 .8rem;
            line-height: 1;
        }

        .section-title .doodle {
            color: #ff3cac;
            font-family: var(--font-script);
            font-size: 1.05em;
            font-weight: 400;
            text-shadow: 0 0 14px rgba(255, 60, 172, .22);
        }

        .section-title .underline {
            border-bottom: 2px solid rgba(124, 58, 237, .36);
            padding-bottom: .08rem;
        }

        div[data-testid="stVerticalBlock"]:has(.section-shell-marker) {
            position: relative;
            padding: .95rem 0 1.1rem;
            border: 0;
            border-top: 1px solid rgba(63, 43, 88, .10);
            border-radius: 0;
            background: transparent;
            box-shadow: none;
            overflow: visible;
        }

        div[data-testid="stVerticalBlock"]:has(.paycheck-shell)::after {
            content: "♡";
            position: absolute;
            right: 1rem;
            top: 2.25rem;
            width: 1.5rem;
            height: 1.5rem;
            border-radius: 50%;
            display: grid;
            place-items: center;
            color: #ff3cac;
            background: rgba(255, 232, 117, .26);
            box-shadow: none;
            font-family: var(--font-script);
            pointer-events: none;
        }

        div[data-testid="stVerticalBlock"]:has(.debt-shell)::before {
            content: "✣";
            position: absolute;
            left: -.65rem;
            top: 4.8rem;
            color: rgba(255, 60, 172, .35);
            font-size: 1.6rem;
            pointer-events: none;
        }

        div[data-testid="stVerticalBlock"]:has(.debt-shell)::after {
            content: "✣";
            position: absolute;
            right: -.55rem;
            top: 7.3rem;
            color: rgba(255, 60, 172, .28);
            font-size: 1.2rem;
            pointer-events: none;
        }

        .field-card-icon,
        .mini-card-icon {
            display: inline-flex;
            width: 2.1rem;
            height: 2.1rem;
            border-radius: 999px;
            align-items: center;
            justify-content: center;
            font-family: var(--font-ui);
            font-size: 1rem;
            font-weight: 900;
        }

        .field-card-icon.purple, .mini-card-icon.purple { color: #7c3aed; background: rgba(124, 58, 237, .12); }
        .field-card-icon.pink, .mini-card-icon.pink { color: #ff2f9f; background: rgba(255, 47, 159, .12); }
        .field-card-icon.blue, .mini-card-icon.blue { color: #2f8cff; background: rgba(47, 140, 255, .12); }
        .field-card-icon.teal, .mini-card-icon.teal { color: #10a7a0; background: rgba(16, 167, 160, .12); }
        .field-card-icon.orange, .mini-card-icon.orange { color: #ff7a1a; background: rgba(255, 122, 26, .12); }
        .field-card-icon.yellow, .mini-card-icon.yellow { color: #f6a800; background: rgba(255, 193, 7, .16); }

        .field-card-label {
            color: rgba(63, 43, 88, .78);
            font-size: .76rem;
            font-weight: 800;
            line-height: 1.15;
        }

        div[data-testid="stVerticalBlock"]:has(.field-card-marker) {
            min-height: 6.85rem;
            padding: .8rem .85rem .72rem;
            border: 1px solid rgba(63, 43, 88, .09);
            border-radius: 8px;
            background: rgba(255,255,255,.48);
            box-shadow: none;
        }

        div[data-testid="stVerticalBlock"]:has(.field-card-marker) [data-testid="stWidgetLabel"] {
            display: none;
        }

        div[data-testid="stVerticalBlock"]:has(.field-card-marker) input {
            color: #352153;
            font-weight: 850;
        }

        div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.field-card-marker) {
            padding: 0;
            border: 0;
            border-radius: 0;
            background: transparent;
            box-shadow: none;
        }

        div[data-testid="stVerticalBlock"]:has(.section-shell-marker) {
            padding: .95rem 0 1.1rem;
            border: 0;
            border-top: 1px solid rgba(63, 43, 88, .10);
            border-radius: 0;
            background: transparent;
            box-shadow: none;
        }

        .debt-total-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: .65rem;
            margin: .25rem 0 .7rem;
        }

        .mini-card {
            display: flex;
            align-items: center;
            gap: .75rem;
            border: 1px solid rgba(63, 43, 88, .09);
            border-radius: 8px;
            background: rgba(255,255,255,.48);
            padding: .85rem .95rem;
            box-shadow: none;
            min-width: 0;
        }

        .mini-card-label {
            color: rgba(63, 43, 88, .72);
            font-size: .75rem;
            font-weight: 850;
        }

        .mini-card-value {
            color: #3f2b58;
            font-size: 1.05rem;
            font-weight: 900;
            white-space: nowrap;
        }

        .debt-row-card {
            display: grid;
            grid-template-columns: auto 1fr auto auto;
            align-items: center;
            gap: .75rem;
            border-bottom: 1px dashed rgba(255, 47, 159, .22);
            padding: .75rem .35rem .85rem;
            margin-bottom: .2rem;
        }

        .debt-row-name {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: 1rem;
            font-weight: 780;
            line-height: 1.1;
        }

        .debt-row-meta {
            color: #7c3aed;
            font-size: .76rem;
            font-weight: 750;
            margin-top: .12rem;
        }

        .debt-row-amount {
            color: #ff2f9f;
            font-weight: 950;
            white-space: nowrap;
        }

        .debt-row-chevron {
            color: rgba(124, 58, 237, .72);
            font-size: 1.1rem;
        }

        .credit-card {
            border: 1px solid rgba(63, 43, 88, 0.10);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.52);
            box-shadow: none;
            padding: 1rem;
        }

        .credit-card-header {
            display: flex;
            justify-content: space-between;
            gap: .75rem;
            align-items: start;
            margin-bottom: .75rem;
        }

        .credit-card-title {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: 1.12rem;
            font-weight: 750;
            line-height: 1.2;
        }

        .apr-pill {
            border-radius: 999px;
            background: linear-gradient(135deg, rgba(255, 232, 117, .65), rgba(255, 159, 143, .38));
            color: #7a1c77;
            border: 1px solid rgba(255, 60, 172, .24);
            padding: .2rem .55rem;
            font-size: .78rem;
            font-weight: 800;
            white-space: nowrap;
        }

        .money-pair {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: .65rem;
            margin-bottom: .75rem;
        }

        .money-label {
            color: rgba(63, 43, 88, .70);
            font-size: .76rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .money-value {
            color: var(--ink);
            font-family: var(--font-ui);
            font-size: 1.05rem;
            font-weight: 800;
        }

        .usage-bar {
            height: .62rem;
            border-radius: 999px;
            overflow: hidden;
            background: rgba(63, 43, 88, .1);
        }

        .usage-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--butter) 0%, var(--salmon) 55%, var(--lilac) 100%);
        }

        .usage-fill.warning {
            background: linear-gradient(90deg, var(--butter) 0%, var(--salmon) 100%);
        }

        .usage-fill.danger {
            background: linear-gradient(90deg, var(--salmon) 0%, var(--neon-pink) 100%);
        }

        .credit-foot {
            display: flex;
            justify-content: space-between;
            gap: .75rem;
            margin-top: .55rem;
            color: rgba(63, 43, 88, .78);
            font-size: .84rem;
            font-weight: 700;
        }

        .quick-card-title {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: 1.08rem;
            font-weight: 750;
            line-height: 1.2;
            margin: .15rem 0 .1rem;
        }

        .quick-card-meta {
            color: rgba(63, 43, 88, .72);
            font-size: .82rem;
            font-weight: 700;
        }

        .quick-card-value {
            color: var(--ink);
            font-family: var(--font-ui);
            font-size: 1.08rem;
            font-weight: 850;
            line-height: 1.18;
            white-space: nowrap;
        }

        div[data-testid="stPopover"] button {
            border-radius: 999px;
        }

        .payment-list {
            display: grid;
            gap: .55rem;
            margin-top: .4rem;
        }

        .payment-row {
            display: flex;
            justify-content: space-between;
            gap: .75rem;
            align-items: center;
            border: 1px solid rgba(63, 43, 88, .09);
            border-radius: 8px;
            background: rgba(255, 255, 255, .46);
            padding: .7rem .85rem;
            box-shadow: none;
        }

        .payment-name {
            color: var(--ink);
            font-family: var(--font-display);
            font-weight: 750;
        }

        .payment-meta {
            color: rgba(63, 43, 88, .68);
            font-size: .84rem;
            margin-top: .15rem;
        }

        .payment-amount {
            color: #7a1c77;
            font-family: var(--font-ui);
            font-weight: 900;
            white-space: nowrap;
        }

        [data-testid="stMetric"] {
            padding: 1rem;
        }

        [data-testid="stMetricValue"] {
            font-family: var(--font-ui);
            font-size: clamp(1.45rem, 3vw, 2rem) !important;
            line-height: 1.15 !important;
        }

        div.stButton > button,
        div[data-testid="stDownloadButton"] button {
            border: 1px solid rgba(63, 43, 88, 0.12);
            border-radius: 8px;
            background: rgba(255,255,255,.62);
            color: var(--ink);
            box-shadow: none;
            font-family: var(--font-ui);
            font-weight: 700;
        }

        div.stButton > button:hover,
        div[data-testid="stDownloadButton"] button:hover {
            border-color: var(--neon-pink);
            color: #7a1c77;
            transform: translateY(-1px);
        }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--neon-pink) 0%, var(--salmon) 48%, var(--butter) 100%);
            color: white;
            border-color: rgba(255, 255, 255, .52);
        }

        [data-baseweb="tab-list"] {
            gap: .45rem;
            padding: 0 0 .35rem;
            margin: .85rem 0 1rem;
            border: 0;
            border-bottom: 1px solid rgba(63, 43, 88, .10);
            border-radius: 0;
            background: transparent;
            backdrop-filter: none;
            box-shadow: none;
        }

        [data-baseweb="tab"] {
            min-height: 2.25rem;
            padding: 0 .85rem;
            border-radius: 999px;
            color: var(--ink);
            background: transparent;
            font-weight: 700;
            transition: all .18s ease;
        }

        [data-baseweb="tab"]:hover {
            background: rgba(255, 255, 255, .48);
            color: #7a1c77;
        }

        [aria-selected="true"][data-baseweb="tab"] {
            background: linear-gradient(135deg, rgba(255,232,117,.28) 0%, rgba(255,159,143,.22) 100%);
            color: #7a1c77;
            box-shadow: none;
        }

        [data-baseweb="tab-highlight"] {
            display: none;
        }

        .girlie-login {
            position: relative;
            z-index: 2;
            width: min(980px, 96vw);
            min-height: min(46vh, 25rem);
            margin: 0 auto;
            text-align: center;
            padding: 0;
            overflow: visible;
        }

        .girlie-login > *:not(.passcode-dots) {
            display: none !important;
        }

        .girlie-login::before {
            display: none;
        }

        .girlie-login::after {
            display: none;
        }

        .login-palm-shadow {
            position: absolute;
            left: -18vw;
            top: -5.5rem;
            width: 35rem;
            height: 18rem;
            z-index: 0;
            opacity: .36;
            filter: blur(2px);
            transform: rotate(-10deg);
            pointer-events: none;
        }

        .login-palm-shadow span {
            position: absolute;
            left: 3rem;
            top: 8rem;
            width: 25rem;
            height: 1.05rem;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(61, 47, 77, .38), transparent 74%);
            transform-origin: left center;
        }

        .login-palm-shadow span:nth-child(1) { transform: rotate(-40deg); }
        .login-palm-shadow span:nth-child(2) { transform: rotate(-24deg); top: 7.4rem; }
        .login-palm-shadow span:nth-child(3) { transform: rotate(-9deg); top: 6.9rem; }
        .login-palm-shadow span:nth-child(4) { transform: rotate(8deg); top: 6.7rem; }
        .login-palm-shadow span:nth-child(5) { transform: rotate(25deg); top: 7.2rem; }
        .login-palm-shadow span:nth-child(6) { transform: rotate(42deg); top: 8rem; }

        .login-flower-spray {
            position: absolute;
            right: -7vw;
            bottom: -30rem;
            width: 22rem;
            height: 25rem;
            z-index: 0;
            opacity: .70;
            pointer-events: none;
        }

        .login-flower-spray::before {
            content: "";
            position: absolute;
            left: 45%;
            bottom: 0;
            width: 1px;
            height: 22rem;
            background: rgba(170, 125, 92, .35);
            transform: rotate(-18deg);
            transform-origin: bottom;
            box-shadow:
                -4rem -4rem 0 rgba(170, 125, 92, .18),
                3.2rem -6rem 0 rgba(170, 125, 92, .14);
        }

        .login-flower-spray span {
            position: absolute;
            width: 1.35rem;
            height: 1.35rem;
            border-radius: 50%;
            background:
                radial-gradient(circle at 50% 50%, rgba(255, 235, 220, .95) 0 .22rem, transparent .24rem),
                radial-gradient(circle at 25% 35%, rgba(255, 255, 255, .9) 0 .32rem, transparent .34rem),
                radial-gradient(circle at 70% 34%, rgba(255, 214, 224, .9) 0 .32rem, transparent .34rem),
                radial-gradient(circle at 42% 72%, rgba(255, 196, 214, .86) 0 .34rem, transparent .36rem);
            filter: drop-shadow(0 8px 14px rgba(245, 170, 190, .16));
        }

        .login-flower-spray span:nth-child(1) { left: 43%; top: 21%; }
        .login-flower-spray span:nth-child(2) { left: 54%; top: 28%; transform: scale(.8); }
        .login-flower-spray span:nth-child(3) { left: 36%; top: 35%; transform: scale(.72); }
        .login-flower-spray span:nth-child(4) { left: 62%; top: 42%; transform: scale(.68); }
        .login-flower-spray span:nth-child(5) { left: 48%; top: 50%; transform: scale(.62); }

        .hello-lockup {
            position: relative;
            z-index: 3;
            margin: -.05rem auto .56rem;
            color: #22172f;
        }

        .login-monogram {
            position: relative;
            z-index: 2;
            color: #f49aad;
            font-family: "Fraunces", Georgia, serif;
            font-size: clamp(2.35rem, 5.6vw, 3.75rem);
            font-weight: 650;
            line-height: .8;
            margin-bottom: .18rem;
            text-shadow: 0 8px 22px rgba(255, 155, 180, .16);
        }

        .login-monogram span {
            color: #f6a6bd;
            font-family: var(--font-script);
            font-size: .56em;
            font-weight: 400;
            margin-left: .12rem;
        }

        .hello-line {
            display: block;
            letter-spacing: 0;
            text-shadow: 0 12px 28px rgba(63, 43, 88, .10);
        }

        .hello-serif {
            display: inline-flex;
            align-items: center;
            gap: .32rem;
            color: #29242b;
            font-family: "Fraunces", Georgia, serif;
            font-size: clamp(4.85rem, 10.8vw, 7.05rem);
            font-weight: 650;
            line-height: .70;
        }

        .hello-heart {
            color: #f29db0;
            font-family: var(--font-script);
            font-style: italic;
            font-size: .52em;
            font-weight: 400;
            text-shadow: 0 0 15px rgba(255, 151, 177, .22);
        }

        .hello-script {
            display: block;
            margin-top: -.1rem;
            color: #f191a8;
            font-family: "Fraunces", Georgia, serif;
            font-style: italic;
            font-size: clamp(3.85rem, 9.2vw, 6.0rem);
            font-weight: 750;
            line-height: .72;
        }

        .login-tagline {
            position: relative;
            z-index: 2;
            display: inline-flex;
            align-items: center;
            gap: .75rem;
            color: #2f2932;
            font-family: var(--font-ui);
            font-size: clamp(.82rem, 1.8vw, 1.02rem);
            font-weight: 500;
            letter-spacing: .36em;
            text-transform: uppercase;
            margin: .34rem auto .70rem;
        }

        .login-tagline::before,
        .login-tagline::after {
            content: "";
            display: block;
            width: 4.4rem;
            height: 1px;
            background: rgba(242, 157, 176, .48);
        }

        .login-sparkle {
            position: absolute;
            z-index: 2;
            color: #f49aad;
            font-family: var(--font-ui);
            font-size: 1.6rem;
            line-height: 1;
            animation: sparkle 4.2s ease-in-out infinite;
            pointer-events: none;
        }

        .login-sparkle.one { left: 19%; top: 46%; }
        .login-sparkle.two { right: 21%; top: 39%; color: #c9a2e8; animation-delay: 1.2s; }
        .login-sparkle.three { left: 27%; top: 72%; font-size: 1.1rem; color: #c9a2e8; animation-delay: 2.1s; }
        .login-sparkle.four { right: 14%; top: 77%; font-size: 1.9rem; animation-delay: 2.8s; }

        .login-footer-note {
            position: relative;
            z-index: 2;
            color: #f191a8;
            font-family: var(--font-script);
            font-style: italic;
            font-size: clamp(1.45rem, 3vw, 2rem);
            line-height: 1;
            margin: .52rem auto .05rem;
            text-shadow: 0 8px 20px rgba(255, 151, 177, .16);
        }

        .login-footer-heart {
            color: #cda1ef;
            font-family: var(--font-script);
            font-style: italic;
            font-size: 1.2rem;
            line-height: 1;
        }

        .wallpaper-flower {
            display: none;
        }

        .wallpaper-flower.one {
            left: 7%;
            top: 48%;
            --s: 1.05;
            --r: -10deg;
        }

        .wallpaper-flower.two {
            right: 8%;
            top: 9%;
            --s: .82;
            --r: 18deg;
            animation-delay: 1.1s;
        }

        .wallpaper-flower.three {
            left: 23%;
            top: 8%;
            --s: .68;
            --r: -22deg;
            animation-delay: 2.1s;
        }

        .wallpaper-flower.four {
            right: 24%;
            bottom: 2%;
            --s: .62;
            --r: 34deg;
            animation-delay: 3s;
        }

        .wallpaper-flower.five {
            left: 41%;
            top: 4%;
            --s: .54;
            --r: 12deg;
            animation-delay: 1.7s;
        }

        .wallpaper-flower.six {
            right: 43%;
            bottom: -5%;
            --s: .48;
            --r: -28deg;
            animation-delay: 2.8s;
        }

        .wallpaper-flower span {
            position: absolute;
            left: 50%;
            top: 50%;
            width: 16px;
            height: 26px;
            border-radius: 999px 999px 6px 6px;
            background: linear-gradient(180deg, rgba(255,255,255,.86), var(--salmon));
            transform-origin: 50% 90%;
        }

        .wallpaper-flower.two span {
            background: linear-gradient(180deg, rgba(255,255,255,.86), var(--lilac));
        }

        .wallpaper-flower.three span {
            background: linear-gradient(180deg, rgba(255,255,255,.9), var(--butter));
        }

        .wallpaper-flower.four span {
            background: linear-gradient(180deg, rgba(255,255,255,.86), #ffb7cf);
        }

        .wallpaper-flower.five span {
            background: linear-gradient(180deg, rgba(255,255,255,.86), #b9ff7d);
        }

        .wallpaper-flower.six span {
            background: linear-gradient(180deg, rgba(255,255,255,.9), #ffc36b);
        }

        .wallpaper-flower span:nth-child(1) { transform: translate(-50%, -92%) rotate(0deg); }
        .wallpaper-flower span:nth-child(2) { transform: translate(-50%, -92%) rotate(72deg); }
        .wallpaper-flower span:nth-child(3) { transform: translate(-50%, -92%) rotate(144deg); }
        .wallpaper-flower span:nth-child(4) { transform: translate(-50%, -92%) rotate(216deg); }
        .wallpaper-flower span:nth-child(5) { transform: translate(-50%, -92%) rotate(288deg); }

        .wallpaper-flower b {
            position: absolute;
            left: 50%;
            top: 50%;
            width: 13px;
            height: 13px;
            border-radius: 50%;
            background: var(--butter);
            transform: translate(-50%, -50%);
            box-shadow: 0 0 16px rgba(199,255,61,.5);
        }

        .passcode-dots {
            position: absolute;
            left: 50%;
            top: min(45.2vh, 24.6rem);
            z-index: 6;
            display: flex !important;
            align-items: center;
            justify-content: center;
            gap: clamp(4.35rem, 5.7vw, 5.95rem);
            margin: 0;
            min-height: 1.6rem;
            transform: translateX(-50%);
            pointer-events: none;
            visibility: visible;
        }

        .passcode-dot {
            width: 1rem;
            height: 1rem;
            border-radius: 50%;
            border: 0;
            background: transparent;
            box-shadow: none;
        }

        .passcode-dot.filled {
            background: #c99be6;
            box-shadow: 0 0 18px rgba(201, 155, 230, .36);
        }

        .passcode-grid-marker {
            position: relative;
            z-index: 4;
            width: min(460px, 92vw);
            height: 0;
            margin: 0 auto .15rem;
        }

        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) {
            position: relative;
            z-index: 4;
        }

        .login-footer-note,
        .login-footer-heart {
            position: relative;
            z-index: 4;
            text-align: center;
            display: none;
        }

        .passcode-grid-marker::before {
            display: none;
        }

        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div[data-testid="stHorizontalBlock"] {
            width: min(356px, 84vw);
            margin-left: auto;
            margin-right: auto;
            display: flex !important;
            flex-direction: row !important;
            gap: 1.16rem !important;
        }

        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div[data-testid="stColumn"] {
            flex: 1 1 0 !important;
            min-width: 0 !important;
            width: 33.333% !important;
        }

        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div.stButton > button {
            width: 4.45rem;
            height: 4.45rem;
            min-height: 4.45rem;
            margin: .12rem auto;
            border-radius: 50%;
            border: 0 !important;
            background: transparent !important;
            backdrop-filter: none;
            box-shadow: none !important;
            color: transparent !important;
            font-size: 1.52rem;
            font-family: var(--font-apple);
            font-weight: 700;
            letter-spacing: 0;
            line-height: 1;
            text-shadow: none;
        }

        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div.stButton > button p {
            color: transparent !important;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 100%;
            margin: 0 !important;
            padding: 0 !important;
            text-align: center;
            line-height: 1;
            font-weight: 700;
        }

        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div.stButton > button:hover {
            border-color: transparent;
            color: transparent;
            box-shadow: none;
        }

        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) .st-key-passcode_backspace button,
        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) .st-key-passcode_clear button {
            background: transparent !important;
            box-shadow: none !important;
            border-color: transparent !important;
            font-size: 1.02rem;
            font-weight: 700;
        }

        .routine-hero {
            position: relative;
            overflow: hidden;
            border: 0;
            border-bottom: 1px solid rgba(63, 43, 88, .10);
            border-radius: 0;
            background:
                radial-gradient(circle at 8% 18%, rgba(255, 232, 117, .24), transparent 24%),
                radial-gradient(circle at 84% 22%, rgba(199, 164, 255, .18), transparent 26%);
            padding: .55rem 0 1rem;
            box-shadow: none;
            margin-bottom: 1.05rem;
        }

        .routine-kicker {
            color: #ff7f95;
            font-family: var(--font-ui);
            font-size: .75rem;
            font-weight: 900;
            letter-spacing: .08em;
            text-transform: uppercase;
        }

        .routine-title {
            color: #2f2145;
            font-family: var(--font-display);
            font-size: clamp(1.8rem, 4vw, 3.2rem);
            font-weight: 750;
            line-height: 1;
            margin-top: .25rem;
        }

        .routine-subtitle {
            color: #f191a8;
            font-family: var(--font-script);
            font-style: italic;
            font-size: clamp(1.45rem, 3vw, 2.05rem);
            font-weight: 650;
            line-height: .95;
            margin-top: .25rem;
        }

        .routine-progress-text {
            color: #3f2b58;
            font-weight: 900;
            font-size: 1.05rem;
            margin: .9rem 0 .35rem;
        }

        .routine-meta {
            color: rgba(63, 43, 88, .72);
            font-size: .88rem;
            font-weight: 650;
        }

        .routine-mini-grid,
        .routine-week-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: .7rem;
            margin: .55rem 0 .8rem;
        }

        .routine-mini-card,
        .coach-card,
        div[data-testid="stVerticalBlock"]:has(.routine-section-marker) {
            border: 1px solid rgba(63, 43, 88, .09);
            border-radius: 8px;
            background: rgba(255,255,255,.46);
            box-shadow: none;
        }

        .routine-mini-card {
            padding: .72rem 0 .78rem;
            border: 0;
            border-bottom: 1px solid rgba(63, 43, 88, .10);
            border-radius: 0;
            background: transparent;
        }

        .routine-mini-label {
            color: rgba(63, 43, 88, .66);
            font-size: .72rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: .05em;
        }

        .routine-mini-value {
            color: #3f2b58;
            font-size: 1.1rem;
            font-weight: 900;
            margin-top: .15rem;
        }

        div[data-testid="stVerticalBlock"]:has(.routine-section-marker) {
            padding: .85rem .9rem;
            min-height: 100%;
        }

        div[data-testid="stVerticalBlock"]:has(.wellness-top),
        div[data-testid="stVerticalBlock"]:has(.routine-hero) {
            padding: 0;
            border: 0;
            border-radius: 0;
            background: transparent;
            box-shadow: none;
        }

        .routine-section-heading {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .75rem;
            margin-bottom: .45rem;
            padding: .18rem 0 .42rem;
            border-radius: 0;
            border-bottom: 1px solid rgba(255, 159, 143, .22);
            background: transparent;
            color: #33224c;
            font-family: var(--font-ui);
            font-size: .78rem;
            font-weight: 950;
            letter-spacing: .06em;
            text-transform: uppercase;
        }

        div[data-testid="stVerticalBlock"]:has(.routine-section-marker) label {
            color: #3f2b58 !important;
            font-weight: 650;
        }

        .routine-note {
            color: rgba(63, 43, 88, .58);
            font-size: .76rem;
            margin: -.3rem 0 .25rem 1.9rem;
        }

        .coach-card {
            padding: .85rem 0 .9rem .85rem;
            margin-bottom: .75rem;
            border-top: 0;
            border-right: 0;
            border-bottom: 1px solid rgba(63, 43, 88, .10);
            border-radius: 0;
            background: transparent;
            border-left: 3px solid rgba(255, 142, 163, .62);
        }

        .coach-title {
            color: #3f2b58;
            font-family: var(--font-display);
            font-size: 1.35rem;
            font-weight: 800;
            line-height: 1.1;
        }

        .coach-copy {
            color: rgba(63, 43, 88, .78);
            font-size: .95rem;
            font-weight: 650;
            margin-top: .35rem;
        }

        .mantra-text {
            color: #ff5b8a;
            font-family: var(--font-script);
            font-style: italic;
            font-size: clamp(1.35rem, 3vw, 2.1rem);
            line-height: 1.05;
        }

        .week-row {
            display: grid;
            grid-template-columns: minmax(120px, 1.2fr) repeat(7, 1fr);
            align-items: center;
            gap: .35rem;
            border-bottom: 1px solid rgba(255, 204, 222, .38);
            padding: .42rem 0;
        }

        .week-name {
            color: #3f2b58;
            font-size: .82rem;
            font-weight: 800;
        }

        .week-day,
        .week-dot {
            display: grid;
            place-items: center;
            min-height: 1.25rem;
            font-size: .72rem;
            font-weight: 900;
        }

        .week-dot span {
            width: .62rem;
            height: .62rem;
            border-radius: 50%;
            background: rgba(199, 164, 255, .30);
        }

        .week-dot.done span { background: #ff7f95; box-shadow: 0 0 0 3px rgba(255, 127, 149, .12); }

        .wellness-top {
            margin: .2rem 0 1rem;
        }

        .wellness-greeting {
            color: #2f2145;
            font-family: var(--font-display);
            font-size: clamp(2.15rem, 5vw, 3.35rem);
            font-weight: 780;
            line-height: 1.02;
            margin-bottom: .35rem;
        }

        .wellness-sub {
            color: rgba(63, 43, 88, .68);
            font-family: var(--font-ui);
            font-size: .98rem;
            font-weight: 600;
            margin-bottom: .9rem;
        }

        .ritual-strip {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            align-items: stretch;
            border: 0;
            border-top: 1px solid rgba(255, 159, 143, .18);
            border-bottom: 1px solid rgba(255, 159, 143, .18);
            border-radius: 0;
            background: transparent;
            box-shadow: none;
            overflow: hidden;
            backdrop-filter: none;
        }

        .ritual-item {
            min-width: 0;
            padding: .88rem .45rem .78rem;
            text-align: center;
            border-right: 1px solid rgba(255, 159, 143, .32);
        }

        .ritual-item:last-child {
            border-right: 0;
        }

        .ritual-icon {
            color: #ff8ea3;
            font-size: 1.65rem;
            line-height: 1;
            margin-bottom: .36rem;
        }

        .ritual-label {
            color: #30243d;
            font-size: .72rem;
            font-weight: 850;
            letter-spacing: .12em;
            text-transform: uppercase;
        }

        .discipline-card {
            width: min(520px, 92%);
            margin: -.12rem auto 1.05rem;
            padding: .85rem 1.1rem .78rem;
            border-radius: 0;
            background: transparent;
            border: 0;
            border-bottom: 1px solid rgba(255, 159, 143, .18);
            box-shadow: none;
            text-align: center;
            backdrop-filter: none;
        }

        .discipline-card .quote {
            color: #ff8ea3;
            font-size: 1.25rem;
            font-weight: 900;
        }

        .discipline-main {
            color: #3b2d47;
            font-size: .88rem;
            font-weight: 700;
            letter-spacing: .26em;
            text-transform: uppercase;
        }

        .discipline-script {
            color: #ff8ea3;
            font-family: var(--font-script);
            font-style: italic;
            font-size: 1.58rem;
            font-weight: 650;
            line-height: .95;
        }

        .become-pill {
            display: block;
            width: min(340px, 88%);
            margin: .25rem auto 1.15rem;
            padding: .92rem 1.2rem;
            border-radius: 999px;
            background: linear-gradient(135deg, rgba(255, 179, 192, .84) 0%, rgba(255, 153, 173, .86) 55%, rgba(255, 197, 204, .78) 100%);
            border: 1px solid rgba(255, 134, 155, .34);
            box-shadow: none;
            color: white;
            text-align: center;
            font-family: var(--font-ui);
            font-size: 1rem;
            font-weight: 850;
            letter-spacing: .14em;
            text-transform: uppercase;
        }

        .become-pill span {
            color: #fff7bf;
            font-family: var(--font-script);
            font-style: italic;
            font-size: 1.72rem;
            font-weight: 650;
            letter-spacing: 0;
            text-transform: none;
        }

        @media (max-width: 640px) {
            .stApp:not(:has(.girlie-login)) .block-container {
                padding: .85rem .72rem 2.2rem;
            }

            .stApp:not(:has(.girlie-login)) h1,
            .stApp:not(:has(.girlie-login)) [data-testid="stMarkdownContainer"] h1 {
                font-size: 2.15rem !important;
                line-height: 1.05 !important;
            }

            .wellness-greeting {
                font-size: 2rem;
            }

            .wellness-sub {
                font-size: .9rem;
            }

            .ritual-strip {
                grid-template-columns: repeat(5, minmax(68px, 1fr));
                overflow-x: auto;
                scrollbar-width: none;
            }

            .ritual-strip::-webkit-scrollbar {
                display: none;
            }

            .ritual-item {
                padding: .72rem .38rem .65rem;
            }

            .ritual-icon {
                font-size: 1.28rem;
            }

            .ritual-label {
                font-size: .58rem;
                letter-spacing: .08em;
            }

            .discipline-card {
                width: 92%;
                padding: .78rem .8rem .7rem;
            }

            .discipline-main {
                font-size: .72rem;
                letter-spacing: .18em;
            }

            .discipline-script {
                font-size: 1.45rem;
            }

            .become-pill {
                width: 86%;
                font-size: .82rem;
                padding: .78rem 1rem;
            }

            .become-pill span {
                font-size: 1.55rem;
            }

            .stApp:not(:has(.girlie-login)) [data-testid="stCaptionContainer"],
            .stApp:not(:has(.girlie-login)) p {
                overflow-wrap: anywhere;
            }

            [data-baseweb="tab-list"] {
                overflow-x: auto;
                overflow-y: hidden;
                scrollbar-width: none;
                gap: .25rem;
                padding: .18rem;
            }

            [data-baseweb="tab-list"]::-webkit-scrollbar {
                display: none;
            }

            [data-baseweb="tab"] {
                flex: 0 0 auto;
                min-height: 2.25rem;
                padding: 0 .62rem;
                font-size: .82rem;
            }

            .section-title {
                font-size: 1.32rem;
                line-height: 1.05;
                flex-wrap: wrap;
            }

            .summary-grid,
            .credit-grid,
            .debt-total-grid,
            .routine-mini-grid,
            .routine-week-grid {
                grid-template-columns: 1fr !important;
            }

            .summary-value,
            .mini-card-value,
            .quick-card-value,
            .payment-amount,
            .debt-row-amount {
                white-space: normal;
                overflow-wrap: anywhere;
            }

            div[data-testid="stVerticalBlock"]:has(.section-shell-marker),
            div[data-testid="stVerticalBlock"]:has(.routine-section-marker),
            div[data-testid="stVerticalBlock"]:has(.field-card-marker) {
                padding: .82rem;
            }

            .routine-hero {
                padding: 1rem;
            }

            .routine-title {
                font-size: 2.05rem;
            }

            .routine-subtitle,
            .mantra-text {
                font-size: 1.45rem;
            }

            .week-row {
                grid-template-columns: minmax(92px, 1.25fr) repeat(7, minmax(18px, 1fr));
                gap: .18rem;
            }

            .week-name {
                font-size: .72rem;
            }

            .debt-row-card {
                grid-template-columns: auto 1fr;
                align-items: start;
            }

            .debt-row-amount,
            .debt-row-chevron {
                grid-column: 2;
                justify-self: start;
            }

            .stApp:has(.girlie-login) {
                background-image: var(--login-cover-mobile);
                background-size: cover;
                background-position: center top;
            }

            .girlie-login {
                min-height: 30.5vh;
            }

            .passcode-dots {
                left: 50%;
                top: 28.8vh;
                gap: 2.48rem;
            }

            .passcode-dot {
                width: .72rem;
                height: .72rem;
                border: 1.7px solid rgba(179, 151, 199, .72);
                background: rgba(255, 255, 255, .12);
                border-width: 1.7px;
            }

            div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div[data-testid="stHorizontalBlock"] {
                width: min(304px, 82vw);
                gap: .50rem !important;
                transform: translateX(17px);
            }

            div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div.stButton > button {
                width: clamp(3.28rem, 14vw, 3.72rem);
                height: clamp(3.28rem, 14vw, 3.72rem);
                min-height: clamp(3.28rem, 14vw, 3.72rem);
                display: inline-flex;
                align-items: center;
                justify-content: center;
                padding: 0 !important;
                border: 1px solid rgba(255, 255, 255, .82) !important;
                background: rgba(255, 255, 255, .54) !important;
                color: #57505a !important;
                font-family: var(--font-apple);
                font-size: 1.05rem;
                font-weight: 500;
                line-height: 1;
                backdrop-filter: blur(12px);
                box-shadow: 0 10px 24px rgba(219, 160, 190, .12), inset 0 1px 0 rgba(255,255,255,.85) !important;
            }

            div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div.stButton > button p {
                color: #57505a !important;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100%;
                height: 100%;
                margin: 0 !important;
                padding: 0 !important;
                line-height: 1;
                font-size: inherit;
                font-weight: inherit;
                text-align: center;
            }

            div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div.stButton > button:hover {
                background: rgba(255, 255, 255, .68) !important;
                color: #4b4350 !important;
            }

            div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) .st-key-passcode_backspace button,
            div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) .st-key-passcode_clear button {
                font-size: .92rem;
                font-weight: 500;
            }

            .login-footer-note,
            .login-footer-heart {
                display: block;
                font-family: var(--font-display);
                font-style: italic;
                color: #f29ab0;
                text-align: center;
            }

            .login-footer-note {
                margin-top: .18rem;
                font-size: 1.05rem;
            }

            .login-footer-heart {
                color: #cda3e8;
                font-size: 1.05rem;
                line-height: 1.1;
            }
        }

        @media (min-width: 641px) and (max-width: 1024px) and (orientation: portrait) {
            .stApp:has(.girlie-login) {
                background-image: var(--login-cover-ipad);
                background-size: contain;
                background-position: center top;
                background-repeat: no-repeat;
            }

            .girlie-login {
                min-height: 29vh;
            }

            .passcode-dots {
                top: 28.2vh;
                gap: 3.18rem;
            }

            .passcode-dot {
                width: .78rem;
                height: .78rem;
                border: 1.7px solid rgba(179, 151, 199, .72);
                background: rgba(255, 255, 255, .12);
                border-width: 1.7px;
            }

            div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div[data-testid="stHorizontalBlock"] {
                width: min(388px, 58vw);
                gap: .66rem !important;
            }

            div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div.stButton > button {
                width: 4.05rem;
                height: 4.05rem;
                min-height: 4.05rem;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                padding: 0 !important;
                border: 1px solid rgba(255, 255, 255, .82) !important;
                background: rgba(255, 255, 255, .52) !important;
                color: #57505a !important;
                font-family: var(--font-apple);
                font-size: 1.18rem;
                font-weight: 500;
                line-height: 1;
                backdrop-filter: blur(12px);
                box-shadow: 0 10px 24px rgba(219, 160, 190, .12), inset 0 1px 0 rgba(255,255,255,.85) !important;
            }

            div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div.stButton > button p {
                color: #57505a !important;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100%;
                height: 100%;
                margin: 0 !important;
                padding: 0 !important;
                line-height: 1;
                font-size: inherit;
                font-weight: inherit;
                text-align: center;
            }

            div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) .st-key-passcode_backspace button,
            div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) .st-key-passcode_clear button {
                font-size: 1rem;
                font-weight: 500;
            }

            .login-footer-note,
            .login-footer-heart {
                display: block;
                font-family: var(--font-display);
                font-style: italic;
                color: #f29ab0;
                text-align: center;
            }

            .login-footer-note {
                margin-top: .24rem;
                font-size: 1.16rem;
            }

            .login-footer-heart {
                color: #cda3e8;
                font-size: 1.02rem;
                line-height: 1.1;
            }
        }

        @media (min-aspect-ratio: 16/9) {
            .stApp:has(.girlie-login) {
                background-size: auto 100%;
            }
        }

        @keyframes sunriseGlow {
            0%, 100% { transform: translateY(0) scale(1); opacity: .78; }
            50% { transform: translateY(10px) scale(1.04); opacity: 1; }
        }

        @keyframes cloudDrift {
            0%, 100% { transform: translateX(-8px); opacity: .76; }
            50% { transform: translateX(10px); opacity: .95; }
        }

        @keyframes flowerFloat {
            0%, 100% { transform: translateY(0) scale(var(--s)) rotate(var(--r)); }
            50% { transform: translateY(-9px) scale(var(--s)) rotate(calc(var(--r) + 12deg)); }
        }

        @keyframes sparkle {
            0%, 100% { opacity: .35; transform: scale(.85) rotate(0deg); }
            50% { opacity: 1; transform: scale(1.2) rotate(14deg); }
        }
        </style>
        """.replace("__LOGIN_BG__", login_bg).replace("__LOGIN_COVER__", login_cover).replace("__LOGIN_COVER_MOBILE__", login_cover_mobile).replace("__LOGIN_COVER_IPAD__", login_cover_ipad),
        unsafe_allow_html=True,
    )


def render_login_hero() -> None:
    dots = "".join(
        f'<span class="passcode-dot{" filled" if index < len(st.session_state.passcode_input) else ""}"></span>'
        for index in range(4)
    )
    st.markdown(
        f"""
        <div class="girlie-login">
            <div class="login-palm-shadow"><span></span><span></span><span></span><span></span><span></span><span></span></div>
            <div class="login-flower-spray"><span></span><span></span><span></span><span></span><span></span></div>
            <div class="login-sparkle one">✧</div>
            <div class="login-sparkle two">✧</div>
            <div class="login-sparkle three">✧</div>
            <div class="login-sparkle four">✧</div>
            <div class="login-monogram">GM<span>♡</span></div>
            <div class="hello-lockup">
                <span class="hello-line hello-serif">Hello,</span>
                <span class="hello-line hello-script">baby girl<span class="hello-heart">♡</span></span>
            </div>
            <div class="login-tagline">Small habits, big results</div>
            <div class="passcode-dots">{dots}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def money(value: float) -> str:
    return f"${float(value or 0):,.2f}"


CARD_COLUMN_LABELS = {
    "Tarjeta": "Card",
    "APR %": "APR %",
    "Cupo": "Limit",
    "Saldo": "Balance",
    "Dia pago": "Due day",
    "Minimo toca": "Minimum due",
    "Minimo": "Minimum",
    "Gasto extra": "Extra spend",
    "Notas": "Notes",
}

EXPENSE_COLUMN_LABELS = {
    "Categoria": "Category",
    "Nombre": "Name",
    "Cuenta/Tarjeta": "Account/Card",
    "Monto quincena": "Paycheck amount",
    "Tipo": "Type",
    "Incluir": "Include",
    "Notas": "Notes",
}

CARD_PLAN_LABELS = {
    "Tarjeta": "Card",
    "Minimo si toca": "Minimum due",
    "Debitos auto": "Auto debits",
    "Gastos extra": "Extra spend",
    "Pago exacto ahora": "Pay now",
    "Payoff con SoFi": "Can pay off with SoFi",
    "Notas": "Notes",
}

ACCOUNT_PLAN_LABELS = {
    "Cuenta / tarjeta": "Account / card",
    "Monto": "Amount",
}

HISTORY_LABELS = {
    "Fecha": "Date",
    "Cuenta inicial": "Starting cash",
    "Obligatorio": "Required",
    "Mama": "Personal debts",
    "Extra tarjetas": "Card extra",
    "Tarjeta extra": "Extra card target",
}


def english_columns(df: pd.DataFrame, labels: dict[str, str]) -> pd.DataFrame:
    return df.rename(columns=labels)


def format_money_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    shown = df.copy()
    for column in columns:
        if column in shown:
            shown[column] = shown[column].apply(money)
    return shown


def parse_money(value: str) -> float:
    cleaned = str(value).replace("$", "").replace(",", "").strip()
    try:
        return max(0.0, float(cleaned or 0))
    except ValueError:
        return 0.0


def normalize_money_state(input_key: str) -> None:
    raw = str(st.session_state.get(input_key, "")).strip()
    parsed = parse_money(raw)
    st.session_state[input_key] = "" if parsed == 0 else money(parsed)


def money_field_initial(value: float) -> str:
    return "" if float(value or 0) == 0 else money(value)


def money_input(label: str, settings: dict, key: str, label_visibility: str = "visible") -> float:
    input_key = f"money_input_{key}"
    if input_key not in st.session_state:
        st.session_state[input_key] = money_field_initial(settings.get(key, 0.0))
    entered = st.text_input(label, key=input_key, placeholder="$0.00", on_change=normalize_money_state, args=(input_key,), label_visibility=label_visibility)
    parsed = parse_money(entered)
    settings[key] = parsed
    return parsed


def money_text_input(label: str, value: float, key: str) -> float:
    if key not in st.session_state:
        st.session_state[key] = money_field_initial(value)
    entered = st.text_input(label, key=key, placeholder="$0.00", on_change=normalize_money_state, args=(key,))
    return parse_money(entered)


def field_card_header(icon: str, color: str, label: str) -> None:
    st.markdown(
        f"""
        <div class="field-card-marker"></div>
        <div class="field-card-head">
            <span class="field-card-icon {html.escape(color)}">{html.escape(icon)}</span>
            <span class="field-card-label">{html.escape(label)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(label: str, left: str = "✧", right: str = "♡") -> None:
    st.markdown(
        f"""
        <div class="section-title">
            <span class="doodle">{html.escape(left)}</span>
            <span class="underline">{html.escape(label)}</span>
            <span class="doodle">{html.escape(right)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_number(row: pd.Series, column: str) -> float:
    return float(pd.to_numeric(pd.Series([row.get(column, 0.0)]), errors="coerce").fillna(0.0).iloc[0])


def render_credit_snapshot(cards: pd.DataFrame) -> None:
    if cards.empty:
        st.info("No cards yet.")
        return

    items = []
    for _, card in cards.iterrows():
        name = html.escape(str(card.get("Tarjeta", "Card")))
        apr = card_number(card, "APR %")
        limit = card_number(card, "Cupo")
        used = card_number(card, "Saldo")
        available = max(0.0, limit - used)
        utilization = (used / limit * 100) if limit > 0 else 0.0
        fill_width = min(100.0, max(0.0, utilization))
        fill_class = "danger" if utilization >= 90 else "warning" if utilization >= 65 else ""
        due_day = int(card_number(card, "Dia pago"))
        items.append(
            textwrap.dedent(
                f"""
            <div class="credit-card">
                <div class="credit-card-header">
                    <div class="credit-card-title">{name}</div>
                    <div class="apr-pill">{apr:.2f}% APR</div>
                </div>
                <div class="money-pair">
                    <div>
                        <div class="money-label">Total limit</div>
                        <div class="money-value">{money(limit)}</div>
                    </div>
                    <div>
                        <div class="money-label">Used</div>
                        <div class="money-value">{money(used)}</div>
                    </div>
                </div>
                <div class="money-pair">
                    <div>
                        <div class="money-label">Available</div>
                        <div class="money-value">{money(available)}</div>
                    </div>
                    <div>
                        <div class="money-label">Utilization</div>
                        <div class="money-value">{utilization:.0f}%</div>
                    </div>
                </div>
                <div class="usage-bar"><div class="usage-fill {fill_class}" style="width: {fill_width:.0f}%"></div></div>
                <div class="credit-foot">
                    <span>Due day {due_day}</span>
                    <span>{money(max(0.0, used - limit))} over limit</span>
                </div>
            </div>
            """
            ).strip()
        )
    st.markdown(f'<div class="credit-grid">{"".join(items)}</div>', unsafe_allow_html=True)


def render_plan_credit_cards(cards: pd.DataFrame) -> None:
    if cards.empty:
        st.info("No cards yet.")
        return

    rows = cards.reset_index(drop=True)
    for start in range(0, len(rows), 2):
        cols = st.columns(2)
        for offset, col in enumerate(cols):
            card_index = start + offset
            if card_index >= len(rows):
                continue
            card = rows.iloc[card_index]
            name = str(card.get("Tarjeta", "Card")) or f"Card {card_index + 1}"
            apr = card_number(card, "APR %")
            limit = card_number(card, "Cupo")
            used = card_number(card, "Saldo")
            available = max(0.0, limit - used)
            utilization = (used / limit * 100) if limit > 0 else 0.0

            with col.container(border=True):
                header_left, header_apr, header_edit = st.columns([1, .55, .24], vertical_alignment="center")
                with header_left:
                    st.markdown(f'<div class="quick-card-title">{html.escape(name)}</div>', unsafe_allow_html=True)
                with header_apr:
                    st.markdown(f'<div class="apr-pill">{apr:.2f}% APR</div>', unsafe_allow_html=True)
                with header_edit:
                    with st.popover("✎", use_container_width=True):
                        with st.form(f"quick_card_edit_{card_index}"):
                            st.caption(f"Edit {name}")
                            new_apr = st.number_input(
                                "APR %",
                                value=apr,
                                min_value=0.0,
                                step=0.25,
                                format="%.2f",
                                key=f"plan_card_apr_{card_index}",
                            )
                            new_limit = st.text_input(
                                "Total limit",
                                value=money_field_initial(limit),
                                placeholder="$0.00",
                                key=f"plan_card_limit_{card_index}",
                            )
                            new_used = st.text_input(
                                "Used amount",
                                value=money_field_initial(used),
                                placeholder="$0.00",
                                key=f"plan_card_used_{card_index}",
                            )
                            submitted = st.form_submit_button("Save", type="primary", use_container_width=True)
                            if submitted:
                                st.session_state.data["cards"][card_index]["APR %"] = float(new_apr)
                                st.session_state.data["cards"][card_index]["Cupo"] = parse_money(new_limit)
                                st.session_state.data["cards"][card_index]["Saldo"] = parse_money(new_used)
                                save_data(st.session_state.data)
                                st.success("Card updated.")
                                st.rerun()

                v1, v2 = st.columns(2)
                with v1:
                    st.markdown('<div class="quick-card-meta">Total limit</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="quick-card-value">{money(limit)}</div>', unsafe_allow_html=True)
                with v2:
                    st.markdown('<div class="quick-card-meta">Used</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="quick-card-value">{money(used)}</div>', unsafe_allow_html=True)

                st.progress(min(1.0, max(0.0, utilization / 100)), text=f"{money(available)} available · {utilization:.0f}% used")


def render_credit_totals(total_limit: float, total_used: float, total_available: float, avg_apr: float) -> None:
    cards = [
        ("Total limit", money(total_limit)),
        ("Used limit", money(total_used)),
        ("Available limit", money(total_available)),
        ("Avg APR", f"{avg_apr:.2f}%"),
    ]
    html_cards = "".join(
        textwrap.dedent(
            f"""
        <div class="summary-card">
            <div class="summary-label">{html.escape(label)}</div>
            <div class="summary-value">{html.escape(value)}</div>
        </div>
        """
        ).strip()
        for label, value in cards
    )
    st.markdown(f'<div class="summary-grid">{html_cards}</div>', unsafe_allow_html=True)


def render_payment_rows(rows: list[dict]) -> None:
    if not rows:
        st.caption("Nothing to show yet.")
        return
    html_rows = []
    for row in rows:
        title = html.escape(str(row.get("title", "")))
        meta = html.escape(str(row.get("meta", "")))
        amount = money(float(row.get("amount", 0.0)))
        html_rows.append(
            textwrap.dedent(
                f"""
            <div class="payment-row">
                <div>
                    <div class="payment-name">{title}</div>
                    <div class="payment-meta">{meta}</div>
                </div>
                <div class="payment-amount">{amount}</div>
            </div>
            """
            ).strip()
        )
    st.markdown(f'<div class="payment-list">{"".join(html_rows)}</div>', unsafe_allow_html=True)


def render_cards_editor(cards: pd.DataFrame) -> pd.DataFrame:
    edited_rows = []
    for index, card in cards.reset_index(drop=True).iterrows():
        default_name = str(card.get("Tarjeta", ""))
        label_name = default_name or f"Card {index + 1}"
        with st.expander(label_name, expanded=index == 0):
            top_left, top_right = st.columns([1.25, 1])
            with top_left:
                name = st.text_input("Card name", value=default_name, key=f"card_name_{index}")
                notes = st.text_input("Notes", value=str(card.get("Notas", "")), key=f"card_notes_{index}")
            with top_right:
                apr = st.number_input("APR %", value=card_number(card, "APR %"), min_value=0.0, step=0.25, format="%.2f", key=f"card_apr_{index}")
                due_day = st.number_input("Due day", value=int(card_number(card, "Dia pago")), min_value=1, max_value=31, step=1, key=f"card_due_{index}")

            money_cols = st.columns(4)
            with money_cols[0]:
                limit = money_text_input("Total limit", card_number(card, "Cupo"), f"card_limit_{index}")
            with money_cols[1]:
                balance = money_text_input("Used", card_number(card, "Saldo"), f"card_balance_{index}")
            with money_cols[2]:
                minimum = money_text_input("Minimum", card_number(card, "Minimo"), f"card_minimum_{index}")
            with money_cols[3]:
                extra_spend = money_text_input("Extra spend", card_number(card, "Gasto extra"), f"card_extra_spend_{index}")

            minimum_due = st.checkbox("Minimum due this paycheck", value=bool(card.get("Minimo toca", False)), key=f"card_min_due_{index}")
            utilization = (balance / limit * 100) if limit > 0 else 0.0
            st.progress(min(1.0, max(0.0, utilization / 100)), text=f"{money(balance)} used of {money(limit)} ({utilization:.0f}%)")

            edited_rows.append(
                {
                    "Tarjeta": name,
                    "APR %": apr,
                    "Cupo": limit,
                    "Saldo": balance,
                    "Dia pago": due_day,
                    "Minimo toca": minimum_due,
                    "Minimo": minimum,
                    "Gasto extra": extra_spend,
                    "Notas": notes,
                }
            )
    return pd.DataFrame(edited_rows, columns=list(DEFAULT_DATA["cards"][0].keys()))


def render_debts_editor(debts: pd.DataFrame) -> pd.DataFrame:
    edited_rows = []
    if debts.empty:
        st.caption("No personal debts yet.")
    for index, debt in debts.reset_index(drop=True).iterrows():
        default_name = str(debt.get("Name", ""))
        label_name = default_name or f"Debt {index + 1}"
        with st.expander(label_name, expanded=index == 0):
            order_col, c1, c2, c3 = st.columns([.42, 1.15, 1, .65])
            with order_col:
                st.markdown("Move")
                up_disabled = index == 0
                down_disabled = index >= len(debts) - 1
                if st.button("↑", key=f"debt_move_up_{index}", disabled=up_disabled, use_container_width=True):
                    st.session_state.data["personal_debts"][index - 1], st.session_state.data["personal_debts"][index] = (
                        st.session_state.data["personal_debts"][index],
                        st.session_state.data["personal_debts"][index - 1],
                    )
                    save_data(st.session_state.data)
                    st.rerun()
                if st.button("↓", key=f"debt_move_down_{index}", disabled=down_disabled, use_container_width=True):
                    st.session_state.data["personal_debts"][index + 1], st.session_state.data["personal_debts"][index] = (
                        st.session_state.data["personal_debts"][index],
                        st.session_state.data["personal_debts"][index + 1],
                    )
                    save_data(st.session_state.data)
                    st.rerun()
            with c1:
                name = st.text_input("Name", value=default_name, key=f"debt_name_{index}")
                notes = st.text_input("Notes", value=str(debt.get("Notes", "")), key=f"debt_notes_{index}")
            with c2:
                amount = money_text_input("Amount left", parse_money(str(debt.get("Amount", 0.0))), f"debt_amount_{index}")
            with c3:
                include = st.checkbox("Include", value=bool(debt.get("Include", True)), key=f"debt_include_{index}")
            edited_rows.append({"Name": name, "Amount": amount, "Priority": index + 1, "Include": include, "Notes": notes})
    return pd.DataFrame(edited_rows, columns=list(DEFAULT_DATA["personal_debts"][0].keys()))


def render_debt_snapshot(debts: pd.DataFrame) -> None:
    if debts.empty:
        st.info("No personal debts yet.")
        return
    rows = []
    for index, debt in debts.reset_index(drop=True).iterrows():
        meta = "Top priority" if index == 0 else ("Included" if bool(debt.get("Include", True)) else "Paused")
        rows.append(
            textwrap.dedent(
                f"""
                <div class="debt-row-card">
                    <span class="mini-card-icon pink">♡</span>
                    <div>
                        <div class="debt-row-name">{html.escape(str(debt.get("Name", "")))}</div>
                        <div class="debt-row-meta">{html.escape(meta)}</div>
                    </div>
                    <div class="debt-row-amount">{money(parse_money(str(debt.get("Amount", 0.0))))}</div>
                    <div class="debt-row-chevron">›</div>
                </div>
                """
            ).strip()
        )
    st.markdown("".join(rows), unsafe_allow_html=True)


def render_debt_totals(total_debt: float, active_debt: float) -> None:
    cards = [
        ("Total personal debt", money(total_debt), "$", "purple"),
        ("Active priority amount", money(active_debt), "☆", "yellow"),
    ]
    html_cards = "".join(
        textwrap.dedent(
            f"""
            <div class="mini-card">
                <span class="mini-card-icon {html.escape(color)}">{html.escape(icon)}</span>
                <div>
                    <div class="mini-card-label">{html.escape(label)}</div>
                    <div class="mini-card-value">{html.escape(value)}</div>
                </div>
            </div>
            """
        ).strip()
        for label, value, icon, color in cards
    )
    st.markdown(f'<div class="debt-total-grid">{html_cards}</div>', unsafe_allow_html=True)


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            saved = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            data = deepcopy(DEFAULT_DATA)
            data.update(saved)
            data["settings"] = {**DEFAULT_DATA["settings"], **saved.get("settings", {})}
            data["routine"] = {**deepcopy(DEFAULT_DATA["routine"]), **saved.get("routine", {})}
            data["routine"].setdefault("activities", deepcopy(DEFAULT_ROUTINE_ACTIVITIES))
            data["routine"].setdefault("completions", {})
            data["routine"].setdefault("future_me", {})
            data["routine"].setdefault("mantra_index", 0)
            return data
        except Exception:
            return deepcopy(DEFAULT_DATA)
    return deepcopy(DEFAULT_DATA)


def save_data(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def require_password() -> None:
    PASSCODE_LENGTH = 4
    password = st.secrets.get("APP_PASSWORD", "")
    if not password:
        return
    if st.session_state.get("authenticated"):
        return

    st.session_state.setdefault("passcode_input", "")
    st.session_state.setdefault("passcode_error", False)

    render_login_hero()

    def add_digit(digit: str) -> None:
        st.session_state.passcode_input = (st.session_state.passcode_input + digit)[-PASSCODE_LENGTH:]
        st.session_state.passcode_error = False
        if len(st.session_state.passcode_input) == PASSCODE_LENGTH:
            submit_passcode()

    def backspace() -> None:
        st.session_state.passcode_input = st.session_state.passcode_input[:-1]
        st.session_state.passcode_error = False

    def clear_passcode() -> None:
        st.session_state.passcode_input = ""
        st.session_state.passcode_error = False

    def submit_passcode() -> None:
        if st.session_state.passcode_input == password:
            st.session_state.authenticated = True
        else:
            st.session_state.passcode_input = ""
            st.session_state.passcode_error = True

    with st.container():
        st.markdown('<div class="passcode-grid-marker"></div>', unsafe_allow_html=True)
        for row in (("1", "2", "3"), ("4", "5", "6"), ("7", "8", "9")):
            cols = st.columns(3)
            for col, digit in zip(cols, row):
                col.button(digit, key=f"passcode_{digit}", use_container_width=True, on_click=add_digit, args=(digit,))

        cols = st.columns(3)
        cols[0].button("Del", key="passcode_backspace", use_container_width=True, on_click=backspace)
        cols[1].button("0", key="passcode_0", use_container_width=True, on_click=add_digit, args=("0",))
        cols[2].button("⌫", key="passcode_clear", use_container_width=True, on_click=clear_passcode)

    st.markdown('<div class="login-footer-note">Just one more day.</div><div class="login-footer-heart">♥</div>', unsafe_allow_html=True)

    if st.session_state.get("authenticated"):
        st.rerun()
    if st.session_state.passcode_error:
        st.error("Incorrect passcode.")
    st.stop()


def init_state() -> None:
    if "data" not in st.session_state:
        st.session_state.data = load_data()
    st.session_state.data.setdefault("personal_debts", deepcopy(DEFAULT_DATA["personal_debts"]))
    st.session_state.data.setdefault("settings", deepcopy(DEFAULT_DATA["settings"]))
    st.session_state.data["settings"] = {**DEFAULT_DATA["settings"], **st.session_state.data["settings"]}
    st.session_state.data.setdefault("routine", deepcopy(DEFAULT_DATA["routine"]))
    st.session_state.data["routine"].setdefault("activities", deepcopy(DEFAULT_ROUTINE_ACTIVITIES))
    st.session_state.data["routine"].setdefault("completions", {})
    st.session_state.data["routine"].setdefault("future_me", {})
    st.session_state.data["routine"].setdefault("mantra_index", 0)


def cards_df() -> pd.DataFrame:
    return pd.DataFrame(st.session_state.data["cards"], columns=list(DEFAULT_DATA["cards"][0].keys()))


def expenses_df() -> pd.DataFrame:
    expenses = pd.DataFrame(st.session_state.data["expenses"], columns=list(DEFAULT_DATA["expenses"][0].keys()))
    if not expenses.empty and "Tipo" in expenses:
        expenses["Tipo"] = expenses["Tipo"].replace({"Fijo": "Fixed", "Variable": "Variable", "Auto debit": "Auto debit"})
    return expenses


def personal_debts_df() -> pd.DataFrame:
    debts = st.session_state.data.get("personal_debts", DEFAULT_DATA["personal_debts"])
    return pd.DataFrame(debts, columns=list(DEFAULT_DATA["personal_debts"][0].keys()))


def routine_data() -> dict:
    return st.session_state.data.setdefault("routine", deepcopy(DEFAULT_DATA["routine"]))


def routine_date_key(day: date | None = None) -> str:
    return (day or date.today()).isoformat()


def activity_key(activity: dict) -> str:
    return str(activity.get("Name", "")).strip()


def activity_days(activity: dict) -> list[int]:
    days = activity.get("Days", [])
    return [int(day) for day in days if str(day).isdigit()]


def activity_due_on(activity: dict, day_index: int) -> bool:
    return day_index in activity_days(activity)


def scheduled_activities(day_index: int | None = None) -> list[dict]:
    index = date.today().weekday() if day_index is None else day_index
    return [activity for activity in routine_data().get("activities", []) if activity_due_on(activity, index)]


def completion_for(day_key: str) -> dict:
    completions = routine_data().setdefault("completions", {})
    return completions.setdefault(day_key, {})


def is_activity_done(activity: dict, day_key: str) -> bool:
    return bool(completion_for(day_key).get(activity_key(activity), False))


def set_activity_done(activity: dict, day_key: str, done: bool) -> None:
    completion_for(day_key)[activity_key(activity)] = bool(done)


def week_start(day: date | None = None) -> date:
    current = day or date.today()
    return current - timedelta(days=current.weekday())


def render_routine_summary() -> None:
    today_key = routine_date_key()
    due_today = scheduled_activities()
    completed = sum(1 for activity in due_today if is_activity_done(activity, today_key))
    total = len(due_today)
    progress = completed / total if total else 0.0
    routine = routine_data()
    mantra = MANTRAS[int(routine.get("mantra_index", 0)) % len(MANTRAS)]

    st.markdown(
        f"""
        <div class="routine-hero">
            <div class="routine-kicker">Small habits. Big results.</div>
            <div class="routine-title">Good morning, Gina</div>
            <div class="routine-subtitle">for my best version</div>
            <div class="routine-progress-text">{completed} / {total} habits completed today</div>
            <div class="routine-meta">{date.today().strftime("%A, %B %d")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(progress, text=f"{progress:.0%} complete")

    c1, c2, c3 = st.columns(3)
    non_negotiables = [activity for activity in due_today if bool(activity.get("Non-negotiable", False))]
    non_done = sum(1 for activity in non_negotiables if is_activity_done(activity, today_key))
    with c1:
        st.markdown(
            f'<div class="routine-mini-card"><div class="routine-mini-label">Non-negotiables</div><div class="routine-mini-value">{non_done} / {len(non_negotiables)}</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="routine-mini-card"><div class="routine-mini-label">Today focus</div><div class="routine-mini-value">{WEEKDAYS[date.today().weekday()]}</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="routine-mini-card"><div class="routine-mini-label">Future me</div><div class="routine-mini-value">{routine.get("future_me", {}).get(today_key, "Choose today").title()}</div></div>',
            unsafe_allow_html=True,
        )

    mantra_left, mantra_right = st.columns([1.5, 1])
    with mantra_left:
        st.markdown(
            f'<div class="coach-card"><div class="coach-title">Today&apos;s Mantra</div><div class="mantra-text">{html.escape(mantra)}</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("New phrase", use_container_width=True):
            routine["mantra_index"] = int(routine.get("mantra_index", 0)) + 1
            save_data(st.session_state.data)
            st.rerun()
    with mantra_right:
        st.markdown(
            '<div class="coach-card"><div class="coach-title">Future Me Check</div><div class="coach-copy">Is what I am doing today helping tomorrow&apos;s Gina?</div></div>',
            unsafe_allow_html=True,
        )
        yes_col, no_col = st.columns(2)
        if yes_col.button("Yes", type="primary", use_container_width=True):
            routine.setdefault("future_me", {})[today_key] = "yes"
            save_data(st.session_state.data)
            st.rerun()
        if no_col.button("Not yet", use_container_width=True):
            routine.setdefault("future_me", {})[today_key] = "not yet"
            save_data(st.session_state.data)
            st.rerun()


def render_routine_sections() -> None:
    today_key = routine_date_key()
    due_today = scheduled_activities()
    changed = False

    for start in range(0, len(ROUTINE_SECTIONS), 2):
        cols = st.columns(2)
        for offset, col in enumerate(cols):
            section_index = start + offset
            if section_index >= len(ROUTINE_SECTIONS):
                continue
            section = ROUTINE_SECTIONS[section_index]
            activities = [activity for activity in due_today if activity.get("Section") == section]
            with col.container():
                st.markdown('<div class="routine-section-marker"></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="routine-section-heading"><span>{html.escape(section)}</span><span>♡</span></div>', unsafe_allow_html=True)
                if not activities:
                    st.caption("Nothing scheduled for today.")
                for activity in activities:
                    key = activity_key(activity)
                    check_col, text_col = st.columns([.14, .86], vertical_alignment="center")
                    checked = check_col.checkbox(
                        key,
                        value=is_activity_done(activity, today_key),
                        key=f"routine_{today_key}_{section}_{key}",
                        label_visibility="collapsed",
                    )
                    text_col.markdown(f"**{html.escape(key)}**")
                    if checked != is_activity_done(activity, today_key):
                        set_activity_done(activity, today_key, checked)
                        changed = True
                    note = str(activity.get("Notes", "")).strip()
                    if note:
                        st.markdown(f'<div class="routine-note">{html.escape(note)}</div>', unsafe_allow_html=True)
    if changed:
        save_data(st.session_state.data)
        st.rerun()


def render_add_activity() -> None:
    with st.expander("Add routine activity", expanded=False):
        with st.form("add_routine_activity", clear_on_submit=True):
            name = st.text_input("Activity name", placeholder="Example: Facial mask")
            section = st.selectbox("Section", ROUTINE_SECTIONS)
            days = st.multiselect("Days of the week", WEEKDAYS, default=WEEKDAYS)
            non_negotiable = st.checkbox("Non-negotiable")
            notes = st.text_input("Notes", placeholder="Optional")
            submitted = st.form_submit_button("Add activity", type="primary", use_container_width=True)
            if submitted and name.strip():
                routine_data()["activities"].append(
                    {
                        "Name": name.strip(),
                        "Section": section,
                        "Days": [WEEKDAYS.index(day) for day in days],
                        "Non-negotiable": bool(non_negotiable),
                        "Notes": notes.strip(),
                    }
                )
                save_data(st.session_state.data)
                st.success("Activity added.")
                st.rerun()


def render_emergency_mode() -> None:
    st.markdown(
        '<div class="coach-card"><div class="coach-title">Emergency Mode</div><div class="coach-copy">Pick the feeling. Then do the tiny version.</div></div>',
        unsafe_allow_html=True,
    )
    choice = st.selectbox("What is coming up?", list(EMERGENCY_RESPONSES.keys()))
    st.info(EMERGENCY_RESPONSES[choice])


def render_weekly_tracker() -> None:
    start = week_start()
    activities = [activity for activity in routine_data().get("activities", []) if bool(activity.get("Non-negotiable", False))]
    st.markdown("#### Weekly Dashboard")
    header = '<div class="week-row"><div></div>' + "".join(f'<div class="week-day">{day}</div>' for day in WEEKDAY_ABBR) + "</div>"
    rows = [header]
    for activity in activities:
        dots = []
        for day_offset in range(7):
            current_day = start + timedelta(days=day_offset)
            if not activity_due_on(activity, day_offset):
                dots.append('<div class="week-dot"><span style="opacity:.18"></span></div>')
                continue
            status = "done" if is_activity_done(activity, current_day.isoformat()) else ""
            dots.append(f'<div class="week-dot {status}"><span></span></div>')
        rows.append(f'<div class="week-row"><div class="week-name">{html.escape(activity_key(activity))}</div>{"".join(dots)}</div>')
    st.markdown(f'<div class="coach-card">{"".join(rows)}</div>', unsafe_allow_html=True)


def render_routine_dashboard() -> None:
    render_routine_summary()
    st.divider()
    render_routine_sections()
    render_add_activity()
    st.divider()
    coach_col, week_col = st.columns([.9, 1.35])
    with coach_col:
        render_emergency_mode()
    with week_col:
        render_weekly_tracker()


def render_app_header() -> None:
    rituals = [
        ("☊", "Move"),
        ("◌", "Nourish"),
        ("♢", "Hydrate"),
        ("✿", "Self Care"),
        ("☾", "Rest"),
    ]
    ritual_html = "".join(
        f"""
        <div class="ritual-item">
            <div class="ritual-icon">{icon}</div>
            <div class="ritual-label">{label}</div>
        </div>
        """
        for icon, label in rituals
    )
    st.markdown(
        f"""
        <div class="wellness-top">
            <div class="wellness-greeting">Good morning, Gina.</div>
            <div class="wellness-sub">Small habits, money clarity, and one more promise kept today.</div>
            <div class="ritual-strip">{ritual_html}</div>
            <div class="discipline-card">
                <span class="quote">“</span>
                <span class="discipline-main"> Discipline today, </span>
                <span class="discipline-script">freedom tomorrow.</span>
                <span class="quote"> ”</span>
            </div>
            <div class="become-pill">Let's become <span>her.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def save_personal_debts(debts: pd.DataFrame) -> None:
    cleaned = debts.fillna("").to_dict("records")
    for index, debt in enumerate(cleaned, start=1):
        debt["Priority"] = index
    st.session_state.data["personal_debts"] = cleaned
    save_data(st.session_state.data)


def included_expenses(expenses: pd.DataFrame) -> pd.DataFrame:
    if expenses.empty:
        return expenses
    return expenses[expenses["Incluir"].fillna(False)]


def card_auto_debit(card_name: str, expenses: pd.DataFrame) -> float:
    inc = included_expenses(expenses)
    if inc.empty:
        return 0.0
    return float(inc.loc[inc["Cuenta/Tarjeta"].str.lower() == card_name.lower(), "Monto quincena"].sum())


def is_card_account(account: str, cards: pd.DataFrame) -> bool:
    names = set(cards["Tarjeta"].astype(str).str.lower())
    return str(account).lower() in names


def calculate_plan(settings: dict, cards: pd.DataFrame, expenses: pd.DataFrame, personal_debts: pd.DataFrame) -> dict:
    cards = cards.copy()
    expenses = expenses.copy()
    if cards.empty:
        cards = pd.DataFrame(columns=DEFAULT_DATA["cards"][0].keys())
    if expenses.empty:
        expenses = pd.DataFrame(columns=DEFAULT_DATA["expenses"][0].keys())
    if personal_debts.empty:
        personal_debts = pd.DataFrame(columns=DEFAULT_DATA["personal_debts"][0].keys())

    for col in ["APR %", "Cupo", "Saldo", "Minimo", "Gasto extra"]:
        cards[col] = pd.to_numeric(cards[col], errors="coerce").fillna(0.0)
    for col in ["Monto quincena"]:
        expenses[col] = pd.to_numeric(expenses[col], errors="coerce").fillna(0.0)

    included = included_expenses(expenses)
    checking_total = 0.0
    if not included.empty:
        checking_total = float(
            included.loc[~included["Cuenta/Tarjeta"].apply(lambda account: is_card_account(account, cards)), "Monto quincena"].sum()
        )

    rows = []
    for _, card in cards.iterrows():
        auto_debit = card_auto_debit(str(card["Tarjeta"]), expenses)
        minimum = float(card["Minimo"]) if bool(card["Minimo toca"]) else 0.0
        extra = float(card["Gasto extra"])
        required = minimum + auto_debit + extra
        rows.append(
            {
                "Tarjeta": card["Tarjeta"],
                "Minimo si toca": minimum,
                "Debitos auto": auto_debit,
                "Gastos extra": extra,
                "Pago exacto ahora": required,
                "APR %": float(card["APR %"]),
                "Saldo": float(card["Saldo"]),
                "Payoff con SoFi": bool(float(settings["sofi"]) >= float(card["Saldo"]) > 0),
                "Notas": card.get("Notas", ""),
            }
        )
    card_plan = pd.DataFrame(rows)

    available = max(0.0, float(settings["cash_now"]) - float(settings["reserve"]) - float(settings["groceries"]))
    card_required = float(card_plan["Pago exacto ahora"].sum()) if not card_plan.empty else 0.0
    after_required = available - checking_total - card_required
    debt_rows = []
    debt_payment = 0.0
    debt_target = None
    debt_extra_pool = max(0.0, after_required) if settings.get("debts_first", settings.get("mom_first", True)) else 0.0
    if debt_extra_pool > 0 and not personal_debts.empty:
        debts = personal_debts.reset_index(drop=True).copy()
        debts["Amount"] = pd.to_numeric(debts["Amount"], errors="coerce").fillna(0.0)
        debts["Priority"] = debts.index + 1
        debts = debts[debts["Include"].fillna(True).astype(bool) & (debts["Amount"] > 0)]
        remaining_pool = debt_extra_pool
        for _, debt in debts.iterrows():
            pay = min(float(debt["Amount"]), remaining_pool)
            if pay <= 0:
                break
            debt_rows.append({"Name": debt["Name"], "Priority": int(debt["Priority"]), "Amount left": float(debt["Amount"]), "Suggested payment": pay})
            if debt_target is None:
                debt_target = debt
            debt_payment += pay
            remaining_pool -= pay
    mom_payment = debt_payment
    card_extra = max(0.0, after_required - debt_payment)

    active_cards = card_plan[card_plan["Saldo"] > 0].copy()
    target = None
    if not active_cards.empty:
        if settings.get("strategy") in ("Lowest balance", "Saldo mas bajo"):
            target = active_cards.sort_values("Saldo", ascending=True).iloc[0]
        else:
            target = active_cards.sort_values("APR %", ascending=False).iloc[0]

    account_rows = []
    if not included.empty:
        account_rows.extend(
            included.groupby("Cuenta/Tarjeta", dropna=False)["Monto quincena"]
            .sum()
            .reset_index()
            .rename(columns={"Cuenta/Tarjeta": "Cuenta / tarjeta", "Monto quincena": "Monto"})
            .to_dict("records")
        )
    account_rows.extend(
        card_plan.loc[card_plan["Pago exacto ahora"] > 0, ["Tarjeta", "Pago exacto ahora"]]
        .rename(columns={"Tarjeta": "Cuenta / tarjeta", "Pago exacto ahora": "Monto"})
        .to_dict("records")
    )
    account_plan = pd.DataFrame(account_rows)
    if not account_plan.empty:
        account_plan = account_plan.groupby("Cuenta / tarjeta", dropna=False)["Monto"].sum().reset_index()
        account_plan = account_plan.sort_values("Monto", ascending=False)

    return {
        "available": available,
        "checking_total": checking_total,
        "card_required": card_required,
        "after_required": after_required,
        "mom_payment": mom_payment,
        "debt_payment": debt_payment,
        "debt_target": debt_target,
        "debt_plan": pd.DataFrame(debt_rows),
        "card_extra": card_extra,
        "target": target,
        "card_plan": card_plan,
        "account_plan": account_plan,
    }


def save_tables(cards: pd.DataFrame, expenses: pd.DataFrame) -> None:
    st.session_state.data["cards"] = cards.fillna("").to_dict("records")
    st.session_state.data["expenses"] = expenses.fillna("").to_dict("records")
    save_data(st.session_state.data)


def settings_panel() -> dict:
    settings = st.session_state.data["settings"]
    with st.container():
        st.markdown('<div class="section-shell-marker paycheck-shell"></div>', unsafe_allow_html=True)
        section_title("Today's Paycheck", "✧", "✦")
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container():
                field_card_header("▣", "purple", "Pay date")
                settings["pay_date"] = st.date_input("Pay date", value=date.fromisoformat(settings["pay_date"]), label_visibility="collapsed").isoformat()
            with st.container():
                field_card_header("$", "blue", "Cash available today")
                money_input("Cash available today", settings, "cash_now", label_visibility="collapsed")
            with st.container():
                field_card_header("▤", "orange", "Reserve I won't touch")
                money_input("Reserve I won't touch", settings, "reserve", label_visibility="collapsed")
        with col2:
            with st.container():
                field_card_header("▾", "pink", "Planned groceries")
                money_input("Planned groceries", settings, "groceries", label_visibility="collapsed")
            with st.container():
                field_card_header("⌂", "teal", "Available in SoFi")
                money_input("Available in SoFi", settings, "sofi", label_visibility="collapsed")
        with col3:
            with st.container():
                field_card_header("●", "purple", "If there's extra, personal debts first")
                settings["debts_first"] = st.toggle("If there's extra, personal debts first", value=bool(settings.get("debts_first", settings.get("mom_first", True))), label_visibility="collapsed")
            with st.container():
                field_card_header("↗", "purple", "Extra-to-cards strategy")
                strategy_options = ["Highest APR", "Lowest balance"]
                current_strategy = "Lowest balance" if settings.get("strategy") in ("Lowest balance", "Saldo mas bajo") else "Highest APR"
                settings["strategy"] = st.selectbox("Extra-to-cards strategy", strategy_options, index=strategy_options.index(current_strategy), label_visibility="collapsed")
            if st.button("+ Save changes", type="primary", use_container_width=True):
                save_data(st.session_state.data)
                st.success("Saved.")
    return settings


def render_plan(plan: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Real available", money(plan["available"]))
    c2.metric("Checking / cash", money(plan["checking_total"]))
    c3.metric("Cards required", money(plan["card_required"]))
    c4.metric("Left after required", money(plan["after_required"]))

    if plan["after_required"] < 0:
        st.error(f"You are short {money(abs(plan['after_required']))} to cover required payments without touching the reserve.")
    elif plan["card_extra"] > 0:
        st.success("There is extra money after covering what is required.")
    else:
        st.info("Required payments are covered, with no extra left over.")

    left, right = st.columns([1, 1.25])
    with left:
        st.markdown("#### Set aside / pay by account")
        if plan["account_plan"].empty:
            st.caption("Select expenses or minimums to see payments.")
        else:
            render_payment_rows(
                [
                    {"title": row["Cuenta / tarjeta"], "meta": "Account total", "amount": row["Monto"]}
                    for _, row in plan["account_plan"].iterrows()
                ]
            )
    with right:
        st.markdown("#### What to pay on each card")
        card_rows = []
        for _, row in plan["card_plan"].iterrows():
            amount = float(row["Pago exacto ahora"])
            if amount <= 0:
                continue
            meta_parts = [
                f"Minimum {money(row['Minimo si toca'])}",
                f"Auto debits {money(row['Debitos auto'])}",
                f"Extra spend {money(row['Gastos extra'])}",
            ]
            card_rows.append({"title": row["Tarjeta"], "meta": " | ".join(meta_parts), "amount": amount})
        render_payment_rows(card_rows)

    st.markdown("#### Extra recommendation")
    target = plan["target"]
    if plan["debt_payment"] > 0:
        debt_target = plan["debt_target"]
        target_name = debt_target["Name"] if debt_target is not None else "personal debts"
        st.write(f"Personal debts first: **{money(plan['debt_payment'])}** starting with **{target_name}**.")
    if target is not None and plan["card_extra"] > 0:
        extra = min(float(plan["card_extra"]), float(target["Saldo"]))
        st.write(f"Then, suggested extra to **{target['Tarjeta']}**: **{money(extra)}**.")
    payoff = plan["card_plan"].loc[plan["card_plan"]["Payoff con SoFi"], "Tarjeta"].tolist()
    if payoff:
        st.write("With SoFi, you could fully pay off: **" + ", ".join(payoff) + "**.")


def main() -> None:
    inject_girlie_theme()
    inject_app_icon_links()
    require_password()
    init_state()

    render_app_header()

    tab_routine, tab_money, tab_history_data = st.tabs(["✧ Routine", "◇ Money", "▥ Data"])

    with tab_routine:
        render_routine_dashboard()

    with tab_money:
        settings = settings_panel()
        with st.container():
            st.markdown('<div class="section-shell-marker debt-shell"></div>', unsafe_allow_html=True)
            section_title("Personal Debts", "✧", "♡")
            debts_current = personal_debts_df()
            total_debt = float(pd.to_numeric(debts_current["Amount"], errors="coerce").fillna(0.0).sum()) if not debts_current.empty else 0.0
            active_debt = float(pd.to_numeric(debts_current.loc[debts_current["Include"].fillna(True).astype(bool), "Amount"], errors="coerce").fillna(0.0).sum()) if not debts_current.empty else 0.0
            render_debt_totals(total_debt, active_debt)
            render_debt_snapshot(debts_current)

            if st.button("Add personal debt", use_container_width=True):
                st.session_state.data["personal_debts"].append({"Name": "New debt", "Amount": 0.0, "Priority": len(debts_current) + 1, "Include": True, "Notes": ""})
                save_data(st.session_state.data)
                st.rerun()

            with st.expander("Edit personal debts", expanded=False):
                debts = render_debts_editor(debts_current)
                if st.button("Save debts", type="primary"):
                    save_personal_debts(debts)
                    st.success("Debts saved.")

        st.divider()
        st.subheader("Credit Cards")
        card_summary = cards_df()
        render_plan_credit_cards(card_summary)

        with st.expander("Add credit card", expanded=False):
            with st.form("add_credit_card_form", clear_on_submit=True):
                f1, f2 = st.columns([1.25, 1])
                with f1:
                    new_name = st.text_input("Card name", placeholder="Chase Freedom")
                    new_notes = st.text_input("Notes", placeholder="0% promo, travel card, etc.")
                with f2:
                    new_apr = st.number_input("APR %", value=0.0, min_value=0.0, step=0.25, format="%.2f")
                    new_due_day = st.number_input("Due day", value=1, min_value=1, max_value=31, step=1)

                m1, m2, m3 = st.columns(3)
                with m1:
                    new_limit = st.text_input("Total limit", placeholder="$0.00")
                with m2:
                    new_used = st.text_input("Used amount", placeholder="$0.00")
                with m3:
                    new_minimum = st.text_input("Minimum payment", placeholder="$0.00")

                add_submitted = st.form_submit_button("Add credit card", type="primary", use_container_width=True)
                if add_submitted:
                    st.session_state.data["cards"].append(
                        {
                            "Tarjeta": new_name.strip() or "New card",
                            "APR %": float(new_apr),
                            "Cupo": parse_money(new_limit),
                            "Saldo": parse_money(new_used),
                            "Dia pago": int(new_due_day),
                            "Minimo toca": False,
                            "Minimo": parse_money(new_minimum),
                            "Gasto extra": 0.0,
                            "Notas": new_notes.strip(),
                        }
                    )
                    save_data(st.session_state.data)
                    st.success("Credit card added.")
                    st.rerun()

        with st.expander("Edit full card details", expanded=False):
            cards = render_cards_editor(card_summary)
            if st.button("Save cards", type="primary"):
                save_tables(cards, expenses_df())
                st.success("Cards saved.")

        st.divider()
        st.subheader("Expenses and Debits")
        expenses = st.data_editor(
            expenses_df(),
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Categoria": st.column_config.TextColumn("Category"),
                "Nombre": st.column_config.TextColumn("Name"),
                "Cuenta/Tarjeta": st.column_config.TextColumn("Account/Card"),
                "Monto quincena": st.column_config.NumberColumn("Paycheck amount", format="$%.2f"),
                "Tipo": st.column_config.SelectboxColumn("Type", options=["Fixed", "Variable", "Auto debit"]),
                "Incluir": st.column_config.CheckboxColumn("Include"),
                "Notas": st.column_config.TextColumn("Notes"),
            },
            key="expenses_editor",
        )
        if st.button("Save expenses", type="primary"):
            save_tables(cards_df(), expenses)
            st.success("Expenses saved.")

        st.divider()
        st.subheader("Summary")
        current_cards = cards_df()
        current_expenses = expenses_df()
        current_debts = personal_debts_df()
        total_limit = float(pd.to_numeric(current_cards["Cupo"], errors="coerce").fillna(0.0).sum()) if not current_cards.empty else 0.0
        total_used = float(pd.to_numeric(current_cards["Saldo"], errors="coerce").fillna(0.0).sum()) if not current_cards.empty else 0.0
        total_available = max(0.0, total_limit - total_used)
        avg_apr = float(pd.to_numeric(current_cards["APR %"], errors="coerce").fillna(0.0).mean()) if not current_cards.empty else 0.0
        render_credit_totals(total_limit, total_used, total_available, avg_apr)

        plan = calculate_plan(settings, current_cards, current_expenses, current_debts)
        render_plan(plan)
        if st.button("Save this paycheck snapshot", type="primary"):
            target_name = plan["target"]["Tarjeta"] if plan["target"] is not None else ""
            st.session_state.data["history"].append(
                {
                    "Fecha": settings["pay_date"],
                    "Cuenta inicial": settings["cash_now"],
                    "Obligatorio": plan["checking_total"] + plan["card_required"],
                    "Mama": plan["debt_payment"],
                    "Extra tarjetas": plan["card_extra"],
                    "Tarjeta extra": target_name,
                }
            )
            save_data(st.session_state.data)
            st.success("Snapshot saved.")

    with tab_history_data:
        st.subheader("History")
        history = pd.DataFrame(st.session_state.data["history"])
        if history.empty:
            st.info("No saved snapshots yet.")
        else:
            history_shown = english_columns(history, HISTORY_LABELS)
            history_shown = format_money_columns(history_shown, ["Starting cash", "Required", "Mom", "Card extra"])
            st.dataframe(history_shown, use_container_width=True, hide_index=True)
        if st.button("Clear history"):
            st.session_state.data["history"] = []
            save_data(st.session_state.data)
            st.rerun()

        st.divider()
        st.subheader("Backup")
        payload = json.dumps(st.session_state.data, indent=2, ensure_ascii=False)
        st.download_button("Download JSON backup", payload, file_name="my_nest_egg_backup.json", mime="application/json")
        uploaded = st.file_uploader("Import JSON backup", type=["json"])
        if uploaded and st.button("Import backup"):
            st.session_state.data = json.loads(uploaded.read().decode("utf-8"))
            save_data(st.session_state.data)
            st.success("Backup imported.")
            st.rerun()
        st.warning("If you publish this app, protect access with APP_PASSWORD in Streamlit secrets.")

    save_data(st.session_state.data)


if __name__ == "__main__":
    main()
