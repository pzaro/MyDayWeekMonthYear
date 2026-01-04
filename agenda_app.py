import streamlit as st
import pandas as pd
import datetime
import feedparser
import os.path
import pickle
import time
import base64
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Dashboard Pro", layout="wide", page_icon="🏛️")

# --- ΑΥΤΟΜΑΤΟΠΟΙΗΜΕΝΗ ΣΥΝΔΕΣΗ ΜΕ GOOGLE CALENDAR (ΜΕΣΩ SECRETS) ---
def get_calendar_service():
    creds = None
    if "GOOGLE_TOKEN_BASE64" in st.secrets:
        try:
            token_data = base64.b64decode(st.secrets["GOOGLE_TOKEN_BASE64"])
            creds = pickle.loads(token_data)
        except Exception as e:
            st.sidebar.error(f"Σφάλμα ανάγνωσης Secrets: {e}")
            return None
    
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except:
            creds = None
            
    if not creds or not creds.valid:
        st.sidebar.error("❌ Η σύνδεση Google δεν είναι έγκυρη.")
        return None
        
    return build('calendar', 'v3', credentials=creds)

# --- CSS STYLING (Μικρότερο ρολόι) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .clock-container {
        background: #1e1e1e; padding: 15px; border-radius: 12px;
        border: 1px solid #ff4b4b; text-align: center; margin-bottom: 10px;
    }
    .time-box { color: #00ff00; font-size: 35px; font-weight: bold; font-family: 'Courier New', monospace; }
    .date-box { color: #00d4ff; font-size: 18px; font-weight: bold; }
    .ticker-container {
        background: #000; padding: 8px; border: 1px solid #00d4ff; margin-bottom: 20px;
    }
    .alarm-msg { color: #ff4b4b; font-weight: bold; font-size: 18px; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

if 'alarms' not in st.session_state: st.session_state.alarms = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("📻 Ραδιόφωνο")
    radio_stations = {
        "ΕΡΤ (Πρώτο)": "https://ertradio.secure.footprint.net/atunw/radio/ert_proto/playlist.m3u8",
        "ERT News 105.8": "https://ertradio.secure.footprint.net/atunw/radio/ert_news/playlist.m3u8",
        "REAL NEWS 97.8": "https://realfm.live24.gr/realfm",
        "RADIO THESSALONIKI": "https://rthes.live24.gr/rthes",
        "METROPOLIS 95.5": "https://metropolis.live24.gr/metropolis955"
    }
    selected_r = st.selectbox("Σταθμός:", list(radio_stations.keys()))
    st.audio(radio_stations[selected_r], format="audio/mp3")

    st.markdown("---")
    st.header("📰 News Feed")
    categories = {
        "Πολιτική (Διεθνής)": {
            "POLITICO Europe": "https://www.politico.eu/feed",
            "RealClearPolitics": "https://www.realclearpolitics.com/index.xml",
            "The Hill": "https://thehill.com/homenews/feed"
        },
        "Ελληνικά Media": {
            "Η Καθημερινή": "https://www.kathimerini.gr/rss",
            "Ναυτεμπορική": "https://www.naftemporiki.gr/feed/",
            "ΕΡΤ News": "https://www.ertnews.gr/feed/",
            "Newsbeast": "https://www.newsbeast.gr/feed"
        },
        "Οικονομία": {
            "Capital.gr": "https://www.capital.gr/rss",
            "Reuters Business": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
            "Financial Times": "https://www.ft.com/?format=rss"
        }
    }
    cat_choice = st.selectbox("Κατηγορία:", list(categories.keys()))
    feed_choice = st.selectbox("Πηγή:", list(categories[cat_choice].keys()))
    feed_url = categories[cat_choice][feed_choice]

    st.markdown("---")
    st.header("⏰ Ξυπνητήρι")
    al_time = st.time_input("Ώρα αφύπνισης:", datetime.time(8, 0))
    if st.button("🔔 Ορισμός"):
        st.session_state.alarms.append(al_time.strftime("%H:%M"))
    if st.session_state.alarms:
        for i, a in enumerate(st.session_state.alarms):
            col_a, col_b = st.columns([0.7, 0.3])
            col_a.code(f"⏰ {a}")
            if col_b.button("✖️", key=f"del_al_{i}"):
                st.session_state.alarms.pop(i)
                st.rerun()

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ ---

# 1. Ρολόι και Ημερομηνία (Μικρότερο)
now = datetime.datetime.now()
curr_time_str = now.strftime("%H:%M")
alarm_html = f'<div class="alarm-msg">🔔 ΞΥΠΝΗΤΗΡΙ: {curr_time_str}! 🔔</div>' if curr_time_str in st.session_state.alarms else ""

st.markdown(f"""
    <div class="clock-container">
        <div class="time-box">{now.strftime('%H:%M:%S')}</div>
        <div class="date-box">{now.strftime('%A, %d %B %Y')}</div>
        {alarm_html}
    </div>
    """, unsafe_allow_html=True)

# 2. News Ticker (Μεταφέρθηκε ψηλά)
try:
    feed = feedparser.parse(feed_url)
    titles = "  •  ".join([p.title for p in feed.entries[:12]])
    st.markdown(f"""
        <div class="ticker-container">
            <marquee style="color:#00ff00; font-weight:bold;">{titles}</marquee>
        </div>
        """, unsafe_allow_html=True)
except:
    st.error("Σφάλμα φόρτωσης Ticker.")

# 3. Περιεχόμενο (Ημερολόγιο και Λίστα Ειδήσεων)
c1, c2 = st.columns([1.5, 1])

with c1:
    st.subheader("🗓️ Google Calendar")
    with st.form("google_cal_form", clear_on_submit=True):
        title = st.text_input("Τίτλος Ραντεβού")
        loc = st.text_input("Τοποθεσία")
        d_val = st.date_input("Ημερομηνία", datetime.date.today())
        t_val = st.time_input("Ώρα", datetime.time(9, 0))
        if st.form_submit_button("✅ Αποθήκευση"):
            service = get_calendar_service()
            if service:
                start = datetime.datetime.combine(d_val, t_val)
                end = start + datetime.timedelta(hours=1)
                event = {
                    'summary': title, 'location': loc,
                    'start': {'dateTime': start.isoformat(), 'timeZone': 'Europe/Athens'},
                    'end': {'dateTime': end.isoformat(), 'timeZone': 'Europe/Athens'},
                    'reminders': {'useDefault': True},
                }
                service.events().insert(calendarId='primary', body=event).execute()
                st.success(f"Το '{title}' προστέθηκε!")
            else:
                st.error("Σφάλμα σύνδεσης.")

with c2:
    st.subheader(f"🗞️ {feed_choice}")
    if 'feed' in locals():
        for post in feed.entries[:8]:
            st.markdown(f"🔹 **[{post.title}]({post.link})**")
            st.divider()

# Auto-refresh
time.sleep(10)
st.rerun()
