"""La rainette en peluche : bleu ciel, le ventre crème, assise le torse bombé, les cuisses repliées.
Ses doigts à ventouses sont en feutrine corail, et elle tire un bout de langue.

    python grenouille.py        fabrique la fiche art/apercus/animaux/grenouille.png
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
import peluche as K

CORPS = Vector((0.0, 0.0, 0.113))
LARGE, LONG, HAUT = 0.105, 0.125, 0.085     # les demi-mesures du corps avant qu'il se redresse
PENTE = 0.60                                # l'assise : le devant du corps monte, la croupe reste au sol


def doigts(depart, bouts, fil, ventouse):
    """Une main ou un pied : des doigts de feutrine qui partent du même point, une ventouse ronde au bout de chacun."""
    m = None
    for bout in bouts:
        doigt = A.tube([depart, bout], fil, 10) + A.boule(1.0, 16, 8).etire(ventouse, ventouse, ventouse * 0.55).pose(bout)
        m = doigt if m is None else m + doigt
    return m


def construire():
    a = K.Animal("grenouille")
    a.taille = 0.38
    a.tete = Vector((0.0, -0.10, 0.19))

    def vise(centre, direction):
        """Le point du corps visé depuis « centre », et la normale du tissu à cet endroit."""
        d = Vector(direction).normalized()
        e1 = d.orthogonal().normalized()
        p, p1, p2 = a.trace("corps", centre, [d, d + e1 * 0.04, d + d.cross(e1) * 0.04], 0.0)
        n = (p1 - p).cross(p2 - p).normalized()
        return p, (n if n.dot(d) > 0 else -n)

    # ----- le corps : un galet large devant, étroit à la croupe, redressé comme une grenouille assise -----
    def coque(v):
        u = v
        for cote in (1, -1):                                   # les coins de la bouche : une tête large
            u = K.bosse(u, (0.80 * cote, -0.60, 0.05), 0.10, 0.22)
        s = u * [LARGE, LONG, HAUT]
        s[:, 0] *= 1 - 0.18 * u[:, 1]
        s[:, 2] -= PENTE * s[:, 1]
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    G.sillons(corps, [14], 0.005, 1.1)                         # la couture du dos creuse un peu le tissu
    a.piece("corps", corps, K.CIEL, pos=CORPS)
    a.couture("dos", "corps", 14, 0.40, 0.97)
    a.rustine("ventre", "corps", CORPS, (0, -0.75, -0.40), lambda th: 0.69 - 0.10 * math.cos(2 * th), K.CREME, feston=40)
    a.rustine("tache", "corps", CORPS, (0.50, 0.45, 0.74), lambda th: 0.31 + 0.04 * math.cos(3 * th), K.TURQUOISE, feston=18)

    # ----- les yeux : deux globes sur le dessus de la tête, un gros bouton sur chacun -----
    sommet = a.trace("corps", (0.060, -0.078, 0.16), [(0, 0, 1)], 0.0)[0]
    globe = sommet + Vector((0.004, -0.004, 0.012))
    a.piece("globe", A.boule(1.0, 40, 20).etire(0.044), K.CIEL, pos=globe, paire=True)
    regard = Vector((0.42, -0.78, 0.46)).normalized()
    a.bouton("oeil", globe + regard * 0.040, regard, 0.026, paire=True)

    # ----- la bouche : un grand trait brodé d'une joue à l'autre, et un bout de langue qui dépasse -----
    def levre(s):
        return (LARGE * math.sin(s), -LONG * math.cos(s), -0.016 + 0.045 * abs(s / 1.25) ** 2.5 + PENTE * LONG * math.cos(s))
    a.broderie("bouche", a.trace("corps", CORPS, [levre(s) for s in np.linspace(-1.25, 1.25, 25)], 0.0035), 0.0028)
    coin, dehors = vise(CORPS, levre(0.50))
    langue = A.boule(1.0, 20, 10).etire(0.0095, 0.017, 0.0035).pose((0, -0.015, 0)).pose((0, 0, 0.003), (-35, 0, 0))   # elle pend et se décolle du menton
    a.piece("langue", langue, K.CORAIL, mat=A.cadre(coin, dehors), poil=False)

    # ----- les cuisses repliées : deux galets contre les flancs, le genou relevé, cousus sur leur tranche -----
    cuisse = A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.044, 0.100, 0.062)
    a.piece("cuisse", cuisse, K.CIEL, pos=(0.110, 0.035, 0.072), rot=(-22, 0, 14), paire=True)
    for cote in (10, 30):
        a.couture("cuisse%d" % cote, "cuisse", cote, 0.12, 0.88, "droit", paire=True)
    pied = doigts((0.112, 0.02, 0.011), [(0.130, -0.100, 0.010), (0.156, -0.085, 0.010), (0.172, -0.058, 0.010)], 0.009, 0.015)
    a.piece("pied", pied, K.CORAIL, poil=False, paire=True)

    # ----- les bras : deux boudins qui descendent du poitrail, les mains à plat dans l'herbe -----
    bras = A.tube(A.courbe([(0.062, -0.085, 0.145), (0.078, -0.100, 0.075), (0.075, -0.125, 0.018)], 6), lambda t: 0.026 - 0.008 * t, 12)
    a.piece("bras", bras, K.CIEL, paire=True)
    main = doigts((0.075, -0.125, 0.010), [(0.050, -0.168, 0.009), (0.080, -0.176, 0.009), (0.108, -0.160, 0.009)], 0.008, 0.013)
    a.piece("main", main, K.CORAIL, poil=False, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py grenouille)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.08, 0.0)),               # sous la croupe : elle est assise dessus et bascule autour
    ("gorge", "corps", (0, -0.067, 0.157)),            # derrière le sac de la gorge : il gonfle depuis là
    ("langue", "corps", (0.052, -0.112, 0.167)),       # le coin de la bouche
    ("globe_G", "corps", (0.064, -0.082, 0.224)),      # le milieu du globe : l'œil roule, ou rentre dans la tête
    ("bras_G", "corps", (0.062, -0.085, 0.140)),       # l'épaule
    ("main_G", "bras_G", (0.075, -0.125, 0.016)),      # le poignet
    ("cuisse_G", "corps", (0.085, 0.085, 0.055)),      # la hanche, à l'arrière de la cuisse repliée
    ("pied_G", "cuisse_G", (0.112, 0.020, 0.012)),     # le talon
]
SAC = (0.0, -0.105, 0.132)                             # le milieu de la gorge, sous la bouche


def peau(points, cote):
    """Le corps est d'une seule pièce : sous la bouche, le tissu suit peu à peu l'os « gorge », pour qu'elle gonfle."""
    g = np.clip(1.0 - np.linalg.norm((points - SAC) / (0.078, 0.058, 0.048), axis=1), 0.0, 1.0)
    sac = g * g * (3 - 2 * g)
    return {"corps": 1.0 - sac, "gorge": sac}


