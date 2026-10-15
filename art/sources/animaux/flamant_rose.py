"""Le flamant rose en peluche de velours ras : un rose vif franc, un petit corps ovale tout en plumes, un cou immense en
S souple, une petite tête à l'œil jaune, un bec coudé (rose pâle à la base, noir au bout) ; les ailes ont les rémiges
noires, et deux très longues jambes roses aux genoux inversés. Le danseur de marais : perché sur UNE patte, l'autre
repliée contre le ventre, le cou en S qui revient sur lui-même, la tête de profil, le bec baissé : élégant, un peu
snob, en équilibre.

    python flamant_rose.py        fabrique la fiche art/apercus/animaux/flamant_rose.png (velours ras, palier 3)
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


ROSE = np.array(M.hexa("#ff8fb0"))            # la dominante : rose vif franc (le poil le fonce)
PALE = np.array(M.hexa("#ffc4d4"))            # le bec à la base, le haut du cou, les plumes claires
NOIR = M.hexa("#2a2630")                      # l'accent : le bout du bec, les rémiges
JAUNE = M.hexa("#ffd84a")                     # l'œil
PATTE = M.hexa("#ff7fa4")
PAS = 0.007


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=48, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("flamant_rose")
    a.taille = 1.50

    # ----- le corps : un œuf allongé, le dos bas, la queue relevée en pointe ; rose, plus pâle au ventre ; une couture de dos -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.280, 0.790), (0.160, 0.770), (0.000, 0.760), (-0.150, 0.790), (-0.240, 0.830))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.060), (0.18, 0.110), (0.45, 0.150), (0.75, 0.140), (0.93, 0.100), (1.0, 0.0)], L, 56)
    corps.teinte = np.where((np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1])) > 2.4)[:, None], PALE, ROSE)
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou : très long, en S souple (il monte, plonge en arrière, remonte, et la tête retombe devant) -----
    BASE = Vector((0.0, -0.190, 0.820))
    pts = ((0.0, 0.0), (0.060, 0.150), (0.030, 0.320), (-0.070, 0.470), (-0.110, 0.620), (-0.030, 0.760), (0.090, 0.810))      # (avance, monte)
    enc = K.Fil([tuple(BASE + Vector((0, -u, z))) for u, z in pts], (1, 0, 0))
    Lc = enc.long
    cou = fuseau([(0.0, 0.070), (0.10, 0.056), (0.40, 0.036), (0.80, 0.030), (1.0, 0.034)], Lc, 36, 0.006)
    cou.teinte = np.where((cou.v[:, 2] > 0.55 * Lc)[:, None], PALE, ROSE)
    a.piece("cou", cou.sculpte(enc.couche), None)

    # ----- la tête : petite, ronde ; le bec coudé (rose pâle puis noir), le dessous clair ; l'œil jaune cerné de noir -----
    centre, avant, nuque = enc.cadre(Lc)
    T = A.cadre(Vector(centre) + Vector((0.020, -0.030, 0.0)), Vector((0.24, -1.0, -0.30)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.040, 0.044, 0.046), tuple(PALE), mat=T)
    bec = A.tour(A.profil([(0, 0), (0.034, 0.006), (0.036, 0.040), (0.030, 0.080), (0.024, 0.115), (0.014, 0.140), (0, 0.150)], 6), 28)
    K.bandes(bec, [(0.070, tuple(PALE)), (9, NOIR)])

    def coude(v):
        s = v.copy()
        s[:, 1] -= 0.080 * np.clip((v[:, 2] - 0.060) / 0.090, 0, 1) ** 1.5                  # le bec se plie vers le bas
        s[:, 2] = np.where(v[:, 2] > 0.06, 0.06 + (v[:, 2] - 0.06) * (1 - 0.35 * np.clip((v[:, 2] - 0.06) / 0.09, 0, 1)), v[:, 2])
        return s
    a.piece("bec", bec.etire(1.0, 0.82, 1.0).sculpte(coude), None, mat=T @ A.repere((0, -0.004, 0.026)), poil=False)
    a.tete = T @ Vector((0, 0.0, 0.110))
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.90, -0.18, 0.40))
        a.rustine("cerne_" + nom, "tete", T.to_translation(), regard, 0.30, NOIR, 0.0025, 0)
        p, n = a.surface("tete", T.to_translation(), regard)
        a.rustine("iris_" + nom, "tete", T.to_translation(), regard, 0.17, JAUNE, 0.0035, 0)
        a.oeil("oeil_" + nom, p + n * 0.005, n, 0.0115)

    # ----- les ailes : deux galets roses plaqués, les rémiges noires qui dépassent en bas, une plume claire au-dessus -----
    for nom, c, rot in (("G", 1, (-6, 0, 10)), ("D", -1, (-6, 0, -10))):
        aile = A.boule(1.0, 40, 20)
        aile.teinte = np.where((aile.v[:, 1] < -0.30)[:, None] & (aile.v[:, 2] < -0.05)[:, None], np.array(NOIR),
                               np.where((aile.v[:, 1] > 0.40)[:, None], PALE, ROSE))
        a.piece("aile_" + nom, aile.etire(0.030, 0.165, 0.110), None, pos=(c * 0.122, 0.040, 0.800), rot=rot)

    # ----- les jambes : deux très longues, minces, roses, le genou inversé (la cheville) marqué ; la gauche repliée -----
    jamb = [(0.040, 0.020, 0.760), (0.044, 0.050, 0.520), (0.046, 0.000, 0.300), (0.046, -0.020, 0.052)]
    a.piece("patte_G", K.tube_peint(A.courbe(jamb, 7), lambda t: 0.020 - 0.006 * t + 0.008 * math.exp(-((t - 0.60) / 0.06) ** 2), [(1, tuple(PATTE))], 12), None)
    doigts = None
    for ang in (-30, 0, 30):
        d = A.boule(1.0, 14, 8).etire(0.012, 0.066, 0.010).pose((0, -0.050, 0.0)).pose((0, 0, 0), (0, 0, ang))
        doigts = d if doigts is None else doigts + d
    a.piece("doigts_G", doigts, tuple(PATTE), pos=(0.046, -0.020, 0.012), poil=False)
    repliee = [(-0.040, 0.020, 0.760), (-0.044, 0.130, 0.640), (-0.050, 0.020, 0.560), (-0.052, -0.080, 0.600)]
    a.piece("patte_D", A.tube(A.courbe(repliee, 6), 0.017, 12), tuple(PATTE), poil=False)
    a.piece("pied_D", A.boule(1.0, 20, 10).etire(0.020, 0.052, 0.016), tuple(PATTE), pos=(-0.052, -0.110, 0.600), rot=(10, 0, 0), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("flamant_rose", styles.style_de("flamant_rose"), sys.modules[__name__]), "Flamant rose")
