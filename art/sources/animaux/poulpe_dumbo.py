"""Le poulpe dumbo en peluche : le plus tendre du fond, rose saumon pâle, une tête-manteau ronde comme un ballon, deux
grandes nageoires en grandes oreilles rondes qui battent de chaque côté, de gros yeux ronds sous une paupière douce, et huit bras
courts, réunis à la base par une jupe de peau en feston. Il nage en battant des oreilles, très lentement, au ras de la vase :
c'est le plus mignon des animaux abyssaux, et il n'en a jamais rien su.

    python poulpe_dumbo.py        fabrique la fiche art/apercus/animaux/poulpe_dumbo.png (style du palier : voir styles.py)
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

SAUMON = np.array(M.hexa("#f4b3a0"))          # la dominante (registre : rose saumon pâle)
OREILLE = np.array(M.hexa("#fbd2c4"))         # l'accent : les nageoires-oreilles plus claires
VENTOUSE = np.array(M.hexa("#fff0e6"))
FIL = M.hexa("#8a4a40")


def trace_bras(th0, long, onde, boucle, rayon=0.050, n=14):
    """Un bras court qui part de dessous la tête, descend au sol en un tiers, puis s'étale en S et se recourbe au bout."""
    pts = []
    for t in np.linspace(0.0, 1.0, n):
        r = 0.045 + long * t ** 0.92
        th = th0 + onde * math.sin(2.0 * math.pi * 1.0 * t) + boucle * max(0.0, t - 0.55) ** 2 * 5.0
        rr = rayon * (1.0 - t) ** 0.85 + 0.008
        z = rr * 0.95 + 0.002 + 0.110 * max(0.0, 1.0 - t / 0.30) ** 2
        pts.append((r * math.cos(th), 0.02 + r * math.sin(th), z))
    return pts


def construire():
    a = K.Animal("poulpe_dumbo")
    a.taille = 0.30

    # ----- la tête-manteau : un dôme rond, un peu pincé en bas ; la jupe de peau sous lui -----
    def forme(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 0] *= 1 - 0.16 * np.clip(-z, 0, 1)
        s[:, 1] *= 1 - 0.16 * np.clip(-z, 0, 1)
        return s
    tete = A.boule(1.0, 52, 26)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(SAUMON, (len(u), 1))
    t[u[:, 2] < -0.35] = SAUMON * 1.04
    tete.teinte = t
    a.piece("tete", tete.sculpte(forme).etire(0.170, 0.165, 0.165).pose((0.0, 0.020, 0.215)), None)
    # ----- le visage : deux gros yeux ronds sous une paupière douce, un sourire minuscule -----
    centre = Vector((0.0, 0.020, 0.215))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, Vector((c * 0.58, -0.80, 0.02)))
        a.oeil("oeil_" + nom, pos + n * 0.003, n, 0.044)
        haut_oeil = (Vector((0, 0, 1)) - n * n.z).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.044, 0.18), tuple(SAUMON), mat=A.cadre(pos + n * 0.003, n, haut_oeil), poil=False)
    sourire = [Vector((0.16 * u_, -0.96, -0.30 + 0.07 * u_ * u_)) for u_ in np.linspace(-1, 1, 7)]
    a.broderie("sourire", A.courbe(a.trace("tete", centre, sourire, 0.004), 4), 0.0028, FIL)
    a.tete = centre + Vector((0.0, -0.18, 0.0))

    # ----- les deux nageoires en grandes oreilles rondes : des éventails arrondis, dressés de chaque côté du dôme -----
    contour = []
    for k in range(40):
        th = math.tau * k / 40
        r = 0.150 * (1.0 + 0.14 * math.cos(2 * th)) * (0.90 + 0.10 * math.cos(th))
        contour.append((0.100 + r * 0.95 * math.cos(th) + 0.06, r * 0.70 * math.sin(th)))
    for nom, c in (("G", 1), ("D", -1)):
        oreille = A.decoupe(contour, 0.016, 0.007)               # le plan miroir fait déjà la nageoire de l'autre côté : les DEUX se voient
        oreille.teinte = np.tile(OREILLE, (len(oreille.v), 1))
        R = O.plan(Vector((c * 0.105, 0.030, 0.255)), Vector((c * 0.93, 0.0, 0.25)), Vector((c * 0.10, 0.0, 1.0)))
        a.piece("nageoire_" + nom, O.couche(oreille, R), None, poil=False)

    # ----- les huit bras courts, du dessous de la tête, étalés en S et recourbés ; quelques ventouses sous les bouts -----
    config = [(-0.78, 0.30, 0.26, +1.4), (-1.58, 0.27, -0.24, -1.1), (-2.36, 0.30, 0.26, 0.9), (-3.14, 0.28, -0.24, -1.3),
              (2.36, 0.30, 0.26, 1.2), (1.58, 0.27, -0.26, -0.9), (0.78, 0.30, 0.24, 1.3), (0.00, 0.27, -0.26, -1.0)]
    ventouses = None
    for k, (th0, long, onde, boucle) in enumerate(config):
        pts = trace_bras(th0, long, onde, boucle)
        m = A.tube(A.courbe(pts, 4), lambda t_: 0.050 * (1.0 - t_) ** 0.85 + 0.008, 12)
        m.teinte = np.tile(SAUMON, (len(m.v), 1))
        a.piece("bras_%d" % k, m, None)
        if k in (0, 3, 5):
            for tt in np.linspace(0.4, 0.9, 4):
                x, y, z = pts[int(tt * (len(pts) - 1))]
                p = Vector((x, y, z + 0.016))
                pt = O.couche(O.teinte(A.boule(1.0, 10, 6).etire(0.0095, 0.0095, 0.0040), VENTOUSE), A.cadre(p, Vector((0.0, -0.3, 1.0))))
                ventouses = pt if ventouses is None else ventouses + pt
    a.piece("ventouses", ventouses, None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "bras")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("poulpe_dumbo", styles.style_de("poulpe_dumbo"), sys.modules[__name__]), "Poulpe dumbo")
