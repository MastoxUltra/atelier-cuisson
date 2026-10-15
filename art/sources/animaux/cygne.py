"""Le cygne en peluche : un cygne NOIR, le plumage à reflets bleu nuit, le bec rouge vif barré de blanc près du bout,
l'œil cerclé de rouge. Souverain et ombrageux : posé comme sur l'eau, sans pattes, les ailes relevées en voile
au-dessus du dos, couvertes de languettes de feutrine frisées, un cou immense en S qui se referme sur lui-même,
le bec baissé contre le cou, la paupière en biais.

    python cygne.py        fabrique la fiche art/apercus/animaux/cygne.png
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

NOIR = M.hexa("#171a2c")                      # le plumage : un noir qui tire sur le bleu
NUIT = M.hexa("#263582")                      # les reflets bleu nuit : un rang sur deux des languettes des ailes
ROUGE = M.hexa("#e8212b")                     # le bec, le tour de l'œil et tout le fil
CORPS = Vector((0.0, 0.03, 0.118))
TOURNE = math.radians(0)                      # pour la fiche : -20 (le cou part vers sa droite, on lit mieux le S) ; 0 pour le jeu
AVANT = Vector((math.sin(TOURNE), -math.cos(TOURNE), 0.0))
FLANC = np.array([math.cos(TOURNE), math.sin(TOURNE), 0.0])      # le côté gauche du cou
BASE = Vector((0.0, -0.210, 0.200))           # le pied du cou, enfoui dans le poitrail
# le cou : chaque point (ce qu'il avance, ce qu'il monte) depuis la base. Il sort du poitrail, part en arrière, remonte,
# passe par-dessus et retombe : la tête pend, le bec revient contre le cou.
S = [(0.0, 0.0), (0.10, 0.04), (0.185, 0.13), (0.200, 0.26), (0.130, 0.39), (0.060, 0.50), (0.050, 0.62), (0.100, 0.72),
     (0.190, 0.765), (0.275, 0.720), (0.305, 0.630), (0.285, 0.555)]


class Fil:
    """Un chemin lissé, tenu dans un plan debout : de quoi coucher une pièce tournée le long d'un cou en S."""

    def __init__(self, points, flanc, pas=8):
        self.p = A.courbe(points, pas)
        self.fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(self.p, axis=0), axis=1))])
        self.sens = np.gradient(self.p, self.fait, axis=0)
        self.long = float(self.fait[-1])
        self.flanc = np.asarray(flanc, float)

    def cadre(self, s):
        """À s mètres de la base : le centre du fil, la direction où il va, et sa nuque (le dehors de la courbe en haut)."""
        centre = np.stack([np.interp(s, self.fait, self.p[:, k]) for k in range(3)], axis=-1)
        avant = np.stack([np.interp(s, self.fait, self.sens[:, k]) for k in range(3)], axis=-1)
        avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
        return centre, avant, np.cross(avant, self.flanc)

    def couche(self, v):
        """Couche une pièce tournée toute droite (son axe Z) le long du fil : son +X devient le flanc gauche, son +Y la nuque."""
        s = np.clip(v[:, 2], 0.0, self.long)
        centre, avant, nuque = self.cadre(s)
        return centre + avant * (v[:, 2] - s)[:, None] + v[:, 0:1] * self.flanc + v[:, 1:2] * nuque

    def vise(self, s, devant, cote, haut):
        """Depuis le centre du fil à la hauteur s : ce centre, et une direction (vers l'avant, vers la gauche, vers la nuque)."""
        centre, avant, nuque = self.cadre(s)
        return Vector(centre), Vector(avant * devant + self.flanc * cote + nuque * haut)


def rangs(plumes, impairs):
    """Un rang sur deux des languettes posées par G.franges (chacune : six points, deux faces), pour les couper dans
    deux feutrines unies. On les reconnaît à la teinte donnée à la pose : blanc pour les rangs impairs, noir pour les pairs."""
    garde = (plumes.teinte.reshape(-1, 6, 3)[:, 0].sum(axis=1) > 0.1) == impairs
    faces = []
    for i in range(int(garde.sum())):
        faces += [(6 * i, 6 * i + 1, 6 * i + 3, 6 * i + 2), (6 * i + 2, 6 * i + 3, 6 * i + 5, 6 * i + 4)]
    return A.Maille(plumes.v.reshape(-1, 6, 3)[garde].reshape(-1, 3), faces)