PORTEURS = [("corps", peau, "corps"), ("dos", peau, "corps"), ("ventre", peau, "corps"), ("tache", peau, "corps"),
            ("bouche", peau, "corps"), ("langue", "langue"), ("globe", "globe", True), ("oeil", "globe", True),
            ("cuisse", "cuisse", True), ("pied", "pied", True), ("bras", "bras", True), ("main", "main", True)]


def monte(t, debut, fin):
    """De 0 (avant « debut ») à 1 (après « fin »), en douceur."""
    x = borne((t - debut) / (fin - debut))
    return x * x * (3 - 2 * x)


def gonfle(p, g):
    """La gorge : g = 1 pour le grand sac du coassement, 0,15 pour un battement."""
    p.add("gorge", ech=(1 + 1.5 * g, 1 + 1.5 * g, 1 + 1.5 * g))


def repos(t):
    """Assise, la gorge qui bat. Elle la gonfle en grand, puis roule des yeux vers sa gauche, cligne,
    et se passe la langue sur la lèvre."""
    p = Pose()
    sac = cloche(t, 0.28, 0.17)
    bat = (0.5 + 0.5 * onde(t, 10)) * (1 - sac)
    r = onde(t, 2)
    regard = cloche(t, 0.58, 0.09)
    gonfle(p, sac + 0.15 * bat)
    p.add("corps", rot=(-3.5 * sac, 0, 0), ech=(1 + 0.012 * r + 0.02 * sac, 1, 1 + 0.018 * r))
    p.paire("bras", ech=(1, 1, 1 + 0.085 * sac))                   # les mains restent dans l'herbe
    p.paire("pied", rot=(3.5 * sac, 0, 0))
    for cote in ("_G", "_D"):
        p.add("globe" + cote, rot=(-8 * regard, 0, 26 * regard))
    p.add("langue", rot=(0, 0, 38 * (cloche(t, 0.80, 0.035) - cloche(t, 0.86, 0.035))),
          ech=(1, 1 + 0.5 * cloche(t, 0.83, 0.08), 1 + 0.7 * cloche(t, 0.83, 0.08)))
    p.ouvert = 1 - cloche(t, 0.70, 0.025) - cloche(t, 0.05, 0.025)
    return p


