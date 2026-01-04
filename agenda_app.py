import streamlit as st
import pandas as pd
import datetime
import feedparser

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Dashboard Pro", layout="wide", page_icon="⚡")

# Custom CSS για εμφάνιση και το "ρολόι"
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

# --- SIDEBAR: ΡΑΔΙΟΦΩΝΟ ΚΑΙ ΡΥΘΜΙΣΕΙΣ ---
with st.sidebar:
    st.header("📻 Ζωντανό Ραδιόφωνο")
    radio_stations = {
        "ΕΡΤ (Πρώτο)": "https://ertradio.secure.footprint.net/atunw/radio/ert_proto/playlist.m3u8",
        "ERT News 105.8": "https://ertradio.secure.footprint.net/atunw/radio/ert_news/playlist.m3u8",
        "REAL NEWS 97.8": "https://realfm.live24.gr/realfm",
        "RADIO THESSALONIKI": "https://rthes.live24.gr/rthes",
        "LOVE RADIO 97.5": "https://loveradio.live24.gr/loveradio1000",
        "KISS FM 92.9": "https://kissfm.live24.gr/kiss929",
        "METROPOLIS 95.5": "https://metropolis.live24.gr/metropolis955"
    }
    selected_r = st.selectbox("Επίλεξε σταθμό:", list(radio_stations.keys()))
    st.audio(radio_stations[selected_r], format="audio/mp3")
    st.caption("ℹ️ Αν κολλήσει, αλλάξτε σταθμό και επιστρέψτε.")

    st.markdown("---")
    st.header("📰 News Feed Configuration")
    
    # ΠΛΗΡΗΣ ΛΙΣΤΑ ΑΠΟ ΤΟ ΑΡΧΕΙΟ ΣΟΥ
    categories = {
        "Διεθνή Ειδησεογραφικά": {
            "Reuters - Top News": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
            "ABC News Stories": "http://feeds.abcnews.com/abcnews/topstories",
            "BBC World News": "https://feeds.bbci.co.uk/news/world/rss.xml",
            "Euronews": "https://www.euronews.com/rss?level=vertical&name=news",
            "France24": "https://www.france24.com/en/rss",
            "Aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
            "The Guardian": "https://www.theguardian.com/world/rss"
        },
        "Ελληνικά Media": {
            "Η Καθημερινή": "https://www.kathimerini.gr/rss",
            "eKathimerini (En)": "https://www.ekathimerini.com/feed/",
            "ΤΑ ΝΕΑ": "https://www.tanea.gr/feed/",
            "Ναυτεμπορική": "https://www.naftemporiki.gr/feed/",
            "ΕΡΤ News": "https://www.ertnews.gr/feed/",
            "Newsbeast": "https://www.newsbeast.gr/feed",
            "Hellenic Parliament": "https://www.hellenicparliament.gr/rss"
        },
        "Τεχνολογία & Linux": {
            "ArsTechnica": "https://feeds.arstechnica.com/arstechnica/index",
            "9to5Linux": "https://9to5linux.com/category/news/feed",
            "Wired Tech": "https://www.wired.com/feed/category/gear/latest/rss",
            "TechCrunch": "https://techcrunch.com/feed/",
            "The Verge": "https://www.theverge.com/rss/index.xml"
        },
        "Επιστήμη & Διάστημα": {
            "NASA Image of the Day": "https://www.nasa.gov/rss/dyn/lg_image_of_the_day.rss",
            "Science Daily": "https://www.sciencedaily.com/rss/all.xml",
            "Popular Science": "https://www.popsci.com/feed",
            "Wired Science": "https://www.wired.com/feed/category/science/latest/rss",
            "Phys.org": "https://phys.org/rss-feed/"
        },
        "Gaming & Hobby": {
            "IGN All": "https://feeds.feedburner.com/ign/all",
            "Eurogamer": "https://www.eurogamer.net/feed",
            "Polygon": "https://www.polygon.com/rss/index.xml",
            "Kotaku": "https://kotaku.com/rss",
            "3D Printing News": "https://3dprinting.com/feed",
            "Warhammer Community": "https://warhammer-community.com/feed"
        }
    }
    
    cat_choice = st.selectbox("Επίλεξε Κατηγορία:", list(categories.keys()))
    feed_choice = st.selectbox("Επίλεξε Πηγή:", list(categories[cat_choice].keys()))
    feed_url = categories[cat_choice][feed_choice]

    st.markdown("---")
    st.header("⏰ Αφύπνιση / Timer")
    mode = st.radio("Τύπος:", ["Ώρα", "Timer (λεπτά)"])
    if mode == "Ώρα":
        t_input = st.time_input("Στις:", datetime.time(8, 0))
        if st.button("🔔 Ορισμός"): 
            st.session_state.alarms.append(t_input.strftime('%H:%M'))
            st.rerun()
    else:
        m_input = st.number_input("Λεπτά:", 1, 600, 15)
        if st.button("⏳ Έναρξη"):
            target = (datetime.datetime.now() + datetime.timedelta(minutes=m_input)).strftime('%H:%M')
            st.session_state.alarms.append(target)
            st.rerun()

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ ---
col1, col2 = st.columns([1.8, 1.2])

