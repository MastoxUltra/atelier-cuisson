"""Le moloch (le diable épineux) en peluche cousue main : un petit lézard plat et large, orange brique rayé de brun
et de sable, tout hérissé de cônes pointus semés sur le dos, les flancs, les pattes et la queue ; deux grandes cornes au
dessus des yeux, un faux visage en bosse sur la nuque, des petits yeux perlés, de courtes pattes écartées, une queue qui
traîne. Le lent : il avance par à-coups, une patte avant levée, la tête tournée vers nous, sûr d'être trop épineux
pour qu'on le croque.

    python moloch.py        fabrique la fiche art/apercus/animaux/moloch.png (cousu main, palier 2)
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


BRIQUE = np.array(M.hexa("#e08c54"))          # la dominante : orange brique
BRUN = np.array(M.hexa("#9a5a3a"))            # les bandes sombres
SABLE = np.array(M.hexa("#f2cc94"))           # les bandes claires, le ventre
POINTE = M.hexa("#f6dcae")                    # les cônes : plus pâles que la peau
NOIR = M.hexa("#2e2826")
PAS = 0.006


def cone(base, hauteur, cotes=10):
    return A.tour(A.profil([(0, 0), (base, 0.0), (base * 0.62, hauteur * 0.45), (base * 0.26, hauteur * 0.80), (0, hauteur)], 4), cotes)


def pose_sur(mesh, point, normale, dedans=0.006):
    """Pose un cône (axe Z) sur la peau, la pointe le long de la normale."""
    n = np.asarray(normale, float)
    n = n / np.linalg.norm(n)
    a = math.degrees(math.acos(max(-1.0, min(1.0, n[2]))))
    b = math.degrees(math.atan2(n[0], -n[1])) if math.hypot(n[0], n[1]) > 1e-6 else 0.0
    return mesh.pose(tuple(np.asarray(point, float) - n * dedans), (a, 0.0, b))


def construire():
    a = K.Animal("moloch")
    a.taille = 0.22

    # ----- le corps : un galet plat et large, rayé de brun et de sable en travers ; le ventre sable -----
    C = np.array([0.0, 0.020, 0.062])
    R = np.array([0.090, 0.135, 0.056])
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    bande = np.sin(v[:, 1] * 6.5 + 0.6 * v[:, 0]) > 0.35
    t = np.tile(BRIQUE, (len(v), 1))
    t[bande & (v[:, 2] > -0.2)] = BRUN
    t[(np.sin(v[:, 1] * 6.5 + 0.6 * v[:, 0] + 1.9) > 0.88) & (v[:, 2] > -0.2)] = SABLE
    t[v[:, 2] < -0.35] = SABLE
    corps.teinte = t
    a.piece("corps", corps.etire(*R), None, pos=tuple(C))

    # ----- les pointes : des cônes semés régulièrement sur le dos et les flancs (plus hauts sur le dos) -----
    pointes = None
    rng = np.random.default_rng(4)
    for lev, n_az, h in ((12.0, 16, 0.024), (36.0, 14, 0.032), (58.0, 10, 0.040), (78.0, 5, 0.044)):
        for k in range(n_az):
            psi = 2 * math.pi * (k + 0.5 * (lev > 30) + 0.25 * rng.random()) / n_az
            lam = math.radians(lev + rng.uniform(-4, 4))
            d = np.array([math.cos(lam) * math.cos(psi), math.cos(lam) * math.sin(psi), math.sin(lam)])
            p = C + d * R
            nrm = d / R
            if p[1] < -0.07 and abs(p[0]) < 0.06:                                # pas là où la tête se pose
                continue
            c = pose_sur(cone(0.015, h * (0.85 + 0.3 * rng.random())), p, nrm)
            pointes = c if pointes is None else pointes + c
    a.piece("pointes", pointes, POINTE, poil=False)

    # ----- la tête : un petit coin, des yeux perlés, deux grandes cornes ; la fausse tête en bosse sur la nuque -----
    TETE = Vector((0.0, -0.162, 0.066))
    H = A.repere(TETE, (0, 0, 24))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 36, 18)
    tete.teinte = np.where((tete.v[:, 2] > 0.1)[:, None], BRUN, BRIQUE)
    a.piece("tete", tete.etire(0.040, 0.052, 0.032), None, mat=H)
    a.tete = H @ Vector((0, -0.050, 0.0))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.70, -0.40, 0.58))
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0105)
        corne = pose_sur(cone(0.014, 0.060, 12), H @ Vector((c * 0.026, -0.010, 0.022)), H3 @ Vector((c * 0.55, 0.45, 0.70)), 0.004)
        a.piece("corne_" + nom, corne, POINTE, poil=False)
        petite = pose_sur(cone(0.008, 0.026, 8), H @ Vector((c * 0.018, -0.030, 0.018)), H3 @ Vector((c * 0.50, -0.20, 0.82)), 0.003)
        a.piece("cornette_" + nom, petite, POINTE, poil=False)
    nuque = A.boule(1.0, 28, 14)
    nuque.teinte = np.tile(BRIQUE, (len(nuque.v), 1))
    a.piece("fausse_tete", nuque.etire(0.034, 0.030, 0.024), None, pos=(0.0, -0.088, 0.098))
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("fausse_corne_" + nom, pose_sur(cone(0.009, 0.034, 8), (c * 0.018, -0.094, 0.110), (c * 0.45, -0.30, 0.85), 0.004), POINTE, poil=False)

    # ----- les pattes : courtes et écartées, le coude en dehors, le petit pied plat ; l'avant gauche levé -----
    for nom, x_, y_, levee in (("av_G", 0.095, -0.075, True), ("av_D", -0.095, -0.075, False), ("ar_G", 0.100, 0.115, False), ("ar_D", -0.100, 0.115, False)):
        c = 1 if x_ > 0 else -1
        bas = (c * 0.150, y_ - (0.040 if levee else 0.010), 0.040 if levee else 0.012)
        ch = [(c * 0.050, y_, 0.060), (c * 0.118, y_ - 0.004, 0.056), (c * 0.142, y_ - 0.008, 0.040), bas]
        a.piece("patte_" + nom, A.tube(A.courbe(propres(ch), 5), 0.019, 12), tuple(BRIQUE))
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.026, 0.038, 0.011), tuple(SABLE), pos=(bas[0], bas[1] - 0.012, bas[2] + (0.010 if levee else 0.0)))
        po = pose_sur(cone(0.009, 0.034, 8), (c * 0.118, y_ - 0.004, 0.062), (c * 0.2, 0.0, 1.0), 0.003)
        a.piece("pointe_patte_" + nom, po, POINTE, poil=False)

    # ----- la queue : un cône mince qui traîne et se recourbe, semée de pointes ; la queue en tube de feutre -----
    chemin = [(0.0, 0.130, 0.058), (0.0, 0.220, 0.040), (0.040, 0.300, 0.030), (0.090, 0.340, 0.028)]
    a.piece("queue", K.tube_peint(A.courbe(propres(chemin), 6), lambda t: 0.034 - 0.026 * t, [(0.5, tuple(BRIQUE)), (0.75, tuple(BRUN)), (1.0, tuple(BRIQUE))], 14), None)
    qp = None
    for i, (f, dy) in enumerate(((0.18, 0.0), (0.34, 0.0), (0.52, 0.0), (0.70, 0.0))):
        pt = A.courbe(propres(chemin), 6)
        P = np.asarray(pt[int(f * (len(pt) - 1))], float)
        c = pose_sur(cone(0.009, 0.026, 8), P + np.array([0.0, 0.0, 0.020 * (1 - f)]), (0.0, 0.1, 1.0), 0.004)
        qp = c if qp is None else qp + c
    a.piece("pointes_queue", qp, POINTE, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("moloch", styles.style_de("moloch"), sys.modules[__name__]), "Moloch")
