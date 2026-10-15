"""Le phacochère en peluche cousue main : un rouille franc, la grosse tête plate et large, quatre verrues, deux défenses
d'ivoire qui se recourbent vers le haut, une crinière en brosse raide sur l'échine, de petites oreilles pointues, et la
queue dressée en antenne à houppe noire. L'important vexé : à genoux sur ses antérieurs, comme il aime, le museau en
avant, la queue droite comme un mât, un œil de travers : il fouille.

    python phacochere.py        fabrique la fiche art/apercus/animaux/phacochere.png (cousu main, palier 2)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import garnitures as G
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


ROUILLE = M.hexa("#d98a58")                   # la dominante : rouille franc (le poil le fonce : on le prend clair)
SOMBRE = M.hexa("#5a3a2c")                    # la crinière, le museau, la houppe
IVOIRE = M.hexa("#fff2d8")                    # l'accent : les défenses
CLAIR = M.hexa("#f2c8a0")                     # le dessous, le tour du museau
CORPS = Vector((0.0, 0.080, 0.360))
TETE = Vector((0.0, -0.360, 0.270))
LACET = 22.0


def construire():
    a = K.Animal("phacochere")
    a.taille = 1.00

    # ----- le corps : un tonneau court, les épaules hautes, la croupe plus basse ; la crinière en brosse raide -----
    def tonneau(v):
        v = K.bosse(v, (0, -0.7, 0.4), 0.14, 0.45)
        s = v * [0.200, 0.320, 0.215]
        s[:, 2] *= 1 - 0.12 * K.lisse((v[:, 1] + 0.0) / 1.0)
        return s
    corps = A.boule(1.0, 56, 28)
    corps.teinte = np.where((corps.v[:, 2] < -0.45)[:, None], np.asarray(CLAIR), np.asarray(ROUILLE))
    G.sillons(corps, [14], 0.005, 1.1)
    a.piece("corps", corps.sculpte(tonneau), None, pos=CORPS)
    a.couture("dos", "corps", 14, 0.35, 0.95)
    for i, y in enumerate(np.linspace(-0.26, 0.30, 12)):
        h = 0.052 - 0.020 * abs(y) / 0.3
        a.piece("soie_%02d" % i, A.boule(1.0, 8, 4).etire(0.014, 0.020, 0.052 + 0.008 * math.cos(i)), SOMBRE,
                pos=(0.0, CORPS.y + y, CORPS.z + 0.215 * (1 - 0.12 * ((y / 0.32 + 0.0) / 1.0)) + 0.030), poil=False)

    # ----- la tête : large, plate sur le dessus, le museau carré ; quatre verrues ; les défenses recourbées ; de côté vers nous -----
    H = A.repere(TETE, (-10, 0, LACET))
    H3 = H.to_3x3()

    def large(v):
        s = K.emousse(v, 0.80)
        s[:, 1] *= 0.80
        return s * [0.150, 0.130, 0.200]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(large), ROUILLE, mat=H @ A.repere((0, 0, 0)))
    a.piece("groin", A.boule(1.0, 32, 16).etire(0.080, 0.062, 0.090), tuple(SOMBRE), mat=H @ A.repere((0, -0.230, -0.030)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.040, 0.030, 0.016), tuple(SOMBRE), mat=H @ A.repere((0, -0.305, -0.026)), poil=False)
    a.tete = H @ Vector((0, -0.220, -0.020))
    for k, (dx, dy, dz) in enumerate(((0.100, -0.060, 0.040), (-0.100, -0.060, 0.040), (0.120, -0.150, -0.050), (-0.120, -0.150, -0.050))):
        a.piece("verrue_%d" % k, A.boule(1.0, 14, 8).etire(0.030, 0.026, 0.028), CLAIR, mat=H @ A.repere((dx, dz * 1.0 + 0.0, dy)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        ch = [H @ Vector(q) for q in ((c * 0.100, -0.150, -0.130), (c * 0.150, -0.230, -0.130), (c * 0.170, -0.290, -0.040), (c * 0.150, -0.320, 0.070))]
        a.piece("defense_" + nom, A.tube(A.courbe(propres(ch), 6), lambda t: 0.026 - 0.020 * t, 14), IVOIRE, poil=False)
        p, n = a.surface("tete", H @ Vector((0, 0.0, 0.0)), H3 @ Vector((c * 0.72, 0.40, -0.48)))
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0140)
        po = A.profil([(0, 0), (0.030, 0.008), (0.036, 0.034), (0.026, 0.060), (0.008, 0.074), (0, 0.080)], 5)
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.42, 1.0), ROUILLE,
                mat=A.cadre(H @ Vector((c * 0.110, 0.110, 0.080)), H3 @ Vector((c * 0.30, 0.18, 0.95)), H3 @ Vector((c * 0.3, -0.9, 0.0))))

    # ----- les pattes : les antérieurs à genoux (repliés sous la poitrine), les postérieurs droits ; la queue en antenne -----
    for nom, c in (("av_G", 1), ("av_D", -1)):
        a.piece("genou_" + nom, A.boule(1.0, 24, 12).etire(0.050, 0.090, 0.050), ROUILLE, pos=(c * 0.115, -0.230, 0.050), rot=(0, 0, c * 6))
        a.piece("patte_" + nom, A.tube(A.courbe([(c * 0.110, -0.150, 0.230), (c * 0.115, -0.220, 0.100), (c * 0.115, -0.290, 0.030)], 5), 0.054, 14), ROUILLE)
        a.piece("sabot_" + nom, A.boule(1.0, 20, 10).etire(0.040, 0.060, 0.026), SOMBRE, pos=(c * 0.115, -0.340, 0.028), poil=False)
    for nom, c in (("ar_G", 1), ("ar_D", -1)):
        a.piece("patte_" + nom, A.tube(A.courbe([(c * 0.110, 0.300, 0.250), (c * 0.120, 0.290, 0.130), (c * 0.120, 0.300, 0.034)], 5), 0.058, 14), ROUILLE)
        a.piece("sabot_" + nom, A.boule(1.0, 20, 10).etire(0.044, 0.064, 0.028), SOMBRE, pos=(c * 0.120, 0.280, 0.030), poil=False)
    a.piece("queue", A.tube(A.courbe([(0.0, 0.380, 0.400), (0.0, 0.460, 0.520), (0.0, 0.470, 0.700)], 5), 0.016, 12), ROUILLE)
    a.piece("houppe", A.boule(1.0, 16, 8).etire(0.040, 0.040, 0.090), SOMBRE, pos=(0.0, 0.470, 0.770))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("phacochere", styles.style_de("phacochere"), sys.modules[__name__]), "Phacochère")
