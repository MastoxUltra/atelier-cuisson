"""La méduse en peluche, deuxième dessin : une diva qui flotte. Une cloche lavande festonnée, renversée en arrière comme un
menton qu'on lève, bordée d'une jupe pâle qui ondule ; dessous, quatre longs bras-rubans plissés en volants, d'un lavande
plus soutenu à l'ourlet pâle, qui traînent jusqu'au sol en S, l'un lancé de côté comme un boa. De petits yeux mi-clos
sous une lourde paupière, trois cils chacun, une moue de travers : elle n'a jamais pensé à vous. Pas de bouton à croix,
pas de sourire de bébé : l'air d'être très belle, et au courant.

    python meduse.py        fabrique la fiche art/apercus/animaux/meduse.png (style du palier : A, cousu main)
    (le premier dessin, refusé le 15/10 : « des yeux à croix et un sourire, donc du bébé »)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import matieres as M
import peluche as K
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

LAVANDE = np.array(M.hexa("#b9a3e3"))         # la dominante (registre : lavande translucide)
HAUT = np.array(M.hexa("#a58ad8"))            # le dessus de la cloche, un peu plus soutenu
PALE = np.array(M.hexa("#ece3fb"))            # l'ourlet, la jupe, les filaments
RUBAN = np.array(M.hexa("#9479d8"))           # les rubans
CIL = M.hexa("#2b1d47")
FIL = M.hexa("#3a2a5e")
HAUTEUR = 0.46                                # la hauteur du bord de la cloche au-dessus du sol


def ruban(base_ang, longueur, balancement, phase, largeur=0.062, n=18):
    """Un bras-ruban plissé : une suite de petites lames aplaties, inclinées en alternance, le long d'un chemin ondulé
    qui descend en S. Retourne la maille et le chemin."""
    pts = []
    for k in range(n + 1):
        t = k / n
        r = 0.050 + 0.100 * math.sin(math.pi * t) + 0.120 * t
        ang = base_ang + balancement * math.sin(math.tau * (0.9 * t) + phase)
        pts.append(Vector((r * math.cos(ang), r * math.sin(ang), -0.030 - longueur * t)))
    maille = None
    for k in range(n):
        t = k / n
        a_, b_ = pts[k], pts[k + 1]
        tang = (b_ - a_).normalized()
        centre = (a_ + b_) * 0.5
        rad = Vector((centre.x, centre.y, 0.0))
        rad = rad.normalized() if rad.length > 1e-6 else Vector((1.0, 0.0, 0.0))
        rad = (rad - tang * rad.dot(tang)).normalized()
        roule = Matrix.Rotation(math.radians(28 if k % 2 == 0 else -28), 3, tang)
        haut_ = roule @ rad
        larg = largeur * (0.75 + 0.35 * math.sin(math.pi * min(1.0, t * 1.1)))
        lame = A.boule(1.0, 16, 8).etire(larg, 0.0085, (b_ - a_).length * 0.80)
        ex = np.abs(lame.v[:, 0]) / larg                                    # le milieu plus soutenu, l'ourlet pâle
        lame.teinte = np.where((ex > 0.62)[:, None], PALE, RUBAN)
        lame = O.couche(lame, A.cadre(centre, tang, haut_))
        maille = lame if maille is None else maille + lame
    return maille, pts


def construire():
    a = K.Animal("meduse")
    a.taille = 0.66
    T = A.repere((0.0, 0.0, HAUTEUR), (-16, 0, 0))          # la cloche renversée : le menton levé
    T3 = T.to_3x3()

    # ----- la cloche : un dôme à bord festonné (douze lobes), plus soutenu dessus, pâle à l'ourlet -----
    def feston(v):
        s = v.copy()
        ang = np.arctan2(v[:, 1], v[:, 0])
        bas = K.lisse((0.075 - v[:, 2]) / 0.075)
        k = 1 + 0.085 * bas * np.cos(12 * ang)
        s[:, 0] *= k
        s[:, 1] *= k
        s[:, 2] -= 0.026 * bas * (0.5 + 0.5 * np.cos(12 * ang))
        return s
    prof = A.profil([(0, 0.0), (0.160, 0.0), (0.198, 0.016), (0.202, 0.060), (0.176, 0.125), (0.118, 0.178), (0.052, 0.205), (0, 0.214)], 5)
    cloche = A.tour(prof, 72)
    zf = np.clip(cloche.v[:, 2] / 0.214 * 1.2, 0, 1)[:, None]
    cloche.teinte = LAVANDE * (1 - zf) + HAUT * zf
    a.piece("cloche", cloche.sculpte(feston), None, mat=T)

    def jupe_(v):
        s = v.copy()
        ang = np.arctan2(v[:, 1], v[:, 0])
        s[:, 2] += 0.030 * np.sin(9 * ang)
        return s
    jupe = A.tore(0.205, 0.020, 72, 10).sculpte(jupe_)
    a.piece("jupe", O.teinte(jupe, PALE), None, mat=T @ A.repere((0, 0, -0.004)), poil=False)

    # ----- le visage : des yeux mi-clos sous une lourde paupière, trois cils par œil, une moue de travers -----
    centre = T @ Vector((0.0, 0.0, 0.080))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("cloche", centre, T3 @ Vector((c * 0.40, -0.90, 0.04)))
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0165)
        haut_ = (T3 @ Vector((0, 0, 1)) - n * n.dot(T3 @ Vector((0, 0, 1)))).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.0165, -0.12), tuple(LAVANDE), mat=A.cadre(pos + n * 0.002, n, haut_), poil=False)
        lat = n.cross(haut_) * c
        for k, dx in enumerate((-0.010, 0.003, 0.016)):
            base = pos + n * 0.003 + haut_ * 0.015 + lat * dx
            bout = base + haut_ * 0.020 + lat * (dx * 2.0 + 0.006 * c) + n * 0.008
            milieu = base + (bout - base) * 0.5 + n * 0.004
            a.piece("cil_%s%d" % (nom, k), O.teinte(O.tube_r([tuple(base), tuple(milieu), tuple(bout)], [0.0020, 0.0017, 0.0010], 6), np.array(CIL)),
                    None, poil=False)
    O.broder(a, "moue", "cloche", centre,
             [tuple(T3 @ Vector((0.22 * u_ + 0.10, -0.96, -0.32 + 0.10 * u_ * u_ + 0.06 * u_))) for u_ in np.linspace(-1, 1, 9)], 0.0021, FIL, decolle=0.002)
    a.tete = centre + T3 @ Vector((0, -0.20, 0.0))

    # ----- les quatre rubans : plissés en volants, longs, en S ; le plus long lancé de côté comme un boa -----
    for k, (ang, longu, bal, ph) in enumerate(((0.3, 0.38, 0.55, 0.0), (1.9, 0.33, 0.60, 1.4), (3.5, 0.36, 0.50, 2.8), (5.0, 0.42, 0.90, 4.2))):
        m, pts = ruban(ang, longu, bal, ph)
        a.piece("ruban_%d" % k, O.couche(m, T), None, poil=False)

    # ----- les filaments : quelques longs fils pâles qui partent du bord et traînent jusqu'au sol -----
    for k in range(6):
        ang = math.tau * k / 6 + 0.4
        cx, cy = math.cos(ang), math.sin(ang)
        long_ = 0.40 + 0.06 * math.sin(2.7 * k)
        chemin = [(0.185 * cx, 0.185 * cy, -0.006), (0.200 * cx + 0.022 * cy, 0.200 * cy - 0.022 * cx, -0.10),
                  (0.180 * cx - 0.030 * cy, 0.180 * cy + 0.030 * cx, -0.22), (0.205 * cx + 0.018 * cy, 0.205 * cy - 0.018 * cx, -long_)]
        pts = [tuple(T @ Vector(p)) for p in A.courbe(chemin, 5)]
        a.piece("filament_%d" % k, O.teinte(A.tube(pts, lambda t_: 0.0062 - 0.0030 * t_, 8), PALE), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "meduse")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("meduse", styles.style_de("meduse"), sys.modules[__name__]), "Méduse")
