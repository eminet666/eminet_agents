import json
import os
from datetime import datetime, timedelta
from vols import FlightSearcher
from alerts import EmailAlert
from database import FlightDatabase

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def format_flight(flight):
    return f"{flight['origin']}→{flight['destination']} [{flight['compagnie']}] {flight['heure_depart']} {flight['prix']}{flight['devise']}"

def main():
    config = load_config()
    searcher = FlightSearcher()
    db = FlightDatabase()
    email_alert = EmailAlert()  # <-- CORRIGÉ ICI

    all_results = []
    for search in config["searches"]:
        date = search["date"]
        return_date = search.get("return_date")
        direct = search.get("direct", False)

        flights = searcher.search(
            origin=search["origin"],
            destination=search["destination"],
            date=date,
            return_date=return_date,
            limit=3,
            direct=direct
        )

        for flight in flights:
            db.save_flight(flight)
            all_results.append(format_flight(flight))

    if all_results:
        subject = f"📊 Résultats vols - {datetime.now().strftime('%Y-%m-%d')}"
        body = "Voici les résultats des recherches :\n\n" + "\n".join(all_results)
        email_alert.send(subject, body, config["email"]["to"])
        print("✅ Email envoyé avec les résultats")
    else:
        print("⚠️ Aucun vol trouvé")

if __name__ == "__main__":
    main()