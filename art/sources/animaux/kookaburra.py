"""Le kookaburra en peluche cousue main (4e dessin, repris d'une autre base : l'œuf de la poule, la tête tendue sur le
côté) : le grand martin-pêcheur rieur d'Australie, trapu, la TÊTE énorme et le bec énorme, droit comme une lance et
pointé vers l'avant ; la tête crème coiffée d'une calotte brune et barrée d'un trait brun à travers l'œil ; le ventre
crème, le dos brun avec la plaque bleu ciel de l'aile, une queue rousse barrée de noir, de courtes pattes. Il se tient
tout droit sur son perchoir, la tête tournée vers nous, le bec en avant : il va rire.

    python kookaburra.py        fabrique la fiche art/apercus/animaux/kookaburra.png (cousu main, palier 2)
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


CREME = np.array(M.hexa("#fff2d6"))           # la dominante : crème chaud
CAFE = np.array(M.hexa("#8a6040"))            # la calotte, le dos, le trait de l'œil
CIEL = M.hexa("#58c0f0")                      # l'accent : la plaque bleu ciel de l'aile
ROUX = M.hexa("#d88a50")                      # la queue
CHARBON = M.hexa("#4a3a34")                   # le dessus du bec, les barres de la queue
CORNE = M.hexa("#f0dcb8")                     # le dessous du bec
PATTE = M.hexa("#c8aa94")
CORPS = Vector((0.0, 0.050, 0.235))
TETE = Vector((0.0, -0.030, 0.445))
LACET = 38.0


def pied():
    """Un pied : trois doigts devant (vers -Y), un derrière."""
    def doigt(degres, long):
        t = math.radians(degres)
        return A.boule(1.0, 16, 8).etire(0.009, long, 0.008).pose((0.8 * long * math.sin(t), -0.8 * long * math.cos(t), 0), (0, 0, degres))
    return doigt(-30, 0.032) + doigt(0, 0.036) + doigt(30, 0.032) + doigt(180, 0.020)


def construire():
    a = K.Animal("kookaburra")
    a.taille = 0.50

    # ----- le corps : un œuf droit et trapu, la poitrine crème, un peu penché en arrière ; le dos brun -----
    def oeuf(v):
        v = K.bosse(v, (0, -0.85, 0.10), 0.20, 0.30)
        s = v * [0.112, 0.124, 0.170]
        s[:, 0] *= 1 - 0.20 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s
    corps = A.boule(1.0, 56, 28)
    corps.teinte = np.where((corps.v[:, 1] > 0.40)[:, None], tuple(CAFE), tuple(CREME))
    a.piece("corps", corps.sculpte(oeuf), None, pos=CORPS, rot=(-8, 0, 0))

    # ----- la tête : GROSSE et ronde, la calotte brune, la gorge et la nuque crème ; un trait brun à travers l'œil -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    cr = A.boule(1.0, 56, 28)
    cr.teinte = np.where((cr.v[:, 2] > 0.42)[:, None], tuple(CAFE), tuple(CREME))
    a.piece("tete", cr, None, mat=H @ A.repere((0, 0, 0), (0, 0, 0), (0.100, 0.104, 0.098)))
    a.tete = H @ Vector((0, -0.190, -0.020))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.80, -0.50, 0.12))
        a.rustine("trait_" + nom, "tete", H.to_translation(), regard, 0.30, tuple(CAFE), 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0145)

    # ----- le bec : ÉNORME, droit, épais à la base, qui part vers l'avant ; le dessus sombre, le dessous clair -----
    lac = math.radians(LACET)
    avant = H3 @ Vector((0.0, -1.0, -0.10))
    haut = A.tour(A.profil([(0, 0), (0.054, 0.008), (0.056, 0.060), (0.044, 0.130), (0.026, 0.200), (0.010, 0.250), (0, 0.268)], 6), 48)
    a.piece("bec", haut.etire(1.0, 0.86, 1.0), CHARBON, mat=A.cadre(H @ Vector((0, -0.070, -0.010)), avant, Vector((0, 0, 1))), poil=False)
    bas = A.tour(A.profil([(0, 0), (0.046, 0.006), (0.046, 0.050), (0.034, 0.120), (0.016, 0.190), (0, 0.226)], 6), 40)
    a.piece("bec_bas", bas.etire(1.0, 0.52, 1.0), CORNE,
            mat=A.cadre(H @ Vector((0, -0.064, -0.038)), H3 @ Vector((0.0, -1.0, -0.04)), Vector((0, 0, 1))), poil=False)

    # ----- les ailes : deux galets bruns serrés sur les flancs, chacun avec sa plaque bleu ciel en haut ; la queue :
    #       un éventail roux barré de noir, qui dépasse derrière et pend -----
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 40, 20)
        aile.teinte = np.where((aile.v[:, 2] > 0.20)[:, None], tuple(CIEL), tuple(CAFE))
        aile.teinte[aile.v[:, 2] > 0.80] = np.array(CAFE)
        a.piece("aile_" + nom, aile.etire(0.030, 0.100, 0.130), None, pos=(c * 0.112, 0.070, 0.240), rot=(-6, 0, c * 5))
    chemin = [(0.0, 0.130, 0.170), (0.0, 0.200, 0.110), (0.0, 0.245, 0.030)]
    bandes = [(0.18, tuple(ROUX)), (0.30, CHARBON), (0.46, tuple(ROUX)), (0.58, CHARBON), (0.74, tuple(ROUX)), (0.86, CHARBON), (1.0, tuple(CREME))]
    a.piece("queue", K.tube_peint(A.courbe(propres(chemin), 6), lambda t: 0.044 - 0.010 * t, bandes, 14), None)

    # ----- les pattes : courtes et fortes, grises ; un pied à trois doigts devant, un derrière -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.048, 0.030, 0.100), (c * 0.052, 0.020, 0.050), (c * 0.052, 0.010, 0.012)]
        a.piece("patte_" + nom, A.tube(A.courbe(propres(ch), 5), 0.012, 10), PATTE, poil=False)
        a.piece("pied_" + nom, pied().pose((c * 0.052, 0.010, 0.010), (0, 0, c * 10)), PATTE, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("kookaburra", styles.style_de("kookaburra"), sys.modules[__name__]), "Kookaburra")
