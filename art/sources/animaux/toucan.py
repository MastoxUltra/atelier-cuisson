"""Le toucan en peluche de velours ras : un noir bleuté, la gorge et la poitrine blanc crème, le dessous de la queue
rouge vif, un cercle bleu ciel autour de l'œil, et surtout ce bec monumental, plus gros que sa tête, jaune citron à la
base, orange puis rouge, la pointe noire. Un snob qui porte son bec comme une œuvre d'art : il se tient droit comme un
i, le bec pointé vers nous en biais, l'œil mi-clos de quelqu'un qui n'a pas besoin d'expliquer.

    python toucan.py        fabrique la fiche art/apercus/animaux/toucan.png (velours ras, palier 3)

Les 5 traits de l'espèce (photos de Commons, 15/10) : 1. un bec énorme, aussi long que le corps, jaune à la base, orange puis
rouge, la pointe sombre ; 2. le corps noir, la gorge et la poitrine blanches ; 3. un cercle de peau bleu clair autour de l'œil ;
4. le dessous de la queue rouge ; 5. des pattes courtes grises à deux doigts devant, deux derrière.
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

GONFLAGE = True       # la base aux volumes gonflés de l'Artiste (fusion.py) : jointures fondues, bouts arrondis

NOIR = M.hexa("#2b3140")                      # la dominante : noir bleuté (le poil le fonce : on le prend un peu clair)
CREME = M.hexa("#fffbec")                     # la gorge et la poitrine
CITRON = M.hexa("#fff04a")                    # l'accent : le bec, à la base
ORANGE = M.hexa("#ff9a1f")                    # le milieu du bec
ROUGE = M.hexa("#f02a22")                     # le bout du bec, le dessous de la queue
CIEL = M.hexa("#6fd0f2")                      # le cercle de l'œil
CORPS = Vector((0.0, 0.040, 0.290))
TETE = Vector((0.0, -0.045, 0.515))
LACET = 44.0                                  # de trois quarts : le bec se voit en long, les deux yeux restent visibles


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
        a.piece("lourde_" + nom, K.paupiere(0.021, 0.58), NOIR, mat=A.cadre(p + n * 0.005, n, H3 @ Vector((0, 0, 1))), poil=False)

    # ----- le bec : une énorme gouttière tournée, bandée jaune, orange, rouge, la pointe noire ; un peu courbe -----
    B = A.cadre(H @ Vector((0, -0.075, -0.014)), H3 @ Vector((0, -0.97, -0.20)), H3 @ Vector((0, 0.2, 0.98)))

    def courbe_(v):
        s = v.copy()
        s[:, 1] -= 0.035 * np.clip(v[:, 2] / 0.300, 0, 1) ** 2.0
        s[:, 0] *= 1 - 0.18 * np.clip(v[:, 2] / 0.300, 0, 1)
        return s
    bec = A.tour(A.profil([(0, 0), (0.048, 0.010), (0.066, 0.060), (0.068, 0.130), (0.056, 0.210), (0.036, 0.270), (0.014, 0.300), (0, 0.308)], 6), 40)
    # les couleurs se fondent l'une dans l'autre (citron, orange, rouge) et la pointe noire est nette : plus de bandes dures
    zz = bec.v[:, 2] / 0.308
    cles = [0.0, 0.14, 0.46, 0.84, 0.90, 0.93, 1.0]
    palette = [CITRON, CITRON, ORANGE, ROUGE, ROUGE, NOIR, NOIR]
    bec.teinte = np.stack([np.interp(zz, cles, [c[k] for c in palette]) for k in range(3)], axis=1)
    a.piece("bec", bec.etire(0.82, 1.0, 1.0).sculpte(courbe_), None, mat=B, poil=False)
    # la mandibule : plus courte et plus fine, sous le bec, d'un rouge orangé
    bas = A.tour(A.profil([(0, 0), (0.036, 0.008), (0.046, 0.060), (0.040, 0.140), (0.024, 0.215), (0.008, 0.262), (0, 0.272)], 6), 36)
    a.piece("mandibule", bas.etire(0.76, 0.55, 1.0).sculpte(courbe_), ORANGE, mat=B @ A.repere((0, -0.044, 0.006)), poil=False)

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


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py toucan). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.135                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.113, 0.162)),
    ('tete', 'corps', (0.001, -0.018, 0.431)),
    ('patte_av_G', 'corps', (0.051, 0.022, 0.135)),
    ('aile_G', 'corps', (0.109, 0.085, 0.441)),
    ('queue', 'corps', (0.000, 0.114, 0.162)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('sous_queue', 'corps'), ('orteils', 'patte_av', True), ('lourde', 'tete'), ('mandibule', 'tete'),
    ('corps', 'corps'), ('cerne', 'tete'), ('queue', 'queue'), ('patte', 'patte_av', True), ('tete', 'tete'),
    ('oeil', 'tete'), ('aile', 'aile', True), ('bec', 'tete'), ('paupiere_0', 'paupiere_0'),
    ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add('queue', rot=(0, 0, 10 * onde(t, 1)))
    p.paire('aile', rot=(0, -3 * cloche(t, 0.55, 0.06), 0))
    p.ouvert = borne(1 - 0.3 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.62, 0.02))
    return p


def avance(t):
    """Sa marche : les pattes alternent, le corps oscille, la tête dodeline."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 18.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_av_D', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('queue', rot=(-6, 0, -10 * s))
    p.paire('aile', rot=(0, -2 + 2 * onde(t, 2), 0))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(34 * bas + 3 * coups, 0, 0))
    p.paire('patte_av', rot=(-30 * bas, 0, 0))
    p.add('tete', rot=(16 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.040 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    p.paire('aile', rot=(0, -48 * vol, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.02), rot=(36, 0, 6), ech=(1 + 0.010 * r, 1, 1 + 0.020 * r))
    p.paire('patte_av', rot=(-30, 0, 0))
    p.add('tete', rot=(32, 4, 40))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
