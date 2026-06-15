# Journal de bord — PPE1 Rattrapage 2025-2026
**Houssaynatou Diallo — M1 PluriTAL**


## Mise en place du projet

J'ai initialisé le projet de rattrapage dans un nouveau dossier `PPE1-rattrapage/`, puis j'ai créé l'arborescence :
`aspirations/`, `dumps-txt/`, `contextes/`, `pals/`, `concordances/`,`bigrammes/`, `cooccurrents/`, `nuages/`, `tableaux/`, `programmes/`, `URLS/`, `images/`. 
Chaque dossier existe en version `fr/` et `en/` pour les deux langues du corpus.

J'ai repris les 10 URLs Wikipédia françaises autour de *lumière* (physique, vitesse de la lumière, photon, optique, spectre visible, réfraction, réflexion, éclairage, Siècle des Lumières) et j'ai choisis 10 URLs anglaises autour de *light* (mêmes thèmes côté anglophone).

Le script principal `programmes/pipeline.sh`  enchaîne quatre étapes :
- l'aspiration des pages avec `curl`, 
- l'extraction du texte brut avec `lynx`, 
- l'extraction des contextes contenant le mot cible avec `grep`, 
- et la production des textes propres (PALS) par une chaîne de filtres `tr`, `sed`, `grep`. 
J'ai aussi cinq scripts
Python : `concordances.py` (concordancier KWiC), `bigrammes.py` (top 30 bigrammes), `cooccurrents.py` (mots voisins du mot cible), `nuage_mots.py` (nuage de mots PNG), `tableaux.py` (tableau récapitulatif HTML). Enfin, j'ai créé le site web avec cinq pages HTML (`index.html`, `technique.html`, `resultats-fr.html`,
`resultats-en.html`, `analyse.html`) et une feuille de style CSS.


## Exécution du pipeline et débogage

J'ai lancé le script `run_all.sh` qui exécute le pipeline complet pour
les deux langues. Voici les résultats de l'aspiration :

- Français : 9 pages sur 10 récupérées avec succès (HTTP 200). La page
  `Lumière_(physique)` a retourné un code 404 : l'article Wikipédia a
  été renommé ou fusionné. 
- Anglais : 10 pages sur 10 récupérées (HTTP 200).

L'extraction avec `lynx` a produit des dumps allant de 432 mots (page 404) à 20 166 mots. J'ai obtenu 692 contextes contenant *lumière* en français et 1 646 contextes contenant *light* en anglais.

**Problème rencontré : artefacts MathJax dans les analyses.**
En examinant les résultats des bigrammes, j'ai vu que les premiers rangs étaient occupés par des séquences sans grand interrêt linguistique : `class mjx`, `mrow class`, `texatom ord`, etc. 
Ces tokens proviennent du rendu des formules mathématiques dans les pages
Wikipédia : `lynx` convertit en texte les attributs HTML et MathML des
équations (noms de classes CSS, balises SVG, attributs `data-`), qui
se retrouvent mélangés au texte naturel dans les PALS.

**Solution apportée : nettoyage itératif des fichiers PALS.**
J'ai fait une liste d'exclusion (`bad`) regroupant les tokens "parasites" identifiés : tokens MathJax (`mjx`, `mrow`, `texatom`, `displaystyle`, `msqrt`, etc.), attributs HTML (`class`, `span`, `div`, `style`, `role`, `aria`), attributs MathML (`semantics`, `annotation`, `mathvariant`), métadonnées de contenu (`encoding`, `archived`). J'ai appliqué ce filtre directement sur les fichiers PALS avec un script Python inline, sans avoir à ré-aspirer les pages. 

Après nettoyage, les résultats des bigrammes sont pertinents du point de vue linguistique :

| Langue | Top bigrammes |
|--------|---------------|
| FR | `vitesse lumière` (110), `longueur onde` (67), `siècle lumières` (44) |
| EN | `speed light` (207), `electromagnetic radiation` (93) |

Les nuages de mots montrent pour le français : vitesse, optique, onde ; pour l'anglais : radiation, speed, wave, energy, electromagnetic.
Ces résultats reflètent bien le champ sémantique physique et scientifique du corpus.

Les cooccurrents du mot cible confirment cette orientation :
*lumière* co-occure principalement avec *vitesse* (89 fois), *vide*
(20), *visible* (14) ; *light* avec *speed* (177), *visible* (61),
*wave* (38).


## 
