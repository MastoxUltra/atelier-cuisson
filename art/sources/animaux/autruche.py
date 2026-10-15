"""L'autruche en peluche de velours ras : un noir velouté (un noir d'encre qui tire sur le brun), un gros corps ovoïde
aux ailes blanches en grands éventails de plumes bouclées, une queue blanche en panache, un long cou rosé presque nu
terminé par une toute petite tête au grand œil à longs cils et au bec plat, et deux jambes énormes d'un rose sale aux
cuisses nues et à deux orteils. La dame distraite : lancée en pleine foulée, un pied levé, le cou tendu en avant et
légèrement ondulé, les ailes à demi déployées pour garder l'équilibre.

    python autruche.py        fabrique la fiche art/apercus/animaux/autruche.png (velours ras, palier 3)
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


NOIR = np.array(M.hexa("#4a4448"))            # la dominante : noir velouté (le poil la fonce : on la prend plus claire)
BLANC = np.array(M.hexa("#fffaf0"))           # l'accent : les ailes, la queue
PEAU = np.array(M.hexa("#e8aaa0"))            # le cou, les cuisses : rose sale
BEC = M.hexa("#e8c8a8")
CHARBON = M.hexa("#2e2828")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def eventail(pos, rot, large, long, etages=6, couleur=BLANC, pointe=None):
    """Un éventail de plumes : « etages » gros pétales aplatis, en arc, qui partent du même point ; une seule pièce."""
    m = None
    for k in range(etages):
        u = (k / (etages - 1)) - 0.5
        long_k = long * (0.80 + 0.20 * math.cos(u * 2.4))
        pl = A.boule(1.0, 16, 8).etire(large, 0.026, long_k * 0.5)
        pl = pl.pose((0, 0, long_k * 0.5)).pose((0, 0, 0), (0, math.degrees(u) * 70, 0))
        m = pl if m is None else m + pl
    return m


def construire():
    a = K.Animal("autruche")
    a.taille = 2.40

    # ----- le corps : un gros œuf couché, la poitrine haute, la croupe qui monte ; noir velouté -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.500, 0.960), (0.300, 1.020), (0.020, 1.030), (-0.250, 1.050), (-0.380, 1.080))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.170), (0.15, 0.260), (0.45, 0.300), (0.75, 0.275), (0.92, 0.205), (1.0, 0.0)], L, 64, 0.010)
    corps.teinte = np.tile(NOIR, (len(corps.v), 1))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou : long, rosé, presque nu, tendu en avant et légèrement ondulé ; la tête minuscule, le bec plat, le grand œil -----
    BASE = Vector((0.0, -0.330, 1.110))
    pts = ((0.0, 0.0), (0.050, 0.130), (0.120, 0.300), (0.100, 0.500), (0.170, 0.680), (0.300, 0.780))      # (avance, monte)
    enc = K.Fil([tuple(BASE + Vector((0, -u, z))) for u, z in pts], (1, 0, 0))
    Lc = enc.long
    cou = fuseau([(0.0, 0.130), (0.10, 0.085), (0.40, 0.050), (0.80, 0.042), (1.0, 0.046)], Lc, 40, 0.008)
    cou.teinte = np.tile(PEAU, (len(cou.v), 1))
    a.piece("cou", cou.sculpte(enc.couche), None)
    centre, avant, nuque = enc.cadre(Lc)
    H = A.cadre(Vector(centre) + Vector((0.0, -0.020, 0.0)), Vector((0.20, -1.0, -0.10)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.052, 0.062, 0.050), tuple(PEAU), mat=H)
    bec = A.boule(1.0, 28, 14).etire(0.046, 0.074, 0.020)
    a.piece("bec", bec, BEC, mat=H @ A.repere((0, -0.080, -0.006)), poil=False)
    a.tete = H @ Vector((0, -0.100, 0.0))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.92, -0.20, 0.36))
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0200)
        a.piece("cils_" + nom, K.paupiere(0.0250, 0.30), CHARBON, mat=A.cadre(p + n * 0.006, n, H3 @ Vector((0, 0, 1))), poil=False)

    # ----- les ailes : de grands éventails de plumes blanches qui se déploient de chaque côté du corps ; la queue : un panache -----
    for nom, c, rot in (("G", 1, (0, 0, 52)), ("D", -1, (0, 0, -30))):
        ev = eventail((0, 0, 0), (0, 0, 0), 0.085, 0.52, 7)
        a.piece("aile_" + nom, ev, tuple(BLANC), mat=A.cadre(Vector((c * 0.240, 0.040, 1.120)), Vector((c * 0.55, 0.78, -0.30)), Vector((c * 0.2, 0, 1))), poil=False)
    queue = eventail((0, 0, 0), (0, 0, 0), 0.075, 0.46, 7)
    a.piece("queue", queue, tuple(BLANC), mat=A.cadre(Vector((0.0, 0.440, 1.090)), Vector((0.0, 0.85, 0.35)), Vector((1, 0, 0))), poil=False)

    # ----- les jambes : énormes, rosées, la cuisse nue ; une jambe plantée, l'autre levée en pleine foulée ; deux orteils -----
    def jambe(pts, r0):
        f = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.30, r0 * 0.70), (0.52, r0 * 0.56), (0.62, r0 * 0.66), (0.95, r0 * 0.50), (1.0, 0.0)], f.long, 32, 0.012)
        m.teinte = np.tile(PEAU, (len(m.v), 1))
        return m.sculpte(f.couche)
    plan_g = [(0.140, 0.100, 0.960), (0.150, 0.130, 0.680), (0.150, 0.090, 0.360), (0.150, 0.020, 0.040)]
    plan_d = [(-0.140, 0.100, 0.960), (-0.150, -0.040, 0.720), (-0.150, -0.240, 0.620), (-0.150, -0.330, 0.400)]
    for nom, pts in (("G", plan_g), ("D", plan_d)):
        a.piece("jambe_" + nom, jambe(pts, 0.105), None)
    for ang, dx in ((-14, -0.034), (10, 0.034)):
        a.piece("orteil_G%d" % ang, A.boule(1.0, 14, 8).etire(0.032, 0.090, 0.022), BEC, pos=(0.150 + dx, -0.040, 0.020), rot=(0, 0, ang), poil=False)
        a.piece("orteil_D%d" % ang, A.boule(1.0, 14, 8).etire(0.032, 0.090, 0.022), BEC, pos=(-0.150 + dx, -0.420, 0.360), rot=(-20, 0, ang), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("autruche", styles.style_de("autruche"), sys.modules[__name__]), "Autruche")



# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py autruche). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.638                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.293, 1.028)),
    ('cou', 'corps', (0.000, -0.284, 1.192)),
    ('tete', 'cou', (-0.000, -0.628, 1.838)),
    ('patte_ar_G', 'corps', (0.141, 0.120, 0.928)),
    ('patte_av_D', 'corps', (-0.142, 0.036, 0.945)),
    ('patte_av_G', 'corps', (0.126, -0.035, 0.041)),
    ('aile_G', 'corps', (-0.098, -0.085, 1.253)),
    ('queue', 'corps', (-0.001, 0.290, 1.026)),
]

PORTEURS = [
    ('orteil_G-14', 'patte_av_G'), ('orteil_D-14', 'patte_av_D'), ('oeil_reflet', 'tete'),
    ('orteil_G10', 'patte_av_G'), ('orteil_D10', 'patte_av_D'), ('corps', 'corps'), ('jambe', 'patte_ar', True),
    ('jambe', 'patte_av', True), ('queue', 'queue'), ('tete', 'tete'), ('oeil', 'tete'), ('aile', 'aile', True),
    ('cils', 'tete'), ('cou', 'cou'), ('bec', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
    ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.191 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    p.paire('aile', rot=(0, -48 * vol, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.351), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
