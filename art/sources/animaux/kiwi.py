"""Le kiwi en peluche de velours ras (2e dessin) : le seul oiseau qui a l'air d'un mammifère. Un corps en poire penché
en avant, tout en franges de poils hirsutes brun tabac, sans ailes ni queue, le cou qui coule du corps sans qu'on puisse
dire où commence la tête, de petits yeux, d'énormes cuisses de coq, de gros pieds à trois orteils, et ce long bec fin
d'ivoire qui fouille le sol, narines au bout, comme un nez de fourmilier. Il renifle : la pointe du bec dans la terre.

    python kiwi.py        fabrique la fiche art/apercus/animaux/kiwi.png (velours ras, palier 3)
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

TABAC = M.hexa("#c8a068")                     # la dominante : brun tabac (le poil le fonce : on le prend clair)
FONCE = M.hexa("#8a6a40")                     # les franges du dessus, le crâne
IVOIRE = M.hexa("#fff2d8")                    # l'accent : le bec
PATTE = M.hexa("#c89878")                     # les pattes
CHARBON = M.hexa("#3a2c28")
# le fil du corps, de la croupe au bout du cou (et de la tête) : en poire penchée, le cou qui plonge vers le sol
FIL = [(0.12, 0.340), (0.07, 0.365), (0.00, 0.360), (-0.06, 0.335), (-0.11, 0.300), (-0.14, 0.270)]
GALBE = [(0.0, 0.0), (0.035, 0.030), (0.090, 0.080), (0.140, 0.240), (0.150, 0.400), (0.120, 0.560), (0.080, 0.700), (0.055, 0.830),
         (0.050, 0.915), (0.052, 0.965), (0, 1.0)]


def touffes(maille, nb, longueur, rayon, graine, couleur, dos_seul=True, sens=(0.0, 0.0, 0.0)):
    """Des touffes en cônes épais plantés sur la surface d'une pièce (plus de cartes plates) : nb cônes d'une longueur et
    d'un rayon de base donnés, dirigés vers l'extérieur (un peu vers « sens »), colorés par couleur(t) (t : 0 base, 1 pointe)."""
    rng = np.random.default_rng(graine)
    v = np.asarray(maille.v, float)
    centre = v.mean(axis=0)
    choisis = np.nonzero(v[:, 2] > centre[2] + (0.0 if dos_seul else -9.0))[0]
    choisis = rng.choice(choisis, size=min(nb, len(choisis)), replace=False)
    profil = A.profil([(0, 0), (rayon, 0.004), (rayon * 0.95, longueur * 0.40), (rayon * 0.78, longueur * 0.78), (rayon * 0.42, longueur * 0.95), (0, longueur)], 4)
    cone = A.tour(profil, 8)
    cone.teinte = np.stack([np.array(couleur(z / longueur)) for z in cone.v[:, 2]])
    sortie = None
    for i in choisis:
        d = v[i] - centre
        d = d / max(np.linalg.norm(d), 1e-9) + np.asarray(sens)
        d = d / max(np.linalg.norm(d), 1e-9)
        m = cone.copy() if hasattr(cone, "copy") else cone
        pos = Vector(tuple(v[i] - d * 0.004))
        haut = Vector((0.0, 0.0, 1.0)) if abs(d[2]) < 0.95 else Vector((0.0, 1.0, 0.0))
        t = A.cadre(pos, Vector(tuple(d)), haut)
        m = m.pose((0, 0, 0)) if False else m
        piece = _poser(cone, t)
        sortie = piece if sortie is None else sortie + piece
    return sortie


def _poser(maille, rep):
    """Une copie de la maille portée dans le repère rep (une matrice 4x4)."""
    import copy
    m = copy.deepcopy(maille)
    M3 = np.array(rep.to_3x3())
    tr = np.array(rep.to_translation())
    m.v = np.asarray(m.v, float) @ M3.T + tr
    return m


def construire():
    a = K.Animal("kiwi")
    a.taille = 0.60

    # ----- le corps, le cou et la tête : une seule pièce en poire penchée, les franges de poils hirsutes dessus -----
    fil = K.Fil([(0.0, y, z) for y, z in FIL], (1, 0, 0))
    L = fil.long
    corps = A.tour(A.profil([(r, f * L) for r, f in GALBE], 8), 48)
    corps.teinte = np.tile(np.asarray(TABAC, float), (len(corps.v), 1))
    corps.teinte[(np.floor(corps.v[:, 2] / 0.032) % 2 == 0)] *= 0.86                       # de fines bandes sombres : le poil hirsute
    corps = corps.sculpte(fil.couche)
    a.piece("corps", corps, None)
    # (plus de touffes en cônes : elles faisaient un cône de pin ; le kiwi est un doux manteau de poils hirsutes, rendu par le
    # velours lui-même, avec de fines bandes sombres couchées sur le corps)
    centre, avant, nuque = fil.cadre(0.93 * L)
    C = Vector(centre)

    # ----- la tête : une vraie petite tête ronde, en vue au bout du cou (plus noyée dans les touffes) -----
    # la tête tournée de 26° vers la caméra (les deux yeux visibles sur les trois vues)
    lat_ = np.cross(np.array(avant), np.array(nuque))
    av2 = np.array(avant) * math.cos(math.radians(26)) - lat_ * math.sin(math.radians(26))
    lat2 = np.cross(av2, np.array(nuque))
    Hc = Vector(np.array(centre) + np.array(avant) * 0.040 + np.array(nuque) * 0.012)
    tete_ = A.boule(1.0, 36, 18)
    tete_.teinte = np.tile(np.asarray(TABAC, float) * 1.08, (len(tete_.v), 1))
    a.piece("tete", tete_.etire(0.056, 0.062, 0.058), None, mat=A.cadre(Hc, Vector(av2), Vector(nuque)))

    # ----- le bec : long, fin, d'ivoire, légèrement recourbé, qui descend et fouille le sol ; les narines au bout -----
    dirige = Vector(av2 * 0.78 + np.array([0.0, 0.0, -0.62]))
    dirige.normalize()
    B = A.cadre(Hc + dirige * 0.040, dirige, Vector((0, 0, 1)))

    def canne(v):
        s = v.copy()
        s[:, 1] += 0.040 * np.clip(v[:, 2] / 0.225, 0, 1) ** 2.0
        return s
    bec = A.tour(A.profil([(0, 0), (0.020, 0.006), (0.016, 0.040), (0.011, 0.130), (0.008, 0.200), (0.005, 0.240), (0, 0.256)], 5), 24)
    a.piece("bec", bec.sculpte(canne), IVOIRE, mat=B, poil=False)
    a.tete = Hc + Vector(nuque) * 0.020 + dirige * 0.025                       # le CENTRE de la tête (le bec pointe vers le bas : le viser le sortait du cadre, en haut)
    for c in (1, -1):
        p, n = a.surface("tete", Hc, Vector(av2 * 0.60 + np.array(nuque) * 0.30 + lat2 * c * 0.75))
        a.oeil("oeil_" + ("G" if c > 0 else "D"), p + n * 0.004, n, 0.0155)

    # ----- les cuisses : d'énormes jambons, hauts sur la croupe ; les pattes : minces, les gros pieds à trois orteils -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.tube(A.courbe([(c * 0.098, 0.130, 0.250), (c * 0.106, 0.108, 0.180), (c * 0.108, 0.070, 0.120)], 5),
                                         lambda t_: 0.044 - 0.016 * t_, 18), TABAC)       # une cuisse qui descend dans la patte, plus de boule
        chemin = [(c * 0.100, 0.100, 0.200), (c * 0.108, 0.070, 0.120), (c * 0.108, 0.030, 0.026)]
        a.piece("patte_" + nom, A.tube(A.courbe(chemin, 5), 0.020, 12), PATTE, poil=False)
        doigts = None
        for ang in (-30, 0, 30):
            d = A.boule(1.0, 14, 8).etire(0.013, 0.060, 0.011).pose((0, -0.044, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("doigts_" + nom, doigts, PATTE, pos=(c * 0.108, 0.020, 0.012), poil=False)
    # les proportions du kiwi réel (silhouettes.py contre references_3d/kiwi : un corps rond, plus large que haut)
    import deformer_b as DF
    DF.etirer(a, sy=1.18, sz=0.86)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("kiwi", styles.style_de("kiwi"), sys.modules[__name__]), "Kiwi")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py kiwi). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.212                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.079, 0.313)),
    ('tete', 'corps', (-0.004, -0.128, 0.241)),
    ('patte_ar_G', 'corps', (0.103, 0.141, 0.212)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('cuisse', 'patte_ar', True), ('doigts', 'patte_ar', True), ('corps', 'corps'),
    ('patte', 'patte_ar', True), ('tete', 'tete'), ('oeil', 'tete'), ('bec', 'tete'), ('paupiere_0', 'paupiere_0'),
    ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.064 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.117), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
