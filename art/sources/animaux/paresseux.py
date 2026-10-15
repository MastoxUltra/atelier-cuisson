"""Le paresseux en peluche de velours ras : un beige lichen tout hirsute, des mèches qui lui pendent du corps comme de
la mousse, la face crème et ronde sous deux grands masques chocolat qui lui font un sourire permanent, et des bras
démesurés aux trois longues griffes crème. Le roi de la lenteur : assis en tas, la tête penchée de côté sur l'épaule,
les yeux presque fermés, les bras qui pendent jusqu'au sol, un bout de sourire : il n'a pas encore fini d'y penser.

    python paresseux.py        fabrique la fiche art/apercus/animaux/paresseux.png (velours ras, palier 3)
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


def propres(points, eps=2e-4):
    """Les points d'un tracé sans doublons consécutifs (un tube dont deux points se suivent à l'identique se déforme en NaN) ;
    au moins deux points, écartés d'un millimètre au pire."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie

LICHEN = M.hexa("#e4d9b4")                    # la dominante : beige lichen (le poil le dore : on le prend clair)
MOUSSE = M.hexa("#d0c898")                    # les mèches, un ton plus bas, un rien verdi
CREME = M.hexa("#fffbe8")                     # la face
CHOCOLAT = M.hexa("#5a4030")                  # l'accent : les masques d'œil, le nez
GRIFFE = M.hexa("#f2e4c0")                    # les griffes
CORPS = Vector((0.0, 0.040, 0.250))
TETE = Vector((0.0, -0.100, 0.455))
LACET, PENCHE = 18.0, 14.0                    # la tête tournée vers nous, penchée sur l'épaule


def meche(chemin, large, face, plat=0.40, cotes=14):
    """Une mèche plate (le geste des mèches du cheval) couchée le long d'un chemin."""
    p = A.courbe(chemin, 8)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    n0 = np.asarray(face, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.linalg.norm(t, axis=1, keepdims=True)
        x = np.cross(n0, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.60 * large, 0.05 * L), (0.95 * large, 0.22 * L), (large, 0.42 * L), (0.72 * large, 0.70 * L),
                     (0.30 * large, 0.93 * L), (0.06 * large, 0.985 * L), (0, L)], 5)
    return A.tour(prof, cotes).etire(1.0, plat, 1.0).sculpte(couche)


def construire():
    a = K.Animal("paresseux")
    a.taille = 0.80

    # ----- le corps : un gros tas rond, le dos voûté, le ventre qui s'étale sur le sol -----
    def tas(v):
        v = K.bosse(v, (0, -0.8, 0.2), 0.10, 0.5)
        s = v * [0.185, 0.175, 0.200]
        s[:, 2] = np.where(s[:, 2] < 0, s[:, 2] * 0.85, s[:, 2])
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(tas), LICHEN, pos=CORPS)

    # ----- des mèches de mousse : des longues mèches plates qui pendent des flancs et du dos, comme du lichen -----
    rng = np.random.default_rng(11)
    meches = None
    for i in range(22):
        t = 2 * math.pi * (i + rng.uniform(-0.3, 0.3)) / 22
        base = np.array([0.168 * math.cos(t), CORPS.y + 0.160 * math.sin(t)])
        radial = np.array([math.cos(t), math.sin(t)])
        hz = CORPS.z + rng.uniform(-0.01, 0.07)
        k = 0.8 + 0.5 * rng.random()
        chemin = [(base[0] * 0.92, base[1] * 0.92 + CORPS.y * 0.08, hz + 0.04), (base[0], base[1], hz - 0.04),
                  (base[0] + radial[0] * 0.035, base[1] + radial[1] * 0.035, hz - 0.10 * k),
                  (base[0] + radial[0] * 0.050, base[1] + radial[1] * 0.050, hz - 0.165 * k)]
        m = meche(chemin, 0.042 + 0.012 * rng.random(), (radial[0], radial[1], 0.0))
        meches = m if meches is None else meches + m
    a.piece("meches", meches, MOUSSE)

    # ----- la tête : ronde et petite, les joues molles ; penchée sur l'épaule, tournée vers nous -----
    H = A.repere(TETE, (0, PENCHE, LACET))
    H3 = H.to_3x3()

    def tete_f(v):
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.9, -0.2, -0.35), 0.14, 0.30)
        return v * [0.112, 0.100, 0.098]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(tete_f), LICHEN, mat=H)
    a.tete = H @ Vector((0, -0.100, -0.005))
    # la face : un grand disque crème ; les masques chocolat en virgules qui descendent de chaque œil vers la joue
    a.rustine("face", "tete", TETE, H3 @ Vector((0, -1.0, 0.0)), lambda th: 0.62 + 0.06 * math.cos(2 * th), CREME, 0.003, 0)
    for nom, c in (("G", 1), ("D", -1)):
        masque = H3 @ Vector((c * 0.46, -0.84, 0.0))
        a.rustine("masque_" + nom, "tete", TETE, masque, lambda th: 0.26 + 0.20 * max(0.0, -math.sin(th)) ** 1.2, CHOCOLAT, 0.004, 0)
        p, n = a.surface("tete", TETE, H3 @ Vector((c * 0.46, -0.84, 0.10)))
        a.oeil("oeil_" + nom, p + n * 0.005, n, 0.0135)
        a.piece("lourde_" + nom, K.paupiere(0.0165, 0.02), LICHEN, mat=A.cadre(p + n * 0.006, n, H3 @ Vector((0, 0, 1))), poil=False)
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.022, 0.014, 0.014), CHOCOLAT, mat=H @ A.repere((0, -0.102, -0.014)), poil=False)
    sourire = [H3 @ Vector(d) for d in ((-0.38, -0.84, -0.42), (-0.16, -0.92, -0.52), (0.16, -0.92, -0.52), (0.40, -0.80, -0.42))]
    a.broderie("sourire", A.courbe(propres(a.trace("tete", TETE, sourire, 0.004)), 4), 0.0030, CHOCOLAT)

    # ----- les bras : démesurés, ils pendent devant jusqu'au sol, les trois griffes crème qui griffent l'herbe -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.150, -0.040, 0.350), (c * 0.205, -0.110, 0.250), (c * 0.215, -0.185, 0.120), (c * 0.205, -0.235, 0.040)]
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.050 - 0.012 * t, 16), LICHEN)
        griffes = None
        for k in (-1, 0, 1):
            g = A.tour(A.profil([(0, 0), (0.014, 0.004), (0.011, 0.040), (0.005, 0.075), (0, 0.095)], 5), 14)
            g = g.etire(1.5, 1.5, 1.7).pose((0, 0, 0), (-80, 0, 0)).pose((k * 0.026, -0.015, 0.0), (0, 0, k * 10))
            griffes = g if griffes is None else griffes + g
        a.piece("griffes_" + nom, griffes, GRIFFE, pos=(chemin[-1][0], chemin[-1][1], 0.026), poil=False)
        a.piece("main_" + nom, A.boule(1.0, 24, 12).etire(0.046, 0.054, 0.038), LICHEN, pos=(chemin[-1][0], chemin[-1][1] - 0.010, 0.050))

    # ----- les jambes : deux petits genoux repliés sous le tas, les pieds à plat -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.boule(1.0, 28, 14).etire(0.060, 0.090, 0.062), LICHEN, pos=(c * 0.100, 0.020, 0.062))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("paresseux", styles.style_de("paresseux"), sys.modules[__name__]), "Paresseux")
