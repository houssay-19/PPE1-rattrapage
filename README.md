# PPE1 — Rattrapage 2025-2026

**Houssaynatou Diallo — M1 PluriTAL**
(INALCO / Sorbonne Nouvelle / Paris Nanterre)

Corpus web bilingue autour du mot **lumière** (français) et **light** (anglais).



## Structure du projet

```
PPE1-rattrapage/
├── URLS/
│   ├── urls-fr.txt          # 10 URLs françaises (Wikipedia)
│   └── urls-en.txt          # 10 URLs anglaises (Wikipedia)
├── programmes/
│   ├── pipeline.sh          # Aspiration + extraction + contextes + PALS
│   ├── concordances.py      # Concordancier KWiC HTML
│   ├── bigrammes.py         # Bigrammes HTML
│   ├── cooccurrents.py      # Cooccurrents HTML
│   ├── nuage_mots.py        # Nuage de mots PNG
│   └── tableaux.py          # Tableau récapitulatif HTML
├── aspirations/fr/ et /en/  # Pages HTML téléchargées
├── dumps-txt/fr/ et /en/    # Textes bruts (lynx)
├── contextes/fr/ et /en/    # Lignes contenant le mot cible
├── pals/fr/ et /en/         # Textes propres (PALS)
├── concordances/fr/ et /en/ # Concordancier HTML
├── bigrammes/fr/ et /en/    # Bigrammes HTML
├── cooccurrents/fr/ et /en/ # Cooccurrents HTML
├── nuages/fr/ et /en/       # Nuage de mots PNG
├── tableaux/fr/ et /en/     # Tableau récapitulatif HTML
├── images/                  # Logo PluriTAL
├── index.html               # Page d'accueil
├── technique.html           # Démarche technique
├── resultats-fr.html        # Résultats français
├── resultats-en.html        # Résultats anglais
├── analyse.html             # Analyse comparative
└── style.css                # Feuille de style
```



## Utilisation

### Prérequis

```bash
# Vérifier que curl et lynx sont disponibles
which curl lynx

# Installer les bibliothèques Python (si absentes)
pip3 install wordcloud matplotlib
```

### Lancer le pipeline (depuis la racine du projet)

```bash
# Langue française — mot cible : lumière
bash programmes/pipeline.sh fr lumière

# Langue anglaise — mot cible : light
bash programmes/pipeline.sh en light
```

### Générer les analyses Python

```bash
# Pour le français
python3 programmes/concordances.py fr lumière
python3 programmes/bigrammes.py fr lumière
python3 programmes/cooccurrents.py fr lumière
python3 programmes/nuage_mots.py fr lumière
python3 programmes/tableaux.py fr lumière

# Pour l'anglais
python3 programmes/concordances.py en light
python3 programmes/bigrammes.py en light
python3 programmes/cooccurrents.py en light
python3 programmes/nuage_mots.py en light
python3 programmes/tableaux.py en light
```

### Consulter le site

Ouvrir `index.html` dans un navigateur (ou via GitHub Pages).



## Outils

- **curl** — aspiration des pages web
- **lynx** — conversion HTML → texte
- **grep / sed / tr** — traitement texte Unix
- **Python 3** — analyses, génération HTML
- **wordcloud + matplotlib** — nuage de mots

