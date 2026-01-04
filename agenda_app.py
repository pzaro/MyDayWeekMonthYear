import streamlit as st
import datetime
import feedparser
import pandas as pd

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="H Έξυπνη Ατζέντα μου", layout="wide")

# Αρχικοποίηση session state για τα ραντεβού
if 'appointments' not in st.session_state:
    st.session_state.appointments = []

# --- SIDEBAR: ΕΠΙΛΟΓΗ ΕΙΔΗΣΕΩΝ ---
st.sidebar.header("📰 Πηγές Ειδήσεων")
news_sources = {
    "Πρώτο Θέμα (Γενικά)": "https://www.protothema.gr/rss/general/",
    "Καθημερινή (Ελλάδα)": "https://www.kathimerini.gr/rss/",
    "Ναυτεμπορική (Οικονομία)": "https://www.naftemporiki.gr/rss",
    "CNN Greece": "https://www.cnn.gr/rss",
    "ΑΠΕ-ΜΠΕ (Πρακτορείο)": "https://www.amna.gr/rss",
    "Reuters (World)": "http://feeds.reuters.com/reuters/topNews",
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml"
}
selected_news = st.sidebar.selectbox("Επίλεξε Ροή Ειδήσεων:", list(news_sources.keys()))

# --- SIDEBAR: ΞΥΠΝΗΤΗΡΙ & ΜΟΥΣΙΚΗ ---
st.sidebar.markdown("---")
st.sidebar.header("⏰ Ξυπνητήρι / Timer")
alarm_mode = st.sidebar.radio("Λειτουργία:", ["Ώρα", "Αντίστροφη"])

if alarm_mode == "Ώρα":
    a_time = st.sidebar.time_input("Ρύθμιση:", datetime.time(8, 0))
else:
    mins = st.sidebar.number_input("Λεπτά:", 1, 300, 15)

media_type = st.sidebar.selectbox("Ήχος από:", ["YouTube Link", "Ραδιόφωνο"])
if media_type == "YouTube Link":
    yt_url = st.sidebar.text_input("YouTube URL:", "https://www.youtube.com/watch?v=SSuCyZlksrI")
    st.sidebar.video(yt_url)
else:
    radio_stations = {
        "ΣΚΑΪ 100.3": "https://skai.live24.gr/skai1003",
        "Love Radio 97.5": "https://loveradio.live24.gr/loveradio1000",
        "Red 96.3": "https://red.live24.gr/red963"
    }
    r_choice = st.sidebar.selectbox("Σταθμός:", list(radio_stations.keys()))
    st.sidebar.audio(radio_stations[r_choice])

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ: ΡΑΝΤΕΒΟΥ & ΧΑΡΤΕΣ ---
st.title("📅 Dashboard Ατζέντας")

col1, col2 = st.columns([2, 1])

with col1:
    with st.expander("➕ Νέο Ραντεβού", expanded=True):
        with st.form("appt_form", clear_on_submit=True):
            t = st.text_input("Τίτλος")
            l = st.text_input("Τοποθεσία (π.χ. Γιαννιτσά ή Οδός)")
            d = st.date_input("Ημερομηνία")
            tm = st.time_input("Ώρα")
            if st.form_submit_button("Προσθήκη"):
                # Δημιουργία Link για Google Maps
                m_url = f"https://www.google.com/maps/search/?api=1&query={l.replace(' ', '+')}"
                st.session_state.appointments.append({"Τίτλος": t, "Τοποθεσία": l, "Ημερομηνία": str(d), "Ώρα": tm.strftime("%H:%M"), "Link": m_url})
                st.success("Αποθηκεύτηκε!")

    if st.session_state.appointments:
        st.subheader("Τα ραντεβού μου")
        for appt in st.session_state.appointments:
            st.markdown(f"🗓️ **{appt['Τίτλος']}** | 🕒 {appt['Ώρα']} | 📍 [{appt['Τοποθεσία']}]({appt['Link']})")

with col2:
    # ΕΔΩ ΕΜΦΑΝΙΖΕΤΑΙ Η ΡΟΗ ΠΟΥ ΕΠΕΛΕΞΕΣ
    st.subheader(f"🗞️ {selected_news}")
    try:
        feed = feedparser.parse(news_sources[selected_news])
        news_ticker = "  •  ".join([post.title for post in feed.entries[:12]])
        st.markdown(f"""
            <div style="background-color: #1e1e1e; padding: 10px; border-radius: 10px; border: 1px solid red;">
                <marquee style="color: #00ff00; font-family: monospace; font-size: 18px;">
                    {news_ticker}
                </marquee>
            </div>
        """, unsafe_allow_html=True)
        
        # Λίστα ειδήσεων κάτω από το ticker
        for post in feed.entries[:5]:
            st.write(f"- [{post.title}]({post.link})")
    except:
        st.error("Αδυναμία φόρτωσης της ροής.")

# ΦΟΡΜΑ ΓΙΑ ΔΙΑΤΡΟΦΗ/ΚΟΣΤΟΣ (Σύμφωνα με τις οδηγίες σου)
st.markdown("---")
with st.expander("🥗 Καταγραφή Δίαιτας & Κόστους"):
    c1, c2 = st.columns(2)
    with c1:
        meal = st.text_input("Γεύμα")
        cost = st.number_input("Κόστος (€)", min_value=0.0)
    with c2:
        st.write("Σύνολο ημέρας: ...")
