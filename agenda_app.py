import streamlit as st
import pandas as pd
import datetime
import feedparser

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="News & Agenda Dashboard", layout="wide", page_icon="🏛️")

# Custom CSS για Dashboard αισθητική
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .clock-container {
        background: #1e1e1e; padding: 25px; border-radius: 15px;
        border: 2px solid #ff4b4b; text-align: center; margin-bottom: 25px;
    }
    .time-box { color: #00ff00; font-size: 55px; font-weight: bold; line-height: 1; }
    .date-box { color: #00d4ff; font-size: 22px; font-weight: bold; margin-top: 10px; border-top: 1px solid #444; padding-top: 10px; }
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
        "ΕΡΤ (Πρώτο)": "https://ertradio.secure.footprint.net/atunw/radio/ert_proto/playlist.m3u8",
        "ERT News 105.8": "https://ertradio.secure.footprint.net/atunw/radio/ert_news/playlist.m3u8",
        "REAL NEWS 97.8": "https://realfm.live24.gr/realfm",
        "RADIO THESSALONIKI": "https://rthes.live24.gr/rthes",
        "LOVE RADIO 97.5": "https://loveradio.live24.gr/loveradio1000",
        "METROPOLIS 95.5": "https://metropolis.live24.gr/metropolis955"
    }
    selected_r = st.selectbox("Επίλεξε σταθμό:", list(radio_stations.keys()))
    st.audio(radio_stations[selected_r], format="audio/mp3")

    st.markdown("---")
    st.header("📰 Επιλογή Ενημέρωσης")
    
    categories = {
        "Πολιτική (Διεθνής)": {
            "POLITICO Europe": "https://www.politico.eu/feed",
            "RealClearPolitics": "https://www.realclearpolitics.com/index.xml",
            "The Nation": "https://www.thenation.com/subject/politics/feed",
            "National Review": "https://www.nationalreview.com/feed",
            "Foreign Policy": "https://foreignpolicy.com/feed",
            "The Hill": "https://thehill.com/homenews/feed"
        },
        "Ελληνικά Media": {
            "Η Καθημερινή": "https://www.kathimerini.gr/rss",
            "Ναυτεμπορική": "https://www.naftemporiki.gr/feed/",
            "ΕΡΤ News": "https://www.ertnews.gr/feed/",
            "Newsbeast": "https://www.newsbeast.gr/feed",
            "ΤΑ ΝΕΑ": "https://www.tanea.gr/feed/",
            "Ελληνικό Κοινοβούλιο": "https://www.hellenicparliament.gr/rss"
        },
        "Οικονομία & Business": {
            "Reuters Business": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
            "Financial Times": "https://www.ft.com/?format=rss",
            "The Economist": "https://www.economist.com/the-world-this-week/rss.xml",
            "Capital.gr": "https://www.capital.gr/rss",
            "Bloomberg Politics": "https://www.bloomberg.com/politics/feeds/site.xml"
        },
        "Διεθνή Πρακτορεία": {
            "Reuters - All": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
            "BBC News World": "https://feeds.bbci.co.uk/news/world/rss.xml",
            "Aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
            "France24": "https://www.france24.com/en/rss",
            "Euronews": "https://www.euronews.com/rss?level=vertical&name=news"
        }
    }
    
    cat_choice = st.selectbox("Κατηγορία:", list(categories.keys()))
    feed_choice = st.selectbox("Πηγή:", list(categories[cat_choice].keys()))
    feed_url = categories[cat_choice][feed_choice]

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
col1, col2 = st.columns([1.8, 1.2])

with col1:
    st.subheader("📝 Πρόγραμμα")
    with st.expander("➕ Νέα Καταχώρηση", expanded=False):
        with st.form("appt_form", clear_on_submit=True):
            t = st.text_input("Τίτλος"); l = st.text_input("Τοποθεσία")
            d = st.date_input("Ημερομηνία"); tm = st.time_input("Ώρα")
            rep = st.selectbox("Επανάληψη:", ["Μία φορά", "Καθημερινά", "Εβδομαδιαίως", "Μηνιαίως"])
            if st.form_submit_button("Αποθήκευση"):
                st.session_state.appointments.append({
                    "Τίτλος": t, "Τοπ": l, "D": str(d), "T": tm.strftime("%H:%M"), 
                    "L": f"http://googleusercontent.com/maps.google.com/8{l.replace(' ', '+')}", "Repeat": rep
                })
                st.rerun()

    if st.session_state.appointments:
        for i, a in enumerate(st.session_state.appointments):
            c_task, c_del = st.columns([0.9, 0.1])
            with c_task:
                st.markdown(f"🗓️ **{a['Τίτλος']}** | 🕒 {a['T']} | 📍 [{a['Τοπ']}]({a['L']}) | 🔄 {a['Repeat']}")
            with c_del:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.appointments.pop(i); st.rerun()
            st.divider()

with col2:
    st.subheader(f"🔥 {feed_choice}")
    try:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            # Ticker
            titles_ticker = "  •  ".join([post.title for post in feed.entries[:10]])
            st.markdown(f'<div style="background:#000;padding:10px;border:1px solid #00d4ff;"><marquee style="color:#00ff00;font-family:monospace;">{titles_ticker}</marquee></div>', unsafe_allow_html=True)
            
            # List
            for post in feed.entries[:12]:
                st.markdown(f"🔗 **[{post.title}]({post.link})**")
                st.divider()
        else:
            st.warning("Το feed είναι προσωρινά μη διαθέσιμο.")
    except Exception as e:
        st.error(f"Σφάλμα: {e}")
