import os
import requests
import base64

class EmailAlert:
    def __init__(self):
        self.api_key = os.getenv("MAILJET_API_KEY")
        self.api_secret = os.getenv("MAILJET_API_SECRET")
        self.from_email = os.getenv("MAILJET_FROM_EMAIL", "ton_email@domaine.com")
        if not self.api_key or not self.api_secret:
            raise ValueError("MAILJET_API_KEY ou MAILJET_API_SECRET manquant")

    def send(self, subject, body, to_email):
        auth = (self.api_key, self.api_secret)
        url = "https://api.mailjet.com/v3.1/send"

        payload = {
            "Messages": [{
                "From": {"Email": self.from_email, "Name": "Flight Alerts"},
                "To": [{"Email": to_email}],
                "Subject": subject,
                "TextPart": body
            }]
        }

        try:
            response = requests.post(
                url,
                auth=auth,
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ Email envoyé à {to_email}")
                return True
            else:
                print(f"❌ Erreur Mailjet: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False