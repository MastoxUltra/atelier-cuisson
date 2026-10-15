"""La limace en peluche, deuxième dessin : la grande limace rouge des jardins, une flâneuse. Un long corps de peluche
saumon, haut et dodu, plissé en long comme un édredon piqué, qui ondule en S dans l'herbe ; l'avant se dresse et
s'étire vers le ciel, le nez au vent. Sur ses épaules, le manteau : une selle rouille, bombée, plus large que le corps,
dont le bord se décolle ; sur son flanc, l'œillet de la respiration, une pastille bleu nuit cousue de crème. Le tour du
pied est un liseré crème rayé de bleu nuit. Les yeux au bout de deux longues antennes : l'une se penche vers vous,
curieuse, l'autre regarde ailleurs ; des paupières mi-closes, l'air de quelqu'un qui a tout son temps.

    python limace.py        fabrique la fiche art/apercus/animaux/limace.png
    (le premier dessin, jamais gardé : limace_ancien.py)
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

SAUMON = M.hexa("#ff9e78")                    # le corps : un saumon franc, orangé (le ver de terre garde le rose pêche)
ROUILLE = M.hexa("#b8512c")                   # le manteau, les antennes
CREME = M.hexa("#ffe6cf")                     # le liseré du pied, le fil
NUIT = M.hexa("#27305c")                      # l'accent : l'œillet, les rayures du liseré
COTES = 56

# Le fil du corps, de la queue au nez : un S couché dans l'herbe, puis l'avant qui se dresse vers le ciel.
TRACE = [(0.046, 0.262), (0.026, 0.200), (-0.006, 0.130), (-0.020, 0.060), (-0.008, -0.010), (0.012, -0.072), (0.020, -0.128),
         (0.016, -0.178)]
_xy = A.courbe(TRACE, 10)
_t = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(_xy, axis=0), axis=1))])
_t /= _t[-1]


def rayon_t(t):
    """Le rayon du corps à la fraction t de sa longueur : la queue effilée, le ventre plein, le cou, le nez bien rond."""
    t = np.asarray(t, float)
    r = 0.050 * np.minimum(1.0, (t / 0.42) ** 0.62)
    r = r * (1 - 0.20 * K.lisse((t - 0.80) / 0.14))
    nez = 0.075
    return r * np.sqrt(np.clip(1 - (np.maximum(t - (1 - nez), 0.0) / nez) ** 2, 0.0, 1.0))


def ventre_t(t):
    """Où le ventre est coupé à plat sous l'axe, en rayons : posé au sol à l'arrière, tout rond sur le cou dressé."""
    return 0.56 + 0.44 * K.lisse((np.asarray(t, float) - 0.74) / 0.12)


def leve_t(t):
    """De combien l'avant se soulève : le cou se dresse au sortir du manteau."""
    return 0.062 * K.lisse((np.asarray(t, float) - 0.76) / 0.24) ** 1.3


FIL = np.stack([_xy[:, 0], _xy[:, 1], ventre_t(_t) * rayon_t(_t) + leve_t(_t) - 0.001], axis=1)
FAIT = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(FIL, axis=0), axis=1))])
SENS = np.gradient(FIL, FAIT, axis=0)
LONG = float(FAIT[-1])


def rayon(s):
    return rayon_t(np.interp(s, FAIT, _t))


def repere(s):
    """En un point du fil : le centre, la direction où il va, le dos (vers le ciel) et le flanc gauche."""
    centre = np.stack([np.interp(s, FAIT, FIL[:, k]) for k in range(3)], axis=-1)
    avant = np.stack([np.interp(s, FAIT, SENS[:, k]) for k in range(3)], axis=-1)
    avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
    dos = np.array([0.0, 0.0, 1.0]) - avant[..., 2:3] * avant
    dos = dos / np.linalg.norm(dos, axis=-1, keepdims=True)
    return centre, avant, dos, np.cross(dos, avant)


def couche(v):
    """Couche une pièce tournée toute droite le long du fil : son +X devient le flanc gauche, son +Y le dos."""
    s = np.clip(v[:, 2], 0.0, LONG)
    centre, avant, dos, flanc = repere(s)
    return centre + avant * (v[:, 2] - s)[:, None] + v[:, 0:1] * flanc + v[:, 1:2] * dos


