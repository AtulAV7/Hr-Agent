import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from typing import Dict

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = settings.EMAIL_USER
        self.email_password = settings.EMAIL_PASSWORD
    
    def send_interview_confirmation(self, recipient_email: str, subject: str, body: str) -> Dict:
        """Send interview confirmation email"""
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_user, recipient_email, text)
            server.quit()
            
            return {'status': 'sent', 'message': 'Email sent successfully'}
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return {'status': 'failed', 'error': str(e)}