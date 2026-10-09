import json
import os
from datetime import datetime, timedelta
from vols import FlightSearcher
from alerts import AlertManager, EmailAlert
from database import FlightDatabase

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def format_flight(flight):
    return f"{flight['origin']}→{flight['destination']} [{flight['compagnie']}] {flight['heure_depart']} {flight['prix']}{flight['devise']}"

def main():
    # Charger la config
    config = load_config()
    searcher = FlightSearcher()
    db = FlightDatabase()
    email_alert = EmailAlert(
        smtp_server=config["email"]["smtp_server"],
        smtp_port=config["email"]["smtp_port"],
        email=os.getenv("SMTP_EMAIL"),
        password=os.getenv("SMTP_PASSWORD")
    )

    # Exécuter les recherches
    all_results = []
    for search in config["searches"]:
        date = search["date"]
        flights = searcher.search(
            origin=search["origin"],
            destination=search["destination"],
            date=date,
            limit=3
        )
        for flight in flights:
            db.save_flight(flight)
            all_results.append(format_flight(flight))

    # Envoyer les résultats par email
    if all_results:
        subject = f"📊 Résultats vols - {datetime.now().strftime('%Y-%m-%d')}"
        body = "\n".join(all_results)
        email_alert.send(subject, body, config["email"]["to"])
        print("✅ Email envoyé avec les résultats")
    else:
        print("⚠️ Aucun vol trouvé")

if __name__ == "__main__":
    main()