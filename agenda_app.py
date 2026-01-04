import streamlit as st
import pandas as pd
import datetime
import feedparser
import json
import os

# --- ΡΥΘΜΙΣΕΙΣ & ΑΠΟΘΗΚΕΥΣΗ ---
DB_FILE = "agenda_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'appointments' not in st.session_state:
    st.session_state.appointments = load_data()

st.set_page_config(page_title="H Έξυπνη Ατζέντα μου", layout="wide")

# --- SIDEBAR: ΡΑΔΙΟΦΩΝΟ (TOP 10) ---
st.sidebar.header("🎵 Ελληνικό Ραδιόφωνο")
radio_stations = {
    "ΣΚΑΪ 100.3": "https://skai.live24.gr/skai1003",
    "Ρυθμός 94.9": "https://rythmos.live24.gr/rythmos949",
    "Δίεση 101.3": "https://diesi.live24.gr/diesi1013",
    "Red 96.3": "https://red.live24.gr/red963",
    "Love Radio 97.5": "https://loveradio.live24.gr/loveradio1000",
    "Real FM 97.8": "https://realfm.live24.gr/realfm",
    "Μελωδία 99.2": "https://melodia.live24.gr/melodia992",
    "Kiss 92.9": "https://kissfm.live24.gr/kiss929",
    "En Lefko 87.7": "https://enlefko.live24.gr/enlefko877",
    "Hit 88.9": "https://hit889.live24.gr/hit889"
}
radio_choice = st.sidebar.selectbox("Επίλεξε σταθμό:", list(radio_stations.keys()))
st.sidebar.audio(radio_stations[radio_choice])

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("📅 Dashboard Ατζέντας")
    
    # Φόρμα Καταχώρησης
    with st.expander("➕ Νέο Ραντεβού / Ειδοποίηση στο Κινητό", expanded=True):
        with st.form("appt_form", clear_on_submit=True):
            title = st.text_input("Τίτλος Ραντεβού")
            date = st.date_input("Ημερομηνία", datetime.date.today())
            t_time = st.time_input("Ώρα", datetime.time(12, 0))
            
            st.markdown("---")
            st.subheader("🔔 Ρυθμίσεις Ειδοποίησης")
            reminder_min = st.slider("Πόσα λεπτά πριν να έρθει το Pop-up στο κινητό;", 5, 120, 15)
            notif_type = st.multiselect("Τρόπος ειδοποίησης:", ["Google Calendar (Pop-up)", "SMS", "Email"], default=["Google Calendar (Pop-up)"])
            
            submit = st.form_submit_button("Αποθήκευση & Συγχρονισμός")
            
            if submit:
                new_entry = {
                    "Τίτλος": title, 
                    "Ημερομηνία": str(date), 
                    "Ώρα": t_time.strftime("%H:%M"),
                    "Ειδοποίηση": f"{reminder_min} min πριν",
                    "Status": "Εκκρεμεί συγχρονισμός"
                }
                st.session_state.appointments.append(new_entry)
                save_data(st.session_state.appointments)
                st.success(f"Το ραντεβού '{title}' αποθηκεύτηκε! Έτοιμο για συγχρονισμό με το Google Calendar.")

    # Εμφάνιση Πίνακα
    if st.session_state.appointments:
        st.subheader("Προσεχή Ραντεβού")
        df = pd.DataFrame(st.session_state.appointments)
        st.dataframe(df, use_container_width=True)
        if st.button("Διαγραφή Όλων"):
            save_data([])
            st.rerun()

with col2:
    st.markdown(f"### ⏰ {datetime.datetime.now().strftime('%H:%M')}")
    st.write(f"**{datetime.datetime.now().strftime('%A, %d %B %Y')}**")
    
    st.markdown("---")
    st.markdown("### 📰 Ροή Ειδήσεων (Live)")
    feed_url = "https://www.protothema.gr/rss/general/"
    try:
        feed = feedparser.parse(feed_url)
        news_titles = "  •  ".join([post.title for post in feed.entries[:10]])
    except:
        news_titles = "Αδυναμία φόρτωσης ειδήσεων..."
        
    st.markdown(f"""
        <div style="background-color: #0e1117; padding: 15px; border: 1px solid #31333f; border-radius: 10px;">
            <marquee style="color: #ff4b4b; font-family: 'Courier New'; font-size: 18px; font-weight: bold;">
                {news_titles}
            </marquee>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Σημείωση:** Για να έρθει το SMS και το Pop-up στο κινητό, πρέπει να ολοκληρώσουμε το Βήμα 2 (Google Cloud).")
