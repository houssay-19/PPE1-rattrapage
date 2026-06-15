#!/usr/bin/env python3

import sys
import re
import unicodedata
import html as html_lib
from pathlib import Path


# ── Utilitaires - ---

def normaliser(s: str) -> str:
    """Supprime les accents et met en minuscules pour la comparaison."""
    return unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode('ascii')


def trouver_concordances(texte: str, mot: str, fenetre: int = 5):
    """
    Parcourt le texte ligne par ligne et retourne une liste de tuples
    (contexte_gauche, mot_trouvé, contexte_droit).
    fenetre : nombre de tokens de chaque côté.
    """
    mot_norm = normaliser(mot)
    concordances = []

    for ligne in texte.split('\n'):
        ligne = ligne.strip()
        if not ligne:
            continue

        tokens = ligne.split()
        for i, token in enumerate(tokens):
            # Nettoyer le token pour la comparaison
            token_clean = re.sub(r'[^\w]', '', token, flags=re.UNICODE)
            if not token_clean:
                continue

            if normaliser(token_clean) == mot_norm:
                gauche  = ' '.join(tokens[max(0, i - fenetre): i])
                droite  = ' '.join(tokens[i + 1: i + fenetre + 1])
                concordances.append((gauche, token, droite))

    return concordances


# ── Génération HTML --

def generer_html(concordances_par_fichier: dict, mot: str, lang: str) -> str:
    """Génère la page HTML complète du concordancier."""
    total = sum(len(c) for c in concordances_par_fichier.values())
    label_lang = "Français" if lang == "fr" else "English"

    lignes_tableau = ""
    for nom_fichier, concordances in concordances_par_fichier.items():
        if not concordances:
            continue
        for gauche, kw, droite in concordances:
            lignes_tableau += f"""            <tr>
                <td class="ctx-left">{html_lib.escape(gauche)}</td>
                <td class="ctx-kw">{html_lib.escape(kw)}</td>
                <td class="ctx-right">{html_lib.escape(droite)}</td>
                <td class="ctx-src">{html_lib.escape(nom_fichier)}</td>
            </tr>\n"""

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <title>Concordances — {html_lib.escape(mot)}</title>
  <link rel="stylesheet" href="../../style.css">
  <style>
    .concordance-table {{ width:100%; border-collapse:collapse; font-size:.9em; }}
    .concordance-table th {{ background:#2c4a7c; color:white; padding:8px 10px; text-align:left; }}
    .concordance-table td {{ padding:5px 10px; border-bottom:1px solid #e8e8e8; }}
    .concordance-table tr:nth-child(even) {{ background:#f8f9fa; }}
    .concordance-table tr:hover {{ background:#e8f0fe; }}
    .ctx-left  {{ text-align:right; color:#555; width:38%; }}
    .ctx-kw    {{ text-align:center; font-weight:bold; color:#c62828; white-space:nowrap; width:10%; }}
    .ctx-right {{ text-align:left; color:#555; width:38%; }}
    .ctx-src   {{ text-align:center; color:#888; font-size:.8em; width:14%; }}
    .stat-box  {{ background:#e8edf6; border-left:4px solid #2c4a7c; padding:12px 18px; border-radius:4px; margin-bottom:20px; }}
  </style>
</head>
<body>
<nav>
  <a class="logo" href="../../index.html">
    <img src="../../images/plurital-logo.jpg" alt="PluriTAL">
  </a>
  <a href="../../index.html">Accueil</a>
  <a href="../../technique.html">Démarche technique</a>
  <a href="../../resultats-fr.html">Résultats FR</a>
  <a href="../../resultats-en.html">Résultats EN</a>
  <a href="../../analyse.html">Analyse comparative</a>
</nav>
<div class="page-header">
  <h1>Concordances : <em>{html_lib.escape(mot)}</em></h1>
  <p>{label_lang} — {total} occurrences trouvées dans le corpus</p>
</div>
<div class="container">
  <div class="stat-box">
    <strong>{total}</strong> occurrence(s) du mot <em>«&nbsp;{html_lib.escape(mot)}&nbsp;»</em>
    réparties sur <strong>{len([f for f,c in concordances_par_fichier.items() if c])}</strong> fichier(s).
    Fenêtre de contexte : ±5 tokens.
  </div>
  <div class="card">
    <table class="concordance-table">
      <thead>
        <tr>
          <th>Contexte gauche</th>
          <th>Mot cible</th>
          <th>Contexte droit</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody>
{lignes_tableau}      </tbody>
    </table>
  </div>
</div>
</body>
</html>"""


# ── Main

def main():
    if len(sys.argv) < 3:
        print("Usage : python3 programmes/concordances.py <lang> <mot_cible>")
        sys.exit(1)

    lang = sys.argv[1]
    mot  = sys.argv[2]

    dumps_dir  = Path(f"dumps-txt/{lang}")
    output_dir = Path(f"concordances/{lang}")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not dumps_dir.exists():
        print(f"Erreur : {dumps_dir} introuvable. Lancez d'abord pipeline.sh.")
        sys.exit(1)

    concordances_par_fichier: dict = {}
    total = 0

    for fichier in sorted(dumps_dir.glob("*.txt")):
        texte = fichier.read_text(encoding='utf-8', errors='ignore')
        conc = trouver_concordances(texte, mot)
        concordances_par_fichier[fichier.name] = conc
        total += len(conc)
        print(f"  {fichier.name} : {len(conc)} occurrence(s)")

    # Écrire le HTML
    contenu = generer_html(concordances_par_fichier, mot, lang)
    sortie  = output_dir / "concordances.html"
    sortie.write_text(contenu, encoding='utf-8')

    print(f"\n→ {sortie} généré  ({total} occurrences au total)")


if __name__ == '__main__':
    main()
