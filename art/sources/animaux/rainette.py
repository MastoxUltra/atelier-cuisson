"""La rainette en peluche : jaune citron, la gorge et le ventre crème, un bandeau noir qui part du nez, traverse l'œil
et file sur le flanc. Toute en pattes et en doigts : accroupie, les cuisses repliées en Z, les coudes sortis, les
ventouses corail grandes ouvertes, la tête tournée et penchée. Elle a repéré quelque chose et va sauter.

    python rainette.py        fabrique la fiche art/apercus/animaux/rainette.png
"""
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

CITRON = M.hexa("#fff25e")                    # le jaune citron du dos (le canard est jaune d'or : K.JAUNE)
NUIT = M.hexa("#26242b")                      # le noir du bandeau : un anthracite, pour que le poil garde du relief
CORPS = Vector((0.0, 0.022, 0.052))
TETE = Vector((0.004, -0.072, 0.090))
DOS = A.repere(CORPS, (-18, 0, 0))            # le corps : l'avant relevé, la croupe au ras de l'herbe
FACE = A.repere(TETE, (-8, 6, 20))            # la tête : le nez levé, tournée et penchée vers celui qui la regarde
F3 = FACE.to_3x3()


def quartiers(maille, paliers):
    """Peint une boule par quartiers, comme une orange, pareil à gauche et à droite : paliers = [(angle, couleur), ...]
    donne la couleur jusqu'à chaque angle (en degrés, une fois la boule couchée : -90 sous le ventre, 0 au flanc, 90 au dos).
    Les limites suivent les mailles : elles sortent nettes, et les bandes s'effilent toutes seules vers les deux bouts."""
    maille.teinte = np.tile(np.asarray(paliers[-1][1], float), (len(maille.v), 1))
    for anneau in maille.anneaux:
        n = len(anneau)
        for j, i in enumerate(anneau if n > 1 else []):
            c = 360.0 * (j + 0.5) / n                                  # le milieu de la case que ce point colore
            angle = c if c <= 90 else 180 - c if c <= 270 else c - 360
            maille.teinte[i] = next(couleur for seuil, couleur in paliers if angle <= seuil)
    return maille


def boudin(points, rayons, cotes=14):
    """Un membre : un boudin lisse qui passe par les points, avec le rayon voulu à chacun."""
    n = len(points) - 1
    return A.tube(A.courbe(points, 8), lambda s: float(np.interp(s * n, range(n + 1), rayons)), cotes)


def doigts(racine, vers, paume, longueurs, ecart, fil=0.0042, ventouse=0.0105):
    """Une main ou un pied : des doigts de feutrine en éventail autour de « vers », chacun un peu arqué, et une ventouse
    ronde au bout, à plat sur « paume » (la direction que regarde le dos de la main). Rend les doigts, puis les ventouses."""
    racine, vers, paume = Vector(racine), Vector(vers).normalized(), Vector(paume)
    paume = (paume - vers * paume.dot(vers)).normalized()
    tiges = A.boule(1.0, 20, 10).etire(0.011, 0.011, 0.006).pose(racine + vers * 0.004, A.viser(paume))
    pastilles = None
    for k, long in enumerate(longueurs):
        d = A.tourne(paume, ecart * (k / (len(longueurs) - 1) - 0.5), vers)
        bout = racine + d * long
        tiges = tiges + A.tube(A.courbe([racine, racine + d * long * 0.5 + paume * long * 0.13, bout], 6), fil, 12)
        pastille = A.boule(1.0, 20, 10).etire(ventouse, ventouse, ventouse * 0.45).pose(bout, A.viser(paume))
        pastilles = pastille if pastilles is None else pastilles + pastille
    return tiges, pastilles


