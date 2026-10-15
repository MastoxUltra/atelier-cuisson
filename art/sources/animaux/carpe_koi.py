"""La carpe koï en peluche : blanc crème, rapiécée de corail et de noir, posée sur le ventre dans l'herbe.
Elle relève le nez comme une carpe qui réclame, et sa queue part sur le côté.

    python carpe_koi.py        fabrique la fiche art/apercus/animaux/carpe_koi.png
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

CORPS = Vector((0.0, -0.13, 0.066))     # le milieu de l'épaule, là où le corps est le plus gros
AVANT, ARRIERE = 0.15, 0.31             # de l'épaule au nez, de l'épaule au bout du pédoncule
CHARBON = M.hexa("#2b2a30")             # le noir des taches : un feutre anthracite, pour que son relief se voie
IVOIRE = M.hexa("#fff5e0")              # le blanc crème du poil : entre K.BLANC (gris à l'ombre) et K.CREME (beige)


def ploie(y):
    """La pose : le nez se relève, la queue part vers la gauche et remonte un peu.
    Rend le décalage (en x, en z) du corps à la distance y de l'épaule."""
    avant, arriere = np.maximum(-y, 0.0), np.maximum(y, 0.0)
    return 0.62 * arriere ** 2, 1.5 * avant ** 2 + 0.25 * arriere ** 2


def axe(y):
    """Le point du milieu du corps à la distance y de l'épaule (devant si y < 0) : toujours dans la peluche."""
    dx, dz = ploie(y)
    return CORPS + Vector((float(dx), y, float(dz)))


def debout(depart, arrivee, penche=0.0):
    """Le repère d'une pièce découpée posée de chant : son X va de « depart » vers « arrivee », son Y monte.
    penche : des degrés pour la coucher un peu vers la droite (sa face gauche se tourne vers le ciel)."""
    u = (Vector(arrivee) - Vector(depart)).normalized()
    n = u.cross(Vector((0, 0, 1))).normalized()
    n = n * math.cos(math.radians(penche)) + n.cross(u) * math.sin(math.radians(penche))
    return A.cadre(depart, n, n.cross(u))