def troncon(fraction, large, bas, haut, jusque=1.0, plis=()):
    """Un boudin tourné de la queue au nez (ou jusqu'à la fraction « jusque » du corps), à la section de limace :
    plus large que haut, le ventre à plat là où il est posé. large : l'élargissement ; bas et haut : où la section est
    coupée, en rayons sous l'axe (bas=None : le ventre du corps)."""
    fin = float(np.interp(jusque, _t, FAIT))
    pas = np.linspace(0.0, fin, int(220 * jusque))
    ferme = (lambda s: 1.0) if jusque >= 1.0 else (lambda s: math.sqrt(max(0.0, 1 - (max(s - (fin - 0.020), 0.0) / 0.020) ** 2)))
    prof = [(0.0, 0.0)] + [(float(rayon(s)) * fraction * ferme(s), float(s)) for s in pas[1:-1]] + [(0.0, fin)]
    m = A.tour(prof, COTES)

    def section(v):
        r = np.maximum(rayon(v[:, 2]), 1e-4)
        t = np.interp(v[:, 2], FAIT, _t)
        dessous = ventre_t(t) if bas is None else bas
        s = v.copy()
        if plis:                                          # les plis en long, qui s'effacent vers la queue et le cou
            angle = np.arctan2(v[:, 1], v[:, 0]) * COTES / (2 * math.pi)
            creux = np.zeros(len(v))
            for c in plis:
                d = np.abs(angle - c) % COTES
                creux += np.exp(-(np.minimum(d, COTES - d) / 1.2) ** 2)
            fondu = K.lisse((t - 0.04) / 0.10) * K.lisse((0.84 - t) / 0.08)
            s[:, :2] *= (1 - np.minimum(creux, 1.0) * fondu * np.minimum(0.0050 / r, 0.25))[:, None]
        s[:, 0] *= large
        s[:, 1] = np.clip(v[:, 1], -dessous * r, haut * r)
        return s
    return m.sculpte(section)


