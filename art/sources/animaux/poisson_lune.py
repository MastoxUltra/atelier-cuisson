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
TOURNE = -20                                  # trois quarts ouvert : les ailerons de biais et les deux yeux avancés (Principal, 16/10) ; 0 pour le jeu


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def construire():
    a = K.Animal("poisson_lune")
    a.taille = 3.00

    # (16/10, passé à la session Art après six essais : le disque se lisait comme une tranche mince, un seul œil, des
    # ailerons en lames, pas de clavus) : un DISQUE de peluche, aussi haut que long, épais devant (le visage large, les deux
    # yeux se voient de trois quarts) et plus mince derrière ; deux grandes nageoires épaisses, haute et basse, rejetées
    # vers l'arrière comme chez la vraie môle ; et derrière, le CLAVUS : la queue tronquée, un bord ondulé en festons
    ZC = 0.700                                     # debout sur sa nageoire du bas
    def galet(v):
        s = np.zeros_like(v)
        s[:, 0] = v[:, 0] * (0.165 - 0.060 * np.clip(v[:, 1], 0, 1)) * (1 - 0.30 * np.abs(v[:, 2]) ** 2)   # épais devant
        s[:, 1] = 0.320 * v[:, 1]
        s[:, 2] = 0.320 * v[:, 2] * (1 - 0.10 * np.clip(-v[:, 1], 0, None) ** 1.5 * (v[:, 2] > 0))           # le front qui fuit
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
    a.piece("corps", corps.sculpte(galet), None, pos=(0.0, 0.0, ZC))

    # ----- le clavus : la queue tronquée, un demi-ovale plat qui borde tout l'arrière du disque, au bord en festons -----
    contour = [(-0.050, 0.300)]
    for th in np.linspace(math.pi / 2, -math.pi / 2, 81):
        feston = 1.0 + 0.10 * abs(math.cos(5.5 * (th + math.pi / 2)))
        contour.append((0.135 * math.cos(th) * feston, 0.300 * math.sin(th)))
    contour.append((-0.050, -0.300))
    clavus = A.decoupe(contour, 0.070, 0.025)
    clavus.teinte = np.tile(GRIS, (len(clavus.v), 1))
    a.piece("clavus", couche(clavus, A.cadre((0.0, 0.285, ZC), (1.0, 0.0, 0.0), (0, 0, 1))), None, poil=False)

    # ----- les deux grandes nageoires : épaisses, larges à la base, rejetées vers l'arrière, à l'arrière du disque -----
    aileron = [(-0.130, 0.0), (-0.090, 0.140), (-0.025, 0.280), (0.055, 0.385), (0.115, 0.425), (0.158, 0.400), (0.172, 0.300),
               (0.162, 0.160), (0.140, 0.0)]
    haut = A.decoupe(aileron, 0.090, 0.035)
    haut.teinte = np.tile(GRIS * 1.08, (len(haut.v), 1))
    a.piece("dorsale", couche(haut, A.cadre((0.0, 0.150, ZC + 0.250), (1.0, 0.0, 0.0), (0, 0, 1))), None, poil=False)
    bas = A.decoupe([(x, -y) for x, y in aileron], 0.090, 0.035)
    bas.teinte = np.tile(GRIS * 1.08, (len(bas.v), 1))
    a.piece("anale", couche(bas, A.cadre((0.0, 0.150, ZC - 0.250), (1.0, 0.0, 0.0), (0, 0, 1))), None, poil=False)

    # ----- le visage : deux yeux ronds ouverts, la petite bouche en « o » devant -----
    CENTRE = Vector((0.0, 0.0, ZC))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("corps", CENTRE, Vector((c * 0.55, -0.82, 0.16)))     # avancés sur le devant, comme un poisson en peluche (Principal, 16/10)     # plus en avant : de trois quarts, les deux yeux (16/10)
        a.oeil("oeil_" + nom, pos + n * 0.004, n, 0.0420)      # rond et noir, sans paupière : l'anneau argent faisait un hublot
    p, n = a.surface("corps", CENTRE, Vector((0.0, -0.98, -0.12)))
    lèvre = A.tore(0.022, 0.010, 32, 8)
    a.piece("bouche", lèvre, tuple(GRIS * 0.62), mat=A.cadre(p + n * 0.004, n), poil=False)
    a.tete = CENTRE + Vector((0.0, -0.10, 0.03))                # le gros plan vise le visage entier, pas le flanc

    # ----- deux petites pectorales, qui battent comme des mains ; la gauche pendante -----
    for nom, c in (("G", 1), ("D", -1)):
        pec = A.boule(1.0, 24, 12).etire(0.014, 0.078, 0.086)
        pec.teinte = np.tile(GRIS * 1.1, (len(pec.v), 1))
        a.piece("pectorale_" + nom, pec, None, pos=(c * 0.150, 0.000, ZC - 0.030), rot=(0, 0, c * -22), poil=False)
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
    th = math.radians(TOURNE)
    a.cap_tete = Vector((math.sin(th), -math.cos(th), 0.0))    # l'avant de la tête (tourné avec la bête) : la vue de près
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("poisson_lune", styles.style_de("poisson_lune"), sys.modules[__name__]), "Poisson-lune")
