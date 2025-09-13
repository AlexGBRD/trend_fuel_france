# Nettoyage robuste + garde-fous + enrichissements
import os, json
import pandas as pd
from dateutil import parser
import numpy as np

RAW_DIR = "data/raw"
OUT_CSV = "data/processed/prix_carburants_clean.csv"

# Normalisation des libellés
FUEL_ALIASES = {
    "GAZOLE": "Gazole", "GASOIL": "Gazole", "DIESEL": "Gazole",
    "SP95": "SP95", "SP-95": "SP95",
    "SP98": "SP98", "SP-98": "SP98",
    "E10": "E10", "E-10": "E10",
    "E85": "E85", "E-85": "E85",
    "GPL": "GPLc", "GPLC": "GPLc", "GPL-C": "GPLc",
}

# Bornes (euros/litre) – à ajuster au besoin
FUEL_BOUNDS = {
    "Gazole": (1.10, 2.80),
    "SP95":   (1.30, 2.90),
    "SP98":   (1.40, 3.10),
    "E10":    (1.20, 2.70),
    "E85":    (0.45, 1.50),
    "GPLc":   (0.60, 1.70),
}

FR_BBOX = {"lon_min": -5.8, "lon_max": 10.5, "lat_min": 41.0, "lat_max": 51.5}

def load_latest_json():
    files = sorted(f for f in os.listdir(RAW_DIR)
                   if f.startswith("prix_carburants_") and f.endswith(".json"))
    if not files:
        raise FileNotFoundError("Aucun JSON trouvé. Lancez d'abord: python src/download_data.py")
    return os.path.join(RAW_DIR, files[-1])

def first_non_null(d, *keys):
    for k in keys:
        v = d.get(k)
        if v is not None and v != "":
            return v
    return None

def normalize_fuel_label(x):
    if not x:
        return None
    s = str(x).strip().upper()
    return FUEL_ALIASES.get(s, x)  # garde le libellé d’origine si inconnu (ex: additivé)

def infer_carburant(fields):
    cand = first_non_null(
        fields,
        "nom", "carburant", "produit", "prix_nom", "libelle",
        "nom_carburant", "type", "code", "fuel", "fuel_name"
    )
    lab = normalize_fuel_label(cand)
    if lab:
        return lab
    idc = first_non_null(fields, "idcarburant", "carburant_id", "code_carburant")
    id_map = {"1":"SP95","2":"Gazole","3":"SP98","4":"E85","5":"GPLc","6":"E10"}
    if idc is not None:
        return id_map.get(str(idc), None)
    return None

def parse_price(x):
    if x is None:
        return None
    s = str(x).strip().replace("€", "").replace(" ", "").replace(",", ".")
    try:
        v = float(s)
    except Exception:
        return None
    # Corrections d’unité éventuelles (centimes)
    # Si > 10 et < 1000, on considère que c’est en centimes -> /100
    if v > 10 and v < 1000:
        v = v / 100.0
    return v

def infer_departement(cp):
    s = str(cp) if pd.notna(cp) else ""
    return s[:2] if len(s) >= 2 else None

def in_france(lat, lon):
    if pd.isna(lat) or pd.isna(lon):
        return True  # on tolère NaN (juste pas cartographiable)
    return (FR_BBOX["lat_min"] <= lat <= FR_BBOX["lat_max"] and
            FR_BBOX["lon_min"] <= lon <= FR_BBOX["lon_max"])

def extract_fields(rec):
    if isinstance(rec, dict) and "fields" in rec:
        fields = rec.get("fields", {})
        coords = rec.get("geometry", {}).get("coordinates", [None, None])
        lon, lat = (coords[0], coords[1]) if isinstance(coords, list) and len(coords) == 2 else (None, None)
        recid = rec.get("recordid")
    else:
        fields = rec if isinstance(rec, dict) else {}
        g = fields.get("geometry") or {}
        coords = g.get("coordinates") if isinstance(g, dict) else None
        if isinstance(coords, list) and len(coords) == 2:
            lon, lat = coords[0], coords[1]
        else:
            lon = fields.get("longitude") or fields.get("x")
            lat = fields.get("latitude")  or fields.get("y")
        recid = fields.get("recordid") or fields.get("id")

    date_raw = first_non_null(fields, "maj", "date", "date_maj", "prix_maj", "horodatage")
    try:
        date = parser.parse(date_raw) if date_raw else None
    except Exception:
        date = None

    prix = parse_price(first_non_null(fields, "prix", "valeur", "prix_valeur"))

    row = {
        "id": recid,
        "date": date,
        "cp": first_non_null(fields, "cp", "code_postal", "codepostal"),
        "commune": first_non_null(fields, "commune", "ville"),
        "adresse": first_non_null(fields, "adresse", "adr"),
        "carburant": infer_carburant(fields),
        "prix": prix,
        "latitude": lat,
        "longitude": lon,
        "id_station": first_non_null(fields, "id", "id_station", "identifiant"),
    }
    return row

def normalize(records):
    rows = [extract_fields(r) for r in records]
    df = pd.DataFrame(rows)

    # Types
    df["date"] = pd.to_datetime(df["date"], utc=True).dt.tz_convert("Europe/Paris")
    df["jour"] = df["date"].dt.date

    n0 = len(df)

    # Prix valides
    df = df[df["prix"].notna() & (df["prix"] > 0)]
    n_after_price = len(df)

    # France métropolitaine approx (tolère NaN lat/lon)
    df = df[df.apply(lambda r: in_france(r["latitude"], r["longitude"]), axis=1)]
    n_after_geo = len(df)

    # Normalise carburant, supprime les lignes sans carburant pour les analyses par type
    df = df[df["carburant"].notna()]
    n_after_fuel = len(df)

    # Dédoublonnage: on garde la dernière mise à jour par (station, carburant, jour)
    df = (df.sort_values("date")
            .drop_duplicates(subset=["id_station", "carburant", "jour"], keep="last"))

    # Filtre par bornes réalistes par carburant
    def in_bounds(row):
        bounds = FUEL_BOUNDS.get(row["carburant"])
        if not bounds:
            return True
        lo, hi = bounds
        return (row["prix"] >= lo) and (row["prix"] <= hi)

    df["__keep"] = df.apply(in_bounds, axis=1)
    n_before_bounds = len(df)
    df = df[df["__keep"]].drop(columns="__keep")
    n_after_bounds = len(df)

    # Arrondis & enrichissements
    df["prix"] = df["prix"].round(3)
    df["departement"] = df["cp"].apply(infer_departement)

    print(
        f"Nettoyage: brut={n0} -> prix_ok={n_after_price} -> geo_ok={n_after_geo} "
        f"-> fuel_ok={n_after_fuel} -> bounds_ok={n_after_bounds} "
        f"(éliminé par bornes={n_before_bounds - n_after_bounds})"
    )

    return df

def main():
    os.makedirs("data/processed", exist_ok=True)
    json_path = load_latest_json()
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)
    df = normalize(records)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"OK: {len(df)} lignes -> {OUT_CSV}")

if __name__ == "__main__":
    main()
