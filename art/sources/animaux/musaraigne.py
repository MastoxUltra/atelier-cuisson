"""La musaraigne en peluche, deuxième dessin : la petite anxieuse du tas de feuilles. Une poire de velours chocolat froid,
assise sur sa croupe ronde, le dos voûté, coupée net en deux par le ventre crème qui lui monte jusqu'au menton ; une
toute petite tête, et devant, une trompe interminable, plus longue que la tête et le cou réunis, qui part de travers,
se tortille et relève le bout rose pour flairer. Les deux menottes roses serrées sous le menton, les sourcils brodés
qui se froncent en accent, une queue mince qui traîne derrière elle en S. Elle a entendu quelque chose.

    python musaraigne.py        fabrique la fiche art/apercus/animaux/musaraigne.png
    (le premier dessin, jamais gardé : musaraigne_ancien.py)
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

CACAO = M.hexa("#5c443e")                     # le velours : un chocolat froid, tiré vers le gris (pas le chocolat chaud du chien)
SUIE = M.hexa("#36282a")                      # les oreilles, la queue, la pièce de la hanche, le fil des sourcils
CREME = M.hexa("#f4ead6")                     # le ventre, le menton
ROSE = M.hexa("#f27f9a")                      # l'accent : le bout de la trompe, les menottes, les pieds
TOURNE = 0                                    # -28 pour la fiche, posée de biais (on lit la trompe) ; 0 pour le jeu
# l'échine, de la croupe à la nuque : assise sur la croupe, le dos voûté, l'avant dressé
DOS = K.Fil([(0.0, 0.070, 0.041), (0.0, 0.030, 0.060), (0.0, -0.012, 0.080), (0.0, -0.044, 0.104)], flanc=(1, 0, 0))
GALBE = [(0, 0), (0.040, 0.006), (0.056, 0.026), (0.060, 0.052), (0.055, 0.080), (0.044, 0.106), (0.032, 0.124), (0, 0.140)]
TETE = Vector((0.004, -0.066, 0.134))
PORT = A.repere(TETE, (-4, -10, 20))         # la tête levée, tournée vers vous, penchée : elle écoute


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def construire():
    a = K.Animal("musaraigne")
    a.taille = 0.30

    # ----- le corps : une poire couchée le long de l'échine, la croupe large ; le ventre crème coupé net, qui monte
    #       jusqu'au poitrail -----
    corps = A.tour(A.profil(GALBE, 8), 56)
    rho = np.maximum(np.hypot(corps.v[:, 0], corps.v[:, 1]), 1e-9)
    ligne = -0.30 + 0.55 * K.lisse((corps.v[:, 2] - 0.070) / 0.060)          # la limite du crème monte vers le poitrail
    corps.teinte = np.where((corps.v[:, 1] / rho < ligne)[:, None], np.asarray(CREME), np.asarray(CACAO))

    def hanches(v):
        s = v.copy()
        s[:, 0] *= 1 + 0.14 * np.exp(-((v[:, 2] - 0.040) / 0.030) ** 2)
        return s
    corps.sculpte(hanches)
    G.sillons(corps, [14], 0.004, 1.1)
    corps.sculpte(DOS.couche)
    a.piece("corps", corps, None)
    a.couture("dos", "corps", 14, 0.10, 0.80, fil=CREME, large=0.007, haut=0.003, pas=0.011)
    centre, d = DOS.vise(0.034, 0.0, 0.85, 0.30)
    a.rustine("hanche", "corps", centre, d, lambda th: 0.30 + 0.05 * math.cos(3 * th) + 0.03 * math.sin(2 * th), SUIE,
              feston=14, fil=CREME)

    # ----- la tête : une petite boule, le crâne chocolat, les joues et le menton crème -----
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.where((tete.v[:, 2] - 0.55 * tete.v[:, 1] < -0.22)[:, None], np.asarray(CREME), np.asarray(CACAO))
    tete.sculpte(lambda v: K.bosse(v, (0, -0.6, 0.6), 0.10, 0.3) * [0.034, 0.038, 0.032])
    a.piece("tete", tete, None, mat=PORT)
    a.couture("crane", "tete", 14, 0.55, 0.96, fil=CREME, large=0.006, haut=0.003, pas=0.010)

    # ----- la trompe : interminable, elle part droit puis file de travers et relève son bout rose pour flairer -----
    f, l, h = vers(0, -1, 0), vers(-1, 0, 0), vers(0, 0, 1)        # l : elle part vers sa droite, de travers
    chemin = [TETE + f * 0.022, TETE + f * 0.054 - h * 0.002, TETE + f * 0.086 + l * 0.008 - h * 0.004,
              TETE + f * 0.114 + l * 0.026 - h * 0.002, TETE + f * 0.134 + l * 0.046 + h * 0.008, TETE + f * 0.144 + l * 0.058 + h * 0.022]
    chemin = A.courbe([tuple(p) for p in chemin], 6)
    a.piece("trompe", K.tube_peint(chemin, lambda t: 0.0150 - 0.0112 * t ** 0.7, [(0.82, CACAO), (9, ROSE)], 16), None)
    bout = Vector(chemin[-1])
    a.piece("nez", A.boule(0.0052, 20, 10), ROSE, pos=bout, poil=False)
    a.tete = TETE + f * 0.050

    # ----- les moustaches : deux fils crème de chaque côté, à mi-trompe -----
    milieu = Vector(chemin[len(chemin) * 3 // 5])
    for nom, c in (("g", 1), ("d", -1)):
        for i, (recul, leve) in enumerate(((0.006, 0.012), (-0.004, -0.010))):
            depart = milieu + l * (0.006 * c)
            fin = depart + l * (0.040 * c) + f * recul + h * leve
            a.broderie("moustache_%s%d" % (nom, i), A.courbe([depart, depart.lerp(fin, 0.5) + f * 0.004 + h * 0.003, fin], 5), 0.0011, CREME)

    # ----- les yeux : petits, vifs, sous deux sourcils froncés en accent ; les oreilles, deux pastilles dans le poil -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, vers(0.60 * c, -0.58, 0.48))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0072)
        cil = a.trace("tete", TETE, [vers(c * (0.20 + 0.42 * u), -0.66 + 0.36 * u, 0.88 - 0.22 * u) for u in np.linspace(0, 1, 5)], 0.0035)
        a.broderie("sourcil_" + nom, A.courbe(cil, 4), 0.0019, SUIE)
        p, n = a.surface("tete", TETE, vers(0.66 * c, 0.34, 0.62))
        a.piece("oreille_" + nom, A.boule(1.0, 24, 12).etire(0.013, 0.013, 0.0045), SUIE,
                mat=A.cadre(p + n * 0.004, (n + vers(0, -0.6, 0)).normalized(), n), poil=False)

    # ----- les menottes : deux petits bras serrés sous le menton, les mains roses jointes -----
    centre, av, nu = (Vector(x) for x in DOS.cadre(0.100))
    fl = Vector(DOS.flanc)
    for nom, c in (("G", 1), ("D", -1)):
        epaule, n = a.surface("corps", centre, fl * (0.70 * c) + av * 0.62 - nu * 0.12)
        main, n = a.surface("corps", centre, fl * (0.16 * c) + av * 0.80 - nu * 0.35)
        main = main + n * 0.006
        coude = epaule.lerp(main, 0.5) + n * 0.006 - nu * 0.008
        a.piece("bras_" + nom, A.tube(A.courbe([tuple(epaule - n * 0.004), tuple(coude), tuple(main)], 5), lambda t: 0.0085 - 0.0015 * t, 12), CACAO)
        a.piece("main_" + nom, A.boule(1.0, 20, 10).etire(0.0070, 0.0058, 0.0090), ROSE, mat=A.cadre(main + n * 0.002, -nu, n), poil=False)

    # ----- les pieds de derrière, roses, posés à plat de chaque côté de la croupe -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.013, 0.026, 0.0075), ROSE, pos=(0.044 * c, 0.056, 0.0075), rot=(0, 0, 12 * c), poil=False)

    # ----- la queue : mince, elle traîne derrière en S, le bout relevé -----
    queue = A.courbe([(0, 0.078, 0.034), (0.004, 0.112, 0.030), (0.022, 0.142, 0.029), (0.044, 0.162, 0.034), (0.058, 0.186, 0.046)], 6)
    a.piece("queue", A.tube(queue, lambda t: 0.0070 - 0.0040 * t, 12), SUIE)
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py musaraigne). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# La trompe est une pièce souple que deux os se passent : sa racine sur la tête, et son milieu, d'où le bout se tortille.

from poses import Pose, borne, cloche, onde


def _fil_trompe():
    """Le fil de la trompe, le même que dans construire() : de la tête jusqu'au bout rose."""
    f, l, h = vers(0, -1, 0), vers(-1, 0, 0), vers(0, 0, 1)
    chemin = [TETE + f * 0.022, TETE + f * 0.054 - h * 0.002, TETE + f * 0.086 + l * 0.008 - h * 0.004,
              TETE + f * 0.114 + l * 0.026 - h * 0.002, TETE + f * 0.134 + l * 0.046 + h * 0.008, TETE + f * 0.144 + l * 0.058 + h * 0.022]
    return A.courbe([tuple(p) for p in chemin], 6)


