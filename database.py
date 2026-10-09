import sqlite3
from datetime import datetime

class FlightDatabase:
    def __init__(self, db_name="flights.db"):
        self.conn = sqlite3.connect(db_name)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin TEXT,
                destination TEXT,
                date TEXT,
                company TEXT,
                price REAL,
                currency TEXT,
                flight_number TEXT,
                departure_time TEXT,
                duration TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin TEXT,
                destination TEXT,
                max_price REAL,
                min_price REAL,
                email TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_flight(self, flight):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO flights (origin, destination, date, company, price, currency, flight_number, departure_time, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            flight['origin'],
            flight['destination'],
            flight['date'],
            flight['compagnie'],
            flight['prix'],
            flight['devise'],
            flight['numero_vol'],
            flight['heure_depart'],
            flight['duree']
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_flights(self, origin=None, destination=None, limit=10):
        cursor = self.conn.cursor()
        query = "SELECT * FROM flights"
        params = []
        if origin:
            query += " WHERE origin = ?"
            params.append(origin)
            if destination:
                query += " AND destination = ?"
                params.append(destination)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        return cursor.fetchall()

    def close(self):
        self.conn.close()