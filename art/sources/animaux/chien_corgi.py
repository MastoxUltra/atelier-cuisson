"""Le chien en peluche, la race corgi (le teckel, chien.py, reste la robe de base du chien). Un tonneau de velours roux
posé sur quatre moignons blancs plus courts encore que ceux du teckel, le jabot blanc bombé, la croupe ronde comme une
miche où pointe un plumeau de rien du tout. Sa signature : deux oreilles immenses, dressées en antennes et doublées de
feutrine blanche. Il refuse d'avancer : les pattes avant arc-boutées devant lui, le poids sur l'arrière, la tête
penchée sur le côté, un seul sourcil froncé, et il sourit jusqu'aux oreilles, la langue framboise pendue de travers.
Jovial, et têtu comme une mule.

    python chien_corgi.py        fabrique la fiche art/apercus/animaux/chien_corgi.png
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

ROUX = M.hexa("#efa25c")                      # le velours : un roux de renard (le poil le fonce en roux cuivré)
BRAISE = M.hexa("#c9733a")                    # la selle et le dos des oreilles : le roux plus sombre
BLANC = M.hexa("#fcf7ee")                     # le liseré du front, le museau, le jabot, le dessous, les chaussettes
LANGUE = M.hexa("#ec5f78")                    # l'accent : la langue framboise, pendue de travers
FIL = M.hexa("#4a2a1c")                       # le fil des broderies : le sourire, le sourcil
TOURNE = 0                                    # -30 pour la fiche, posé de biais (on lit sa longueur) ; 0 pour le jeu
CORPS = Vector((0.0, 0.030, 0.150))
LARGE, LONG, HAUT = 0.106, 0.270, 0.098       # les demi-mesures du tonneau
TETE = Vector((0.006, -0.282, 0.392))
PORT = A.repere(TETE, (-8, 16, 22))           # la tête penchée sur le côté, tournée vers vous, le menton à peine levé


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du village."""
    return PORT.to_3x3() @ Vector((x, y, z))


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def oreille():
    """Une grande oreille dressée : un triangle épais aux coins ronds, aplati d'avant en arrière, et son creux de
    feutrine. Dans son repère, l'attache est à l'origine, la pointe monte le long de +Z, le creux regarde vers +Y.
    Le bas s'incurve pour épouser le crâne (sans quoi les coins de l'attache resteraient en l'air)."""
    po = A.profil([(0, 0), (0.052, 0.012), (0.058, 0.040), (0.046, 0.082), (0.026, 0.118), (0.009, 0.138), (0, 0.145)], 6)

    def epouse(v):
        s = v.copy()
        s[:, 2] -= v[:, 0] ** 2 / 0.18 * (1 - K.lisse(v[:, 2] / 0.06))
        return s
    dehors = A.tour(po, 32).etire(1.0, 0.32, 1.0).sculpte(epouse)
    creux = A.tour(po, 24).etire(0.62, 0.30, 0.80).pose((0, 0.008, 0.014)).sculpte(epouse)
    return dehors, creux


def patte(chemin, blanc):
    """Une patte courte et forte : le velours roux en haut, la chaussette blanche sur les derniers « blanc » mètres."""
    ch = A.courbe(chemin, 5)
    long = float(np.sum(np.linalg.norm(np.diff(ch, axis=0), axis=1)))
    return K.tube_peint(ch, lambda t: 0.033 - 0.005 * t, [(1 - blanc / long, ROUX), (9, BLANC)], 16)