TROMPE = _fil_trompe()
_FAIT = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(TROMPE, axis=0), axis=1))])
_MILIEU = int(np.searchsorted(_FAIT, 0.5 * _FAIT[-1]))


def _ou(v):
    return tuple(round(float(x), 4) for x in v)


OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.050, 0.020)),            # le bas de la croupe, où elle est assise
    ("tete", "corps", (0.002, -0.050, 0.110)),           # la nuque, en haut de l'échine voûtée
    ("trompe", "tete", _ou(TROMPE[0])),                  # la racine de la trompe
    ("trompe2", "trompe", _ou(TROMPE[_MILIEU])),         # son milieu, d'où le bout se tortille
    ("bras_G", "corps", (0.026, -0.042, 0.095)),         # l'épaule (la droite est son miroir)
    ("pied_G", "racine", (0.044, 0.056, 0.0075)),        # le milieu du pied
    ("queue", "corps", (0.0, 0.078, 0.034)),
]


def _trompe(points, cote):
    """La trompe : la racine suit « trompe », le bout suit « trompe2 », en douceur autour du milieu."""
    a, ab = TROMPE[:-1], np.diff(TROMPE, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    ap = points[:, None, :] - a[None, :, :]
    u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
    j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
    s = (_FAIT[j] + u[np.arange(len(points)), j] * np.sqrt(l2[j])) / _FAIT[-1]
    w = K.lisse((s - 0.38) / 0.24)
    return {"trompe": 1 - w, "trompe2": w}


PORTEURS = [("corps", "corps"), ("dos", "corps"), ("hanche", "corps"),
            ("tete", "tete"), ("crane", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("oreille", "tete"),
            ("trompe", _trompe), ("nez", "trompe2"), ("moustache", "trompe2"),
            ("bras", "bras", True), ("main", "bras", True), ("pied", "pied", True), ("queue", "queue"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]

FLAIRE_SOL = (6.0, 20.0, 12.0)                # mange : le corps se penche, la tête plonge, la trompe se couche vers l'herbe
BOULE = (6.0, 16.0, 16.0, 40.0)                # dort : le corps, la tête, la trompe et son bout se replient


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _tortille(p, t, force, vite):
    """Le bout de la trompe se tortille dans tous les sens pour flairer (vite : combien d'allers-retours)."""
    p.add("trompe", rot=(3 * force * onde(t, vite / 2, 0.1), 0, 6 * force * onde(t, vite / 2)))
    p.add("trompe2", rot=(10 * force * onde(t, vite, 0.25), 0, 16 * force * onde(t, vite)))


def repos(t):
    """La petite anxieuse : elle respire vite, la trompe flaire sans arrêt, les menottes se tordent sous le menton ;
    elle tend l'oreille d'un côté, puis sursaute (tout le corps se raidit d'un coup), se fige, la trompe en l'air,
    et reprend son flair ; elle cligne vite."""
    p = Pose()
    r = onde(t, 8)
    p.add("corps", ech=(1 + 0.018 * r, 1 + 0.010 * r, 1 + 0.014 * r))
    _tortille(p, t, 1 - cloche(t, 0.62, 0.10), 16)
    ecoute = cloche(t, 0.30, 0.12)
    sursaut = cloche(t, 0.55, 0.03)
    fige = cloche(t, 0.62, 0.10)
    p.add("tete", rot=(-4 * fige, -10 * ecoute, 16 * ecoute - 10 * fige))
    p.add("corps", pos=(0, 0, 0.006 * sursaut), rot=(-5 * sursaut - 3 * fige, 0, 0))
    p.add("trompe", rot=(-12 * fige, 0, 0))
    p.paire("bras", rot=(6 * onde(t, 8) * (1 - fige), 0, 4 * onde(t, 8, 0.25)))
    p.add("queue", rot=(0, 0, 8 * onde(t, 2) + 12 * sursaut))
    p.ouvert = 1 - cloche(t, 0.12, 0.015) - cloche(t, 0.84, 0.015)
    return p


def avance(t):
    """Elle file à toute vitesse sous les feuilles : de petits bonds pressés (deux par cycle), les pieds qui trottinent,
    le corps qui se tasse et se détend, la trompe qui balaie le chemin d'un côté à l'autre, la queue qui traîne."""
    p = Pose()
    b = abs(onde(t, 2))
    p.add("corps", pos=(0, 0, 0.012 * b), rot=(6 - 6 * b, 0, 0), ech=(1, 1 + 0.04 * b, 1 - 0.03 * b))
    for nom, phase in (("pied_G", 0.0), ("pied_D", 0.5)):
        p.add(nom, pos=(0, -0.008 * onde(t, 2, phase), 0.008 * max(0.0, onde(t, 2, phase + 0.25)) + 0.012 * b))
    p.paire("bras", rot=(-14 * b, 0, 0))
    p.add("tete", rot=(-4 + 4 * b, 0, 0))
    p.add("trompe", rot=(0, 0, 10 * onde(t, 1)))
    p.add("trompe2", rot=(4 * onde(t, 2), 0, 14 * onde(t, 1, -0.15)))
    p.add("queue", rot=(0, 0, 10 * onde(t, 1, 0.3)))
    return p


def mange(t):
    """Elle couche la trompe dans l'herbe et fouille à petits coups pressés, croque un insecte en trois bouchées vives,
    se redresse en le serrant dans ses menottes et mâche en jetant des regards inquiets à droite, à gauche."""
    p = Pose()
    bas = _plateau(t, 0.36, 0.22, 0.10)
    croque = max(0.0, onde(t, 9)) * _plateau(t, 0.36, 0.18, 0.05)
    mache = cloche(t, 0.80, 0.14)
    p.add("corps", rot=(FLAIRE_SOL[0] * bas, 0, 0))
    p.add("tete", rot=(FLAIRE_SOL[1] * bas + 8 * croque - 6 * mache, 0, 22 * cloche(t, 0.76, 0.05) - 22 * cloche(t, 0.88, 0.05)))
    p.add("trompe", rot=(FLAIRE_SOL[2] * bas, 0, 0))
    _tortille(p, t, 0.6 * bas + 0.3, 12)
    p.paire("bras", rot=(-10 * bas + 6 * mache * onde(t, 10), 0, 0))
    p.ouvert = 1 - cloche(t, 0.68, 0.02)
    return p


def joie(t):
    """Sa joie, nerveuse : trois petits bonds sur place, tout droit, les menottes levées, la trompe qui s'enroule
    vers le ciel et frétille, la queue qui fouette ; puis elle retombe assise, déjà aux aguets."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85)) if t < 0.85 else 0.0
    bond = abs(onde(borne(t / 0.85), 3)) * env
    p.add("corps", pos=(0, 0, 0.035 * bond), rot=(-8 * env, 0, 0))
    p.paire("pied", pos=(0, 0, 0.035 * bond))
    p.paire("bras", rot=(-40 * env, -10 * env, 0))
    p.add("tete", rot=(-10 * env, 0, 8 * onde(t, 3) * env))
    p.add("trompe", rot=(-24 * env, 0, 0))
    p.add("trompe2", rot=(-30 * env + 10 * onde(t, 8) * env, 0, 12 * onde(t, 6) * env))
    p.add("queue", rot=(0, 0, 24 * onde(t, 6) * env))
    return p


def dort(t):
    """Pelotonnée, le dos rond, la tête baissée sur le ventre, la trompe posée dans l'herbe et le bout recourbé, la
    queue enroulée autour d'elle, les yeux fermés ; elle respire vite même en dormant, mais doucement."""
    p = Pose()
    r = onde(t, 3)
    p.ouvert = 0.0
    p.add("corps", rot=(BOULE[0], 0, 0), ech=(1.04 + 0.012 * r, 1.0, 0.96 + 0.015 * r))
    p.add("tete", rot=(BOULE[1], 0, 10))
    p.add("trompe", rot=(BOULE[2], 0, 10))
    p.add("trompe2", rot=(BOULE[3], 0, 0))
    p.paire("bras", rot=(10, 0, 0))
    p.add("queue", rot=(0, 0, 60))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Musaraigne")
