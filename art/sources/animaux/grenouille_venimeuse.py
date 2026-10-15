"""La grenouille venimeuse en peluche, cousue main (2e dessin : plus de bébé aux yeux énormes) : un DENDROBATE, fin et
nerveux, le corps mince d'un jaune citron vif tout recouvert d'un RÉSEAU noir en mailles (le dos, la tête, les
cuisses), la tête en coin, de petits yeux noirs à fleur de peau, de longues pattes grêles et des ventouses rondes et
pâles au bout de chaque doigt, les grandes pattes arrière repliées. Posée sur ses quatre pattes, la tête haute : toute
petite, toute vive, elle sait qu'on n'y touche pas.

    python grenouille_venimeuse.py        fabrique la fiche art/apercus/animaux/grenouille_venimeuse.png (cousu main, palier 2)
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
    """Les points d'un tracé sans doublons consécutifs (deux points identiques à la suite déforment un tube en NaN)."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie


CITRON = np.array(M.hexa("#ffe95a"))          # la dominante : jaune citron vif
NOIR = np.array(M.hexa("#26242c"))            # l'accent : le réseau
VENTRE = np.array(M.hexa("#fff8c0"))          # le ventre, la gorge
VENTOUSE = M.hexa("#fff4b0")                  # le bout des doigts
PAS = 0.005


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=48, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def reseau(m, graine, n=34, largeur=0.0105, ventre=None):
    """Peint un RÉSEAU noir en mailles sur du jaune : le plus proche et le deuxième plus proche de quelques graines tirées
    dans la boîte de la pièce (le joint, là où ils sont presque à égale distance) ; le ventre jaune pâle, sans réseau."""
    rng = np.random.default_rng(graine)
    v = m.v
    lo, hi = v.min(axis=0) - 0.01, v.max(axis=0) + 0.01
    graines = lo + rng.random((n, 3)) * (hi - lo)
    d = np.sort(np.linalg.norm(v[:, None, :] - graines[None, :, :], axis=2), axis=1)[:, :2]
    t = np.tile(CITRON, (len(v), 1))
    t[(d[:, 1] - d[:, 0]) < largeur] = NOIR
    if ventre is not None:
        t[ventre(v)] = VENTRE
    m.teinte = t
    return m


def construire():
    a = K.Animal("grenouille_venimeuse")
    a.taille = 0.34

    # ----- le corps : mince, un peu relevé devant, le dos tout couvert du réseau noir, le ventre pâle -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.120, 0.060), (0.050, 0.075), (-0.020, 0.100), (-0.070, 0.118))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.05, 0.036), (0.28, 0.054), (0.62, 0.052), (0.90, 0.040), (1.0, 0.0)], L, 52, 0.004)
    reseau(corps, 3, 38, 0.0115, ventre=lambda v: (v[:, 1] < -0.030))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- la tête : un coin pointu, bas ; de PETITS yeux noirs, à fleur de tête, sur les côtés du crâne -----
    T = A.cadre(Vector((0.0, -0.105, 0.134)), Vector((0.30, -1.0, 0.16)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.10, 0.042), (0.36, 0.052), (0.64, 0.044), (0.88, 0.030), (0.98, 0.016), (1.0, 0.0)], 0.110, 40, 0.003)
    tete.v[:, 1] *= 0.80
    reseau(tete, 5, 14, 0.0095, ventre=lambda v: (v[:, 1] < -0.020))
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.040)))
    a.tete = T @ Vector((0, 0.0, 0.060))
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.74, 0.55, 0.20))
        p, n = a.surface("tete", T @ Vector((0, 0.0, 0.020)), regard)
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0105)

    # ----- les pattes avant : fines et droites, quatre longs doigts à ventouse ; les arrière : longues, repliées en Z,
    #       le pied à plat, les doigts écartés, chacun sa ventouse -----
    def doigts(centre, cap, long, k=4):
        m = None
        for i in range(k):
            ang = cap + (i - (k - 1) / 2) * 24
            t = math.radians(ang)
            d = A.boule(1.0, 12, 6).etire(0.0045, long, 0.0045).pose((long * math.sin(t) * 0.9, -long * math.cos(t) * 0.9, 0.0), (0, 0, ang))
            v = A.boule(1.0, 12, 6).etire(0.0105, 0.0105, 0.0065).pose((long * math.sin(t) * 1.85, -long * math.cos(t) * 1.85, 0.0))
            m = d + v if m is None else m + d + v
        return m.pose(tuple(centre))
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.034, -0.050, 0.095), (c * 0.052, -0.080, 0.056), (c * 0.058, -0.100, 0.014)]
        m = A.tube(A.courbe(propres(ch), 5), lambda t: 0.013 - 0.005 * t, 12)
        m.teinte = np.tile(CITRON, (len(m.v), 1))
        a.piece("bras_" + nom, m, None)
        a.piece("doigts_av_" + nom, doigts((c * 0.058, -0.104, 0.010), c * 14, 0.030), VENTOUSE, poil=False)
        cu = [(c * 0.046, 0.100, 0.082), (c * 0.092, 0.040, 0.070), (c * 0.084, 0.118, 0.026), (c * 0.074, 0.062, 0.012)]
        mj = A.tube(A.courbe(propres(cu), 6), lambda t: 0.020 - 0.010 * t, 14)
        reseau(mj, 11 + (c > 0), 12, 0.0085)
        a.piece("jambe_ar_" + nom, mj, None)
        a.piece("doigts_ar_" + nom, doigts((c * 0.074, 0.060, 0.010), c * 10, 0.040), VENTOUSE, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("grenouille_venimeuse", styles.style_de("grenouille_venimeuse"), sys.modules[__name__]), "Grenouille venimeuse")
