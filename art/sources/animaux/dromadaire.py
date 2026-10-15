"""Le dromadaire en peluche de velours ras : un fauve caramel, UNE bosse haute et ronde au milieu du dos, un long cou en
S qui se retourne vers nous, une petite tête au long museau et à la lèvre pendante, de grands yeux aux longs cils, de
longues jambes minces aux genoux marqués et aux larges pieds plats, une courte queue à mèche. Le voyageur : debout,
tranquille, la tête haute, un air de grand seigneur qui n'a besoin de rien.

    python dromadaire.py        fabrique la fiche art/apercus/animaux/dromadaire.png (velours ras, palier 3)
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


CARAMEL = np.array(M.hexa("#e8b068"))         # la dominante : fauve caramel (le poil le fonce)
CLAIR = np.array(M.hexa("#f8dca8"))           # le ventre, le dedans des jambes, le menton
FONCE = np.array(M.hexa("#c08440"))           # la bosse, le dessus du cou, les mèches
COUSSIN = M.hexa("#8a6a48")                   # les grands pieds plats
NOIR = np.array(M.hexa("#3a2e28"))
PAS = 0.007


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("dromadaire")
    a.taille = 2.10

    # ----- le corps : un long tonneau étroit, le ventre remonté, UNE grosse bosse ronde au milieu du dos -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.480, 0.980), (0.300, 1.010), (0.040, 1.030), (-0.220, 1.040), (-0.420, 1.030))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.130), (0.14, 0.205), (0.42, 0.225), (0.72, 0.230), (0.90, 0.190), (0.97, 0.130), (1.0, 0.0)], L, 80)
    f = corps.v[:, 2] / L
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    haut = np.clip(corps.v[:, 1] / 0.20, 0.0, 1.0)
    corps.v[:, 1] += 0.230 * np.exp(-((f - 0.46) / 0.12) ** 2) * haut                      # la bosse
    corps.v[:, 0] *= 1 - 0.20 * np.exp(-((f - 0.46) / 0.12) ** 2) * haut                   # étroite, ronde
    corps.teinte = np.where((th > 2.2)[:, None], CLAIR, np.where((corps.v[:, 1] > 0.24)[:, None], FONCE, CARAMEL))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou : long, en S, d'une seule pièce couchée sur son arc ; le dessus plus sombre -----
    BASE = Vector((0.0, -0.360, 1.060))
    arc = ((0.0, 0.0), (0.060, 0.110), (0.130, 0.260), (0.150, 0.430), (0.090, 0.600), (0.0, 0.720))      # (avance, monte)
    enc = K.Fil([tuple(BASE + Vector((0, -u, z))) for u, z in arc], (1, 0, 0))
    Lc = enc.long
    cou = fuseau([(0.0, 0.150), (0.12, 0.130), (0.40, 0.092), (0.80, 0.074), (1.0, 0.068)], Lc, 56)
    cou.teinte = np.where((cou.v[:, 1] > 0.020)[:, None], FONCE, CARAMEL)
    a.piece("cou", cou.sculpte(enc.couche), None)
    centre, avant, nuque = enc.cadre(Lc)
    bout = Vector(centre)

    # ----- la tête : petite, un long museau qui descend ; la lèvre qui pend ; les narines en fentes ; tournée vers nous -----
    T = A.cadre(bout + Vector((0.0, -0.020, 0.030)), Vector((0.40, -1.0, -0.30)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.060), (0.22, 0.082), (0.46, 0.068), (0.72, 0.058), (0.90, 0.060), (0.97, 0.046), (1.0, 0.0)], 0.360, 52, 0.005)
    tete.teinte = np.where((tete.v[:, 2] > 0.20)[:, None], tuple(CARAMEL * 0.96), tuple(CARAMEL))
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.070)))
    a.tete = T @ Vector((0, 0.0, 0.200))
    a.piece("levre", A.boule(1.0, 24, 12).etire(0.044, 0.022, 0.060), tuple(CLAIR), mat=T @ A.repere((0.0, -0.068, 0.215), (10, 0, 0)))
    for nom, c in (("G", 1), ("D", -1)):
        pn, nn = a.surface("tete", T @ Vector((0, 0.0, 0.250)), T3 @ Vector((c * 0.45, 0.89, 0.0)))
        a.piece("narine_" + nom, A.boule(1.0, 14, 8).etire(0.006, 0.014, 0.012), tuple(NOIR), mat=A.cadre(pn + nn * 0.002, nn, T3 @ Vector((0, 0, 1))), poil=False)
        regard = T3 @ Vector((c * 0.84, 0.36, 0.04))
        p, n = a.surface("tete", T @ Vector((0, 0.0, 0.040)), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0185)
        a.piece("cils_" + nom, K.paupiere(0.0235, 0.20), tuple(FONCE), mat=A.cadre(p + n * 0.005, n, T3 @ Vector((0, 1, 0))), poil=False)
        po = A.profil([(0, 0), (0.026, 0.008), (0.032, 0.032), (0.024, 0.058), (0.009, 0.078), (0, 0.086)], 5)
        a.piece("oreille_" + nom, A.tour(po, 20).etire(1.0, 0.45, 1.0), tuple(CARAMEL),
                mat=A.cadre(T @ Vector((c * 0.046, 0.052, -0.020)), T3 @ Vector((c * 0.55, 0.62, -0.30)), T3 @ Vector((c * 0.3, 0.0, 1.0))))

    # ----- les jambes : longues et minces, le genou net, le canon grêle, le grand coussin plat ; les postérieurs plus coudés ;
    #       l'antérieur gauche un peu avancé -----
    def jambe(pts, r0):
        ft = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.25, r0 * 0.72), (0.44, r0 * 0.50), (0.50, r0 * 0.64), (0.57, r0 * 0.44), (0.90, r0 * 0.42), (0.96, r0 * 0.50), (1.0, 0.0)],
                   ft.long, 32, 0.007)
        m.teinte = np.where((m.v[:, 2] > 0.58 * ft.long)[:, None], CLAIR, CARAMEL)
        return m.sculpte(ft.couche)
    for nom, pts, r0 in (("av_D", [(-0.130, -0.300, 0.960), (-0.135, -0.310, 0.640), (-0.135, -0.300, 0.330), (-0.135, -0.310, 0.030)], 0.085),
                         ("ar_G", [(0.140, 0.340, 0.920), (0.150, 0.280, 0.620), (0.150, 0.360, 0.340), (0.150, 0.350, 0.030)], 0.095),
                         ("ar_D", [(-0.140, 0.340, 0.920), (-0.150, 0.280, 0.620), (-0.150, 0.360, 0.340), (-0.150, 0.350, 0.030)], 0.095),
                         ("av_G", [(0.130, -0.300, 0.960), (0.135, -0.340, 0.650), (0.135, -0.400, 0.340), (0.135, -0.410, 0.030)], 0.085)):
        a.piece("jambe_" + nom, jambe(pts, r0), None)
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.058, 0.082, 0.026), COUSSIN, pos=(pts[-1][0], pts[-1][1] - 0.020, 0.026), poil=False)
    queue = A.tube(A.courbe(propres([(0.0, 0.500, 0.960), (0.0, 0.560, 0.860), (0.0, 0.570, 0.700)]), 5), lambda t: 0.024 - 0.008 * t, 12)
    a.piece("queue", queue, tuple(CARAMEL))
    a.piece("meche", A.boule(1.0, 20, 10).etire(0.030, 0.030, 0.070), tuple(FONCE), pos=(0.0, 0.572, 0.650))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("dromadaire", styles.style_de("dromadaire"), sys.modules[__name__]), "Dromadaire")
