# Télécharge tout le flux du jour via le service "download" (pas de limite 10k)
import os, json, datetime as dt, requests

DOWNLOAD_URL = "https://data.economie.gouv.fr/api/records/1.0/download/"
DATASET = "prix-carburants-quotidien"

def fetch_all_records():
    params = {
        "dataset": DATASET,
        "format": "json",
        "timezone": "Europe/Paris",
    }
    resp = requests.get(DOWNLOAD_URL, params=params, timeout=180)
    resp.raise_for_status()

    # Tente: JSON standard -> dict ou liste
    try:
        payload = resp.json()
    except ValueError:
        # Fallback: NDJSON (ligne par ligne)
        lines = [json.loads(line) for line in resp.text.splitlines() if line.strip()]
        return lines

    if isinstance(payload, dict) and "records" in payload:
        return payload["records"]
    if isinstance(payload, list):
        return payload

    # Dernier recours: parser ligne à ligne
    try:
        lines = [json.loads(line) for line in resp.text.splitlines() if line.strip()]
        return lines
    except Exception as e:
        raise RuntimeError("Format inattendu du service 'download'.") from e

def main():
    os.makedirs("data/raw", exist_ok=True)
    out = f"data/raw/prix_carburants_{dt.datetime.now().strftime('%Y%m%d')}.json"
    recs = fetch_all_records()
    with open(out, "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(recs)} enregistrements -> {out}")

if __name__ == "__main__":
    main()