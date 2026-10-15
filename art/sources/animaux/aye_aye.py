"""L'aye-aye en peluche de velours ras (2e dessin, d'après photos : un lémurien, pas une souris) : un brun sombre grisé tout
hirsute, un long poil de garde pâle au bout qui pend sur les flancs ; une grosse tête ronde au museau court et obtus, la
face rose sale, des yeux d'ambre immenses ; de très grandes oreilles rondes et minces, nues, qui se tournent vers nous ;
des mains aux longs doigts fins dont le MILIEU, démesuré, pâle, fin comme une baguette ; et une queue très longue,
touffue, qui balaie derrière lui. Le tapoteur de la nuit : accroupi, le dos rond, une main sur le sol, l'autre levée
près de l'oreille, le long doigt prêt à tapoter l'écorce.

    python aye_aye.py        fabrique la fiche art/apercus/animaux/aye_aye.png (velours ras, palier 3)
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


TAUPE = np.array(M.hexa("#6a5a56"))           # la dominante : taupe sombre (le poil la fonce : on la prend plus claire)
POIL = np.array(M.hexa("#c8b4a4"))            # le bout pâle des longs poils de garde
FACE = np.array(M.hexa("#d8aca8"))            # la face, le nez : rose sale
OREILLE = np.array(M.hexa("#8a7480"))         # les oreilles nues
DOIGT = np.array(M.hexa("#efe0cc"))           # les doigts
AMBRE = M.hexa("#f0a828")
CHARBON = M.hexa("#2e2628")
CORPS = Vector((0.0, 0.050, 0.140))
TETE = Vector((0.0, -0.140, 0.250))
LACET = 24.0
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=40, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 5)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("aye_aye")
    a.taille = 0.62

    # ----- le corps : une grosse boule accroupie, le dos rond ; les longs poils de garde pâles qui pendent des flancs -----
    corps = A.boule(1.0, 48, 24)
    corps.teinte = np.tile(TAUPE, (len(corps.v), 1))
    a.piece("corps", corps.etire(0.125, 0.150, 0.120), None, pos=tuple(CORPS))
    rng = np.random.default_rng(3)
    gardes = None
    for i in range(34):
        z = rng.uniform(-0.05, 0.90)
        t = rng.uniform(0.0, 2 * math.pi)
        r = math.sqrt(max(0.0, 1 - z * z))
        d = np.array([r * math.cos(t), r * math.sin(t), z])
        if d[1] < -0.60:
            continue
        p = np.array(CORPS) + d * np.array([0.128, 0.154, 0.124])
        long_ = 0.050 + 0.040 * rng.random()
        m = A.boule(1.0, 8, 6).etire(0.020, 0.016, long_).pose(tuple(p + np.array([0.0, 0.0, -long_ * 0.80])), (8 * d[1], -10 * d[0], 0))
        gardes = m if gardes is None else gardes + m
    a.piece("gardes", gardes, tuple(POIL))

    # ----- la tête : ronde et large, le museau court et obtus, la face rose sale ; tournée de trois quarts -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.where(((tete.v[:, 1] < -0.45) & (np.abs(tete.v[:, 0]) < 0.70))[:, None], tuple(FACE), tuple(TAUPE))
    a.piece("tete", tete.etire(0.088, 0.092, 0.082), None, mat=H)
    a.piece("museau", A.boule(1.0, 28, 14).etire(0.040, 0.046, 0.034), tuple(FACE), mat=H @ A.repere((0, -0.088, -0.024)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.020, 0.012, 0.014), CHARBON, mat=H @ A.repere((0, -0.130, -0.020)), poil=False)
    a.tete = H @ Vector((0, -0.110, -0.010))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.52, -0.82, 0.22))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.30, AMBRE, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0270)
        # l'immense oreille : un disque mince, nu, dressé sur le côté, le dedans plus clair
        E = A.cadre(H @ Vector((c * 0.078, 0.020, 0.040)), H3 @ Vector((c * 0.62, 0.20, 0.76)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, A.boule(1.0, 36, 18).etire(0.096, 0.012, 0.106).pose((0, 0, 0.070)), tuple(OREILLE), mat=E, poil=False)
        a.piece("dedans_" + nom, A.boule(1.0, 28, 14).etire(0.066, 0.008, 0.074).pose((0, -0.010, 0.068)), tuple(FACE), mat=E, poil=False)

    # ----- les mains : trois doigts courts et UN très long, fin et pâle ; la gauche posée sur le sol, la droite levée à
    #       l'oreille, le grand doigt tendu ; les pieds à plat -----
    def main(centre, cap, long_doigt):
        m = A.boule(1.0, 20, 10).etire(0.026, 0.030, 0.014).pose((0, 0, 0))
        for k, ang in enumerate((-30, -12, 12, 30)):
            t = math.radians(ang)
            l = long_doigt if k == 1 else 0.052
            d = A.tube([(0.0, -0.020, 0.0), (l * math.sin(t) * 0.5, -0.020 - l * 0.5, 0.0), (l * math.sin(t), -0.020 - l, 0.0)], 0.0072 if k == 1 else 0.0085, 8)
            m = m + d
        return m.pose(tuple(centre), (0, 0, cap))
    gauche = [(0.080, -0.070, 0.150), (0.115, -0.130, 0.090), (0.105, -0.205, 0.040)]
    a.piece("bras_G", A.tube(A.courbe(propres(gauche), 5), 0.030, 12), tuple(TAUPE))
    a.piece("main_G", main(gauche[-1], 8, 0.150), tuple(DOIGT), poil=False)
    droite = [(-0.080, -0.060, 0.170), (-0.130, -0.110, 0.230), (-0.135, -0.190, 0.300)]
    a.piece("bras_D", A.tube(A.courbe(propres(droite), 5), 0.030, 12), tuple(TAUPE))
    a.piece("main_D", main((-0.135, -0.200, 0.305), -10, 0.150).pose((0, 0, 0), (-70, 0, 0)), tuple(DOIGT), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        cu = A.boule(1.0, 24, 12).etire(0.060, 0.090, 0.060)
        cu.teinte = np.tile(TAUPE, (len(cu.v), 1))
        a.piece("cuisse_" + nom, cu, None, pos=(c * 0.100, 0.060, 0.080))
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.042, 0.080, 0.020), tuple(FACE), pos=(c * 0.105, -0.030, 0.022), rot=(0, 0, c * 8), poil=False)

    # ----- la queue : très longue et touffue, une grande courbe qui s'élève et retombe derrière lui -----
    qf = K.Fil([(0.0, 0.180, 0.120), (0.0, 0.320, 0.100), (0.040, 0.440, 0.180), (0.090, 0.480, 0.320), (0.100, 0.420, 0.440)], (1, 0, 0))
    queue = fuseau([(0.0, 0.040), (0.30, 0.062), (0.70, 0.068), (0.94, 0.042), (1.0, 0.0)], qf.long, 36, 0.006)
    queue.teinte = np.where((queue.v[:, 2] > 0.55 * qf.long)[:, None], tuple(POIL), tuple(TAUPE))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("aye_aye", styles.style_de("aye_aye"), sys.modules[__name__]), "Aye-aye")
