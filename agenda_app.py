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

# --- ΣΥΝΔΕΣΗ ΜΕ GOOGLE CALENDAR (ΜΟΝΙΜΗ ΜΕΣΩ SECRETS) ---
def get_calendar_service():
    creds = None
    # Διάβασμα της άδειας απευθείας από τα Secrets του Streamlit
    if "GOOGLE_TOKEN_BASE64" in st.secrets:
        try:
            token_data = base64.b64decode(st.secrets["GOOGLE_TOKEN_BASE64"])
            creds = pickle.loads(token_data)
        except Exception as e:
            st.sidebar.error("Πρόβλημα με την ανάγνωση του Token από τα Secrets.")
            return None
    
    # Αυτόματη ανανέωση αν λήξει η συνεδρία
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except:
            creds = None
            
    if not creds or not creds.valid:
        st.sidebar.warning("⚠️ Η σύνδεση Google δεν βρέθηκε ή έληξε.")
        return None
        
    return build('calendar', 'v3', credentials=creds)

# --- CSS STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .clock-container {
        background: #1e1e1e; padding: 25px; border-radius: 15px;
        border: 2px solid #ff4b4b; text-align: center; margin-bottom: 25px;
    }
    .time-box { color: #00ff00; font-size: 55px; font-weight: bold; font-family: 'Courier New', monospace; }
    .date-box { color: #00d4ff; font-size: 22px; font-weight: bold; }
    .alarm-msg { color: #ff4b4b; font-weight: bold; font-size: 20px; animation: blinker 1s linear infinite; margin-top:10px; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

if 'alarms' not in st.session_state:
    st.session_state.alarms = []

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
    st.header("📰 Ειδήσεις")
    categories = {
        "Ελληνικά Media": {
            "Η Καθημερινή": "https://www.kathimerini.gr/rss",
            "ΕΡΤ News": "https://www.ertnews.gr/feed/",
            "Ναυτεμπορική": "https://www.naftemporiki.gr/feed/"
        },
        "Οικονομία": {
            "Capital.gr": "https://www.capital.gr/rss",
            "Reuters Business": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best"
        }
    }
    cat_choice = st.selectbox("Κατηγορία:", list(categories.keys()))
    feed_choice = st.selectbox("Πηγή:", list(categories[cat_choice].keys()))
    feed_url = categories[cat_choice][feed_choice]

    st.markdown("---")
    st.header("⏰ Τοπικό Ξυπνητήρι")
    al_time = st.time_input("Ώρα:", datetime.time(8, 0))
    if st.button("🔔 Ορισμός"):
        st.session_state.alarms.append(al_time.strftime("%H:%M"))
    if st.session_state.alarms:
        for i, a in enumerate(st.session_state.alarms):
            c_a, c_b = st.columns([0.7, 0.3])
            c_a.code(f"⏰ {a}")
            if c_b.button("✖️", key=f"del_{i}"):
                st.session_state.alarms.pop(i)
                st.rerun()

# --- DASHBOARD ---
now = datetime.datetime.now()
curr_time_str = now.strftime("%H:%M")

# Έλεγχος Alarms
alarm_alert = f'<div class="alarm-msg">🔔 ΞΥΠΝΗΤΗΡΙ: {curr_time_str}! 🔔</div>' if curr_time_str in st.session_state.alarms else ""

st.markdown(f"""
    <div class="clock-container">
        <div class="time-box">{now.strftime('%H:%M:%S')}</div>
        <div class="date-box">{now.strftime('%A, %d %B %Y')}</div>
        {alarm_alert}
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("🗓️ Google Calendar")
    with st.form("cal_form", clear_on_submit=True):
        title = st.text_input("Τίτλος Ραντεβού")
        location = st.text_input("Τοποθεσία")
        d_val = st.date_input("Ημερομηνία", datetime.date.today())
        t_val = st.time_input("Ώρα", datetime.time(9, 0))
        
        if st.form_submit_button("✅ Αποθήκευση στο Ημερολόγιο"):
            service = get_calendar_service()
            if service:
                start_dt = datetime.datetime.combine(d_val, t_val).isoformat()
                event = {
                    'summary': title, 'location': location,
                    'start': {'dateTime': start_dt, 'timeZone': 'Europe/Athens'},
                    'end': {'dateTime': start_dt, 'timeZone': 'Europe/Athens'},
                    'reminders': {'useDefault': True},
                }
                service.events().insert(calendarId='primary', body=event).execute()
                st.success(f"Επιτυχία! Το '{title}' στάλθηκε στο κινητό.")
            else:
                st.error("Η σύνδεση Google δεν είναι έτοιμη.")

with col2:
    st.subheader(f"🗞️ {feed_choice}")
    try:
        feed = feedparser.parse(feed_url)
        for post in feed.entries[:10]:
            st.markdown(f"🔹 **[{post.title}]({post.link})**")
            st.divider()
    except:
        st.error("Σφάλμα ειδήσεων.")

# Auto-refresh για το ρολόι
time.sleep(10)
st.rerun()
