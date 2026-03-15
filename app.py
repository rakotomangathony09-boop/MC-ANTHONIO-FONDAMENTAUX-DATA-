import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime
import pytz
import requests

# --- CONFIGURATION BLOOMBERG ---
st.set_page_config(page_title="MICHEL ANTHONIO - XAU TERMINAL", layout="wide", initial_sidebar_state="collapsed")

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

# --- TEMPS RÉEL ANTANANARIVO ---
tana_tz = pytz.timezone('Indian/Antananarivo')
now_tana = datetime.now(tana_tz)

# --- EN-TÊTE DU TERMINAL ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<p class="bloomberg-header">XAU/USD INSTITUTIONAL TERMINAL v1.0</p>', unsafe_allow_html=True)
    st.markdown('<p class="user-tag">PROPRIÉTAIRE EXCLUSIF : MICHEL ANTHONIO RAKOTOMANGA</p>', unsafe_allow_html=True)
with col_h2:
    st.metric("ANTANANARIVO TIME", now_tana.strftime("%H:%M:%S"))

st.write("---")

# --- RÉCUPÉRATION DES DONNÉES OR ---
@st.cache_data(ttl=60)
def get_gold_data():
    gold = yf.Ticker("GC=F")
    hist = gold.history(period="5d", interval="1h")
    return hist

data = get_gold_data()
current_price = data['Close'].iloc[-1]
change = current_price - data['Close'].iloc[-2]

# --- ALGORITHME DE SCORING ---
# Simulation des données COT et Sentiment (liées à votre base de données)
cot_score = 4.8  
retail_sentiment = -2.7 
final_score = min(10, max(0, cot_score + abs(retail_sentiment)))

# --- AFFICHAGE DES MODULES ---
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.subheader("ÉTAT DU MARCHÉ")
    st.metric("XAU/USD LIVE", f"${current_price:,.2f}", f"{change:+.2f}")
    st.write("---")
    st.write("**SENTIMENT RETAIL**")
    st.progress(0.12) # Simule 88% de vendeurs
    st.caption("Forte majorité vendeuse : Biais HAUSSIER détecté.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.subheader("GRAPHIQUE DE LIQUIDITÉ INSTITUTIONNELLE")
    st.line_chart(data['Close'])
    if st.button("📸 EXPORTATION VERS RÉSEAUX SOCIAUX"):
        st.info("Capture haute résolution prête pour Michel Anthonio.")

with col3:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.subheader("SCORE DE PROBABILITÉ")
    st.title(f"{final_score:.1f}/10")
    if final_score >= 7.5:
        st.success("SIGNAL : ACHAT FORT")
    elif final_score <= 2.5:
        st.error("SIGNAL : VENTE FORTE")
    else:
        st.warning("SIGNAL : ATTENTE / NEUTRE")
    st.markdown('</div>', unsafe_allow_html=True)

# --- CALENDRIER ÉCONOMIQUE ---
st.write("---")
st.subheader("🕒 CALENDRIER ÉCONOMIQUE (HIGH IMPACT)")
events = [
    {"name": "US Retail Sales", "time": "15:30", "impact": "HIGH"},
    {"name": "FOMC Meeting Minutes", "time": "21:00", "impact": "HIGH"},
]

cols = st.columns(len(events))
for i, event in enumerate(events):
    with cols[i]:
        st.markdown(f'<p class="high-impact">🚨 {event["name"]}</p>', unsafe_allow_html=True)
        st.write(f"Heure : {event['time']} (Tana)")
