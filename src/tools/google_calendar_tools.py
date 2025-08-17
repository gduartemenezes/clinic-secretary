"""
Google Calendar tools for appointment scheduling.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GoogleCalendarTools:
    """Google Calendar tools class for calendar operations."""
    
    def __init__(self):
        """Initialize Google Calendar tools."""
        self.service = None
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API.
        
        Authentication priority (most secure to least secure):
        1. GOOGLE_SERVICE_ACCOUNT_JSON - Service account credentials as JSON string (production)
        2. GOOGLE_SERVICE_ACCOUNT_FILE - Service account credentials file path
        3. GOOGLE_ACCESS_TOKEN - Direct access token
        4. GOOGLE_CREDENTIALS_FILE - OAuth2 credentials file (development)
        """
        try:
            # Option 1: Service account JSON as environment variable (most secure, production-ready)
            if os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"):
                import json
                service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
                credentials = service_account.Credentials.from_service_account_info(
                    service_account_info,
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
            # Option 2: Service account file path
            elif os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"):
                credentials = service_account.Credentials.from_service_account_file(
                    os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"),
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
            # Option 3: Direct access token (simple but less secure)
            elif os.getenv("GOOGLE_ACCESS_TOKEN"):
                credentials = Credentials(
                    token=os.getenv("GOOGLE_ACCESS_TOKEN"),
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
            # Option 4: OAuth2 credentials file (development fallback)
            else:
                credentials = Credentials.from_authorized_user_file(
                    os.getenv("GOOGLE_CREDENTIALS_FILE", "token.json"),
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
            
            self.service = build('calendar', 'v3', credentials=credentials)
        except Exception as e:
            print(f"Failed to authenticate with Google Calendar: {e}")
            self.service = None
    
    def list_events(
        self,
        calendar_id: Optional[str] = None,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """List events from Google Calendar."""
        if not self.service:
            return []
        
        calendar_id = calendar_id or self.calendar_id
        
        # Set default time range if not provided
        if not time_min:
            time_min = datetime.utcnow()
        if not time_max:
            time_max = time_min + timedelta(days=7)
        
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return [
                {
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'attendees': [
                        attendee.get('email') 
                        for attendee in event.get('attendees', [])
                    ]
                }
                for event in events
            ]
        except Exception as e:
            print(f"Failed to list events: {e}")
            return []
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        calendar_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new event in Google Calendar."""
        if not self.service:
            return None
        
        calendar_id = calendar_id or self.calendar_id
        
        event = {
            'summary': summary,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        try:
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            return {
                'id': event['id'],
                'summary': event['summary'],
                'start': event['start']['dateTime'],
                'end': event['end']['dateTime'],
                'htmlLink': event['htmlLink']
            }
        except Exception as e:
            print(f"Failed to create event: {e}")
            return None
    
    def check_availability(
        self,
        start_time: datetime,
        end_time: datetime,
        calendar_id: Optional[str] = None
    ) -> bool:
        """Check if a time slot is available."""
        events = self.list_events(
            calendar_id=calendar_id,
            time_min=start_time,
            time_max=end_time
        )
        
        # If no events found, the slot is available
        return len(events) == 0
    
    def delete_event(
        self,
        event_id: str,
        calendar_id: Optional[str] = None
    ) -> bool:
        """Delete an event from Google Calendar."""
        if not self.service:
            return False
        
        calendar_id = calendar_id or self.calendar_id
        
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f"Failed to delete event: {e}")
            return False