def construire():
    a = K.Animal("chien_corgi")
    a.taille = 0.70
    a.tete = PORT @ Vector((0.0, -0.104, -0.012))

    # ----- le corps : un tonneau, le jabot bombé en avant, la croupe ronde et haute comme une miche ; roux dessus,
    #       blanc dessous, une selle braise sur l'échine -----
    def coque(v):
        y = v[:, 1]
        rond = np.sqrt(np.maximum(1 - y * y, 1e-9))
        boudin = np.maximum(1 - np.abs(y) ** 2.4, 0.0) ** (1 / 2.4)
        k = boudin / rond
        s = np.stack([v[:, 0] * k, y, v[:, 2] * k], axis=1)
        s = K.bosse(s, (0, -0.70, -0.60), 0.24, 0.22)                 # le jabot
        s = K.bosse(s, (0, 0.80, 0.25), 0.16, 0.30)                   # la croupe en miche
        s = K.bosse(K.bosse(s, (0.85, -0.50, -0.10), 0.05, 0.10), (-0.85, -0.50, -0.10), 0.05, 0.10)   # les épaules
        avant = K.lisse((-s[:, 1] - 0.1) / 0.8)
        arriere = K.lisse((s[:, 1] + 0.1) / 0.9)
        s = s * [LARGE, LONG, HAUT]
        s[:, 0] *= 1 + 0.06 * avant + 0.04 * arriere                  # large partout, la croupe aussi
        s[:, 2] *= np.where(s[:, 2] < 0, 1 + 0.08 * avant - 0.18 * arriere, 1.0)
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    cv = corps.v
    dessous = cv[:, 2] < -0.030 + 0.105 * K.lisse((-cv[:, 1] - 0.13) / 0.12)      # le blanc monte sur le jabot
    selle = (cv[:, 2] > 0.062) & (cv[:, 1] > -0.17) & (cv[:, 1] < 0.21)
    corps.teinte = np.where(dessous[:, None], np.asarray(BLANC), np.where(selle[:, None], np.asarray(BRAISE), np.asarray(ROUX)))
    G.sillons(corps, [14, 42], 0.005, 1.1)
    a.piece("corps", corps, None, pos=CORPS, rot=(-6, 0, 0))
    a.couture("dos", "corps", 14, 0.60, 0.99, fil=BLANC)
    a.couture("echine", "corps", 42, 0.80, 0.99, fil=BLANC)
    a.rustine("rapiecage", "corps", CORPS + Vector((0, 0.10, 0.01)), (1.0, 0.05, 0.30),
              lambda th: 0.26 + 0.05 * math.cos(3 * th) + 0.03 * math.sin(2 * th), BLANC, feston=16, fil=BRAISE)

    # ----- le cou : court et épais, le jabot blanc devant -----
    fil_cou = K.Fil([(0.0, -0.150, 0.185), (0.002, -0.212, 0.282), (0.005, -0.262, 0.352)], flanc=(1, 0, 0))
    cou = A.tour(A.profil([(0, -0.02), (0.084, 0.0), (0.080, 0.06), (0.070, 0.12), (0.062, 0.17), (0, 0.205)], 5), 32)
    cou.teinte = np.where((cou.v[:, 1] < -0.020)[:, None], np.asarray(BLANC), np.asarray(ROUX))
    a.piece("cou", cou.sculpte(fil_cou.couche), None)

    # ----- la tête : large, les joues rieuses ; un liseré blanc descend du front et s'ouvre sur le menton -----
    def crane(v):
        v = K.bosse(v, (0, -0.55, 0.80), 0.08, 0.25)                 # le front
        v = K.bosse(K.bosse(v, (0.80, -0.50, -0.35), 0.12, 0.22), (-0.80, -0.50, -0.35), 0.12, 0.22)   # les joues
        return v * [0.088, 0.088, 0.078]
    tete = A.boule(1.0, 56, 28).sculpte(crane)
    tv = tete.v
    liste = (tv[:, 1] < -0.020) & (np.abs(tv[:, 0]) < 0.010 + 0.50 * np.maximum(0.025 - tv[:, 2], 0.0))
    menton = (tv[:, 2] < -0.032) & (tv[:, 1] < 0.020)
    tete.teinte = np.where((liste | menton)[:, None], np.asarray(BLANC), np.asarray(ROUX))
    a.piece("tete", tete, None, mat=PORT)
    a.couture("crane", "tete", 14, 0.55, 0.97, fil=BLANC)

    # ----- le museau : un museau de renard, blanc, deux touches rousses en haut des joues ; la truffe noire -----
    MU = PORT @ A.repere((0, -0.050, -0.024), (96, 0, 0))     # dans ce repère : X la gauche, Y le haut, Z vers la truffe
    MU3 = MU.to_3x3()
    museau = A.tour(A.profil([(0, -0.015), (0.064, 0.0), (0.060, 0.035), (0.049, 0.075), (0.038, 0.108), (0.029, 0.128),
                              (0, 0.140)], 6), 40)
    museau.etire(1.0, 0.84, 1.0)
    angle = np.degrees(np.arctan2(museau.v[:, 1], museau.v[:, 0]))
    joue = (np.abs(angle - 90) > 24) & (np.abs(angle - 90) < 78) & (museau.v[:, 2] < 0.052)
    museau.teinte = np.where(joue[:, None], np.asarray(ROUX), np.asarray(BLANC))
    a.piece("museau", museau, None, mat=MU)
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.022, 0.016, 0.015), K.NOIR, mat=MU @ A.repere((0, 0.006, 0.134)), poil=False)
    for nom, c in (("g", 1), ("d", -1)):                       # le grand sourire, qui remonte aux coins
        pts = [a.trace("museau", MU @ Vector((0, 0, z)), [MU3 @ Vector((c * math.cos(math.radians(d)), math.sin(math.radians(d)), 0))])[0]
               for z, d in zip(np.linspace(0.124, 0.050, 7), (-86, -80, -72, -62, -52, -42, -36))]
        a.broderie("bouche_" + nom, A.courbe(pts, 4), 0.0022, FIL)
    # la langue : un pan de feutrine framboise qui sort sous le museau et pend de travers, du côté qu'il nous tend
    a.piece("langue", A.boule(1.0, 24, 12).etire(0.017, 0.032, 0.0065), LANGUE,
            mat=MU @ A.repere((0.010, -0.042, 0.092), (-20, 0, 15)), poil=False)

    # ----- les yeux : petits et vifs ; au-dessus du gauche, un seul sourcil brodé, froncé : il ne bougera pas -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, vers(0.50 * c, -0.74, 0.30))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0145)
    sourcil = a.trace("tete", TETE, [vers(0.24, -0.82, 0.46), vers(0.40, -0.74, 0.58), vers(0.58, -0.62, 0.58), vers(0.70, -0.52, 0.48)])
    a.broderie("sourcil_g", A.courbe(sourcil, 4), 0.0024, FIL)

    # ----- les oreilles : immenses, dressées et écartées en antennes, le dos braise, le creux de feutrine blanche ;
    #       la tête penchée en couche une un peu plus que l'autre -----
    dehors, creux = oreille()
    for nom, c, ecart in (("G", 1, 0.44), ("D", -1, 0.36)):
        p, n = a.surface("tete", TETE, vers(0.48 * c, 0.04, 0.88))
        dresse = vers(ecart * c, -0.04, 0.92).normalized()
        E = A.cadre(p - dresse * 0.020, dresse, vers(0, -1, 0.10))
        a.piece("oreille_" + nom, dehors.copie(), BRAISE, mat=E)
        a.piece("pavillon_" + nom, creux.copie(), BLANC, mat=E, poil=False)

    # ----- les pattes : des moignons ; les deux de devant arc-boutées loin en avant (il refuse d'avancer), celles de
    #       derrière plantées sous de grosses cuisses ; des chaussettes blanches, les pieds tournés en dehors -----
    for nom, c, devant in (("G", 1, 0.0), ("D", -1, 0.012)):
        a.piece("patte_avant_" + nom, patte([(0.060 * c, -0.150, 0.115), (0.066 * c, -0.200 - devant, 0.062),
                                             (0.070 * c, -0.236 - devant, 0.020)], 0.080), None)
        a.piece("pied_avant_" + nom, A.boule(1.0, 24, 12).etire(0.034, 0.044, 0.017).pose((0.072 * c, -0.252 - devant, 0.0168), (0, 0, 10 * c)), BLANC)
        a.piece("cuisse_" + nom, A.boule(1.0, 32, 16).etire(0.046, 0.068, 0.064), ROUX, pos=(0.066 * c, 0.212, 0.120), rot=(-14, 0, 0))
        a.piece("patte_arriere_" + nom, patte([(0.068 * c, 0.200, 0.110), (0.072 * c, 0.212, 0.058), (0.074 * c, 0.204, 0.020)], 0.060), None)
        a.piece("pied_arriere_" + nom, A.boule(1.0, 24, 12).etire(0.033, 0.042, 0.017).pose((0.076 * c, 0.192, 0.0168), (0, 0, 6 * c)), BLANC)

    # ----- la queue : un plumeau de rien du tout, roux au pied, blanc au bout, planté en haut de la miche -----
    plumeau = A.boule(1.0, 24, 12).etire(0.022, 0.020, 0.030)
    plumeau.teinte = np.where((plumeau.v[:, 2] > 0.012)[:, None], np.asarray(BLANC), np.asarray(ROUX))
    a.piece("queue", plumeau, None, pos=(0.0, 0.318, 0.184), rot=(-35, 0, 0))
    if TOURNE:
        tourner(a, TOURNE)
    return a


if __name__ == "__main__":
    K.planche(construire, "Corgi")
