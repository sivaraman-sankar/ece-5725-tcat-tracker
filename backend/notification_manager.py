import pandas as pd
import csv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To
from typing import List, Dict
import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL')

class NotificationManager:
    def __init__(self, notification_file: str, rate_limit_minutes: int = 5):
        self.notification_file = notification_file
        self.rate_limit_minutes = rate_limit_minutes
        self.logger = self._setup_logger()
        self.from_email = FROM_EMAIL
        self.sg_client = SendGridAPIClient(SENDGRID_API_KEY)
        self.last_sent = {}  # Dictionary to track last sent time
        print("NOTIFICATION MODULE SET")

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def save_route_notification(self, email: str, stop: str, route: str) -> bool:
        try:
            try:
                df = pd.read_csv(self.notification_file)
            except FileNotFoundError:
                df = pd.DataFrame(columns=['email', 'stop', 'route'])
            
            new_data = {
                'email': email,
                'stop': stop,
                'route': route
            }

            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(self.notification_file, index=False)
            self.logger.info(f"Successfully saved notification for {email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving notification: {str(e)}")
            return False

    def _can_send_notification(self, email: str, stop: str, route: str) -> bool:
        """Check if a notification can be sent based on the rate limit."""
        key = (email, stop, route)
        now = datetime.now()
        if key in self.last_sent:
            last_sent_time = self.last_sent[key]
            if now - last_sent_time < timedelta(minutes=self.rate_limit_minutes):
                self.logger.info(f"Rate limited: Notification for {key} skipped.")
                return False
        self.last_sent[key] = now
        return True

    def _send_notification(self, subscriber: Dict) -> bool:
        try:
            if not self._can_send_notification(
                subscriber['email'], subscriber['stop'], subscriber['route']
            ):
                return False

            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(subscriber['email']),
                subject=f"Route Update: {subscriber['route']}",
                plain_text_content=f"TCAT Route: {subscriber['route']} is coming soon to the Stop: {subscriber['stop']}, please plan accordingly"
            )
            
            response = self.sg_client.send(message)
            if response.status_code == 202:
                self.logger.info(f"Email sent successfully to {subscriber['email']}")
                return True
            else:
                self.logger.error(f"Failed to send email: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False

    def process_notifications(self, vehicles: List[Dict]) -> None:
        try:
            with open(self.notification_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                candidates = []
                
                for subscriber in csv_reader:
                    for vehicle in vehicles:
                        if (subscriber['route'] == vehicle['route_id'] and 
                            subscriber['stop'] == vehicle['incoming_stop']):
                            candidates.append(subscriber)
                
                for candidate in candidates:
                    print(f"candidate: {candidate}")
                    self._send_notification(candidate)
                    
        except Exception as e:
            self.logger.error(f"Error processing notifications: {str(e)}")