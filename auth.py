import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Τα δικαιώματα που ζητάμε (πρόσβαση στο Calendar)
SCOPES = ['https://www.googleapis.com/auth/calendar']

def generate_token():
    creds = None
    # Αν υπάρχει ήδη παλιό token, το διαγράφουμε για να φτιάξουμε φρέσκο
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')

    # Φορτώνει το αρχείο credentials.json που κατέβασες από την εικόνα που μου έστειλες
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    # Αποθηκεύει την έγκριση στο αρχείο token.pickle
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

    print("✅ Επιτυχία! Το αρχείο 'token.pickle' δημιουργήθηκε στον φάκελό σου.")

if __name__ == '__main__':
    generate_token()
