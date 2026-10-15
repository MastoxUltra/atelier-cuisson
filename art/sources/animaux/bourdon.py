"""Le bourdon en peluche, deuxième dessin : le pataud du jardin, qui vient d'atterrir de travers. Une grosse poire de
peluche à long poil, assise sur son derrière : la fesse blanche (rapiécée de corail, à force de s'y asseoir), une bande
de charbon, une large bande moutarde, la taille et le dos du thorax en charbon, un col moutarde. Tout le corps penche
sur une hanche, la tête basse et ronde rentrée sous le col, penchée de l'autre côté, deux petits yeux vifs très
écartés dans des lunettes crème : l'air de se demander comment il a fait pour voler. Sur le dos, deux ailes de
feutrine fumée ridiculement petites, dont une froissée ; des antennes coudées ; six pattes courtes et trapues, les
pattes de derrière élargies en corbeille ; une patte du milieu levée, il cherche encore l'équilibre.

    python bourdon.py        fabrique la fiche art/apercus/animaux/bourdon.png
    (le premier dessin, jamais gardé : bourdon_ancien.py)
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

MOUTARDE = M.hexa("#f2bc45")                  # les bandes claires (le long poil les dore)
CHARBON = M.hexa("#2e2a2a")                   # les bandes sombres, la tête, les pattes
BLANC = M.hexa("#faf6ee")                     # la fesse
CREME = M.hexa("#f3e3bf")                     # le fil du dos
FUME = M.hexa("#bdb6cc")                      # la feutrine des ailes
CORAIL = M.hexa("#f0705a")                    # l'accent : la pièce sur la fesse
PENCHE = A.repere((0.0, 0.0, 0.0), (0, 13, 0))     # il penche sur sa hanche droite (le haut part vers sa gauche)
# l'axe du corps, de la fesse (s = 0) au col : assis sur le derrière, le thorax relevé, la fesse un peu rentrée dessous
AXE = K.Fil([(0, 0.122, 0.086), (0, 0.040, 0.112), (0, -0.040, 0.138), (0, -0.098, 0.166)], flanc=(1, 0, 0))
LONG = AXE.long
BANDES = [(0.20, BLANC), (0.34, CHARBON), (0.54, MOUTARDE), (0.86, CHARBON), (9, MOUTARDE)]


def rayon(t):
    """Le rayon du corps à la fraction t de sa longueur : un gros abdomen rond, une taille à peine marquée, un thorax
    plus petit et bien plein."""
    abdomen = 0.112 * math.sqrt(max(0.0, 1 - ((t - 0.34) / 0.36) ** 2))
    thorax = 0.090 * math.sqrt(max(0.0, 1 - ((t - 0.80) / 0.215) ** 2))
    return max(abdomen, thorax, 0.0) * 1.0


def ici(p):
    """Un point du corps avant qu'il penche, rendu dans le jardin."""
    return PENCHE @ Vector(p)


