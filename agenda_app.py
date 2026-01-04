import streamlit as st
import pandas as pd
import datetime
import feedparser
import os.path
import pickle
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Dashboard Pro", layout="wide", page_icon="🏛️")

# --- ΣΥΝΔΕΣΗ ΜΕ GOOGLE CALENDAR API ---
def get_calendar_service():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    # Αναζήτηση για το αρχείο άδειας
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            else:
                return None
    return build('calendar', 'v3', credentials=creds)

# --- CSS STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .clock-container {
        background: #1e1e1e; padding: 20px; border-radius: 15px;
        border: 2px solid #ff4b4b; text-align: center; margin-bottom: 20px;
    }
    .time-box { color: #00ff00; font-size: 50px; font-weight: bold; font-family: 'Courier New', monospace; }
    .date-box { color: #00d4ff; font-size: 20px; font-weight: bold; }
    .alarm-msg { color: #ff4b4b; font-weight: bold; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# Αρχικοποίηση Alarms στη μνήμη
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
    st.header("📰 News Feed")
    categories = {
        "Πολιτική (Διεθνής)": {
            "POLITICO Europe": "https://www.politico.eu/feed",
            "The Nation": "https://www.thenation.com/subject/politics/feed",
            "The Hill": "https://thehill.com/homenews/feed"
        },
        "Ελληνικά Media": {
            "Η Καθημερινή": "https://www.kathimerini.gr/rss",
            "Ναυτεμπορική": "https://www.naftemporiki.gr/feed/",
            "ΕΡΤ News": "https://www.ertnews.gr/feed/"
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
    alarm_time = st.time_input("Ορισμός ώρας:", datetime.time(8, 0))
    if st.button("🔔 Προσθήκη Ξυπνητηριού"):
        st.session_state.alarms.append(alarm_time.strftime("%H:%M"))
        st.success(f"Ξυπνητήρι για τις {alarm_time.strftime('%H:%M')}!")

    if st.session_state.alarms:
        st.write("Ενεργά:")
        for a in st.session_state.alarms:
            st.code(f"⏰ {a}")
        if st.button("🗑️ Καθαρισμός όλων"):
            st.session_state.alarms = []
            st.rerun()

# --- ΚΥΡΙΩΣ DASHBOARD ---
now = datetime.datetime.now()
current_time = now.strftime("%H:%M")

# Έλεγχος αν χτυπάει ξυπνητήρι
alarm_alert = ""
if current_time in st.session_state.alarms:
    alarm_alert = f'<div class="alarm-msg">🔔 ΤΩΡΑ: ΞΥΠΝΗΤΗΡΙ {current_time}! 🔔</div>'

st.markdown(f"""
    <div class="clock-container">
        <div class="time-box">{now.strftime('%H:%M:%S')}</div>
        <div class="date-box">{now.strftime('%A, %d %B %Y')}</div>
        {alarm_alert}
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("🗓️ Προσθήκη στο Google Calendar")
    st.info("Τα ραντεβού εδώ θα συγχρονιστούν με το κινητό σου για αυτόματη ειδοποίηση.")
    
    with st.form("cal_form", clear_on_submit=True):
        t = st.text_input("Τίτλος")
        l = st.text_input("Τοποθεσία")
        d_cal = st.date_input("Ημερομηνία", datetime.date.today())
        tm_cal = st.time_input("Ώρα", datetime.time(10, 0))
        
        if st.form_submit_button("✅ Αποθήκευση & Ειδοποίηση στο Κινητό"):
            service = get_calendar_service()
            if service:
                start_dt = datetime.datetime.combine(d_cal, tm_cal)
                end_dt = start_dt + datetime.timedelta(hours=1)
                event = {
                    'summary': t, 'location': l,
                    'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Europe/Athens'},
                    'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Europe/Athens'},
                    'reminders': {'useDefault': True}
                }
                service.events().insert(calendarId='primary', body=event).execute()
                st.success(f"Το '{t}' στάλθηκε στο Google Calendar!")
            else:
                st.error("Λείπει το credentials.json ή η άδεια (token).")

with col2:
    st.subheader(f"🗞️ {feed_choice}")
    try:
        feed = feedparser.parse(feed_url)
        for post in feed.entries[:8]:
            st.markdown(f"🔗 **[{post.title}]({post.link})**")
            st.caption(post.get('published', ''))
            st.divider()
    except:
        st.error("Σφάλμα στη φόρτωση ειδήσεων.")

# Auto-refresh για το ρολόι και το ξυπνητήρι (κάθε 30 δευτερόλεπτα)
time.sleep(30)
st.rerun()
