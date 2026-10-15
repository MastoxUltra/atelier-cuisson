"""La tortue en peluche : le corps bleu ciel, la carapace en patchwork (moutarde, caramel, chocolat) cousue au point de feston.
Elle tend le cou, l'air d'une vieille dame pas commode.

    python tortue.py        fabrique la fiche art/apercus/animaux/tortue.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import peluche as K

CARAPACE = Vector((0.0, 0.035, 0.080))      # le milieu du bord de la carapace
RX, RY, RZ = 0.145, 0.160, 0.135            # sa demi-largeur, sa demi-longueur, la hauteur du dôme
COEUR = CARAPACE + Vector((0, 0, 0.005))    # le point d'où l'on vise les écailles
TETE = Vector((0.0, -0.226, 0.212))


def cap(ecart, tour):
    """Une direction vue du cœur de la carapace : « ecart » depuis le sommet, « tour » depuis l'avant vers la gauche (degrés)."""
    e, t = math.radians(ecart), math.radians(tour)
    return Vector((math.sin(e) * math.sin(t), -math.sin(e) * math.cos(t), math.cos(e)))


def ecaille(axe, coins, rond=8):
    """L'ouverture d'une rustine à pans, aux coins arrondis : « coins » sont les directions de ses coins.
    (Le repère est celui que prend le kit pour une rustine d'axe « axe ».)"""
    a = Vector(axe).normalized()
    e1 = a.cross(Vector((0, 0, 1)))
    if e1.length < 1e-4:
        e1 = a.cross(Vector((1, 0, 0)))
    e1.normalize()
    e2 = a.cross(e1).normalized()
    pts = []
    for c in coins:
        d = Vector(c).normalized()
        r, th = a.angle(d), math.atan2(d.dot(e2), d.dot(e1))
        pts.append(np.array([r * math.cos(th), r * math.sin(th)]))
    pans = []
    for p, q in zip(pts, pts[1:] + pts[:1]):
        n = np.array([q[1] - p[1], p[0] - q[0]])
        n /= np.linalg.norm(n)
        if n @ p < 0:
            n = -n
        pans.append((n, float(n @ p)))

    def ouverture(th):
        u = np.array([math.cos(th), math.sin(th)])
        return sum((max(float(n @ u), 0.0) / d) ** rond for n, d in pans) ** (-1.0 / rond)
    return ouverture


