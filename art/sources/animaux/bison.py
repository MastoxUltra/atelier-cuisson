"""Le bison en peluche de magasin : un brun tabac roux, la masse sombre et laineuse de l'avant (la bosse haute des
épaules, la crinière qui lui tombe sur les yeux, la barbe), et l'arrière-train mince, clair, qui s'effile. Deux petites
cornes noires, relevées, et une queue en point d'interrogation au bout touffu. Un chef de troupeau qui n'a pas dit son
dernier mot : la tête baissée à hauteur de genou, le regard par en dessous, la queue dressée : il va charger.

    python bison.py        fabrique la fiche art/apercus/animaux/bison.png (peluche de magasin, palier 4)
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
TABAC = M.hexa("#b8794a")                     # la dominante : brun tabac roux
SOMBRE = M.hexa("#5a3a2a")                    # l'accent : la crinière, la barbe, le bas des jambes
CORNE = M.hexa("#3a3434")                     # les cornes, les sabots
CROUPE = Vector((0.0, 0.50, 0.50))            # le bout arrière du corps (une pièce tournée, couchée vers l'avant)
LACET, PIQUE = 20.0, 28.0                     # la tête tournée vers nous, le museau à hauteur de genou


def construire():
    a = K.Animal("bison")
    a.taille = 3.50

    # ----- le corps : tourné de la croupe à la bosse puis couché (X la gauche, Y le dos, Z l'avant) : fin derrière,
    #       de plus en plus épais, la bosse des épaules très haute ; teinté : tabac derrière, sombre sur l'avant -----
    corps = A.tour(A.profil([(0, 0), (0.105, 0.020), (0.160, 0.110), (0.185, 0.250), (0.215, 0.420), (0.265, 0.580),
                             (0.295, 0.730), (0.270, 0.870), (0.190, 0.960), (0, 1.010)], 6), 56)
    K.bandes(corps, [(0.50, TABAC), (0.64, (0.45 * TABAC[0] + 0.55 * SOMBRE[0], 0.45 * TABAC[1] + 0.55 * SOMBRE[1], 0.45 * TABAC[2] + 0.55 * SOMBRE[2])), (9, SOMBRE)])

    def bosse(v):
        s = v.copy()
        h = np.exp(-((v[:, 2] - 0.72) / 0.17) ** 2)
        s[:, 1] = np.where(v[:, 1] > 0, v[:, 1] * (1 + 0.42 * h), v[:, 1] * (1 + 0.06 * h))      # la bosse au garrot
        s[:, 0] *= 1 + 0.10 * h
        return s
    a.piece("corps", corps.sculpte(bosse), None, pos=CROUPE, rot=(90 + 3, 0, 0))

    # ----- la tête : lourde et basse, le front large sous la crinière ; le museau sombre -----
    H = A.repere(Vector((0.0, -0.700, 0.390)), (PIQUE, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(lambda v: K.bosse(v, (0, -0.7, -0.2), 0.12, 0.40) * [0.150, 0.210, 0.155]), SOMBRE, mat=H)
    a.piece("criniere", A.boule(1.0, 40, 20).etire(0.215, 0.225, 0.250), SOMBRE, pos=(0, -0.470, 0.585))
    a.piece("barbe", A.boule(1.0, 32, 16).etire(0.085, 0.110, 0.170), SOMBRE, pos=(0, -0.760, 0.285))
    a.piece("toupet", A.boule(1.0, 28, 14).etire(0.120, 0.105, 0.075), SOMBRE, mat=H @ A.repere((0, -0.120, 0.080)))
    a.tete = H @ Vector((0, -0.210, 0.000))

    # ----- les yeux : de petites billes sous le toupet, qui vous regardent par en dessous -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.72, -0.60, 0.05)))
        a.bouton("oeil_" + nom, p + n * 0.003, n, 0.028)

    # ----- les cornes : deux courts crochets noirs sortis du crâne, qui se relèvent -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [H @ Vector(q) for q in ((c * 0.115, -0.010, 0.095), (c * 0.215, -0.020, 0.100), (c * 0.275, -0.040, 0.170), (c * 0.250, -0.070, 0.270))]
        a.piece("corne_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.034 - 0.026 * t, 14), CORNE, poil=False)

    # ----- les jambes : de grosses culottes de poils devant (sombres, épaisses), les bas minces et sombres, les sabots noirs -----
    avant = lambda x: [(x, -0.360, 0.560), (x * 1.10, -0.375, 0.330), (x * 1.12, -0.370, 0.170), (x * 1.12, -0.380, 0.045)]
    arriere = lambda x: [(x * 0.80, 0.300, 0.460), (x * 1.00, 0.370, 0.300), (x * 1.05, 0.410, 0.150), (x * 1.05, 0.425, 0.045)]
    for nom, chemin, r0, r1, haut in (("av_G", avant(0.150), 0.092, 0.050, 0.55), ("av_D", avant(-0.150), 0.092, 0.050, 0.55),
                                      ("ar_G", arriere(0.135), 0.078, 0.046, 0.30), ("ar_D", arriere(-0.135), 0.078, 0.046, 0.30)):
        jambe = K.tube_peint(A.courbe(chemin, 6), lambda t, r0=r0, r1=r1: r0 + (r1 - r0) * min(1.0, t * 1.4), [(haut, SOMBRE if "av" in nom else TABAC), (1, SOMBRE)], 18)
        a.piece("jambe_" + nom, jambe, None)
        x, y, _z = chemin[-1]
        a.piece("sabot_" + nom, A.boule(1.0, 24, 12).etire(0.060, 0.074, 0.040), CORNE, pos=(x, y - 0.012, 0.034), poil=False)

    for nom, c in (("G", 1), ("D", -1)):                      # les cuisses : deux jambons tabac qui cachent l'attache des jambes
        a.piece("cuisse_" + nom, A.boule(1.0, 28, 14).etire(0.090, 0.135, 0.150), TABAC, pos=(c * 0.125, 0.345, 0.420))

    # ----- la queue : dressée en point d'interrogation, le bout touffu sombre -----
    queue = A.tube(A.courbe([(0, 0.490, 0.560), (0, 0.560, 0.640), (0, 0.585, 0.760), (0, 0.540, 0.840)], 6), lambda t: 0.028 - 0.010 * t, 12)
    a.piece("queue", queue, TABAC)
    a.piece("touffe", A.boule(1.0, 24, 12).etire(0.050, 0.055, 0.085), SOMBRE, pos=(0, 0.520, 0.850))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("bison", styles.style_de("bison"), sys.modules[__name__]), "Bison")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py bison). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.537                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.142, 0.515)),
    ('tete', 'corps', (-0.019, -0.521, 0.444)),
    ('patte_av_G', 'corps', (0.159, -0.370, 0.546)),
    ('patte_ar_G', 'corps', (0.126, 0.346, 0.528)),
    ('queue', 'corps', (0.001, 0.486, 0.573)),
]

PORTEURS = [
    ('jambe_av', 'patte_av', True), ('jambe_ar', 'patte_ar', True), ('criniere', 'corps'),
    ('sabot_av', 'patte_av', True), ('sabot_ar', 'patte_ar', True), ('toupet', 'corps'), ('touffe', 'queue'),
    ('cuisse', 'patte_ar', True), ('corps', 'corps'), ('barbe', 'tete'), ('corne', 'tete'), ('queue', 'queue'),
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
    p.add('queue', rot=(0, 0, 10 * onde(t, 1)))
    p.ouvert = borne(1 - 0.3 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.62, 0.02))
    return p


def avance(t):
    """Sa marche : les pattes alternent, le corps oscille, la tête dodeline."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 26.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('queue', rot=(-6, 0, -10 * s))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.add('queue', rot=(0, 0, -7 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.161 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.295), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
