"""Le lièvre en peluche : fauve doré, le ventre blanc, sec et tout en longueur. Dressé sur ses pattes arrière
démesurées, il fait le guet : le poitrail en avant, une main levée, une oreille tournée vers l'arrière, prêt à détaler.

    python lievre.py        fabrique la fiche art/apercus/animaux/lievre.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import garnitures as G
import matieres as M
import peluche as K

FAUVE = M.hexa("#efc98a")                   # le sable chaud de la robe (le poil le fonce et le dore)
SUIE = M.hexa("#1f1c1b")                    # le noir des pointes d'oreilles, du dessus de la queue, de la truffe
BASSIN = Vector((0.0, 0.07, 0.085))         # le bas du corps : une pièce tournée qui monte de là jusqu'au cou
DEVERS = 11.0                               # tout le corps penche vers l'avant
NUQUE = Vector((-0.032, 0.005, 0.618))      # l'arrière du crâne, posé sur le cou
LACET, LEVE, PENCHE = 24.0, 6.0, 5.0        # la tête : tournée vers sa gauche (vers nous), le nez un peu levé, à peine de travers


def plastron(piece, premier, dernier, debut=0.0):
    """Peint en blanc une bande de côtés d'une pièce tournée (le ventre, la gorge), le reste en fauve.
    La limite suit les mailles de la pièce : elle sort nette dans le poil."""
    t = np.tile(np.asarray(FAUVE, float), (len(piece.v), 1))
    for anneau in piece.anneaux:
        for j, k in enumerate(anneau):
            if len(anneau) > 1 and premier <= j <= dernier and piece.v[k, 2] > debut:
                t[k] = K.BLANC
    piece.teinte = t
    return piece


def construire():
    a = K.Animal("lievre")
    a.taille = 1.05

    # ----- le corps : debout, la taille fine, le dos voûté vers l'avant et le poitrail qui pointe -----
    def echine(v):
        s = v.copy()
        s[:, 0] *= 0.86
        s[:, 1] -= 0.045 * (v[:, 2] / 0.47) ** 2                          # le haut du corps part vers l'avant
        s[:, 1] -= 0.016 * K.lisse(-v[:, 1] / 0.05) * np.exp(-((v[:, 2] - 0.33) / 0.05) ** 2)   # le bréchet
        return s
    corps = A.tour(A.profil([(0, 0), (0.080, 0.015), (0.098, 0.07), (0.086, 0.15), (0.070, 0.23), (0.080, 0.31),
                             (0.075, 0.36), (0.054, 0.41), (0.047, 0.455), (0, 0.47)], 6), 48)
    G.sillons(corps, [30, 42], 0.004, 1.1)
    a.piece("corps", plastron(corps.sculpte(echine), 30, 41), None, pos=BASSIN, rot=(DEVERS, 0, 0))   # le côté 36 est le devant
    a.couture("ventre_G", "corps", 42, 0.12, 0.80)                        # les deux coutures suivent la limite du fauve et du blanc
    a.couture("ventre_D", "corps", 30, 0.12, 0.80)

    # ----- les pattes arrière démesurées : une cuisse en jambon, cousue sur sa tranche, et un pied interminable au bout blanc -----
    def jambon(v):                                        # large à la hanche, plus étroite vers le genou
        s = K.emousse(v, 0.82)
        s[:, 1] *= 1 - 0.30 * K.lisse(-v[:, 2])
        return s
    a.piece("cuisse", A.boule(1.0, 40, 20).sculpte(jambon).etire(0.042, 0.090, 0.125), FAUVE,
            pos=(0.096, 0.092, 0.159), rot=(-22, 0, 6), paire=True)
    for cote in (10, 30):
        a.couture("cuisse%d" % cote, "cuisse", cote, 0.15, 0.88, "droit", paire=True)
    pp = A.profil([(0, 0), (0.028, 0.010), (0.034, 0.05), (0.039, 0.13), (0.037, 0.19), (0.024, 0.222), (0, 0.235)], 6)
    for nom, c, recul in (("G", 1, 0.050), ("D", -1, 0.090)):             # le pied gauche en avant : il a déjà pris son élan
        pied = K.bandes(A.tour(pp, 32).etire(1.0, 0.60, 1.0), [(0.168, FAUVE), (9, K.BLANC)])
        a.piece("pied_" + nom, pied, None, pos=(c * 0.098, recul, 0.0245), rot=(90, 0, c * 12))   # couché vers l'avant, la pointe en dehors
        a.ourlet("orteils_" + nom, "pied_" + nom, 0.60)

    # ----- la queue : une touffe noire dessus, blanche dessous -----
    a.piece("queue", K.bandes(A.boule(0.038, 24, 12), [(0.004, K.BLANC), (9, SUIE)]), None, pos=(0, 0.165, 0.165))

    # ----- les bras maigres, repliés devant le poitrail, les mains blanches qui pendent ; la gauche est levée -----
    for nom, c, haut in (("G", 1, 0.060), ("D", -1, 0.0)):
        bras = A.courbe([(c * 0.054, -0.026, 0.440), (c * 0.080, -0.060, 0.385 + haut * 0.3), (c * 0.074, -0.125, 0.352 + haut * 0.8),
                         (c * 0.054, -0.162, 0.378 + haut)], 6)
        a.piece("bras_" + nom, A.tube(bras, lambda t: 0.022 - 0.006 * t, 12), FAUVE)
        a.piece("main_" + nom, A.boule(1.0, 20, 10).etire(0.017, 0.020, 0.023), K.BLANC, pos=(c * 0.050, -0.175, 0.360 + haut), rot=(-20, 0, 0))

    # ----- la tête : un coin au nez busqué, plus grosse que nature ; dans son repère, X la gauche, Y le dessus, Z vers le nez -----
    l, p = math.radians(LACET), math.radians(LEVE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), math.sin(p)))
    T = A.cadre(NUQUE, nez) @ Matrix.Rotation(math.radians(PENCHE), 4, "Z")
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.03, 0.15))

    def crane(v):
        s = v.copy()
        s[:, 1] *= np.where(v[:, 1] < 0, 1 + 0.10 * np.exp(-((v[:, 2] - 0.09) / 0.05) ** 2),      # la mâchoire
                            1 + 0.16 * np.exp(-((v[:, 2] - 0.150) / 0.045) ** 2))                # le nez busqué
        s[:, 0] *= 0.95 - 0.20 * K.lisse((v[:, 2] - 0.12) / 0.08)                                  # de larges joues, un museau étroit
        return s
    tete = A.tour(A.profil([(0, 0), (0.060, 0.013), (0.088, 0.060), (0.090, 0.100), (0.058, 0.150), (0.044, 0.190),
                            (0.040, 0.210), (0, 0.226)], 6), 48)                                 # les joues tombent d'un coup vers le museau : les yeux s'y posent
    a.piece("tete", plastron(tete.sculpte(crane), 31, 40, 0.04), None, mat=T)                     # le côté 36 est le dessous : le menton blanc
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.016, 0.011, 0.011), SUIE, mat=T @ A.repere((0, 0.010, 0.219)), poil=False)
    a.broderie("levre", a.trace("tete", T @ Vector((0, 0, 0.190)), [T3 @ Vector((0, -0.25 - 0.5 * t, 0.9)) for t in (0, 0.5, 1)]), 0.0022)

    # ----- les yeux, gros et tournés vers l'avant, sous deux sourcils droits qui descendent vers le nez : il ne quitte rien du regard -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, vers = a.surface("tete", T @ Vector((0, 0, 0.126)), T3 @ Vector((c * 0.77, 0.64, 0.0)))
        vers = (vers + nez * 0.25).normalized()                                                   # le bouton regarde un peu plus vers l'avant que le tissu
        a.bouton("oeil_" + nom, pos - vers * 0.002, vers, 0.026)
        arc = []
        for t in np.linspace(0, 1, 5):
            tour_ = math.radians(78 - 20 * t)
            arc += a.trace("tete", T @ Vector((0, 0, 0.085 + 0.065 * t)), [T3 @ Vector((c * math.cos(tour_), math.sin(tour_), 0))])
        a.broderie("sourcil_" + nom, A.courbe(arc, 4), 0.0034)
        for k, (dy, dz) in enumerate(((0.016, -0.010), (-0.020, 0.004))):                         # deux moustaches blanches
            a.broderie("moustache_%s%d" % (nom, k), [T @ Vector((c * 0.022, -0.006, 0.186)), T @ Vector((c * 0.066, -0.006 + dy * 0.5, 0.186 + dz * 0.6)),
                                                     T @ Vector((c * 0.104, -0.006 + dy, 0.186 + dz))], 0.0011, K.BLANC)

    # ----- les très longues oreilles à pointe noire, doublées de pêche : la gauche vers le ciel, la droite tournée vers l'arrière -----
    po = A.profil([(0, 0), (0.024, 0.022), (0.037, 0.110), (0.036, 0.220), (0.024, 0.310), (0.009, 0.352), (0, 0.360)], 6)
    for nom, c, vers, face in (("G", 1, (0.22, 0.02, 0.975), (0.45, -0.89, 0.0)), ("D", -1, (-0.30, 0.30, 0.90), (-0.80, 0.50, 0.0))):
        vers = Vector(vers).normalized()
        E = A.cadre(T @ Vector((c * 0.032, 0.060, 0.040)) - vers * 0.022, vers, face)   # Z le long de l'oreille, Y son dedans
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 40).etire(1.0, 0.32, 1.0), [(0.264, FAUVE), (9, SUIE)]), None, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 32).etire(0.60, 0.32, 0.66).pose((0, 0.0075, 0.020)), K.PECHE, mat=E, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py lievre)

from poses import Pose, borne, cloche, onde

# Le corps est une seule pièce tournée, du bassin jusque sous la tête : une pièce souple que trois os se partagent le
# long de son axe (corps au bassin, poitrine entre les bras, cou en haut), pour qu'il puisse se dresser, se courber et
# se mettre à quatre pattes. La tête est tournée vers nous, les oreilles, les bras et les pieds ne sont pas posés en
# miroir : leurs os sont nommés à la main, en minuscules, et une fonction donne à chaque pièce l'os de son côté.
# Seules les cuisses sont une vraie paire (cuisse_G, recopiée en cuisse_D). Les pieds pendent à la racine : posés à plat,
# ils ne bougent pas quand le corps se penche au-dessus d'eux.
_AXE = np.array([0.0, -math.sin(math.radians(DEVERS)), math.cos(math.radians(DEVERS))])     # l'axe du corps, du bassin vers le cou
_HAUT = 0.47                                                                                 # sa longueur
_JALONS = (("corps", 0.0), ("poitrine", 0.50), ("cou", 0.84))


def _sur_axe(f):
    """Le point de l'axe du corps à la fraction f de sa hauteur : le pivot d'un os."""
    return tuple(round(float(x), 3) for x in np.array(BASSIN) + _AXE * f * _HAUT)


def _relais(f, jalons, large):
    """Des os qui se passent la main le long d'un axe : chacun porte le tronçon qui suit son pivot, et cède au suivant
    en douceur sur ± large autour du pivot de celui-ci."""
    def marche(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3 - 2 * x)
    montees = [np.ones_like(f)] + [marche((f - f0 + large) / (2 * large)) for _o, f0 in jalons[1:]] + [np.zeros_like(f)]
    return {o: montees[i] - montees[i + 1] for i, (o, _f0) in enumerate(jalons)}


def _echine(points, cote):
    return _relais(np.clip((points - np.array(BASSIN)) @ _AXE / _HAUT, 0.0, 1.0), _JALONS, 0.10)


def _cote(os_):
    """Une pièce d'un côté (oreille_G, pied_D...) portée tout entière par l'os de son côté : oreille_g, pied_d..."""
    return lambda points, cote: {os_ + "_" + cote[1:].lower(): np.ones(len(points))}


OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", _sur_axe(0.08)),                  # le bassin, entre les cuisses : il se dresse et se penche autour
    ("poitrine", "corps", _sur_axe(0.50)),
    ("cou", "poitrine", _sur_axe(0.84)),
    ("tete", "cou", (-0.016, -0.012, 0.590)),             # la nuque, posée sur le haut du corps
    ("oreille_g", "tete", (0.006, -0.015, 0.684)),        # la base de chaque oreille
    ("oreille_d", "tete", (-0.052, -0.041, 0.679)),
    ("bras_g", "poitrine", (0.054, -0.026, 0.440)),       # les épaules
    ("bras_d", "poitrine", (-0.054, -0.026, 0.440)),
    ("cuisse_G", "corps", (0.096, 0.100, 0.215)),         # la hanche, au haut du jambon
    ("pied_g", "racine", (0.098, 0.060, 0.030)),          # le talon (le gauche est plus en avant)
    ("pied_d", "racine", (-0.098, 0.100, 0.030)),
    ("queue", "corps", (0.0, 0.140, 0.160)),
]
PORTEURS = [("corps", _echine, "corps"), ("ventre", _echine, "corps"),
            ("tete", "tete"), ("truffe", "tete"), ("levre", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("moustache", "tete"),
            ("oreille", _cote("oreille"), "oreille_g"), ("pavillon", _cote("oreille"), "oreille_g"),
            ("bras", _cote("bras"), "poitrine"), ("main", _cote("bras"), "poitrine"),
            ("cuisse", "cuisse", True),
            ("pied", _cote("pied"), "pied_g"), ("orteils", _cote("pied"), "pied_g"),
            ("queue", "queue"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _a_quatre(p, k):
    """À quatre pattes, à la fraction k (0 : dressé, 1 : à quatre pattes) : le corps bascule en avant sur le bassin,
    le dos s'arrondit, les bras descendent jusqu'au sol, la tête se relève pour regarder devant."""
    p.add("corps", rot=(70 * k, 0, 0))
    p.add("poitrine", rot=(-10 * k, 0, 0))
    p.add("cou", rot=(-20 * k, 0, 0))
    p.add("tete", rot=(-35 * k, 0, 0))
    p.add("bras_g", rot=(-15 * k, 0, 0))                     # la main gauche, levée au repos, a moins de chemin à faire
    p.add("bras_d", rot=(-30 * k, 0, 0))
    p.paire("cuisse", rot=(-36 * k, 0, 0))                   # la cuisse reste couchée le long du flanc


def repos(t):
    """Dressé, il fait le guet : il respire, le nez frémit, il tourne la tête par à-coups (devant, vers nous, de l'autre
    côté), l'oreille tournée vers l'arrière pivote pour écouter ; puis il se hisse sur ses pattes arrière pour voir plus
    loin, la main levée qui tressaille, et redescend ; il cligne."""
    p = Pose()
    r = onde(t, 2)
    hisse = _plateau(t, 0.55, 0.08, 0.08)
    p.add("corps", rot=(-6 * hisse, 0, 0), pos=(0, 0, 0.030 * hisse), ech=(1 + 0.012 * r, 1 + 0.012 * r, 1 + 0.008 * r))
    p.paire("cuisse", rot=(8 * hisse, 0, 0), pos=(0, 0, -0.025 * hisse))        # la cuisse se déplie, le talon reste au sol
    p.add("poitrine", rot=(-3 * hisse, 0, 0))
    regard = 26 * _plateau(t, 0.20, 0.05, 0.02) - 30 * _plateau(t, 0.36, 0.05, 0.02)
    p.add("tete", rot=(2.5 * onde(t, 20) * cloche(t, 0.08, 0.05) + 6 * hisse, 0, regard))
    p.add("oreille_d", rot=(0, 0, 40 * cloche(t, 0.28, 0.06) - 25 * cloche(t, 0.78, 0.05)))
    p.add("oreille_g", rot=(0, 0, -20 * cloche(t, 0.70, 0.04)))
    p.add("bras_g", rot=(10 * cloche(t, 0.60, 0.03), 0, 0))
    p.add("queue", rot=(-12 * cloche(t, 0.88, 0.04), 0, 0))
    p.ouvert = borne(1 - cloche(t, 0.12, 0.02) - cloche(t, 0.46, 0.02) - cloche(t, 0.90, 0.02))
    return p


def avance(t):
    """Il détale, à quatre pattes, par bonds : il pousse des deux longs pieds et passe en l'air, le nez d'abord levé puis
    plongeant, les mains tendues devant ; il se reçoit sur les mains, se tasse, et ses pieds posés glissent vers l'arrière
    jusqu'au bond suivant. Les oreilles se couchent dans le vent, la queue blanche se relève."""
    p = Pose()
    _a_quatre(p, 1.0)
    vol = max(0.0, onde(t, 1))                                 # en l'air de 0 à 0,5, au sol de 0,5 à 1
    sol = max(0.0, -onde(t, 1))
    p.add("corps", rot=(-12 * onde(t, 2) * vol, 0, 0), pos=(0, 0, 0.070 * vol), ech=(1 + 0.03 * sol, 1, 1 - 0.06 * sol))
    p.add("poitrine", rot=(-6 * vol, 0, 0))
    p.add("tete", rot=(8 * vol, 0, 0))
    for nom in ("pied_g", "pied_d"):
        p.add(nom, rot=(12 * vol, 0, 0), pos=(0, 0.030 * math.cos(math.tau * t), 0.060 * vol))
    p.paire("cuisse", rot=(-10 * vol, 0, 0), pos=(0, 0, -0.010 * vol))
    p.add("bras_g", rot=(-22 * vol, 0, 0))
    p.add("bras_d", rot=(-20 * vol, 0, 0))
    p.add("oreille_g", rot=(-40, 0, 0))
    p.add("oreille_d", rot=(-25, 0, 0))
    p.add("queue", rot=(-20 - 10 * vol, 0, 0))
    return p