def construire():
    a = K.Animal("carpe_koi")
    a.taille = 0.75
    a.tete = axe(-0.09) + Vector((0, 0, 0.015))

    def vise(centre, direction):
        """Le point du corps visé depuis « centre », et la normale du tissu à cet endroit."""
        d = Vector(direction).normalized()
        e1 = d.orthogonal().normalized()
        p, p1, p2 = a.trace("corps", centre, [d, d + e1 * 0.04, d + d.cross(e1) * 0.04], 0.0)
        n = (p1 - p).cross(p2 - p).normalized()
        return p, (n if n.dot(d) > 0 else -n)

    # ----- le corps : une boule couchée (son pôle du haut fait le nez), ronde devant, effilée derrière -----
    def coque(v):
        u = np.stack([v[:, 0], -v[:, 2], v[:, 1]], axis=1)
        for cote in (1, -1):                                   # deux bonnes joues
            u = K.bosse(u, (0.75 * cote, -0.55, -0.20), 0.07, 0.25)
        x, t, z = u[:, 0], u[:, 1], u[:, 2]
        arriere = K.lisse(t)
        y = t * np.where(t < 0, AVANT, ARRIERE)
        dx, dz = ploie(y)
        return np.stack([x * 0.098 * (1 - 0.42 * arriere) + dx, y,
                         z * np.where(z > 0, 0.088, 0.070) * (1 - 0.32 * arriere) + dz], axis=1)
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    G.sillons(corps, [14], 0.004, 1.1)                         # la couture du dos creuse un peu le tissu
    a.piece("corps", corps, IVOIRE, pos=CORPS)
    a.couture("dos", "corps", 14, 0.19, 0.34)                  # entre la dorsale et la queue

    # ----- la robe : trois rapiéçages du côté qu'on voit, un quatrième sur l'autre épaule -----
    a.rustine("calotte", "corps", axe(-0.08), (0.12, -0.15, 1.0),
              lambda th: 0.50 + 0.07 * math.cos(2 * th) + 0.05 * math.sin(3 * th), K.CORAIL, feston=24)
    a.rustine("selle", "corps", axe(0.06), (0.35, 0.0, 0.94),
              lambda th: 0.70 + 0.16 * math.cos(2 * th) + 0.10 * math.sin(th) + 0.05 * math.cos(3 * th + 0.6), K.CORAIL, feston=44)
    a.rustine("tache", "corps", axe(0.205), (0.85, 0.0, 0.40),
              lambda th: 0.62 + 0.20 * math.cos(2 * th) + 0.05 * math.sin(3 * th), CHARBON, feston=26)
    a.rustine("tache2", "corps", axe(0.01), (-0.72, 0.0, 0.69), lambda th: 0.30 + 0.05 * math.cos(3 * th), CHARBON, feston=16)

    # ----- les yeux sur les côtés de la tête, et l'ouïe brodée derrière -----
    oeil, regard = vise(axe(-0.085), (0.82, -0.22, 0.42))
    a.bouton("oeil", oeil, regard, 0.024, paire=True)
    ouie = a.trace("corps", axe(-0.045), [(math.cos(s), 0.22 * math.cos(1.3 * s) - 0.05, math.sin(s))
                                          for s in np.linspace(-0.30, 0.85, 14)], 0.004)
    a.broderie("ouie", ouie, 0.0022, K.CARAMEL, paire=True)

    # ----- la bouche en rond, tournée vers le haut, et les deux barbillons -----
    gueule, devant = vise(axe(-0.10), (0, -1.0, 0.22))
    a.piece("bouche", A.tore(0.0145, 0.006, 32, 10), K.CORAIL, pos=gueule - devant * 0.002, rot=A.viser(devant), poil=False)
    a.piece("gosier", A.boule(1.0, 20, 10).etire(0.011, 0.011, 0.004), CHARBON, pos=gueule, rot=A.viser(devant), poil=False)
    barbillon = A.courbe([gueule + Vector(p) for p in ((0.015, 0.004, -0.006), (0.028, -0.006, -0.012),
                                                       (0.037, -0.008, -0.024), (0.040, -0.003, -0.038))], 5)
    a.broderie("barbillon", barbillon, lambda s: 0.0034 - 0.0016 * s, K.BRUN, paire=True)

    # ----- la queue : un éventail de feutrine à deux lobes, dans le prolongement du corps -----
    racine = axe(0.265)
    rep = debout(racine, racine + Vector((0.40, 1.0, 0.16)), 25)      # elle retombe un peu sur le côté, comme du feutre
    eventail = A.courbe([(0.0, 0.018), (0.04, 0.030), (0.10, 0.070), (0.165, 0.110), (0.200, 0.105), (0.195, 0.070),
                         (0.165, 0.025), (0.150, 0.0), (0.165, -0.025), (0.190, -0.060), (0.192, -0.088), (0.160, -0.092),
                         (0.10, -0.060), (0.04, -0.028), (0.0, -0.018)], 5, fermee=True)
    a.piece("queue", A.decoupe(eventail, 0.012, 0.003), K.CREME, mat=rep, poil=False)
    for i, (w0, u1, w1) in enumerate(((0.012, 0.172, 0.088), (0.004, 0.150, 0.042), (-0.004, 0.158, -0.036), (-0.012, 0.168, -0.070))):
        for face in (1, -1):                                   # les rayons, brodés des deux côtés
            a.broderie("rayon_queue%d" % i, [rep @ Vector((0.05, w0, face * 0.0068)), rep @ Vector((u1, w1, face * 0.0068))], 0.0015, K.CORAIL)

    # ----- la dorsale : une voile basse plantée dans la couture du dos -----
    p0 = a.trace("corps", axe(-0.03), [(0, 0, 1)], 0.0)[0] - Vector((0, 0, 0.004))
    p1 = a.trace("corps", axe(0.15), [(0, 0, 1)], 0.0)[0] - Vector((0, 0, 0.004))
    rep, long = debout(p0, p1), (p1 - p0).length
    voile = A.courbe([(u * long, w) for u, w in ((0.0, -0.014), (0.02, 0.012), (0.12, 0.046), (0.28, 0.058), (0.48, 0.050),
                                                 (0.68, 0.038), (0.86, 0.028), (0.98, 0.014), (1.0, -0.014), (0.5, -0.018))], 5, fermee=True)
    a.piece("dorsale", A.decoupe(voile, 0.010, 0.003), K.CREME, mat=rep, poil=False)
    for i, (u0, u1, w1) in enumerate(((0.16, 0.26, 0.046), (0.40, 0.52, 0.040), (0.64, 0.76, 0.027))):
        for face in (1, -1):
            a.broderie("rayon_dorsale%d" % i, [rep @ Vector((u0 * long, 0.006, face * 0.0058)), rep @ Vector((u1 * long, w1, face * 0.0058))], 0.0015, K.CORAIL)

    # ----- les pectorales : deux palettes de feutrine ouvertes sur l'herbe -----
    palette = A.courbe([(-0.018, -0.012), (0.020, -0.032), (0.062, -0.030), (0.098, -0.004), (0.108, 0.036), (0.094, 0.070),
                        (0.062, 0.078), (0.028, 0.052), (-0.018, 0.022)], 5, fermee=True)
    rep = A.repere((0.076, CORPS.y - 0.045, 0.052), (0, 18, 0))
    a.piece("pectorale", A.decoupe(palette, 0.010, 0.003), K.CREME, mat=rep, poil=False, paire=True)
    for i, (y0, x1, y1) in enumerate(((0.004, 0.090, 0.002), (0.016, 0.092, 0.040), (0.026, 0.066, 0.064))):
        a.broderie("rayon_pectorale%d" % i, [rep @ Vector((0.034, y0, 0.0058)), rep @ Vector((x1, y1, 0.0058))], 0.0015, K.CORAIL, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py carpe_koi)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, -0.13, 0.066)),            # l'épaule : la tête et l'avant du corps
    ("dos", "corps", (0.0, -0.03, 0.068)),             # le milieu du corps
    ("croupe", "dos", (0.02, 0.07, 0.070)),            # l'arrière, qui s'effile
    ("queue", "croupe", (0.0435, 0.135, 0.084)),       # la racine de l'éventail
    ("pectorale_G", "corps", (0.076, -0.175, 0.052)),
]


