#!/bin/bash


echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  PPE1 Rattrapage — Pipeline complet FR + EN      ║"
echo "╚══════════════════════════════════════════════════╝"

# ── Vérifier les dépendances
echo ""
echo ">>> Vérification des outils..."

for CMD in curl lynx python3; do
    if command -v "$CMD" &>/dev/null; then
        echo "  ✔ $CMD"
    else
        echo "  ✘ $CMD MANQUANT — installez-le avant de continuer"
        exit 1
    fi
done

# Vérifier wordcloud Python
python3 -c "import wordcloud" 2>/dev/null && echo "  ✔ wordcloud" || {
    echo "  ⚠ wordcloud absent — installez avec : pip3 install wordcloud matplotlib"
    echo "    (Le nuage de mots sera ignoré mais le reste fonctionnera)"
}

# ================================================================
# FRANÇAIS — lumière
# ================================================================
echo ""
echo "┌────────────────────────────────────────┐"
echo "│  LANGUE : FRANÇAIS  |  MOT : lumière   │"
echo "└────────────────────────────────────────┘"

bash programmes/pipeline.sh fr "lumière"

echo ""
echo "--- Analyses Python (FR) ---"
python3 programmes/concordances.py fr "lumière"
python3 programmes/bigrammes.py    fr "lumière"
python3 programmes/cooccurrents.py fr "lumière"
python3 programmes/nuage_mots.py   fr "lumière"
python3 programmes/tableaux.py     fr "lumière"

# ANGLAIS — light

echo ""
echo "┌────────────────────────────────────────┐"
echo "│  LANGUE : ENGLISH   |  MOT : light     │"
echo "└────────────────────────────────────────┘"

bash programmes/pipeline.sh en "light"

echo ""
echo "--- Analyses Python (EN) ---"
python3 programmes/concordances.py en "light"
python3 programmes/bigrammes.py    en "light"
python3 programmes/cooccurrents.py en "light"
python3 programmes/nuage_mots.py   en "light"
python3 programmes/tableaux.py     en "light"

# RÉSUMÉ FINAL

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  Pipeline terminé !                              ║"
echo "║  Ouvrez index.html dans votre navigateur.        ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "Fichiers générés :"
echo "  concordances/fr/concordances.html"
echo "  concordances/en/concordances.html"
echo "  bigrammes/fr/bigrammes.html"
echo "  bigrammes/en/bigrammes.html"
echo "  cooccurrents/fr/cooccurrents.html"
echo "  cooccurrents/en/cooccurrents.html"
echo "  nuages/fr/nuage.png"
echo "  nuages/en/nuage.png"
echo "  tableaux/fr/tableau.html"
echo "  tableaux/en/tableau.html"
echo ""
echo "Prochaine étape :"
echo "  git init && git add . && git commit -m 'Init projet PPE1 rattrapage'"
echo "  git remote add origin https://github.com/houssay-19/PPE1-rattrapage.git"
echo "  git push -u origin main"
