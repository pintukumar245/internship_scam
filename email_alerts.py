"""
Email Alerts System
Sends email notifications to subscribed users about company risk changes
"""

import os
import json
from datetime import datetime
from flask import Flask
from flask_mail import Mail, Message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
ALERTS_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "email_alerts.json")
ALERT_HISTORY_PATH = os.path.join(os.path.dirname(__file__), "data", "alert_history.json")

# Ensure files exist
os.makedirs(os.path.dirname(ALERTS_DB_PATH), exist_ok=True)
for path in [ALERTS_DB_PATH, ALERT_HISTORY_PATH]:
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump({} if path == ALERTS_DB_PATH else [], f)

class EmailAlertSystem:
    """Manages email alerts for company risk changes."""
    
    def __init__(self):
        self.mail = None
        self.smtp_configured = False
        self.setup_smtp()
    
    def setup_smtp(self):
        """Configure SMTP settings from environment."""
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        
        if self.sender_email and self.sender_password:
            self.smtp_configured = True
            print("[OK] SMTP configured successfully")
        else:
            print("[WARNING] SMTP not configured. Email alerts disabled.")
            print("   Add SENDER_EMAIL and SENDER_PASSWORD to .env file")
    
    def configure_flask_mail(self, app):
        """Configure Flask-Mail (alternative method)."""
        app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
        app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
        app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", True)
        app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
        app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
        
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            self.mail = Mail(app)
            self.smtp_configured = True
            print("[OK] Flask-Mail configured")
    
    def subscribe(self, email, companies):
        """Subscribe user to email alerts for specific companies."""
        try:
            with open(ALERTS_DB_PATH, 'r+') as f:
                alerts_db = json.load(f)
                
                # Validate email
                if '@' not in email:
                    return {'success': False, 'message': 'Invalid email address'}
                
                # Add/update subscription
                alerts_db[email.lower()] = {
                    'companies': companies if isinstance(companies, list) else [companies],
                    'subscribed_date': datetime.now().isoformat(),
                    'status': 'active'
                }
                
                f.seek(0)
                json.dump(alerts_db, f, indent=2)
                f.truncate()
            
            print(f"[OK] {email} subscribed to alerts for {len(companies)} companies")
            return {'success': True, 'message': 'Subscription successful'}
        
        except Exception as e:
            print(f"[ERROR] Subscription error: {e}")
            return {'success': False, 'message': str(e)}
    
    def unsubscribe(self, email):
        """Unsubscribe user from email alerts."""
        try:
            with open(ALERTS_DB_PATH, 'r+') as f:
                alerts_db = json.load(f)
                
                if email.lower() in alerts_db:
                    del alerts_db[email.lower()]
                    
                    f.seek(0)
                    json.dump(alerts_db, f, indent=2)
                    f.truncate()
                    
                    print(f"[OK] {email} unsubscribed")
                    return {'success': True, 'message': 'Unsubscribed successfully'}
                
                return {'success': False, 'message': 'Email not found in subscriptions'}
        
        except Exception as e:
            print(f"[ERROR] Unsubscribe error: {e}")
            return {'success': False, 'message': str(e)}
    
    def send_alert(self, email, company_name, old_score, new_score, details):
        """Send email alert about company risk change."""
        if not self.smtp_configured:
            print("[WARNING] SMTP not configured, skipping email")
            return False
        
        try:
            # Determine if risk increased or decreased
            risk_change = new_score - old_score
            change_icon = "⚠️" if risk_change > 0 else "✓"
            change_text = f"increased to {new_score}%" if risk_change > 0 else f"decreased to {new_score}%"
            
            # Create email content
            subject = f"{change_icon} Risk Alert: {company_name} risk {change_text}"
            
            html_body = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                        .company-name {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                        .score-change {{ font-size: 36px; font-weight: bold; }}
                        .score-high {{ color: #e74c3c; }}
                        .score-low {{ color: #27ae60; }}
                        .details {{ background-color: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                        .footer {{ font-size: 12px; color: #95a5a6; margin-top: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="company-name">{company_name}</div>
                            <p>Risk Score Update</p>
                        </div>
                        
                        <h2>Risk Change Detected</h2>
                        <p>
                            Previous Risk Score: <strong>{old_score}%</strong><br>
                            New Risk Score: <strong class="{'score-high' if new_score > old_score else 'score-low'}">{new_score}%</strong>
                        </p>
                        
                        <div class="details">
                            <h3>Changes Detected:</h3>
                            <ul>
                                {''.join([f'<li>{detail}</li>' for detail in details])}
                            </ul>
                        </div>
                        
                        <h3>Recommendation:</h3>
                        {'<p style="color: #e74c3c;"><strong>⚠️ HIGH RISK - Be very careful before applying!</strong></p>' if new_score > 60 else '<p style="color: #27ae60;"><strong>✓ Relatively Safe - You can consider this company</strong></p>'}
                        
                        <p>
                            <a href="http://localhost:5000/analyze?company_name={company_name.replace(' ', '%20')}" 
                               style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                                View Full Analysis
                            </a>
                        </p>
                        
                        <div class="footer">
                            <p>This is an automated alert from Internship Scam Shield.</p>
                            <p><a href="http://localhost:5000/unsubscribe?email={email}">Unsubscribe from alerts</a></p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
            Risk Alert: {company_name}
            
            Risk Score Change: {old_score}% → {new_score}%
            
            Changes Detected:
            {chr(10).join(['- ' + detail for detail in details])}
            
            View full analysis: http://localhost:5000/analyze?company_name={company_name.replace(' ', '%20')}
            
            ---
            Internship Scam Shield
            """
            
            # Send email using SMTP
            self._send_smtp(email, subject, html_body, text_body)
            
            # Log alert
            self._log_alert(email, company_name, old_score, new_score)
            
            return True
        
        except Exception as e:
            print(f"[ERROR] Error sending alert: {e}")
            return False
    
    def _send_smtp(self, to_email, subject, html_body, text_body):
        """Send email via SMTP."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = to_email
            
            # Attach parts
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, msg.as_string())
            
            print(f"[OK] Alert sent to {to_email}")
        
        except Exception as e:
            print(f"[ERROR] SMTP error: {e}")
    
    def _log_alert(self, email, company_name, old_score, new_score):
        """Log alert in history."""
        try:
            with open(ALERT_HISTORY_PATH, 'r+') as f:
                history = json.load(f)
                
                history.append({
                    'email': email,
                    'company': company_name,
                    'old_score': old_score,
                    'new_score': new_score,
                    'timestamp': datetime.now().isoformat()
                })
                
                f.seek(0)
                json.dump(history, f, indent=2)
                f.truncate()
        
        except Exception as e:
            print(f"[WARNING] Failed to log alert: {e}")
    
    def get_subscriptions(self, email):
        """Get user's email alert subscriptions."""
        try:
            with open(ALERTS_DB_PATH, 'r') as f:
                alerts_db = json.load(f)
                return alerts_db.get(email.lower(), {})
        except:
            return {}
    
    def send_batch_alerts(self, company_name, old_score, new_score, details):
        """Send alerts to all users subscribed to this company."""
        try:
            with open(ALERTS_DB_PATH, 'r') as f:
                alerts_db = json.load(f)
            
            alerts_sent = 0
            for email, subscription in alerts_db.items():
                companies = subscription.get('companies', [])
                
                # Check if user is subscribed to this company
                if any(company.lower() == company_name.lower() for company in companies):
                    if self.send_alert(email, company_name, old_score, new_score, details):
                        alerts_sent += 1
            
            print(f"[OK] Batch alerts sent: {alerts_sent} users notified")
            return alerts_sent
        
        except Exception as e:
            print(f"[ERROR] Batch alert error: {e}")
            return 0


# Global instance
email_alert_system = EmailAlertSystem()

def subscribe_to_alerts(email, companies):
    """Subscribe user to alerts."""
    return email_alert_system.subscribe(email, companies)

def unsubscribe_from_alerts(email):
    """Unsubscribe user from alerts."""
    return email_alert_system.unsubscribe(email)

def send_company_alert(company_name, old_score, new_score, details):
    """Send alert about company risk change."""
    return email_alert_system.send_batch_alerts(company_name, old_score, new_score, details)

def get_user_subscriptions(email):
    """Get user's subscriptions."""
    return email_alert_system.get_subscriptions(email)
