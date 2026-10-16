"""Le vautour en peluche de velours ras (2e dessin, d'après photos : plus de bloc) : un grand rapace PERCHÉ, voûté, le
corps en pente qui plonge vers l'avant, un brun sombre en plumes lisses, deux grandes ailes repliées en cape dont les
longues plumes noires croisent la queue, le COU NU, long et ridé, d'un rose gris qui sort d'une collerette de duvet
blanc, la petite tête chauve au bec crochu et fort, l'œil enfoncé ; des cuisses en culottes de plumes et de grosses
pattes à serres. Il attend, de profil, la tête tournée vers nous, un regard patient de croque-mort.

    python vautour.py        fabrique la fiche art/apercus/animaux/vautour.png (velours ras, palier 3)
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


BRUN = np.array(M.hexa("#7a6250"))            # la dominante : brun sombre (le poil le fonce : on le prend plus clair)
PLUME = np.array(M.hexa("#9a8068"))           # les couvertures claires
PEAU = np.array(M.hexa("#e0a8a0"))            # le cou nu, la tête : rose gris
DUVET = np.array(M.hexa("#fff6e8"))           # la collerette
BEC = M.hexa("#c8b898")
OEIL = M.hexa("#c8903a")
CHARBON = np.array(M.hexa("#3a3230"))         # le bout des ailes, les serres
PAS = 0.006
LACET = 28.0


def O_couche(m, mat):
    """La maille m posée dans le repère mat (les points transformés)."""
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("vautour")
    a.taille = 1.10

    # ----- le corps : un tronc voûté en pente, la queue basse derrière, la poitrine bombée devant ; le dos plus sombre -----
    # 16/10, 3e essai du corps (« une carapace de tortue ») : le dos voûté qui penche en avant ; un brun uni (plus de taches
    # rondes claires) ; deux vraies ailes en cape, gardées à part de la peau gonflée (fondues, elles faisaient la carapace)
    fil = K.Fil([(0.0, y, z) for y, z in ((0.250, 0.270), (0.140, 0.362), (0.010, 0.440), (-0.090, 0.488))], (1, 0, 0))   # plus couché
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.05, 0.105), (0.25, 0.180), (0.55, 0.185), (0.84, 0.140), (1.0, 0.0)], L, 56)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.teinte = np.tile(BRUN, (len(th), 1))
    a.fusion_a_part = ("aile", "plumes")                    # les ailes et les rémiges restent des pièces : on les lit
    def voute(v):                                          # le dos voûté : une bosse sur les épaules, côté dos (+Y de la pièce)
        s = v.copy()
        f = v[:, 2] / L
        s[:, 1] += np.where(v[:, 1] > 0, 0.045 * np.exp(-((f - 0.72) / 0.16) ** 2), 0.0)
        return s
    a.piece("corps", corps.sculpte(voute).sculpte(fil.couche), None)

    # ----- les ailes : deux capes repliées sur les flancs, les couvertures claires en haut, les longues plumes noires qui
    #       descendent et croisent la queue -----
    for nom, c in (("G", 1), ("D", -1)):
        # une aile repliée : un long fuseau plaqué contre le flanc, large à l'épaule, qui s'effile en pointe vers la queue
        # une aile repliée en cape : plate, haute sur le flanc, de l'épaule jusqu'à la queue ; brune, le bout sombre (les rémiges)
        # (4e essai : vue en bout, l'aile ronde faisait un disque ; longue et effilée, étagée en trois tons, elle se lit)
        aile = A.tour(A.profil([(0, 0), (0.050, 0.030), (0.086, 0.100), (0.086, 0.200), (0.072, 0.320), (0.048, 0.440), (0.024, 0.540),
                                (0, 0.620)], 6), 36)
        zz = aile.v[:, 2]
        aile.teinte = np.where((zz > 0.40)[:, None], tuple(CHARBON),                                 # les rémiges, sombres
                               np.where((zz < 0.20)[:, None], tuple(np.asarray(BRUN) * 1.12), tuple(BRUN)))   # les couvertures, plus claires
        depart = Vector((c * 0.160, -0.075, 0.470))
        vers = Vector((c * 0.070, 0.86, -0.50)).normalized()
        a.piece("aile_" + nom, aile.etire(0.40, 1.05, 1.0), None, mat=A.cadre(depart, vers, Vector((0, 0, 1))))
        # les longues rémiges sombres, qui se croisent sur la queue (celle de gauche passe à droite)
        remige = A.boule(1.0, 24, 12).etire(0.044, 0.012, 0.250)
        a.piece("plumes_" + nom, O_couche(remige, A.cadre(Vector((c * 0.035, 0.375, 0.205)), Vector((-c * 0.30, 1.0, -0.50)).normalized(), Vector((0, 0, 1)))),
                tuple(CHARBON))
    a.piece("queue", A.boule(1.0, 24, 12).etire(0.070, 0.030, 0.150), tuple(BRUN), pos=(0.0, 0.290, 0.150), rot=(38, 0, 0))

    # ----- le cou nu et ridé, qui s'étire hors de la collerette ; la tête chauve ; le bec crochu -----
    # (16/10, planche 21 : « pas sûr, faut affiner ») : un cou de vautour au repos, court et épais, qui sort d'une
    # collerette pleine (plus le long cou d'oie) ; une tête plus grosse, à l'échelle d'une peluche ; un bec plus fort
    chemin = [(0.0, -0.095, 0.545), (0.0, -0.150, 0.615), (0.0, -0.168, 0.672), (0.0, -0.198, 0.712)]
    cou = A.tube(A.courbe(propres(chemin), 6), lambda t: 0.060 - 0.016 * t, 20)
    cou.teinte = np.tile(PEAU, (len(cou.v), 1))
    a.piece("cou", cou, None, poil=False)
    a.piece("collerette", A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.140, 0.120, 0.078), tuple(DUVET),
            pos=(0.0, -0.085, 0.552), rot=(-18, 0, 0))
    H = A.repere(Vector((0.0, -0.220, 0.738)), (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 40, 20)
    tete.teinte = np.tile(PEAU, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.058, 0.074, 0.060), None, mat=H, poil=False)
    a.tete = H @ Vector((0, -0.105, -0.010))
    # 2e essai : le bec plus petit (il faisait un bec de perroquet), le bout crochu plus sombre, comme le vrai (vautour fauve)
    haut = A.tour(A.profil([(0, 0), (0.033, 0.005), (0.030, 0.031), (0.019, 0.058), (0.007, 0.077), (0, 0.085)], 5), 28)
    haut.teinte = np.where((haut.v[:, 2] > 0.058)[:, None], np.array(M.hexa("#5a5048")), np.array(BEC))

    def crochu(v):
        s = v.copy()
        s[:, 1] *= 1.10
        s[:, 1] -= 0.040 * np.clip(v[:, 2] / 0.085, 0, 1) ** 2.4                     # le crochet, franc
        return s
    a.piece("bec", haut.sculpte(crochu), None, mat=A.cadre(H @ Vector((0, -0.060, -0.012)), H3 @ Vector((0, -1.0, -0.20)), Vector((0, 0, 1))), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.72, -0.52, 0.32))
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0165)
        # (paupière retirée : yeux ouverts, bouton net, sans air fatigué ni fâché)

    # ----- les pattes : des culottes de plumes, de grosses pattes grises, trois serres devant et une derrière -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("culotte_" + nom, A.boule(1.0, 28, 14).etire(0.070, 0.095, 0.115), tuple(BRUN), pos=(c * 0.085, 0.020, 0.230))
        ch = [(c * 0.080, 0.000, 0.170), (c * 0.082, -0.010, 0.090), (c * 0.082, -0.020, 0.018)]
        m = A.tube(A.courbe(propres(ch), 5), 0.026, 12)
        m.teinte = np.tile(PEAU * 0.85, (len(m.v), 1))
        a.piece("patte_" + nom, m, None, poil=False)
        serres = None
        for ang in (-28, 0, 28, 180):
            d = A.boule(1.0, 12, 6).etire(0.010, 0.046, 0.010).pose((0.7 * 0.046 * math.sin(math.radians(ang)), -0.7 * 0.046 * math.cos(math.radians(ang)), 0), (0, 0, ang))
            serres = d if serres is None else serres + d
        a.piece("serres_" + nom, serres, tuple(CHARBON), pos=(c * 0.082, -0.020, 0.012), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("vautour", styles.style_de("vautour"), sys.modules[__name__]), "Vautour")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py vautour). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.167                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.178, 0.370)),
    ('cou', 'corps', (-0.002, -0.074, 0.559)),
    ('tete', 'cou', (-0.004, -0.200, 0.706)),                    # 16/10 : le cou raccourci, la tête plus bas
    ('patte_av_G', 'corps', (0.080, -0.004, 0.167)),
    ('aile_G', 'corps', (0.151, 0.003, 0.486)),
    ('queue', 'corps', (-0.000, 0.169, 0.318)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('collerette', 'corps'), ('culotte', 'corps'), ('plumes', 'queue'),
    ('serres', 'patte_av', True), ('corps', 'corps'), ('patte', 'patte_av', True), ('queue', 'queue'),
    ('aile', 'aile', True), ('tete', 'tete'), ('oeil', 'tete'), ('cou', 'cou'), ('bec', 'tete'),
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
    for nom, sens in [('patte_av_G', 1), ('patte_av_D', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('cou', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('tete', rot=(3 - 2 * onde(t, 2, -0.2), -2 * c, -2 * s))
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
    p.add('cou', rot=(34 * bas + 4 * coups, 0, 5 * leve))
    p.add('tete', rot=(18 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.050 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    p.paire('aile', rot=(0, -48 * vol, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.092), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
