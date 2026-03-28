import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import requests
import os
import plotly.graph_objects as go
from typing import Optional, Tuple, List, Dict

# --- CONFIGURATION SYSTÈME ---
st.set_page_config(
    page_title="MICHEL ANTHONIO - XAU TERMINAL ULTIMATE", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

class SecurityManager:
    """Gère l'accès sécurisé aux credentials."""
    @staticmethod
    def get_credential(key: str) -> Optional[str]:
        # Priorité aux variables d'environnement (Production)
        return os.getenv(key) or st.secrets.get(key)

class NewsEngine:
    """Moteur d'analyse fondamentale via Finnhub."""
    def __init__(self):
        self.api_key = SecurityManager.get_credential("FINNHUB_API_KEY")
        self.url = "https://finnhub.io/api/v1/calendar/economic"

    @st.cache_data(ttl=3600)
    def fetch_high_impact(_self) -> List[Dict]:
        if not _self.api_key:
            return []
        try:
            with requests.Session() as s:
                res = s.get(_self.url, params={"token": _self.api_key}, timeout=10)
                res.raise_for_status()
                data = res.json().get("economicCalendar", [])
                today = datetime.now(pytz.utc).strftime('%Y-%m-%d')
                return [n for n in data if n['country'] == 'US' and n['impact'] == 'high' and n['date'].startswith(today)]
        except Exception as e:
            st.error(f"News Engine Error: {str(e)}")
            return []

    @staticmethod
    def is_risky(news_list: List[Dict]) -> bool:
        now_utc = datetime.now(pytz.utc)
        for n in news_list:
            n_time = datetime.fromisoformat(n['date'].replace('Z', '+00:00'))
            # Fenêtre de risque : 30 min avant et après l'annonce
            if abs((now_utc - n_time).total_seconds() / 60) <= 30:
                return True
        return False

class SMCEngine:
    """Algorithme Smart Money Concepts (SMC)."""
    @staticmethod
    @st.cache_data(ttl=60)
    def get_data(symbol: str = "GC=F") -> pd.DataFrame:
        """Récupération optimisée des prix."""
        return yf.Ticker(symbol).history(period="4d", interval="15m")

    @staticmethod
    def scan(df: pd.DataFrame) -> Tuple[str, float, float]:
        if len(df) < 30:
            return "INSUFFICIENT DATA", 0.0, 0.0
        
        # Identification des zones de liquidité (Lookback 20 bougies)
        lookback = df.iloc[-25:-5]
        h_liq = lookback['High'].max()
        l_liq = lookback['Low'].min()
        
        curr = df.iloc[-1]
        # Logique de Sweep institutionnel
        bull_sweep = (curr['Low'] < l_liq) and (curr['Close'] > l_liq)
        bear_sweep = (curr['High'] > h_liq) and (curr['Close'] < h_liq)
        
        if bull_sweep:
            return "💎 STRONG BUY (LIQUIDITY SWEEP)", h_liq, l_liq
        elif bear_sweep:
            return "📉 STRONG SELL (LIQUIDITY SWEEP)", h_liq, l_liq
        
        return "WAITING FOR SMC SETUP", h_liq, l_liq

    @staticmethod
    def plot_smc_chart(df: pd.DataFrame, h_liq: float, l_liq: float, session_color: str):
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name="XAU/USD"
        ))
        
        # Zones de liquidité
        fig.add_hline(y=h_liq, line_dash="dash", line_color="#FF4444", annotation_text="LIQ HIGH")
        fig.add_hline(y=l_liq, line_dash="dash", line_color="#44FF44", annotation_text="LIQ LOW")

        fig.update_layout(
            template="plotly_dark", xaxis_rangeslider_visible=False,
            height=600, paper_bgcolor="#000", plot_bgcolor="#000",
            margin=dict(l=0, r=0, t=0, b=0)
        )
        return fig

def send_telegram_alert(signal: str, price: float, session: str):
    """Envoi d'alerte sécurisé avec dédoublonnage."""
    token = SecurityManager.get_credential("TELEGRAM_TOKEN")
    cid = SecurityManager.get_credential("CHAT_ID")
    
    if token and cid:
        msg = f"🏛️ **SNIPER SIGNAL v4.0**\nSession: {session}\nSignal: {signal}\nPrice: {price:.2f}"
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          data={"chat_id": cid, "text": msg, "parse_mode":"Markdown"}, 
                          timeout=10)
            return True
        except Exception:
            return False
    return False

def main():
    # --- UI CUSTOM CSS ---
    st.markdown("<style>.stMetric { background-color: #111; padding: 10px; border-radius: 10px; border: 1px solid #333; }</style>", unsafe_allow_html=True)

    # Initialisation data
    news_engine = NewsEngine()
    df = SMCEngine.get_data()
    if df.empty:
        st.error("Connection error with Market Data API.")
        return

    # Analyse
    news_list = news_engine.fetch_high_impact()
    risk_status = news_engine.is_risky(news_list)
    signal, h_zone, l_zone = SMCEngine.scan(df)
    
    # Header & Time
    tana_now = datetime.now(pytz.timezone('Indian/Antananarivo'))
    st.title("XAU/USD SNIPER PRO 🚀")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("ANTANANARIVO", tana_now.strftime("%H:%M:%S"))
    c2.metric("CURRENT PRICE", f"${df['Close'].iloc[-1]:,.2f}")
    c3.info(f"RISK STATUS: {'🔴 BLOCKED' if risk_status else '🟢 CLEAR'}")

    # Layout Principal
    col_main, col_side = st.columns([3, 1])

    with col_main:
        fig = SMCEngine.plot_smc_chart(df, h_zone, l_zone, "#00CCFF")
        st.plotly_chart(fig, use_container_width=True)

    with col_side:
        st.subheader("Signal Intelligence")
        if "STRONG" in signal:
            st.success(signal)
            # Logique d'envoi unique
            if not st.session_state.get('last_alert') == signal and not risk_status:
                if send_telegram_alert(signal, df['Close'].iloc[-1], "LIVE"):
                    st.session_state.last_alert = signal
                    st.toast("Telegram Alert Dispatched!")
        else:
            st.warning(signal)

    if news_list:
        with st.expander("Economic Calendar"):
            st.table(pd.DataFrame(news_list)[['event', 'date', 'impact']])

if __name__ == "__main__":
    main()