def construire():
    a = K.Animal("limace")
    a.taille = 0.44

    # ----- le corps : haut et dodu, le ventre à plat, piqué de deux plis en long sur chaque flanc et d'une couture
    #       sur l'échine -----
    corps = troncon(1.0, 1.16, None, 9.0, plis=(8, 14, 20))
    a.piece("corps", corps.sculpte(couche), SAUMON)
    a.couture("echine", "corps", 14, 0.06, 0.56, "droit", fil=ROUILLE, large=0.007, haut=0.0028, pas=0.013)
    # un rapiéçage crème sur le flanc de la queue, au point de feston
    centre, avant, dos, flanc = (Vector(q) for q in repere(0.26 * LONG))
    a.rustine("rapiecage", "corps", centre, flanc * 0.85 + dos * 0.45, 0.34, CREME, 0.003, 14, fil=ROUILLE)

    # ----- le pied : un liseré de feutrine crème qui dépasse sous le corps, rayé de bleu nuit -----
    pied = troncon(1.0, 1.30, 0.56, -0.40, 0.74)
    rayure = np.sin(pied.v[:, 2] * 2 * math.pi / 0.016) > 0.55
    pied.teinte = np.where(rayure[:, None], np.asarray(NUIT), np.asarray(CREME))
    a.piece("pied", pied.sculpte(couche), None, poil=False)

    # ----- le manteau : une selle rouille sur les épaules, plus large que le corps, le bord qui se décolle ;
    #       une couture au milieu, et l'œillet de la respiration sur le flanc -----
    sm = float(np.interp(0.66, _t, FAIT))
    c, av, do, fl = repere(sm)
    rm = float(rayon(sm))

    def selle(v):
        u = v.copy()
        u[:, 1] = np.maximum(u[:, 1], -0.30)                  # coupée à plat dessous, dans le corps
        u = K.bosse(u, (0, 1, 0), 0.22, 0.5)
        x, y, z = u[:, 0] * rm * 1.34, u[:, 1] * rm * 1.16 + 0.20 * rm, u[:, 2] * 0.068
        return c + np.outer(x, fl) + np.outer(y, do) + np.outer(z, av)
    manteau = A.boule(1.0, 56, 28).sculpte(selle)
    a.piece("manteau", manteau, ROUILLE)
    a.couture("manteau", "manteau", 14, 0.16, 0.84, "droit", fil=CREME, large=0.008, haut=0.0035, pas=0.012)
    milieu = Vector(c + do * 0.25 * rm)
    a.rustine("oeillet", "manteau", milieu, Vector(fl * 0.86 + do * 0.30 + av * 0.10), 0.20, NUIT, 0.004, 12, fil=CREME)

    # ----- la tête, au bout du cou dressé : deux longues antennes, une boule au bout, l'œil et sa paupière lourde ;
    #       celle de gauche se penche vers nous, celle de droite regarde ailleurs -----
    st = LONG - 0.030
    c, av, do, fl = (Vector(q) for q in repere(st))
    a.tete = c + av * 0.020 + Vector((0, 0, 0.034))
    #       (le coude et le bout sont donnés dans le jardin : vers sa gauche, vers l'avant, vers le ciel)
    for nom, cote, coude, bout in (("G", 1, (0.014, 0.012, 0.040), (0.040, 0.030, 0.074)),
                                   ("D", -1, (0.012, -0.002, 0.044), (0.034, -0.014, 0.082))):
        p, n = a.surface("corps", c, av * 0.30 + fl * (0.42 * cote) + do * 0.86)
        mi = p + Vector((coude[0] * cote, -coude[1], coude[2]))
        fin = p + Vector((bout[0] * cote, -bout[1], bout[2]))
        tige = A.tube(A.courbe([tuple(p - n * 0.006), tuple(mi), tuple(fin)], 8), lambda t: 0.0085 - 0.0030 * t, 12)
        sens = (fin - mi).normalized()
        boule = fin + sens * 0.006
        a.piece("antenne_" + nom, tige + A.boule(1.0, 24, 12).etire(0.0135).pose(tuple(boule)), ROUILLE)
        regard = (sens + (Vector((0.40, -0.92, 0.10)) if cote > 0 else fl * -0.6 + do * 0.3)).normalized()
        q = boule + regard * 0.0135
        a.oeil("oeil_" + nom, q + regard * 0.0015, regard, 0.0108)
        a.piece("lourde_" + nom, K.paupiere(0.0108, 0.25 if cote > 0 else 0.10), ROUILLE,
                mat=A.cadre(q + regard * 0.0025, regard, Vector((0, 0, 1))), poil=False)
    # une bouche gourmande, en coin
    bouche = [av * 0.96 + fl * x + do * y for x, y in ((-0.30, -0.36), (-0.12, -0.42), (0.08, -0.42), (0.26, -0.32))]
    a.broderie("bouche", A.courbe(a.trace("corps", c, bouche, 0.0040), 4), 0.0026, ROUILLE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py limace). Les mesures sont celles du modèle, avant a.taille.
# Le corps est un seul boudin souple que cinq os se passent le long de son fil : du « corps », sous le manteau, une
# chaîne part vers la queue, une autre vers le cou qui se dresse et la tête. Le pied, le manteau et tout ce qui y est
# cousu suivent le même fil. Les deux antennes ne sont pas symétriques (l'une se penche vers nous, l'autre regarde
# ailleurs) : chacune a son os, nommé à la main à sa vraie place, à la base de sa tige.

from poses import Pose, borne, cloche, onde

# chaque os du boudin et sa place le long du corps (en fraction de sa longueur, depuis la queue)
NOMS = ["queue2", "queue1", "corps", "cou", "tete"]
OU = np.interp([0.15, 0.35, 0.55, 0.74, 0.86], _t, FAIT)
MILIEU = 2
PARENT = ["racine" if k == MILIEU else NOMS[k + 1] if k < MILIEU else NOMS[k - 1] for k in range(len(NOMS))]
_PIVOTS = repere(OU)[0]

