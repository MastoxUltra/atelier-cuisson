"""Le perroquet en peluche, cousu main : un ara écarlate franc, la face nue blanche cernée de rides brodées, un énorme bec
en crochet ivoire, les ailes bleu roi bordées de jaune, et deux très longues plumes de queue qui traînent derrière lui
jusqu'au sol. Un cabotin perché sur ses pattes serrées : le poitrail en avant, la tête penchée par-dessus l'épaule,
l'œil rond et fixe, une aile entrouverte comme pour saluer.

    python perroquet.py        fabrique la fiche art/apercus/animaux/perroquet.png (cousu main, palier 2)
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


def propres(points, eps=2e-4):
    """Les points d'un tracé sans doublons consécutifs (un tube dont deux points se suivent à l'identique se déforme en NaN) ;
    au moins deux points, écartés d'un millimètre au pire."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie

ECARLATE = M.hexa("#f2392a")                  # la dominante : écarlate franc (le poil le fonce un peu)
ROI = M.hexa("#2f62e0")                       # l'accent : le bleu roi des ailes et de la queue
JAUNE = M.hexa("#ffd22a")                     # la bande jaune des ailes
IVOIRE = M.hexa("#fff2d6")                    # le bec, la face nue
CHARBON = M.hexa("#3a3436")                   # la mandibule du bas, les griffes
CORPS = Vector((0.0, 0.040, 0.300))
TETE = Vector((0.0, -0.075, 0.520))
LACET = 28.0                                  # la tête tournée vers nous, par-dessus l'épaule gauche


def plume(chemin, large, face, paliers, plat=0.30, cotes=16):
    """Une longue plume plate (le geste des mèches du cheval) peinte par tronçons : paliers = [(fraction, couleur), ...]."""
    p = A.courbe(chemin, 8)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    n0 = np.asarray(face, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.linalg.norm(t, axis=1, keepdims=True)
        x = np.cross(n0, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.55 * large, 0.04 * L), (0.95 * large, 0.20 * L), (large, 0.45 * L), (0.82 * large, 0.75 * L),
                     (0.40 * large, 0.95 * L), (0, L)], 5)
    m = A.tour(prof, cotes).etire(1.0, plat, 1.0)
    t = np.zeros((len(m.v), 3))
    reste = np.ones(len(m.v), bool)
    for fr, c in paliers:
        ici = reste & (m.v[:, 2] <= fr * L)
        t[ici] = c
        reste &= ~ici
    t[reste] = paliers[-1][1]
    m.teinte = t
    return m.sculpte(couche)


