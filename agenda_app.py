import streamlit as st
import pandas as pd
import datetime
import feedparser
import os.path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Dashboard Pro", layout="wide", page_icon="🏛️")

# --- GOOGLE CALENDAR CONNECTION ---
def get_calendar_service():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    # Το αρχείο token.pickle αποθηκεύει τις εγκρίσεις σου μετά την πρώτη φορά
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                st.error("Λείπει το αρχείο credentials.json! Κατέβασέ το από το Google Cloud Console.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

# --- CSS STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .clock-container {
        background: #1e1e1e; padding: 20px; border-radius: 15px;
        border: 2px solid #ff4b4b; text-align: center; margin-bottom: 20px;
    }
    .time-box { color: #00ff00; font-size: 50px; font-weight: bold; }
    .date-box { color: #00d4ff; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: RADIO & FEEDS CONFIG ---
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
    st.header("📰 Ρυθμίσεις Ειδήσεων")
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

# --- MAIN DASHBOARD ---
now = datetime.datetime.now()
st.markdown(f"""
    <div class="clock-container">
        <div class="time-box">{now.strftime('%H:%M:%S')}</div>
        <div class="date-box">{now.strftime('%A, %d %B %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📝 Προσθήκη στο Google Calendar")
    with st.form("google_calendar_form", clear_on_submit=True):
        title = st.text_input("Τίτλος Ραντεβού")
        location = st.text_input("Τοποθεσία")
        date_val = st.date_input("Ημερομηνία", datetime.date.today())
        time_val = st.time_input("Ώρα", datetime.time(9, 0))
        
        submitted = st.form_submit_button("Αποστολή στο Ημερολόγιο")
        
        if submitted:
            service = get_calendar_service()
            if service:
                start_dt = datetime.datetime.combine(date_val, time_val)
                end_dt = start_dt + datetime.timedelta(hours=1)
                
                event = {
                    'summary': title,
                    'location': location,
                    'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Europe/Athens'},
                    'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Europe/Athens'},
                    'reminders': {'useDefault': True},
                }
                
                try:
                    service.events().insert(calendarId='primary', body=event).execute()
                    st.success(f"✅ Επιτυχία! Το '{title}' προστέθηκε. Θα λάβεις ειδοποίηση στο κινητό.")
                except Exception as e:
                    st.error(f"Σφάλμα κατά την αποθήκευση: {e}")

with col2:
    st.subheader(f"🗞️ {feed_choice}")
    try:
        feed = feedparser.parse(feed_url)
        for post in feed.entries[:10]:
            st.markdown(f"🔹 **[{post.title}]({post.link})**")
            st.caption(post.get('published', ''))
            st.divider()
    except:
        st.error("Αδυναμία φόρτωσης ειδήσεων.")
