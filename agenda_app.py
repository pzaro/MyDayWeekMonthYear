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
        "METROPOLIS 95.5": "https://metropolis.live24.gr/metropolis955"
    }
    selected_r = st.selectbox("Επίλεξε σταθμό:", list(radio_stations.keys()))
    st.audio(radio_stations[selected_r], format="audio/mp3")

    st.markdown("---")
    st.header("📰 News Feed")
    
    # ΟΡΓΑΝΩΣΗ ΤΩΝ ΠΗΓΩΝ ΣΟΥ ΣΕ ΚΑΤΗΓΟΡΙΕΣ
    categories = {
        "Διεθνή Ειδησεογραφικά": {
            "Reuters - All News": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
            "ABC News Top Stories": "http://feeds.abcnews.com/abcnews/topstories",
            "BBC News World": "https://feeds.bbci.co.uk/news/world/rss.xml",
            "Euronews": "https://www.euronews.com/rss?level=vertical&name=news",
            "France24": "https://www.france24.com/en/rss",
            "Aljazeera": "https://www.aljazeera.com/xml/rss/all.xml"
        },
        "Ελληνικά Media": {
            "Η Καθημερινή": "https://www.kathimerini.gr/rss",
            "eKathimerini (English)": "https://www.ekathimerini.com/feed/",
            "ΤΑ ΝΕΑ": "https://www.tanea.gr/feed/",
            "Ναυτεμπορική": "https://www.naftemporiki.gr/feed/",
            "ΕΡΤ News": "https://www.ertnews.gr/feed/",
            "Newsbeast": "https://www.newsbeast.gr/feed",
            "Ελληνικό Κοινοβούλιο": "https://www.hellenicparliament.gr/rss"
        },
        "Τεχνολογία & Επιστήμη": {
            "ArsTechnica": "https://feeds.arstechnica.com/arstechnica/index",
            "Wired Science": "https://www.wired.com/feed/category/science/latest/rss",
            "Popular Science": "https://www.popsci.com/feed",
            "NASA Image of the Day": "https://www.nasa.gov/rss/dyn/lg_image_of_the_day.rss",
            "Science Daily": "https://www.sciencedaily.com/rss/all.xml",
            "9to5Linux": "https://9to5linux.com/category/news/feed"
        },
        "Gaming & Hobby": {
            "IGN All": "https://feeds.feedburner.com/ign/all",
            "Eurogamer": "https://www.eurogamer.net/feed",
            "Polygon": "https://www.polygon.com/rss/index.xml",
            "3D Printing News": "https://3dprinting.com/feed",
            "Warhammer Community": "https://warhammer-community.com/feed"
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
col1, col2 = st.columns([2, 1])

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
                    "L": f"http://google.com/maps/search/{l.replace(' ', '+')}", "Repeat": rep
                })
                st.rerun()

    for i, a in enumerate(st.session_state.appointments):
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"🗓️ **{a['Τίτλος']}** | 🕒 {a['T']} | 📍 [{a['Τοπ']}]({a['L']}) | 🔄 {a['Repeat']}")
        if c2.button("🗑️", key=f"d_{i}"): st.session_state.appointments.pop(i); st.rerun()

with col2:
    st.subheader(f"🔥 {feed_choice}")
    try:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            titles = "  •  ".join([post.title for post in feed.entries[:15]])
            st.markdown(f"""
                <div style="background:#000; padding:10px; border-left:5px solid #ff4b4b; border-radius:5px;">
                    <marquee color="#00ff00" font-size="18px" font-weight="bold">{titles}</marquee>
                </div>
                """, unsafe_allow_html=True)
            for post in feed.entries[:8]:
                st.markdown(f"🔹 <a href='{post.link}' target='_blank' style='color:#00d4ff; text-decoration:none; font-size:14px;'>{post.title}</a>", unsafe_allow_html=True)
        else:
            st.warning("Δεν βρέθηκαν δεδομένα για αυτή την πηγή.")
    except Exception as e:
        st.error(f"Σφάλμα σύνδεσης: {e}")
