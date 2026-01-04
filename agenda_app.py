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
    .repeat-tag { background-color: #3d3d3d; color: #ffbd45; padding: 2px 8px; border-radius: 5px; font-size: 12px; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# Αρχικοποίηση session states
if 'appointments' not in st.session_state: st.session_state.appointments = []
if 'alarms' not in st.session_state: st.session_state.alarms = []
if 'diet_logs' not in st.session_state: st.session_state.diet_logs = []

# --- ΨΗΛΑ: ΩΡΑ ΚΑΙ ΗΜΕΡΟΜΗΝΙΑ ---
now = datetime.datetime.now()
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

# --- SIDEBAR: ΡΑΔΙΟΦΩΝΟ & ΑΠΛΟ ΞΥΠΝΗΤΗΡΙ ---
with st.sidebar:
    st.header("📻 Ραδιόφωνο")
    radio_stations = {
        "ΕΡΤ (Πρώτο)": "https://ert-proto.live24.gr/ert_proto",
        "ERT News 105.8": "https://ert-news.live24.gr/ert_news",
        "PARAPOLITIKA 90.1": "https://parapolitika.live24.gr/parapolitika901",
        "REAL NEWS 97.8": "https://realfm.live24.gr/realfm",
        "RADIO THESSALONIKI 94.5": "https://rthes.live24.gr/rthes",
        "COSMORADIO 95.9": "https://cosmoradio.live24.gr/cosmo959",
        "VELVET 96.8": "https://velvet968.live24.gr/velvet968",
        "LOVE RADIO 97.5": "https://loveradio.live24.gr/loveradio1000",
        "KISS FM 92.9": "https://kissfm.live24.gr/kiss929",
        "METROPOLIS 95.5": "https://metropolis.live24.gr/metropolis955"
    }
    selected_r = st.selectbox("Σταθμός:", list(radio_stations.keys()))
    st.audio(radio_stations[selected_r])

    st.markdown("---")
    st.header("⏰ Απλό Ξυπνητήρι")
    new_alarm = st.time_input("Ρύθμιση ώρας:", datetime.time(8, 0))
    if st.button("🔔 Ορισμός Αφύπνισης"):
        st.session_state.alarms.append(new_alarm.strftime('%H:%M'))
        st.success("Το ξυπνητήρι αποθηκεύτηκε!")

    if st.session_state.alarms:
        st.write("**Ενεργές Αφυπνίσεις:**")
        for i, alarm in enumerate(st.session_state.alarms):
            col_al1, col_al2 = st.columns([3, 1])
            col_al1.info(f"⏰ {alarm}")
            if col_al2.button("✖️", key=f"alarm_{i}"):
                st.session_state.alarms.pop(i)
                st.rerun()

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Πρόγραμμα & Ραντεβού")
    with st.expander("➕ Προσθήκη Καταχώρησης", expanded=False):
        with st.form("appt_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            title = f_col1.text_input("Τίτλος")
            loc = f_col2.text_input("Τοποθεσία")
            
            d_col1, d_col2 = st.columns(2)
            d = d_col1.date_input("Ημερομηνία")
            tm = d_col2.time_input("Ώρα")
            
            repeat_freq = st.selectbox("Επανάληψη:", ["Μία φορά", "Καθημερινά", "Εβδομαδιαίως", "Μηνιαίως", "Ετησίως"])
            
            if st.form_submit_button("Αποθήκευση"):
                m_url = f"https://www.google.com/maps/search/?api=1&query={loc.replace(' ', '+')}"
                st.session_state.appointments.append({
                    "Τίτλος": title, "Τοπ": loc, "D": str(d), 
                    "T": tm.strftime("%H:%M"), "L": m_url, "Repeat": repeat_freq
                })
                st.rerun()

    # Λίστα Ραντεβού με δυνατότητα διαγραφής
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
    st.subheader("🔥 Ειδήσεις")
    news_sources = {"ΕΡΤ News": "https://www.ertnews.gr/feed/", "Ναυτεμπορική": "https://www.naftemporiki.gr/feed/"}
    s_news = st.selectbox("Πηγή:", list(news_sources.keys()))
    try:
        feed = feedparser.parse(news_sources[s_news])
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
        if st.button("Καθαρισμός Εξόδων"):
            st.session_state.diet_logs = []
            st.rerun()