def construire():
    a = K.Animal("rainette")
    a.taille = 0.30
    a.tete = FACE @ Vector((0, -0.034, 0.004))

    # ----- le corps : une poire couchée, les épaules larges, la taille fine, la bosse du bassin.
    #       La boule est couchée (son pôle du haut fait le cou) : ses quartiers donnent le ventre crème et le bandeau -----
    def coque(v):
        u = K.bosse(np.stack([v[:, 0], -v[:, 2], v[:, 1]], axis=1), (0, 0.30, 0.95), 0.16, 0.10)
        x, t, z = u[:, 0], u[:, 1], u[:, 2]
        arriere = K.lisse(t * 0.5 + 0.5)
        return np.stack([x * 0.046 * (1 - 0.40 * arriere), t * 0.082, z * np.where(z > 0, 0.030, 0.026) * (1 - 0.22 * arriere)], axis=1)
    corps = quartiers(A.boule(1.0, 56, 28), [(-8, K.CREME), (8, CITRON), (44, NUIT), (90, CITRON)]).sculpte(coque)
    G.sillons(corps, [14], 0.003, 1.0)                         # la couture du dos creuse un peu le tissu
    a.piece("corps", corps, None, mat=DOS)
    a.couture("dos", "corps", 14, 0.10, 0.62, large=0.007, haut=0.003, pas=0.011)

    # ----- la tête : large et plate, le museau en pointe ; la gorge crème s'arrête à la bouche -----
    def crane(v):
        x, t, z = v[:, 0], -v[:, 2], v[:, 1]
        nez = K.lisse(-t)
        return np.stack([x * 0.050 * (1 - 0.30 * nez), t * np.where(t < 0, 0.056, 0.044), z * np.where(z > 0, 0.027, 0.023) * (1 - 0.30 * nez)], axis=1)
    tete = quartiers(A.boule(1.0, 56, 28), [(-20, K.CREME), (5, CITRON), (26, NUIT), (90, CITRON)]).sculpte(crane)
    a.piece("tete", tete, None, mat=FACE)
    a.couture("crane", "tete", 14, 0.30, 0.80, large=0.007, haut=0.003, pas=0.011)
    # la bouche : un seul fil qui suit la limite de la gorge, d'une joue à l'autre par le bout du nez ; un coin remonte
    levre = [tete.anneaux[9][55], tete.anneaux[10][54]] + [tete.anneaux[i][53] for i in range(11, 28)] + [tete.anneaux[i][31] for i in range(27, 13, -1)]
    a.broderie("bouche", a.trace("tete", TETE, [F3 @ Vector(tete.v[i]) for i in levre], 0.0035), 0.0016)

    # ----- les yeux énormes, sur les côtés de la tête : un globe ceint du bandeau, un gros bouton planté dedans -----
    for nom, cote in (("_G", 1), ("_D", -1)):
        place = Vector((0.040 * cote, 0.004, 0.010))
        regard = F3 @ Vector((0.62 * cote, -0.70, 0.35)).normalized()
        globe = K.bandes(A.boule(1.0, 40, 24), [(-0.30, CITRON), (0.20, NUIT), (9, CITRON)]).etire(0.030)
        a.piece("globe" + nom, globe, None, mat=FACE @ A.repere(place, A.viser((-0.49 * cote, 0, 0.87))))
        a.bouton("oeil" + nom, FACE @ place + regard * 0.028, regard, 0.018)

    # ----- les pattes arrière : pliées en Z le long du flanc, la cuisse dodue, le genou sorti,
    #       le talon contre la croupe, le pied à plat et les orteils en éventail -----
    patte = boudin([(0.016, 0.072, 0.036), (0.044, 0.036, 0.046), (0.070, 0.000, 0.056), (0.066, 0.048, 0.040), (0.056, 0.098, 0.022), (0.092, 0.050, 0.012)],
                   [0.022, 0.021, 0.016, 0.013, 0.010, 0.009])
    a.piece("patte", patte, CITRON, paire=True)
    orteils, pastilles = doigts((0.092, 0.052, 0.011), (0.55, -0.83, 0.02), (0, 0, 1), (0.044, 0.056, 0.058, 0.046), 82)
    a.piece("pied", orteils, CITRON, poil=False, paire=True)
    a.piece("ventouse_pied", pastilles, K.CORAIL, poil=False, paire=True)

    # ----- les bras : le coude sorti, les mains à plat, les doigts grands ouverts ; la gauche a déjà fait un pas -----
    a.piece("bras_D", boudin([(-0.028, -0.026, 0.074), (-0.056, -0.010, 0.046), (-0.050, -0.066, 0.013)], [0.013, 0.010, 0.008]), CITRON)
    tiges, pastilles = doigts((-0.050, -0.068, 0.012), (-0.22, -0.96, -0.02), (0, 0, 1), (0.038, 0.048, 0.048, 0.040), 100)
    a.piece("main_D", tiges, CITRON, poil=False)
    a.piece("ventouse_main_D", pastilles, K.CORAIL, poil=False)
    a.piece("bras_G", boudin([(0.028, -0.026, 0.074), (0.064, -0.022, 0.048), (0.074, -0.088, 0.013)], [0.013, 0.010, 0.008]), CITRON)
    tiges, pastilles = doigts((0.074, -0.090, 0.012), (0.30, -0.94, -0.02), (0, 0, 1), (0.040, 0.050, 0.050, 0.042), 105)
    a.piece("main_G", tiges, CITRON, poil=False)
    a.piece("ventouse_main_G", pastilles, K.CORAIL, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py rainette). Les mesures sont celles du modèle, avant a.taille.

