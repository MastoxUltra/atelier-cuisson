"""Le papillon morpho en peluche, cousu main : quatre grandes ailes de feutrine d'un bleu ciel électrique, le bord noir
cousu autour comme un passepoil et un liseré de petits points blancs, le dessous brun orné d'yeux ; un petit corps
duveteux, deux antennes à massue. Le plus beau des courants d'air : posé à plat, les ailes OUVERTES en un léger V,
le bleu électrique tourné vers le ciel, une antenne qui nous cherche.

    python papillon_morpho.py        fabrique la fiche art/apercus/animaux/papillon_morpho.png (cousu main, palier 2)
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

BLEU = M.hexa("#35b7ff")                      # la dominante : bleu ciel électrique
NOIR = M.hexa("#25222e")                      # l'accent : le passepoil des ailes, la tête, les antennes
DESSOUS = M.hexa("#9a6a46")                   # le dessous, brun
CORPS_C = M.hexa("#5a4538")                   # le corps, brun sombre
POINTS = M.hexa("#fff6e8")                    # le liseré de petits points


def aile(rx, ry, pointe, decalage=0.0, n=48):
    """Le contour d'une aile : une goutte arrondie de rayon (rx, ry), plus ou moins pointue vers l'extérieur."""
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    x = rx * (0.5 + 0.5 * np.cos(t)) * (1 + pointe * np.maximum(0.0, np.cos(t)) * np.sin(t) ** 2)
    y = ry * np.sin(t) * (1 - 0.15 * np.cos(t))
    return np.stack([x + decalage, y], axis=1)


def construire():
    a = K.Animal("papillon_morpho")
    a.taille = 0.30

    # ----- le corps : un petit fuseau duveteux couché à l'horizontale, la tête ronde devant, les antennes à massue ;
    #       posé sur ses six petites pattes -----
    corps = A.tour(A.profil([(0, 0), (0.016, 0.010), (0.022, 0.060), (0.020, 0.120), (0.012, 0.180), (0, 0.200)], 5), 24)
    a.piece("corps", corps, CORPS_C, mat=A.repere((0.0, 0.092, 0.066), (90, 0, 0)))
    a.piece("tete", A.boule(1.0, 24, 12).etire(0.020, 0.019, 0.020), NOIR, pos=(0, -0.120, 0.066))
    a.tete = Vector((0, -0.150, 0.080))
    antennes = None
    for c, nom in ((1, "G"), (-1, "D")):
        tige = [(c * 0.008, -0.130, 0.076), (c * 0.040, -0.190, 0.110), (c * 0.080, -0.230, 0.140)]
        t = A.tube(A.courbe(tige, 4), 0.0030, 8) + A.boule(1.0, 12, 6).etire(0.009, 0.012, 0.009).pose(tige[-1], (0, 0, c * 30))
        antennes = t if antennes is None else antennes + t
        p, n = a.surface("tete", Vector((0, -0.120, 0.066)), Vector((c * 0.7, -0.7, 0.2)))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0068)
    a.piece("antennes", antennes, NOIR, poil=False)
    pattes = None
    for c in (1, -1):
        for y in (-0.080, -0.010, 0.060):
            t = A.tube(A.courbe([(c * 0.014, y, 0.058), (c * 0.050, y - 0.008, 0.030), (c * 0.062, y - 0.014, 0.004)], 4), 0.0030, 6)
            pattes = t if pattes is None else pattes + t
    a.piece("pattes", pattes, NOIR, poil=False)

    # ----- les ailes : OUVERTES à plat (un léger V), le bleu électrique vu de dessus, le bord noir cousu comme un passepoil,
    #       le liseré de petits points blancs ; le dessous brun en bas. Chacune est faite de trois couches ; les quatre
    #       ailes d'une même couche ne font qu'une pièce -----
    couches = {"dessous": None, "bord": None, "bleu": None, "points": None}

    def ajoute(cle, m):
        couches[cle] = m if couches[cle] is None else couches[cle] + m
    for c in (1, -1):
        for rx, ry, y0, pointe, balayage in ((0.150, 0.085, -0.014, 0.20, -22), (0.120, 0.075, 0.034, 0.05, 20)):
            contour = aile(rx, ry, pointe, 0.010) * np.array([c, 1.0])
            if c < 0:
                contour = contour[::-1]
            # le bord festonné : de petites vagues sur le contour (Cohérence : plus d'assiettes lisses)
            cx, cy = contour.mean(axis=0)
            ang = np.arctan2(contour[:, 1] - cy, contour[:, 0] - cx)
            fest = 1.0 + 0.045 * np.sin(12 * ang)
            contour = np.stack([cx + (contour[:, 0] - cx) * fest, cy + (contour[:, 1] - cy) * fest], axis=1)
            Rc = float(np.linalg.norm(contour - np.array([cx, cy]), axis=1).max())

            def voute(v, cx=cx, cy=cy, Rc=Rc):
                s_ = v.copy()
                d = np.minimum(np.hypot(v[:, 0] - cx, v[:, 1] - cy) / Rc, 1.0)
                s_[:, 2] += 0.024 * (1.0 - d ** 2)                                   # l'aile bombée : une voûte, pas une assiette
                return s_
            pos = (c * 0.014, y0, 0.064)
            rot = (0, -c * 12, c * balayage)
            for niveau, ech, epaisseur, ecart in (("dessous", 1.00, 0.004, 0.0000), ("bord", 0.98, 0.004, 0.0035), ("bleu", 0.82, 0.004, 0.0075)):
                m = A.decoupe(contour * ech, epaisseur, casse=0.0016)
                m = m.sculpte(voute)
                ajoute(niveau, m.pose((0, 0, ecart), (0, 0, 0)).pose(pos, rot))
            M_ = A.repere(pos, rot)
            for k in range(0, len(contour), 6):
                x, y = contour[k] * 0.93
                q = M_ @ Vector((x, y, 0.0105))
                ajoute("points", A.boule(1.0, 8, 4).etire(0.0045, 0.0045, 0.0016).pose((q.x, q.y, q.z)))
    for cle, couleur in (("dessous", DESSOUS), ("bord", NOIR), ("bleu", BLEU), ("points", POINTS)):
        a.piece("ailes_" + cle, couches[cle], couleur, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("papillon_morpho", styles.style_de("papillon_morpho"), sys.modules[__name__]), "Papillon morpho")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py papillon_morpho). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.060                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.009, 0.096)),
    ('tete', 'corps', (-0.001, -0.104, 0.073)),
    ('patte_ar_G', 'corps', (0.000, -0.014, 0.060)),
    ('aile_G', 'corps', (0.001, -0.056, 0.101)),
]

PORTEURS = [
    ('ailes_dessous', 'aile_G'), ('ailes_points', 'aile_G'), ('oeil_reflet', 'tete'), ('ailes_bord', 'aile_G'),
    ('ailes_bleu', 'aile_G'), ('antennes', 'corps'), ('pattes', 'patte_ar_G'), ('corps', 'corps'), ('tete', 'tete'),
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
    p.paire('aile', rot=(0, -3 * cloche(t, 0.55, 0.06), 0))
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
    p.paire('aile', rot=(0, -2 + 2 * onde(t, 2), 0))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.018 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('aile', rot=(0, -48 * vol, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.033), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
