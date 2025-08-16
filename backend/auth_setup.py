#!/usr/bin/env python3
"""
Google Calendar Authentication Setup Script

Run this script once to authenticate and generate the token.json file.
After this, your FastAPI server will work without interactive prompts.
"""

import os
import sys
import pickle

# IMPORTANT: Allow HTTP for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Add the current directory to Python path to import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    print("✅ Google libraries imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Google libraries: {e}")
    print("Please install required packages:")
    print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

try:
    from app.config import settings
    print("✅ App config imported successfully")
except ImportError as e:
    print(f"⚠️  Could not import app.config: {e}")
    print("Using default file names...")
    
    # Fallback to default settings
    class DefaultSettings:
        GOOGLE_CALENDAR_CREDENTIALS_FILE = "credentials.json"
        GOOGLE_CALENDAR_TOKEN_FILE = "token.json"
    
    settings = DefaultSettings()

def setup_google_calendar_auth():
    """Setup Google Calendar authentication and save token"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    
    print(f"Looking for token file: {settings.GOOGLE_CALENDAR_TOKEN_FILE}")
    print(f"Looking for credentials file: {settings.GOOGLE_CALENDAR_CREDENTIALS_FILE}")
    
    # Check if token file already exists
    if os.path.exists(settings.GOOGLE_CALENDAR_TOKEN_FILE):
        print("Found existing token file, loading...")
        try:
            with open(settings.GOOGLE_CALENDAR_TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
            print("✅ Token file loaded successfully")
        except Exception as e:
            print(f"⚠️  Error loading token file: {e}")
            creds = None
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            try:
                creds.refresh(Request())
                print("✅ Credentials refreshed successfully")
            except Exception as e:
                print(f"❌ Failed to refresh credentials: {e}")
                creds = None
        
        if not creds:
            print("Setting up new Google Calendar authentication...")
            print("=" * 60)
            
            # Check if credentials file exists
            if not os.path.exists(settings.GOOGLE_CALENDAR_CREDENTIALS_FILE):
                print(f"❌ ERROR: Credentials file not found: {settings.GOOGLE_CALENDAR_CREDENTIALS_FILE}")
                print("\nPlease follow these steps:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable Google Calendar API")
                print("4. Create OAuth2 credentials (Desktop application)")
                print("5. Download the JSON file and save it as 'credentials.json' in this directory")
                print(f"6. Current directory: {os.getcwd()}")
                return False
            
            print(f"✅ Found credentials file: {settings.GOOGLE_CALENDAR_CREDENTIALS_FILE}")
            
            try:
                flow = Flow.from_client_secrets_file(
                    settings.GOOGLE_CALENDAR_CREDENTIALS_FILE, SCOPES)
                
                # Use localhost for better user experience
                flow.redirect_uri = 'http://localhost:8080'
                
                auth_url, _ = flow.authorization_url(prompt='consent')
                
                print(f"\n🔗 Please visit this URL to authorize the application:")
                print(f"{auth_url}")
                print("\n📋 After authorization, you'll be redirected to localhost:8080")
                print("💡 Copy the ENTIRE URL from your browser address bar after authorization")
                print("=" * 60)
                
                # Get the authorization response URL
                auth_response = input('\n📎 Paste the full redirect URL here: ')
                
                if not auth_response.strip():
                    print("❌ No URL provided. Exiting...")
                    return False
                
                flow.fetch_token(authorization_response=auth_response)
                creds = flow.credentials
                print("\n✅ Authentication successful!")
                
            except Exception as e:
                print(f"\n❌ Authentication failed: {e}")
                print("\nPlease try again and make sure to:")
                print("1. Copy the complete URL from your browser")
                print("2. Add http://localhost:8080 as authorized redirect URI in Google Cloud Console")
                return False
        
        # Save the credentials for the next run
        try:
            with open(settings.GOOGLE_CALENDAR_TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            print(f"✅ Token saved to: {settings.GOOGLE_CALENDAR_TOKEN_FILE}")
        except Exception as e:
            print(f"❌ Failed to save token: {e}")
            return False
    
    else:
        print("✅ Existing valid credentials found!")
    
    print(f"\n🎉 Google Calendar authentication setup complete!")
    print(f"📝 Your FastAPI server should now work without authentication prompts.")
    return True

if __name__ == "__main__":
    print("🔐 Google Calendar Authentication Setup")
    print("=" * 50)
    
    try:
        success = setup_google_calendar_auth()
        if success:
            print("\n🚀 You can now start your server with:")
            print("   python main.py")
        else:
            print("\n💥 Setup failed. Please check the instructions above.")
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup cancelled by user.")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()