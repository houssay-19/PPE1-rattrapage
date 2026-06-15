#!/usr/bin/env python3
"""
nuage_mots.py Génère un nuage de mots à partir des textes propres (PALS)
Nécessite : pip3 install wordcloud matplotlib
Usage (depuis la racine du projet) :
    python3 programmes/nuage_mots.py fr lumière
    python3 programmes/nuage_mots.py en light
"""
import sys
import re
from pathlib import Path
from collections import Counter

# bruit dans les dumps lynx
MATH_ARTIFACTS = {
    'mjx','mrow','texatom','ord','displaystyle','class','modifier',
    'merror','mstyle','msqrt','mfrac','msub','msup','mtext','mover',
    'munder','mtable','mtr','mtd','mroot','mpadded','mphantom','mspace',
    'mn','mi','mo','math','span','div','textstyle','inline','bold',
    'italic','none','svg','aria','role','focusable','false','true',
    'jax','chtml','data','style','width','height','xmlns',
}

STOPWORDS = {
    'fr': {
        'le','la','les','de','du','des','et','en','un','une','que','qui',
        'dans','est','pour','par','sur','au','aux','avec','se','sa','son',
        'ses','il','elle','ils','elles','nous','vous','je','tu','ou','mais',
        'donc','or','ni','car','ce','cette','ces','mon','ma','mes','dont',
        'ne','pas','plus','tres','bien','aussi','comme','si','tout','tous',
        'a','y','n','d','l','s','j','m','c','qu','lui','eux','on',
        'ete','etre','avoir','faire','peut','sont','tres','bien','cest',
        'cela','mais','plus','moins','tres','bien','seul','toute',
    } | MATH_ARTIFACTS,
    'en': {
        'the','a','an','and','or','but','in','on','at','to','for','of',
        'with','by','from','is','are','was','were','be','been','being',
        'have','has','had','do','does','did','will','would','could',
        'should','may','might','it','its','that','this','these','those',
        'we','you','he','she','they','i','me','him','her','us','them',
        'my','your','his','our','their','not','no','so','as','if','all',
        'also','which','who','what','when','where','how','than','then',
        'can','into','more','there','about','such','each','they',
    } | MATH_ARTIFACTS,
}


def construire_frequences(pals_dir: Path, mot: str, lang: str) -> Counter:
    """Lit tous les fichiers PALS et construit le compteur de fréquences."""
    mot_clean = re.sub(r'[^\wÀ-ÿ]', '', mot.lower())
    sw = STOPWORDS.get(lang, set())
    compteur: Counter = Counter()

    for fichier in sorted(pals_dir.glob("*.txt")):
        try:
            for ligne in fichier.read_text(encoding='utf-8', errors='ignore').split():
                token = re.sub(r'[^\wÀ-ÿ]', '', ligne.lower())
                if len(token) > 2 and token not in sw and token != mot_clean:
                    compteur[token] += 1
        except Exception as e:
            print(f"  Erreur {fichier.name}: {e}")

    return compteur


def generer_nuage(compteur: Counter, sortie_png: Path, lang: str):
    """Génère le nuage de mots avec wordcloud + matplotlib."""
    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n⚠  wordcloud/matplotlib non installé.")
        print("   Installez avec : pip3 install wordcloud matplotlib")
        print("   En attendant, un fichier de fréquences .txt est généré.\n")
        return False

    # Palette : bleu PPE pour FR, rouge pour EN
    couleur = '#2c4a7c' if lang == 'fr' else '#c62828'

    wc = WordCloud(
        width=1200,
        height=600,
        background_color='white',
        max_words=100,
        colormap='Blues' if lang == 'fr' else 'Reds',
        collocations=False,
        min_font_size=10,
        max_font_size=120,
    ).generate_from_frequencies(dict(compteur))

    plt.figure(figsize=(14, 7))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(str(sortie_png), dpi=150, bbox_inches='tight')
    plt.close()

    print(f"→ Nuage de mots sauvegardé : {sortie_png}")
    return True


def sauvegarder_frequences(compteur: Counter, sortie_txt: Path, n: int = 50):
    """Sauvegarde le top-N des fréquences en .txt (fallback)."""
    with open(sortie_txt, 'w', encoding='utf-8') as f:
        f.write("mot\tfrequence\n")
        for mot, freq in compteur.most_common(n):
            f.write(f"{mot}\t{freq}\n")
    print(f"→ Fréquences sauvegardées : {sortie_txt}")


def main():
    if len(sys.argv) < 3:
        print("Usage : python3 programmes/nuage_mots.py <lang> <mot_cible>")
        sys.exit(1)

    lang = sys.argv[1]
    mot  = sys.argv[2]

    pals_dir   = Path(f"pals/{lang}")
    output_dir = Path(f"nuages/{lang}")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not pals_dir.exists():
        print(f"Erreur : {pals_dir} introuvable. Lancez d'abord pipeline.sh.")
        sys.exit(1)

    print(f"Lecture des textes propres ({lang})...")
    compteur = construire_frequences(pals_dir, mot, lang)

    if not compteur:
        print("Aucun mot trouvé dans les PALS.")
        sys.exit(1)

    print(f"→ {sum(compteur.values())} occurrences, {len(compteur)} mots distincts")
    print("  Top 5 :")
    for m, f in compteur.most_common(5):
        print(f"    '{m}' : {f}")

    # Toujours sauvegarder le fichier de fréquences
    sauvegarder_frequences(compteur, output_dir / "frequences.txt")

    # Générer le nuage (si wordcloud disponible)
    succes = generer_nuage(compteur, output_dir / "nuage.png", lang)

    if not succes:
        print("→ Relancez après installation de wordcloud pour obtenir le .png")


if __name__ == '__main__':
    main()
