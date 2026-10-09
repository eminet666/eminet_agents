import json, os
from pathlib import Path
from typing import Any, Dict
import requests

class LLMAgent:
    def __init__(self, api_key=None, model="mistral-tiny"):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY manquant dans .env")
        self.model = model
        self.base_url = "https://api.mistral.ai/v1"

        self.prompts_dir = Path(__file__).parent / "prompts"
        self._load_prompts()

    def _load_prompts(self):
        self.prompts = {}
        for p in self.prompts_dir.glob("*.md"):
            with open(p, "r", encoding="utf-8") as f:
                self.prompts[p.stem] = f.read()

    def _call_llm(self, messages, temperature=0.0):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        response = requests.post(
            f"{self.base_url}/chat/completions",  # <-- CORRECTION ICI
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _extract_json(self, text):
        import re
        # Nettoyer le texte : supprimer les commentaires et backticks
        text = text.strip()
        text = re.sub(r'```(json)?', '', text)  # Supprimer ```json et ```
        text = re.sub(r'//.*', '', text)        # Supprimer les commentaires //
        text = re.sub(r'\n', ' ', text)          # Supprimer les sauts de ligne

        # Extraire le premier bloc JSON valide
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Essayer de parser tout le texte
        try:
            return json.loads(text)
        except Exception as e:
            raise ValueError(f"Échec parsing JSON. Texte: {text[:300]}... (Erreur: {e})")

    def extract_product(self, html):
        prompt = self.prompts["extract_product"].replace("{{content}}", html)
        return self._extract_json(self._call_llm([{"role": "user", "content": prompt}]))

    def extract_flight(self, api_response):
        if isinstance(api_response, dict):
            content = json.dumps(api_response, ensure_ascii=False)
        else:
            content = api_response
        prompt = self.prompts["extract_flight"].replace("{{content}}", content)
        return self._extract_json(self._call_llm([{"role": "user", "content": prompt}]))        

    def interpret_query(self, query):
        prompt = self.prompts["interpret_query"].replace("{{query}}", query)
        return self._extract_json(self._call_llm([{"role": "user", "content": prompt}]))

def create_agent(api_key=None, model="mistral-tiny"):
    return LLMAgent(api_key=api_key, model=model)