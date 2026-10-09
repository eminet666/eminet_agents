from dotenv import load_dotenv
load_dotenv()

import os, requests
from datetime import datetime, timedelta
from agents.llm_agent import LLMAgent

class TravelpayoutsAPI:
    BASE_URL = "https://api.travelpayouts.com/v1"

    def __init__(self):
        self.token = os.getenv("TRAVELPAYOUTS_TOKEN")
        if not self.token:
            raise ValueError("TRAVELPAYOUTS_TOKEN manquant dans .env")
        self.session = requests.Session()

    def search_flights(self, origin, destination, depart_date, return_date=None, **kwargs):
        # Convertir les dates au format YYYY-MM-DD si ce sont des objets date
        if isinstance(depart_date, datetime):
            depart_date = depart_date.strftime("%Y-%m-%d")
        if return_date and isinstance(return_date, datetime):
            return_date = return_date.strftime("%Y-%m-%d")

        params = {
            "origin": origin,
            "destination": destination,
            "depart_date": depart_date,
            "return_date": return_date,
            "adults": kwargs.get("adults", 1),
            "currency": kwargs.get("currency", "EUR"),
            "limit": kwargs.get("limit", 20),
            "token": self.token,
        }

        # Travelpayouts n'a PAS de paramètre 'direct' dans /prices/cheap
        # On filtrera les résultats après
        response = self.session.get(
            f"{self.BASE_URL}/prices/cheap",
            params=params,
            timeout=30
        )

        # DEBUG: Afficher l'URL et la réponse
        print(f"\n🔍 DEBUG API Travelpayouts:")
        print(f"URL: {response.url}")
        print(f"Status: {response.status_code}")
        try:
            response_json = response.json()
            print(f"Réponse: {response_json}\n")
            return response_json
        except Exception as e:
            print(f"Erreur parsing JSON: {e}")
            response.raise_for_status()

class FlightSearcher:
    def __init__(self):
        self.api = TravelpayoutsAPI()
        self.agent = LLMAgent()

    def search(self, origin, destination, date, return_date=None, **kwargs):
        api_response = self.api.search_flights(origin, destination, date, return_date, **kwargs)

        if not api_response or not api_response.get("data"):
            print("⚠️ Aucune donnée")
            return []

        # 🟢 PARSING DIRECT (sans LLM)
        flights = []
        data = api_response["data"]

        for dest, flights_data in data.items():
            for flight_id, flight_info in flights_data.items():
                flight = {
                    "compagnie": flight_info.get("airline", ""),
                    "prix": float(flight_info.get("price", 0)),
                    "devise": api_response.get("currency", "EUR"),
                    "escales": 0,  # Travelpayouts ne donne pas cette info
                    "heure_depart": flight_info.get("departure_at", "").split("T")[0],
                    "heure_arrivee": flight_info.get("return_at", "").split("T")[0] if return_date else "",
                    "duree": f"{flight_info.get('duration_to', 0)} min",
                    "date": date,
                    "origin": origin,
                    "destination": dest,
                    "numero_vol": flight_info.get("flight_number", "")
                }
                flights.append(flight)

        # Filtrer les vols directs si demandé
        if kwargs.get("direct", False):
            # Travelpayouts ne donne pas escales, on suppose direct
            pass

        return flights

    def search_natural(self, query):
        criteria = self.agent.interpret_query(query)
        print(f"🔍 Critères interprétés: {criteria}")  # DEBUG

        if criteria.get("type") != "vol":
            print("⚠️ Requête non reconnue comme un vol")
            return []

        c = criteria.get("critères", {})
        origin = c.get("depart")
        destination = c.get("arrivee")

        if not origin or not destination:
            print("⚠️ Origin ou destination manquant")
            return []

        # Gérer les dates spéciales
        date = c.get("date")
        if date and isinstance(date, str):
            if date.lower() == "aujourd'hui":
                date = datetime.now().strftime("%Y-%m-%d")
            elif date.lower() == "demain":
                date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        return_date = c.get("date_retour")
        if return_date and isinstance(return_date, str):
            if return_date.lower() == "aujourd'hui":
                return_date = datetime.now().strftime("%Y-%m-%d")
            elif return_date.lower() == "demain":
                return_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        return self.search(
            origin=origin,
            destination=destination,
            date=date,
            return_date=return_date,
            adults=c.get("adultes", 1),
            currency=c.get("devise", "EUR"),
            direct=c.get("escales_max", 1) == 0  # True si escales_max=0
        )

    def get_cheapest_flights(self, origin, destination, date, return_date=None, limit=5, direct=False):
        flights = self.search(origin, destination, date, return_date, limit=limit*2, direct=direct)
        return sorted(flights, key=lambda x: x["prix"])[:limit]  # Trie et limite        