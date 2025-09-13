import os, pandas as pd
from pathlib import Path

DAILY = Path("data/processed/prix_carburants_clean.csv")
HIST_DIR = Path("data/processed/history")
HIST_CSV = HIST_DIR / "prix_carburants_history.csv"
HIST_PARQ = HIST_DIR / "prix_carburants_history.parquet"

def main():
    if not DAILY.exists():
        raise FileNotFoundError(f"Fichier quotidien absent: {DAILY}. Lance d'abord clean_data.py")
    HIST_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DAILY, parse_dates=["date"])
    # Clés d’unicité par jour/station/carburant
    key = ["jour", "id_station", "carburant"]

    if HIST_CSV.exists():
        hist = pd.read_csv(HIST_CSV, parse_dates=["date"])
        combo = pd.concat([hist, df], ignore_index=True)
        combo = (combo
                 .sort_values("date")
                 .drop_duplicates(subset=key, keep="last"))
    else:
        combo = df.copy()

    combo.to_csv(HIST_CSV, index=False, encoding="utf-8")
    try:
        combo.to_parquet(HIST_PARQ, index=False)
    except Exception:
        pass

    # Agrégat utile pour Power BI (moyenne par jour/carburant)
    agg = (combo.groupby(["jour","carburant"], as_index=False)["prix"].mean())
    agg.to_csv(HIST_DIR / "moyennes_journalieres.csv", index=False, encoding="utf-8")

    print(f"Historique: {len(combo)} lignes -> {HIST_CSV}")
    print("Agrégat quotidien -> data/processed/history/moyennes_journalieres.csv")

if __name__ == "__main__":
    main()