def construire():
    a = K.Animal("cygne")
    a.taille = 1.40

    # ----- le corps : une barque noire posée à plat, comme sur l'eau ; le poitrail plein, la queue relevée en pointe -----
    def coque(v):
        v = K.bosse(v, (0, -0.80, 0.30), 0.20, 0.35)
        arriere = K.lisse((v[:, 1] - 0.05) / 0.95)
        s = v * [0.215, 0.400, 0.190]
        s[:, 0] *= 1 - 0.55 * arriere
        s[:, 2] = np.where(s[:, 2] < 0, s[:, 2] * 0.62, s[:, 2])
        s[:, 2] = s[:, 2] * (1 - 0.40 * arriere) + 0.15 * arriere ** 1.5
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    G.sillons(corps, [14], 0.005, 1.1)
    a.piece("corps", corps, NOIR, pos=CORPS)

    # ----- le cou et la tête, d'une seule chaussette couchée le long du S ; la couture rouge court sur toute la nuque -----
    fil = Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in S], FLANC)
    L = fil.long
    pc = A.profil([(0, 0), (0.100, 0.02 * L), (0.086, 0.10 * L), (0.063, 0.24 * L), (0.051, 0.42 * L), (0.047, 0.62 * L),
                   (0.047, 0.78 * L), (0.053, 0.86 * L), (0.068, 0.925 * L), (0.061, 0.965 * L), (0.042, 0.995 * L), (0, 1.012 * L)], 6)
    cou = A.tour(pc, 48)
    G.sillons(cou, [12], 0.004, 1.1)
    a.piece("cou", cou.sculpte(fil.couche), NOIR)
    a.couture("nuque", "cou", 12, 0.22, 0.84, fil=ROUGE)
    centre, avant, nuque = fil.cadre(0.94 * L)
    a.tete = Vector(centre + FLANC * 0.05 + avant * 0.03)

    # ----- les yeux : un bouton noir sur un rond de feutrine rouge. Le rond est coupé droit du côté du front, en biais
    #       vers le bec : l'œil mauvais, sans une pièce de plus. (Autour de l'axe du regard, l'angle 0 est l'avant pour
    #       l'œil gauche et l'arrière pour le droit, un quart de tour plus loin c'est le bas.) -----
    for nom, c, front in (("G", 1, math.radians(28)), ("D", -1, math.radians(152))):
        milieu, regard = fil.vise(0.922 * L, 0.05, 0.94 * c, 0.30)
        a.rustine("cerne_" + nom, "cou", milieu, regard, lambda th, front=front: min(0.56, 0.27 / max(math.cos(th - front), 1e-3)), ROUGE, 0.003, 0)
        p, n = a.surface("cou", milieu, regard)
        a.bouton("oeil_" + nom, p + n * 0.0035, n, 0.023)

    # ----- le bec : rouge vif, barré d'une bande blanche avant le bout, en feutrine ; il pend, pointé vers le cou -----
    centre, avant, nuque = fil.cadre(0.962 * L)
    B = A.cadre(Vector(centre - nuque * 0.006), Vector(avant), Vector(nuque))    # X la gauche, Y le dessus du bec, Z vers le bout
    bec = A.tour(A.profil([(0, 0), (0.047, 0.008), (0.044, 0.048), (0.035, 0.100), (0.028, 0.142), (0.020, 0.166), (0, 0.178)], 6), 36)
    K.bandes(bec, [(0.112, ROUGE), (0.140, K.BLANC), (9, ROUGE)])
    a.piece("bec", bec.etire(1.0, 0.72, 1.0), None, mat=B, poil=False)

    # ----- les ailes en voile : une coque noire dressée de l'épaule à la queue, gonflée vers le dehors, et dessus des
    #       rangs de grandes languettes de feutrine frisées, le bout retroussé : un rang noir, un rang bleu nuit -----
    def voile(v):
        z, h = v[:, 2], v[:, 1]                           # z : de l'épaule (-1) à la pointe (+1) ; h : du bas au bord du haut
        s = np.empty_like(v)
        s[:, 2] = 0.33 * z
        s[:, 1] = np.where(h > 0, h * (0.15 + 0.21 * K.lisse(0.70 + 0.80 * z)), h * 0.10)
        s[:, 0] = v[:, 0] * 0.034 + 0.050 * (1 - h ** 2) * (1 - z ** 2)
        return s

    aile = A.boule(1.0, 40, 22).sculpte(voile)
    plumes = G.franges(aile, 0.125, 0.050, 0.060, 0.040, lambda rang, t: (rang % 2,) * 3, 5, 1, 0.03, 0.92)
    W = A.cadre((0.150, 0.110, 0.345), (-0.035, 0.870, 0.490), (0.42, -0.45, 0.80))    # Z le long de l'aile, Y le haut de la voile
    a.piece("aile", aile, NOIR, mat=W, paire=True)
    a.piece("plumes_noires", rangs(plumes, False), NOIR, mat=W, poil=False, paire=True)
    a.piece("plumes_nuit", rangs(plumes, True), NUIT, mat=W, poil=False, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py cygne)

