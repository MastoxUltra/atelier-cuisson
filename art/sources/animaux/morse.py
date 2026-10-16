"""Le morse en peluche de magasin : une masse cannelle rosé, dressée sur ses nageoires de devant, le poitrail énorme,
deux bourrelets de graisse autour du cou, une petite tête ronde où tout est dans le museau : deux grosses babines
crème piquées de points (les racines de la moustache en brosse), et deux longues défenses ivoire. Un vieux colonel
bougon qui toise le monde : le menton haut, l'œil mi-clos sous une paupière lourde, la tête tournée vers nous.

    python morse.py        fabrique la fiche art/apercus/animaux/morse.png (peluche de magasin, palier 4)
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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
CANNELLE = M.hexa("#e48a62")                  # la dominante : cannelle rosé
CREME = M.hexa("#fff1dc")                     # les babines (la moustache)
POINTS = M.hexa("#7a4a3a")                    # les racines de la moustache
IVOIRE = M.hexa("#fff4dc")                    # l'accent : les défenses
SOMBRE = M.hexa("#9a5a44")                    # le bout des nageoires
# l'échine, de la queue à la nuque (avance vers l'arrière, hauteur) : couché derrière, dressé devant
ECHINE = [(0.56, 0.085), (0.40, 0.135), (0.20, 0.205), (0.02, 0.330), (-0.11, 0.450), (-0.19, 0.548)]
GALBE = [(0.0, 0.0), (0.03, 0.060), (0.15, 0.150), (0.30, 0.215), (0.48, 0.262), (0.66, 0.252), (0.82, 0.205), (0.94, 0.165), (1.0, 0.0)]
TETE = Vector((0.0, -0.250, 0.628))
MENTON, LACET = -18.0, 0.0                   # le menton levé, la tête tournée vers nous


def construire():
    a = K.Animal("morse")
    a.taille = 3.50

    # ----- le corps : une seule masse couchée le long de l'échine, large et plate dessous -----
    fil = K.Fil([(0.0, y, z) for y, z in ECHINE], (1, 0, 0))
    L = fil.long
    corps = A.tour(A.profil([(r, f * L) for f, r in GALBE], 8), 56)

    def masse(v):
        s = v * [1.16, 0.96, 1.0]
        s[:, 1] = np.where(s[:, 1] < 0, s[:, 1] * 0.80, s[:, 1])
        return s
    a.piece("corps", corps.sculpte(masse).sculpte(fil.couche), CANNELLE)

    # ----- deux bourrelets de graisse autour du cou -----
    for nom, f, r in (("bourrelet_1", 0.80, 0.205), ("bourrelet_2", 0.90, 0.180)):
        centre, avant, nuque = fil.cadre(f * L)
        a.piece(nom, A.tore(r * 0.93, 0.024, 56, 14).etire(1.16, 0.96, 1.0), CANNELLE, mat=A.cadre(Vector(centre), Vector(avant), Vector(nuque)))

    # ----- la tête : petite et ronde au bout du cou, le menton levé, tournée vers nous -----
    H = A.repere(TETE, (MENTON, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(lambda v: K.bosse(v, (0, -0.6, -0.5), 0.12, 0.4) * [0.130, 0.118, 0.120]), CANNELLE, mat=H)

    # ----- le museau : deux grosses babines crème piquées de points, la moustache en brosse -----
    for nom, c in (("G", 1), ("D", -1)):
        # la moustache : un coussin APLATI et large, enfoncé dans le museau : le bord du bas s'aplatit, le haut se fond dans la tête
        coussin = A.boule(1.0, 40, 20).sculpte(lambda v: np.stack([v[:, 0] * 0.082, v[:, 1] * 0.046, v[:, 2] * np.where(v[:, 2] < 0, 0.036, 0.050)], axis=1))
        a.piece("babine_" + nom, coussin, CREME, mat=H @ A.repere((c * 0.050, -0.096, -0.052), (0, 0, c * 10)),
                motif=("pois", POINTS))
    a.tete = H @ Vector((0, -0.120, 0.010))

    # ----- les défenses : longues, ivoire, qui sortent sous les babines et descendent en s'écartant à peine -----
    for nom, c in (("G", 1), ("D", -1)):
        racine = H @ Vector((c * 0.040, -0.118, -0.098))
        bout = racine + H3 @ Vector((c * 0.030, -0.070, -0.250))
        D = A.cadre(racine, bout - racine, H3 @ Vector((0, -1, 0)))
        defense = A.tour(A.profil([(0, -0.02), (0.031, 0.0), (0.029, 0.08), (0.021, 0.17), (0.010, 0.245), (0, 0.270)], 6), 32)
        defense.sculpte(lambda v: v + np.stack([np.zeros(len(v)), 0.06 * (v[:, 2] / 0.26) ** 2, np.zeros(len(v))], axis=1))
        a.piece("defense_" + nom, defense, IVOIRE, mat=D, poil=False)

    # ----- les yeux : petits, enfoncés, sous une paupière lourde : il toise -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, H3 @ Vector((c * 0.62, -0.62, 0.42)))
        a.bouton("oeil_" + nom, p + n * 0.005, n, 0.026)               # de vrais yeux visibles : plus gros, un peu sortis du poil
        P = A.cadre(p + n * 0.004, n, H3 @ Vector((0, 0, 1)))
        # (paupière retirée : yeux ouverts, bouton net, sans air fatigué ni fâché)

    # ----- les nageoires de devant : larges, plantées au sol de part et d'autre du poitrail, qui le tiennent dressé -----
    for nom, c in (("G", 1), ("D", -1)):
        epaule = Vector((c * 0.195, -0.120, 0.180))
        sol = Vector((c * 0.350, -0.290, 0.022))
        W = A.cadre(epaule, sol - epaule, Vector((c * 0.70, 0.70, 0.0)))          # le plat de la main vers le ciel

        def pagaie(v):
            s = v.copy()
            z = v[:, 2]
            s[:, 1] *= 0.55 + 0.45 * K.lisse((z + 0.8) / 1.4)
            return s * [0.036, 0.100, 0.150]
        nag = A.boule(1.0, 36, 18)
        nag.teinte = np.where((nag.v[:, 2] > 0.70)[:, None], np.asarray(SOMBRE), np.asarray(CANNELLE))
        a.piece("nageoire_" + nom, nag.sculpte(pagaie).pose((0, 0, 0.130)), None, mat=W)

    # ----- les palmes de derrière : deux éventails posés à plat, ouverts en V derrière lui -----
    for nom, c in (("G", 1), ("D", -1)):
        palme = A.boule(1.0, 32, 16)
        palme.teinte = np.where((palme.v[:, 2] > 0.55)[:, None], np.asarray(SOMBRE), np.asarray(CANNELLE))

        def eventail(v):
            s = v.copy()
            z = v[:, 2]
            s[:, 1] *= 0.40 + 0.60 * K.lisse((z + 1.0) / 1.6)
            s[:, 2] -= 0.18 * np.exp(-(v[:, 1] / 0.35) ** 2) * K.lisse((z - 0.6) / 0.4)
            return s * [0.024, 0.110, 0.120]
        W = A.cadre(Vector((c * 0.040, 0.560, 0.070)), Vector((c * 0.45, 0.85, -0.20)), Vector((c * 0.85, -0.45, 0.0)))
        a.piece("palme_" + nom, palme.sculpte(eventail).pose((0, 0, 0.100)), None, mat=W)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("morse", styles.style_de("morse"), sys.modules[__name__]), "Morse")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py morse). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.082                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.313, 0.341)),
    ('tete', 'corps', (0.006, -0.187, 0.535)),
    ('patte_ar_G', 'corps', (0.047, 0.574, 0.082)),
]

PORTEURS = [
    ('bourrelet_1', 'corps'), ('bourrelet_2', 'corps'), ('nageoire', 'corps'), ('defense', 'tete'),
    ('lourde', 'tete'), ('babine', 'corps'), ('corps', 'corps'), ('palme', 'patte_ar', True), ('tete', 'tete'),
    ('oeil', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'),
    ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
    p.ouvert = borne(1 - 0.3 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.62, 0.02))
    return p


def avance(t):
    """Sa marche : les pattes alternent, le corps oscille, la tête dodeline."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 26.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_ar_G', 1), ('patte_ar_D', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.024 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.045), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
