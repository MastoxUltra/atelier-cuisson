"""La pieuvre en peluche, deuxième dessin : une grosse tête bombée brique sombre, deux yeux malins sous une paupière lourde, et
huit bras qui partent naturellement de DESSOUS la tête, rayonnent tout autour, s'étalent en S sur le sable et se
recourbent au bout. Un seul se lève, devant à gauche, en point d'interrogation (elle vous fait signe de patienter) ; les
ventouses crème se voient sous lui et sous deux bouts recourbés. Elle a l'air de préparer un coup, et elle y réussira.
(le premier dessin, jugé le 15/10 par l'auteur : « les tentacules doivent partir du dessous de la tête et s'étaler »)

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


def trace_bras(th0, long, onde, boucle, leve=0.0, rayon=0.078, n=18):
    """Le chemin d'un bras qui part de DESSOUS la tête (sa racine est sous le dôme, un peu au-dessus du sable), descend vers le
    sable en moins du premier tiers, puis s'étale en S doux (onde) et se recourbe au bout (boucle). leve : de combien
    le bras se dresse en l'air (il garde alors son S et sa boucle)."""
    pts = []
    for t in np.linspace(0.0, 1.0, n):
        r = 0.060 + long * t ** 0.92
        th = th0 + onde * math.sin(2.0 * math.pi * 1.05 * t) + boucle * max(0.0, t - 0.55) ** 2 * 5.0
        rr = rayon * (1.0 - t) ** 0.85 + 0.010
        tombe = 0.150 * max(0.0, 1.0 - t / 0.30) ** 2                      # la descente de la racine vers le sable
        z = rr * 0.95 + 0.002 + tombe + leve * t ** 1.4
        pts.append((r * math.cos(th), 0.03 + r * math.sin(th), z))
    return pts


def bras(th0, long, onde, boucle, leve=0.0, rayon=0.078):
    pts = trace_bras(th0, long, onde, boucle, leve, rayon)
    return A.tube(A.courbe(pts, 4), lambda t: rayon * (1.0 - t) ** 0.85 + 0.010, 14), pts


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
        a.piece("lourde_" + nom, K.paupiere(0.040, 0.60), tuple(BRIQUE), mat=A.cadre(pos + n * 0.003, n, haut_oeil), poil=False)
    sourire = [Vector((0.30 * u_ + 0.04, -0.94, -0.30 + 0.10 * u_ * u_)) for u_ in np.linspace(-1, 1, 9)]
    a.broderie("sourire", A.courbe(a.trace("tete", centre, sourire, 0.004), 4), 0.0030, FIL)
    a.tete = centre + Vector((0.0, -0.18, 0.0))

    # ----- les huit bras : ils partent du dessous de la tête, rayonnent tout autour, s'étalent en S sur le sable et se
    #       recourbent au bout ; celui de devant à gauche se lève pour un signe (en gardant son S et sa boucle) -----
    config = [(-0.78, 0.50, 0.30, +1.6, 0.0),                      # devant à gauche : POSÉ au sol comme les autres (l'auteur : tentacules baissés par défaut)
              (-1.58, 0.46, -0.28, -1.2, 0.0), (-2.36, 0.50, 0.30, 1.0, 0.0), (-3.14, 0.52, -0.26, -1.4, 0.0),
              (2.36, 0.52, 0.28, 1.3, 0.0), (1.58, 0.48, -0.30, -1.0, 0.0), (0.78, 0.50, 0.26, 1.5, 0.0), (0.00, 0.46, -0.28, -1.1, 0.0)]
    pastilles = None
    for k, (th0, long, onde, boucle, leve) in enumerate(config):
        m, pts = bras(th0, long, onde, boucle, leve)
        a.piece("bras_%d" % k, m, tuple(BRIQUE))
        # les ventouses : une rangée de pastilles crème sous le bras levé et sous les bouts qui se recourbent
        if leve > 0.0 or k in (3, 5):
            for tt in np.linspace(0.18, 0.88, 7):
                r = 0.060 + long * tt ** 0.92
                th = th0 + onde * math.sin(2.0 * math.pi * 1.05 * tt) + boucle * max(0.0, tt - 0.55) ** 2 * 5.0
                rr = 0.078 * (1.0 - tt) ** 0.85 + 0.010
                tombe = 0.150 * max(0.0, 1.0 - tt / 0.30) ** 2
                z = rr * 0.95 + 0.002 + tombe + leve * tt ** 1.4
                p = Vector((r * math.cos(th), 0.03 + r * math.sin(th), z + rr * 0.80))
                pt = couche(A.boule(1.0, 14, 8).etire(0.016 * (1 - 0.4 * tt), 0.016 * (1 - 0.4 * tt), 0.0065), A.cadre(p, Vector((0.0, -0.4, 1.0))))
                pastilles = pt if pastilles is None else pastilles + pt
    if pastilles is not None:
        a.piece("ventouses", pastilles, CREME, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "bras")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pieuvre", styles.style_de("pieuvre"), sys.modules[__name__]), "Pieuvre")