with col1:
    st.subheader("📝 Το Πρόγραμμά μου")
    with st.expander("➕ Προσθήκη Ραντεβού/Υποχρέωσης", expanded=False):
        with st.form("appt_form", clear_on_submit=True):
            t = st.text_input("Τίτλος")
            l = st.text_input("Τοποθεσία")
            d = st.date_input("Ημερομηνία")
            tm = st.time_input("Ώρα")
            rep = st.selectbox("Επανάληψη:", ["Μία φορά", "Καθημερινά", "Εβδομαδιαίως", "Μηνιαίως"])
            if st.form_submit_button("Αποθήκευση"):
                st.session_state.appointments.append({
                    "Τίτλος": t, "Τοπ": l, "D": str(d), "T": tm.strftime("%H:%M"), 
                    "L": f"https://www.google.com/maps/search/{l.replace(' ', '+')}", "Repeat": rep
                })
                st.rerun()

    # Εμφάνιση λίστας ραντεβού
    if not st.session_state.appointments:
        st.info("Δεν υπάρχουν προγραμματισμένα ραντεβού.")
    else:
        for i, a in enumerate(st.session_state.appointments):
            c_task, c_del = st.columns([0.9, 0.1])
            with c_task:
                st.markdown(f"🗓️ **{a['Τίτλος']}**")
                st.markdown(f"🕒 {a['T']} | 📍 [{a['Τοπ']}]({a['L']}) | 🔄 {a['Repeat']}")
            with c_del:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.appointments.pop(i)
                    st.rerun()
            st.divider()

with col2:
    st.subheader(f"🗞️ {feed_choice}")
    try:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            # News Ticker (Κυλιόμενοι Τίτλοι)
            titles_ticker = "  •  ".join([post.title for post in feed.entries[:10]])
            st.markdown(f"""
                <div style="background:#000; padding:10px; border-radius:5px; border:1px solid #00d4ff; margin-bottom:15px;">
                    <marquee scrollamount="5" style="color:#00ff00; font-family:monospace; font-size:16px;">{titles_ticker}</marquee>
                </div>
                """, unsafe_allow_html=True)
            
            # Λίστα άρθρων
            for post in feed.entries[:12]:
                with st.container():
                    st.markdown(f"🔗 **[{post.title}]({post.link})**")
                    if 'published' in post:
                        st.caption(f"📅 {post.published}")
                    st.divider()
        else:
            st.warning("Δεν βρέθηκαν ειδήσεις. Ίσως το feed να είναι προσωρινά μη διαθέσιμο.")
    except Exception as e:
        st.error(f"Σφάλμα φόρτωσης ειδήσεων: {e}")

# Check για Alarms (απλή ειδοποίηση στην οθόνη)
current_time_str = now.strftime('%H:%M')
if current_time_str in st.session_state.alarms:
    st.toast(f"🔔 ΕΙΔΟΠΟΙΗΣΗ: {current_time_str}!", icon="⏰")
    # Αφαιρούμε το alarm αφού χτυπήσει για να μην ξαναχτυπάει στο ίδιο λεπτό
    st.session_state.alarms.remove(current_time_str)
