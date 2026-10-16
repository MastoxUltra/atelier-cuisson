"""Le lemming en peluche, cousu main : une poire caramel doré, la calotte et la grande selle charbon qui lui couvre les épaules, le ventre et le
museau crème, les petites pattes roses. Il se dresse sur ses pattes de derrière, le torse bombé, un poing levé au ciel
et l'autre sur la hanche, le regard calme et vif tourné vers nous : il va peut-être sauter de la falaise, mais il y réfléchit.

    python lemming.py        fabrique la fiche art/apercus/animaux/lemming.png (cousu main, palier 2)
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

CARAMEL = M.hexa("#f1c06a")                   # la dominante : caramel doré (le poil le fonce : on le prend nettement plus clair)
CHARBON = M.hexa("#35302f")                   # la calotte et la selle
CREME = M.hexa("#fff3dc")                     # le ventre, le museau
ROSE = M.hexa("#ee9aa6")                      # l'accent : les pattes, le nez, le dedans des oreilles
CORPS = Vector((0.0, 0.020, 0.185))
TETE = Vector((0.0, -0.040, 0.395))
LACET = 16.0                                  # la tête tournée vers nous


def peindre(m, region):
    """Peint la boule encore unité : region(v) rend « charbon », « creme » ou « caramel » pour chaque point."""
    t = np.zeros((len(m.v), 3))
    noms = region(m.v)
    for nom, c in (("caramel", CARAMEL), ("charbon", CHARBON), ("creme", CREME)):
        t[noms == nom] = c
    m.teinte = t
    return m


def construire():
    a = K.Animal("lemming")
    a.taille = 0.55

    # ----- le corps : une poire dodue, le torse bombé, penchée en arrière (il se cambre) ; la selle charbon couvre le dos -----
    def poire(v):
        v = K.bosse(v, (0, -0.9, 0.35), 0.14, 0.45)
        s = v * [0.118, 0.108, 0.150]
        s[:, 0] *= 1 + 0.12 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        s[:, 1] *= 1 + 0.10 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s

    def zone(v):
        x = np.abs(v[:, 0])                                   # une selle en lentille : large sur le dos, qui s'effile sur les flancs
        sel = (v[:, 1] > -0.22) & (v[:, 2] > -0.40 + 0.80 * x) & (v[:, 2] < 0.86 - 0.35 * x)
        ventre = (v[:, 1] < -0.30) & (v[:, 2] < 0.55)
        return np.where(sel, "charbon", np.where(ventre, "creme", "caramel"))
    corps = peindre(A.boule(1.0, 56, 28), zone).sculpte(poire)
    G.sillons(corps, [14], 0.005, 1.1)
    a.piece("corps", corps, None, pos=CORPS, rot=(-8, 0, 0))
    a.couture("dos", "corps", 14, 0.20, 0.95, fil=CARAMEL)
    a.rustine("ventre", "corps", CORPS + Vector((0, -0.01, 0.0)), (0, -0.90, -0.15), lambda th: 0.62 - 0.08 * math.cos(2 * th),
              K.CREME, 0.003, 24)

    # ----- la tête : large et ronde, les joues pleines, la calotte charbon qui descend jusqu'à la nuque -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()

    def large(v):
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.9, -0.25, -0.35), 0.18, 0.30)
        return v * [0.104, 0.096, 0.092]

    def calotte(v):
        return np.where((v[:, 2] > 0.18) & (v[:, 1] > -0.55), "charbon", np.where((v[:, 1] < -0.55) & (v[:, 2] < -0.10), "creme", "caramel"))
    a.piece("tete", peindre(A.boule(1.0, 48, 24), calotte).sculpte(large), None, mat=H)
    a.couture("crane", "tete", 14, 0.45, 0.98, fil=CARAMEL)
    a.tete = H @ Vector((0, -0.095, -0.005))

    # ----- le museau : court et rond, crème, le nez rose, la bouche serrée -----
    a.piece("museau", A.boule(1.0, 28, 14).etire(0.044, 0.046, 0.038), CREME, mat=H @ A.repere((0, -0.083, -0.030)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.013, 0.009, 0.010), ROSE, mat=H @ A.repere((0, -0.124, -0.019)), poil=False)
    bouche = [H3 @ Vector(d) for d in ((-0.22, -0.84, -0.50), (0.0, -0.90, -0.56), (0.22, -0.84, -0.50))]
    a.broderie("bouche", A.courbe(propres(a.trace("museau", H @ Vector((0, -0.083, -0.030)), bouche, 0.003)), 4), 0.0022, CHARBON)
    for nom, c in (("G", 1), ("D", -1)):                      # deux moustaches charbon
        for k, dz in enumerate((0.010, -0.014)):
            depart = H @ Vector((c * 0.030, -0.100, -0.026 + dz * 0.4))
            a.broderie("moustache_%s%d" % (nom, k), [depart, depart + H3 @ Vector((c * 0.050, 0.004, dz * 0.8)),
                                                      depart + H3 @ Vector((c * 0.092, 0.010, dz * 1.5))], 0.0013, CHARBON)

    # ----- les yeux : grands, vivants, au regard calme et curieux (plus de sourcils froncés) -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, H3 @ Vector((c * 0.46, -0.82, 0.18)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0180)

    # ----- les oreilles : deux petits ronds, le dedans rose -----
    po = A.profil([(0, 0), (0.026, 0.008), (0.030, 0.028), (0.022, 0.048), (0.008, 0.058), (0, 0.062)], 5)
    for nom, c in (("G", 1), ("D", -1)):
        E = A.cadre(H @ Vector((c * 0.066, 0.004, 0.066)), H3 @ Vector((c * 0.55, 0.05, 0.84)), H3 @ Vector((c * 0.40, -0.90, 0.0)))
        a.piece("oreille_" + nom, A.tour(po, 28).etire(1.0, 0.40, 1.0), CHARBON, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 20).etire(0.58, 0.30, 0.70).pose((0, 0.006, 0.008)), ROSE, mat=E, poil=False)

    # ----- les bras : le gauche lève un poing au ciel, le droit sur la hanche ; poings roses -----
    for nom, c, chemin in (("G", 1, [(0.100, -0.015, 0.290), (0.150, -0.050, 0.350), (0.158, -0.080, 0.425), (0.150, -0.085, 0.470)]),
                           ("D", -1, [(-0.100, -0.015, 0.290), (-0.158, 0.005, 0.230), (-0.150, -0.025, 0.170), (-0.108, -0.055, 0.185)])):
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.034 - 0.008 * t, 14), CARAMEL)
        a.piece("poing_" + nom, A.boule(1.0, 24, 12).etire(0.030, 0.032, 0.030), CARAMEL, pos=chemin[-1])

    # ----- les jambes courtes, les grosses pattes roses plantées en canard ; la queue : un petit moignon -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.boule(1.0, 28, 14).etire(0.052, 0.068, 0.070), CARAMEL, pos=(c * 0.072, 0.030, 0.075))
        a.piece("pied_" + nom, A.boule(1.0, 28, 14).etire(0.046, 0.074, 0.024), ROSE, pos=(c * 0.082, -0.040, 0.022), rot=(0, 0, c * 14))
        a.ourlet("orteils_" + nom, "pied_" + nom, 0.50)
    a.piece("queue", A.boule(1.0, 20, 10).etire(0.030, 0.034, 0.030), CARAMEL, pos=(0, 0.132, 0.080))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lemming", styles.style_de("lemming"), sys.modules[__name__]), "Lemming")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py lemming). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.298                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.069, 0.106)),
    ('tete', 'corps', (0.001, -0.034, 0.304)),
    ('oreille_G', 'tete', (0.060, -0.019, 0.465)),
    ('patte_av_G', 'corps', (0.154, -0.083, 0.459)),
    ('patte_ar_D', 'corps', (-0.123, -0.006, 0.290)),
    ('patte_ar_G', 'corps', (0.075, 0.033, 0.143)),
    ('queue', 'corps', (-0.000, 0.102, 0.092)),
]

PORTEURS = [
    ('moustache_G0', 'tete'), ('moustache_G1', 'tete'), ('moustache_D0', 'tete'), ('moustache_D1', 'tete'),
    ('oeil_reflet', 'tete'), ('pavillon', 'oreille', True), ('oreille', 'oreille', True), ('sourcil', 'tete'),
    ('orteils', 'patte_av', True), ('ventre', 'corps'), ('museau', 'tete'), ('cuisse', 'patte_ar', True),
    ('bouche', 'tete'), ('corps', 'corps'), ('poing', 'corps'), ('queue', 'queue'), ('crane', 'tete'),
    ('tete', 'tete'), ('pied', 'patte_av', True), ('oeil', 'tete'), ('bras', 'patte_av', True),
    ('bras', 'patte_ar', True), ('nez', 'tete'), ('dos', 'corps'), ('paupiere_0', 'paupiere_0'),
    ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
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
    pas = 18.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.paire('oreille', rot=(-8 + 3 * onde(t, 2, -0.25), 0, 0))
    p.add('queue', rot=(-6, 0, -10 * s))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.089 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.02), rot=(36, 0, 6), ech=(1 + 0.010 * r, 1, 1 + 0.020 * r))
    p.paire('patte_av', rot=(-30, 0, 0))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