def _corps(points, cote):
    """Le corps est un seul boudin qui ondule : l'avant suit « corps », le milieu « dos », l'arrière « croupe »."""
    y = points[:, 1]
    milieu = K.lisse((y + 0.10) / 0.10)
    arriere = K.lisse((y - 0.03) / 0.09)
    return {"corps": 1.0 - milieu, "dos": milieu * (1.0 - arriere), "croupe": milieu * arriere}


PORTEURS = [("rayon_queue", "queue"), ("rayon_dorsale", _corps, "corps"), ("rayon_pectorale", "pectorale", True),
            ("queue", "queue"), ("dorsale", _corps, "corps"), ("pectorale", "pectorale", True),
            ("corps", _corps, "corps"), ("dos", _corps, "corps"), ("calotte", _corps, "corps"), ("selle", _corps, "corps"),
            ("tache", _corps, "corps"), ("ouie", "corps"), ("oeil", "corps"), ("bouche", "corps"), ("gosier", "corps"), ("barbillon", "corps")]


def ondule(p, t, force, tours=1):
    """La nage : une vague qui part de la tête et grossit jusqu'à la queue."""
    p.add("corps", rot=(0, 0, 0.30 * force * onde(t, tours)))
    p.add("dos", rot=(0, 0, -0.55 * force * onde(t, tours, -0.12)))
    p.add("croupe", rot=(0, 0, -0.85 * force * onde(t, tours, -0.26)))
    p.add("queue", rot=(0, 0, -1.30 * force * onde(t, tours, -0.40)))


def repos(t):
    """Elle se tient sur place : le corps ondule à peine, les nageoires godillent, elle cligne et hoche du nez."""
    p = Pose()
    ondule(p, t, 9, 2)
    p.paire("pectorale", rot=(0, 16 * onde(t, 4), 8 * onde(t, 4, 0.25)))
    p.add("corps", rot=(-4 * cloche(t, 0.55, 0.08), 0, 0), pos=(0, 0, 0.004 * onde(t, 1)))
    p.ouvert = 1 - cloche(t, 0.30, 0.03) - cloche(t, 0.80, 0.03)
    return p


def avance(t):
    """Elle nage : tout le corps ondule, la queue fouette large, les nageoires se plaquent le long du corps."""
    p = Pose()
    ondule(p, t, 20)
    p.paire("pectorale", rot=(0, -10 + 6 * onde(t, 2), 26))
    return p


def mange(t):
    """Elle gobe à la surface : quatre coups de bouche vers le haut, le nez relevé, la queue qui équilibre."""
    p = Pose()
    gobe = max(0.0, onde(t, 4)) ** 2 * (1 - cloche(t, 0.90, 0.08))
    ondule(p, t, 6, 2)
    p.add("corps", rot=(-16 * gobe - 5, 0, 0), pos=(0, 0, 0.018 * gobe))
    p.add("dos", rot=(9 * gobe, 0, 0))
    p.add("croupe", rot=(6 * gobe, 0, 0))
    p.paire("pectorale", rot=(0, 20 * gobe + 8 * onde(t, 4), 0))
    p.ouvert = 1 - 0.5 * gobe
    return p


def joie(t):
    """Elle frétille, bondit hors de l'eau en se cambrant, et retombe en fouettant de la queue."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    s = borne((t - 0.25) / 0.45)
    saut = 4 * s * (1 - s)
    ondule(p, t, 22 * env, 5)
    p.add("corps", pos=(0, 0, 0.14 * saut), rot=(-22 * saut + 14 * cloche(t, 0.72, 0.10, False), 0, 0))
    p.add("dos", rot=(12 * saut, 0, 0))
    p.add("croupe", rot=(14 * saut, 0, 0))
    p.paire("pectorale", rot=(0, 34 * saut, 0))
    return p


def dort(t):
    """Immobile entre deux eaux, les yeux fermés ; la queue balance à peine, une nageoire frémit de temps en temps."""
    p = Pose()
    ondule(p, t, 3)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.004 + 0.003 * onde(t, 1)))
    p.paire("pectorale", rot=(0, -8 + 5 * cloche(t, 0.6, 0.06) * onde(t, 8), 10))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (20, avance, True), "mange": (80, mange, True),
              "joie": (54, joie, False), "dort": (150, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Carpe koï")
