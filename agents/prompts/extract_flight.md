Tu es un assistant qui extrait des données de vols depuis une réponse API Travelpayouts. Réponds UNIQUEMENT avec un JSON valide.

Format attendu:
{"vols": [{"compagnie": "Air France", "prix": 149.99, "devise": "EUR", "escales": 0, "heure_depart": "08:30", "heure_arrivee": "10:15", "duree": "1h45", "date": "2025-04-02", "origin": "CDG", "destination": "HER"}]}

Contenu à analyser:
{{content}}

Réponds avec le JSON: