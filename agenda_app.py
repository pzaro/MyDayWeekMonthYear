import streamlit as st
import pandas as pd
import datetime
import feedparser
import time

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Dashboard Pro", layout="wide", page_icon="⚡")

# Custom CSS για το νέο design
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
    .stAudio { margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Αρχικοποίηση session states
if 'appointments' not in st.session_state: st.session_state.appointments = []
if 'alarms' not in st.session_state: st.session_state.alarms = []
if 'diet_logs' not in st.session_state: st.session_state.diet_logs = []

# --- ΨΗΛΑ: ΩΡΑ ΚΑΙ ΗΜΕΡΟΜΗΝΙΑ (Η ημερομηνία κάτω από την ώρα) ---
now = datetime.datetime.now()
st.markdown(f"""
    <div class="clock-container">
        <div class="time-box">{now.strftime('%H:%M:%S')}</div>
        <div class="date-box">{now.strftime('%A, %d %B %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR: ΡΑΔΙΟΦΩΝΟ & NEWS FEED ---
with st.sidebar:
    st.header("📻 Live Radio")
    st.write("Ακούστε ζωντανά οποιαδήποτε στιγμή:")
    radio_stations = {
        "ΕΡΤ (Πρώτο Πρόγραμμα)": "https://ert-proto.live24.gr/ert_proto",
        "ERT News 105.8": "https://ert-news.live24.gr/ert_news",
        "REAL NEWS 97.8": "https://realfm.live24.gr/realfm",
        "RADIO THESSALONIKI 94.5": "https://rthes.live24.gr/rthes",
        "COSMORADIO 95.9": "https://cosmoradio.live24.gr/cosmo959",
        "LOVE RADIO 97.5": "https://loveradio.live24.gr/loveradio1000",
        "KISS FM 92.9": "https://kissfm.live24.gr/kiss929",
        "METROPOLIS 95.5": "https://metropolis.live24.gr/metropolis955",
        "VELVET 96.8": "https://velvet968.live24.gr/velvet968",
        "ZOO RADIO 90.8": "https://zooradio.live24.gr/zoo908"
    }
    selected_r = st.selectbox("Επιλογή Σταθμού:", list(radio_stations.keys()))
    st.audio(radio_stations[selected_r]) # Το ραδιόφωνο είναι πάντα διαθέσιμο εδώ

    st.markdown("---")
    st.header("📰 News Feed (Λειτουργικά)")
    # Επιλογή πηγών που έχουν επιβεβαιωμένα ενεργό RSS
    news_sources = {
        "Ναυτεμπορική (Οικονομία)": "https://www.naftemporiki.gr/feed/",
        "Reuters (World News)": "https://www.reutersagency.com/feed/?best-topics=world-news&post_type=best",
        "ΕΡΤ News (Επικαιρότητα)": "https://www.ertnews.gr/feed/",
        "Capital.gr (Επιχειρήσεις)": "https://www.capital.gr/rss",
        "BBC News": "http://feeds.bbci.co.uk/news/rss.xml"
    }
    selected_news_source = st.selectbox("Επίλεξε Πηγή Ειδήσεων:", list(news_sources.keys()))

    st.markdown("---")
    st.header("⏰ Ξυπνητήρι")
    new_alarm = st.time_input("Ώρα αφύπνισης:", datetime.time(8, 0))
    if st.button("🔔 Ορισμός"):
        st.session_state.alarms.append(new_alarm.strftime('%H:%M'))
        st.rerun()
    
    for i, alarm in enumerate(st.session_state.alarms):
        col_al1, col_al2 = st.columns([3, 1])
        col_al1.warning(f"⏰ {alarm}")
        if col_al2.button("✖️", key=f"al_{i}"):
            st.session_state.alarms.pop(i)
            st.rerun()

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Πρόγραμμα & Ραντεβού")
    with st.expander("➕ Προσθήκη Καταχώρησης", expanded=False):
        with st.form("appt_form", clear_on_submit=True):
            title = st.text_input("Τίτλος")
            loc = st.text_input("Τοποθεσία")
            d = st.date_input("Ημερομηνία")
            tm = st.time_input("Ώρα")
            repeat = st.selectbox("Επανάληψη:", ["Μία φορά", "Καθημερινά", "Εβδομαδιαίως", "Μηνιαίως"])
            if st.form_submit_button("Αποθήκευση"):
                m_url = f"https://www.google.com/maps/search/{loc.replace(' ', '+')}"
                st.session_state.appointments.append({
                    "Τίτλος": title, "Τοπ": loc, "D": str(d), 
                    "T": tm.strftime("%H:%M"), "L": m_url, "Repeat": repeat
                })
                st.rerun()

    if st.session_state.appointments:
        for i, a in enumerate(st.session_state.appointments):
            with st.container():
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"🗓️ **{a['Τίτλος']}** | 🕒 {a['T']} | 📍 [{a['Τοπ']}]({a['L']}) | 🔄 {a['Repeat']}")
                if c2.button("🗑️", key=f"del_{i}"):
                    st.session_state.appointments.pop(i)
                    st.rerun()
                st.markdown("---")

with col2:
    # News Ticker με την επιλεγμένη πηγή
    st.subheader("🔥 Breaking News")
    try:
        feed = feedparser.parse(news_sources[selected_news_source])
        if feed.entries:
            titles = "  •  ".join([post.title for post in feed.entries[:12]])
            st.markdown(f"""
                <div style="background:#000; padding:10px; border-left:5px solid #ff4b4b; border-radius:5px;">
                    <marquee color="#00ff00" font-size="18px" font-weight="bold">{titles}</marquee>
                </div>
                """, unsafe_allow_html=True)
            for post in feed.entries[:5]:
                st.caption(f"🔗 [{post.title}]({post.link})")
        else:
            st.write("Δεν βρέθηκαν ειδήσεις.")
    except:
        st.error("Σφάλμα στη φόρμα ειδήσεων.")

    st.markdown("---")
    st.subheader("🥗 Έξοδα & Δίαιτα")
    with st.form("diet"):
        meal = st.text_input("Γεύμα")
        cost = st.number_input("Ευρώ (€)", min_value=0.0)
        if st.form_submit_button("Καταγραφή"):
            st.session_state.diet_logs.append({"Γεύμα": meal, "Κόστος": cost})
            st.rerun()
    
    if st.session_state.diet_logs:
        df_diet = pd.DataFrame(st.session_state.diet_logs)
        st.write(f"**Σύνολο:** {df_diet['Κόστος'].sum():.2f} €")
        if st.button("Καθαρισμός"):
            st.session_state.diet_logs = []
            st.rerun()
