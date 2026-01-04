import streamlit as st
import pandas as pd
import datetime
import feedparser
import os.path
import pickle
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

st.set_page_config(page_title="Σύνδεση Google", layout="wide")

# --- ΕΙΔΙΚΟΣ ΚΩΔΙΚΑΣ ΓΙΑ ΔΗΜΙΟΥΡΓΙΑ TOKEN ΧΩΡΙΣ ΤΟΠΙΚΗ PYTHON ---
st.sidebar.header("🔐 Σύνδεση με Google")

if not os.path.exists('token.pickle'):
    if os.path.exists('credentials.json'):
        # Ρύθμιση του Flow για χειροκίνητη εισαγωγή κωδικού
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/calendar'],
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )

        auth_url, _ = flow.authorization_url(prompt='consent')

        st.sidebar.warning("Χρειάζεται έγκριση!")
        st.sidebar.write("1. Πάτα το παρακάτω link:")
        st.sidebar.markdown(f"[Έγκριση Google]({auth_url})")
        
        auth_code = st.sidebar.text_input("2. Βάλε τον κωδικό που σου έβγαλε η Google:")
        
        if auth_code:
            try:
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
                st.sidebar.success("✅ Το token δημιουργήθηκε! Κάνε Refresh τη σελίδα.")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Λάθος κωδικός: {e}")
    else:
        st.sidebar.error("Ανέβασε το credentials.json στο GitHub πρώτα!")

# --- ΤΟ ΥΠΟΛΟΙΠΟ DASHBOARD (Ο κώδικας που είχαμε) ---
# (Εδώ συνεχίζει ο υπόλοιπος κώδικας που σου έδωσα πριν...)
