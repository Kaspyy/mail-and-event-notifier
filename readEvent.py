from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Działanie skryptu opartego o API Google Calendar.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # Plik token.json przechowuje prawa dostępu użytkownika oraz token.
    # Tworzony jest automatycznie przy pierwszym uruchomieniu skryptu.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Jeśli nie istnieją dane logowania, pozwala użytkownikowi się zalogować.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Wywołanie API Kalendarza
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' odpowiada za UTC
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True, #maxResluts definiuje liczbę wyświetlanych wydarzeń
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


if __name__ == '__main__':
    main()