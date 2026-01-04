import streamlit as st
import pandas as pd
import datetime
import feedparser
import time

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Smart Agenda Dashboard", layout="wide")

# --- ΛΕΙΤΟΥΡΓΙΕΣ ---
def get_news(url):
    feed = feedparser.parse(url)
    titles = [post.title for post in feed.entries[:10]] # Τα 10 πρώτα
    return "  •  ".join(titles)

# Αποθήκευση/Φόρτωση Ραντεβού (Session State)
if 'appointments' not in st.session_state:
    st.session_state.appointments = []

# --- SIDEBAR: ΡΑΔΙΟΦΩΝΟ & YOUTUBE ---
st.sidebar.header("🎵 Μουσική & Ραδιόφωνο")
radio_choice = st.sidebar.selectbox("Επίλεξε Σταθμό:", [
    "Love Radio", "ΣΚΑΪ 100.3", "Custom URL"
])

radio_urls = {
    "Love Radio": "https://loveradio.live24.gr/loveradio1000",
    "ΣΚΑΪ 100.3": "https://skai.live24.gr/skai1003",
}

if radio_choice == "Custom URL":
    stream_url = st.sidebar.text_input("Δώσε το Stream URL:")
else:
    stream_url = radio_urls.get(radio_choice)

if stream_url:
    st.sidebar.audio(stream_url)

st.sidebar.markdown("---")
yt_url = st.sidebar.text_input("YouTube Link για Ξυπνητήρι:")
if yt_url:
    st.sidebar.video(yt_url)

# --- ΚΥΡΙΩΣ ΠΑΝΕΛ ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("📅 Η Ατζέντα μου")
    st.subheader(f"Σήμερα είναι {datetime.datetime.now().strftime('%A, %d %B %Y')}")
    
    # Φόρμα Καταχώρησης
    with st.expander("➕ Προσθήκη Νέου Ραντεβού"):
        with st.form("appt_form", clear_on_submit=True):
            title = st.text_input("Τίτλος Ραντεβού")
            date = st.date_input("Ημερομηνία")
            t_time = st.time_input("Ώρα")
            submit = st.form_submit_button("Αποθήκευση")
            
            if submit:
                st.session_state.appointments.append({"Τίτλος": title, "Ημερομηνία": date, "Ώρα": t_time})
                st.success("Το ραντεβού καταχωρήθηκε!")

    # Εμφάνιση Ραντεβού
    if st.session_state.appointments:
        df = pd.DataFrame(st.session_state.appointments)
        st.table(df)
    else:
        st.info("Δεν υπάρχουν προγραμματισμένα ραντεβού.")

with col2:
    st.markdown("### ⏰ Ρολόι")
    st.metric(label="Ώρα Ελλάδος", value=datetime.datetime.now().strftime("%H:%M:%S"))
    
    st.markdown("---")
    st.markdown("### 📰 Τελευταίες Ειδήσεις")
    news_source = st.radio("Πηγή:", ["Πρώτο Θέμα (GR)", "BBC World (EN)"])
    
    rss_urls = {
        "Πρώτο Θέμα (GR)": "https://www.protothema.gr/rss/general/",
        "BBC World (EN)": "http://feeds.bbci.co.uk/news/rss.xml"
    }
    
    news_ticker = get_news(rss_urls[news_source])
    # Εφέ Ticker με HTML
    st.markdown(f"""
        <div style="background-color: black; padding: 10px; border-radius: 5px; overflow: hidden; white-space: nowrap;">
            <marquee style="color: #00FF00; font-family: monospace; font-size: 18px;">
                {news_ticker}
            </marquee>
        </div>
    """, unsafe_allow_html=True)

# --- ΠΡΟΤΑΣΕΙΣ (Σύμφωνα με το προφίλ σου) ---
st.markdown("---")
st.info("💡 **Extra Tip:** Μπορείς να συνδέσεις την ατζέντα με το κόστος της διατροφής σου (από το προφίλ σου) για να βλέπεις πόσα ξοδεύεις ανά ημέρα!")
