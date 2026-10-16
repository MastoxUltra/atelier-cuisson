"""Le poisson-lune en peluche : un énorme disque d'argent froid, nacré, qui n'est que tête : pas de queue, une frange
ondulante à la place, un aileron en haut et un autre dessous, deux grands comme des voiles. Debout sur la tranche, sur
son aileron du bas, il regarde de côté d'un œil rond sous une paupière à demi tombée, la petite bouche en « o » :
il a l'air de n'avoir rien pensé depuis sa naissance, et d'en être très content.

    python poisson_lune.py        fabrique la fiche art/apercus/animaux/poisson_lune.png (style du palier : B, peluche de magasin)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

ARGENT = np.array(M.hexa("#b3bfd0"))          # la dominante (registre : argent bleuté, plus froid et nacré)
NACRE = np.array(M.hexa("#e7ecf4"))           # le ventre, les reflets
GRIS = np.array(M.hexa("#7f8a9e"))            # les nageoires, la frange
FIL = M.hexa("#3a4256")
TOURNE = 5                                     # de trois quarts avant : les deux yeux ET les grands ailerons (à 35, de face, ils se lisaient comme des tiges ; à -22, un seul œil) ; 0 pour le jeu


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def construire():
    a = K.Animal("poisson_lune")
    a.taille = 3.00

    # ----- le disque : un large galet aplati sur les côtés, plus haut que long, le menton qui pointe en bas à l'avant ;
    #       argenté dessus, nacré dessous, moucheté de gris -----
    def galet(v):
        s = np.zeros_like(v)
        s[:, 0] = 0.115 * v[:, 0] * (1 - 0.35 * np.abs(v[:, 2]))                          # épaisseur (X)
        s[:, 1] = 0.300 * v[:, 1]                                                         # longueur (Y)
        s[:, 2] = 0.360 * v[:, 2] * (1 - 0.16 * np.clip(-v[:, 1], 0, None) ** 1.5 * (v[:, 2] > 0))    # le front qui fuit vers la bouche
        return s
    corps = A.boule(1.0, 64, 32)
    u = corps.v / np.maximum(np.linalg.norm(corps.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(ARGENT, (len(u), 1))
    t[u[:, 2] < -0.35] = NACRE
    rng = np.random.default_rng(8)
    graines = rng.normal(size=(60, 3))
    graines /= np.linalg.norm(graines, axis=1, keepdims=True)
    proche = u @ graines.T > np.cos(0.13 * rng.uniform(0.7, 1.3, 60))[None, :]
    t[proche.any(axis=1)] = GRIS * 0.55 + ARGENT * 0.45
    corps.teinte = t
    a.piece("corps", corps.sculpte(galet), None, pos=(0.0, 0.0, 0.790))

    # ----- la frange arrière : la « queue » qui n'en est pas une, une jupe ondulée qui borde le derrière du disque -----
    def ondule(v):
        s = v.copy()
        s[:, 0] += 0.014 * np.sin(v[:, 2] * 38)
        return s
    frange = A.boule(1.0, 40, 16).sculpte(ondule).etire(0.050, 0.080, 0.300)
    frange.teinte = np.tile(GRIS, (len(frange.v), 1))
    a.piece("frange", frange, None, pos=(0.0, 0.265, 0.790), poil=False)

    # ----- les deux grands ailerons : dorsal en haut, anal en bas (celui sur lequel il se tient), en larges faucilles -----
    haut = A.decoupe([(-0.10, 0), (-0.06, 0.16), (0.00, 0.30), (0.06, 0.44), (0.10, 0.50), (0.16, 0.42), (0.20, 0.26), (0.24, 0.10), (0.26, 0.0)],
                     0.048, 0.016)                 # large à la base, épais (étroits, ils se lisaient comme des tiges : 16/10)
    haut.teinte = np.tile(GRIS * 1.08, (len(haut.v), 1))
    a.piece("dorsale", couche(haut, A.cadre((0.0, 0.100, 1.120), (1.0, 0.0, 0.0), (0, 0, 1))), None, poil=False)
    bas = A.decoupe([(-0.10, 0), (-0.06, -0.14), (0.00, -0.27), (0.06, -0.39), (0.10, -0.44), (0.16, -0.37), (0.20, -0.23), (0.24, -0.09), (0.26, 0.0)],
                    0.048, 0.016)
    bas.teinte = np.tile(GRIS * 1.08, (len(bas.v), 1))
    a.piece("anale", couche(bas, A.cadre((0.0, 0.100, 0.468), (1.0, 0.0, 0.0), (0, 0, 1))), None, poil=False)

    # ----- le visage : deux yeux ronds ouverts, la petite bouche en « o » devant -----
    CENTRE = Vector((0.0, 0.0, 0.790))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("corps", CENTRE, Vector((c * 0.62, -0.78, 0.08)))
        a.oeil("oeil_" + nom, pos + n * 0.004, n, 0.0420)      # rond et noir, sans paupière : l'anneau argent faisait un hublot
    p, n = a.surface("corps", CENTRE, Vector((0.0, -0.98, -0.12)))
    lèvre = A.tore(0.022, 0.010, 32, 8)
    a.piece("bouche", lèvre, tuple(GRIS * 0.62), mat=A.cadre(p + n * 0.004, n), poil=False)
    a.tete = CENTRE + Vector((0.0, -0.10, 0.03))                # le gros plan vise le visage entier, pas le flanc

    # ----- deux petites pectorales, qui battent comme des mains ; la gauche pendante -----
    for nom, c in (("G", 1), ("D", -1)):
        pec = A.boule(1.0, 24, 12).etire(0.014, 0.078, 0.086)
        pec.teinte = np.tile(GRIS * 1.1, (len(pec.v), 1))
        a.piece("pectorale_" + nom, pec, None, pos=(c * 0.108, 0.010, 0.760), rot=(0, 0, c * -22), poil=False)
    # la fente des ouïes : un trait brodé derrière l'œil, de chaque côté
    for c in (1, -1):
        pts = []
        for u_ in np.linspace(0.0, 1.0, 6):
            q = a.trace("corps", CENTRE, [Vector((c * 0.95, -0.10 + 0.06 * u_, 0.34 - 0.62 * u_))], 0.002)
            if q:
                pts.append(q[0])
        if len(pts) > 1:
            a.broderie("ouie_" + ("G" if c > 0 else "D"), A.courbe(pts, 3), 0.0030, FIL)
    if TOURNE:
        O.tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("poisson_lune", styles.style_de("poisson_lune"), sys.modules[__name__]), "Poisson-lune")
