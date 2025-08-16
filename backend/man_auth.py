import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import webbrowser
from urllib.parse import urlparse, parse_qs

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    creds = None
    
    # Check if token file exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Setting up Google Calendar authentication...")
            
            # Set up the flow
            flow = Flow.from_client_secrets_file(
                'credentials.json', 
                SCOPES,
                redirect_uri='http://localhost:8080'
            )
            
            # Get the authorization URL
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print(f"\n🔗 Please visit this URL to authorize the application:")
            print(f"{auth_url}")
            print(f"\n📋 After authorization, you'll be redirected to localhost:8080")
            print(f"📋 Copy the ENTIRE URL from your browser address bar and paste it here")
            print(f"📋 (It will look like: http://localhost:8080/?code=xxx&scope=xxx)")
            
            # Open the URL automatically
            try:
                webbrowser.open(auth_url)
                print(f"\n🌐 Opening browser automatically...")
            except:
                print(f"\n⚠️  Could not open browser automatically")
            
            # Get the authorization response from user
            authorization_response = input(f"\n🔗 Paste the full redirect URL here: ").strip()
            
            # Complete the flow
            try:
                flow.fetch_token(authorization_response=authorization_response)
                creds = flow.credentials
                
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
                
                print(f"✅ Authentication successful! Token saved to token.pickle")
                
            except Exception as e:
                print(f"❌ Error during authentication: {e}")
                print(f"💡 Make sure you copied the ENTIRE URL including the code parameter")
                return None
    
    return creds

if __name__ == "__main__":
    creds = get_credentials()
    if creds:
        print(f"🎉 Google Calendar authentication setup complete!")
        print(f"📁 Token file created: token.pickle")
        print(f"🚀 You can now run: python main.py")
    else:
        print(f"❌ Authentication failed. Please try again.")