def construire():
    a = K.Animal("bourdon")
    a.taille = 0.36
    a.poil_long = 0.0080                      # bien plus poilu que les autres

    # ----- le corps : une seule poire tournée, peinte par bandes, couchée le long de l'axe, puis penchée -----
    ts = 0.5 - 0.5 * np.cos(np.linspace(0, math.pi, 44))
    profil = [(rayon(t), t * LONG) for t in ts]
    profil[0], profil[-1] = (0.0, 0.0), (0.0, LONG)
    corps = K.bandes(A.tour(A.profil(profil, 2), 56).etire(1.06, 0.96, 1.0), [(f * LONG, c) for f, c in BANDES])
    G.sillons(corps, [14], 0.005, 1.2)
    a.piece("corps", corps.sculpte(AXE.couche), None, mat=PENCHE)
    a.couture("dos", "corps", 14, 0.22, 0.78, "droit", fil=CREME, large=0.012, haut=0.0070, pas=0.018)
    centre, sens = AXE.vise(0.13 * LONG, -0.30, 0.55, -0.10)
    a.rustine("piece", "corps", ici(centre), PENCHE.to_3x3() @ sens, 0.36, CORAIL, 0.003, 14, fil=CHARBON)

    # ----- la tête : une boule ronde rentrée sous le col, penchée de l'autre côté ; deux lunettes crème -----
    col, avant, nuque = AXE.cadre(LONG)
    tete = ici(Vector(col) + Vector(avant) * 0.010 - Vector(nuque) * 0.060)
    port = A.repere(tete, (16, -16, 14))      # la tête basse, penchée sur sa gauche, tournée vers nous
    a.tete = port @ Vector((0, -0.050, 0.0))

    def vers(x, y, z):
        return port.to_3x3() @ Vector((x, y, z))

    def caboche(v):
        v = K.bosse(v, (0, -0.6, -0.8), 0.10, 0.30)               # un museau qui pend
        return K.emousse(v, 0.92) * [0.060, 0.052, 0.054]
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(caboche), CHARBON, mat=port)
    # le museau : une pièce moutarde cousue au feston sur le bas du visage
    a.rustine("museau", "tete", tete, vers(0, -0.86, -0.50), lambda th: 0.40 + 0.10 * math.cos(2 * th), MOUTARDE, 0.003, 16, fil=CHARBON)
    a.couture("crane", "tete", 14, 0.55, 0.97, "droit", fil=MOUTARDE, large=0.008, haut=0.0060, pas=0.013)
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", tete, vers(0.56 * cote, -0.76, 0.30))
        a.oeil("oeil_" + nom, p + n * 0.0045, n, 0.0105)
        # une paupière moutarde, à peine baissée : le regard un peu ahuri
        a.piece("lourde_" + nom, K.paupiere(0.0105, 0.38), MOUTARDE, mat=A.cadre(p + n * 0.0055, n, vers(0, 0.10, 1)), poil=False)
        # les antennes coudées : elles montent, puis cassent vers l'avant
        p, n = a.surface("tete", tete, vers(0.24 * cote, -0.50, 0.84))
        fil = A.conges([p - n * 0.004, p + vers(0.010 * cote, 0.004, 0.034), p + vers(0.024 * cote, -0.030, 0.050),
                        p + vers(0.034 * cote, -0.050, 0.040)], 0.008, 5)
        a.piece("antenne_" + nom, A.tube(fil, lambda u: 0.0052 - 0.0012 * u, 12), CHARBON, poil=False)
    moue = a.trace("tete", tete, [vers(x, -0.95, z) for x, z in ((0.15, -0.50), (0.06, -0.45), (-0.04, -0.50), (-0.12, -0.46))], 0.0080)
    a.broderie("moue", A.courbe(moue, 4), 0.0026, CHARBON)

    # ----- les ailes : deux toutes petites gouttes fumées plantées sur le thorax ; la droite froissée, retombée -----
    def goutte(v):
        s = v.copy()
        s[:, 0] *= 0.55 + 0.45 * K.lisse((v[:, 1] + 1.0) / 1.6)
        s[:, 2] = np.sign(v[:, 2]) * np.abs(v[:, 2]) ** 0.6
        return s
    for nom, cote, elan in (("G", 1, (0.45, 0.62, 0.64)), ("D", -1, (-0.62, 0.58, 0.30))):
        s = 0.76 * LONG
        c, av, nu = AXE.cadre(s)
        pied = ici(Vector(c) + Vector(nu) * (rayon(0.76) + 0.004) + Vector((0.026 * cote, 0, 0)))
        aile = A.boule(1.0, 32, 16).sculpte(goutte).etire(0.020, 0.030, 0.004)
        if cote < 0:
            aile = aile.sculpte(lambda v: v + np.outer(np.maximum(v[:, 1], 0) ** 2 * 14, [0, 0, -1]))
        e = Vector(elan).normalized()
        a.piece("aile_" + nom, aile, FUME, mat=A.cadre(pied + e * 0.026, (-0.25 * cote, -0.6, 0.75), e), poil=False)

    # ----- les pattes : courtes, trapues, charbon ; celles de derrière élargies en corbeille ; la patte du milieu
    #       gauche levée. Une pièce par patte (pour le jeu : chacune bouge à son tour) -----
    for nom, cote in (("G", 1), ("D", -1)):
        for rang, (f, sortie, pied, gros) in zip(("avant", "milieu", "arriere"),
                                                 ((0.86, 0.80, (0.078, -0.128, 0.010), 0.0135),
                                                  (0.66, 0.92, (0.120, -0.040, 0.010) if cote < 0 else (0.132, -0.066, 0.056), 0.0135),
                                                  (0.46, 0.96, (0.126, 0.050, 0.010), 0.0135))):
            c, av, nu = AXE.cadre(f * LONG)
            r = rayon(f)
            hanche = ici(Vector(c) + Vector((cote * 0.62 * r, 0, 0)) - Vector(nu) * 0.62 * r)
            bout = Vector((cote * pied[0], pied[1], pied[2]))
            genou = (hanche + bout) * 0.5 + Vector((cote * 0.030, 0, 0.026))
            corbeille = f < 0.5
            une = A.tube(A.conges([hanche, genou, bout], 0.012, 5),
                         (lambda u, g=gros: g * (1 + 0.55 * math.sin(math.pi * min(1, max(0, (u - 0.40) / 0.55))))) if corbeille
                         else (lambda u, g=gros: g * (1 - 0.25 * u)), 12)
            a.piece("patte_" + rang + "_" + nom, une, CHARBON, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py bourdon). Les mesures sont celles du modèle, avant a.taille.
