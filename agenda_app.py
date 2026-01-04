import streamlit as st
import pandas as pd
import datetime
import time
import feedparser

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="H Έξυπνη Ατζέντα μου", layout="wide", page_icon="📅")

# Αρχικοποίηση δεδομένων (Session State)
if 'appointments' not in st.session_state:
    st.session_state.appointments = []
if 'diet_logs' not in st.session_state:
    st.session_state.diet_logs = []

# --- SIDEBAR: ΞΥΠΝΗΤΗΡΙ & ΜΟΥΣΙΚΗ ---
st.sidebar.header("⏰ Ξυπνητήρι & Ήχος")

alarm_mode = st.sidebar.radio("Λειτουργία:", ["Συγκεκριμένη Ώρα", "Αντίστροφη Μέτρηση"])

if alarm_mode == "Συγκεκριμένη Ώρα":
    alarm_time = st.sidebar.time_input("Ρύθμιση ώρας:", datetime.time(8, 0))
    if st.sidebar.button("Ενεργοποίηση Ξυπνητηριού"):
        st.sidebar.success(f"Το ξυπνητήρι ορίστηκε για τις {alarm_time.strftime('%H:%M')}")
else:
    timer_mins = st.sidebar.number_input("Λεπτά:", min_value=1, max_value=300, value=15)
    if st.sidebar.button("Έναρξη Αντίστροφης Μέτρησης"):
        st.sidebar.warning(f"Ειδοποίηση σε {timer_mins} λεπτά!")

st.sidebar.markdown("---")
st.sidebar.subheader("🎵 Πηγή Ήχου")
media_type = st.sidebar.selectbox("Είδος:", ["YouTube Link", "Ραδιοφωνικός Σταθμός"])

if media_type == "YouTube Link":
    yt_url = st.sidebar.text_input("YouTube URL:", "https://www.youtube.com/watch?v=SSuCyZlksrI")
    st.sidebar.video(yt_url)
else:
    radio_stations = {
        "ΣΚΑΪ 100.3": "https://skai.live24.gr/skai1003",
        "Ρυθμός 94.9": "https://rythmos.live24.gr/rythmos949",
        "Love Radio 97.5": "https://loveradio.live24.gr/loveradio1000",
        "Red 96.3": "https://red.live24.gr/red963",
        "Μελωδία 99.2": "https://melodia.live24.gr/melodia992",
        "En Lefko 87.7": "https://enlefko.live24.gr/enlefko877"
    }
    r_choice = st.sidebar.selectbox("Επίλεξε σταθμό:", list(radio_stations.keys()))
    st.sidebar.audio(radio_stations[r_choice])

# --- SIDEBAR: ΕΠΙΛΟΓΗ ΠΗΓΗΣ ΕΙΔΗΣΕΩΝ ---
st.sidebar.markdown("---")
st.sidebar.header("📰 Πρακτορεία & Site")
news_sources = {
    "ΕΡΤ News (Ελλάδα)": "https://www.ertnews.gr/feed/",
    "Ναυτεμπορική (Οικονομία)": "https://www.naftemporiki.gr/feed/",
    "Capital.gr (Επιχειρήσεις)": "https://www.capital.gr/rss",
    "Reuters (World News)": "https://www.reutersagency.com/feed/?best-topics=world-news&post_type=best",
    "BBC News (International)": "http://feeds.bbci.co.uk/news/rss.xml",
    "Newsbomb (Επικαιρότητα)": "https://www.newsbomb.gr/ellada?format=feed&type=rss"
}
selected_source = st.sidebar.selectbox("Επίλεξε Ροή:", list(news_sources.keys()))

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("📅 Dashboard Ατζέντας")
    
    # Φόρμα Ραντεβού
    with st.expander("➕ Καταχώρηση Νέου Ραντεβού", expanded=True):
        with st.form("appt_form", clear_on_submit=True):
            t = st.text_input("Τίτλος Ραντεβού")
            l = st.text_input("Τοποθεσία (π.χ. Γιαννιτσά ή Οδός)")
            d = st.date_input("Ημερομηνία")
            tm = st.time_input("Ώρα")
            
            if st.form_submit_button("Αποθήκευση"):
                # Δημιουργία Google Maps Link
                maps_url = f"https://www.google.com/maps/search/?api=1&query={l.replace(' ', '+')}"
                st.session_state.appointments.append({
                    "Τίτλος": t, 
                    "Τοποθεσία": l, 
                    "Ημερομηνία": str(d), 
                    "Ώρα": tm.strftime("%H:%M"), 
                    "Χάρτης": maps_url
                })
                st.success("Το ραντεβού αποθηκεύτηκε!")

    # Εμφάνιση Ραντεβού
    if st.session_state.appointments:
        st.subheader("Τα Ραντεβού μου")
        for appt in st.session_state.appointments:
            st.markdown(f"🔹 **{appt['Τίτλος']}** | 🕒 {appt['Ώρα']} | 📍 [{appt['Τοποθεσία']}]({appt['Χάρτης']})")
    else:
        st.info("Δεν υπάρχουν ραντεβού.")

    # Ενότητα Δίαιτας & Κόστους (Σύμφωνα με τις οδηγίες σου)
    st.markdown("---")
    st.subheader("🥗 Δίαιτα & Έξοδα Ημέρας")
    with st.form("diet_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            meal = st.text_input("Γεύμα / Τρόφιμο")
        with f_col2:
            price = st.number_input("Κόστος (€)", min_value=0.0, step=0.1)
        
        if st.form_submit_button("Καταγραφή"):
            st.session_state.diet_logs.append({"Γεύμα": meal, "Κόστος": price, "Ώρα": datetime.datetime.now().strftime("%H:%M")})
    
    if st.session_state.diet_logs:
        diet_df = pd.DataFrame(st.session_state.diet_logs)
        st.table(diet_df)
        total_cost = diet_df["Κόστος"].sum()
        st.metric("Συνολικό Κόστος", f"{total_cost:.2f} €")

with col2:
    # Ειδήσεις Ticker
    st.subheader(f"🗞️ {selected_source}")
    try:
        feed = feedparser.parse(news_sources[selected_source])
        if feed.entries:
            titles = "  •  ".join([post.title for post in feed.entries[:12]])
            st.markdown(f"""
                <div style="background-color: #0e1117; padding: 15px; border: 1px solid #ff4b4b; border-radius: 10px;">
                    <marquee style="color: #00ff00; font-family: 'Courier New'; font-size: 18px; font-weight: bold;">
                        {titles}
                    </marquee>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            for post in feed.entries[:6]:
                st.markdown(f"🔗 [{post.title}]({post.link})")
        else:
            st.warning("Η ροή είναι προσωρινά κενή.")
    except Exception as e:
        st.error("Σφάλμα σύνδεσης με τις ειδήσεις.")

    # Ρολόι
    st.markdown("---")
    st.markdown(f"### ⌚ {datetime.datetime.now().strftime('%H:%M:%S')}")
    st.write(datetime.datetime.now().strftime("%A, %d %B %Y"))
