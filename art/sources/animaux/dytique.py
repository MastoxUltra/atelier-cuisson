"""Le dytique en peluche, deuxième dessin : le requin de la mare, sous ses airs de bijou. Une goutte large et basse,
en feutrine lie-de-vin lisse comme une laque, cerclée tout autour d'un passepoil d'or, fendue au milieu par une couture
d'or ; un corselet et une tête de velours du même vin, le corselet bordé d'or sur les côtés. Ses deux grandes rames
caramel frangées de crème partent en arrière, l'une levée en plein coup d'aviron. Il pique du nez, la tête tournée
vers nous, l'œil mi-clos du chasseur et un sourire en coin brodé d'or : il a repéré quelque chose de bon à manger.

    python dytique.py        fabrique la fiche art/apercus/animaux/dytique.png
    (le premier dessin, refusé le 14/10 : dytique_ancien.py)
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

VIN = M.hexa("#7a1f35")                       # les élytres, en feutrine lisse : un lie-de-vin laqué
VELOURS = M.hexa("#9c3b52")                   # le corselet et la tête, en velours (le poil le fonce vers le vin)
OR = M.hexa("#e8b23a")                        # l'accent : le passepoil, la couture, le sourire
CARAMEL = M.hexa("#c7854a")                   # les pattes et les rames
POSE = A.repere((0, 0, 0.004), (7, 0, 0))     # il pique du nez
TETE = Vector((0.0, -0.090, 0.040))
PORT = POSE @ A.repere(TETE, (6, 0, 16))      # la tête basse, tournée vers nous
CENTRE_TETE = PORT @ Vector((0, 0, 0))


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête, rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def ici(x, y, z):
    """Un point du corps (avant qu'il pique du nez), rendu dans le jardin."""
    return POSE @ Vector((x, y, z))


def rame(base, direction, long, large):
    """Le contour d'une rame : un manche étroit à la racine, une pale qui s'élargit, le bout arrondi."""
    return A.courbe([(0.0, 0.0), (large * 0.35, 0.004), (large * 0.70, long * 0.35), (large, long * 0.72), (large * 0.70, long * 0.96),
                     (0.0, long), (-large * 0.55, long * 0.92), (-large * 0.80, long * 0.66), (-large * 0.30, long * 0.30),
                     (-large * 0.30, 0.004)], 5, fermee=True)


def construire():
    a = K.Animal("dytique")
    a.taille = 0.34
    a.tete = PORT @ Vector((0, -0.026, 0.002))

    # ----- les élytres : une goutte large, plus large derrière, plate dessous ; un passepoil d'or tout autour du bord,
    #       une couture d'or qui la fend du cou au bout -----
    def goutte(v):
        s = v.copy()
        s[:, 0] *= 0.058 * (1 + 0.10 * v[:, 1])
        s[:, 1] *= 0.082
        s[:, 2] = np.where(v[:, 2] > 0, v[:, 2] * 0.034, v[:, 2] * 0.012)
        return s
    elytres = K.bandes(A.boule(1.0, 56, 28).sculpte(goutte), [(0.0035, OR), (9, VIN)])
    G.sillons(elytres, [14, 42], 0.004, 1.2)
    a.piece("elytres", elytres, None, mat=POSE @ A.repere((0, 0.028, 0.046)), poil=False)
    a.couture("suture", "elytres", 14, 0.52, 0.99, "droit", fil=OR, large=0.010, haut=0.0015, pas=0.015)
    a.couture("suture2", "elytres", 42, 0.70, 0.99, "droit", fil=OR, large=0.010, haut=0.0015, pas=0.015)

    # ----- le corselet : un bourrelet de velours qui coiffe l'avant de la goutte, bordé d'or sur les deux côtés -----
    corselet = A.boule(1.0, 48, 24)
    bord = np.abs(corselet.v[:, 0]) > 0.82
    corselet.sculpte(lambda v: np.stack([v[:, 0] * 0.050, v[:, 1] * 0.026, np.where(v[:, 2] > 0, v[:, 2] * 0.026, v[:, 2] * 0.011)], axis=1))
    corselet.teinte = np.where(bord[:, None], np.asarray(OR), np.asarray(VELOURS))
    a.piece("corselet", corselet, None, mat=POSE @ A.repere((0, -0.058, 0.047), (8, 0, 0)))

    # ----- la tête : large et courte, enfoncée sous le corselet ; l'œil mi-clos, un sourire en coin brodé d'or -----
    def caboche(v):
        return K.emousse(K.bosse(v, (0, -1, -0.2), 0.10, 0.25), 0.90) * [0.036, 0.024, 0.020]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(caboche), VELOURS, mat=PORT)
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", CENTRE_TETE, vers(0.62 * cote, -0.60, 0.42))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0105)
        a.piece("lourde_" + nom, K.paupiere(0.0105, 0.18), VIN, mat=A.cadre(p + n * 0.003, n, vers(0, 0.15, 1)), poil=False)
        # les antennes : deux fils caramel, fins, qui partent en arc vers l'avant
        p, n = a.surface("tete", CENTRE_TETE, vers(0.80 * cote, -0.30, 0.50))
        fil = A.courbe([p - n * 0.003, p + vers(0.012 * cote, -0.010, 0.012), p + vers(0.030 * cote, -0.030, 0.018),
                        p + vers(0.046 * cote, -0.046, 0.012)], 6)
        a.piece("antenne_" + nom, A.tube(fil, lambda t: 0.0030 - 0.0008 * t, 12), CARAMEL, poil=False)
    sourire = a.trace("tete", CENTRE_TETE, [vers(x, -0.95, z) for x, z in ((0.48, 0.04), (0.26, -0.13), (0.02, -0.19), (-0.18, -0.19))])
    a.broderie("sourire", A.courbe(sourire, 4), 0.0022, OR)

    # ----- les pattes : quatre courtes, caramel, sous l'avant ; deux grandes rames qui partent en arrière, la gauche levée
    #       en plein coup d'aviron, chacune frangée de crème -----
    for cote, nom in ((1, "pattes_G"), (-1, "pattes_D")):
        pattes = None
        for chemin in ([ici(0.032 * cote, -0.070, 0.034), ici(0.058 * cote, -0.088, 0.030), Vector((0.066 * cote, -0.108, 0.008)),
                        Vector((0.072 * cote, -0.116, 0.004))],
                       [ici(0.042 * cote, -0.026, 0.032), ici(0.076 * cote, -0.030, 0.034), Vector((0.088 * cote, -0.012, 0.008)),
                        Vector((0.094 * cote, -0.004, 0.004))]):
            une = A.tube(A.conges(chemin, 0.008, 5), lambda t: 0.0068 * (1 - 0.35 * t), 12)
            pattes = une if pattes is None else pattes + une
        a.piece(nom, pattes, CARAMEL, poil=False)
    for nom, cote, monte, vise in (("G", 1, 0.20, 0.50), ("D", -1, 0.06, 0.40)):
        hanche, genou = ici(0.040 * cote, 0.010, 0.034), ici(0.086 * cote, 0.030, 0.044)
        a.piece("cuisse_" + nom, A.tube(A.conges([hanche, genou], 0.006, 3), lambda t: 0.0075 * (1 - 0.15 * t), 12), CARAMEL, poil=False)
        d = Vector((vise * cote, 0.88, monte)).normalized()
        n = (Vector((0, 0, 1)) - d * d.z).normalized()
        rep = A.cadre(genou, n, d)
        a.piece("rame_" + nom, A.decoupe(rame(genou, d, 0.100, 0.011 * cote), 0.0040, 0.0012), CARAMEL, mat=rep, poil=False)
        # la frange : une seconde pale de crème, plus large, glissée dessous et décalée vers le bord de fuite (vers le corps)
        frange = A.decoupe(rame(genou, d, 0.104, 0.017 * cote), 0.0026, 0.0008)
        a.piece("frange_" + nom, frange, K.CREME, mat=rep @ A.repere((-0.006 * cote, 0.004, -0.0026)), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py dytique). Les mesures sont celles du modèle, avant a.taille.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.000, 0.040)),                  # le milieu de la goutte
    ("tete", "corps", (0.0, -0.074, 0.042)),                   # la nuque, sous le corselet
    ("rame_G", "corps", (0.040, 0.012, 0.037)),                # la hanche de la rame (la droite est son miroir)
    ("pattes_G", "racine", (0.040, -0.050, 0.032)),            # les petites pattes de devant : à la racine, elles restent au sol
]
PORTEURS = [("elytres", "corps"), ("suture", "corps"), ("corselet", "corps"),
            ("tete", "tete"), ("oeil", "tete"), ("lourde", "tete"), ("antenne", "tete"), ("sourire", "tete"),
            ("cuisse", "rame", True), ("rame", "rame", True), ("frange", "rame", True), ("pattes", "pattes", True),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def rames(p, angle, leve=0.0):
    """Les deux rames ensemble : angle > 0 les tire vers l'arrière, leve les soulève."""
    p.paire("rame", rot=(0, -leve, angle))


def repos(t):
    """Il attend à l'affût : il respire, les antennes en avant ; un petit coup de rame pour se replacer, la tête qui
    suit une proie, un clignement lent de chasseur."""
    p = Pose()
    r = onde(t, 2)
    p.add("corps", ech=(1 + 0.010 * r, 1, 1 + 0.016 * r))
    rames(p, 14 * cloche(t, 0.40, 0.06) - 4 * cloche(t, 0.80, 0.08))
    p.add("tete", rot=(0, 0, -12 * cloche(t, 0.62, 0.12) + 8 * cloche(t, 0.15, 0.08)))
    p.ouvert = 1 - cloche(t, 0.30, 0.025)
    return p


def avance(t):
    """Il nage comme on rame : les deux rames tirent ensemble, il file, elles reviennent repliées."""
    p = Pose()
    tire = 0.5 - 0.5 * math.cos(math.tau * t)
    rames(p, -24 + 40 * tire, 8 * cloche(t, 0.75, 0.22))
    p.add("corps", pos=(0, -0.006 * math.sin(math.tau * t), 0.002 * onde(t, 2)), rot=(-2 * cloche(t, 0.25, 0.2), 0, 0))
    p.paire("pattes", rot=(0, 0, 8 * onde(t, 2)))
    return p


def mange(t):
    """Il fond sur sa proie, la tient sous lui et la mâchonne, le derrière qui remonte à chaque bouchée."""
    p = Pose()
    bas = 1 - cloche(t, 0.88, 0.12)
    p.add("corps", rot=(10 * bas + 3 * abs(onde(t, 5)) * bas, 0, 0))
    p.add("tete", rot=(14 * bas, 0, 0))
    rames(p, 10 * bas, -4 * bas)
    p.ouvert = 1 - cloche(t, 0.93, 0.02)
    return p


def joie(t):
    """Il bondit, fait la roue sur le dos (un tour complet, les rames grandes ouvertes) et retombe à l'endroit."""
    p = Pose()
    phase = borne(t / 0.8)
    env = math.sin(math.pi * phase)
    p.add("corps", pos=(0, 0, 0.050 * env), rot=(0, 360 * K.lisse(np.array(phase)).item(), 0))
    rames(p, -20 * env, 30 * env)
    p.add("tete", rot=(-10 * env, 0, 0))
    return p


def dort(t):
    """Posé à plat, les rames rangées le long du corps, les yeux fermés ; il respire à peine."""
    p = Pose()
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.006), ech=(1.0, 1.0, 1.0 + 0.015 * onde(t, 1)))
    rames(p, 16, 4)
    p.add("tete", rot=(8, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Dytique")