# Il penche sur une hanche, la tête penchée de l'autre côté, une patte levée : rien n'est en miroir, chaque aile, chaque
# antenne et chaque patte a son os à elle, à sa vraie place. La poire du corps est une pièce souple : l'abdomen suit
# « corps », le thorax « thorax ». Les pattes pendent à la racine : posées, elles restent au sol quand le corps
# tangue ; en vol (et pour se coucher), « suivre » les emmène avec le corps.

from poses import Pose, borne, cloche, onde

_AXE = np.array([tuple(ici(q)) for q in AXE.p])          # l'axe du corps, penché comme lui
_PIVOT = np.array(tuple(ici(Vector(AXE.cadre(0.30 * LONG)[0]))))      # le cœur de l'abdomen
_HANCHES = {"av_g": (0.0754, -0.0926, 0.0883), "mi_g": (0.0621, -0.0395, 0.0809), "ar_g": (0.0764, -0.0002, 0.0398),
            "av_d": (-0.0290, -0.0926, 0.1124), "mi_d": (-0.0204, -0.0395, 0.0999), "ar_d": (-0.0512, -0.0002, 0.0692)}

OS = ([("racine", None, (0, 0, 0)),
       ("corps", "racine", tuple(round(float(x), 4) for x in _PIVOT)),   # l'abdomen, sur lequel il est assis
       ("thorax", "corps", tuple(round(x, 4) for x in ici(Vector(AXE.cadre(0.60 * LONG)[0])))),     # la taille
       ("tete", "thorax", (0.032, -0.115, 0.140)),            # la nuque, sous le col
       ("antenne_g", "tete", (0.0374, -0.1682, 0.1500)),      # la racine de chaque antenne
       ("antenne_d", "tete", (0.0144, -0.1739, 0.1432)),
       ("aile_g", "thorax", (0.0762, -0.0113, 0.2145)),       # le pied de chaque aile, sur le dos du thorax
       ("aile_d", "thorax", (0.0255, -0.0113, 0.2262))]
      + [(n, "racine", h) for n, h in _HANCHES.items()])


