"""L'aigle en peluche : le roi des crêtes, planté sur ses grosses serres, les deux ailes déployées d'un coup, comme
l'oiseau d'un blason. Le corps brun chocolat, la nuque couverte de plumes d'or en collerette, un sourcil épais qui lui
donne l'air fâché, un bec jaune vif en crochet, des serres énormes. La tête tournée vers nous : il nous a repérés.

    python aigle.py        fabrique la fiche art/apercus/animaux/aigle.png (style du palier : B, peluche de magasin)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import matieres as M
import peluche as K
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

CHOCO = np.array(M.hexa("#6a4a38"))           # la dominante (registre du 14/10 : brun chocolat #5e4130) ; un cran plus
                                              # clair, le style B adoucit et le poil long fonce
SOMBRE = np.array(M.hexa("#2c1f19"))          # le bout des plumes
OR = np.array(M.hexa("#f0b648"))              # la nuque (collerette dorée)
JAUNE = M.hexa("#ffd21f")                     # l'accent : le bec, les serres, la peau autour de l'œil
GRIFFE = M.hexa("#2a2523")
PIED = Vector((0.0, 0.0, 0.0))


def plume(longueur, large, sombre=0.55, epais=0.15, cotes=14, dessus=False):
    """Une plume plate : un fuseau tourné, aplati sur X (on le couche ensuite le long d'une direction avec A.viser),
    brun à la base et sombre au bout."""
    L, w = longueur, large
    m = A.tour(A.profil([(0, 0), (0.55 * w, 0.06 * L), (w, 0.30 * L), (0.92 * w, 0.64 * L), (0.55 * w, 0.90 * L), (0, L)], 4), cotes)
    m.etire(1.0, epais, 1.0) if dessus else m.etire(epais, 1.0, 1.0)      # dessus : plat vu d'en haut (la queue)
    t = np.clip((m.v[:, 2] / L - sombre) / (1 - sombre), 0.0, 1.0)[:, None]
    m.teinte = CHOCO * (1 - t) + SOMBRE * t
    return m


def pose(m, depart, direction):
    """Couche une plume : son axe Z le long de « direction », son pied en « depart »."""
    return m.pose(depart, A.viser(direction))


def aile(c):
    """Une aile déployée, côté c (1 = gauche) : l'avant-bras, les secondaires qui pendent derrière, la main aux dix
    plumes longues qui s'ouvrent en éventail, et la plume de tête dorée."""
    epaule, poignet = Vector((c * 0.10, 0.02, 0.43)), Vector((c * 0.46, -0.05, 0.66))
    sortie = A.tube(A.courbe([epaule, (epaule + poignet) * 0.5 + Vector((0, -0.01, 0.05)), poignet], 6), lambda t: 0.050 - 0.030 * t, 14)
    sortie.teinte = np.tile(CHOCO, (len(sortie.v), 1))
    n = 7                                                            # les secondaires, le long du bras
    for k in range(n):
        u = (k + 0.5) / n
        depart = epaule + (poignet - epaule) * u + Vector((0, 0.01, -0.01))
        sortie = sortie + pose(plume(0.30 + 0.04 * math.sin(math.pi * u), 0.046, dessus=True), depart,
                               (c * (0.16 + 0.25 * u), 1.0, -0.20 + 0.10 * u))
    n = 8                                                            # les primaires, en éventail depuis le poignet
    for k in range(n):
        u = k / (n - 1)
        phi = math.radians(8 + 66 * u)                               # 0 : vers l'avant et le bout ; grand : vers l'arrière
        d = (c * math.cos(phi), 0.18 + math.sin(phi) * 0.95 - 0.35, 0.26 - 0.20 * u)
        sortie = sortie + pose(plume(0.44 - 0.07 * u + 0.05 * math.sin(math.pi * u), 0.046), poignet + Vector((c * 0.012 * k, 0, -0.004 * k)), d)
    return sortie


def construire():
    a = K.Animal("aigle")
    a.taille = 2.00                           # ailes ouvertes : l'envergure est sa plus grande dimension (règle d'l'auteur du 15/10)

    # ----- le corps : un œuf dressé, penché vers l'arrière, le poitrail en avant ; brun, la poitrine plus fournie -----
    T = A.repere((0.0, 0.07, 0.17), (28, 0, 0))
    corps = A.tour(A.profil([(0, 0), (0.060, 0.010), (0.108, 0.060), (0.130, 0.150), (0.126, 0.250), (0.108, 0.340),
                             (0.078, 0.400), (0.046, 0.436), (0, 0.452)], 6), 48)
    corps.teinte = np.tile(CHOCO, (len(corps.v), 1))
    a.piece("corps", corps, None, mat=T)
    haut = Vector(T @ Vector((0, 0, 0.44)))
    a.piece("jabot", A.boule(1.0, 36, 18).etire(0.100, 0.080, 0.120), tuple(CHOCO), mat=A.repere(T @ Vector((0, -0.095, 0.275))))

    # ----- le cou court et la collerette dorée : des plumes d'or hérissées autour de la nuque -----
    collerette = None
    for k in range(9):
        ang = math.radians(-100 + 200 * k / 8)                      # un demi-tour : les côtés et le derrière, jamais devant
        f = A.boule(1.0, 16, 8).etire(0.024, 0.016, 0.066)
        f.teinte = np.tile(OR, (len(f.v), 1))
        d = Vector((math.sin(ang), math.cos(ang), 0.0))             # vers le côté, puis vers l'arrière
        f = f.pose(haut + d * 0.080 + Vector((0, 0.010, -0.012)), A.viser(d * 0.40 + Vector((0, 0.55, 0.60))))
        collerette = f if collerette is None else collerette + f
    a.piece("collerette", collerette, None)

    # ----- la tête : large, plate sur le dessus ; la nuque dorée, le visage brun -----
    centre_tete = haut + Vector((0.0, -0.080, 0.080))
    H = A.repere(centre_tete, (-6, 0, 22))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 56, 28)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(CHOCO, (len(u), 1))
    t[(u[:, 1] > 0.05) & (u[:, 2] > -0.45)] = OR                    # la nuque et le derrière du crâne
    tete.teinte = t
    tete.v = tete.v * [0.080, 0.096, 0.078]
    a.piece("tete", tete, None, mat=H)
    a.tete = H @ Vector((0, -0.100, -0.004))

    # ----- le bec : jaune vif, haut, en crochet ; une cire de peau jaune à sa base -----
    def crochet(v):
        s = v.copy()
        h = np.clip(v[:, 2] / 0.062, 0.0, 1.0)
        s[:, 1] -= 0.030 * h ** 2.2                                 # la pointe plonge vers le bas
        return s
    haut_bec = A.tour(A.profil([(0.036, 0.0), (0.034, 0.012), (0.028, 0.030), (0.018, 0.048), (0.008, 0.060), (0, 0.066)], 4), 28)
    a.piece("bec", haut_bec.etire(0.80, 1.30, 1.0).sculpte(crochet), JAUNE, mat=H @ A.cadre((0, -0.088, -0.022), (0, -1, -0.12), (0, -0.12, 1)),
            poil=False)
    a.piece("cire", A.boule(1.0, 24, 12).etire(0.030, 0.026, 0.022), JAUNE, mat=H @ A.repere((0, -0.084, -0.010)), poil=False)

    # ----- les yeux : de grosses billes dorées sous un sourcil épais qui fait l'air fâché -----
    centre = H @ Vector((0, -0.010, 0.012))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, H3 @ Vector((c * 0.72, -0.60, 0.06)))
        a.bouton("oeil_" + nom, pos + n * 0.002, n, 0.0215)
        haut_oeil = (H3 @ Vector((0, 0.1, 1)) - n * n.dot(H3 @ Vector((0, 0.1, 1)))).normalized()
        sourcil = A.boule(1.0, 28, 14).etire(0.038, 0.014, 0.018)
        sourcil.teinte = np.tile(SOMBRE, (len(sourcil.v), 1))
        a.piece("sourcil_" + nom, sourcil, None,
                mat=A.cadre(pos + n * 0.010 + haut_oeil * 0.024, n, haut_oeil), poil=False)

    # ----- les ailes déployées -----
    a.piece("aile_G", aile(1), None)
    a.piece("aile_D", aile(-1), None)

    # ----- la queue : un éventail court de plumes qui retombent derrière -----
    queue = None
    for k in range(7):
        u = k / 6 - 0.5
        f = pose(plume(0.32, 0.050, 0.55, dessus=True), Vector((0.012 * u * 4, 0.21, 0.200)), (u * 1.5, 0.90, -0.34))
        queue = f if queue is None else queue + f
    a.piece("queue", queue, None)

    # ----- les pattes : de grosses culottes de plumes, les tarses jaunes, les gros doigts et les serres -----
    for nom, c in (("G", 1), ("D", -1)):
        cuisse = A.tube(A.courbe([(c * 0.075, 0.100, 0.200), (c * 0.092, 0.040, 0.150), (c * 0.075, -0.020, 0.088)], 5), lambda t: 0.060 - 0.016 * t, 14)
        cuisse.teinte = np.tile(CHOCO, (len(cuisse.v), 1))
        a.piece("cuisse_" + nom, cuisse, None)
        tarse = A.tube(A.courbe([(c * 0.075, -0.020, 0.092), (c * 0.075, -0.030, 0.046), (c * 0.075, -0.034, 0.020)], 4), 0.019, 14)
        a.piece("tarse_" + nom, tarse, JAUNE, poil=False)
        doigts = None
        for ang in (-34, 0, 34, 180):                                # trois doigts devant, un pouce derrière
            r = math.radians(ang)
            d = Vector((math.sin(r), -math.cos(r), 0.0))
            long = 0.080 if ang != 180 else 0.052
            d_ = A.tube(A.courbe([(0, 0, 0.022), d * long * 0.55 + Vector((0, 0, 0.020)), d * long + Vector((0, 0, 0.012))], 4),
                        lambda t: 0.0165 - 0.005 * t, 12).pose((c * 0.075, -0.034, 0.0))
            doigts = d_ if doigts is None else doigts + d_
        a.piece("doigts_" + nom, doigts, JAUNE, poil=False)
        griffes = None
        for ang in (-34, 0, 34, 180):
            r = math.radians(ang)
            d = Vector((math.sin(r), -math.cos(r), 0.0))
            long = 0.080 if ang != 180 else 0.052
            g = A.tour(A.profil([(0.011, 0.0), (0.008, 0.016), (0.0035, 0.030), (0, 0.036)], 4), 16)
            g = g.pose(Vector((c * 0.075, -0.034, 0.0)) + d * (long + 0.004) + Vector((0, 0, 0.012)),
                       A.viser(d * 0.75 + Vector((0, 0, -0.55))))
            griffes = g if griffes is None else griffes + g
        a.piece("griffes_" + nom, griffes, GRIFFE, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("aigle", styles.style_de("aigle"), sys.modules[__name__]), "Aigle")
