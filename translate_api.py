import requests
import json

RAPID_API_KEY = "6e3c84602amsh087a22037527a53p1fdd2bjsnc3793c5d472d"
RAPID_API_HOST = "rapid-translate-multi-traduction.p.rapidapi.com"
RAPID_API_URL = f"https://{RAPID_API_HOST}/t"

def translate_text(titles: list) -> list:
    """Translates a list of Spanish titles to English using a mock RapidAPI endpoint."""
    if not titles:
        return []

    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": RAPID_API_HOST,
        "Content-Type": "application/json"
    }

    payload = {
        "from": "es",
        "to": "en",
        "q": titles
    }

    print("\nTranslating all titles in bulk...")
    try:
        response = requests.post(RAPID_API_URL, headers=headers, data=json.dumps(payload), timeout=15)
        response.raise_for_status()
        
        translated_texts = response.json()
        print("Translation complete")

        return translated_texts
        
    except requests.exceptions.RequestException as e:
        print(f"Translation failed: {e}")
        return titles