OS = ([("racine", None, (0, 0, 0))]
      + [(NOMS[k], PARENT[k], tuple(round(float(x), 4) for x in _PIVOTS[k])) for k in (2, 1, 0, 3, 4)]
      + [("antenne_g", "tete", (0.026, -0.184, 0.103)),      # le pied de chaque tige, enfoncé dans le front
         ("antenne_d", "tete", (0.004, -0.181, 0.103))])


def _abscisse(points):
    """Pour chaque point : sa place le long du fil, au pied de la perpendiculaire sur le tronçon le plus proche."""
    a, ab = FIL[:-1], np.diff(FIL, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    s = np.empty(len(points))
    for d in range(0, len(points), 2000):
        q = points[d:d + 2000]
        ap = q[:, None, :] - a[None, :, :]
        u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
        j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
        s[d:d + 2000] = FAIT[j] + u[np.arange(len(q)), j] * (FAIT[j + 1] - FAIT[j])
    return s


def souple(points, cote):
    """Le boudin et ce qui le couvre : chaque point se partage en douceur entre les deux os qui l'encadrent le long
    du fil ; le bout de la queue suit « queue2 », le nez suit « tete »."""
    s = np.clip(_abscisse(points), OU[0], OU[-1])
    j = np.clip(np.searchsorted(OU, s, side="right") - 1, 0, len(OU) - 2)
    f = K.lisse((s - OU[j]) / (OU[j + 1] - OU[j]))
    return {n: np.where(j == k, 1 - f, 0.0) + np.where(j + 1 == k, f, 0.0) for k, n in enumerate(NOMS)}


def antenne(points, cote):
    """Une antenne, son œil et sa paupière : tout entière sur l'os de son côté (nommé à la main, sans miroir)."""
    return {"antenne_g" if cote == "_G" else "antenne_d": np.ones(len(points))}


# « oeillet » avant « oeil » : le premier qui correspond gagne
PORTEURS = [("corps", souple, "corps"), ("echine", souple, "corps"), ("rapiecage", souple, "corps"), ("pied", souple, "corps"),
            ("manteau", souple, "corps"), ("oeillet", souple, "corps"), ("bouche", souple, "corps"),
            ("antenne", antenne), ("oeil", antenne), ("lourde", antenne),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]

BAISSE = (18.0, 12.0)                         # mange : de combien le cou et la tête plongent vers l'herbe


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def repos(t):
    """Elle a tout son temps : le corps respire, l'avant se balance lentement au vent ; l'antenne gauche se penche vers
    nous, curieuse, pendant que la droite fouille ailleurs, puis elles échangent ; la droite se rétracte à moitié,
    hésite et ressort ; elle cligne lentement sous ses paupières lourdes."""
    p = Pose()
    r = onde(t, 2)
    p.add("corps", ech=(1 + 0.015 * r, 1, 1 + 0.025 * r))
    p.add("cou", rot=(1.5 * r, 0.8 * onde(t, 1), 4 * onde(t, 1, 0.1)))
    p.add("tete", rot=(0, -2 * onde(t, 1, 0.2), 0))
    vers_nous = cloche(t, 0.22, 0.14)
    ailleurs = cloche(t, 0.62, 0.14)
    rentre = cloche(t, 0.82, 0.06)
    p.add("antenne_g", rot=(14 * vers_nous - 6 * ailleurs + 4 * onde(t, 2), 0, 10 * vers_nous))
    p.add("antenne_d", rot=(-8 * vers_nous + 12 * ailleurs + 4 * onde(t, 2, 0.3), 0, -14 * ailleurs),
          ech=(1, 1, 1 - 0.45 * rentre))
    p.add("queue2", rot=(0, 0, 6 * onde(t, 1)))
    p.ouvert = 1 - cloche(t, 0.10, 0.03) - cloche(t, 0.46, 0.03)
    return p


def avance(t):
    """Elle glisse : l'avant s'étire vers l'avant, puis le reste du corps suit, en une vague lente qui court du cou à
    la queue sur son pied posé à plat ; la tête dodeline, les antennes se balancent au rythme de la glisse."""
    p = Pose()
    s, c = math.sin(math.tau * t), math.cos(math.tau * t)
    p.add("cou", pos=(0, -0.010 * (0.5 + 0.5 * s), 0.002 * c), rot=(2 * c, 0, 0))
    p.add("tete", pos=(0, -0.006 * (0.5 + 0.5 * onde(t, 1, -0.1)), 0), rot=(0, 0, 3 * onde(t, 1, 0.25)))
    p.add("queue1", pos=(0, -0.008 * (0.5 + 0.5 * onde(t, 1, -0.25)), 0))
    p.add("queue2", pos=(0, -0.006 * (0.5 + 0.5 * onde(t, 1, -0.40)), 0), rot=(0, 0, 4 * onde(t, 1, -0.4)))
    p.add("corps", ech=(1 - 0.015 * s, 1, 1 + 0.02 * onde(t, 1, -0.15)))
    p.add("antenne_g", rot=(6 * s, 0, 3 * c))
    p.add("antenne_d", rot=(6 * onde(t, 1, 0.15), 0, -3 * c))
    return p


def mange(t):
    """L'avant plonge jusqu'à la feuille, la tête râpe à petits coups (quatre), les antennes se couchent en arrière ;
    puis elle se redresse, savoure, et une antenne se rallonge la première."""
    p = Pose()
    bas = _plateau(t, 0.42, 0.26, 0.14)
    coups = max(0.0, onde(t, 8)) ** 2 * _plateau(t, 0.42, 0.20, 0.06)
    p.add("cou", rot=(BAISSE[0] * bas, 0, 2 * onde(t, 2) * bas), pos=(0, 0, 0.006 * bas))
    p.add("tete", rot=(BAISSE[1] * bas + 6 * coups, 0, 0), pos=(0, -0.004 * coups, 0))
    p.add("antenne_g", rot=(-26 * bas, 0, 0), ech=(1, 1, 1 - 0.25 * bas))
    p.add("antenne_d", rot=(-22 * bas, 0, 0), ech=(1, 1, 1 - 0.25 * _plateau(t, 0.40, 0.26, 0.14)))
    p.add("queue2", rot=(0, 0, 4 * onde(t, 1)))
    p.ouvert = 1 - cloche(t, 0.90, 0.03)
    return p


def joie(t):
    """Sa fête, au ralenti : elle se dresse tant qu'elle peut, les antennes s'allongent et saluent l'une après l'autre,
    l'avant se balance de gauche à droite, le bout de la queue frétille ; puis elle redescend sans se presser."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    balance = onde(borne(t / 0.9), 2) * env
    p.add("cou", rot=(-16 * env, 6 * balance, 0), pos=(0, 0, 0.010 * env))
    p.add("tete", rot=(-8 * env, 4 * balance, 0))
    p.add("antenne_g", rot=(18 * onde(t, 3) * env, 10 * env, 0), ech=(1, 1, 1 + 0.25 * env))
    p.add("antenne_d", rot=(18 * onde(t, 3, 0.5) * env, -10 * env, 0), ech=(1, 1, 1 + 0.25 * env))
    p.add("queue2", rot=(0, 0, 18 * onde(t, 6) * env))
    p.add("queue1", rot=(0, 0, 5 * balance))
    return p


def dort(t):
    """L'avant redescend se poser à plat dans l'herbe, les antennes rentrées presque tout entières, les yeux fermés ;
    la queue se ramène un peu contre elle ; le corps se gonfle et se dégonfle lentement, comme un édredon."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", ech=(1 + 0.02 * r, 1, 1 + 0.03 * r), pos=(0, 0, 0.001 + 0.001 * r))
    p.add("cou", rot=(14, 0, 4), pos=(0, 0, 0.005))
    p.add("tete", rot=(10, 0, 0))
    p.add("antenne_g", rot=(-20, 0, 0), ech=(0.45, 0.45, 0.40))
    p.add("antenne_d", rot=(-16, 0, 0), ech=(0.45, 0.45, 0.40))
    p.add("queue2", rot=(0, 0, 14))
    p.add("queue1", rot=(0, 0, 6))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Limace")