def construire():
    a = K.Animal("tortue")
    a.taille = 0.62
    a.tete = TETE

    def vise(sur, centre, direction):
        """Le point de la pièce « sur » visé depuis « centre », et la normale du tissu à cet endroit."""
        d = Vector(direction).normalized()
        e1 = d.orthogonal().normalized()
        p, p1, p2 = a.trace(sur, centre, [d, d + e1 * 0.04, d + d.cross(e1) * 0.04], 0.0)
        n = (p1 - p).cross(p2 - p).normalized()
        return p, (n if n.dot(d) > 0 else -n)

    # ----- la carapace : un dôme de feutrine brune, bordé d'un bourrelet, sur un plastron crème -----
    def dome(v):
        s = K.emousse(v, 0.88) * [RX, RY, RZ]
        s[v[:, 2] < 0, 2] *= 0.22                              # un dessous presque plat
        return s
    a.piece("carapace", A.boule(1.0, 56, 28).sculpte(dome), K.BRUN, pos=CARAPACE, poil=False)
    a.piece("bourrelet", A.tore(1.0, 0.085, 56, 12).etire(RX, RY, RX), K.CARAMEL, pos=CARAPACE, poil=False)
    a.piece("plastron", A.boule(1.0, 40, 20).etire(0.128, 0.146, 0.038), K.CREME, pos=(0, 0.035, 0.058), poil=False)

    # ----- le patchwork : une écaille chocolat au sommet, six autour, le brun du dôme fait les joints -----
    # (un tissu à motif doit être clair et tourné vers l'œil : foncé ou vu de biais, son reflet blanc le délave)
    a.rustine("sommet", "carapace", COEUR, (0, 0, 1), ecaille((0, 0, 1), [cap(21, 30 + 60 * k) for k in range(6)]),
              K.CHOCOLAT, feston=18)
    etoffes = [(K.MOUTARDE, None), (K.CARAMEL, ("rayures", K.CREME)), (K.MOUTARDE, None),
               (K.CARAMEL, ("pois", K.CREME)), (K.MOUTARDE, None), (K.CARAMEL, None)]
    for k, (couleur, motif) in enumerate(etoffes):
        t = 60 * k
        pans = ecaille(cap(54, t), [cap(24.5, t - 26), cap(24.5, t + 26), cap(83, t + 28.3), cap(83, t - 28.3)])
        a.rustine("ecaille%d" % k, "carapace", COEUR, cap(54, t), pans, couleur, feston=26, motif=motif)

    # ----- les quatre pattes : des poteaux qui sortent de sous le bord, un ourlet à la cheville -----
    poteau = A.profil([(0, 0), (0.036, 0.006), (0.035, 0.045), (0.030, 0.085), (0, 0.10)], 6)
    for nom, y, penche in (("patte_avant", -0.090, 0.32), ("patte_arriere", 0.160, -0.32)):
        patte = A.tour(poteau, 32).sculpte(lambda v, penche=penche: v + np.outer(v[:, 2], [-0.45, penche, 0.0]))
        a.piece(nom, patte, K.MENTHE, pos=(0.108, y, 0.0), paire=True)
        a.ourlet(nom, nom, 0.42, paire=True)

    # ----- le cou tendu, ridé de deux ourlets, et la queue -----
    cou = A.tour(A.profil([(0, 0), (0.040, 0.012), (0.036, 0.08), (0.032, 0.17), (0, 0.19)], 5), 32)
    a.piece("cou", cou, K.MENTHE, pos=(0, -0.085, 0.088), rot=A.viser((0, -0.74, 0.67)))
    for i, pli in enumerate((0.48, 0.58)):
        a.ourlet("pli%d" % i, "cou", pli)
    queue = A.tube(A.courbe([(0, 0.175, 0.070), (0, 0.222, 0.058), (0, 0.250, 0.036)], 5), lambda t: 0.018 - 0.012 * t, 10)
    a.piece("queue", queue, K.MENTHE)

    # ----- la tête : deux boutons, une bouche qui tombe, des sourcils froncés -----
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(lambda v: K.emousse(v, 0.9)).etire(0.056, 0.066, 0.050), K.MENTHE, pos=TETE)
    a.couture("crane", "tete", 12, 0.55, 0.98)
    vers_oeil = Vector((0.80, -0.40, 0.38)).normalized()
    oeil, regard = vise("tete", TETE, vers_oeil)
    a.bouton("oeil", oeil, regard, 0.017, paire=True)
    bec = [(0.056 * math.sin(s), -0.066 * math.cos(s), -0.014 - 0.0125 * (abs(s) / 1.5) ** 2) for s in np.linspace(-1.5, 1.5, 21)]
    a.broderie("bouche", a.trace("tete", TETE, bec, 0.0035), 0.0026)
    haut = (Vector((0, 0, 1)) - vers_oeil * vers_oeil.z).normalized()      # vers le haut, le long de la tête
    nez = haut.cross(vers_oeil)
    nez = nez if nez.y < 0 else -nez                                       # vers le museau, le long de la tête
    sourcil = [vers_oeil * math.cos(0.40) + (haut * math.cos(b) + nez * math.sin(b)) * math.sin(0.40) for b in np.linspace(1.22, -0.10, 7)]
    a.broderie("sourcil", a.trace("tete", TETE, sourcil, 0.004), 0.0032, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py tortue)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.035, 0.06)),             # la carapace et tout ce qui est dessous
    ("cou", "corps", (0, -0.085, 0.088)),              # là où le cou sort de la carapace
    ("tete", "cou", (0, -0.200, 0.190)),
    ("avant_G", "corps", (0.063, -0.058, 0.095)),      # le haut de chaque patte, sous le bord
    ("arriere_G", "corps", (0.063, 0.128, 0.095)),
    ("queue", "corps", (0, 0.175, 0.070)),
]
PORTEURS = [("patte_avant", "avant", True), ("patte_arriere", "arriere", True), ("cou", "cou"), ("pli", "cou"),
            ("tete", "tete"), ("crane", "tete"), ("oeil", "tete"), ("bouche", "tete"), ("sourcil", "tete"), ("queue", "queue"),
            ("carapace", "corps"), ("bourrelet", "corps"), ("plastron", "corps"), ("sommet", "corps"), ("ecaille", "corps")]
