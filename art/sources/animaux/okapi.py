"""L'okapi en peluche de magasin : un brun aubergine velouté, des jambes et une croupe zébrées de crème, de très
grandes oreilles en feuilles, un long cou, une tête étroite aux courtes cornes de peau (les ossicônes) et un museau
sombre. Un timide aux aguets : le corps de profil, la tête retournée par-dessus l'épaule vers nous, les oreilles
dressées, une patte avant levée au bord du pas : il va disparaître dans la forêt, mais il voulait vous voir une fois.

    python okapi.py        fabrique la fiche art/apercus/animaux/okapi.png (peluche de magasin, palier 4)

Les 5 traits de l'espèce (relus sur 12 photos de Commons le 15/10) : 1. la silhouette d'une girafe basse, le dos qui
descend vers la croupe, le cou long, les jambes fines ; 2. le corps uni d'un brun chocolat, les rayures blanc et noir
seulement sur la croupe et les jambes ; 3. la tête étroite et longue, le museau sombre, la joue et le front plus clairs ;
4. de très grandes oreilles larges tenues de côté ; 5. de courtes cornes de peau (ossicônes) et une queue courte à pinceau.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import matieres as M
import peluche as K

GONFLAGE = True       # la base aux volumes gonflés de l'Artiste (fusion.py) : jointures fondues, bouts arrondis

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
AUBERGINE = M.hexa("#7a3a4e")                 # la dominante : brun aubergine
SOMBRE = M.hexa("#5e3446")                    # le museau, le dessus du cou, les ossicônes
CREME = M.hexa("#fff2d8")                     # l'accent : les zébrures, le dedans des oreilles
CORNE = M.hexa("#3a2c2c")                     # les sabots
CROUPE = Vector((0.0, 0.44, 0.620))           # le bout arrière du corps
BASE = Vector((0.0, -0.300, 0.800))           # le pied du cou
# le cou : chaque point (avance, monte) depuis la base ; long, qui s'incline un peu vers l'avant
ARC = [(0.0, 0.0), (0.040, 0.100), (0.070, 0.220), (0.085, 0.340), (0.110, 0.430)]
COU = math.radians(10)
AVANT = Vector((math.sin(COU), -math.cos(COU), 0.0))
FLANC = np.array([math.cos(COU), math.sin(COU), 0.0])
LACET, PIQUE = 62.0, 4.0                      # la tête retournée vers nous, presque de face


def zebrer(m, debuts, largeur, axe=2, creme=CREME, base=AUBERGINE):
    """Peint des zébrures crème en travers d'une pièce tournée droite : debuts = la liste des positions (sur l'axe)
    où commence une bande de cette largeur."""
    t = np.tile(np.asarray(base, float), (len(m.v), 1))
    for d in debuts:
        t[(m.v[:, axe] >= d) & (m.v[:, axe] < d + largeur)] = creme
    m.teinte = t
    return m


def construire():
    a = K.Animal("okapi")
    a.taille = 1.90

    # ----- le corps : tourné de la croupe aux épaules puis couché (Z vers l'avant) ; plus haut devant que derrière,
    #       la croupe ronde et zébrée de crème -----
    def galbe(v):
        s = v.copy()
        s[:, 1] *= np.where(v[:, 1] > 0, 1 + 0.22 * K.lisse((v[:, 2] - 0.30) / 0.5), 1.02)    # le garrot, le ventre plein
        s[:, 0] *= 1 + 0.12 * np.exp(-((v[:, 2] - 0.06) / 0.10) ** 2)                          # la croupe ronde
        return s
    DEGONFLE = 0.80      # le gonflage de la base (fusion.py) élargit corps et membres d'environ 30 % : on part plus mince
    corps = A.tour(A.profil([(r * 1.20 * DEGONFLE, z * 1.25) for r, z in [(0, 0), (0.115, 0.012), (0.170, 0.070), (0.190, 0.170), (0.180, 0.300),
                             (0.175, 0.420), (0.185, 0.540), (0.165, 0.620), (0.115, 0.670), (0, 0.700)]], 6), 56)
    zebrer(corps, [0.050, 0.120, 0.190, 0.260], 0.040)                              # des bandes de crème sur la croupe
    a.piece("corps", corps.sculpte(galbe), None, pos=CROUPE, rot=(90 - 6, 0, 0))

    # ----- le cou : long, étroit, d'une seule pièce couchée sur son arc ; le dessus plus sombre -----
    enc = K.Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in ARC], FLANC)
    L = enc.long
    parts, rayons = [0.04, 0.25, 0.55, 0.80, 0.97], [r * 0.84 for r in (0.185, 0.150, 0.118, 0.098, 0.086)]
    pc = A.profil([(0, 0)] + [(r, p * L) for r, p in zip(rayons, parts)] + [(0, 1.01 * L)], 6)
    a.piece("cou", A.tour(pc, 40).etire(0.82, 1.0, 1.0).sculpte(enc.couche), AUBERGINE)

    # ----- la tête : étroite, le museau long et sombre, retournée vers nous par-dessus l'épaule -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0, 0, 0), nez)
    bout = Vector(enc.cadre(L)[0])
    T = A.repere(bout - T.to_3x3() @ Vector((0, -0.010, 0.070))) @ T
    T3 = T.to_3x3()
    tete = A.tour(A.profil([(0, 0), (0.044, 0.008), (0.062, 0.040), (0.060, 0.090), (0.050, 0.150), (0.042, 0.200),
                            (0.046, 0.240), (0.038, 0.268), (0, 0.285)], 6), 48)
    K.bandes(tete, [(0.205, AUBERGINE), (9, SOMBRE)])
    a.piece("tete", tete.etire(0.86, 1.0, 1.0), None, mat=T)
    a.tete = T @ Vector((0, 0.040, 0.150))

    # ----- les yeux : grands, de chaque côté, sous un sourcil crème ; les oreilles : immenses feuilles dressées -----
    centre = T @ Vector((0, 0, 0.090))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.86, 0.34, 0.22)))
        a.oeil("oeil_" + nom, pos + n * 0.004, n, 0.0185)
        a.rustine("joue_" + nom, "tete", centre, T3 @ Vector((c * 0.62, -0.46, 0.70)), 0.30, CREME, 0.003, 0)       # la joue claire, bas sur le museau : loin de l'œil
        a.piece("lourde_" + nom, K.paupiere(0.021, 0.58), AUBERGINE, mat=A.cadre(pos + n * 0.005, n, T3 @ Vector((0, 1, 0))), poil=False)
        po = A.profil([(0, 0), (0.048, 0.016), (0.062, 0.070), (0.056, 0.130), (0.034, 0.180), (0.010, 0.208), (0, 0.216)], 6)
        vers = (T3 @ Vector((c * 0.82, 0.26, 0.54))).normalized()
        E = A.cadre(T @ Vector((c * 0.050, 0.044, 0.028)) - vers * 0.014, vers, T3 @ Vector((c * 0.2, 0.9, -0.2)))
        a.piece("oreille_" + nom, A.tour(po, 36).etire(1.0, 0.30, 1.0), AUBERGINE, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 28).etire(0.64, 0.30, 0.78).pose((0, 0.008, 0.016)), CREME, mat=E, poil=False)
        # les ossicônes : deux courtes cornes de peau, entre les oreilles, pointues
        oss = A.tour(A.profil([(0, 0), (0.016, 0.004), (0.013, 0.034), (0.007, 0.058), (0, 0.068)], 5), 16)
        a.piece("ossicone_" + nom, oss, SOMBRE, mat=A.cadre(T @ Vector((c * 0.024, 0.060, 0.050)), T3 @ Vector((c * 0.1, 0.8, 0.1)), T3 @ Vector((0, 0, 1))))

    # ----- les jambes : fines, zébrées de crème en bandes, les sabots noirs ; l'antérieur gauche levé -----
    def zebre_jambe(points, r0):
        chemin = A.courbe(points, 8)
        fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(chemin, axis=0), axis=1))])
        bandes, pos, clair = [], 0.0, False
        n = max(int(fait[-1] / 0.040), 1)
        for k in range(n):
            bandes.append(((k + 1) / n, CREME if (k % 2 == 1 and k > 1) else AUBERGINE))
        genou = lambda t: 0.020 * math.exp(-((t - 0.52) / 0.10) ** 2) + 0.016 * math.exp(-((t - 0.88) / 0.07) ** 2)    # le genou, le boulet
        return K.tube_peint(chemin, lambda t: r0 * (1.0 - 0.34 * t) + genou(t), bandes + [(1.0, bandes[-1][1])], 18)
    plantees = (("av_D", [(-0.080, -0.210, 0.620), (-0.100, -0.225, 0.470), (-0.108, -0.255, 0.300), (-0.098, -0.225, 0.140), (-0.094, -0.230, 0.050)]),
                ("ar_G", [(0.090, 0.400, 0.620), (0.116, 0.350, 0.470), (0.118, 0.330, 0.330), (0.112, 0.470, 0.210), (0.108, 0.430, 0.050)]),
                ("ar_D", [(-0.090, 0.400, 0.620), (-0.116, 0.350, 0.470), (-0.118, 0.330, 0.330), (-0.112, 0.470, 0.210), (-0.108, 0.430, 0.050)]))
    for nom, pts in plantees:
        a.piece("patte_" + nom, zebre_jambe(pts, 0.052), None)
        a.piece("sabot_" + nom, A.boule(1.0, 24, 12).etire(0.044, 0.058, 0.032), CORNE, pos=(pts[-1][0], pts[-1][1] - 0.010, 0.026), poil=False)
    levee = [(0.080, -0.210, 0.600), (0.092, -0.230, 0.440), (0.092, -0.320, 0.360), (0.092, -0.340, 0.220)]
    a.piece("patte_av_G", zebre_jambe(levee, 0.052), None)
    a.piece("sabot_av_G", A.boule(1.0, 24, 12).etire(0.044, 0.058, 0.032), CORNE, pos=(0.092, -0.352, 0.200), rot=(-70, 0, 0), poil=False)

    # ----- la queue : fine, avec un pinceau sombre au bout -----
    a.piece("queue", A.tube(A.courbe([(0, 0.470, 0.700), (0, 0.505, 0.620), (0, 0.505, 0.470)], 5), lambda t: 0.020 - 0.008 * t, 12), AUBERGINE)
    a.piece("pinceau", A.boule(1.0, 20, 10).etire(0.024, 0.024, 0.060), SOMBRE, pos=(0, 0.505, 0.430))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("okapi", styles.style_de("okapi"), sys.modules[__name__]), "Okapi")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py okapi). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.599                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.224, 0.889)),
    ('cou', 'corps', (-0.002, -0.172, 0.894)),
    ('tete', 'cou', (0.009, -0.395, 1.185)),
    ('oreille_G', 'tete', (0.048, -0.369, 1.299)),
    ('patte_av_D', 'corps', (-0.090, -0.216, 0.604)),
    ('patte_ar_G', 'corps', (0.103, 0.376, 0.606)),
    ('patte_av_G', 'corps', (0.087, -0.214, 0.588)),
    ('queue', 'corps', (-0.001, 0.462, 0.694)),
]

PORTEURS = [('joue', 'tete'), 
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True),
    ('pavillon', 'oreille', True), ('ossicone', 'corps'), ('sabot_av', 'patte_av', True),
    ('sabot_ar', 'patte_ar', True), ('oreille', 'oreille', True), ('pinceau', 'queue'), ('lourde', 'tete'),
    ('corps', 'corps'), ('queue', 'queue'), ('tete', 'tete'), ('oeil', 'tete'), ('cou', 'cou'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('cou', rot=(2 * r, 0, 8 * g - 6 * d))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add('oreille_G', rot=(0, 0, 20 * cloche(t, 0.50, 0.05) - 8 * g))
    p.add('oreille_D', rot=(0, 0, -20 * cloche(t, 0.88, 0.05) + 6 * d))
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
    p.add('cou', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('tete', rot=(3 - 2 * onde(t, 2, -0.2), -2 * c, -2 * s))
    p.paire('oreille', rot=(-8 + 3 * onde(t, 2, -0.25), 0, 0))
    p.add('queue', rot=(-6, 0, -10 * s))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('cou', rot=(34 * bas + 4 * coups, 0, 5 * leve))
    p.add('tete', rot=(18 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.paire('oreille', rot=(-6 * bas + 5 * leve, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.180 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.330), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
