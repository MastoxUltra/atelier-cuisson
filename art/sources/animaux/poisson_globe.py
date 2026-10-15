"""Le poisson-globe en peluche : une grosse boule sable moucheté de brun, gonflée à bloc, qui boude. Le ventre crème,
une petite queue éventail qui dépasse derrière, deux nageoires comme des moignons, de courts piquants brun et sable
plantés sur tout le dos ; les yeux mi-clos sous une lourde paupière et la bouche en cul de poule, prête à éclater
si on l'approche. Il est gonflé pour un rien : il vient de lire une mauvaise critique.

    python poisson_globe.py        fabrique la fiche art/apercus/animaux/poisson_globe.png (style du palier : A, cousu main)
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

SABLE = np.array(M.hexa("#dcc08a"))           # la dominante (registre du 14/10 : sable piqué de brun)
BRUN = np.array(M.hexa("#7a5535"))            # les mouchetures, le bout des piquants
VENTRE = np.array(M.hexa("#fff1d0"))          # le ventre crème
FIL = M.hexa("#4a2d1c")
R = 0.150                                     # le rayon de la boule


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def construire():
    a = K.Animal("poisson_globe")
    a.taille = 0.40
    CENTRE = Vector((0.0, 0.0, R * 0.92))

    # ----- le corps : une boule gonflée, moucheté de brun sur le dos, crème sous le ventre ; il pose ses joues -----
    corps = A.boule(1.0, 56, 28)
    u = corps.v / np.maximum(np.linalg.norm(corps.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(SABLE, (len(u), 1))
    rng = np.random.default_rng(5)
    graines = rng.normal(size=(150, 3))
    graines /= np.linalg.norm(graines, axis=1, keepdims=True)
    proche = u @ graines.T > np.cos(0.10 * rng.uniform(0.7, 1.3, 150))[None, :]
    t[proche.any(axis=1)] = BRUN
    t[u[:, 2] < -0.30] = VENTRE
    corps.teinte = t

    def gonfle(v):
        for c in (1, -1):
            v = K.bosse(v, (c * 0.85, -0.45, -0.20), 0.14, 0.30)                  # les joues
        return v * [R, R * 1.02, R * 0.92]
    a.piece("corps", corps.sculpte(gonfle), None, pos=tuple(CENTRE))

    # ----- les piquants : de courts cônes sable bouts bruns, sur le dos et les flancs, jamais devant le visage ni dessous -----
    herisson = None
    n = 70
    for k in range(n):
        z = 1 - 2 * (k + 0.5) / n
        ang = math.pi * (3 - math.sqrt(5)) * k
        r = math.sqrt(1 - z * z)
        d = Vector((r * math.cos(ang), r * math.sin(ang), z))
        if d.z < -0.18 or d.dot(Vector((0.0, -1.0, 0.0))) > 0.55:
            continue
        m = A.tour(A.profil([(0.0085, 0), (0.0062, 0.016), (0.0030, 0.030), (0, 0.040)], 3), 10)
        h = np.clip(m.v[:, 2] / 0.040, 0.0, 1.0)[:, None] ** 1.2
        m.teinte = SABLE * (1 - h) + BRUN * h
        haut = (0, 0, 1) if abs(d.z) < 0.9 else (0, 1, 0)
        m = couche(m, A.cadre(CENTRE + d * (R * 0.96), d, haut))
        herisson = m if herisson is None else herisson + m
    a.piece("piquants", herisson, None, poil=False)

    # ----- le visage : les yeux mi-clos sous une lourde paupière, la bouche en cul de poule -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, n_ = a.surface("corps", CENTRE, Vector((c * 0.50, -0.82, 0.22)))
        a.bouton("oeil_" + nom, pos + n_ * 0.002, n_, 0.0295)
        haut_oeil = (Vector((0, 0, 1)) - n_ * n_.z).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.0295, 0.04), tuple(SABLE), mat=A.cadre(pos + n_ * 0.002, n_, haut_oeil), poil=False)
    levre = A.tore(0.021, 0.0075, 28, 8)
    p, n_ = a.surface("corps", CENTRE, Vector((0.0, -0.98, -0.10)))
    a.piece("bouche", levre, tuple(BRUN), mat=A.cadre(p + n_ * 0.003, n_), poil=False)
    a.tete = p + n_ * 0.04

    # ----- la queue en éventail, deux nageoires-moignons, la petite dorsale -----
    queue = A.boule(1.0, 28, 14).etire(0.006, 0.060, 0.070)
    queue.teinte = np.tile(SABLE * 0.92, (len(queue.v), 1))
    a.piece("queue", couche(queue, A.cadre(CENTRE + Vector((0.0, R * 1.04, -0.012)), (0.12, 1.0, 0.12), (0, 0, 1))), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        n_ = A.boule(1.0, 20, 10).etire(0.006, 0.040, 0.034)
        n_.teinte = np.tile(SABLE * 0.92, (len(n_.v), 1))
        a.piece("nageoire_" + nom, couche(n_, A.cadre(CENTRE + Vector((c * R * 0.96, -0.012, -0.032)), (c * 1.0, -0.2, 0.5), (0, 0, 1))),
                None, poil=False)
    dorsale = A.boule(1.0, 20, 10).etire(0.006, 0.034, 0.040)
    dorsale.teinte = np.tile(BRUN * 1.1, (len(dorsale.v), 1))
    a.piece("dorsale", couche(dorsale, A.cadre(CENTRE + Vector((0.0, 0.050, R * 0.98)), (0, 1.0, 0.0), (0, 0, 1))), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("poisson_globe", styles.style_de("poisson_globe"), sys.modules[__name__]), "Poisson-globe")
