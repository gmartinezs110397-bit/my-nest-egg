from __future__ import annotations

import base64
import html
import json
import textwrap
from copy import deepcopy
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image


APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "data" / "payment_data.json"
APP_ICON_FILE = APP_DIR / "assets" / "app-icon.png"
APPLE_TOUCH_ICON_FILE = APP_DIR / "assets" / "apple-touch-icon.png"


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
}


st.set_page_config(page_title="My Nest Egg", page_icon=Image.open(APP_ICON_FILE), layout="wide")


def image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def inject_app_icon_links() -> None:
    icon = image_data_uri(APP_ICON_FILE)
    apple_icon = image_data_uri(APPLE_TOUCH_ICON_FILE)
    st.markdown(
        f"""
        <link rel="icon" type="image/png" href="{icon}">
        <link rel="apple-touch-icon" href="{apple_icon}">
        <meta name="apple-mobile-web-app-title" content="My Nest Egg">
        """,
        unsafe_allow_html=True,
    )


def inject_girlie_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Arima:wght@400;600;700&family=Fraunces:opsz,wght@9..144,650;9..144,750&family=Fugaz+One&family=Grand+Hotel&family=Inter:wght@400;500;600;700;800;900&display=swap');

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
            --font-display: "Arima", "Fraunces", Georgia, serif;
            --font-fugaz: "Fugaz One", "Inter", sans-serif;
            --font-script: "Grand Hotel", cursive;
            --font-ui: "Inter", "Segoe UI", Arial, sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 10% 10%, rgba(255, 232, 117, .22), transparent 30%),
                radial-gradient(circle at 86% 14%, rgba(255, 159, 143, .20), transparent 32%),
                linear-gradient(135deg, #fffdf4 0%, #fff1e8 42%, #f7efff 100%);
            color: var(--ink);
            font-family: var(--font-ui);
        }

        .stApp:has(.girlie-login) {
            background: #ffffff;
        }

        .stApp:has(.girlie-login) [data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.92);
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
            border: 1px solid rgba(255, 159, 143, 0.34);
            border-radius: 8px;
            background: var(--soft-card);
            box-shadow: 0 14px 34px rgba(63, 43, 88, 0.08);
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
            border: 1px solid rgba(255, 159, 143, 0.32);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.74);
            box-shadow: 0 12px 32px rgba(63, 43, 88, 0.08);
            padding: 1rem;
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

        .credit-card {
            border: 1px solid rgba(255, 159, 143, 0.32);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.74);
            box-shadow: 0 12px 32px rgba(63, 43, 88, 0.08);
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
            border: 1px solid rgba(199, 164, 255, .28);
            border-radius: 8px;
            background: rgba(255, 255, 255, .70);
            padding: .7rem .85rem;
            box-shadow: 0 8px 20px rgba(63, 43, 88, .06);
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
            border: 1px solid rgba(255, 159, 143, 0.34);
            border-radius: 8px;
            background: linear-gradient(180deg, rgba(255,255,255,.82) 0%, rgba(199,164,255,.20) 100%);
            color: var(--ink);
            box-shadow: 0 8px 18px rgba(255, 159, 143, 0.12);
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
            padding: .35rem;
            margin: .75rem 0 .9rem;
            border: 1px solid rgba(255, 255, 255, .58);
            border-radius: 999px;
            background: rgba(255, 255, 255, .38);
            backdrop-filter: blur(16px);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.58), 0 12px 28px rgba(63, 43, 88, .08);
        }

        [data-baseweb="tab"] {
            min-height: 2.45rem;
            padding: 0 .95rem;
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
            background: linear-gradient(135deg, rgba(255,255,255,.88) 0%, rgba(255,232,117,.48) 48%, rgba(255,159,143,.42) 100%);
            color: #7a1c77;
            box-shadow: 0 8px 18px rgba(255, 159, 143, .16), 0 0 0 1px rgba(255,255,255,.7);
        }

        [data-baseweb="tab-highlight"] {
            display: none;
        }

        .girlie-login {
            position: relative;
            width: min(860px, 96vw);
            min-height: 208px;
            margin: 1.15rem auto .15rem;
            text-align: center;
            padding: 1.9rem 1.2rem .25rem;
            overflow: visible;
        }

        .girlie-login::before {
            display: none;
        }

        .girlie-login::after {
            content: "";
            position: absolute;
            inset: -4rem -1rem -8rem;
            background:
                radial-gradient(circle at 6% 18%, rgba(255, 159, 143, .68) 0 7px, transparent 8px),
                radial-gradient(circle at 11% 24%, rgba(255, 232, 117, .82) 0 5px, transparent 6px),
                radial-gradient(circle at 25% 8%, rgba(255, 183, 207, .74) 0 6px, transparent 7px),
                radial-gradient(circle at 77% 10%, rgba(199, 164, 255, .68) 0 8px, transparent 9px),
                radial-gradient(circle at 86% 19%, rgba(255, 232, 117, .78) 0 5px, transparent 6px),
                radial-gradient(circle at 18% 82%, rgba(199, 164, 255, .55) 0 7px, transparent 8px),
                radial-gradient(circle at 55% 92%, rgba(255, 232, 117, .72) 0 5px, transparent 6px),
                radial-gradient(circle at 82% 78%, rgba(255, 159, 143, .58) 0 7px, transparent 8px);
            animation: cloudDrift 8s ease-in-out infinite;
            pointer-events: none;
        }

        .hello-lockup {
            position: relative;
            z-index: 1;
            margin: .15rem auto 1rem;
            color: var(--ink);
        }

        .hello-line {
            display: block;
            font-family: var(--font-script);
            font-size: clamp(2.4rem, 9vw, 4.7rem);
            line-height: .95;
            color: #111111;
            text-shadow:
                0 1px 0 rgba(255, 255, 255, .92),
                0 8px 18px rgba(17, 17, 17, .08);
        }

        .wallpaper-flower {
            position: absolute;
            z-index: 1;
            --s: 1;
            --r: -5deg;
            width: 42px;
            height: 42px;
            filter: drop-shadow(0 0 12px rgba(255, 60, 172, .35));
            animation: flowerFloat 5.5s ease-in-out infinite;
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
            position: relative;
            z-index: 2;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: .85rem;
            margin: .28rem auto .65rem;
            min-height: 1.6rem;
        }

        .passcode-dot {
            width: .82rem;
            height: .82rem;
            border-radius: 50%;
            border: 2px solid rgba(63, 43, 88, .40);
            background: rgba(255, 255, 255, .34);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 14px rgba(255, 159, 143, .20);
        }

        .passcode-dot.filled {
            border-color: rgba(255,255,255,.85);
            background: var(--neon-pink);
            box-shadow: 0 0 16px rgba(255, 60, 172, .58), 0 0 24px rgba(255, 232, 117, .38);
        }

        .passcode-grid-marker {
            width: min(300px, 92vw);
            height: 0;
            margin: 0 auto;
        }

        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div[data-testid="stHorizontalBlock"] {
            width: min(270px, 92vw);
            margin-left: auto;
            margin-right: auto;
            display: flex !important;
            flex-direction: row !important;
            gap: .55rem !important;
        }

        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div[data-testid="stColumn"] {
            flex: 1 1 0 !important;
            min-width: 0 !important;
            width: 33.333% !important;
        }

        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div.stButton > button {
            width: 3.9rem;
            height: 3.9rem;
            min-height: 3.9rem;
            margin: .05rem auto;
            border-radius: 50%;
            border: 1px solid rgba(255, 255, 255, .55);
            background: rgba(255, 255, 255, .25);
            backdrop-filter: blur(14px);
            box-shadow: 0 12px 28px rgba(63, 43, 88, .12), inset 0 1px 0 rgba(255,255,255,.55);
            color: var(--ink);
            font-size: 1.28rem;
            font-family: var(--font-ui);
            font-weight: 600;
        }

        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) div.stButton > button:hover {
            border-color: rgba(255, 60, 172, .50);
            color: #7a1c77;
            box-shadow: 0 0 0 1px rgba(255,255,255,.44), 0 0 22px rgba(255, 159, 143, .34);
        }

        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) .st-key-passcode_backspace button,
        div[data-testid="stVerticalBlock"]:has(.passcode-grid-marker) .st-key-passcode_clear button {
            background: transparent;
            box-shadow: none;
            border-color: transparent;
            font-size: .82rem;
            font-weight: 600;
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
        """,
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
            <div class="wallpaper-flower one"><span></span><span></span><span></span><span></span><span></span><b></b></div>
            <div class="wallpaper-flower two"><span></span><span></span><span></span><span></span><span></span><b></b></div>
            <div class="wallpaper-flower three"><span></span><span></span><span></span><span></span><span></span><b></b></div>
            <div class="wallpaper-flower four"><span></span><span></span><span></span><span></span><span></span><b></b></div>
            <div class="wallpaper-flower five"><span></span><span></span><span></span><span></span><span></span><b></b></div>
            <div class="wallpaper-flower six"><span></span><span></span><span></span><span></span><span></span><b></b></div>
            <div class="hello-lockup">
                <span class="hello-line">Hello, baby girl.</span>
            </div>
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


def money_input(label: str, settings: dict, key: str) -> float:
    input_key = f"money_input_{key}"
    if input_key not in st.session_state:
        st.session_state[input_key] = money_field_initial(settings.get(key, 0.0))
    entered = st.text_input(label, key=input_key, placeholder="$0.00", on_change=normalize_money_state, args=(input_key,))
    parsed = parse_money(entered)
    settings[key] = parsed
    return parsed


def money_text_input(label: str, value: float, key: str) -> float:
    if key not in st.session_state:
        st.session_state[key] = money_field_initial(value)
    entered = st.text_input(label, key=key, placeholder="$0.00", on_change=normalize_money_state, args=(key,))
    return parse_money(entered)


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
        rows.append(
            {
                "title": str(debt.get("Name", "")),
                "meta": "Top priority" if index == 0 else ("Included" if bool(debt.get("Include", True)) else "Paused"),
                "amount": parse_money(str(debt.get("Amount", 0.0))),
            }
        )
    render_payment_rows(rows)


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            saved = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            data = deepcopy(DEFAULT_DATA)
            data.update(saved)
            data["settings"] = {**DEFAULT_DATA["settings"], **saved.get("settings", {})}
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
    st.markdown('<div class="passcode-grid-marker"></div>', unsafe_allow_html=True)

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

    for row in (("1", "2", "3"), ("4", "5", "6"), ("7", "8", "9")):
        cols = st.columns(3)
        for col, digit in zip(cols, row):
            col.button(digit, key=f"passcode_{digit}", use_container_width=True, on_click=add_digit, args=(digit,))

    cols = st.columns(3)
    cols[0].button("Del", key="passcode_backspace", use_container_width=True, on_click=backspace)
    cols[1].button("0", key="passcode_0", use_container_width=True, on_click=add_digit, args=("0",))
    cols[2].button("Clear", key="passcode_clear", use_container_width=True, on_click=clear_passcode)

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
    st.subheader("Today's Paycheck")
    col1, col2, col3 = st.columns(3)
    with col1:
        settings["pay_date"] = st.date_input("Pay date", value=date.fromisoformat(settings["pay_date"])).isoformat()
        money_input("Cash available today", settings, "cash_now")
        money_input("Reserve I won't touch", settings, "reserve")
    with col2:
        money_input("Planned groceries", settings, "groceries")
        money_input("Available in SoFi", settings, "sofi")
    with col3:
        settings["debts_first"] = st.toggle("If there's extra, personal debts first", value=bool(settings.get("debts_first", settings.get("mom_first", True))))
        strategy_options = ["Highest APR", "Lowest balance"]
        current_strategy = "Lowest balance" if settings.get("strategy") in ("Lowest balance", "Saldo mas bajo") else "Highest APR"
        settings["strategy"] = st.selectbox("Extra-to-cards strategy", strategy_options, index=strategy_options.index(current_strategy))
        if st.button("Save changes", type="primary", use_container_width=True):
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

    st.title("My Nest Egg")
    st.caption("A personal paycheck planner for deciding what to pay now.")

    settings = settings_panel()

    tab_plan, tab_history_data = st.tabs(["Plan", "History & Data"])

    with tab_plan:
        st.subheader("Personal Debts")
        debts_current = personal_debts_df()
        total_debt = float(pd.to_numeric(debts_current["Amount"], errors="coerce").fillna(0.0).sum()) if not debts_current.empty else 0.0
        active_debt = float(pd.to_numeric(debts_current.loc[debts_current["Include"].fillna(True).astype(bool), "Amount"], errors="coerce").fillna(0.0).sum()) if not debts_current.empty else 0.0
        d1, d2 = st.columns(2)
        d1.metric("Total personal debt", money(total_debt))
        d2.metric("Active priority amount", money(active_debt))
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
