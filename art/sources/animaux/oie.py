"""L'oie en peluche : blanche de la tête aux cuisses, le bec et les pattes orange vif. Le gendarme de la basse-cour :
le poitrail bombé sous son plastron, un cou immense en S, le menton levé, le sourcil froncé, les ailes décollées
(elle est prête à pincer), les pieds en canard.

    python oie.py        fabrique la fiche art/apercus/animaux/oie.png
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

CORPS = Vector((0.0, 0.07, 0.385))
FIERE = A.repere(CORPS, (-16, 0, 0))          # le corps : le poitrail haut, le croupion bas
ORANGE = M.hexa("#ff7d1a")                    # le bec, les pattes, le tour de l'œil et tout le fil
PERLE = M.hexa("#c3ccdb")                     # le bout des ailes et de la queue : un gris de perle bleuté

# le cou : un grand S dessiné dans un plan debout, tourné de 15° vers sa droite (elle toise de côté, et de trois quarts
# on lit mieux le S). Chaque point : (ce qu'il avance, ce qu'il monte) depuis la base enfouie dans le poitrail.
BASE = Vector((0.0, -0.056, 0.525))
AVANT = Vector((-0.259, -0.966, 0.0))
FLANC = np.array([0.966, -0.259, 0.0])        # le côté gauche du cou, d'équerre avec le plan du S
S = [(0.0, 0.0), (0.14, 0.07), (0.215, 0.19), (0.15, 0.32), (0.035, 0.42), (0.0, 0.52), (0.06, 0.61), (0.15, 0.655)]
FIL = A.courbe([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in S], 8)
FAIT = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(FIL, axis=0), axis=1))])
SENS = np.gradient(FIL, FAIT, axis=0)
LONG = float(FAIT[-1])


def cadre(s):
    """En un point du fil du cou (s en mètres depuis la base) : le centre, la direction où il va, et sa nuque."""
    centre = np.stack([np.interp(s, FAIT, FIL[:, k]) for k in range(3)], axis=-1)
    avant = np.stack([np.interp(s, FAIT, SENS[:, k]) for k in range(3)], axis=-1)
    avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
    return centre, avant, np.cross(avant, FLANC)


def couche(v):
    """Couche une pièce tournée toute droite (son axe Z) le long du fil du cou : son +Y devient la nuque."""
    s = np.clip(v[:, 2], 0.0, LONG)
    centre, avant, nuque = cadre(s)
    return centre + avant * (v[:, 2] - s)[:, None] + v[:, 0:1] * FLANC + v[:, 1:2] * nuque


def vise(s, devant, cote, haut):
    """Depuis le centre du cou à la hauteur s : ce centre, et une direction (vers l'avant, vers la gauche, vers la nuque)."""
    centre, avant, nuque = cadre(s)
    return Vector(centre), Vector(avant * devant + FLANC * cote + nuque * haut)


def construire():
    a = K.Animal("oie")
    a.taille = 0.85
    F3 = FIERE.to_3x3()

    # ----- le corps : une barque dodue, le poitrail très bombé, le croupion étroit -----
    def coque(v):
        v = K.bosse(v, (0, -0.85, 0.25), 0.26, 0.35)
        arriere = K.lisse((v[:, 1] - 0.1) / 0.9)
        s = v * [0.205, 0.295, 0.205]
        s[:, 0] *= 1 - 0.45 * arriere
        s[:, 2] = s[:, 2] * (1 - 0.40 * arriere) + 0.06 * arriere
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    G.sillons(corps, [14], 0.005, 1.1)                  # la couture du dos creuse un peu le tissu
    a.piece("corps", corps, K.BLANC, mat=FIERE)
    a.couture("dos", "corps", 14, 0.56, 0.97, fil=ORANGE)
    # le plastron du gendarme : une bavette crème nouée sous le cou, tenue au point de feston
    a.rustine("plastron", "corps", CORPS + F3 @ Vector((0, -0.12, 0.0)), F3 @ Vector((0, -0.95, 0.05)),
              lambda th: 0.56 + 0.12 * math.sin(th), K.CREME, 0.003, 30, fil=ORANGE)

    # ----- le cou et la tête, d'une seule chaussette couchée le long du S ; la couture court sur toute la nuque -----
    pc = A.profil([(0, 0), (0.105, 0.02 * LONG), (0.090, 0.12 * LONG), (0.066, 0.28 * LONG), (0.057, 0.50 * LONG), (0.054, 0.70 * LONG),
                   (0.060, 0.80 * LONG), (0.078, 0.89 * LONG), (0.074, 0.945 * LONG), (0.050, 0.992 * LONG), (0, 1.012 * LONG)], 6)
    cou = A.tour(pc, 48)
    G.sillons(cou, [12], 0.004, 1.1)
    a.piece("cou", cou.sculpte(couche), K.BLANC)
    a.couture("nuque", "cou", 12, 0.20, 0.86, fil=ORANGE)
    centre, avant, nuque = cadre(0.93 * LONG)
    a.tete = Vector(centre + avant * 0.06 + FLANC * 0.03)

    # ----- les yeux : petits, haut placés, cerclés d'orange, sous un sourcil froncé qui plonge vers le bec -----
    for nom, cote in (("g", 1), ("d", -1)):
        milieu, regard = vise(0.905 * LONG, 0.22, 0.86 * cote, 0.40)
        a.rustine("cerne_" + nom, "cou", milieu, regard, 0.36, ORANGE, 0.003, 0)
        p, n = a.surface("cou", milieu, regard)
        a.bouton("oeil_" + nom, p + n * 0.0035, n, 0.019)
        sourcil = a.trace("cou", milieu, [vise(0.905 * LONG, d, c * cote, h)[1] for d, c, h in ((0.62, 0.62, 0.48), (0.25, 0.66, 0.72), (-0.10, 0.66, 0.80))], 0.005)
        a.broderie("sourcil_" + nom, A.courbe(sourcil, 5), 0.0036)

    # ----- le bec : long et fort, en feutrine orange ; son trait brodé retombe au coin (la moue) -----
    centre, avant, nuque = cadre(0.955 * LONG)
    B = A.cadre(Vector(centre - nuque * 0.008), Vector(avant), Vector(nuque))     # dans ce repère : X la gauche, Y le dessus, Z vers le bout
    B3 = B.to_3x3()
    bec = A.tour(A.profil([(0, 0), (0.050, 0.008), (0.048, 0.048), (0.037, 0.100), (0.028, 0.142), (0.019, 0.164), (0, 0.174)], 6), 36)
    a.piece("bec", bec.etire(1.0, 0.72, 1.0), ORANGE, mat=B, poil=False)
    for nom, cote in (("g", 1), ("d", -1)):
        moue = [a.trace("bec", B @ Vector((0, 0, z)), [B3 @ Vector((cote * math.cos(math.radians(d)), math.sin(math.radians(d)), 0))], 0.0015)[0]
                for z, d in ((0.158, -10), (0.136, -7), (0.112, -5), (0.090, -6), (0.070, -12), (0.056, -26))]
        a.broderie("moue_" + nom, A.courbe(moue, 4), 0.0024)

    # ----- les ailes décollées : un galet blanc qui ne tient que par l'épaule, trois rémiges de feutrine perle au bout -----
    def galet(v):
        s = K.emousse(v, 0.85)
        pointe = K.lisse((v[:, 1] + 0.1) / 1.1)
        s[:, 2] = s[:, 2] * (1 - 0.50 * pointe) + 0.15 * pointe
        return s
    AILE = FIERE @ A.repere((0.200, 0.035, 0.045), (4, -12, -11))      # l'avant affleure le flanc (sa couture reste visible), l'arrière s'écarte
    a.piece("aile", A.boule(1.0, 40, 20).sculpte(galet).etire(0.032, 0.225, 0.135), K.BLANC, mat=AILE, paire=True)
    for cote in (10, 30):
        a.couture("aile%d" % cote, "aile", cote, 0.12, 0.88, "droit", fil=ORANGE, paire=True)
    remiges = None
    for bas, degres in ((0.036, 12), (0.012, -6), (-0.014, -24)):
        t = math.radians(degres)
        plume = A.boule(1.0, 20, 10).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.015, 0.100, 0.036)
        plume.pose((0, 0.13 + 0.100 * math.cos(t), bas + 0.100 * math.sin(t)), (degres, 0, 0))
        remiges = plume if remiges is None else remiges + plume
    a.piece("remiges", remiges, PERLE, mat=AILE, poil=False, paire=True)

    # ----- la queue : trois pennes de feutrine perle, courtes, retroussées -----
    queue = None
    for degres in (-24, 0, 24):
        t = math.radians(degres)
        penne = A.boule(1.0, 20, 10).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.034, 0.090, 0.012)
        penne.pose((0.065 * math.sin(t), 0.065 * math.cos(t), 0), (0, 0, -degres))
        queue = penne if queue is None else queue + penne
    a.piece("queue", queue, PERLE, mat=FIERE @ A.repere((0, 0.245, 0.065), (38, 0, 0)), poil=False)

    # ----- les cuisses de peluche et les pattes orange : courtes, solides, le pied gauche en avant, les palmes en canard -----
    def palme(v):                                         # étroite au talon, large devant, le bord festonné par trois doigts
        s = v.copy()
        devant = K.lisse((0.3 - v[:, 1]) / 1.3)
        feston = 1 + 0.12 * np.cos(7.2 * np.arctan2(v[:, 0], -v[:, 1])) * devant
        s[:, 0] *= (0.45 + 0.75 * devant) * feston
        s[:, 1] *= feston
        return s
    for nom, cote, y in (("g", 1, -0.010), ("d", -1, 0.080)):
        a.piece("cuisse_" + nom, A.boule(1.0, 32, 16).etire(0.075, 0.085, 0.095), K.BLANC, pos=(0.110 * cote, y + 0.02, 0.265))
        patte = A.tube([(0, 0.012, 0.25), (0, 0.0, 0.02)], 0.026, 14) + A.boule(1.0, 48, 12).sculpte(palme).etire(0.072, 0.092, 0.014).pose((0, -0.046, 0.014))
        a.piece("patte_" + nom, patte, ORANGE, pos=(0.110 * cote, y, 0.0), rot=(0, 0, 14 * cote), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py oie)

