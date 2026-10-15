"""Le papillon morpho en peluche, cousu main : quatre grandes ailes de feutrine d'un bleu ciel électrique, le bord noir
cousu autour comme un passepoil et un liseré de petits points blancs, le dessous brun orné d'yeux ; un petit corps
duveteux, deux antennes à massue. Le plus beau des courants d'air : posé à plat, les ailes OUVERTES en un léger V,
le bleu électrique tourné vers le ciel, une antenne qui nous cherche.

    python papillon_morpho.py        fabrique la fiche art/apercus/animaux/papillon_morpho.png (cousu main, palier 2)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K

BLEU = M.hexa("#35b7ff")                      # la dominante : bleu ciel électrique
NOIR = M.hexa("#25222e")                      # l'accent : le passepoil des ailes, la tête, les antennes
DESSOUS = M.hexa("#9a6a46")                   # le dessous, brun
CORPS_C = M.hexa("#5a4538")                   # le corps, brun sombre
POINTS = M.hexa("#fff6e8")                    # le liseré de petits points


def aile(rx, ry, pointe, decalage=0.0, n=48):
    """Le contour d'une aile : une goutte arrondie de rayon (rx, ry), plus ou moins pointue vers l'extérieur."""
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    x = rx * (0.5 + 0.5 * np.cos(t)) * (1 + pointe * np.maximum(0.0, np.cos(t)) * np.sin(t) ** 2)
    y = ry * np.sin(t) * (1 - 0.15 * np.cos(t))
    return np.stack([x + decalage, y], axis=1)


def construire():
    a = K.Animal("papillon_morpho")
    a.taille = 0.30

    # ----- le corps : un petit fuseau duveteux couché à l'horizontale, la tête ronde devant, les antennes à massue ;
    #       posé sur ses six petites pattes -----
    corps = A.tour(A.profil([(0, 0), (0.016, 0.010), (0.022, 0.060), (0.020, 0.120), (0.012, 0.180), (0, 0.200)], 5), 24)
    a.piece("corps", corps, CORPS_C, mat=A.repere((0.0, 0.092, 0.066), (90, 0, 0)))
    a.piece("tete", A.boule(1.0, 24, 12).etire(0.020, 0.019, 0.020), NOIR, pos=(0, -0.120, 0.066))
    a.tete = Vector((0, -0.150, 0.080))
    antennes = None
    for c, nom in ((1, "G"), (-1, "D")):
        tige = [(c * 0.008, -0.130, 0.076), (c * 0.040, -0.190, 0.110), (c * 0.080, -0.230, 0.140)]
        t = A.tube(A.courbe(tige, 4), 0.0030, 8) + A.boule(1.0, 12, 6).etire(0.009, 0.012, 0.009).pose(tige[-1], (0, 0, c * 30))
        antennes = t if antennes is None else antennes + t
        p, n = a.surface("tete", Vector((0, -0.120, 0.066)), Vector((c * 0.7, -0.7, 0.2)))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0068)
    a.piece("antennes", antennes, NOIR, poil=False)
    pattes = None
    for c in (1, -1):
        for y in (-0.080, -0.010, 0.060):
            t = A.tube(A.courbe([(c * 0.014, y, 0.058), (c * 0.050, y - 0.008, 0.030), (c * 0.062, y - 0.014, 0.004)], 4), 0.0030, 6)
            pattes = t if pattes is None else pattes + t
    a.piece("pattes", pattes, NOIR, poil=False)

    # ----- les ailes : OUVERTES à plat (un léger V), le bleu électrique vu de dessus, le bord noir cousu comme un passepoil,
    #       le liseré de petits points blancs ; le dessous brun en bas. Chacune est faite de trois couches ; les quatre
    #       ailes d'une même couche ne font qu'une pièce -----
    couches = {"dessous": None, "bord": None, "bleu": None, "points": None}

    def ajoute(cle, m):
        couches[cle] = m if couches[cle] is None else couches[cle] + m
    for c in (1, -1):
        for rx, ry, y0, pointe, balayage in ((0.150, 0.085, -0.014, 0.20, -22), (0.120, 0.075, 0.034, 0.05, 20)):
            contour = aile(rx, ry, pointe, 0.010) * np.array([c, 1.0])
            if c < 0:
                contour = contour[::-1]
            pos = (c * 0.014, y0, 0.064)
            rot = (0, -c * 12, c * balayage)
            for niveau, ech, epaisseur, ecart in (("dessous", 1.00, 0.004, 0.0000), ("bord", 0.98, 0.004, 0.0035), ("bleu", 0.82, 0.004, 0.0075)):
                m = A.decoupe(contour * ech, epaisseur, casse=0.0016)
                ajoute(niveau, m.pose((0, 0, ecart), (0, 0, 0)).pose(pos, rot))
            M_ = A.repere(pos, rot)
            for k in range(0, len(contour), 6):
                x, y = contour[k] * 0.93
                q = M_ @ Vector((x, y, 0.0105))
                ajoute("points", A.boule(1.0, 8, 4).etire(0.0045, 0.0045, 0.0016).pose((q.x, q.y, q.z)))
    for cle, couleur in (("dessous", DESSOUS), ("bord", NOIR), ("bleu", BLEU), ("points", POINTS)):
        a.piece("ailes_" + cle, couches[cle], couleur, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("papillon_morpho", styles.style_de("papillon_morpho"), sys.modules[__name__]), "Papillon morpho")