def avance(t):
    """Un saut par cycle : elle se tasse, pousse sur ses cuisses, part les pattes tendues derrière elle,
    les ramène sous le ventre, retombe et s'écrase un peu."""
    p = Pose()
    tasse = cloche(t, 0.10, 0.10)
    u = borne((t - 0.17) / 0.50)                                   # en l'air de 0,17 à 0,67
    vol = 4 * u * (1 - u)
    choc = cloche(t, 0.72, 0.08)
    # la cuisse tourne autour de la hanche : elle pousse jusqu'à la verticale (111°), part en arrière (165°), puis revient
    angle = 111 * borne((t - 0.16) / 0.13) + 54 * monte(t, 0.29, 0.36) - 165 * borne((t - 0.47) / 0.18)
    traine = monte(angle, 111, 165)
    cabre, pique = cloche(t, 0.28, 0.12), cloche(t, 0.54, 0.14)
    arriere = monte(t, 0.17, 0.30) * (1 - monte(t, 0.40, 0.56))    # les bras partent le long du ventre
    devant = cloche(t, 0.59, 0.12)                                 # puis se tendent vers le sol
    p.add("corps", pos=(0, 0, 0.13 * vol), rot=(-6 * cabre + 14 * pique, 0, 0),
          ech=(1 + 0.05 * tasse + 0.07 * choc, 1, 1 - 0.10 * tasse - 0.13 * choc + 0.05 * cabre))
    p.paire("cuisse", rot=(angle, 0, -0.05 * angle), ech=(1, 1 + 0.12 * traine, 1))
    # le pied glisse au bout de la patte et reste presque à plat : la pointe ne descend qu'une fois la patte en arrière
    p.paire("pied", pos=tuple(c * borne(angle / 55) for c in (0.017, -0.057, 0.091)), rot=(-angle + 40 * traine, 0, 0))
    p.paire("bras", rot=(55 * arriere - 28 * devant, 0, 0))
    p.paire("main", rot=(50 * arriere - 15 * devant, 0, 0))
    p.paire("globe", pos=(0, 0, -0.008 * choc))
    p.ouvert = borne(1 - cloche(t, 0.73, 0.05))
    return p


def mange(t):
    """Elle se penche sur l'herbe, darde trois fois la langue, se redresse et avale en rentrant les yeux."""
    p = Pose()
    penche = monte(t, 0.03, 0.15) * (1 - monte(t, 0.50, 0.62))
    dard = max(cloche(t, 0.21, 0.04), cloche(t, 1 / 3, 0.04), cloche(t, 0.45, 0.04))
    avale = cloche(t, 0.69, 0.08)
    p.add("corps", rot=(13 * penche, 0, 0))
    p.paire("bras", rot=(6 * penche, 0, 0), ech=(1, 1, 1 - 0.38 * penche))     # les mains ne quittent pas l'herbe
    p.paire("main", rot=(-28 * penche, 0, 0))
    p.paire("pied", rot=(-13 * penche, 0, 0), pos=(0, 0, 0.012 * penche))
    p.add("langue", rot=(-30 * dard, 0, 0), ech=(1 - 0.25 * dard, 1, 1 + 4 * dard))
    p.paire("globe", pos=(0, 0.004 * avale, -0.022 * avale))
    gonfle(p, 0.6 * cloche(t, 0.74, 0.07))
    p.ouvert = borne(1 - 1.2 * avale)
    return p


def joie(t):
    """Elle se dresse, les bras au ciel, et pousse deux grands coassements : la gorge en ballon, un petit bond à chacun."""
    p = Pose()
    env = monte(t, 0.0, 0.16) * (1 - monte(t, 0.80, 0.98))
    cri = cloche(t, 0.30, 0.15, False) + cloche(t, 0.62, 0.15, False)
    bond = cloche(t, 0.33, 0.11, False) + cloche(t, 0.65, 0.11, False)
    p.add("corps", pos=(0, 0, 0.045 * bond), rot=(-12 * env, 0, 0))
    gonfle(p, 1.15 * cri)
    p.paire("bras", rot=(0, -(105 + 25 * cri) * env, 0))
    p.paire("main", rot=(0, 35 * env, 0))
    p.paire("cuisse", rot=(12 * env, 0, 0))                        # les cuisses restent posées, les pieds dessous
    p.paire("pied", rot=(-14 * bond, 0, 0))
    p.paire("globe", ech=(1 + 0.08 * cri, 1 + 0.08 * cri, 1 + 0.08 * cri))
    return p


def dort(t):
    """Aplatie dans l'herbe, les bras écartés, les yeux rentrés et fermés ; le dos se soulève lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", rot=(15, 0, 0), ech=(1.06 + 0.01 * r, 1.0, 0.82 + 0.03 * r))
    gonfle(p, 0.08 + 0.06 * r)
    p.paire("globe", pos=(0, 0.004, -0.014))
    p.paire("bras", rot=(-18, -52, 0), pos=(0, 0, 0.018), ech=(1, 1, 0.75))       # les coudes écartés, les mains posées devant elle
    p.paire("main", rot=(-15, 52, 0))
    p.paire("cuisse", rot=(-14, 0, -8))
    p.paire("pied", rot=(-12, 0, 8), pos=(0, 0, 0.02))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (30, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