import math

from poses import Pose, borne, cloche, onde

# La tête est tournée et penchée (FACE), et la main gauche a déjà fait un pas : les globes des yeux et les poignets
# n'ont pas de miroir juste. Leurs os sont donc nommés à la main, en minuscules (globe_g, globe_d, main_g, main_d).
# Les pattes arrière, elles, sont posées en paire : la cuisse, le tibia et le pied se partagent le boudin plié en Z.
JAMBE = [(0.016, 0.072, 0.036), (0.044, 0.036, 0.046), (0.070, 0.000, 0.056), (0.066, 0.048, 0.040), (0.056, 0.098, 0.022), (0.092, 0.050, 0.012)]
_TRONCONS = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(np.array(JAMBE), axis=0), axis=1))])
GENOU, TALON = float(_TRONCONS[2]), float(_TRONCONS[4])          # le long du boudin, depuis la hanche
SAC = (0.0, -0.012, -0.022)                                      # le milieu de la gorge, dans le repère de la tête


def _abscisse(points, chemin, faits):
    """Pour chaque point : sa distance le long du chemin, au pied de la perpendiculaire sur le tronçon le plus proche."""
    c = np.asarray(chemin, float)
    a0, ab = c[:-1], np.diff(c, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    ap = points[:, None, :] - a0[None, :, :]
    u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
    j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
    return faits[j] + u[np.arange(len(points)), j] * np.sqrt(l2[j])


def patte(points, cote):
    """Le boudin de la patte arrière : la cuisse jusqu'au genou, le tibia jusqu'au talon, puis le pied."""
    s = _abscisse(points, JAMBE, _TRONCONS)
    g = K.lisse((s - GENOU + 0.008) / 0.016)
    p = K.lisse((s - TALON + 0.006) / 0.012)
    return {"cuisse" + cote: 1 - g, "jambe" + cote: g - p, "pied" + cote: p}


def crane(points, cote):
    """La tête est d'une seule pièce : sous la bouche, le tissu suit peu à peu l'os « gorge », pour qu'elle palpite."""
    local = (points - np.asarray(TETE)) @ np.array(F3)            # dans le repère de la tête
    g = np.clip(1.0 - np.linalg.norm((local - SAC) / (0.040, 0.032, 0.020), axis=1), 0.0, 1.0)
    sac = g * g * (3 - 2 * g)
    return {"tete": 1.0 - sac, "gorge": sac}


def _cote(os_):
    """Une pièce d'un côté (globe_G, main_D...) portée tout entière par l'os de son côté : globe_g, main_d..."""
    return lambda points, cote: {os_ + "_" + cote[1:].lower(): np.ones(len(points))}


OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.070, 0.030)),             # les hanches : elle se tasse et se cabre autour
    ("tete", "corps", (-0.008, -0.043, 0.082)),           # la nuque
    ("gorge", "tete", (0.006, -0.078, 0.087)),            # au-dessus du sac de la gorge, dans la tête : il gonfle depuis là
    ("globe_g", "tete", (0.0405, -0.053, 0.095)),         # le milieu des globes : les yeux rentrent dans la tête pour avaler
    ("globe_d", "tete", (-0.0343, -0.080, 0.1035)),
    # les épaules sont nommées à la main, comme les poignets : le poignet droit doit trouver son épaule déjà déclarée
    # (le miroir automatique d'un os « _G » n'est ajouté qu'en fin de liste, trop tard pour lui servir de parent)
    ("bras_g", "corps", (0.028, -0.026, 0.074)),          # l'épaule gauche
    ("bras_d", "corps", (-0.028, -0.026, 0.074)),         # l'épaule droite
    ("main_g", "bras_g", (0.074, -0.090, 0.012)),         # le poignet gauche, un pas en avant
    ("main_d", "bras_d", (-0.050, -0.068, 0.012)),
    ("cuisse_G", "corps", JAMBE[0]),                      # la hanche
    ("jambe_G", "cuisse_G", JAMBE[2]),                    # le genou
    ("pied_G", "jambe_G", JAMBE[4]),                      # le talon, contre la croupe
]
PORTEURS = [("corps", "corps"), ("dos", "corps"),
            ("tete", crane, "tete"), ("crane", crane, "tete"), ("bouche", crane, "tete"),
            ("globe", _cote("globe")), ("oeil", _cote("globe")),
            ("bras", _cote("bras")), ("main", _cote("main")), ("ventouse_main", _cote("main")),
            ("patte", patte, "cuisse*"), ("pied", "pied", True), ("ventouse_pied", "pied", True),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def monte(t, debut, fin):
    """De 0 (avant « debut ») à 1 (après « fin »), en douceur."""
    x = borne((t - debut) / (fin - debut))
    return x * x * (3 - 2 * x)


def gonfle(p, g):
    """La gorge : g = 1 pour le grand ballon, 0,2 pour un battement."""
    p.add("gorge", ech=(1 + 0.9 * g, 1 + 0.9 * g, 1 + 1.4 * g))


def yeux(p, rentre=0.0, regard=0.0):
    """Les globes : « rentre » les enfonce dans la tête (elle avale), « regard » les roule vers sa gauche."""
    for o in ("globe_g", "globe_d"):
        p.add(o, pos=(0, 0.002 * rentre, -0.013 * rentre), rot=(0, 0, 14 * regard))


def detend(p, e, plie=0.0):
    """Les pattes arrière, pliées en Z presque à plat, se déplient en arrière comme un compas (e de 0 à 1 : la poussée),
    ou se replient un peu plus (plie). La cuisse, le tibia et le pied tournent surtout autour de la verticale."""
    p.paire("cuisse", rot=(4 * e, 0, 129 * e + 6 * plie))
    p.paire("jambe", rot=(-6 * e, 0, -146 * e - 8 * plie))
    p.paire("pied", rot=(0, 0, 150 * e + 2 * plie))


def repos(t):
    """Accroupie, la gorge qui palpite sans arrêt. Elle roule des yeux vers quelque chose, se ramasse en remuant
    la croupe comme pour sauter... puis se ravise ; elle lève un doigt de la main gauche, et cligne."""
    p = Pose()
    r = onde(t, 2)
    bat = 0.5 + 0.5 * onde(t, 12)
    guette = cloche(t, 0.42, 0.16)
    remue = cloche(t, 0.46, 0.08) * onde(t, 14)
    gonfle(p, 0.22 * bat * (1 - 0.6 * guette))
    p.add("corps", rot=(-3 * guette, 0, 4 * remue), pos=(0, 0, -0.004 * guette), ech=(1 + 0.012 * r, 1, 1 + 0.018 * r))
    p.add("tete", rot=(-4 * guette, 0, 6 * cloche(t, 0.20, 0.10) - 4 * guette))
    yeux(p, 0.0, cloche(t, 0.20, 0.10) - 0.6 * guette)
    p.add("main_g", rot=(-14 * cloche(t, 0.78, 0.05), 0, 0))
    p.ouvert = 1 - cloche(t, 0.08, 0.025) - cloche(t, 0.66, 0.025)
    return p


def avance(t):
    """Un bond par cycle : elle se tasse, pousse d'un coup sur ses cuisses, file les pattes tendues derrière elle,
    les bras le long du corps, les ramène sous elle, tend les mains vers l'herbe et se reçoit en s'écrasant un peu."""
    p = Pose()
    tasse = cloche(t, 0.06, 0.08)
    pousse = monte(t, 0.10, 0.24) * (1 - monte(t, 0.46, 0.72))
    u = borne((t - 0.16) / 0.56)                                   # en l'air de 0,16 à 0,72
    vol = 4 * u * (1 - u)
    choc = cloche(t, 0.78, 0.07)
    cabre = cloche(t, 0.30, 0.12) - 0.9 * cloche(t, 0.62, 0.10)
    bras = monte(t, 0.17, 0.30) * (1 - monte(t, 0.48, 0.64))
    tend = cloche(t, 0.68, 0.06)
    p.add("corps", pos=(0, -0.010 * vol, 0.11 * vol + 0.016 * pousse * (1 - u) - 0.006 * tasse - 0.005 * choc), rot=(-12 * cabre, 0, 0),
          ech=(1 + 0.05 * tasse + 0.06 * choc, 1, 1 - 0.08 * tasse - 0.10 * choc))
    detend(p, pousse, tasse + choc)
    for o, s in (("bras_g", 1), ("bras_d", -1)):
        p.add(o, rot=(112 * bras - 25 * tend, 0, s * 10 * bras))
    for o in ("main_g", "main_d"):
        p.add(o, rot=(15 * bras - 20 * tend, 0, 0))
    p.add("tete", rot=(10 * cabre, 0, 0))
    gonfle(p, 0.15 * choc)
    yeux(p, 0.6 * choc)
    p.ouvert = borne(1 - cloche(t, 0.79, 0.04))
    return p


def mange(t):
    """Elle vise, se jette en avant la bouche ouverte et happe la mouche d'un coup de tête ; puis elle avale
    en rentrant deux fois les yeux, la gorge qui roule, et se recale dans sa pose."""
    p = Pose()
    vise = monte(t, 0.02, 0.14) * (1 - monte(t, 0.18, 0.22))
    happe = cloche(t, 0.24, 0.06)
    avale = cloche(t, 0.52, 0.06) + cloche(t, 0.70, 0.06)
    mache = cloche(t, 0.61, 0.20)
    p.add("corps", rot=(-4 * vise + 6 * happe, 0, 0), pos=(0, -0.010 * happe, 0.004 * happe - 0.004 * vise))
    p.add("tete", rot=(-6 * vise + 14 * happe, 0, 0))
    for o in ("bras_g", "bras_d"):
        p.add(o, ech=(1, 1, 1 - 0.22 * happe + 0.05 * vise))          # les mains ne quittent pas l'herbe
    detend(p, 0.12 * happe, 0.6 * vise)
    p.add("gorge", ech=(1 - 0.15 * happe, 1, 1 - 0.25 * happe))
    gonfle(p, 0.25 * mache * (0.5 + 0.5 * onde(t, 10)))
    yeux(p, avale, 0.5 * vise)
    p.add("main_g", rot=(-10 * vise, 0, 0))
    p.ouvert = borne(1 - 0.9 * avale - cloche(t, 0.90, 0.025))
    return p


def joie(t):
    """Le grand saut sur place : elle se ramasse, jaillit tout droit en écartant bras et pattes comme une étoile,
    fait un tour complet en l'air, la gorge en ballon, et retombe dans sa pose de guet."""
    p = Pose()
    tasse = cloche(t, 0.08, 0.08, False) + 0.7 * cloche(t, 0.82, 0.07, False)
    u = borne((t - 0.14) / 0.62)
    vol = 4 * u * (1 - u)
    etoile = math.sin(math.pi * u)
    tour = math.radians(360 * monte(t, 0.18, 0.70))
    # elle pivote autour de son milieu, pas autour des hanches : 6 cm devant elles
    p.add("corps", pos=(-0.060 * math.sin(tour), -0.060 + 0.060 * math.cos(tour), 0.16 * vol - 0.007 * tasse),
          rot=(-18 * etoile, 0, math.degrees(tour)), ech=(1 + 0.05 * tasse, 1, 1 - 0.09 * tasse))
    detend(p, 0.6 * etoile, tasse)
    for c, s in (("_G", 1), ("_D", -1)):
        p.add("cuisse" + c, rot=(0, 0, s * 25 * etoile))
    p.add("bras_g", rot=(0, -95 * etoile, 0))
    p.add("bras_d", rot=(0, 95 * etoile, 0))
    gonfle(p, 0.9 * cloche(t, 0.45, 0.20, False))
    yeux(p, 0.0, 0.0)
    p.ouvert = borne(1 - cloche(t, 0.84, 0.05, False))
    return p


def dort(t):
    """Aplatie, le menton posé dans l'herbe, les pattes serrées sous elle, les yeux rentrés et fermés ;
    sa gorge se soulève lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", rot=(6, 0, 0), pos=(0, 0, -0.004), ech=(1.05 + 0.01 * r, 1.0, 0.86 + 0.025 * r))
    p.add("tete", rot=(10, 0, -6))
    gonfle(p, 0.10 + 0.08 * r)
    yeux(p, 0.6)
    for o in ("bras_g", "bras_d"):
        p.add(o, rot=(-10, 0, 0), ech=(1, 1, 0.66))                  # les coudes écartés, les mains à plat devant elle
    detend(p, 0.0, 1.0)
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Rainette")
