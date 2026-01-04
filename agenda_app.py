import streamlit as st
import pandas as pd
import datetime
import feedparser
import os.path
import pickle
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Dashboard Pro", layout="wide", page_icon="🏛️")

# --- ΣΥΝΔΕΣΗ ΜΕ GOOGLE CALENDAR ---
def get_calendar_service():
    creds = None
    # Αναζήτηση για το αρχείο token.pickle
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Αν δεν υπάρχουν έγκυρα διαπιστευτήρια, προσπάθεια ανανέωσης
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        except:
            creds = None
            
    if not creds or not creds.valid:
        return None # Επιστρέφει None αν χρειάζεται νέα έγκριση από το Sidebar
        
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

# Αρχικοποίηση session states
if 'alarms' not in st.session_state: st.session_state.alarms = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔐 Σύνδεση Google")
    if not os.path.exists('token.pickle'):
        if os.path.exists('credentials.json'):
            flow = Flow.from_client_secrets_file(
                'credentials.json',
                scopes=['https://www.googleapis.com/auth/calendar'],
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.warning("Απαιτείται σύνδεση!")
            st.markdown(f"[🔗 Πάτα εδώ για Έγκριση]({auth_url})")
            auth_code = st.sidebar.text_input("Επικόλλησε τον κωδικό εδώ:")
            if auth_code:
                flow.fetch_token(code=auth_code)
                with open('token.pickle', 'wb') as f:
                    pickle.dump(flow.credentials, f)
                st.success("✅ Συνδέθηκες! Κάνε Refresh.")
                st.rerun()
        else:
            st.error("Λείπει το credentials.json!")

    st.markdown("---")
    st.header("📻 Ραδιόφωνο")
    radio_stations = {
        "ΕΡΤ (Πρώτο)": "https://ertradio.secure.footprint.net/atunw/radio/ert_proto/playlist.m3u8",
        "ERT News 105.8": "https://ertradio.secure.footprint.net/atunw/radio/ert_news/playlist.m3u8",
        "REAL NEWS 97.8": "https://realfm.live24.gr/realfm",
        "RADIO THESSALONIKI": "https://rthes.live24.gr/rthes",
        "LOVE RADIO 97.5": "https://loveradio.live24.gr/loveradio1000",
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
            "The Nation": "https://www.thenation.com/subject/politics/feed",
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
    st.header("⏰ Τοπικό Ξυπνητήρι")
    al_time = st.time_input("Ώρα αφύπνισης:", datetime.time(8, 0))
    if st.button("🔔 Ορισμός"):
        st.session_state.alarms.append(al_time.strftime("%H:%M"))
        st.success(f"Ξυπνητήρι στις {al_time.strftime('%H:%M')}")
    if st.session_state.alarms:
        for i, a in enumerate(st.session_state.alarms):
            col_a, col_b = st.columns([0.8, 0.2])
            col_a.code(f"⏰ {a}")
            if col_b.button("✖️", key=f"del_al_{i}"):
                st.session_state.alarms.pop(i)
                st.rerun()

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ ---
now = datetime.datetime.now()
curr_time_str = now.strftime("%H:%M")

# Έλεγχος Alarms
alarm_html = ""
if curr_time_str in st.session_state.alarms:
    alarm_html = f'<div class="alarm-msg">🔔 ΞΥΠΝΗΤΗΡΙ: {curr_time_str}! 🔔</div>'

st.markdown(f"""
    <div class="clock-container">
        <div class="time-box">{now.strftime('%H:%M:%S')}</div>
        <div class="date-box">{now.strftime('%A, %d %B %Y')}</div>
        {alarm_html}
    </div>
    """, unsafe_allow_html=True)

c1, c2 = st.columns([1.5, 1])

with c1:
    st.subheader("🗓️ Προσθήκη στο Google Calendar")
    with st.form("google_cal_form", clear_on_submit=True):
        title = st.text_input("Τίτλος Ραντεβού")
        loc = st.text_input("Τοποθεσία")
        d_val = st.date_input("Ημερομηνία", datetime.date.today())
        t_val = st.time_input("Ώρα", datetime.time(9, 0))
        if st.form_submit_button("✅ Αποστολή στο Ημερολόγιο"):
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
                st.success(f"Επιτυχία! Το '{title}' στάλθηκε στο κινητό σου.")
            else:
                st.error("Πρέπει πρώτα να κάνεις τη σύνδεση στο Sidebar!")

with c2:
    st.subheader(f"🗞️ {feed_choice}")
    try:
        feed = feedparser.parse(feed_url)
        # News Ticker
        titles = "  •  ".join([p.title for p in feed.entries[:10]])
        st.markdown(f'<div style="background:#000;padding:10px;border:1px solid #00d4ff;"><marquee style="color:#00ff00;">{titles}</marquee></div>', unsafe_allow_html=True)
        # List
        for post in feed.entries[:10]:
            st.markdown(f"🔹 **[{post.title}]({post.link})**")
            st.divider()
    except:
        st.error("Σφάλμα ειδήσεων.")

# Auto-refresh για το ρολόι
time.sleep(10)
st.rerun()