def mange(t):
    """Il se laisse retomber sur ses mains, le nez dans l'herbe, broute à petits coups rapides, puis se redresse sur son
    séant pour mâcher en surveillant, les oreilles de nouveau aux aguets."""
    p = Pose()
    bas = _plateau(t, 0.40, 0.25, 0.14)
    broute = abs(onde(t, 12)) * _plateau(t, 0.40, 0.22, 0.04)
    _a_quatre(p, bas)
    p.add("poitrine", rot=(10 * bas, 0, 0))
    p.add("bras_g", rot=(-8 * bas, 0, 0))                    # la poitrine plonge : les mains se relèvent pour rester sur l'herbe
    p.add("bras_d", rot=(-20 * bas, 0, 0))
    p.add("cou", rot=(30 * bas, 0, 0))
    p.add("tete", rot=(30 * bas + 6 * broute, 0, 0))
    p.add("oreille_g", rot=(-15 * bas, 0, 0))
    p.add("oreille_d", rot=(-10 * bas, 0, 0))
    mache = cloche(t, 0.86, 0.10)
    p.add("tete", rot=(3 * mache * onde(t, 14), 0, 18 * cloche(t, 0.90, 0.05)))
    p.ouvert = borne(1 - cloche(t, 0.80, 0.02))
    return p