from poses import Pose, borne, cloche, onde

# Le cou et la tête sont une seule chaussette couchée le long du S : une pièce souple que quatre os se partagent le
# long du fil (cou1 au sortir du poitrail, cou2 au plus avancé du bas du S, cou3 au creux de la nuque, tete en haut).
# Le pied du cou, enfoui dans le poitrail, suit cou1 : pour dormir, le cou se retourne de 165°, et un fondu avec le corps
# l'étranglerait. Passé 0,87 du fil, tout est à « tete », comme le bec, les yeux, leurs cernes et les sourcils. Le pied gauche est posé en avant : chaque patte a son os à elle (pas de
# miroir), et les pattes pendent à la racine, pas au corps : une palme posée ne bouge pas quand le corps roule.
_JALONS = (("cou1", 0.06), ("cou2", 0.35), ("cou3", 0.62), ("tete", 0.82))


def _au_fil(f):
    """Le centre du cou à la fraction f de sa longueur : le pivot d'un os."""
    return tuple(round(float(x), 3) for x in cadre(f * LONG)[0])


def _abscisse(points):
    """Pour chaque point : sa place le long du fil du cou (de 0 à 1), au pied de la perpendiculaire sur le tronçon le
    plus proche."""
    a, ab = FIL[:-1], np.diff(FIL, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    ap = points[:, None, :] - a[None, :, :]
    u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
    j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
    return (FAIT[j] + u[np.arange(len(points)), j] * np.sqrt(l2[j])) / LONG


def _relais(f, jalons, large):
    """Des os qui se passent la main le long d'un fil : chacun porte le tronçon qui suit son pivot, et cède au suivant
    en douceur sur ± large autour du pivot de celui-ci."""
    def marche(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3 - 2 * x)
    montees = [np.ones_like(f)] + [marche((f - f0 + large) / (2 * large)) for _o, f0 in jalons[1:]] + [np.zeros_like(f)]
    return {o: montees[i] - montees[i + 1] for i, (o, _f0) in enumerate(jalons)}


def _cou(points, cote):
    return _relais(_abscisse(points), _JALONS, 0.045)


OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.050, 0.280)),        # entre les cuisses : elle se dandine et se couche autour
    ("cou1", "corps", _au_fil(0.06)),                # le cou sort du poitrail
    ("cou2", "cou1", _au_fil(0.35)),                 # le plus avancé du bas du S
    ("cou3", "cou2", _au_fil(0.62)),                 # le creux de la nuque
    ("tete", "cou3", _au_fil(0.82)),                 # le haut du S : la tête part devant
    ("aile_G", "corps", (0.170, -0.048, 0.453)),     # l'épaule : l'aile ne tient que par là et part vers l'arrière
    ("queue", "corps", (0.0, 0.323, 0.380)),         # le croupion, d'où partent les trois pennes
    ("patte_g", "racine", (0.110, 0.010, 0.265)),    # la hanche, au cœur de la cuisse
    ("patte_d", "racine", (-0.110, 0.100, 0.265)),
]
PORTEURS = [("corps", "corps"), ("plastron", "corps"), ("dos", "corps"), ("cuisse", "corps"),
            ("cou", _cou, "tete"), ("nuque", _cou, "tete"),
            ("cerne", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("bec", "tete"), ("moue", "tete"),
            ("aile", "aile", True), ("remiges", "aile", True), ("queue", "queue"),
            ("patte_g", "patte_g"), ("patte_d", "patte_d"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _cou_pose(p, k, cou1, cou2, cou3, tete):
    """Le cou à une fraction k (0 à 1) d'une pose donnée os par os : (rx, rz) pour cou1 et la tête, rx pour cou2 et cou3."""
    p.add("cou1", rot=(cou1[0] * k, 0, cou1[1] * k))
    p.add("cou2", rot=(cou2 * k, 0, 0))
    p.add("cou3", rot=(cou3 * k, 0, 0))
    p.add("tete", rot=(tete[0] * k, 0, tete[1] * k))


def _ailes(p, leve):
    """Les deux ailes se décollent de « leve » degrés autour de l'épaule : le bout monte et s'écarte du corps."""
    p.paire("aile", rot=(0.55 * leve, -0.4 * leve, -0.6 * leve))


def _menace(p, k):
    """Le gendarme : le cou tendu en avant, bas et droit comme une lance, le bec pointé sur l'intrus, les ailes
    décollées. À la fraction k (0 à 1)."""
    _cou_pose(p, k, (85, 0), -30, -35, (-15, 0))
    p.add("corps", rot=(10 * k, 0, 0))
    _ailes(p, 16 * k)


def repos(t):
    """Plantée sur ses palmes, le poitrail en avant, elle monte la garde : elle respire, toise à droite puis à gauche
    en levant encore le menton ; puis le gendarme se fâche : elle tend le cou en lance vers l'intrus, ailes décollées,
    et siffle (le bec tremble), avant de se redresser, fière ; la queue frétille, elle cligne."""
    p = Pose()
    r = onde(t, 2)
    d, g = cloche(t, 0.14, 0.09), cloche(t, 0.30, 0.09)
    siffle = _plateau(t, 0.60, 0.07, 0.08)
    p.add("corps", ech=(1 + 0.012 * r, 1 + 0.008 * r, 1 + 0.018 * r))
    p.add("cou2", rot=(1.5 * r, 0, -6 * d + 6 * g))
    p.add("tete", rot=(-8 * (d + g), 0, -22 * d + 22 * g))
    _menace(p, siffle)
    p.add("tete", rot=(2.5 * onde(t, 24) * _plateau(t, 0.60, 0.05, 0.03), 0, 0))
    p.add("queue", rot=(0, 0, 14 * cloche(t, 0.86, 0.06) * onde(t, 8)))
    p.ouvert = borne(1 - cloche(t, 0.06, 0.02) - cloche(t, 0.42, 0.02) - cloche(t, 0.93, 0.02))
    return p


def _pas(p, nom, u, recule=0.045, leve=0.040):
    """Une patte à la phase u de son pas (0 : posée devant ; elle porte et glisse vers l'arrière jusqu'à 0,5 ; puis elle se
    lève et revient devant)."""
    s = math.sin(math.tau * u)
    en_l_air = max(0.0, -s)
    p.add(nom, rot=(-14 * en_l_air, 0, 0), pos=(0, -recule * math.cos(math.tau * u), leve * en_l_air))


def avance(t):
    """Elle se dandine, poitrail haut : à chaque pas le corps roule sur la patte qui porte et pivote un peu, la palme
    levée revient devant ; le cou pompe d'avant en arrière, la tête garde son cap, la queue balance."""
    p = Pose()
    s = math.sin(math.tau * t)
    _pas(p, "patte_g", t)
    _pas(p, "patte_d", t + 0.5)
    p.add("corps", rot=(0, 7 * s, 4 * s), pos=(0.012 * s, 0, 0.008 * (1 - math.cos(2 * math.tau * t)) / 2))
    p.add("cou1", rot=(4 + 4 * onde(t, 2), -5 * s, -3 * s))
    p.add("cou3", rot=(-3 * onde(t, 2, -0.1), 0, 0))
    p.add("tete", rot=(-4 * onde(t, 2), -4 * s, -2 * s))
    _ailes(p, 4 + 3 * abs(s))
    p.add("queue", rot=(0, 0, 10 * s))
    return p


def mange(t):
    """Elle broute : le cou plonge en s'allongeant jusqu'à l'herbe, quatre bouchées (le bec pique, puis arrache la touffe
    d'un coup sec vers l'arrière), puis elle relève la tête, droite et fière, pour avaler."""
    p = Pose()
    leve = cloche(t, 0.86, 0.14)
    bas = 1 - leve
    pique = max(0.0, onde(t, 4)) ** 2 * bas
    arrache = max(0.0, -onde(t, 4)) ** 2 * bas
    p.add("corps", rot=(18 * bas, 0, 0))
    _cou_pose(p, bas, (125, -6), -10, -30, (-30, -8))
    p.add("cou3", rot=(2 * pique - 4 * arrache, 0, 0))
    p.add("tete", rot=(5 * pique - 12 * arrache - 6 * leve * abs(onde(t, 6)), 0, 0))
    _ailes(p, 5 * bas)
    p.add("queue", rot=(0, 0, 8 * onde(t, 4) * bas))
    p.ouvert = borne(1 - cloche(t, 0.92, 0.03))
    return p


def joie(t):
    """Son triomphe : elle gonfle le poitrail, déploie grand les ailes et les bat à grands coups, le cou dressé et
    le bec au ciel (elle claironne), deux petits sauts sur place ; puis elle replie tout et reprend la garde."""
    p = repos(0.0)
    env = math.sin(math.pi * borne(t / 0.88)) if t < 0.88 else 0.0
    bat = onde(t, 4) * env
    saut = abs(onde(t, 2)) * env
    p.add("corps", rot=(-6 * env, 0, 0), pos=(0, 0, 0.035 * saut), ech=(1 + 0.03 * env, 1, 1 + 0.03 * env))
    for nom in ("patte_g", "patte_d"):
        p.add(nom, pos=(0, 0, 0.035 * saut), rot=(-8 * saut, 0, 0))
    _cou_pose(p, env, (0, 0), 20, -10, (-40, 0))
    p.add("tete", rot=(5 * onde(t, 6) * env, 0, 0))
    _ailes(p, 55 * env + 25 * bat)
    p.add("queue", rot=(10 * env, 0, 20 * onde(t, 7) * env))
    return p


def dort(t):
    """Couchée sur le ventre, les palmes dessous, le cou retourné par-dessus le dos et la tête posée dessus, le bec
    glissé dans les plumes du côté de l'aile gauche, les yeux fermés ; elle respire lentement, la tête monte et descend
    avec le dos."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.150), rot=(-4, 0, 0), ech=(1.03 + 0.012 * r, 1.0, 0.97 + 0.022 * r))
    _cou_pose(p, 1.0, (80, 165), -60, 30, (30, 0))
    p.add("cou2", rot=(1.5 * r, 0, 0))
    _ailes(p, 2 + 1.5 * r)
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Oie")
