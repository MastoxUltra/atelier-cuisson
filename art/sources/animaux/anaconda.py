"""L'anaconda en peluche de magasin (3e dessin : plus de bouée) : un serpent ÉPAIS, d'un olive sombre à grandes taches
noires cernées de crème, vautré en lourdes boucles lâches et irrégulières, l'une passant sur l'autre, la queue qui traîne
en pointe, et sur le haut de la pile une tête plate et large, posée sur une boucle, les narines sur le dessus, deux petits
yeux d'or à la fente verticale, la langue fourchue qui goûte l'air. Le roi de la rivière, qui ne fait jamais rien.

    python anaconda.py        fabrique la fiche art/apercus/animaux/anaconda.png (peluche de magasin, palier 4)
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


# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
OLIVE = np.array(M.hexa("#8c8a34"))           # la dominante : olive sombre (bronze verdâtre)
TACHE = np.array(M.hexa("#2a2420"))           # l'accent : les grandes taches charbon
ANNEAU = np.array(M.hexa("#e8d68a"))          # le cerne crème des taches
VENTRE = np.array(M.hexa("#d8c880"))          # le dessous de la tête
OR = M.hexa("#ffcf2a")                        # les yeux
ROSE = M.hexa("#e0556a")                      # la langue
NOIR = M.hexa("#241e1a")
EPAIS = 0.056                                 # le rayon du corps


def mouchetures(v, cote, rayon, graine=0, proba=0.74):
    v = np.asarray(v, float)
    base = np.floor(v / cote).astype(np.int64)
    dedans = np.zeros(len(v), bool)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                c = base + np.array([dx, dy, dz], dtype=np.int64)
                h = ((c[:, 0] * 73856093) ^ (c[:, 1] * 19349663) ^ (c[:, 2] * 83492791) ^ (graine * 40503)) & 0x7FFFFFFF

                def alea(m):
                    return ((((h * m) + 12345) >> 9) & 0xFFFF) / 65535.0
                present = alea(1103515245) < proba
                centre = (c + np.stack([alea(214013), alea(1664525), alea(22695477)], axis=1)) * cote
                r = rayon * (0.70 + 0.60 * alea(134775813))
                dedans |= present & (np.linalg.norm(v - centre, axis=1) < r)
    return dedans


def rayon(t):
    """Le rayon le long du corps (0 = la pointe de la queue, 1 = la nuque)."""
    queue = max(0.0, (0.22 - t) / 0.22) ** 1.3
    cou = min(1.0, max(0.0, (t - 0.86) / 0.14))
    return EPAIS * (1.0 - 0.80 * queue) - 0.014 * cou * cou * (3 - 2 * cou)


# la pile de boucles : une grande boucle à plat, une plus petite posée dessus, puis le cou qui monte poser la tête
CHEMIN = [(0.50, 0.22, 0.020), (0.46, 0.34, 0.052), (0.34, 0.42, 0.056), (0.14, 0.46, 0.056), (-0.08, 0.40, 0.056),
          (-0.28, 0.28, 0.056), (-0.38, 0.06, 0.056), (-0.34, -0.18, 0.056), (-0.16, -0.32, 0.056), (0.08, -0.34, 0.056),
          (0.30, -0.24, 0.056), (0.40, -0.04, 0.060), (0.34, 0.14, 0.100), (0.18, 0.24, 0.150), (-0.02, 0.26, 0.162),
          (-0.18, 0.16, 0.162), (-0.22, -0.04, 0.162), (-0.12, -0.18, 0.164), (0.06, -0.18, 0.176), (0.16, -0.06, 0.206),
          (0.08, 0.08, 0.250), (-0.06, 0.14, 0.262)]


def construire():
    a = K.Animal("anaconda")
    a.taille = 4.50

    # ----- le corps : un gros boudin olive à grandes taches charbon cernées de crème, en boucles lâches et irrégulières -----
    ch = np.asarray([tuple(q) for q in A.courbe(propres(CHEMIN), 8)], float)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(ch, axis=0), axis=1))])
    n = max(32, int(fait[-1] / 0.010))
    u = np.linspace(0.0, 1.0, n)
    ch = np.stack([np.interp(u * fait[-1], fait, ch[:, k]) for k in range(3)], axis=1)
    corps = A.tube(ch, rayon, 24)
    p = np.asarray(corps.v, float)
    grand = mouchetures(p, 0.150, 0.055, 4)
    cerne = mouchetures(p, 0.150, 0.070, 4)
    petit = mouchetures(p + 0.07, 0.100, 0.020, 9, 0.5)
    t = np.tile(OLIVE, (len(p), 1))
    t[cerne] = ANNEAU
    t[grand] = TACHE
    t[petit & ~cerne] = TACHE
    corps.teinte = t
    a.piece("corps", corps, None, poil=False)
    fin = Vector(ch[-1])
    sens = Vector(ch[-1] - ch[-9]).normalized()

    # ----- la tête : plate et large, en coin arrondi, posée sur la boucle du dessus ; narines sur le dessus ; yeux d'or -----
    T = A.cadre(fin + sens * 0.050 + Vector((0, 0, 0.004)), sens, Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = A.boule(1.0, 56, 28)
    tete.teinte = np.where((tete.v[:, 1] < -0.15)[:, None], VENTRE, OLIVE)
    a.piece("tete", tete.etire(0.062, 0.048, 0.098), None, mat=T, poil=False)         # une tête un peu plus épaisse : les yeux s'y posent
    a.tete = T @ Vector((0, 0.0, 0.080))
    for nom, c in (("G", 1), ("D", -1)):
        vers = T3 @ Vector((c * 0.58, 0.82, 0.42))                      # sur le dessus de la tête plate, de part et d'autre : posés sur la surface
        pe, ne = a.surface("tete", T.to_translation(), vers)
        a.rustine("bille_" + nom, "tete", T.to_translation(), vers, 0.20, OR, 0.0015, 0)            # l'iris d'or PEINT à plat (plus de bosse jaune)
        a.bouton("oeil_" + nom, pe + ne * 0.0008, ne, 0.0140)                                          # la pupille noire enfoncée dans l'iris
        a.piece("narine_" + nom, A.boule(1.0, 14, 8).etire(0.008, 0.008, 0.005), NOIR, mat=A.cadre(T @ Vector((c * 0.026, 0.034, 0.080)), T3 @ Vector((c * 0.2, 0.9, 0.3))), poil=False)
    base = T @ Vector((0, -0.005, 0.094))
    tige = [tuple(base), tuple(base + T3 @ Vector((0, -0.004, 0.040))), tuple(base + T3 @ Vector((0, 0.0, 0.080)))]
    a.piece("langue", A.tube(A.courbe(propres(tige), 4), 0.0065, 8), ROSE, poil=False)
    for c, nom in ((1, "G"), (-1, "D")):
        fourche = [Vector(tige[-1]), Vector(tige[-1]) + T3 @ Vector((c * 0.018, 0.004, 0.030))]
        a.piece("fourche_" + nom, A.tube([tuple(q) for q in fourche], 0.0050, 8), ROSE, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("anaconda", styles.style_de("anaconda"), sys.modules[__name__]), "Anaconda")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py anaconda). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.158                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.273, 0.158)),
    ('tete', 'corps', (-0.034, 0.119, 0.249)),
]

PORTEURS = [
    ('fourche', 'tete'), ('narine', 'tete'), ('langue', 'tete'), ('corps', 'corps'), ('bille', 'corps'),
    ('tete', 'tete'), ('oeil', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
    ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.047 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.087), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.add('tete', rot=(32, 4, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