def _abscisse(points, chemin):
    """Pour chaque point : sa place le long d'un chemin (en mètres), au pied de la perpendiculaire sur le tronçon le plus proche."""
    c = np.asarray(chemin, float)
    a, ab = c[:-1], np.diff(c, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    ap = points[:, None, :] - a[None, :, :]
    u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
    j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
    fait = np.concatenate([[0.0], np.cumsum(np.sqrt(l2))])
    return fait[j] + u[np.arange(len(points)), j] * np.sqrt(l2[j])


def souple(points, cote):
    """La poire : l'abdomen sur « corps », le thorax sur « thorax », fondus à la taille sur trois centimètres."""
    w = K.lisse((_abscisse(points, _AXE) - 0.58 * LONG + 0.015) / 0.030)
    return {"corps": 1 - w, "thorax": w}


def _cote(os_):
    """Une pièce d'un côté (aile_G, antenne_D) suit l'os de son côté (aile_g, antenne_d)."""
    return lambda points, cote: {os_ + cote.lower(): np.ones(len(points))}


def _patte(rang):
    return lambda points, cote: {rang + cote.lower(): np.ones(len(points))}


PORTEURS = [("corps", souple, "corps"), ("dos", souple, "corps"), ("piece", souple, "corps"),
            ("tete", "tete"), ("museau", "tete"), ("crane", "tete"), ("oeil", "tete"), ("lourde", "tete"), ("moue", "tete"),
            ("antenne", _cote("antenne")), ("aile", _cote("aile")),
            ("patte_avant", _patte("av")), ("patte_milieu", _patte("mi")), ("patte_arriere", _patte("ar")),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _rot(r):
    """La matrice d'une rotation de Pose (degrés ; X, puis Y, puis Z, autour des axes du monde)."""
    x, y, z = (math.radians(a) for a in r)
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    return (np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
            @ np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]))


def suivre(p, rot, pos, pend=0.0):
    """Le corps tourne de « rot » et se déplace de « pos » (autour de son pivot) : les six pattes, pendues à la racine,
    suivent le même mouvement. pend > 0 : en l'air, elles se replient sous lui."""
    p.add("corps", rot=rot, pos=pos)
    m = _rot(rot)
    for n, h in _HANCHES.items():
        h = np.array(h)
        p.add(n, rot=rot, pos=tuple(_PIVOT + np.asarray(pos, float) + m @ (h - _PIVOT) - h))
        if pend:
            c = 1 if n.endswith("g") else -1
            p.add(n, rot=(-25 * pend, -c * 20 * pend, 0))


def repos(t):
    """Il reprend ses esprits : il respire à gros souffle dans sa fourrure, tangue sur sa fesse en cherchant
    l'équilibre, moulinant de sa patte levée ; il essaie ses ailes (un petit bourdonnement, rien ne se passe), tourne
    la tête d'un air perplexe, les antennes qui tâtonnent ; il cligne."""
    p = Pose()
    r = onde(t, 2)
    p.add("corps", ech=(1 + 0.03 * r, 1 + 0.02 * r, 1 + 0.02 * r))
    p.add("thorax", rot=(0, 4 * onde(t, 1), 2 * onde(t, 1, 0.25)))
    p.add("mi_g", rot=(18 * onde(t, 3), 0, 8 * onde(t, 3, 0.25)))
    essai = cloche(t, 0.40, 0.06)
    p.add("aile_g", rot=(0, -24 * essai * onde(t, 40), 0))
    p.add("aile_d", rot=(0, 24 * essai * onde(t, 40), 0))
    p.add("tete", rot=(0, -10 * cloche(t, 0.65, 0.12), 12 * cloche(t, 0.65, 0.12)))
    p.add("antenne_g", rot=(10 * onde(t, 2), 0, 6 * onde(t, 3)))
    p.add("antenne_d", rot=(-8 * onde(t, 2, 0.3), 0, 6 * onde(t, 3, 0.4)))
    p.ouvert = borne(1 - cloche(t, 0.18, 0.02) - cloche(t, 0.80, 0.02))
    return p


