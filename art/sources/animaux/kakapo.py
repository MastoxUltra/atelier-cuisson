"""Le kakapo en peluche de magasin (4e dessin, repris d'une autre base : le gros œuf de la poule, la tête ronde posée
droit dessus, sans cou) : le perroquet-hibou de Nouvelle-Zélande, énorme, rond, lourd, jaune pâle moucheté de brun ;
un grand DISQUE FACIAL crème autour de deux petits yeux sombres, un gros bec court, crochu et pâle, quelques soies
raides autour ; de petites ailes pliées, une queue courte et usée qui traîne, de grands pieds pâles à quatre doigts. Il
ne vole pas, il ne court pas : il est là, immobile, et il vous regarde avec sérieux.

    python kakapo.py        fabrique la fiche art/apercus/animaux/kakapo.png (peluche de magasin, palier 4)
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
PALE = np.array(M.hexa("#f4e888"))            # la dominante : jaune pâle (jamais vert)
BRUN = np.array(M.hexa("#7a5a30"))            # l'accent : les mouchetures
CREME = M.hexa("#fff6d0")                     # le disque facial, le ventre
BEC = M.hexa("#f2dcb4")                       # le bec
PIED = M.hexa("#d8c4b0")                      # les grands pieds
CHARBON = M.hexa("#3a3028")
CORPS = Vector((0.0, 0.050, 0.205))
TETE = Vector((0.0, -0.110, 0.370))
LACET = 20.0


def mouchetures(v, cote, rayon, graine=0, proba=0.70):
    """Vrai là où un point tombe dans une tache : des sphères posées au hasard dans un quadrillage en 3D ; la surface les
    coupe en ronds de tailles variées."""
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
                r = rayon * (0.55 + 0.9 * alea(134775813))
                dedans |= present & (np.linalg.norm(v - centre, axis=1) < r)
    return dedans


def pied():
    """Un grand pied zygodactyle : deux doigts devant (vers -Y), deux derrière."""
    def doigt(degres, long):
        t = math.radians(degres)
        return A.boule(1.0, 16, 8).etire(0.016, long, 0.011).pose((0.8 * long * math.sin(t), -0.8 * long * math.cos(t), 0), (0, 0, degres))
    return doigt(-20, 0.062) + doigt(20, 0.062) + doigt(160, 0.044) + doigt(-160, 0.044)


def construire():
    a = K.Animal("kakapo")
    a.taille = 0.70

    # ----- le corps : un gros œuf lourd, la poitrine en avant, le ventre bas ; moucheté de brun, le ventre plus clair -----
    def coque(v):
        v = K.bosse(v, (0, -0.75, 0.05), 0.24, 0.30)       # la poitrine
        s = v * [0.150, 0.172, 0.185]
        s[:, 0] *= 1 - 0.20 * K.lisse((v[:, 1] - 0.2) / 0.8)
        return s
    corps = A.boule(1.0, 64, 32)
    pts = corps.v * [0.150, 0.172, 0.185]
    t = np.where(mouchetures(pts, 0.050, 0.020, 5)[:, None], BRUN, PALE)
    t[(corps.v[:, 2] < -0.25) & (corps.v[:, 1] < 0.1)] = np.array(CREME)                         # le ventre
    corps.teinte = t
    a.piece("corps", corps.sculpte(coque), None, pos=CORPS)

    # ----- la tête : ronde et grosse, posée droit sur le corps (pas de cou) ; le DISQUE facial crème, de hibou ;
    #       de petits yeux sombres ; la couronne mouchetée -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    cr = A.boule(1.0, 56, 28)
    pc = cr.v * [0.110, 0.100, 0.104]
    tt = np.where(mouchetures(pc, 0.040, 0.016, 9)[:, None], BRUN, PALE)
    cr.teinte = tt
    a.piece("tete", cr, None, mat=H @ A.repere((0, 0, 0), (0, 0, 0), (0.110, 0.100, 0.104)))
    a.rustine("disque", "tete", H.to_translation(), H3 @ Vector((0.0, -1.0, 0.04)), 0.98, CREME, 0.0035, 0)
    a.tete = H @ Vector((0, -0.110, -0.020))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.46, -0.80, 0.22))
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0135)
        a.piece("cils_" + nom, K.paupiere(0.0180, 0.58), tuple(BRUN), mat=A.cadre(p + n * 0.005, n, H3 @ Vector((0, 0, 1))), poil=False)   # remise : le rendu gardé par l'auteur (planche 12)
        # les soies : trois courts poils raides de chaque côté du bec
        for k, (dz, ouvre) in enumerate(((0.022, 0.50), (0.000, 0.20), (-0.020, -0.15))):
            dep = H @ Vector((c * 0.026, -0.100, -0.032 + dz))
            d = H3 @ Vector((c * (0.70 + ouvre * 0.4), -0.55, ouvre * 0.4))
            a.piece("soie_%s%d" % (nom, k), A.tube([tuple(dep), tuple(dep + d.normalized() * 0.060)], 0.0022, 6), CREME, poil=False)

    # ----- le bec : gros, court, haut, crochu ; pâle ; le dessous plus petit -----
    haut = A.tour(A.profil([(0, 0), (0.038, 0.006), (0.036, 0.026), (0.026, 0.052), (0.012, 0.072), (0, 0.082)], 5), 40)

    def crochu(v):
        s = v.copy()
        s[:, 1] *= 1.22
        s[:, 1] -= 0.040 * np.clip(v[:, 2] / 0.082, 0, 1) ** 2.2
        return s
    lac = math.radians(LACET)
    dirige = Vector((math.sin(lac), -math.cos(lac), -0.10)).normalized()
    Bm = A.cadre(H @ Vector((0, -0.100, -0.030)), H3 @ Vector((0, -1.0, -0.18)), Vector((0, 0, 1)))
    a.piece("bec", haut.sculpte(crochu), BEC, mat=Bm, poil=False)
    bas = A.tour(A.profil([(0, 0), (0.028, 0.004), (0.022, 0.020), (0.010, 0.036), (0, 0.044)], 5), 32).etire(1.0, 0.70, 1.0)
    a.piece("bec_bas", bas, BEC, mat=A.cadre(H @ Vector((0, -0.100, -0.058)), H3 @ Vector((0, -1.0, -0.12)), Vector((0, 0, 1))), poil=False)

    # ----- les ailes : deux petits galets pliés sur les flancs ; la queue : un court balai usé qui traîne -----
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 36, 18)
        aile.teinte = np.where(mouchetures(aile.v * [0.036, 0.098, 0.092], 0.040, 0.016, 13 + (c > 0))[:, None], BRUN, PALE)
        a.piece("aile_" + nom, aile.etire(0.036, 0.098, 0.092), None, pos=(c * 0.140, 0.060, 0.215), rot=(-6, 0, c * 8))
    queue = A.boule(1.0, 24, 12)
    queue.teinte = np.where(mouchetures(queue.v * [0.050, 0.030, 0.110], 0.040, 0.016, 21)[:, None], BRUN, PALE)
    a.piece("queue", queue.etire(0.050, 0.030, 0.110), None, pos=(0.0, 0.215, 0.100), rot=(52, 0, 0))

    # ----- les pattes : très courtes, presque cachées par le ventre ; de grands pieds pâles à quatre doigts -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.070, 0.020, 0.100), (c * 0.076, 0.000, 0.050), (c * 0.076, -0.010, 0.014)]
        a.piece("patte_" + nom, A.tube(A.courbe(propres(ch), 5), 0.022, 12), PIED, poil=False)
        a.piece("pied_" + nom, pied().pose((c * 0.076, -0.010, 0.012), (0, 0, c * 6)), PIED, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("kakapo", styles.style_de("kakapo"), sys.modules[__name__]), "Kakapo")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py kakapo). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.094                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.126, 0.205)),
    ('tete', 'corps', (0.004, -0.048, 0.294)),
    ('patte_av_G', 'corps', (0.072, 0.014, 0.094)),
    ('aile_G', 'corps', (0.140, 0.060, 0.305)),
    ('queue', 'corps', (0.000, 0.134, 0.170)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('soie_G0', 'tete'), ('soie_G1', 'tete'), ('soie_G2', 'tete'), ('soie_D0', 'tete'),
    ('soie_D1', 'tete'), ('soie_D2', 'tete'), ('bec_bas', 'tete'), ('disque', 'tete'), ('corps', 'corps'),
    ('queue', 'queue'), ('patte', 'patte_av', True), ('tete', 'tete'), ('aile', 'aile', True), ('oeil', 'tete'),
    ('cils', 'tete'), ('pied', 'patte_av', True), ('bec', 'tete'), ('paupiere_0', 'paupiere_0'),
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
    pas = 26.0
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.028 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.052), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.add('tete', rot=(32, 4, 40))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
