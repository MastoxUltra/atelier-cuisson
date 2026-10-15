"""La pieuvre en peluche : une grosse tête bombée brique sombre, deux yeux malins sous une paupière lourde, et huit bras
qui s'enroulent sur le sable comme des cordes de marin. Elle se tient à demi dressée sur le dessus de la tête, un bras
levé (elle vous fait signe de patienter), un autre en point d'interrogation ; les ventouses crème se voient sous les bras
levés. Elle a l'air de préparer un coup, et elle y réussira.

    python pieuvre.py        fabrique la fiche art/apercus/animaux/pieuvre.png (style du palier : C, velours ras)
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

BRIQUE = np.array(M.hexa("#a8442f"))          # la dominante (registre : brique sombre) ; le velours éclaircit
HAUT = np.array(M.hexa("#8a3524"))            # le dessus de la tête, plus sombre
CLAIR = np.array(M.hexa("#cf6c52"))           # le dessous des bras, plus clair
CREME = K.CREME
FIL = M.hexa("#3a1710")


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def bras(depart, angle, long, tours=0.0, leve=0.0, rayon=0.062):
    """Un bras : un tube peint qui part de dessous la tête, s'étale en spirale lâche sur le sable (tours > 0 : il s'enroule,
    < 0 : dans l'autre sens) ; si leve > 0, il se dresse en l'air et se courbe au bout."""
    pts = []
    for t in np.linspace(0.0, 1.0, 14):
        r = 0.10 + long * t
        th = angle + tours * t ** 1.6
        z = rayon * (1 - 0.9 * t) + 0.004 + leve * (t ** 1.3)
        pts.append((r * math.cos(th) + depart[0], r * math.sin(th) + depart[1], z))
    return A.tube(A.courbe(pts, 4), lambda t: rayon * (1 - t) ** 0.9 + 0.012, 14)


def construire():
    a = K.Animal("pieuvre")
    a.taille = 1.00

    # ----- la tête : un grand dôme penché en arrière, plus sombre dessus ; sous les yeux elle se rétrécit en cou -----
    def forme(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 0] *= 1 - 0.18 * np.clip(-z, 0, 1)
        s[:, 1] *= 1 - 0.18 * np.clip(-z, 0, 1)
        s[:, 1] += 0.16 * np.clip(z, 0, None) ** 1.6                    # le sommet part en arrière
        return s
    tete = A.boule(1.0, 56, 28)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = HAUT * np.clip((u[:, [2]] + 0.2) / 1.2, 0, 1) + BRIQUE * (1 - np.clip((u[:, [2]] + 0.2) / 1.2, 0, 1))
    tete.teinte = t
    a.piece("tete", tete.sculpte(forme).etire(0.270, 0.245, 0.250).pose((0.0, 0.03, 0.300)), None)

    # ----- le visage : deux gros yeux sous une paupière lourde, un petit sourire en coin -----
    centre = Vector((0.0, 0.03, 0.290))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, Vector((c * 0.62, -0.78, 0.04)))
        a.oeil("oeil_" + nom, pos + n * 0.003, n, 0.040)
        haut_oeil = (Vector((0, 0, 1)) - n * n.z).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.040, 0.10), tuple(BRIQUE), mat=A.cadre(pos + n * 0.003, n, haut_oeil), poil=False)
    sourire = [Vector((0.30 * u_ + 0.04, -0.94, -0.30 + 0.10 * u_ * u_)) for u_ in np.linspace(-1, 1, 9)]
    a.broderie("sourire", A.courbe(a.trace("tete", centre, sourire, 0.004), 4), 0.0030, FIL)
    a.tete = centre + Vector((0.0, -0.18, 0.0))

    # ----- les huit bras : à plat sur le sable, enroulés ; un levé, un en point d'interrogation -----
    base = (0.0, 0.0)
    config = [(-0.55, 0.30, +1.2, 0.0), (-1.35, 0.34, -0.9, 0.0), (0.30, 0.34, +0.6, 0.0), (1.20, 0.36, -1.1, 0.0),
              (2.00, 0.34, +0.9, 0.0), (2.85, 0.32, -0.5, 0.0), (3.80, 0.34, 0.9, 0.0), (5.30, 0.30, -0.7, 0.0)]
    # le bras levé (devant à gauche) et le bras en point d'interrogation (devant à droite)
    levee = bras(base, math.radians(-50), 0.18, tours=0.4, leve=0.42)
    a.piece("bras_leve", levee, tuple(BRIQUE))
    point = bras(base, math.radians(-130), 0.20, tours=-0.5, leve=0.26)
    a.piece("bras_point", point, tuple(BRIQUE))
    for k, (ang, long, tours, leve) in enumerate(config):
        if -2.0 < ang < -0.3 and k in (0, 1):
            continue
        a.piece("bras_%d" % k, bras(base, ang, long, tours, leve), tuple(BRIQUE))

    # ----- les ventouses : une rangée de pastilles crème sous le bras levé et dans la boucle du point d'interrogation -----
    pastilles = None
    for k, (ang, long, tours, leve) in enumerate(((math.radians(-50), 0.18, 0.4, 0.42), (math.radians(-130), 0.20, -0.5, 0.26))):
        for tt in np.linspace(0.12, 0.85, 7):
            r = 0.10 + long * tt
            th = ang + tours * tt ** 1.6
            z = 0.062 * (1 - 0.9 * tt) + 0.004 + leve * (tt ** 1.3)
            rayon_ = 0.062 * (1 - tt) ** 0.9 + 0.012
            p = Vector((r * math.cos(th), r * math.sin(th), z + rayon_ * 0.85))
            m = couche(A.boule(1.0, 14, 8).etire(0.016 * (1 - 0.4 * tt), 0.016 * (1 - 0.4 * tt), 0.0065), A.cadre(p, Vector((0.0, -0.4, 1.0))))
            pastilles = m if pastilles is None else pastilles + m
    a.piece("ventouses", pastilles, CREME, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pieuvre", styles.style_de("pieuvre"), sys.modules[__name__]), "Pieuvre")
