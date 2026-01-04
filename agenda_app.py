import streamlit as st
import pandas as pd
import datetime
import feedparser
import os.path
import pickle
import time
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Dashboard Pro", layout="wide", page_icon="🏛️")

# --- ΣΥΝΔΕΣΗ ΜΕ GOOGLE CALENDAR ---
def get_calendar_service():
    creds = None
    # 1. Προσπάθεια ανάγνωσης από τα Secrets
    if "GOOGLE_TOKEN_BASE64" in st.secrets:
        try:
            token_data = base64.b64decode(st.secrets["GOOGLE_TOKEN_BASE64"])
            creds = pickle.loads(token_data)
        except:
            pass
    
    # 2. Αν δεν υπάρχει στα Secrets, έλεγχος για το αρχείο token.pickle
    if not creds and os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Ανανέωση αν έχει λήξει
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except:
            creds = None
            
    if not creds or not creds.valid:
        return None
        
    return build('calendar', 'v3', credentials=creds)

# --- CSS STYLING ---
st.markdown("""
    <style>
    .clock-container {
        background: #1e1e1e; padding: 25px; border-radius: 15px;
        border: 2px solid #ff4b4b; text-align: center; margin-bottom: 25px;
    }
    .time-box { color: #00ff00; font-size: 55px; font-weight: bold; font-family: 'Courier New', monospace; }
    .date-box { color: #00d4ff; font-size: 22px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'alarms' not in st.session_state: st.session_state.alarms = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("📻 Ραδιόφωνο")
    radio_stations = {
        "ΕΡΤ (Πρώτο)": "https://ertradio.secure.footprint.net/atunw/radio/ert_proto/playlist.m3u8",
        "ERT News 105.8": "https://ertradio.secure.footprint.net/atunw/radio/ert_news/playlist.m3u8",
        "REAL NEWS 97.8": "https://realfm.live24.gr/realfm"
    }
    selected_r = st.selectbox("Σταθμός:", list(radio_stations.keys()))
    st.audio(radio_stations[selected_r], format="audio/mp3")

    st.markdown("---")
    st.header("📰 News Feed")
    categories = {
        "Ελληνικά Media": {
            "Η Καθημερινή": "https://www.kathimerini.gr/rss",
            "ΕΡΤ News": "https://www.ertnews.gr/feed/"
        }
    }
    cat_choice = st.selectbox("Κατηγορία:", list(categories.keys()))
    feed_choice = st.selectbox("Πηγή:", list(categories[cat_choice].keys()))
    feed_url = categories[cat_choice][feed_choice]

    st.markdown("---")
    st.header("⏰ Ξυπνητήρι")
    al_time = st.time_input("Ώρα:", datetime.time(8, 0))
    if st.button("🔔 Ορισμός"):
        st.session_state.alarms.append(al_time.strftime("%H:%M"))

# --- DASHBOARD ---
now = datetime.datetime.now()
st.markdown(f"""
    <div class="clock-container">
        <div class="time-box">{now.strftime('%H:%M:%S')}</div>
        <div class="date-box">{now.strftime('%A, %d %B %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("🗓️ Google Calendar")
    with st.form("cal_form", clear_on_submit=True):
        title = st.text_input("Τίτλος")
        d_val = st.date_input("Ημερομηνία", datetime.date.today())
        t_val = st.time_input("Ώρα", datetime.time(10, 0))
        if st.form_submit_button("✅ Αποθήκευση"):
            service = get_calendar_service()
            if service:
                start = datetime.datetime.combine(d_val, t_val).isoformat()
                event = {'summary': title, 'start': {'dateTime': start, 'timeZone': 'Europe/Athens'}, 'end': {'dateTime': start, 'timeZone': 'Europe/Athens'}}
                service.events().insert(calendarId='primary', body=event).execute()
                st.success("Έγινε!")
            else:
                st.error("Δεν βρέθηκε σύνδεση.")

with col2:
    st.subheader(f"🗞️ {feed_choice}")
    try:
        feed = feedparser.parse(feed_url)
        for post in feed.entries[:5]:
            st.markdown(f"🔹 **[{post.title}]({post.link})**")
            st.divider()
    except: st.error("Σφάλμα ειδήσεων.")

# --- ΕΙΔΙΚΟΣ ΕΛΕΓΧΟΣ ΓΙΑ ΤΟ TOKEN SECRETS ---
st.write("---")
st.subheader("🛠️ Εργαλείο Σύνδεσης (Secrets)")

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as f:
        st.success("✅ Το αρχείο βρέθηκε!")
        st.write("### ⬇️ ΑΝΤΙΓΡΑΨΕ ΤΟΝ ΠΑΡΑΚΑΤΩ ΚΩΔΙΚΟ ΓΙΑ ΤΑ SECRETS:")
        st.code(base64.b64encode(f.read()).decode())
else:
    st.error("❌ Το αρχείο 'token.pickle' ΔΕΝ υπάρχει.")
    if os.path.exists('credentials.json'):
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/calendar'],
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(f"**1. [🔗 Πάτα εδώ για έγκριση στη Google]({auth_url})**")
        new_code = st.text_input("2. Επικόλλησε τον κωδικό που θα σου δώσει η Google:")
        if new_code:
            flow.fetch_token(code=new_code)
            with open('token.pickle', 'wb') as f:
                pickle.dump(flow.credentials, f)
            st.success("✅ Το token δημιουργήθηκε! Κάνε ανανέωση τη σελίδα.")
    else:
        st.error("Λείπει το credentials.json από το GitHub!")

# Ανανέωση κάθε 15 δευτερόλεπτα
time.sleep(15)
st.rerun()
