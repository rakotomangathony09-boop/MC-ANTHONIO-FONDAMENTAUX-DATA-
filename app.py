import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz
import requests
import os

# --- CONFIGURATION SYSTÈME ---
st.set_page_config(page_title="MICHEL ANTHONIO - XAU TERMINAL", layout="wide", initial_sidebar_state="collapsed")

# --- RÉCUPÉRATION DES SECRETS (RENDER & LOCAL) ---
def get_secret(key):
    return os.environ.get(key) or (st.secrets[key] if key in st.secrets else None)

# --- STYLE BLOOMBERG ÉLITE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto Mono', monospace; background-color: #000000; color: #00CCFF; }
    .stApp { background-color: #000000; }
    .bloomberg-header { color: #FF9900; font-size: 28px; font-weight: bold; border-bottom: 2px solid #FF9900; padding-bottom: 10px; }
    .user-tag { color: #00CCFF; font-size: 16px; margin-top: 5px; }
    .metric-box { border: 1px solid #333; padding: 15px; border-radius: 5px; background: #0a0a0a; }
    .high-impact { color: #FF0000; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DU TEMPS (ANTANANARIVO) ---
tana_tz = pytz.timezone('Indian/Antananarivo')
now_tana = datetime.now(tana_tz)

# --- HEADER ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<p class="bloomberg-header">XAU/USD INSTITUTIONAL TERMINAL v1.0</p>', unsafe_allow_html=True)
    st.markdown('<p class="user-tag">PROPRIÉTAIRE EXCLUSIF : MICHEL ANTHONIO RAKOTOMANGA</p>', unsafe_allow_html=True)
with col_h2:
    st.metric("ANTANANARIVO TIME", now_tana.strftime("%H:%M:%S"))

st.write("---")

# --- MOTEUR DE DONNÉES TEMPS RÉEL ---
@st.cache_data(ttl=60)
def get_gold_data():
    return yf.Ticker("GC=F").history(period="2d", interval="15m")

try:
    df = get_gold_data()
    price = df['Close'].iloc[-1]
    change = price - df['Close'].iloc[-2]
except Exception:
    st.error("Flux de données interrompu. Reconnexion automatique...")
    st.stop()

# --- ALGORITHME DE SCORING ---
cot_score = 4.8  
sentiment_score = 3.2 
total_score = min(10.0, cot_score + sentiment_score)

# --- DASHBOARD PRINCIPAL ---
c1, c2, c3 = st.columns([1, 2, 1])

with c1:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.subheader("MARKET STATUS")
    st.metric("GOLD LIVE", f"${price:,.2f}", f"{change:+.2f}")
    st.write("**SENTIMENT RETAIL**")
    st.progress(0.15) # Simule 85% de Shorts
    st.caption("Retail Crowd is SHORT. Strong Bullish Bias.")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.subheader("INSTITUTIONAL LIQUIDITY FLOW")
    st.line_chart(df['Close'])

with c3:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.subheader("PROBABILITY SCORE")
    st.title(f"{total_score}/10")
    if total_score >= 7.5: st.success("SIGNAL : STRONG BUY")
    elif total_score <= 2.5: st.error("SIGNAL : STRONG SELL")
    else: st.warning("SIGNAL : NEUTRAL")
    st.markdown('</div>', unsafe_allow_html=True)

# --- CALENDRIER ÉCONOMIQUE ---
st.write("---")
st.subheader("🕒 HIGH IMPACT CALENDAR (USD)")
st.markdown('<p class="high-impact">🚨 US CPI Report - Scheduled Today</p>', unsafe_allow_html=True)

# --- DÉCLENCHEUR UPTIME ROBOT (AUTOMATISATION) ---
if st.query_params.get("action") == "send_report":
    token = get_secret("TELEGRAM_TOKEN")
    chat_id = get_secret("CHAT_ID")
    if token and chat_id:
        msg = f"🏛️ **LONDON OPEN BRIEFING**\n👤 Michel Anthonio\n📊 Gold Score : {total_score}/10"
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
        st.toast("Rapport matinal envoyé !")
