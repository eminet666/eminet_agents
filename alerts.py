import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailAlert:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587,
                 email=None, password=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email or os.getenv("SMTP_EMAIL")
        self.password = password or os.getenv("SMTP_PASSWORD")

    def send(self, subject, body, to_email):
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            # Connexion avec gestion des erreurs
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Sécurité obligatoire pour Gmail
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            print(f"✅ Email envoyé à {to_email}")
            return True
        except smtplib.SMTPAuthenticationError:
            print("❌ Erreur: Authentification échouée (vérifie ton App Password)")
            return False
        except smtplib.SMTPServerDisconnected:
            print("❌ Erreur: Connexion fermée par le serveur (Gmail bloque peut-être l'IP)")
            return False
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return False