from poses import Pose, borne, cloche, onde

# Le cou et la tête sont une seule chaussette couchée le long du S : une pièce souple, que quatre os se partagent le
# long du fil (cou1 au sortir du poitrail, cou2 dans la remontée, cou3 au creux de la nuque, tete en haut de la crosse).
# Passé 0,84 du fil, tout est à « tete », comme le bec, les yeux et leurs ronds rouges.
_FIL = Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in S], FLANC)
_JALONS = (("cou1", 0.12), ("cou2", 0.42), ("cou3", 0.62), ("tete", 0.80))


def _au_fil(f):
    """Le centre du cou à la fraction f de sa longueur : le pivot d'un os."""
    return tuple(round(float(x), 3) for x in _FIL.cadre(f * _FIL.long)[0])


def _abscisse(points, fil):
    """Pour chaque point : sa place le long du fil (de 0 à 1), au pied de la perpendiculaire sur le tronçon le plus proche."""
    a, ab = fil.p[:-1], np.diff(fil.p, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    ap = points[:, None, :] - a[None, :, :]
    u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
    j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
    return (fil.fait[j] + u[np.arange(len(points)), j] * np.sqrt(l2[j])) / fil.long


def _relais(f, jalons, large):
    """Des os qui se passent la main le long d'un fil : chacun porte le tronçon qui suit son pivot, et cède au suivant
    en douceur sur ± large autour du pivot de celui-ci."""
    def marche(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3 - 2 * x)
    montees = [np.ones_like(f)] + [marche((f - f0 + large) / (2 * large)) for _o, f0 in jalons[1:]] + [np.zeros_like(f)]
    return {o: montees[i] - montees[i + 1] for i, (o, _f0) in enumerate(jalons)}


def _cou(points, cote):
    return _relais(_abscisse(points, _FIL), _JALONS, 0.045)


OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.03, 0.06)),           # au ras de l'eau, au milieu de la barque : elle roule et tangue autour
    ("cou1", "corps", _au_fil(0.12)),                 # le cou sort du poitrail
    ("cou2", "cou1", _au_fil(0.42)),                  # la remontée
    ("cou3", "cou2", _au_fil(0.62)),                  # le creux de la nuque
    ("tete", "cou3", _au_fil(0.80)),                  # le haut de la crosse : la tête pend devant
    ("aile_G", "corps", (0.12, -0.13, 0.22)),         # l'épaule : la voile part de là vers l'arrière et vers le haut
]
PORTEURS = [("corps", "corps"), ("cou", _cou, "tete"), ("nuque", _cou, "tete"), ("cerne", "tete"), ("oeil", "tete"),
            ("bec", "tete"), ("aile", "aile", True), ("plumes", "aile", True),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _cou_tourne(p, k, cou1, cou2, cou3, tete):
    """Le cou à une fraction k (0 à 1) d'une pose donnée os par os : chaque angle est (rx, rz) pour les os du cou,
    (rx, rz) aussi pour la tête."""
    p.add("cou1", rot=(cou1[0] * k, 0, cou1[1] * k))
    p.add("cou2", rot=(cou2 * k, 0, 0))
    p.add("cou3", rot=(cou3 * k, 0, 0))
    p.add("tete", rot=(tete[0] * k, 0, tete[1] * k))


def repos(t):
    """Posé comme sur l'eau, il flotte : la barque roule et tangue à peine, il respire, toise à gauche puis à droite ;
    puis il retourne le cou par-dessus l'épaule gauche, couche la tête sur son dos et lisse les plumes de ses voiles
    à petits coups de bec ; il cligne."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.15, 0.10), cloche(t, 0.32, 0.08)
    lisse = _plateau(t, 0.66, 0.11, 0.10)
    picore = onde(t, 18) * _plateau(t, 0.66, 0.09, 0.03)
    p.add("corps", rot=(1.0 * onde(t, 1, 0.25), 1.5 * onde(t, 1), 0), ech=(1 + 0.010 * r, 1, 1 + 0.016 * r))
    p.add("cou1", rot=(2 * onde(t, 1), 0, 6 * g - 6 * d))
    p.add("cou2", rot=(0, 0, 10 * g - 10 * d))
    p.add("tete", rot=(2 * r, 0, 16 * g - 16 * d))
    _cou_tourne(p, lisse, (-15, 100), 80, 30 + 5 * picore, (70 + 10 * picore, -60))
    p.add("aile_G", rot=(0, 5 * lisse, 0))
    p.ouvert = borne(1 - cloche(t, 0.06, 0.02) - cloche(t, 0.44, 0.02) - 0.45 * lisse)
    return p


def avance(t):
    """Il glisse : la barque ne monte ni ne descend, elle roule à peine à chaque poussée des pattes cachées ; le cou,
    un peu penché, ondule d'avant en arrière, la vague passant de la base à la tête, qui garde le cap."""
    p = Pose()
    p.add("corps", rot=(0.8 * onde(t, 2), 1.2 * onde(t, 1), 1.0 * onde(t, 1, 0.25)), pos=(0, -0.004 * onde(t, 2), 0.002 * onde(t, 2)))
    p.add("cou1", rot=(6 + 6 * onde(t, 1), 0, -1.5 * onde(t, 1, 0.25)))
    p.add("cou2", rot=(-7 * onde(t, 1, -0.15), 0, 0))
    p.add("cou3", rot=(6 * onde(t, 1, -0.30), 0, 0))
    p.add("tete", rot=(-6 - 5 * onde(t, 1, -0.45), 0, 1.5 * onde(t, 1, 0.25)))
    p.paire("aile", rot=(0, 2 * onde(t, 2), 0))
    return p


def mange(t):
    """Il broute : le cou s'arrondit et plonge devant le poitrail, le bec au ras de l'herbe ; quatre coups de bec,
    puis il relève la tête pour avaler."""
    p = Pose()
    leve = cloche(t, 0.84, 0.16)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add("corps", rot=(3 * bas, 0, 0), pos=(0, 0, 0.004 * bas))
    _cou_tourne(p, bas, (10, 0), 120, -40 - 4 * coups, (-60 + 12 * coups, 0))
    p.add("tete", rot=(-5 * leve * onde(t, 6), 0, 0))
    p.paire("aile", rot=(0, -3 * bas, 0))
    p.ouvert = borne(1 - cloche(t, 0.90, 0.03))
    return p


def joie(t):
    """Sa parade : il se hausse, gonfle le poitrail, dresse le cou tout droit le bec au ciel, ouvre ses deux voiles en
    éventail et les bat trois fois en se tournant de gauche à droite ; puis il se recompose, souverain."""
    p = repos(0.0)
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    bat = onde(t, 3) * env
    p.add("corps", rot=(-6 * env, 0, 8 * onde(t, 1) * env), pos=(0, 0, 0.02 * env), ech=(1 + 0.03 * env, 1, 1 + 0.03 * env))
    _cou_tourne(p, env, (-10, 0), -25, -35, (-60, 0))
    p.paire("aile", rot=(-6 * env, 28 * env + 16 * bat, 0))
    return p


def dort(t):
    """Il dort la tête sous l'aile : le cou retourné par-dessus l'épaule gauche, la tête couchée sur le dos, le bec
    glissé entre ses deux voiles ; il respire lentement, la tête monte et descend avec le dos."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", ech=(1.02 + 0.012 * r, 1.0, 0.98 + 0.02 * r))
    _cou_tourne(p, 1.0, (-12, 110), 75 + 2 * r, 30, (75, -55))
    p.paire("aile", rot=(0, -2 + 1.5 * r, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Cygne")
