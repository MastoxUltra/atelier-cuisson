"""Le toucan en peluche de velours ras : un noir bleuté, la gorge et la poitrine blanc crème, le dessous de la queue
rouge vif, un cercle bleu ciel autour de l'œil, et surtout ce bec monumental, plus gros que sa tête, jaune citron à la
base, orange puis rouge, la pointe noire. Un snob qui porte son bec comme une œuvre d'art : il se tient droit comme un
i, le bec pointé vers nous en biais, l'œil mi-clos de quelqu'un qui n'a pas besoin d'expliquer.

    python toucan.py        fabrique la fiche art/apercus/animaux/toucan.png (velours ras, palier 3)
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

NOIR = M.hexa("#2b3140")                      # la dominante : noir bleuté (le poil le fonce : on le prend un peu clair)
CREME = M.hexa("#fffbec")                     # la gorge et la poitrine
CITRON = M.hexa("#fff04a")                    # l'accent : le bec, à la base
ORANGE = M.hexa("#ff9a1f")                    # le milieu du bec
ROUGE = M.hexa("#f02a22")                     # le bout du bec, le dessous de la queue
CIEL = M.hexa("#6fd0f2")                      # le cercle de l'œil
CORPS = Vector((0.0, 0.040, 0.290))
TETE = Vector((0.0, -0.045, 0.515))
LACET = 30.0                                  # la tête tournée vers nous


def construire():
    a = K.Animal("toucan")
    a.taille = 0.62

    # ----- le corps : un œuf dressé, le poitrail blanc devant (peint avant d'être sculpté), le dos noir -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(NOIR, float), (len(v), 1))
    t[(v[:, 1] < -0.28) & (v[:, 2] > -0.55)] = CREME
    corps.teinte = t

    def oeuf(v):
        v = K.bosse(v, (0, -0.9, 0.3), 0.12, 0.5)
        s = v * [0.118, 0.100, 0.185]
        s[:, 0] *= 1 - 0.20 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s
    a.piece("corps", corps.sculpte(oeuf), None, pos=CORPS, rot=(-8, 0, 0))

    # ----- la tête : ronde, sans cou, noire ; la gorge crème dessous -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 48, 24)
    tt = np.tile(np.asarray(NOIR, float), (len(tete.v), 1))
    tt[(tete.v[:, 1] < -0.35) & (tete.v[:, 2] < 0.10)] = CREME
    tete.teinte = tt
    a.piece("tete", tete.etire(0.092, 0.088, 0.090), None, mat=H)
    a.tete = H @ Vector((0, -0.090, -0.010))

    # ----- l'œil : un grand cercle bleu ciel de feutrine, le regard au milieu, une paupière lourde dessus -----
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.62, -0.74, 0.18))
        a.rustine("cerne_" + nom, "tete", TETE, regard, 0.40, CIEL, 0.003, 0)
        p, n = a.surface("tete", TETE, regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0160)
        a.piece("lourde_" + nom, K.paupiere(0.021, 0.20), NOIR, mat=A.cadre(p + n * 0.005, n, H3 @ Vector((0, 0, 1))), poil=False)

    # ----- le bec : une énorme gouttière tournée, bandée jaune, orange, rouge, la pointe noire ; un peu courbe -----
    B = A.cadre(H @ Vector((0, -0.075, -0.014)), H3 @ Vector((0, -0.97, -0.20)), H3 @ Vector((0, 0.2, 0.98)))

    def courbe_(v):
        s = v.copy()
        s[:, 1] -= 0.035 * np.clip(v[:, 2] / 0.300, 0, 1) ** 2.0
        s[:, 0] *= 1 - 0.18 * np.clip(v[:, 2] / 0.300, 0, 1)
        return s
    bec = A.tour(A.profil([(0, 0), (0.048, 0.010), (0.066, 0.060), (0.068, 0.130), (0.056, 0.210), (0.036, 0.270), (0.014, 0.300), (0, 0.308)], 6), 40)
    K.bandes(bec, [(0.115, CITRON), (0.215, ORANGE), (0.272, ROUGE), (9, NOIR)])
    a.piece("bec", bec.etire(0.82, 1.0, 1.0).sculpte(courbe_), None, mat=B, poil=False)

    # ----- les ailes : deux galets noirs plaqués sur les flancs, la pointe qui croise sur la queue -----
    for nom, c in (("G", 1), ("D", -1)):
        def galet(v):
            s = K.emousse(v, 0.88)
            s[:, 1] *= 1 - 0.45 * K.lisse((v[:, 2] + 0.2) / 1.2)
            return s
        a.piece("aile_" + nom, A.boule(1.0, 40, 20).sculpte(galet).etire(0.032, 0.066, 0.190), NOIR, pos=(c * 0.112, 0.060, 0.255), rot=(-8, 0, c * 6))

    # ----- la queue : un court éventail noir, le dessous rouge vif (une petite houppe cousue dessous) -----
    queue = A.tour(A.profil([(0, 0), (0.050, 0.010), (0.048, 0.080), (0.032, 0.150), (0, 0.180)], 5), 32).etire(1.0, 0.36, 1.0)
    a.piece("queue", queue, NOIR, pos=(0, 0.150, 0.210), rot=(160, 0, 0))
    a.piece("sous_queue", A.boule(1.0, 24, 12).etire(0.050, 0.044, 0.040), ROUGE, pos=(0, 0.130, 0.150))

    # ----- les pattes : courtes, bleu-gris, quatre orteils en pince ; plantées sous le ventre -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("patte_" + nom, A.tube(A.courbe([(c * 0.050, 0.030, 0.140), (c * 0.054, -0.010, 0.070), (c * 0.056, -0.040, 0.024)], 5), 0.022, 12),
                M.hexa("#7a8aa8"), poil=False)
        doigts = None
        for ang in (-28, 0, 28):
            d = A.boule(1.0, 16, 8).etire(0.012, 0.050, 0.011).pose((0, -0.040, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("orteils_" + nom, doigts, M.hexa("#7a8aa8"), pos=(c * 0.056, -0.040, 0.012), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("toucan", styles.style_de("toucan"), sys.modules[__name__]), "Toucan")
