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
        self.authenticated = False
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token
        if os.path.exists(settings.GOOGLE_CALENDAR_TOKEN_FILE):
            try:
                with open(settings.GOOGLE_CALENDAR_TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print(f"Error loading token file: {e}")
                creds = None
        
        # Check if credentials are valid
        if creds and creds.valid:
            self.service = build('calendar', 'v3', credentials=creds)
            self.authenticated = True
            print("✅ Google Calendar authentication successful")
            return
        
        # Try to refresh expired credentials
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(settings.GOOGLE_CALENDAR_TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
                self.service = build('calendar', 'v3', credentials=creds)
                self.authenticated = True
                print("✅ Google Calendar credentials refreshed")
                return
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
        
        # If we reach here, we need new authentication
        print("❌ Google Calendar authentication required")
        print("🔧 Please run the authentication setup script:")
        print("   python auth_setup.py")
        print("📝 Or manually authenticate by visiting Google Calendar API setup")
        
        self.authenticated = False
        self.service = None
    
    def _check_authentication(self):
        """Check if the service is authenticated"""
        if not self.authenticated or not self.service:
            raise Exception(
                "Google Calendar not authenticated. Please run 'python auth_setup.py' first."
            )
    
    def schedule_interview(self, candidate_name: str, candidate_email: str, start_time: datetime, duration_hours: int = 1) -> Dict:
        """Schedule an interview in Google Calendar"""
        
        try:
            self._check_authentication()
        except Exception as e:
            return {
                'status': 'failed', 
                'error': str(e),
                'event_id': None,
                'meet_link': 'Authentication required'
            }
        
        end_time = start_time + timedelta(hours=duration_hours)
        
        event = {
            'summary': f'Interview - {candidate_name}',
            'description': f'Technical interview with {candidate_name}\n\nCandidate Email: {candidate_email}',
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
                    'requestId': f'interview-{candidate_name.replace(" ", "-")}-{int(start_time.timestamp())}',
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 30},       # 30 minutes before
                ],
            },
        }
        
        try:
            event_result = self.service.events().insert(
                calendarId='primary', 
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'  # Send email invitations
            ).execute()
            
            # Extract meet link
            meet_link = 'No meet link generated'
            if 'conferenceData' in event_result:
                entry_points = event_result['conferenceData'].get('entryPoints', [])
                for entry_point in entry_points:
                    if entry_point.get('entryPointType') == 'video':
                        meet_link = entry_point.get('uri', meet_link)
                        break
            
            return {
                'event_id': event_result['id'],
                'meet_link': meet_link,
                'status': 'scheduled',
                'calendar_link': event_result.get('htmlLink', 'No calendar link'),
                'created': event_result.get('created'),
                'updated': event_result.get('updated')
            }
            
        except Exception as e:
            print(f"Error scheduling interview: {e}")
            return {
                'status': 'failed', 
                'error': str(e),
                'event_id': None,
                'meet_link': 'Failed to create'
            }
    
    def get_available_slots(self, num_days: int = 7, start_hour: int = 9, end_hour: int = 17) -> List[datetime]:
        """Get available time slots for interviews"""
        
        # For now, return simple time slots
        # In a real implementation, you'd check against existing calendar events
        available_slots = []
        now = datetime.now()
        
        # Skip weekends and generate weekday slots
        for day in range(1, num_days * 2):  # Check more days to account for weekends
            date = now + timedelta(days=day)
            
            # Skip weekends (Saturday = 5, Sunday = 6)
            if date.weekday() >= 5:
                continue
            
            # Generate hourly slots during business hours
            for hour in range(start_hour, end_hour):
                slot_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                available_slots.append(slot_time)
                
                # Stop when we have enough slots
                if len(available_slots) >= 20:
                    break
            
            if len(available_slots) >= 20:
                break
        
        return available_slots[:20]  # Return first 20 available slots
    
    def get_busy_times(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get busy times from calendar (requires authentication)"""
        
        try:
            self._check_authentication()
        except Exception:
            # Return empty if not authenticated
            return []
        
        try:
            freebusy_query = {
                'timeMin': start_date.isoformat() + 'Z',
                'timeMax': end_date.isoformat() + 'Z',
                'items': [{'id': 'primary'}]
            }
            
            freebusy_result = self.service.freebusy().query(body=freebusy_query).execute()
            busy_times = freebusy_result.get('calendars', {}).get('primary', {}).get('busy', [])
            
            return busy_times
            
        except Exception as e:
            print(f"Error fetching busy times: {e}")
            return []
    
    def test_connection(self) -> Dict:
        """Test the Google Calendar connection"""
        
        if not self.authenticated:
            return {
                'status': 'failed',
                'message': 'Not authenticated. Run auth_setup.py first.',
                'authenticated': False
            }
        
        try:
            # Try to get calendar list
            calendar_list = self.service.calendarList().list().execute()
            primary_calendar = None
            
            for calendar in calendar_list.get('items', []):
                if calendar.get('primary'):
                    primary_calendar = calendar
                    break
            
            return {
                'status': 'success',
                'message': 'Google Calendar connection successful',
                'authenticated': True,
                'calendar_count': len(calendar_list.get('items', [])),
                'primary_calendar': primary_calendar.get('summary', 'Unknown') if primary_calendar else 'None'
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Connection test failed: {str(e)}',
                'authenticated': self.authenticated
            }