def joie(t):
    """Sa fête : il se ramasse, puis bondit tout droit en l'air en se tordant (un demi-tour de reins), les oreilles qui
    fouettent, les pieds qui battent ; il retombe sur ses longs pieds et se redresse, aux aguets."""
    p = repos(0.0)
    tasse = cloche(t, 0.10, 0.10, False)
    saut = math.sin(math.pi * borne((t - 0.16) / 0.46))          # en l'air de 0,16 à 0,62
    p.add("corps", rot=(8 * tasse - 10 * saut, 18 * saut, 35 * saut), pos=(0, 0, -0.015 * tasse + 0.20 * saut))
    p.paire("cuisse", rot=(-16 * tasse + 22 * saut, 0, 0))
    for nom in ("pied_g", "pied_d"):
        p.add(nom, rot=(30 * saut, 0, 0), pos=(0, 0.02 * saut, 0.20 * saut + 0.03 * saut))
    p.add("poitrine", rot=(-8 * saut, -10 * saut, 0))
    p.add("tete", rot=(-10 * saut, 0, -20 * saut))
    p.add("oreille_g", rot=(0, 30 * saut * onde(t, 4), 0))
    p.add("oreille_d", rot=(0, -30 * saut * onde(t, 4, 0.25), 0))
    p.add("bras_g", rot=(-30 * saut, 0, 0))
    p.add("bras_d", rot=(-30 * saut, 0, 0))
    p.add("queue", rot=(-25 * saut, 0, 0))
    return p


def dort(t):
    """Tapi au gîte : à demi couché, ramassé en boule, la tête rentrée sur les mains, les deux oreilles couchées à plat
    le long du dos, les yeux fermés ; il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    _a_quatre(p, 0.9)
    p.add("corps", pos=(0, 0, -0.012), ech=(1 + 0.014 * r, 1 + 0.014 * r, 1))
    p.add("cou", rot=(10, 0, 0))
    p.add("tete", rot=(18, 0, 0))
    p.add("oreille_g", rot=(-70, 0, -10))
    p.add("oreille_d", rot=(-60, 0, 30))
    p.add("bras_g", rot=(4, 0, 0))
    p.add("bras_d", rot=(2, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Lièvre")
