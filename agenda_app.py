import streamlit as st
import datetime
import time
import feedparser
import pandas as pd

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Agenda Pro", layout="wide")

# Αρχικοποίηση session state για τα ραντεβού
if 'appointments' not in st.session_state:
    st.session_state.appointments = []

# --- SIDEBAR: ΞΥΠΝΗΤΗΡΙ & ΜΟΥΣΙΚΗ ---
st.sidebar.header("⏰ Ξυπνητήρι & Μουσική")

alarm_type = st.sidebar.radio("Τύπος Ειδοποίησης:", ["Συγκεκριμένη Ώρα", "Αντίστροφη Μέτρηση (Timer)"])

if alarm_type == "Συγκεκριμένη Ώρα":
    alarm_time = st.sidebar.time_input("Ρύθμιση ώρας ξυπνητηριού:", datetime.time(7, 0))
else:
    minutes = st.sidebar.number_input("Λεπτά για αντίστροφη μέτρηση:", min_value=1, max_value=120, value=15)
    if st.sidebar.button("Έναρξη Timer"):
        st.sidebar.write(f"Ο Timer ξεκίνησε για {minutes} λεπτά!")
        # Εδώ μπορεί να προστεθεί logic για πραγματικό countdown

st.sidebar.markdown("---")
st.sidebar.subheader("🎵 Επιλογή Ήχου")
media_source = st.sidebar.selectbox("Πηγή Ήχου:", ["YouTube Link", "Ραδιοφωνικός Σταθμός"])

if media_source == "YouTube Link":
    yt_url = st.sidebar.text_input("Επικόλλησε το YouTube Link:", "https://www.youtube.com/watch?v=SSuCyZlksrI")
    if yt_url:
        st.sidebar.video(yt_url)
else:
    radio_stations = {
        "ΣΚΑΪ 100.3": "https://skai.live24.gr/skai1003",
        "Love Radio 97.5": "https://loveradio.live24.gr/loveradio1000",
        "Red 96.3": "https://red.live24.gr/red963"
    }
    choice = st.sidebar.selectbox("Επίλεξε σταθμό:", list(radio_stations.keys()))
    st.sidebar.audio(radio_stations[choice])

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ: ΡΑΝΤΕΒΟΥ ΜΕ ΤΟΠΟΘΕΣΙΑ ---
st.title("📅 Διαχείριση Ραντεβού")

col1, col2 = st.columns([2, 1])

with col1:
    with st.expander("➕ Καταχώρηση Ραντεβού με Τοποθεσία", expanded=True):
        with st.form("appointment_form", clear_on_submit=True):
            title = st.text_input("Τίτλος Ραντεβού")
            loc = st.text_input("Τοποθεσία (π.χ. Δήμος Πέλλας ή Διεύθυνση)")
            date = st.date_input("Ημερομηνία")
            t_time = st.time_input("Ώρα")
            
            submit = st.form_submit_button("Αποθήκευση")
            
            if submit:
                # Δημιουργία Google Maps Link
                maps_link = f"https://www.google.com/maps/search/?api=1&query={loc.replace(' ', '+')}"
                st.session_state.appointments.append({
                    "Ραντεβού": title,
                    "Τοποθεσία": loc,
                    "Ημερομηνία": str(date),
                    "Ώρα": t_time.strftime("%H:%M"),
                    "Χάρτης": maps_link
                })
                st.success("Το ραντεβού αποθηκεύτηκε!")

    # Εμφάνιση Πίνακα Ραντεβού
    if st.session_state.appointments:
        st.subheader("Η Λίστα μου")
        df = pd.DataFrame(st.session_state.appointments)
        
        # Μετατροπή του Link σε clickable μορφή για το Streamlit
        st.write("Κάντε κλικ στο link της τοποθεσίας για οδηγίες στο Google Maps:")
        for index, row in df.iterrows():
            st.markdown(f"📍 **{row['Ραντεβού']}** | {row['Ημερομηνία']} {row['Ώρα']} | [Οδηγίες Χάρτη]({row['Χάρτης']})")
    else:
        st.info("Δεν υπάρχουν προγραμματισμένα ραντεβού.")

with col2:
    st.subheader("📰 Ειδήσεις")
    feed = feedparser.parse("https://www.protothema.gr/rss/general/")
    titles = "  •  ".join([post.title for post in feed.entries[:8]])
    st.markdown(f"<div style='background:black;padding:10px'><marquee style='color:red'>{titles}</marquee></div>", unsafe_allow_html=True)
