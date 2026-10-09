import smtplib
from email.mime.text import MIMEText
import sqlite3
from datetime import datetime

class EmailAlert:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587,
                 email="eminet666@gmail.com", password="qqwu ujeo ledf kbhd"):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password

    def send(self, subject, body, to_email):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.email
        msg["To"] = to_email

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)

class AlertManager:
    def __init__(self, db_name="flights.db"):
        self.conn = sqlite3.connect(db_name)
        self.email_alert = EmailAlert()

    def add_alert(self, origin, destination, max_price, email):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (origin, destination, max_price, email)
            VALUES (?, ?, ?, ?)
        ''', (origin, destination, max_price, email))
        self.conn.commit()

    def check_alerts(self, new_flights):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM alerts WHERE active = 1")
        alerts = cursor.fetchall()

        for alert in alerts:
            alert_id, origin, destination, max_price, min_price, email, _, _ = alert
            for flight in new_flights:
                if (flight['origin'] == origin and
                    flight['destination'] == destination and
                    flight['prix'] <= max_price):
                    subject = f"✈️ ALERTE : Vol {origin}→{destination} à {flight['prix']}€ !"
                    body = f"""
                    Vol trouvé :
                    - Compagnie : {flight['compagnie']}
                    - Prix : {flight['prix']} {flight['devise']}
                    - Date : {flight['date']}
                    - Heure : {flight['heure_depart']}
                    """
                    self.email_alert.send(subject, body, email)
        self.conn.close()