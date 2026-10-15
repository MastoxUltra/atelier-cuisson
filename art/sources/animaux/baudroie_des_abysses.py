"""La baudroie des abysses en peluche : une grosse boule aubergine toute en bouche, posée au fond du noir. Une
gueule énorme coupée à l'équerre, bordée de dents de feutrine blanche mal alignées, deux petits yeux de rien, et au bout
d'une tige qui part du front une lanterne jaune citron qui pend devant le museau : elle attend qu'on s'approche pour
voir ce que c'est. Les nageoires sont des moignons posés sur le sable comme des mains.

    python baudroie_des_abysses.py        fabrique la fiche art/apercus/animaux/baudroie_des_abysses.png (style du palier : B)
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

AUBERGINE = np.array(M.hexa("#4a3248"))       # la dominante (registre : aubergine sombre) ; le style B éclaircit un peu
GRIS = np.array(M.hexa("#7b6a7a"))            # le dessous, les nageoires
CITRON = M.hexa("#fff04a")                    # l'accent : la lanterne
DENT = M.hexa("#fbf7ea")
BOUCHE = np.array(M.hexa("#241522"))          # l'intérieur de la gueule
FIL = M.hexa("#16101a")


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def construire():
    a = K.Animal("baudroie_des_abysses")
    a.taille = 1.00

    # ----- le corps : une grosse boule aplatie, la gueule en dessous du front ; plus sombre dessus -----
    def forme(v):
        s = v.copy()
        s[:, 0] *= 0.96
        s[:, 1] *= 1.06
        s[:, 2] = np.where(v[:, 2] < 0, v[:, 2] * 0.75, v[:, 2] * 1.0)
        s[:, 1] -= 0.05 * np.clip(-v[:, 2], 0, 1) * (v[:, 1] < 0)       # la mâchoire inférieure avance
        return s
    corps = A.boule(1.0, 64, 32)
    u = corps.v / np.maximum(np.linalg.norm(corps.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(AUBERGINE, (len(u), 1))
    t[u[:, 2] < -0.25] = GRIS
    corps.teinte = t
    a.piece("corps", corps.sculpte(forme).etire(0.280, 0.300, 0.250), None, pos=(0.0, 0.0, 0.250))

    # ----- la gueule : une fente énorme sur le devant, l'intérieur sombre, deux rangées de dents irrégulières -----
    CENTRE = Vector((0.0, 0.0, 0.240))
    haut, bas = [], []
    for u_ in np.linspace(-1.0, 1.0, 13):
        haut.append(Vector((0.92 * u_, -0.98, 0.10 + 0.14 * u_ * u_)))
        bas.append(Vector((0.92 * u_, -0.92, -0.12 + 0.20 * u_ * u_)))
    lèvre = [a.trace("corps", CENTRE, [d], 0.004)[0] for d in haut]
    a.broderie("gueule_haut", A.courbe(lèvre, 4), 0.0075, FIL)
    menton = [a.trace("corps", CENTRE, [d], 0.004)[0] for d in bas]
    a.broderie("gueule_bas", A.courbe(menton, 4), 0.0075, FIL)
    rng = np.random.default_rng(4)
    for k, u_ in enumerate(np.linspace(-0.85, 0.85, 11)):
        for rang, y_ in (("h", 0.06 + 0.15 * u_ * u_), ("b", -0.10 + 0.19 * u_ * u_)):
            q = a.trace("corps", CENTRE, [Vector((0.92 * u_, -0.96, y_ + (0.02 if rang == "b" else -0.02)))], 0.003)
            if not q:
                continue
            long = 0.050 + 0.030 * rng.random()
            dent = A.tour(A.profil([(0.014, 0), (0.0095, 0.020), (0.0042, 0.042), (0, long)], 3), 8)
            sens = (0.0, 0.3, -1.0) if rang == "h" else (0.0, 0.3, 1.0)
            a.piece("dent_%s%d" % (rang, k), couche(dent, A.cadre(q[0], sens, (0, 1, 0))), DENT, poil=False)

    # ----- la lanterne : une tige qui part du front, se penche devant le museau et finit par une boule jaune citron -----
    tige = A.tube(A.courbe([(0.0, -0.06, 0.470), (0.0, -0.18, 0.640), (0.0, -0.36, 0.680), (0.0, -0.46, 0.580)], 5),
                  lambda t_: 0.014 - 0.006 * t_, 12)
    tige.teinte = np.tile(AUBERGINE * 1.1, (len(tige.v), 1))
    a.piece("tige", tige, None, poil=False)
    a.piece("lanterne", A.boule(1.0, 28, 14).etire(0.052, 0.052, 0.058), CITRON, pos=(0.0, -0.46, 0.540), poil=False)
    a.piece("halo", A.tore(0.062, 0.0045, 28, 6), CITRON, pos=(0.0, -0.46, 0.540), rot=(90, 0, 0), poil=False)

    # ----- les yeux : tout petits, haut sur le côté, l'air pas content ; les nageoires moignons -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("corps", Vector((0.0, 0.0, 0.250)), Vector((c * 0.74, -0.60, 0.62)))
        a.bouton("oeil_" + nom, pos + n * 0.002, n, 0.0175)
        nag = A.boule(1.0, 20, 10).etire(0.030, 0.085, 0.110)
        nag.teinte = np.tile(GRIS, (len(nag.v), 1))
        a.piece("nageoire_" + nom, nag, None, pos=(c * 0.285, 0.020, 0.115), rot=(0, 0, c * 18), poil=False)
    a.tete = Vector((0.0, -0.30, 0.240))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("baudroie_des_abysses", styles.style_de("baudroie_des_abysses"), sys.modules[__name__]),
              "Baudroie des abysses")
