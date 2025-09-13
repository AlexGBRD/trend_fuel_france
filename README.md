# Analyse des prix des carburants en France (Projet Débutant -> Intermédiaire)

**Objectif** : récupérer les prix journaliers des carburants en France (open data), nettoyer les données, explorer, visualiser et publier le projet sur GitHub.

## 1) Installation rapide

```bash
# Option A : conda (recommandé)
conda create -n carburants python=3.11 -y
conda activate carburants
pip install -r requirements.txt

# Option B : pip uniquement
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Télécharger les données

```bash
python src/download_data.py
```

## 3) Nettoyer / préparer

```bash
python src/clean_data.py
```

## 4) Explorer

Ouvrez Jupyter et lancez le notebook :
```bash
jupyter notebook notebooks/01_eda.ipynb
```

## 5) Publier sur GitHub

```bash
git init
git add .
git commit -m "Init: projet carburants FR"
# Remplacez URL ci-dessous par votre dépôt vide (sur GitHub)
git remote add origin <URL_DU_DEPOT>
git branch -M main
git push -u origin main
```

## Données

- Source : *Prix des carburants en France – flux quotidien* (data.economie.gouv.fr).
- API publique fournie par la plateforme Opendatasoft.

> Respectez la licence ouverte fournie par les producteurs des données.