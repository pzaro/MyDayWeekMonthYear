import streamlit as st
import pandas as pd
import datetime
import feedparser

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Dashboard Pro", layout="wide", page_icon="⚡")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .clock-container {
        background: #1e1e1e; padding: 30px; border-radius: 20px;
        border: 2px solid #ff4b4b; text-align: center; margin-bottom: 30px;
    }
    .time-box { color: #00ff00; font-size: 60px; font-weight: bold; line-height: 1; }
    .date-box { color: #00d4ff; font-size: 25px; font-weight: bold; margin-top: 15px; border-top: 1px solid #444; padding-top: 10px; }
    .repeat-tag { background-color: #3d3d3d; color: #ffbd45; padding: 2px 8px; border-radius: 5px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# Αρχικοποίηση session states
if 'appointments' not in st.session_state: st.session_state.appointments = []
if 'alarms' not in st.session_state: st.session_state.alarms = []

# --- ΨΗΛΑ: ΩΡΑ ΚΑΙ ΗΜΕΡΟΜΗΝΙΑ ---
now = datetime.datetime.now()
st.markdown(f"""
    <div class="clock-container">
        <div class="time-box">{now.strftime('%H:%M:%S')}</div>
        <div class="date-box">{now.strftime('%A, %d %B %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("📻 Ζωντανό Ραδιόφωνο")
    radio_stations = {
        "ΕΡΤ (Πρώτο)": "https://ert-proto.live24.gr/ert_proto",
        "ERT News 105.8": "https://ert-news.live24.gr/ert_news",
        "REAL NEWS 97.8": "https://realfm.live24.gr/realfm",
        "RADIO THESSALONIKI 94.5": "https://rthes.live24.gr/rthes",
        "COSMORADIO 95.9": "https://cosmoradio.live24.gr/cosmo959",
        "LOVE RADIO 97.5": "https://loveradio.live24.gr/loveradio1000",
        "KISS FM 92.9": "https://kissfm.live24.gr/kiss929",
        "METROPOLIS 95.5": "https://metropolis.live24.gr/metropolis955"
    }
    selected_r = st.selectbox("Επίλεξε σταθμό:", list(radio_stations.keys()))
    # Προσθήκη info για το Play
    st.info("⚠️ Πατήστε το Play δύο φορές αν κολλήσει λόγω browser.")
    st.audio(radio_stations[selected_r], format="audio/mp3")

    st.markdown("---")
    st.header("📰 Πηγές Ειδήσεων (RSS)")
    news_sources = {
        "Reuters World": "https://www.reutersagency.com/feed/?best-topics=world-news&post_type=best",
        "AP News": "https://purl.org/atom/1.0/topstories",
        "Euronews": "https://www.euronews.com/rss?level=vertical&name=news",
        "France24": "https://www.france24.com/en/rss",
        "Η Καθημερινή": "https://www.kathimerini.gr/rss",
        "eKathimerini (EN)": "https://www.ekathimerini.com/feed/",
        "ΤΑ ΝΕΑ": "https://www.tanea.gr/feed/",
        "Newsbeast": "https://www.newsbeast.gr/feed",
        "Ελληνικό Κοινοβούλιο": "https://www.hellenicparliament.gr/rss"
    }
    selected_news = st.selectbox("Επιλογή:", list(news_sources.keys()))

    st.markdown("---")
    st.header("⏰ Αφύπνιση / Timer")
    mode = st.radio("Τύπος:", ["Ώρα", "Timer (λεπτά)"])
    if mode == "Ώρα":
        t_input = st.time_input("Στις:", datetime.time(8, 0))
        if st.button("🔔 Ορισμός"): st.session_state.alarms.append(t_input.strftime('%H:%M')); st.rerun()
    else:
        m_input = st.number_input("Λεπτά:", 1, 600, 15)
        if st.button("⏳ Έναρξη"):
            target = (datetime.datetime.now() + datetime.timedelta(minutes=m_input)).strftime('%H:%M')
            st.session_state.alarms.append(target); st.rerun()

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Πρόγραμμα")
    with st.expander("➕ Νέα Καταχώρηση", expanded=True):
        with st.form("appt_form", clear_on_submit=True):
            t = st.text_input("Τίτλος"); l = st.text_input("Τοποθεσία")
            d = st.date_input("Ημερομηνία"); tm = st.time_input("Ώρα")
            rep = st.selectbox("Επανάληψη:", ["Μία φορά", "Καθημερινά", "Εβδομαδιαίως", "Μηνιαίως"])
            if st.form_submit_button("Αποθήκευση"):
                st.session_state.appointments.append({
                    "Τίτλος": t, "Τοπ": l, "D": str(d), "T": tm.strftime("%H:%M"), 
                    "L": f"http://google.com/maps/search/{l.replace(' ', '+')}", "Repeat": rep
                })
                st.rerun()

    for i, a in enumerate(st.session_state.appointments):
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"🗓️ **{a['Τίτλος']}** | 🕒 {a['T']} | 📍 [{a['Τοπ']}]({a['L']}) | 🔄 {a['Repeat']}")
        if c2.button("🗑️", key=f"d_{i}"): st.session_state.appointments.pop(i); st.rerun()

with col2:
    st.subheader("🔥 Live Ticker")
    try:
        feed = feedparser.parse(news_sources[selected_news])
        titles = "  •  ".join([post.title for post in feed.entries[:15]])
        st.markdown(f"""
            <div style="background:#000; padding:10px; border-left:5px solid #ff4b4b; border-radius:5px;">
                <marquee color="#00ff00" font-size="18px" font-weight="bold">{titles}</marquee>
            </div>
            """, unsafe_allow_html=True)
        for post in feed.entries[:6]:
            st.markdown(f"🔹 <a href='{post.link}' style='color:#00d4ff; text-decoration:none;'>{post.title}</a>", unsafe_allow_html=True)
    except: st.error("Σφάλμα σύνδεσης ειδήσεων.")
