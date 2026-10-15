"""Le gypaète en peluche : le seigneur des à-pics, long, grave et un peu sinistre. Posé sur une pointe, les immenses
ailes ardoise repliées dans le dos, la queue en losange qui traîne derrière, le torse bombé couleur d'argile : il se
teint la poitrine, la gorge et la tête dans la poussière rouille, pour de vrai. Un cercle rouge autour de l'œil noir,
une barbiche noire sous le bec, la tête penchée vers le sol : il a repéré un os, et il y pense.

    python gypaete.py        fabrique la fiche art/apercus/animaux/gypaete.png (style du palier : B, peluche de magasin)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

ARDOISE = np.array(M.hexa("#5d6375"))         # la dominante : les ailes et le dos, ardoise (inversion décidée le 14/10 avec
                                              # la session Animaux : le rouille de la vipère est trop proche)
SOMBRE = np.array(M.hexa("#272a35"))          # le bout des plumes, la queue
ARGILE = np.array(M.hexa("#f0c698"))          # la poitrine, le cou et la tête : crème rouillé (registre : autour de #e8b98a)
ROUGE = M.hexa("#e0261c")                     # l'accent : l'anneau de l'œil
NOIR = np.array(M.hexa("#171616"))            # la barbiche, le bandeau d'œil
GRIFFE = M.hexa("#2a2523")
BEC = M.hexa("#b9b2a2")                       # le bec, gris corne
GRIS = np.array(M.hexa("#8b90a3"))


def plume(longueur, large, sombre=0.55, cotes=14):
    """Une plume plate (fuseau tourné aplati vu d'en haut), ardoise à la base et sombre au bout."""
    L, w = longueur, large
    m = A.tour(A.profil([(0, 0), (0.55 * w, 0.06 * L), (w, 0.30 * L), (0.92 * w, 0.64 * L), (0.55 * w, 0.90 * L), (0, L)], 4), cotes)
    m.etire(1.0, 0.15, 1.0)
    t = np.clip((m.v[:, 2] / L - sombre) / (1 - sombre), 0.0, 1.0)[:, None]
    m.teinte = ARDOISE * (1 - t) + SOMBRE * t
    return m


def construire():
    a = K.Animal("gypaete")
    a.taille = 1.30                           # un grand rapace : du bec au bout de la queue (règle d'l'auteur du 15/10)

    # ----- le corps : un long œuf couché presque à l'horizontale, penché en avant ; poitrail crème rouillé, dos ardoise -----
    T = A.repere((0.0, 0.05, 0.215), (52, 0, 0))                     # presque couché : la queue loin derrière, la tête en avant
    corps = A.tour(A.profil([(0, 0), (0.050, 0.010), (0.098, 0.060), (0.128, 0.150), (0.128, 0.260), (0.108, 0.350),
                             (0.080, 0.410), (0.050, 0.446), (0, 0.460)], 6), 48)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))          # 0 : le dos (axe +Y du corps) ; pi : le ventre
    # le corps est couché : son +Y (dos) regarde en haut et en arrière ; le ventre est crème rouillé
    t = np.tile(ARDOISE, (len(ang), 1))
    t[(ang > 2.35) & (corps.v[:, 2] > 0.06)] = ARGILE
    corps.teinte = t
    a.piece("corps", corps, None, mat=T)
    haut = Vector(T @ Vector((0, 0, 0.45)))

    # ----- le cou : épais, plumeux, crème rouillé ; il penche vers le sol -----
    cou = A.tube(A.courbe([haut + Vector((0, 0.02, -0.02)), haut + Vector((0, -0.06, -0.02)), haut + Vector((0, -0.12, -0.05))], 5),
                 lambda t: 0.082 - 0.016 * t, 18)
    cou.teinte = np.tile(ARGILE, (len(cou.v), 1))
    a.piece("cou", cou, None)

    # ----- la tête : allongée, le front plat, le crâne pâle ; un bandeau noir de l'œil au bec, et la barbiche -----
    H = A.repere(haut + Vector((0, -0.19, -0.10)), (40, 0, 8))      # le nez vers le bas : il fixe le sol
    H3 = H.to_3x3()
    tete = A.boule(1.0, 56, 28)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(ARGILE, (len(u), 1))
    cote = np.abs(u[:, 0])
    t[(cote > 0.28) & (cote < 0.80) & (u[:, 1] < -0.12) & (np.abs(u[:, 2] - 0.05) < 0.30)] = NOIR      # le bandeau d'œil
    tete.teinte = t
    tete.v = tete.v * [0.062, 0.100, 0.060]
    a.piece("tete", tete, None, mat=H)
    a.tete = H @ Vector((0, -0.110, -0.004))

    # ----- le bec : long, gris corne, à crochet léger ; la barbiche noire dessous, en pointe -----
    def crochet(v):
        s = v.copy()
        h = np.clip(v[:, 2] / 0.060, 0.0, 1.0)
        s[:, 1] -= 0.018 * h ** 2.4
        return s
    bec = A.tour(A.profil([(0.032, 0.0), (0.030, 0.012), (0.024, 0.030), (0.014, 0.048), (0.006, 0.058), (0, 0.062)], 4), 28)
    a.piece("bec", bec.etire(0.74, 1.12, 1.0).sculpte(crochet), BEC, mat=H @ A.cadre((0, -0.104, -0.012), (0, -1, -0.10), (0, -0.10, 1)),
            poil=False)
    barbiche = A.boule(1.0, 24, 12).etire(0.018, 0.013, 0.058)
    barbiche.teinte = np.tile(NOIR, (len(barbiche.v), 1))
    a.piece("barbiche", barbiche, None, mat=H @ A.cadre((0, -0.082, -0.050), (0, -0.55, -1), (0, -1, 0.2)), poil=True)

    # ----- les yeux : une bille noire cerclée de rouge, dans le bandeau -----
    centre = H @ Vector((0, -0.020, 0.002))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, H3 @ Vector((c * 0.78, -0.55, 0.06)))
        a.bouton("oeil_" + nom, pos + n * 0.002, n, 0.0165)
        cercle = A.tore(0.0215, 0.0048, 28, 8)
        a.piece("cercle_" + nom, cercle, ROUGE, mat=A.cadre(pos + n * 0.003, n), poil=False)

    # ----- les ailes : immenses, repliées dans le dos en deux grandes lames ardoise qui dépassent la queue -----
    for nom, c in (("G", 1), ("D", -1)):
        aile = None
        for k in range(7):
            u_ = k / 6
            f = plume(0.54 - 0.05 * u_, 0.080 - 0.008 * u_, 0.55)
            f = f.pose(Vector(T @ Vector((c * (0.050 + 0.062 * u_), 0.100 - 0.030 * u_, 0.335 - 0.040 * u_))),
                       A.viser(T.to_3x3() @ Vector((c * (0.04 + 0.10 * u_), 0.07 - 0.02 * u_, -1.0))))
            aile = f if aile is None else aile + f
        a.piece("aile_" + nom, aile, None)

    # ----- la queue : longue, en losange, deux fois la taille d'une queue d'aigle -----
    queue = None
    for k in range(5):
        u_ = k / 4 - 0.5
        f = plume(0.46 - 0.10 * abs(u_) * 2, 0.056, 0.60)
        f = f.pose(Vector((0.012 * u_, 0.22, 0.170)), A.viser((u_ * 0.9, 0.95, -0.22)))
        queue = f if queue is None else queue + f
    a.piece("queue", queue, None)

    # ----- les pattes : courtes et sombres, de grosses culottes de plumes ardoise, des serres -----
    for nom, c in (("G", 1), ("D", -1)):
        cuisse = A.tube(A.courbe([(c * 0.070, 0.100, 0.215), (c * 0.086, 0.046, 0.158), (c * 0.072, -0.010, 0.092)], 5),
                        lambda t: 0.056 - 0.016 * t, 14)
        cuisse.teinte = np.tile(GRIS, (len(cuisse.v), 1))
        a.piece("cuisse_" + nom, cuisse, None)
        tarse = A.tube(A.courbe([(c * 0.072, -0.012, 0.096), (c * 0.072, -0.020, 0.048), (c * 0.072, -0.024, 0.020)], 4), 0.017, 14)
        a.piece("tarse_" + nom, tarse, GRIFFE, poil=False)
        doigts = None
        for ang_ in (-34, 0, 34, 180):
            r = math.radians(ang_)
            d = Vector((math.sin(r), -math.cos(r), 0.0))
            long = 0.074 if ang_ != 180 else 0.048
            d_ = A.tube(A.courbe([(0, 0, 0.020), d * long * 0.55 + Vector((0, 0, 0.018)), d * long + Vector((0, 0, 0.011))], 4),
                        lambda t: 0.0150 - 0.0045 * t, 12).pose((c * 0.072, -0.024, 0.0))
            doigts = d_ if doigts is None else doigts + d_
        a.piece("doigts_" + nom, doigts, GRIFFE, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("gypaete", styles.style_de("gypaete"), sys.modules[__name__]), "Gypaète")
