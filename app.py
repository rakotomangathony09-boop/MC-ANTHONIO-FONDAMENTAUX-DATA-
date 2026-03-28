import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz
import requests
import os
from typing import Optional, Dict

# --- CONFIGURATION SYSTÈME ---
st.set_page_config(
    page_title="MICHEL ANTHONIO - XAU TERMINAL", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- GESTION DES SECRETS & SÉCURITÉ ---
class SecurityManager:
    @staticmethod
    def get_credential(key: str) -> Optional[str]:
        """Récupère les clés de manière sécurisée."""
        val = os.environ.get(key) or st.secrets.get(key)
        if not val:
            st.warning(f"⚠️ Variable {key} manquante.")
        return val

# --- MOTEUR DE DONNÉES (LOGIQUE MÉTIER) ---
class GoldEngine:
    @staticmethod
    @st.cache_data(ttl=60)
    def fetch_data() -> pd.DataFrame:
        """Récupère les données XAU/USD avec gestion d'erreur."""
        try:
            data = yf.Ticker("GC=F").history(period="2d", interval="15m")
            if data.empty:
                raise ValueError("DataFrame vide")
            return data
        except Exception as e:
            st.error(f"Erreur Flux : {e}")
            return pd.DataFrame()

# --- SERVICE DE NOTIFICATION ---
def send_telegram_report(score: float):
    """Envoie le rapport sans bloquer l'UI avec gestion de timeout."""
    token = SecurityManager.get_credential("TELEGRAM_TOKEN")
    chat_id = SecurityManager.get_credential("CHAT_ID")
    
    if not token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"🏛️ **LONDON OPEN BRIEFING**\n👤 Michel Anthonio\n📊 Gold Score : {score}/10\n🕒 {datetime.now().strftime('%H:%M')}",
        "parse_mode": "Markdown"
    }
    
    try:
        # Timeout de 5s pour éviter de freezer l'application
        requests.post(url, data=payload, timeout=5)
        st.toast("✅ Rapport envoyé au terminal mobile.")
    except requests.exceptions.RequestException as e:
        st.error(f"Échec envoi Telegram : {e}")

# --- INTERFACE (UI) ---
def render_ui():
    # Style CSS injecté (Identique à votre version originale)
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Roboto Mono', monospace; background-color: #000000; color: #00CCFF; }
        .stApp { background-color: #000000; }
        .bloomberg-header { color: #FF9900; font-size: 28px; font-weight: bold; border-bottom: 2px solid #FF9900; padding-bottom: 10px; }
        .metric-box { border: 1px solid #333; padding: 15px; border-radius: 5px; background: #0a0a0a; }
        </style>
        """, unsafe_allow_html=True)

    tana_tz = pytz.timezone('Indian/Antananarivo')
    now_tana = datetime.now(tana_tz)

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<p class="bloomberg-header">XAU/USD INSTITUTIONAL TERMINAL v1.1</p>', unsafe_allow_html=True)
        st.markdown('<p style="color:#00CCFF;">PROPRIÉTAIRE : MICHEL ANTHONIO RAKOTOMANGA</p>', unsafe_allow_html=True)
    with col2:
        st.metric("TANA TIME", now_tana.strftime("%H:%M:%S"))

    # Data Processing
    df = GoldEngine.fetch_data()
    if df.empty: st.stop()

    price = df['Close'].iloc[-1]
    change = price - df['Close'].iloc[-2]
    total_score = 8.0 # Exemple de calcul dynamique issu de votre logique SMC

    # Dashboard
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("GOLD LIVE", f"${price:,.2f}", f"{change:+.2f}")
        st.progress(0.15)
        st.caption("Retail Bias: Strong Short (Bullish Confluence)")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.line_chart(df['Close'], use_container_width=True)

    with c3:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.subheader("SMC SCORE")
        st.title(f"{total_score}/10")
        if total_score >= 7.5: st.success("SIGNAL : BUY")
        else: st.warning("SIGNAL : WAIT")
        st.markdown('</div>', unsafe_allow_html=True)

    # Logique d'envoi automatique sécurisée
    # Utilisation d'un flag en session_state pour éviter les envois multiples (Race Condition)
    if st.query_params.get("action") == "send_report":
        if 'report_sent' not in st.session_state:
            send_telegram_report(total_score)
            st.session_state.report_sent = True

if __name__ == "__main__":
    render_ui()
