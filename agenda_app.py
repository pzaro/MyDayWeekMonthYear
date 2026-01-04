import streamlit as st
import pandas as pd
import datetime
import feedparser

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Dashboard Pro", layout="wide", page_icon="⚡")

# Custom CSS για το design
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .clock-container {
        background: #1e1e1e;
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #ff4b4b;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.2);
    }
    .time-box { color: #00ff00; font-size: 60px; font-weight: bold; text-shadow: 0 0 15px #00ff00; line-height: 1; }
    .date-box { color: #00d4ff; font-size: 25px; font-weight: bold; margin-top: 15px; border-top: 1px solid #444; padding-top: 10px; }
    .repeat-tag { background-color: #3d3d3d; color: #ffbd45; padding: 2px 8px; border-radius: 5px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# Αρχικοποίηση session states για αποθήκευση δεδομένων κατά τη διάρκεια της συνεδρίας
if 'appointments' not in st.session_state: st.session_state.appointments = []
if 'alarms' not in st.session_state: st.session_state.alarms = []

# --- ΨΗΛΑ: ΩΡΑ ΚΑΙ ΗΜΕΡΟΜΗΝΙΑ (Κάθετη Διάταξη) ---
now = datetime.datetime.now()
st.markdown(f"""
    <div class="clock-container">
        <div class="time-box">{now.strftime('%H:%M:%S')}</div>
        <div class="date-box">{now.strftime('%A, %d %B %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR: ΡΑΔΙΟΦΩΝΟ, ΞΥΠΝΗΤΗΡΙ & ΕΙΔΗΣΕΙΣ ---
with st.sidebar:
    st.header("📻 Ζωντανό Ραδιόφωνο")
    
    radio_stations = {
        "ΕΡΤ (Πρώτο Πρόγραμμα)": "https://ert-proto.live24.gr/ert_proto",
        "ERT News 105.8": "https://ert-news.live24.gr/ert_news",
        "ERA Sport": "https://ert-erasport.live24.gr/ert_erasport",
        "PARAPOLITIKA 90.1": "https://parapolitika.live24.gr/parapolitika901",
        "REAL NEWS 97.8": "https://realfm.live24.gr/realfm",
        "RADIO THESSALONIKI 94.5": "https://rthes.live24.gr/rthes",
        "COSMORADIO 95.9": "https://cosmoradio.live24.gr/cosmo959",
        "VELVET 96.8": "https://velvet968.live24.gr/velvet968",
        "LOVE RADIO 97.5": "https://loveradio.live24.gr/loveradio1000",
        "KISS FM 92.9": "https://kissfm.live24.gr/kiss929",
        "METROPOLIS 95.5": "https://metropolis.live24.gr/metropolis955",
        "ZOO RADIO 90.8": "https://zooradio.live24.gr/zoo908",
        "LIBERO 101.7": "https://libero.live24.gr/libero1017",
        "PEPPER 96.6": "https://pepper966.live24.gr/pepper966"
    }
    
    selected_r = st.selectbox("Επίλεξε σταθμό:", list(radio_stations.keys()))
    # ΔΙΟΡΘΩΣΗ: Αφαίρεση του key για αποφυγή TypeError στην Python 3.13
    st.audio(radio_stations[selected_r], format="audio/mp3")
    st.caption("💡 Πατήστε Play για να ξεκινήσει η ροή.")

    st.markdown("---")
    st.header("⏰ Διαχείριση Αφύπνισης")
    alarm_mode = st.radio("Λειτουργία:", ["Συγκεκριμένη Ώρα", "Αντίστροφη Μέτρηση"])
    
    if alarm_mode == "Συγκεκριμένη Ώρα":
        new_time = st.time_input("Ώρα:", datetime.time(8, 0))
        if st.button("🔔 Προσθήκη"):
            st.session_state.alarms.append(new_time.strftime('%H:%M'))
            st.rerun()
    else:
        mins = st.number_input("Λεπτά από τώρα:", min_value=1, max_value=600, value=15)
        if st.button("⏳ Έναρξη Timer"):
            target = (datetime.datetime.now() + datetime.timedelta(minutes=mins)).strftime('%H:%M')
            st.session_state.alarms.append(target)
            st.rerun()

    if st.session_state.alarms:
        for i, alarm in enumerate(st.session_state.alarms):
            col_al1, col_al2 = st.columns([3, 1])
            col_al1.warning(f"⏰ {alarm}")
            if col_al2.button("✖️", key=f"al_{i}"):
                st.session_state.alarms.pop(i)
                st.rerun()

    st.markdown("---")
    st.header("📰 Πηγή Ειδήσεων")
    news_sources = {
        "Ναυτεμπορική": "https://www.naftemporiki.gr/feed/",
        "ΕΡΤ News": "https://www.ertnews.gr/feed/",
        "Reuters": "https://www.reutersagency.com/feed/?best-topics=world-news&post_type=best",
        "Capital.gr": "https://www.capital.gr/rss"
    }
    selected_news_source = st.selectbox("Επιλογή:", list(news_sources.keys()))

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Το Πρόγραμμά μου")
    with st.expander("➕ Προσθήκη Νέου Ραντεβού", expanded=True):
        with st.form("appt_form", clear_on_submit=True):
            title = st.text_input("Τίτλος")
            loc = st.text_input("Τοποθεσία")
            d = st.date_input("Ημερομηνία")
            tm = st.time_input("Ώρα")
            repeat = st.selectbox("Επανάληψη:", ["Μία φορά", "Καθημερινά", "Εβδομαδιαίως", "Μηνιαίως"])
            if st.form_submit_button("Αποθήκευση"):
                m_url = f"https://www.google.com/maps/search/?api=1&query={loc.replace(' ', '+')}"
                st.session_state.appointments.append({
                    "Τίτλος": title, "Τοπ": loc, "D": str(d), 
                    "T": tm.strftime("%H:%M"), "L": m_url, "Repeat": repeat
                })
                st.rerun()

    if st.session_state.appointments:
        for i, a in enumerate(st.session_state.appointments):
            with st.container():
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"🗓️ **{a['Τίτλος']}** | 🕒 {a['T']} | 📍 [{a['Τοπ']}]({a['L']})")
                if a['Repeat'] != "Μία φορά":
                    c1.markdown(f"<span class='repeat-tag'>🔄 {a['Repeat']}</span>", unsafe_allow_html=True)
                if c2.button("🗑️", key=f"del_appt_{i}"):
                    st.session_state.appointments.pop(i)
                    st.rerun()
                st.markdown("---")

with col2:
    st.subheader("🔥 Ροή Ειδήσεων")
    try:
        feed = feedparser.parse(news_sources[selected_news_source])
        if feed.entries:
            titles = "  •  ".join([post.title for post in feed.entries[:12]])
            st.markdown(f"""
                <div style="background:#000; padding:10px; border-left:5px solid #ff4b4b; border-radius:5px;">
                    <marquee color="#00ff00" font-size="18px" font-weight="bold">{titles}</marquee>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("---")
            for post in feed.entries[:8]:
                st.markdown(f"🔹 [{post.title}]({post.link})")
    except:
        st.error("Σφάλμα σύνδεσης ειδήσεων.")
