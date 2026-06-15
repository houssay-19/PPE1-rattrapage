#!/usr/bin/env python3

import sys
import re
import unicodedata
import html as html_lib
from pathlib import Path


def normaliser(s: str) -> str:
    return unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode('ascii')


def compter_occurrences(texte: str, mot: str) -> int:
    """Compte les occurrences du mot dans le texte (insensible à la casse et aux accents)."""
    mot_norm = normaliser(mot)
    pattern  = re.compile(r'\b\w+\b', re.UNICODE)
    return sum(1 for m in pattern.findall(texte) if normaliser(m) == mot_norm)


def lire_infos(info_file: Path) -> list:
    """Lit le fichier infos.txt généré par pipeline.sh."""
    infos = []
    if not info_file.exists():
        return infos
    lines = info_file.read_text(encoding='utf-8', errors='ignore').split('\n')
    for ligne in lines[1:]:  # Sauter l'en-tête
        ligne = ligne.strip()
        if not ligne:
            continue
        parts = ligne.split('\t')
        if len(parts) >= 4:
            infos.append({
                'num':       parts[0],
                'url':       parts[1],
                'code_http': parts[2],
                'encodage':  parts[3],
            })
    return infos


def generer_html(infos: list, lang: str, mot: str, dumps_dir: Path) -> str:
    label_lang   = "Français" if lang == "fr" else "English"
    total_occ    = 0
    total_mots   = 0
    lignes_table = ""

    for info in infos:
        num = info['num'].zfill(2)
        txt_file = dumps_dir / f"page_{num}.txt"

        nb_mots = 0
        nb_occ  = 0
        if txt_file.exists():
            texte   = txt_file.read_text(encoding='utf-8', errors='ignore')
            nb_mots = len(texte.split())
            nb_occ  = compter_occurrences(texte, mot)
            total_mots += nb_mots
            total_occ  += nb_occ

        # Couleur du code HTTP
        code = info['code_http']
        couleur_code = '#27ae60' if code.startswith('2') else '#e74c3c' if code.startswith(('4','5')) else '#f39c12'

        # Liens vers les résultats
        lien_ctx  = f"contextes/{lang}/page_{num}_contextes.txt"
        lien_conc = f"concordances/{lang}/concordances.html"

        url_court = info['url'].replace('https://', '').replace('http://', '')
        if len(url_court) > 55:
            url_court = url_court[:52] + '...'

        lignes_table += f"""        <tr>
          <td class="num">{num}</td>
          <td class="url">
            <a href="{html_lib.escape(info['url'])}" target="_blank" title="{html_lib.escape(info['url'])}">
              {html_lib.escape(url_court)}
            </a>
          </td>
          <td class="code" style="color:{couleur_code};font-weight:bold">{html_lib.escape(code)}</td>
          <td class="enc">{html_lib.escape(info['encodage'])}</td>
          <td class="nb">{nb_mots:,}</td>
          <td class="occ {'zero' if nb_occ == 0 else ''}">{nb_occ}</td>
          <td class="liens">
            <a href="{lien_ctx}">contextes</a> |
            <a href="{lien_conc}">concordancier</a>
          </td>
        </tr>\n"""

    # Ligne total
    lignes_table += f"""        <tr class="total-row">
          <td colspan="4"><strong>TOTAL</strong></td>
          <td><strong>{total_mots:,}</strong></td>
          <td><strong>{total_occ}</strong></td>
          <td></td>
        </tr>\n"""

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <title>Tableau récapitulatif — {html_lib.escape(mot)}</title>
  <link rel="stylesheet" href="../../style.css">
  <style>
    .recap-table {{ width:100%; border-collapse:collapse; font-size:.9em; }}
    .recap-table th {{ background:#2c4a7c; color:white; padding:8px 10px; text-align:left; }}
    .recap-table td {{ padding:7px 10px; border-bottom:1px solid #e8e8e8; vertical-align:middle; }}
    .recap-table tr:nth-child(even):not(.total-row) {{ background:#f8f9fa; }}
    .recap-table tr:hover:not(.total-row) {{ background:#e8f0fe; }}
    .total-row {{ background:#e8edf6 !important; font-weight:bold; }}
    .num  {{ text-align:center; color:#888; }}
    .url  {{ max-width:350px; }}
    .url a {{ color:#2c4a7c; text-decoration:none; }}
    .url a:hover {{ text-decoration:underline; }}
    .code {{ text-align:center; }}
    .enc  {{ text-align:center; font-size:.85em; color:#666; }}
    .nb   {{ text-align:right; }}
    .occ  {{ text-align:center; font-weight:bold; font-size:1.1em; }}
    .occ.zero {{ color:#aaa; }}
    .liens {{ text-align:center; font-size:.85em; }}
    .liens a {{ color:#2c4a7c; }}
  </style>
</head>
<body>
<nav>
  <a class="logo" href="../../index.html">
    <img src="../../images/plurital-logo.jpg" alt="PluriTAL">
  </a>
  <a href="../../index.html">Accueil</a>
  <a href="../../resultats-fr.html">Résultats FR</a>
  <a href="../../resultats-en.html">Résultats EN</a>
  <a href="../../analyse.html">Analyse comparative</a>
</nav>
<div class="page-header">
  <h1>Tableau récapitulatif : <em>{html_lib.escape(mot)}</em></h1>
  <p>{label_lang} — {len(infos)} URL(s) aspirées | {total_occ} occurrence(s) au total</p>
</div>
<div class="container">
  <div class="card">
    <h2>Corpus <em>{html_lib.escape(mot)}</em></h2>
    <table class="recap-table">
      <thead>
        <tr>
          <th>#</th>
          <th>URL</th>
          <th>HTTP</th>
          <th>Encodage</th>
          <th>Nb mots</th>
          <th>Occ. «{html_lib.escape(mot)}»</th>
          <th>Liens</th>
        </tr>
      </thead>
      <tbody>
{lignes_table}      </tbody>
    </table>
  </div>
</div>
</body>
</html>"""


def main():
    if len(sys.argv) < 3:
        print("Usage : python3 programmes/tableaux.py <lang> <mot_cible>")
        sys.exit(1)

    lang = sys.argv[1]
    mot  = sys.argv[2]

    info_file  = Path(f"aspirations/{lang}/infos.txt")
    dumps_dir  = Path(f"dumps-txt/{lang}")
    output_dir = Path(f"tableaux/{lang}")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not info_file.exists():
        print(f"Erreur : {info_file} introuvable. Lancez d'abord pipeline.sh.")
        sys.exit(1)

    infos = lire_infos(info_file)
    print(f"→ {len(infos)} URL(s) trouvée(s) dans infos.txt")

    html_contenu = generer_html(infos, lang, mot, dumps_dir)
    sortie = output_dir / "tableau.html"
    sortie.write_text(html_contenu, encoding='utf-8')
    print(f"→ {sortie} généré")


if __name__ == '__main__':
    main()
