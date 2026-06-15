#!/usr/bin/env python3

import sys
import re
import unicodedata
import html as html_lib
from pathlib import Path
from collections import Counter


# ── Mots vides

STOPWORDS = {
    'fr': {
        'le','la','les','de','du','des','et','en','un','une','que','qui',
        'dans','est','pour','par','sur','au','aux','avec','se','sa','son',
        'ses','il','elle','ils','elles','nous','vous','je','tu','ou','mais',
        'donc','or','ni','car','ce','cette','ces','mon','ma','mes','dont',
        'ne','pas','plus','tres','bien','aussi','comme','si','tout','tous',
        'a','y','n','d','l','s','j','m','c','qu','lui','eux','on',
        'ete','etre','avoir','faire','peut','sont','plus','tres','bien',
    },
    'en': {
        'the','a','an','and','or','but','in','on','at','to','for','of',
        'with','by','from','is','are','was','were','be','been','being',
        'have','has','had','do','does','did','will','would','could',
        'should','may','might','it','its','that','this','these','those',
        'we','you','he','she','they','i','me','him','her','us','them',
        'my','your','his','our','their','not','no','so','as','if','all',
        'also','which','who','what','when','where','how','than','then',
        'can','into','more','there','about','such','between','each',
    },
}


def normaliser(s: str) -> str:
    return unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode('ascii')


def extraire_cooccurrents(texte: str, mot: str, fenetre: int = 5) -> list:

    # Pour chaque ligne contenant le mot cible, extrai les N tokens voisins (gauche + droite) comme cooccurrents.

    mot_norm = normaliser(mot)
    cooc: list = []

    for ligne in texte.split('\n'):
        ligne = ligne.strip()
        if not ligne:
            continue
        tokens = ligne.split()
        for i, token in enumerate(tokens):
            t_clean = re.sub(r'[^\wÀ-ÿ]', '', token.lower())
            if not t_clean:
                continue
            if normaliser(t_clean) == mot_norm:
                voisins_idx = list(range(max(0, i - fenetre), i)) + \
                              list(range(i + 1, min(len(tokens), i + fenetre + 1)))
                for j in voisins_idx:
                    voisin = re.sub(r'[^\wÀ-ÿ]', '', tokens[j].lower())
                    if len(voisin) > 2:
                        cooc.append(voisin)
    return cooc


def generer_html(compteur: Counter, mot: str, lang: str, n: int = 40) -> str:
    label_lang = "Français" if lang == "fr" else "English"
    top      = compteur.most_common(n)
    total    = sum(compteur.values())
    max_freq = top[0][1] if top else 1

    lignes = ""
    for rang, (mot_cooc, freq) in enumerate(top, 1):
        pct    = freq / total * 100
        largeur = int(freq / max_freq * 100)
        lignes += f"""        <tr>
          <td class="rank">{rang}</td>
          <td class="word">{html_lib.escape(mot_cooc)}</td>
          <td class="freq">{freq}</td>
          <td class="pct">{pct:.2f}%</td>
          <td class="bar-cell"><div class="bar" style="width:{largeur}%"></div></td>
        </tr>\n"""

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <title>Cooccurrents — {html_lib.escape(mot)}</title>
  <link rel="stylesheet" href="../../style.css">
  <style>
    .cootab {{ width:100%; border-collapse:collapse; margin-top:15px; }}
    .cootab th {{ background:#2c4a7c; color:white; padding:8px 12px; text-align:left; }}
    .cootab td {{ padding:6px 12px; border-bottom:1px solid #e8e8e8; }}
    .cootab tr:nth-child(even) {{ background:#f8f9fa; }}
    .cootab tr:hover {{ background:#e8f0fe; }}
    .rank {{ color:#888; text-align:center; width:40px; }}
    .word {{ font-weight:bold; }}
    .freq {{ text-align:right; color:#c62828; font-weight:bold; }}
    .pct  {{ text-align:right; color:#666; }}
    .bar-cell {{ width:30%; }}
    .bar  {{ background:#e86a1a; height:16px; border-radius:3px; min-width:2px; }}
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
  <h1>Cooccurrents : <em>{html_lib.escape(mot)}</em></h1>
  <p>{label_lang} — Top {n} mots voisins (fenêtre ±5)</p>
</div>
<div class="container">
  <div class="card">
    <h2>Mots les plus fréquemment voisins de <em>{html_lib.escape(mot)}</em></h2>
    <p>
      Extraits des contextes (lignes contenant le mot cible), fenêtre de ±5 tokens.
      Stopwords exclus. Total de cooccurrences analysées : <strong>{total:,}</strong>.
    </p>
    <table class="cootab">
      <thead>
        <tr>
          <th>#</th><th>Mot cooccurrent</th><th>Fréquence</th><th>%</th><th>Distribution</th>
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
        print("Usage : python3 programmes/cooccurrents.py <lang> <mot_cible>")
        sys.exit(1)

    lang = sys.argv[1]
    mot  = sys.argv[2]

    ctx_dir    = Path(f"contextes/{lang}")
    output_dir = Path(f"cooccurrents/{lang}")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not ctx_dir.exists():
        print(f"Erreur : {ctx_dir} introuvable. Lancez d'abord pipeline.sh.")
        sys.exit(1)

    sw = STOPWORDS.get(lang, set())
    tous_cooc: list = []

    for fichier in sorted(ctx_dir.glob("*_contextes.txt")):
        texte = fichier.read_text(encoding='utf-8', errors='ignore')
        cooc  = extraire_cooccurrents(texte, mot)
        # Filtrer stopwords
        cooc_filtres = [c for c in cooc if c not in sw and len(c) > 2]
        tous_cooc.extend(cooc_filtres)
        print(f"  {fichier.name} : {len(cooc_filtres)} cooccurrents")

    if not tous_cooc:
        print("Aucun cooccurrent trouvé.")
        sys.exit(1)

    compteur = Counter(tous_cooc)

    print(f"\n→ Top 5 cooccurrents de '{mot}' :")
    for m, f in compteur.most_common(5):
        print(f"    '{m}' : {f}")

    html_contenu = generer_html(compteur, mot, lang)
    sortie = output_dir / "cooccurrents.html"
    sortie.write_text(html_contenu, encoding='utf-8')
    print(f"\n→ {sortie} généré")


if __name__ == '__main__':
    main()
