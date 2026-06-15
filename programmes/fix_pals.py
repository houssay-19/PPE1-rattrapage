#!/usr/bin/env python3
"""
Avec fix_pals.py  on supprime les artefacts MathJax/MathML des fichiers PALS
Ces artefacts viennent du rendu des formules mathématiques dans Wikipedia.
Usage (depuis la racine du projet) :
    python3 programmes/fix_pals.py
"""
from pathlib import Path

# Tokens parasites issus du HTML/MathJax de Wikipedia
# (classes CSS, attributs MathML, balises SVG, etc.)
ARTEFACTS = {
    # MathJax / MathML
    'mjx', 'mrow', 'texatom', 'ord', 'displaystyle', 'modifier',
    'merror', 'mstyle', 'msqrt', 'mfrac', 'msub', 'msup', 'mtext',
    'mover', 'munder', 'mtable', 'mtr', 'mtd', 'mroot', 'mpadded',
    'mphantom', 'mspace', 'textstyle', 'mn', 'mi', 'mo',
    # HTML / CSS / JavaScript
    'class', 'span', 'div', 'style', 'inline', 'bold', 'italic',
    'none', 'true', 'false', 'role', 'aria', 'focusable',
    # SVG / MathML attributes
    'svg', 'xmlns', 'width', 'height', 'jax', 'chtml',
    # Attributs sémantiques MathML de Wikipedia
    'semantics', 'annotation', 'data',
    # Mots anglais parasites dans les PALS français
    'the', 'of', 'in', 'and', 'for', 'with', 'that',
}


def nettoyer_ligne(ligne: str) -> str:
    """Supprime les artefacts d'une ligne de texte propre."""
    mots = [
        mot for mot in ligne.split()
        if mot.lower() not in ARTEFACTS and len(mot) > 1
    ]
    return ' '.join(mots)


def main():
    total_lignes = 0
    total_fichiers = 0

    for lang in ['fr', 'en']:
        pals_dir = Path(f"pals/{lang}")
        if not pals_dir.exists():
            print(f"  ⚠  pals/{lang}/ introuvable — ignoré")
            continue

        for fichier in sorted(pals_dir.glob("*.txt")):
            lignes = fichier.read_text(encoding='utf-8', errors='ignore').split('\n')
            lignes_nettoyees = []
            for ligne in lignes:
                propre = nettoyer_ligne(ligne)
                if propre.strip():
                    lignes_nettoyees.append(propre)

            fichier.write_text('\n'.join(lignes_nettoyees), encoding='utf-8')
            total_lignes  += len(lignes_nettoyees)
            total_fichiers += 1
            print(f"  ✔ {fichier}  ({len(lignes_nettoyees)} lignes conservées)")

    print(f"\n→ {total_fichiers} fichiers PALS re-nettoyés ({total_lignes} lignes)")
    print("\nRelancez maintenant :")
    print("  python3 programmes/bigrammes.py fr lumière")
    print("  python3 programmes/bigrammes.py en light")
    print("  python3 programmes/nuage_mots.py fr lumière")
    print("  python3 programmes/nuage_mots.py en light")


if __name__ == '__main__':
    main()
