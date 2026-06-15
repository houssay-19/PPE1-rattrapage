#!/usr/bin/env python3

import sys
import re
import html as html_lib
from pathlib import Path
from collections import Counter


# ── Mots vides

STOPWORDS = {
    'fr': {
        'le','la','les','de','du','des','et','en','un','une','que','qui',
        'dans','est','pour','par','sur','au','aux','avec','se','sa','son',
        'ses','il','elle','ils','elles','nous','vous','je','tu','ou','mais',
        'donc','or','ni','car','ce','cette','ces','mon','ma','mes','ton',
        'ta','tes','leur','leurs','dont','ne','pas','plus','tres','bien',
        'aussi','comme','si','tout','tous','toutes','ete','etre','avoir',
        'faire','qui','quoi','dont','ou','a','y','n','d','l','s','j','m',
        'c','qu','au','aux','ni','se','te','me','lui','eux','en','y',
    },
    'en': {
        'the','a','an','and','or','but','in','on','at','to','for','of',
        'with','by','from','is','are','was','were','be','been','being',
        'have','has','had','do','does','did','will','would','could',
        'should','may','might','it','its','that','this','these','those',
        'we','you','he','she','they','i','me','him','her','us','them',
        'my','your','his','our','their','not','no','so','as','if','all',
        'also','which','who','what','when','where','how','than','then',
        'can','into','more','been','they','which','there','their','about',
    },
}


def nettoyer_token(token: str) -> str:
    """Minuscules + suppression ponctuation"""
    return re.sub(r'[^\wÀ-ÿ]', '', token.lower())


def lire_tokens(fichier: Path, stopwords: set) -> list:
    """Lit un fichier texte et retourne les tokens filtrés"""
    tokens = []
    try:
        for ligne in fichier.read_text(encoding='utf-8', errors='ignore').split('\n'):
            for mot in ligne.split():
                t = nettoyer_token(mot)
                if len(t) > 2 and t not in stopwords:
                    tokens.append(t)
    except Exception as e:
        print(f"  Erreur {fichier.name}: {e}")
    return tokens


def extraire_bigrammes(tokens: list) -> list:
    """Retourne la liste des bigrammes consécutifs."""
    return [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]


def generer_html(compteur: Counter, mot: str, lang: str, n: int = 30) -> str:
    """Génère la page HTML avec le tableau + barres de fréquence."""
    label_lang = "Français" if lang == "fr" else "English"
    top        = compteur.most_common(n)
    total      = sum(compteur.values())
    max_freq   = top[0][1] if top else 1

    lignes = ""
    for rang, ((w1, w2), freq) in enumerate(top, 1):
        pct    = freq / total * 100
        largeur = int(freq / max_freq * 100)
        lignes += f"""        <tr>
          <td class="rank">{rang}</td>
          <td class="bigram">{html_lib.escape(w1)}&nbsp;+&nbsp;{html_lib.escape(w2)}</td>
          <td class="freq">{freq}</td>
          <td class="pct">{pct:.2f}%</td>
          <td class="bar-cell"><div class="bar" style="width:{largeur}%"></div></td>
        </tr>\n"""

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <title>Bigrammes — {html_lib.escape(mot)}</title>
  <link rel="stylesheet" href="../../style.css">
  <style>
    .bgtab {{ width:100%; border-collapse:collapse; margin-top:15px; }}
    .bgtab th {{ background:#2c4a7c; color:white; padding:8px 12px; text-align:left; }}
    .bgtab td {{ padding:6px 12px; border-bottom:1px solid #e8e8e8; }}
    .bgtab tr:nth-child(even) {{ background:#f8f9fa; }}
    .bgtab tr:hover {{ background:#e8f0fe; }}
    .rank  {{ color:#888; text-align:center; width:40px; }}
    .bigram{{ font-family:monospace; font-size:1.05em; font-weight:bold; }}
    .freq  {{ text-align:right; font-weight:bold; color:#c62828; }}
    .pct   {{ text-align:right; color:#666; }}
    .bar-cell {{ width:30%; }}
    .bar   {{ background:#2c4a7c; height:16px; border-radius:3px; min-width:2px; }}
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
  <h1>Bigrammes : <em>{html_lib.escape(mot)}</em></h1>
  <p>{label_lang} — Top {n} sur {total:,} bigrammes au total</p>
</div>
<div class="container">
  <div class="card">
    <h2>Top {n} bigrammes</h2>
    <p>Paires de mots fréquentes dans le corpus, stopwords exclus.</p>
    <table class="bgtab">
      <thead>
        <tr>
          <th>#</th><th>Bigramme</th><th>Fréquence</th><th>%</th><th>Distribution</th>
        </tr>
      </thead>
      <tbody>
{lignes}      </tbody>
    </table>
  </div>
</div>
</body>
</html>"""


def main():
    if len(sys.argv) < 3:
        print("Usage : python3 programmes/bigrammes.py <lang> <mot_cible>")
        sys.exit(1)

    lang = sys.argv[1]
    mot  = sys.argv[2]

    pals_dir   = Path(f"pals/{lang}")
    output_dir = Path(f"bigrammes/{lang}")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not pals_dir.exists():
        print(f"Erreur : {pals_dir} introuvable. Lancez d'abord pipeline.sh.")
        sys.exit(1)

    sw = STOPWORDS.get(lang, set())
    tous_tokens: list = []

    for fichier in sorted(pals_dir.glob("*.txt")):
        tokens = lire_tokens(fichier, sw)
        tous_tokens.extend(tokens)
        print(f"  {fichier.name} : {len(tokens)} tokens")

    if not tous_tokens:
        print("Aucun token trouvé.")
        sys.exit(1)

    bigrammes = extraire_bigrammes(tous_tokens)
    compteur  = Counter(bigrammes)

    print(f"\n→ {len(tous_tokens)} tokens, {len(bigrammes)} bigrammes")
    print("  Top 5 :")
    for (w1, w2), f in compteur.most_common(5):
        print(f"    '{w1} {w2}' : {f}")

    html_contenu = generer_html(compteur, mot, lang)
    sortie = output_dir / "bigrammes.html"
    sortie.write_text(html_contenu, encoding='utf-8')
    print(f"\n→ {sortie} généré")


if __name__ == '__main__':
    main()