def construire():
    a = K.Animal("perroquet")
    a.taille = 0.85

    # ----- le corps : un œuf dressé, le poitrail en avant, cambré ; deux coutures de dos -----
    def oeuf(v):
        v = K.bosse(v, (0, -0.9, 0.2), 0.12, 0.5)
        s = v * [0.108, 0.095, 0.175]
        s[:, 0] *= 1 - 0.20 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s
    corps = A.boule(1.0, 56, 28).sculpte(oeuf)
    G.sillons(corps, [14], 0.005, 1.1)
    a.piece("corps", corps, ECARLATE, pos=CORPS, rot=(-16, 12, 0))
    a.couture("dos", "corps", 14, 0.22, 0.92)

    # ----- la tête : ronde et haute, les joues d'écarlate ; tournée vers nous -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 48, 24).etire(0.092, 0.088, 0.090), ECARLATE, mat=H)
    a.couture("crane", "tete", 14, 0.55, 0.98)
    a.tete = H @ Vector((0, -0.100, -0.010))

    # ----- la face nue : une grande rustine blanche cousue, cernée de trois rides brodées charbon ; l'œil rond, fixe -----
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.62, -0.74, 0.08))
        a.rustine("face_" + nom, "tete", TETE, regard, lambda th: 0.30 + 0.07 * math.cos(2 * th), IVOIRE, 0.003, 0)
        p, n = a.surface("tete", TETE, regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0120)
        # (paupière retirée : yeux ouverts, bouton net, sans air fatigué ni fâché)
        for k, dy in enumerate((0.12, 0.0, -0.12)):
            ride = [H3 @ Vector((c * (0.56 + 0.10 * t), -0.70 + 0.04 * t, 0.10 + dy + 0.05 * t * (1 if k != 1 else 0))) for t in np.linspace(0, 1, 4)]
            a.broderie("ride_%s%d" % (nom, k), propres(a.trace("tete", TETE, ride, 0.004)), 0.0014, CHARBON)

    # ----- le bec : énorme, ivoire, en crochet qui retombe ; la mandibule du bas, courte, charbon -----
    B = A.cadre(H @ Vector((0, -0.078, -0.020)), H3 @ Vector((0, -0.86, -0.50)), H3 @ Vector((0, 0.5, -0.86)))

    def crochet(v):
        s = v.copy()
        z = np.clip(v[:, 2] / 0.122, 0, 1)
        s[:, 1] += 0.092 * z ** 1.8                                                 # la pointe se recourbe vers le bas
        return s
    haut = A.tour(A.profil([(0, 0), (0.056, 0.010), (0.062, 0.040), (0.052, 0.074), (0.032, 0.100), (0.012, 0.116), (0, 0.122)], 6), 36)
    a.piece("bec", haut.etire(1.0, 1.15, 1.45).sculpte(crochet), IVOIRE, mat=B, poil=False)
    bas = A.tour(A.profil([(0, 0), (0.034, 0.008), (0.030, 0.034), (0.018, 0.056), (0, 0.064)], 5), 28)
    a.piece("mandibule", bas.etire(0.90, 0.70, 1.20).pose((0, -0.046, 0.010)), CHARBON, mat=B, poil=False)

    # ----- les ailes : deux galets écarlates sur les flancs, la bande jaune, le bout bleu roi ; la gauche entrouverte -----
    for nom, c, rot in (("G", 1, (-8, 0, 58)), ("D", -1, (-8, 0, -2))):
        aile = A.boule(1.0, 40, 20)
        t = np.where((aile.v[:, 2] > -0.10)[:, None], np.asarray(JAUNE), np.asarray(ECARLATE))
        t[aile.v[:, 2] > 0.30] = ROI
        aile.teinte = t

        def galet(v):
            s = K.emousse(v, 0.88)
            s[:, 1] *= 1 - 0.50 * K.lisse((v[:, 2] + 0.2) / 1.2)
            return s
        a.piece("aile_" + nom, aile.sculpte(galet).etire(0.030, 0.052, 0.185), None, pos=(c * 0.112, 0.052, 0.272), rot=rot)

    # ----- la queue : deux très longues plumes plates, écarlates à la racine, jaunes puis bleu roi, qui traînent au sol -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.020, 0.150, 0.230), (c * 0.050, 0.250, 0.130), (c * 0.085, 0.380, 0.050), (c * 0.110, 0.560, 0.022), (c * 0.150, 0.740, 0.016)]
        a.piece("plume_" + nom, plume(chemin, 0.040, (1, 0, 0), [(0.30, ECARLATE), (0.55, JAUNE), (1.0, ROI)]), None, poil=False)

    # ----- les pattes : il porte son poids sur la droite, plantée, et tient la gauche repliée contre le ventre -----
    plantee = [(-0.045, 0.030, 0.150), (-0.048, 0.000, 0.080), (-0.050, -0.030, 0.026)]
    levee = [(0.045, 0.030, 0.150), (0.058, 0.000, 0.120), (0.052, -0.050, 0.140)]
    for nom, c, chemin, pied, rot in (("D", -1, plantee, (-0.050, -0.030, 0.010), (0, 0, 0)), ("G", 1, levee, (0.052, -0.070, 0.135), (-24, 0, 0))):
        a.piece("patte_" + nom, A.tube(A.courbe(chemin, 5), 0.022, 12), CHARBON, poil=False)
        doigts = None
        for ang in (-26, 0, 26):
            d = A.boule(1.0, 16, 8).etire(0.012, 0.050, 0.011).pose((0, -0.040, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("orteils_" + nom, doigts, CHARBON, pos=pied, rot=rot, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("perroquet", styles.style_de("perroquet"), sys.modules[__name__]), "Perroquet")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py perroquet). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.127                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.051, 0.342)),
    ('tete', 'corps', (0.009, -0.054, 0.435)),
    ('patte_ar_D', 'corps', (-0.045, 0.021, 0.155)),
    ('patte_av_D', 'corps', (-0.062, -0.066, 0.020)),
    ('patte_ar_G', 'corps', (0.052, 0.005, 0.161)),
    ('patte_av_G', 'corps', (0.052, -0.137, 0.171)),
    ('aile_G', 'corps', (0.091, 0.065, 0.453)),
    ('queue', 'corps', (-0.001, 0.151, 0.230)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('mandibule', 'corps'), ('orteils', 'patte_av', True), ('ride_G0', 'corps'),
    ('ride_G1', 'corps'), ('ride_G2', 'corps'), ('ride_D0', 'corps'), ('ride_D1', 'corps'), ('ride_D2', 'corps'),
    ('lourde', 'tete'), ('corps', 'corps'), ('patte', 'patte_ar', True), ('plume', 'queue'), ('crane', 'tete'),
    ('tete', 'tete'), ('face', 'corps'), ('oeil', 'tete'), ('aile', 'aile', True), ('bec', 'tete'), ('dos', 'corps'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    pas = 26.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.038 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    p.paire('aile', rot=(0, -48 * vol, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.070), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