def avance(t):
    """Il vole, lourdement : le corps monte haut, pend sous ses ailes minuscules qui vrombissent à toute vitesse,
    tangue et roule comme un bateau ; les pattes pendent, les corbeilles ballantes, la tête toujours un peu de travers."""
    p = Pose()
    haut = 0.18 + 0.025 * onde(t, 2) + 0.010 * onde(t, 1, 0.3)
    suivre(p, (-14 + 3 * onde(t, 2, 0.2), -10 + 6 * onde(t, 1), 3 * onde(t, 1, 0.25)), (0, 0, haut), 1.0)
    p.add("aile_g", rot=(0, -30 - 36 * onde(t, 12), 0))
    p.add("aile_d", rot=(0, 30 + 36 * onde(t, 12), 0))
    p.add("tete", rot=(-6, 0, 0))
    p.add("antenne_g", rot=(-10, 0, 0))
    p.add("antenne_d", rot=(-10, 0, 0))
    return p


def mange(t):
    """Il butine : il plonge la tête la première dans la fleur à ses pieds, se tortille du derrière pour aller au fond
    et fait vibrer ses ailes pour secouer le pollen ; puis il ressort, la tête pleine de poussière d'or, et éternue."""
    p = Pose()
    bas = cloche(t, 0.42, 0.32)
    p.add("thorax", rot=(16 * bas, 0, 0))
    p.add("tete", rot=(22 * bas, 0, 0))
    p.add("corps", rot=(0, 0, 8 * bas * onde(t, 6)))
    vibre = cloche(t, 0.45, 0.16)
    p.add("aile_g", rot=(0, -20 * vibre * onde(t, 40), 0))
    p.add("aile_d", rot=(0, 20 * vibre * onde(t, 40), 0))
    p.add("antenne_g", rot=(14 * bas, 0, 0))
    p.add("antenne_d", rot=(14 * bas, 0, 0))
    atchoum = cloche(t, 0.86, 0.04)
    p.add("tete", rot=(-14 * cloche(t, 0.82, 0.03) + 18 * atchoum, 0, 0))
    p.ouvert = borne(1 - 0.6 * bas - cloche(t, 0.84, 0.03))
    return p


def joie(t):
    """Il décolle en vrombissant, fait un looping en l'air (il en est le premier surpris) et retombe assis sur son
    derrière, de travers comme toujours."""
    p = Pose()
    air = math.sin(math.pi * borne(t / 0.80))
    looping = borne((t - 0.18) / 0.48)
    looping = looping * looping * (3 - 2 * looping)
    suivre(p, (-360 * looping, 0, 0), (0, 0, 0.26 * air), air)
    vrombit = 1 if t < 0.80 else 0
    p.add("aile_g", rot=(0, (-30 - 36 * onde(t, 14)) * air * vrombit, 0))
    p.add("aile_d", rot=(0, (30 + 36 * onde(t, 14)) * air * vrombit, 0))
    p.add("tete", rot=(-10 * air, 0, 0))
    p.add("antenne_g", rot=(-16 * air, 0, 0))
    p.add("antenne_d", rot=(-16 * air, 0, 0))
    p.ouvert = 1 - 0.8 * cloche(t, 0.42, 0.10, False)
    return p


def dort(t):
    """Il s'est endormi où il s'est posé : basculé sur le flanc, tout rond, les pattes en l'air repliées, la tête
    rentrée, les ailes à plat ; les yeux fermés, il ronfle à gros souffle dans sa fourrure."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    suivre(p, (0, 48, 0), (0.0, 0, 0.012))
    p.add("corps", ech=(1 + 0.04 * r, 1 + 0.03 * r, 1 + 0.03 * r))
    for n in _HANCHES:                                         # celles du dessous se replient contre le ventre
        p.add(n, rot=(-20, -75 if n == "ar_g" else -50, 0) if n.endswith("g") else (-20, 0, 0))
    p.add("tete", rot=(12, 10, 0))
    p.add("antenne_g", rot=(24, 0, 0))
    p.add("antenne_d", rot=(24, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Bourdon")
