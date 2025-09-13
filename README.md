# Analyse des prix des carburants en France

Projet pédagogique Data Analyst (Python + pandas + Plotly + Power BI) : collecte quotidienne (API publique), nettoyage robuste, analyses et visualisations (boxplots, carte, évolution multi-jours), puis publication GitHub.

## 🔍 Objectifs
- Mettre en place un **pipeline quotidien** : `download` → `clean` → `append_history`.
- Produire des **insights** par carburant (Gazole, SP95, SP98, E10, E85, GPLc).
- Fournir un **dashboard Power BI** avec filtres (carburant, département, date).
- Présenter le projet de manière **pro** (README, structure, licence).

## 🗂️ Arborescence
```
.
├─ src/
│  ├─ download_data.py         # API Opendatasoft: flux du jour
│  ├─ clean_data.py            # nettoyage robuste + bornes par carburant
│  └─ append_history.py        # historisation + moyennes journalières
├─ data/
│  ├─ raw/                     # JSON bruts (non versionnés)
│  └─ processed/
│     ├─ prix_carburants_clean.csv
│     └─ history/
│        ├─ prix_carburants_history.csv
│        └─ moyennes_journalieres.csv
├─ notebooks/
│  └─ 01_eda.ipynb             # EDA + boxplots + évolution
├─ reports/                    # exports CSV/PNG pour README
├─ requirements.txt
├─ environment.yml
├─ .gitignore
├─ LICENSE                     # MIT (code)
└─ README.md                   # ce fichier
```

## ⚙️ Installation
**Option A: Conda (recommandé)**
```bash
conda env create -f environment.yml
conda activate carburants
```

**Option B: venv + pip**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## ▶️ Utilisation quotidienne
```bash
python src/download_data.py      # récupère le flux du jour
python src/clean_data.py         # génère data/processed/prix_carburants_clean.csv
python src/append_history.py     # met à jour l'historique + moyennes journalières
```

## 📊 Analyses & visuels
Ouvre le notebook :
```bash
jupyter notebook notebooks/01_eda.ipynb
```
Tu y trouveras :
- **Boxplot par carburant** (distribution des prix, points extrêmes affichés).
- **Carte** des stations (échantillon) avec prix en couleur.
- **Évolution multi-jours** du prix moyen par carburant (avec MA7).
- **Top 15** stations les moins chères (carburant choisi).
- **Synthèse par département** (moyenne €/L).

## 🧪 Données & licence des données
- **Source** : *Prix des carburants – flux quotidien* via l’API Opendatasoft/data.economie.gouv.fr.
- **Licence des données** : merci de **vérifier la page du jeu de données** et de citer explicitement la licence (souvent “Licence Ouverte / Etalab 2.0”, mais à confirmer sur la page du dataset).  
- **Bonnes pratiques** : ne pas versionner les données brutes/traitées (voir `.gitignore`). Vous pouvez déposer un **petit échantillon** dans `reports/` à des fins de démonstration.

## 🧾 Licence du code
Le **code** de ce repository est sous licence **MIT** (voir `LICENSE`).  
Les **données** restent soumises à la licence de leur producteur.

## 🚀 Publication GitHub (rapide)
```bash
git init
git add .
git commit -m "Carburants: pipeline + EDA + docs"
git branch -M main
git remote add origin https://github.com/<ton-user>/<ton-repo>.git
git push -u origin main
```

## 🧰 Dépannage
- `ModuleNotFoundError` → installe les libs dans **l’environnement actif** (conda/venv).  
- Carte vide → réduire l’échantillon, vérifier connexion Internet (tuiles OSM).  
- 0 ligne après clean → problème de **format de prix** ou **carburant non détecté** → utiliser la version récente de `clean_data.py`.

## 📌 Roadmap (idées futures)
- Export PNG automatiques pour README (Plotly → static images).
- Alerte quotidienne si écart > X% sur un département.
- Ajout d’une **CI GitHub Actions** (lint + exécution d’un test minimal).