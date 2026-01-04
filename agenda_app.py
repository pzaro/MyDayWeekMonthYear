import streamlit as st
import pandas as pd
import datetime
import feedparser

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Dashboard Pro", layout="wide", page_icon="⚡")

# Custom CSS για ομορφιά
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stHeader { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .clock-container {
        display: flex;
        justify-content: space-around;
        background: #1e1e1e;
        padding: 20px;
        border-radius: 15px;
        border-bottom: 4px solid #ff4b4b;
        margin-bottom: 25px;
    }
    .time-box { color: #00ff00; font-size: 45px; font-weight: bold; text-shadow: 0 0 10px #00ff00; }
    .date-box { color: #00d4ff; font-size: 30px; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Αρχικοποίηση session states
if 'appointments' not in st.session_state: st.session_state.appointments = []
if 'diet_logs' not in st.session_state: st.session_state.diet_logs = []

# --- ΨΗΛΑ: ΩΡΑ ΚΑΙ ΗΜΕΡΟΜΗΝΙΑ ---
now = datetime.datetime.now()
st.markdown(f"""
    <div class="clock-container">
        <div style="text-align: center;">
            <div style="color: #aaa; font-size: 14px; text-transform: uppercase;">Τρέχουσα Ώρα</div>
            <div class="time-box">{now.strftime('%H:%M:%S')}</div>
        </div>
        <div style="text-align: center;">
            <div style="color: #aaa; font-size: 14px; text-transform: uppercase;">Ημερομηνία</div>
            <div class="date-box">{now.strftime('%A, %d %B %Y')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR: ΡΑΔΙΟΦΩΝΟ (ΠΛΗΡΗΣ ΛΙΣΤΑ) ---
st.sidebar.header("📻 Live Radio")
radio_stations = {
    "ΕΡΤ (Πρώτο Πρόγραμμα)": "https://ert-proto.live24.gr/ert_proto",
    "ERT News 105.8": "https://ert-news.live24.gr/ert_news",
    "ERA Sport": "https://ert-erasport.live24.gr/ert_erasport",
    "PARAPOLITIKA 90.1": "https://parapolitika.live24.gr/parapolitika901",
    "REAL NEWS 97.8": "https://realfm.live24.gr/realfm",
    "RADIO THESSALONIKI 94.5": "https://rthes.live24.gr/rthes",
    "COSMORADIO 95.9": "https://cosmoradio.live24.gr/cosmo959",
    "VELVET 96.8": "https://velvet968.live24.gr/velvet968",
    "LOVE 102.8 (Thess)": "https://loveradio.live24.gr/love1028",
    "LOVE RADIO 97.5 (Athens)": "https://loveradio.live24.gr/loveradio1000",
    "PLUS 102.6": "https://plus1026.live24.gr/plus1026",
    "ZOO RADIO 90.8": "https://zooradio.live24.gr/zoo908",
    "ATHENS PARTY": "https://athensparty.live24.gr/athensparty",
    "KISS FM 92.9": "https://kissfm.live24.gr/kiss929",
    "PEPPER 96.6": "https://pepper966.live24.gr/pepper966",
    "METROPOLIS 95.5": "https://metropolis.live24.gr/metropolis955",
    "LIBERO 101.7": "https://libero.live24.gr/libero1017"
}
selected_r = st.sidebar.selectbox("Επίλεξε σταθμό:", list(radio_stations.keys()))
st.sidebar.audio(radio_stations[selected_r])

# --- SIDEBAR: ΕΙΔΗΣΕΙΣ ---
st.sidebar.markdown("---")
st.sidebar.header("📰 Πηγές Ειδήσεων")
news_sources = {
    "ΕΡΤ News": "https://www.ertnews.gr/feed/",
    "Ναυτεμπορική": "https://www.naftemporiki.gr/feed/",
    "Capital.gr": "https://www.capital.gr/rss",
    "Reuters": "https://www.reutersagency.com/feed/?best-topics=world-news&post_type=best",
}
selected_news = st.sidebar.selectbox("Επίλεξε Ροή:", list(news_sources.keys()))

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ ---
col1, col2 = st.columns([2, 1])

with col1:
    # Ενότητα Ραντεβού
    with st.container():
        st.subheader("📝 Διαχείριση Ραντεβού")
        with st.form("appt_form", clear_on_submit=True):
            c_a, c_b = st.columns(2)
            title = c_a.text_input("Τίτλος")
            loc = c_b.text_input("Τοποθεσία (Maps)")
            d = c_a.date_input("Ημερομηνία")
            tm = c_b.time_input("Ώρα")
            if st.form_submit_button("➕ Προσθήκη"):
                m_url = f"https://www.google.com/maps/search/?api=1&query={loc.replace(' ', '+')}"
                st.session_state.appointments.append({"Τίτλος": title, "Τοπ": loc, "D": str(d), "T": tm.strftime("%H:%M"), "L": m_url})
    
    if st.session_state.appointments:
        for a in st.session_state.appointments:
            st.info(f"📅 **{a['Τίτλος']}** | 🕒 {a['T']} | 📍 [{a['Τοπ']}]({a['L']})")

    # Ενότητα Δίαιτας
    st.markdown("---")
    st.subheader("🥗 Καταγραφή Δίαιτας & Εξόδων")
    with st.form("diet_form"):
        f1, f2 = st.columns(2)
        meal = f1.text_input("Γεύμα")
        cost = f2.number_input("Κόστος (€)", min_value=0.0)
        if st.form_submit_button("💾 Καταγραφή"):
            st.session_state.diet_logs.append({"Γεύμα": meal, "Κόστος": cost})
    
    if st.session_state.diet_logs:
        df_diet = pd.DataFrame(st.session_state.diet_logs)
        st.table(df_diet)
        st.metric("Συνολικά Έξοδα", f"{df_diet['Κόστος'].sum():.2f} €")

with col2:
    # News Ticker
    st.subheader("🔥 Breaking News")
    try:
        feed = feedparser.parse(news_sources[selected_news])
        titles = "  •  ".join([post.title for post in feed.entries[:15]])
        st.markdown(f"""
            <div style="background: #000; padding: 10px; border-radius: 5px; border-left: 5px solid #ff4b4b;">
                <marquee color="#fff" font-size="20px">{titles}</marquee>
            </div>
            """, unsafe_allow_html=True)
        for post in feed.entries[:5]:
            st.caption(f"🔗 [{post.title}]({post.link})")
    except:
        st.error("Feed error")

    # Alarm Section
    st.markdown("---")
    st.subheader("⏰ Ξυπνητήρι")
    st.sidebar.radio("Alarm Type", ["YouTube", "Radio"], key="alarm_type")
    st.sidebar.text_input("YouTube URL για Alarm", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
