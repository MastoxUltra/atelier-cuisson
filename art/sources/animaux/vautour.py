"""Le vautour en peluche de velours ras (2e dessin, d'après photos : plus de bloc) : un grand rapace PERCHÉ, voûté, le
corps en pente qui plonge vers l'avant, un brun sombre en plumes lisses, deux grandes ailes repliées en cape dont les
longues plumes noires croisent la queue, le COU NU, long et ridé, d'un rose gris qui sort d'une collerette de duvet
blanc, la petite tête chauve au bec crochu et fort, l'œil enfoncé ; des cuisses en culottes de plumes et de grosses
pattes à serres. Il attend, de profil, la tête tournée vers nous, un regard patient de croque-mort.

    python vautour.py        fabrique la fiche art/apercus/animaux/vautour.png (velours ras, palier 3)
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


BRUN = np.array(M.hexa("#7a6250"))            # la dominante : brun sombre (le poil le fonce : on le prend plus clair)
PLUME = np.array(M.hexa("#9a8068"))           # les couvertures claires
PEAU = np.array(M.hexa("#e0a8a0"))            # le cou nu, la tête : rose gris
DUVET = np.array(M.hexa("#fff6e8"))           # la collerette
BEC = M.hexa("#c8b898")
OEIL = M.hexa("#c8903a")
CHARBON = np.array(M.hexa("#3a3230"))         # le bout des ailes, les serres
PAS = 0.006
LACET = 28.0


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("vautour")
    a.taille = 1.10

    # ----- le corps : un tronc voûté en pente, la queue basse derrière, la poitrine bombée devant ; le dos plus sombre -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.240, 0.250), (0.130, 0.360), (0.000, 0.470), (-0.080, 0.560))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.05, 0.105), (0.25, 0.180), (0.55, 0.185), (0.84, 0.140), (1.0, 0.0)], L, 56)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.teinte = np.where((th > 2.3)[:, None], tuple(PLUME), tuple(BRUN))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- les ailes : deux capes repliées sur les flancs, les couvertures claires en haut, les longues plumes noires qui
    #       descendent et croisent la queue -----
    for nom, c in (("G", 1), ("D", -1)):
        cape = A.boule(1.0, 36, 18)
        cape.teinte = np.where((cape.v[:, 2] > 0.35)[:, None], tuple(PLUME), tuple(BRUN))
        a.piece("aile_" + nom, cape.etire(0.050, 0.200, 0.270), None, pos=(c * 0.170, 0.070, 0.390), rot=(-16, 0, c * 7))
        a.piece("plumes_" + nom, A.boule(1.0, 24, 12).etire(0.030, 0.210, 0.034), tuple(CHARBON), pos=(c * 0.115, 0.290, 0.210), rot=(-34, 0, c * -8))
    a.piece("queue", A.boule(1.0, 24, 12).etire(0.070, 0.030, 0.150), tuple(BRUN), pos=(0.0, 0.290, 0.150), rot=(38, 0, 0))

    # ----- le cou nu et ridé, qui s'étire hors de la collerette ; la tête chauve ; le bec crochu -----
    chemin = [(0.0, -0.090, 0.540), (0.0, -0.170, 0.640), (0.0, -0.160, 0.740), (0.0, -0.230, 0.820)]
    cou = A.tube(A.courbe(propres(chemin), 6), lambda t: 0.052 - 0.020 * t, 20)
    cou.teinte = np.tile(PEAU, (len(cou.v), 1))
    a.piece("cou", cou, None, poil=False)
    a.piece("collerette", A.boule(1.0, 36, 18).etire(0.115, 0.095, 0.060), tuple(DUVET), pos=(0.0, -0.090, 0.560), rot=(-22, 0, 0))
    H = A.repere(Vector((0.0, -0.250, 0.850)), (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 40, 20)
    tete.teinte = np.tile(PEAU, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.046, 0.062, 0.048), None, mat=H, poil=False)
    a.tete = H @ Vector((0, -0.090, -0.010))
    haut = A.tour(A.profil([(0, 0), (0.034, 0.006), (0.030, 0.034), (0.018, 0.064), (0.006, 0.084), (0, 0.092)], 5), 28)

    def crochu(v):
        s = v.copy()
        s[:, 1] *= 1.10
        s[:, 1] -= 0.040 * np.clip(v[:, 2] / 0.092, 0, 1) ** 2.2
        return s
    a.piece("bec", haut.sculpte(crochu), BEC, mat=A.cadre(H @ Vector((0, -0.050, -0.010)), H3 @ Vector((0, -1.0, -0.24)), Vector((0, 0, 1))), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.70, -0.55, 0.30))
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0135)
        a.piece("arcade_" + nom, K.paupiere(0.020, 0.30), tuple(PEAU * 0.82), mat=A.cadre(p + n * 0.004, n, H3 @ Vector((0, 0, 1))), poil=False)

    # ----- les pattes : des culottes de plumes, de grosses pattes grises, trois serres devant et une derrière -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("culotte_" + nom, A.boule(1.0, 28, 14).etire(0.070, 0.095, 0.115), tuple(BRUN), pos=(c * 0.085, 0.020, 0.230))
        ch = [(c * 0.080, 0.000, 0.170), (c * 0.082, -0.010, 0.090), (c * 0.082, -0.020, 0.018)]
        m = A.tube(A.courbe(propres(ch), 5), 0.026, 12)
        m.teinte = np.tile(PEAU * 0.85, (len(m.v), 1))
        a.piece("patte_" + nom, m, None, poil=False)
        serres = None
        for ang in (-28, 0, 28, 180):
            d = A.boule(1.0, 12, 6).etire(0.010, 0.046, 0.010).pose((0.7 * 0.046 * math.sin(math.radians(ang)), -0.7 * 0.046 * math.cos(math.radians(ang)), 0), (0, 0, ang))
            serres = d if serres is None else serres + d
        a.piece("serres_" + nom, serres, tuple(CHARBON), pos=(c * 0.082, -0.020, 0.012), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("vautour", styles.style_de("vautour"), sys.modules[__name__]), "Vautour")
