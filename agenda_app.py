import streamlit as st
import pandas as pd
import datetime
import feedparser
import time

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Dashboard Pro", layout="wide", page_icon="⚡")

# CSS για το Design
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
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
    .alarm-active { background-color: #ff4b4b; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# Αρχικοποίηση session states
if 'appointments' not in st.session_state: st.session_state.appointments = []
if 'alarms' not in st.session_state: st.session_state.alarms = []
if 'diet_logs' not in st.session_state: st.session_state.diet_logs = []

# --- ΨΗΛΑ: ΩΡΑ ΚΑΙ ΗΜΕΡΟΜΗΝΙΑ ---
now = datetime.datetime.now()
current_time_str = now.strftime('%H:%M')

st.markdown(f"""
    <div class="clock-container">
        <div style="text-align: center;">
            <div style="color: #aaa; font-size: 12px; text-transform: uppercase;">ΩΡΑ</div>
            <div class="time-box">{now.strftime('%H:%M:%S')}</div>
        </div>
        <div style="text-align: center;">
            <div style="color: #aaa; font-size: 12px; text-transform: uppercase;">ΗΜΕΡΟΜΗΝΙΑ</div>
            <div class="date-box">{now.strftime('%A, %d %B %Y')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- ΕΛΕΓΧΟΣ ΞΥΠΝΗΤΗΡΙΟΥ (ALARM LOGIC) ---
alarm_triggered = False
if current_time_str in st.session_state.alarms:
    alarm_triggered = True
    st.markdown('<div class="alarm-active">🚨 ΤΟ ΞΥΠΝΗΤΗΡΙ ΧΤΥΠΑΕΙ! 🚨</div>', unsafe_allow_html=True)

# --- SIDEBAR: ΡΑΔΙΟΦΩΝΟ & ΑΠΛΟ ΞΥΠΝΗΤΗΡΙ ---
with st.sidebar:
    st.header("📻 Ρυθμίσεις Ήχου")
    radio_stations = {
        "ΕΡΤ (Πρώτο)": "https://ert-proto.live24.gr/ert_proto",
        "ERT News 105.8": "https://ert-news.live24.gr/ert_news",
        "PARAPOLITIKA 90.1": "https://parapolitika.live24.gr/parapolitika901",
        "REAL NEWS 97.8": "https://realfm.live24.gr/realfm",
        "RADIO THESSALONIKI 94.5": "https://rthes.live24.gr/rthes",
        "COSMORADIO 95.9": "https://cosmoradio.live24.gr/cosmo959",
        "KISS FM 92.9": "https://kissfm.live24.gr/kiss929",
        "METROPOLIS 95.5": "https://metropolis.live24.gr/metropolis955"
    }
    selected_r = st.selectbox("Επιλεγμένος Σταθμός:", list(radio_stations.keys()))
    yt_link = st.text_input("YouTube Link (για αφύπνιση):", "https://www.youtube.com/watch?v=SSuCyZlksrI")
    
    alarm_source = st.radio("Πηγή Ήχου Ξυπνητηριού:", ["Ραδιόφωνο", "YouTube"])

    st.markdown("---")
    st.header("⏰ Διαχείριση Αφύπνισης")
    new_alarm = st.time_input("Ρύθμιση ώρας:", datetime.time(8, 0))
    if st.button("🔔 Προσθήκη Αφύπνισης"):
        st.session_state.alarms.append(new_alarm.strftime('%H:%M'))
        st.rerun()

    if st.session_state.alarms:
        for i, alarm in enumerate(st.session_state.alarms):
            col_al1, col_al2 = st.columns([3, 1])
            col_al1.info(f"⏰ {alarm}")
            if col_al2.button("✖️", key=f"alarm_{i}"):
                st.session_state.alarms.pop(i)
                st.rerun()

    # --- ΑΥΤΟΜΑΤΗ ΕΚΚΙΝΗΣΗ ΗΧΟΥ ---
    if alarm_triggered:
        st.warning(f"Ενεργή Αφύπνιση: {current_time_str}")
        if alarm_source == "Ραδιόφωνο":
            st.audio(radio_stations[selected_r], autoplay=True)
        else:
            st.video(yt_link, autoplay=True)
    else:
        # Απλό player για χειροκίνητη χρήση
        st.audio(radio_stations[selected_r])

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Πρόγραμμα & Ραντεβού")
    with st.expander("➕ Νέο Ραντεβού", expanded=False):
        with st.form("appt_form", clear_on_submit=True):
            title = st.text_input("Τίτλος")
            loc = st.text_input("Τοποθεσία")
            d = st.date_input("Ημερομηνία")
            tm = st.time_input("Ώρα")
            repeat_freq = st.selectbox("Επανάληψη:", ["Μία φορά", "Καθημερινά", "Εβδομαδιαίως", "Μηνιαίως", "Ετησίως"])
            if st.form_submit_button("Αποθήκευση"):
                m_url = f"https://www.google.com/maps/search/{loc.replace(' ', '+')}"
                st.session_state.appointments.append({
                    "Τίτλος": title, "Τοπ": loc, "D": str(d), 
                    "T": tm.strftime("%H:%M"), "L": m_url, "Repeat": repeat_freq
                })
                st.rerun()

    if st.session_state.appointments:
        for i, a in enumerate(st.session_state.appointments):
            with st.container():
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"🗓️ **{a['Τίτλος']}** | 🕒 {a['T']} | 📍 [{a['Τοπ']}]({a['L']}) | 🔄 {a['Repeat']}")
                if c2.button("🗑️", key=f"del_appt_{i}"):
                    st.session_state.appointments.pop(i)
                    st.rerun()
                st.markdown("---")

with col2:
    st.subheader("🔥 Ειδήσεις")
    try:
        feed = feedparser.parse("https://www.ertnews.gr/feed/")
        titles = "  •  ".join([post.title for post in feed.entries[:10]])
        st.markdown(f'<div style="background:#000;padding:10px;border-left:5px solid red;"><marquee color="white">{titles}</marquee></div>', unsafe_allow_html=True)
    except: st.error("Feed error")

    st.markdown("---")
    st.subheader("🥗 Έξοδα")
    with st.form("diet"):
        meal = st.text_input("Γεύμα")
        cost = st.number_input("Ευρώ", min_value=0.0)
        if st.form_submit_button("OK"):
            st.session_state.diet_logs.append({"Γεύμα": meal, "Κόστος": cost})
            st.rerun()
    
    if st.session_state.diet_logs:
        df_diet = pd.DataFrame(st.session_state.diet_logs)
        st.write(f"**Σύνολο:** {df_diet['Κόστος'].sum():.2f} €")
        if st.button("Καθαρισμός"):
            st.session_state.diet_logs = []
            st.rerun()
