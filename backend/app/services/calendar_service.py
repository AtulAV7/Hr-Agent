from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict
from app.config import settings

class GoogleCalendarService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token
        if os.path.exists(settings.GOOGLE_CALENDAR_TOKEN_FILE):
            with open(settings.GOOGLE_CALENDAR_TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = Flow.from_client_secrets_file(
                    settings.GOOGLE_CALENDAR_CREDENTIALS_FILE, self.SCOPES)
                flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                
                auth_url, _ = flow.authorization_url(prompt='consent')
                print(f'Please visit this URL to authorize the application: {auth_url}')
                
                code = input('Enter the authorization code: ')
                flow.fetch_token(code=code)
                creds = flow.credentials
            
            # Save credentials for future use
            with open(settings.GOOGLE_CALENDAR_TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def schedule_interview(self, candidate_name: str, candidate_email: str, start_time: datetime, duration_hours: int = 1) -> Dict:
        """Schedule an interview in Google Calendar"""
        
        end_time = start_time + timedelta(hours=duration_hours)
        
        event = {
            'summary': f'Interview - {candidate_name}',
            'description': f'Technical interview with {candidate_name}',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [
                {'email': candidate_email},
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': f'interview-{candidate_name}-{int(start_time.timestamp())}',
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }
        
        try:
            event = self.service.events().insert(
                calendarId='primary', 
                body=event,
                conferenceDataVersion=1
            ).execute()
            
            return {
                'event_id': event['id'],
                'meet_link': event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', 'No meet link'),
                'status': 'scheduled'
            }
            
        except Exception as e:
            print(f"Error scheduling interview: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def get_available_slots(self, num_days: int = 7) -> List[datetime]:
        """Get available time slots for interviews"""
        available_slots = []
        now = datetime.now()
        
        for day in range(1, num_days + 1):
            date = now + timedelta(days=day)
            # Simple logic: 9 AM to 5 PM, hourly slots
            for hour in range(9, 17):
                slot_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                available_slots.append(slot_time)
        
        return available_slots