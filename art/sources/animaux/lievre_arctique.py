"""Le lièvre arctique en peluche, cousu main : une boule de neige lilas pâle, ronde comme un pain de campagne, les
oreilles courtes à la pointe charbon, et surtout ses pieds : d'énormes raquettes qui dépassent le ventre. Tout le
contraire du lièvre de l'île, sec et dressé : lui est vautré, le menton rentré, une oreille à moitié rabattue sous
la paupière lourde, un bâilleur qui ne bougera pas avant la fin de l'hiver.

    python lievre_arctique.py        fabrique la fiche art/apercus/animaux/lievre_arctique.png (cousu main, palier 2)
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

LILAS = M.hexa("#e1d6f8")                     # la dominante : lilas pâle (le poil la dore : on la prend nettement plus claire)
OMBRE = M.hexa("#c7b8ec")                     # le dessous des pattes, les paupières, un ton plus bas
CHARBON = M.hexa("#2d2831")                   # le bout des oreilles (l'accent), la truffe
NEIGE = M.hexa("#fffaf4")                     # le ventre, la queue
LACET = 22.0                                  # la tête tournée vers nous (vers sa gauche)
CORPS = Vector((0.0, 0.045, 0.190))
TETE = Vector((0.0, -0.185, 0.285))


def construire():
    a = K.Animal("lievre_arctique")
    a.taille = 0.80

    # ----- le corps : un pain rond, large du bas, le dos voûté ; le ventre posé sur le sol -----
    def pain(v):
        v = K.bosse(v, (0, -0.8, -0.3), 0.10, 0.5)
        s = v * [0.175, 0.215, 0.185]
        s[:, 2] = np.where(s[:, 2] < 0, s[:, 2] * 0.92, s[:, 2])
        s[:, 0] *= 1 + 0.10 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s
    corps = A.boule(1.0, 56, 28).sculpte(pain)
    G.sillons(corps, [14], 0.005, 1.1)
    a.piece("corps", corps, LILAS, pos=CORPS)
    a.couture("dos", "corps", 14, 0.28, 0.96)
    a.rustine("ventre", "corps", CORPS + Vector((0, -0.03, 0.0)), (0, -0.85, -0.50),
              lambda th: 0.56 - 0.10 * math.cos(2 * th), NEIGE, 0.003, 26)

    # ----- la tête : ronde, les joues larges, le museau court ; tournée vers nous, le menton rentré dans le poitrail -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()

    def joufflue(v):
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.85, -0.30, -0.40), 0.20, 0.30)
        return v * [0.112, 0.108, 0.104]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(joufflue), LILAS, mat=H)
    a.couture("crane", "tete", 14, 0.55, 0.98)
    a.piece("museau", A.boule(1.0, 32, 16).etire(0.058, 0.062, 0.050), NEIGE, mat=H @ A.repere((0, -0.082, -0.030)))
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.016, 0.010, 0.011), CHARBON, mat=H @ A.repere((0, -0.140, -0.016)), poil=False)
    a.tete = H @ Vector((0, -0.100, 0.0))
    # la bouche : une petite moue qui descend de la truffe en deux traits
    bouche = [H3 @ Vector(d) for d in ((0.0, -0.60, -0.52), (0.18, -0.70, -0.62), (0.34, -0.60, -0.56))]
    a.broderie("bouche", A.courbe(propres(a.trace("museau", H @ Vector((0, -0.082, -0.030)), bouche, 0.003)), 4), 0.0022, CHARBON)

    # ----- les yeux : vivants, mi-clos sous une paupière lourde : il somnole -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, H3 @ Vector((c * 0.70, -0.62, 0.22)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.019)
        P = A.cadre(p + n * 0.004, n, H3 @ Vector((0, 0, 1)))
        a.piece("lourde_" + nom, K.paupiere(0.022, 0.05), OMBRE, mat=P, poil=False)

    # ----- les oreilles : courtes et rondes, la pointe charbon ; la gauche à demi dressée, la droite rabattue sur le côté -----
    po = A.profil([(0, 0), (0.030, 0.012), (0.042, 0.052), (0.040, 0.096), (0.028, 0.130), (0.010, 0.153), (0, 0.160)], 6)
    for nom, c, vers in (("G", 1, (0.30, 0.55, 0.78)), ("D", -1, (-0.80, 0.30, 0.30))):
        vers = (H3 @ Vector(vers)).normalized()
        E = A.cadre(H @ Vector((c * 0.052, 0.040, 0.075)) - vers * 0.014, vers, H3 @ Vector((c * 0.4, -0.9, 0.0)))
        oreille = K.bandes(A.tour(po, 40).etire(1.0, 0.36, 1.0), [(0.110, LILAS), (9, CHARBON)])
        a.piece("oreille_" + nom, oreille, None, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 32).etire(0.60, 0.34, 0.74).pose((0, 0.008, 0.016)), K.ROSE, mat=E, poil=False)

    # ----- les bras : deux petits bouts de patte repliés sous le menton, les mains qui pendent sur les raquettes -----
    for nom, c in (("G", 1), ("D", -1)):
        bras = A.courbe([(c * 0.075, -0.100, 0.215), (c * 0.085, -0.160, 0.140), (c * 0.080, -0.200, 0.070), (c * 0.076, -0.210, 0.034)], 6)
        a.piece("bras_" + nom, A.tube(bras, lambda t: 0.036 - 0.008 * t, 14), LILAS)
        a.piece("main_" + nom, A.boule(1.0, 24, 12).etire(0.032, 0.040, 0.024), LILAS, pos=(c * 0.076, -0.218, 0.028))

    # ----- les raquettes : d'énormes pieds de derrière posés à plat, devant le corps, les orteils cousus en travers -----
    pp = A.profil([(0, 0), (0.046, 0.014), (0.066, 0.080), (0.074, 0.190), (0.064, 0.300), (0.040, 0.360), (0, 0.384)], 6)
    for nom, c, cap in (("G", 1, 16.0), ("D", -1, -12.0)):
        pied = A.tour(pp, 40).etire(1.0, 0.50, 1.0)
        a.piece("pied_" + nom, pied, LILAS, pos=(c * 0.142, 0.150, 0.034), rot=(90, 0, c * cap))
        a.ourlet("orteils_" + nom, "pied_" + nom, 0.62)

    # ----- la queue : une petite houppette blanche -----
    a.piece("queue", A.boule(1.0, 24, 12).etire(0.050, 0.050, 0.046), NEIGE, pos=(0, 0.262, 0.120))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lievre_arctique", styles.style_de("lievre_arctique"), sys.modules[__name__]), "Lièvre arctique")