PAS = (("avant_G", 0.0), ("arriere_D", 0.25), ("avant_D", 0.5), ("arriere_G", 0.75))      # une patte après l'autre


def repos(t):
    """Elle prend son temps : la tête va lentement d'un côté à l'autre, le cou rentre un peu puis ressort, elle cligne."""
    p = Pose()
    g, d = cloche(t, 0.25, 0.20), cloche(t, 0.72, 0.20)
    rentre = cloche(t, 0.48, 0.08)
    p.add("cou", rot=(-4 * g - 4 * d, 0, 18 * g - 18 * d), ech=(1, 1 - 0.18 * rentre, 1 - 0.18 * rentre))
    p.add("tete", rot=(3 * onde(t, 2), 0, 12 * g - 12 * d), ech=(1, 1 / (1 - 0.18 * rentre), 1 / (1 - 0.18 * rentre)))
    p.add("avant_D", rot=(-10 * cloche(t, 0.90, 0.06), 0, 0), pos=(0, 0, 0.008 * cloche(t, 0.90, 0.05)))
    p.add("queue", rot=(0, 0, 14 * cloche(t, 0.60, 0.06) * onde(t, 6)))
    p.ouvert = 1 - cloche(t, 0.12, 0.035) - cloche(t, 0.50, 0.05)
    return p


def avance(t):
    """Très lentement, une patte après l'autre ; la carapace roule un peu, la tête dodeline au bout du cou."""
    p = Pose()
    s = math.sin(math.tau * t)
    p.add("corps", rot=(1.5 * math.sin(2 * math.tau * t), 3 * s, 0), pos=(0, 0, 0.003 * abs(s)))
    for nom, quand in PAS:
        a = math.tau * (t - quand)
        p.add(nom, rot=(20 * math.sin(a), 0, 0), pos=(0, 0, 0.012 * max(0.0, math.cos(a))))
    p.add("cou", rot=(4 * math.sin(2 * math.tau * t), 0, 5 * s))
    p.add("tete", rot=(-4 * math.sin(2 * math.tau * t), 0, 3 * s))
    p.add("queue", rot=(0, 0, -8 * s))
    return p


def mange(t):
    """Le cou s'allonge jusqu'au sol ; elle happe trois fois, sans hâte, puis relève la tête et mâche longuement."""
    p = Pose()
    leve = cloche(t, 0.84, 0.14)
    bas = 1 - leve
    happe = max(0.0, onde(t, 3)) ** 2 * bas
    p.add("corps", rot=(5 * bas, 0, 0))
    p.add("cou", rot=(44 * bas + 6 * happe, 0, 0))
    p.add("tete", rot=(12 * bas + 6 * happe + 3 * onde(t, 6) * leve, 0, 0))
    p.add("queue", rot=(0, 0, 6 * onde(t, 2)))
    p.ouvert = 1 - 0.6 * happe - 0.4 * leve
    return p


def joie(t):
    """Une joie lente et digne : elle se hisse sur ses pattes, tend le cou vers le ciel et hoche deux fois la tête."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    p.add("corps", pos=(0, 0, 0.018 * env), rot=(-4 * env, 0, 0))
    p.paire("avant", ech=(1, 1, 1 + 0.26 * env))
    p.paire("arriere", ech=(1, 1, 1 + 0.12 * env))
    p.add("cou", rot=(-24 * env, 0, 0))
    p.add("tete", rot=(10 * env + 9 * onde(t, 2) * env, 0, 0))
    p.add("queue", rot=(0, 0, 16 * onde(t, 5) * env))
    p.ouvert = 1 - 0.7 * env
    return p


def dort(t):
    """Tout est rentré : les pattes sous le bord, le cou dans la carapace, il ne dépasse que le bout du nez. Elle dort."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.020), ech=(1 + 0.006 * r, 1, 1 + 0.012 * r))
    p.paire("avant", ech=(1, 1, 0.30), pos=(-0.030, 0.020, 0))
    p.paire("arriere", ech=(1, 1, 0.30), pos=(-0.030, -0.020, 0))
    p.add("cou", ech=(1, 0.30, 0.30))
    p.add("tete", ech=(1, 1 / 0.30, 1 / 0.30))
    p.add("queue", ech=(1, 0.40, 1))
    return p


ANIMATIONS = {"repos": (180, repos, True), "avance": (60, avance, True), "mange": (90, mange, True),
              "joie": (72, joie, False), "dort": (150, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
