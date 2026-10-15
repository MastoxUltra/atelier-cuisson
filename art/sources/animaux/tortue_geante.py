"""La tortue géante du volcan : la tortue à dôme du jardin (tortue.py), agrandie. l'auteur, le 14 octobre 2026 : « la plate
pour le marais, celle à dôme agrandie pour la tortue géante du volcan, en peluche de magasin ». Son palier (4, rare) lui
donne le style B tout seul (styles.py).

    python usine.py tortue_geante       la fabrique dans art/modeles/tortue_geante/

Même dessin, même squelette, mêmes animations que la tortue : seule sa taille change (1,15 m au lieu de 0,62).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tortue as _T  # noqa: E402

OS, PORTEURS, ANIMATIONS = _T.OS, _T.PORTEURS, _T.ANIMATIONS
TAILLE = 1.15


def construire():
    a = _T.construire()
    a.nom = "tortue_geante"
    a.taille = TAILLE
    return a


if __name__ == "__main__":
    import peluche as K
    K.planche(construire, "La tortue géante")
