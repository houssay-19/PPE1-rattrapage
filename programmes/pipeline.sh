#!/bin/bash
# pipeline.sh — Pipeline PPE1 (aspiration, extraction, contextes)
# Auteure : Houssaynatou Diallo — PPE1 rattrapage 2025-2026
#
# Usage (depuis la RACINE du projet) :
#   bash programmes/pipeline.sh fr lumière
#   bash programmes/pipeline.sh en light

if [ "$#" -ne 2 ]; then
    echo "Usage : bash programmes/pipeline.sh <lang> <mot_cible>"
    echo "  Exemples :"
    echo "    bash programmes/pipeline.sh fr lumière"
    echo "    bash programmes/pipeline.sh en light"
    exit 1
fi

LANG="$1"
MOT="$2"
URL_FILE="URLS/urls-${LANG}.txt"

if [ ! -f "$URL_FILE" ]; then
    echo "Erreur : fichier URLs introuvable : $URL_FILE"
    exit 1
fi

echo ""
echo "  Pipeline PPE — langue : $LANG — mot cible : $MOT"

# ── Création de l'arborescence --
for DOSSIER in \
    "aspirations/$LANG" \
    "dumps-txt/$LANG" \
    "contextes/$LANG" \
    "pals/$LANG" \
    "concordances/$LANG" \
    "bigrammes/$LANG" \
    "cooccurrents/$LANG" \
    "nuages/$LANG" \
    "tableaux/$LANG"; do
    mkdir -p "$DOSSIER"
done

# ÉTAPE 1 — Aspiration des pages web

echo ""
echo ">>> ÉTAPE 1 : Aspiration des pages web"

INFO_FILE="aspirations/$LANG/infos.txt"
printf "num\turl\tcode_http\tencodage\n" > "$INFO_FILE"

i=1
while IFS= read -r url || [ -n "$url" ]; do
    # Ignorer lignes vides et commentaires
    [ -z "$url" ] && { i=$((i+1)); continue; }
    [[ "$url" =~ ^# ]] && continue

    NUM=$(printf '%02d' $i)
    HTML_OUT="aspirations/$LANG/page_${NUM}.html"

    # Télécharger et récupérer le code HTTP
    HTTP_CODE=$(curl -s -o "$HTML_OUT" -w "%{http_code}" -L \
        --max-time 30 \
        -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
        "$url" 2>/dev/null)

    # Encodage depuis les en-têtes HTTP
    ENC=$(curl -sI -L --max-time 10 \
        -H "User-Agent: Mozilla/5.0" \
        "$url" 2>/dev/null \
        | grep -i "content-type" \
        | grep -oiE "charset=[^; ]+" \
        | head -1 \
        | cut -d= -f2 \
        | tr -d '\r\n')
    [ -z "$ENC" ] && ENC="N/A"

    printf "%s\t%s\t%s\t%s\n" "$i" "$url" "$HTTP_CODE" "$ENC" >> "$INFO_FILE"
    echo "  [$NUM] HTTP $HTTP_CODE — $url"

    i=$((i + 1))
done < "$URL_FILE"

NB_PAGES=$((i - 1))
echo "→ $NB_PAGES pages récupérées → aspirations/$LANG/"

# ÉTAPE 2 — Extraction du texte avec lynx

echo ""
echo ">>> ÉTAPE 2 : Extraction du texte (lynx)"

for HTML_FILE in aspirations/$LANG/page_*.html; do
    [ -f "$HTML_FILE" ] || continue
    BASE=$(basename "$HTML_FILE" .html)
    TXT_OUT="dumps-txt/$LANG/${BASE}.txt"

    lynx -dump -nolist -display_charset=utf-8 "$HTML_FILE" > "$TXT_OUT" 2>/dev/null

    NB_MOTS=$(wc -w < "$TXT_OUT" | tr -d ' ')
    echo "  → $TXT_OUT  ($NB_MOTS mots)"
done

echo "→ Textes bruts → dumps-txt/$LANG/"


# ÉTAPE 3 — Extraction des contextes (lignes contenant le mot)

echo ""
echo ">>> ÉTAPE 3 : Extraction des contextes (\"$MOT\")"

TOTAL_CTX=0
for TXT_FILE in dumps-txt/$LANG/page_*.txt; do
    [ -f "$TXT_FILE" ] || continue
    BASE=$(basename "$TXT_FILE" .txt)
    CTX_OUT="contextes/$LANG/${BASE}_contextes.txt"

    # grep insensible à la casse, supprime les lignes vides
    grep -i "$MOT" "$TXT_FILE" \
        | grep -v "^[[:space:]]*$" \
        > "$CTX_OUT" 2>/dev/null || true

    NB=$(wc -l < "$CTX_OUT" | tr -d ' ')
    TOTAL_CTX=$((TOTAL_CTX + NB))
    echo "  → $BASE : $NB lignes"
done

echo "→ Total : $TOTAL_CTX contextes → contextes/$LANG/"

# ÉTAPE 4 — Textes propres (PALS)

echo ""
echo ">>> ÉTAPE 4 : Textes propres (PALS)"

for TXT_FILE in dumps-txt/$LANG/page_*.txt; do
    [ -f "$TXT_FILE" ] || continue
    BASE=$(basename "$TXT_FILE" .txt)
    PALS_OUT="pals/$LANG/${BASE}_propre.txt"

    # Nettoyage en chaîne :
    #  1. Minuscules
    #  2. Supprimer URLs (http...)
    #  3. Garder seulement lettres (y compris accents) et espaces
    #  4. Supprimer espaces multiples
    #  5. Supprimer lignes vides et lignes < 5 chars
    cat "$TXT_FILE" \
        | tr '[:upper:]' '[:lower:]' \
        | sed 's/https\?:\/\/[^ ]*//g' \
        | sed "s/[^a-zA-ZÀ-ÿ ]/ /g" \
        | tr -s ' ' \
        | sed 's/^ *//;s/ *$//' \
        | grep -v "^[[:space:]]*$" \
        | awk 'length($0) >= 5' \
        > "$PALS_OUT" 2>/dev/null || true

    NB=$(wc -l < "$PALS_OUT" | tr -d ' ')
    echo "  → $PALS_OUT ($NB lignes)"
done

echo "→ Textes propres → pals/$LANG/"

# RÉSUMÉ ET PROCHAINES ÉTAPES

echo ""
echo " Pipeline bash terminé pour '$MOT' ($LANG) !"
echo ""
echo " Prochaines étapes (depuis la racine du projet) :"
echo "   python3 programmes/concordances.py $LANG '$MOT'"
echo "   python3 programmes/bigrammes.py $LANG '$MOT'"
echo "   python3 programmes/cooccurrents.py $LANG '$MOT'"
echo "   python3 programmes/nuage_mots.py $LANG '$MOT'"
echo "   python3 programmes/tableaux.py $LANG '$MOT'"
