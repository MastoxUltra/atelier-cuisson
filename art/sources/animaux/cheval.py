"""Le cheval en peluche : un cob alezan aux crins couleur lin, le gros bras de la ferme qui se croit étalon (la robe
choisie par l'auteur le 14/10, sur une planche de cinq). Un tonneau de velours roux cuivré sur quatre jambes courtes et
épaisses, l'encolure énorme et rouée, une grosse tête au chanfrein droit et au bout du nez large et doux, une liste
blanche. La crinière lin tombe en lourdes mèches du côté qu'il nous tend, le toupet lui cache un œil ; la queue,
épaisse, retombe jusqu'au sol. Et surtout ses fanons : de grandes franges crème qui lui couvrent les sabots comme des
pantalons à pattes d'éléphant ; on ne voit dépasser que la pince de corne miel. Il se pavane en plein passage,
l'antérieur gauche levé haut, la tête tournée vers nous, un sourcil levé : très content de lui.

    python cheval.py bai     le même cheval dans une autre robe (voir ROBES) : fiche art/apercus/animaux/cheval_bai.png
    (l'auteur, 14/10 : la forme du cob lui va, il choisit la robe sur une planche ; le gris pommelé : cheval_pommele.py)
    (les dessins refusés : cheval_ancien.py, le palomino ; cheval_ancien2.py, le bai, « non » d'l'auteur le 14/10)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import matieres as M
import peluche as K

# Les robes proposées à l'auteur : la robe, le bout du nez, les crins, les fanons, le bas des jambes (None : la robe),
# et des taches (None, ou leur couleur : la robe pie)
ROBES = {
    "noir": ("#2d2729", "#5e5355", "#d9dce2", "#d9dce2", None, None),        # le premier : noir chaud, crins d'argent
    "bai": ("#94492a", "#3b2a27", "#2a2225", "#ece8e0", "#2a2225", None),    # brun cerise, crins et bas des jambes noirs
    "alezan": ("#cf7a3e", "#7a4428", "#f2dcb0", "#f3e6cc", None, None),       # roux cuivré, crins lavés couleur lin
    "palomino": ("#eec784", "#9a7650", "#f6f2e8", "#f6f2e8", None, None),     # doré, crins blancs
    "pie": ("#f2efe8", "#a88a86", "#ede9e2", "#f2efe8", None, "#2d2729"),     # blanc à grandes taches noires
}
CHOISIE = "alezan"                            # la robe choisie par l'auteur le 14/10 ; les autres restent des variantes
ROBE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ROBES else os.environ.get("ROBE_CHEVAL", CHOISIE)
NOIR, MUFLE, ARGENT, FANONS, BAS, TACHES = (M.hexa(c) if c else None for c in ROBES[ROBE])   # NOIR : la couleur de la robe
TETE = TACHES or NOIR                         # la pie a la tête de la couleur de ses taches, la liste blanche au milieu
CORNE = M.hexa("#d9a24e")                     # l'accent : la corne miel des sabots, qui dépasse sous les fanons
TOURNE = 0                                    # -24 sur la fiche (il pose de trois quarts) ; 0 pour le jeu
CROUPE = Vector((0.0, 0.28, 0.515))           # le bout arrière du corps (une pièce tournée, couchée vers l'avant)
CABRE = 4.0                                   # le garrot un peu plus haut que la croupe
COL = math.radians(12)                        # l'encolure part un peu vers sa gauche, du côté où il regarde
AVANT = Vector((math.sin(COL), -math.cos(COL), 0.0))
FLANC = np.array([math.cos(COL), math.sin(COL), 0.0])      # le côté gauche de l'encolure : celui de la crinière
BASE = Vector((0.0, -0.170, 0.520))           # le pied de l'encolure, enfoui entre les épaules
ARC = [(0.0, 0.0), (0.028, 0.120), (0.060, 0.235), (0.100, 0.320), (0.142, 0.372), (0.176, 0.388)]    # (avance, monte) : courte et rouée
LACET, PIQUE, PENCHE = 28.0, 46.0, 8.0        # la tête : tournée vers nous, le nez bas mais en avant, un rien penchée
GROSSE = 1.40                                 # une grosse tête : c'est elle qu'on lit de loin, et c'est une peluche


def gauss(x):
    return np.exp(-x * x)


def meche(chemin, large, face, plat=0.36, long_pointe=0.93, cotes=20):
    """Une mèche plate : un fuseau tourné, aplati, couché le long d'un chemin. « face » : la direction de son
    épaisseur (on la voit de plat depuis là) ; sa largeur se met d'équerre avec le chemin, en chaque point."""
    p = A.courbe(chemin, 8)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    n0 = np.asarray(face, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.linalg.norm(t, axis=1, keepdims=True)
        x = np.cross(n0, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.60 * large, 0.05 * L), (0.95 * large, 0.22 * L), (large, 0.42 * L), (0.72 * large, 0.70 * L),
                     (0.30 * large, long_pointe * L), (0.06 * large, 0.985 * L), (0, L)], 5)
    return A.tour(prof, cotes).etire(1.0, plat, 1.0).sculpte(couche)


def membre(points, rayons):
    """Une jambe : un boudin qui passe par ses articulations, avec un rayon donné à chacune."""
    return A.courbe(points, 6), lambda t: float(np.interp(t, np.linspace(0, 1, len(rayons)), rayons))


def jambe(points, rayons):
    """Une jambe de la couleur de la robe, ou qui fonce peu à peu vers BAS sous le genou (le bai)."""
    if BAS is None:
        return K.tube_peint(*membre(points, rayons), [(1, NOIR)], 20)
    a, b = np.asarray(NOIR), np.asarray(BAS)
    return K.tube_peint(*membre(points, rayons), [(0.45, NOIR)] + [(0.45 + 0.2 * k / 6, tuple(a + (b - a) * k / 6)) for k in range(1, 7)] + [(1, BAS)], 20)


def sabot():
    def pince(v):                                         # la pince avance un peu, comme un vrai sabot
        s = v.copy()
        s[:, 1] -= 0.016 * K.lisse((0.05 - v[:, 2]) / 0.05)
        return s
    return A.tour(A.profil([(0, 0), (0.054, 0.003), (0.058, 0.020), (0.048, 0.054), (0.040, 0.068), (0, 0.074)], 5), 28).sculpte(pince)


def fanons(boulet, sol, cap=0.0, n=7):
    """Les fanons d'une jambe : des mèches d'argent nées tout autour du boulet, qui tombent en s'évasant jusqu'au sol
    et couvrent le sabot ; devant, elles s'ouvrent pour laisser voir la pince. cap : là où regarde le devant du pied."""
    b = Vector(boulet)
    toutes = None
    for k in range(n):
        ang = cap + math.pi * (0.30 + 1.40 * k / (n - 1))        # tout le tour, sauf le devant
        dehors = Vector((math.sin(ang), -math.cos(ang), 0.0))
        long = 1.0 + 0.25 * math.sin(2.3 * k)
        chemin = [b + dehors * 0.030 + Vector((0, 0, 0.040)), b + dehors * 0.050, b + dehors * (0.066 + 0.010 * long) + Vector((0, 0, -0.045)),
                  Vector((b.x, b.y, sol)) + dehors * (0.086 + 0.016 * long) + Vector((0, 0, 0.010))]
        m = meche(chemin, 0.030, dehors, 0.42, 0.90, 16)
        toutes = m if toutes is None else toutes + m
    return toutes


def tacher(m, graine=3, n=8, rayon=0.68):
    """La robe pie : quelques grandes taches rondes de la couleur TACHES sur la robe claire (dans le repère de la pièce)."""
    if TACHES is None:
        return m
    rng = np.random.default_rng(graine)
    graines = rng.normal(size=(n, 3))
    graines /= np.linalg.norm(graines, axis=1, keepdims=True)
    u = m.v - m.v.mean(axis=0)
    u = u / np.maximum(np.abs(u).max(axis=0), 1e-9)
    u /= np.maximum(np.linalg.norm(u, axis=1, keepdims=True), 1e-9)
    d = np.sqrt(np.min(np.sum((u[:, None, :] - graines[None, :, :]) ** 2, axis=2), axis=1))
    m.teinte = np.where((d < rayon)[:, None], np.asarray(TACHES), np.asarray(NOIR))
    return m


REPERES = {}                                  # quelques points du modèle, notés pendant construire() pour le squelette


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def construire():
    a = K.Animal("cheval" if ROBE == CHOISIE else "cheval_" + ROBE)
    a.taille = 2.00

    # ----- le corps : tourné de la croupe au poitrail, puis couché ; dans la pièce, X est la gauche, Y le dos, Z l'avant.
    #       Un tonneau : la croupe ronde et large, le ventre plein, le poitrail énorme. -----
    def galbe(v):
        s = v.copy()
        croupe = gauss((v[:, 2] - 0.12) / 0.11)
        s[:, 0] *= 0.98 * (1 + 0.14 * croupe + 0.12 * gauss((v[:, 2] - 0.48) / 0.08))       # la croupe et les épaules
        dessus = v[:, 1] > 0
        s[dessus, 1] *= (1 + 0.10 * croupe + 0.06 * gauss((v[:, 2] - 0.45) / 0.06))[dessus]
        s[~dessus, 1] *= (1 - 0.10 * K.lisse((0.30 - v[:, 2]) / 0.20) + 0.12 * gauss((v[:, 2] - 0.43) / 0.09))[~dessus]
        return s
    corps = A.tour(A.profil([(0, 0), (0.100, 0.010), (0.150, 0.060), (0.165, 0.130), (0.162, 0.215), (0.155, 0.300),
                             (0.162, 0.400), (0.158, 0.470), (0.125, 0.548), (0, 0.590)], 6), 48).sculpte(galbe)
    a.piece("corps", tacher(corps), None if TACHES else NOIR, pos=CROUPE, rot=(90 - CABRE, 0, 0))

    # ----- l'encolure : une seule pièce couchée le long de son arc, énorme au garrot -----
    enc = K.Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in ARC], FLANC)
    L = enc.long
    parts, rayons = [0.03, 0.15, 0.35, 0.55, 0.75, 0.90, 0.985], [0.150, 0.142, 0.120, 0.098, 0.082, 0.074, 0.064]
    pc = A.profil([(0, 0)] + [(r, p * L) for r, p in zip(rayons, parts)] + [(0, 1.01 * L)], 6)
    a.piece("cou", tacher(A.tour(pc, 48).etire(0.78, 1.0, 1.0), 5, 5, 0.75).sculpte(enc.couche), None if TACHES else NOIR)

    # ----- la tête : un profil de cob, le front large, le chanfrein droit, un gros bout de nez rond et doux, la ganache
    #       pleine ; dans son repère, X la gauche, Y le chanfrein, Z vers le nez -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0, 0, 0), nez) @ Matrix.Rotation(math.radians(PENCHE), 4, Vector((0, 0, 1))) @ A.repere(ech=(GROSSE,) * 3)
    bout = Vector(enc.cadre(L)[0])
    T = A.repere(bout - T.to_3x3() @ Vector((0, -0.022, 0.070))) @ T            # le bout de l'encolure entre dans la ganache
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.060, 0.150))

    def cob(v):
        s = v.copy()
        z, haut = v[:, 2], v[:, 1] > 0
        s[:, 0] *= 0.80 + 0.10 * gauss((z - 0.085) / 0.050) + 0.06 * gauss((z - 0.265) / 0.030)
        s[:, 1] *= np.where(haut, 1 + 0.08 * gauss((z - 0.075) / 0.040),
                            1 + 0.30 * gauss((z - 0.075) / 0.045) + 0.10 * gauss((z - 0.262) / 0.026))
        return s
    tete = A.tour(A.profil([(0, 0), (0.046, 0.008), (0.070, 0.040), (0.076, 0.090), (0.066, 0.140), (0.056, 0.190),
                            (0.056, 0.222), (0.064, 0.256), (0.056, 0.288), (0, 0.304)], 6), 64)
    # la liste : une étoile entre les yeux, une large bande qui descend, qui s'arrête sur le bout du nez gris
    tour_ = np.abs(np.arctan2(tete.v[:, 0], tete.v[:, 1]))
    z = tete.v[:, 2]
    large = 0.20 + 0.30 * gauss((z - 0.090) / 0.026) + 0.10 * K.lisse((z - 0.200) / 0.040)
    liste = (tour_ < large) & (z > 0.060) & (z < 0.258)
    tete.teinte = np.where(liste[:, None], K.BLANC, np.where((z > 0.250)[:, None], MUFLE, TETE))
    a.piece("tete", tete.sculpte(cob), None, mat=T)
    for nom, c in (("G", 1), ("D", -1)):
        a.rustine("naseau_" + nom, "tete", T @ Vector((0, 0, 0.262)), T3 @ Vector((c * 0.60, 0.30, 0.74)), 0.24, NOIR, 0.0025, 0)

    # ----- les yeux : grands, vivants, sur une amande blanche ; un sourcil d'argent levé du côté qu'il nous tend.
    #       De l'autre côté, le toupet lui tombe sur l'œil. -----
    centre = T @ Vector((0, 0, 0.094))
    for nom, c in (("G", 1), ("D", -1)):
        vers = T3 @ Vector((c * 0.70, 0.56, -0.02))
        a.rustine("blanc_" + nom, "tete", centre, vers, 0.37, K.BLANC, 0.003, 0)
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.62, 0.64, 0.24)))
        a.oeil("oeil_" + nom, pos + n * 0.0045, n, 0.021)
    leve = [T3 @ Vector((0.48, 0.96 + 0.22 * math.sin(math.pi * u), -0.16 + 0.64 * u)) for u in np.linspace(0, 1, 7)]
    a.broderie("sourcil_g", A.courbe(a.trace("tete", centre, leve, 0.003), 4), 0.0045, ARGENT)

    # ----- les oreilles : petites et dressées (c'est un cob), l'une pointée vers nous, l'autre tournée en arrière -----
    po = A.profil([(0, 0), (0.025, 0.012), (0.031, 0.040), (0.022, 0.072), (0.008, 0.096), (0, 0.103)], 6)
    for nom, c, regard in (("G", 1, Vector((0.30, 0.82, -0.48))), ("D", -1, Vector((-0.55, 0.70, 0.40)))):
        def courbe_(v, c=c):
            s = v.copy()
            s[:, 0] -= c * 0.9 * np.clip(v[:, 2] - 0.05, 0, None) ** 2 / 0.07
            return s
        vers = (T3 @ regard).normalized()
        E = A.cadre(T @ Vector((c * 0.040, 0.034, 0.024)) - vers * 0.012, vers, T3 @ Vector((c * 0.2, 0.3, 0.95)))
        a.piece("oreille_" + nom, A.tour(po, 32).etire(1.0, 0.45, 1.0).sculpte(courbe_), TETE, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 24).etire(0.60, 0.40, 0.78).pose((0, 0.010, 0.016)).sculpte(courbe_), MUFLE, mat=E, poil=False)

    # ----- la crinière : de lourdes mèches d'argent nées sur la crête, qui passent du côté gauche et tombent le long de
    #       l'encolure ; la pointe se recourbe un peu -----
    arriere, haut = -np.array(AVANT), np.array([0.0, 0.0, 1.0])
    criniere = None
    for i, f in enumerate(np.linspace(0.12, 0.97, 9)):
        c_, av, nq = enc.cadre(f * L)
        r = float(np.interp(f, parts, rayons))
        crete = c_ + nq * r
        k = (0.95 + 0.30 * math.sin(math.pi * f)) * (0.78 if i % 2 else 1.0)
        chemin = [crete - FLANC * 0.016 - nq * 0.012, crete + nq * 0.022 + FLANC * 0.020,
                  crete + nq * 0.006 + FLANC * 0.066 + arriere * 0.020]
        chemin += [chemin[-1] + FLANC * 0.022 + arriere * 0.030 * k - haut * 0.110 * k,
                   chemin[-1] + FLANC * 0.030 + arriere * 0.060 * k - haut * 0.200 * k,
                   chemin[-1] + FLANC * 0.048 + arriere * 0.100 * k - haut * 0.250 * k]
        m = meche(chemin, 0.050 if i % 2 else 0.056, FLANC + nq * 0.3, 0.38)
        criniere = m if criniere is None else criniere + m
    a.piece("criniere", criniere, ARGENT)
    # le toupet : une grosse mèche qui sort entre les oreilles et retombe en travers du front, sur son œil droit
    toupet = [T @ Vector(q) for q in ((0.000, 0.034, 0.010), (0.004, 0.078, 0.030), (-0.010, 0.094, 0.060), (-0.032, 0.088, 0.090),
                                      (-0.052, 0.074, 0.110))]
    a.piece("toupet", meche(toupet, 0.034, T3 @ Vector((0, 1, 0)), 0.42), ARGENT)

    # ----- la queue : épaisse, attachée haut, elle s'arque un peu puis retombe jusqu'au sol en une lourde gerbe -----
    queue = A.tube(A.courbe([(0, 0.215, 0.610), (0, 0.290, 0.660), (0, 0.345, 0.660), (0, 0.380, 0.620)], 6),
                   lambda t: 0.046 - 0.012 * t, 16)
    depart = np.array([0.0, 0.370, 0.630])
    for e, r, c, large in ((0.000, 1.00, 1.00, 0.064), (0.040, 1.18, 0.92, 0.054), (-0.036, 0.86, 1.05, 0.056),
                           (0.070, 1.30, 0.80, 0.044), (-0.062, 1.08, 0.96, 0.046)):
        bonds = [(0.3 * e, 0.06 * r, -0.040), (0.6 * e, 0.10 * r, -0.160 * c), (0.9 * e, 0.13 * r, -0.300 * c),
                 (1.2 * e, 0.16 * r, -0.440 * c), (1.6 * e, 0.22 * r, -0.540 * c)]
        queue = queue + meche([depart] + [depart + np.array(b) for b in bonds], large, (1, 0, 0), 0.42)
    a.piece("queue", queue, ARGENT)

    # ----- les jambes : courtes et épaisses, le genou et le boulet marqués. Trois sont plantées ; l'antérieur gauche est
    #       levé haut, le sabot pendant. Au bout de chacune, ses fanons. -----
    hanche = [0.070, 0.118, 0.084, 0.050, 0.036, 0.040, 0.036]         # un rayon par articulation, de la croupe au paturon
    epaule = [0.062, 0.074, 0.058, 0.046, 0.034, 0.038, 0.034]
    plantees = (("avant_D", [(-0.048, -0.220, 0.590), (-0.074, -0.214, 0.490), (-0.084, -0.206, 0.390), (-0.088, -0.218, 0.240),
                             (-0.088, -0.214, 0.150), (-0.088, -0.214, 0.075), (-0.088, -0.222, 0.044)], epaule),
                ("arriere_G", [(0.080, 0.205, 0.580), (0.100, 0.180, 0.485), (0.104, 0.160, 0.380), (0.104, 0.250, 0.240),
                               (0.104, 0.232, 0.150), (0.104, 0.218, 0.075), (0.104, 0.206, 0.044)], hanche),
                ("arriere_D", [(-0.080, 0.175, 0.580), (-0.100, 0.140, 0.485), (-0.104, 0.110, 0.380), (-0.104, 0.190, 0.240),
                               (-0.104, 0.162, 0.150), (-0.104, 0.138, 0.075), (-0.104, 0.122, 0.044)], hanche))
    for nom, points, rayons_ in plantees:
        a.piece("patte_" + nom, jambe(points, rayons_), None)
        a.piece("sabot_" + nom, sabot(), CORNE, pos=(points[-1][0], points[-1][1] - 0.010, 0.0), poil=False)
        a.piece("fanon_" + nom, fanons(points[-2], 0.0), FANONS)
    levee = [(0.048, -0.220, 0.590), (0.074, -0.226, 0.490), (0.086, -0.276, 0.420), (0.092, -0.400, 0.408),
             (0.095, -0.394, 0.312), (0.095, -0.366, 0.240), (0.095, -0.344, 0.212)]
    a.piece("patte_avant_G", jambe(levee, epaule), None)
    pend = (Vector(levee[-1]) - Vector(levee[-2])).normalized()
    a.piece("sabot_avant_G", sabot(), CORNE, mat=A.cadre(Vector(levee[-1]) + pend * 0.050, -pend, (0, 1, 0)), poil=False)
    a.piece("fanon_avant_G", fanons(levee[-2], levee[-2][2] - 0.105), FANONS)
    REPERES.update(nuque=tuple(bout), tete=tuple(T @ Vector((0, 0.020, 0.090))), oreille_G=tuple(T @ Vector((0.040, 0.034, 0.024))),
                   oreille_D=tuple(T @ Vector((-0.040, 0.034, 0.024))))
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py cheval). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Le modèle est saisi en plein passage, l'antérieur gauche levé : chaque jambe a donc ses deux os à elle, à sa vraie place
# (pas de miroir), et ses pièces passent de l'os du haut à celui du bas au genou (ou au jarret).

from poses import Pose, borne, cloche, onde

# chaque jambe : l'os du haut et son épaule (ou sa hanche), l'os du bas et son genou (ou son jarret), et les deux points
# de la jambe qui encadrent le genou
JAMBES = {
    ("avant", "_G"): ("av_g", (0.048, -0.220, 0.590), "av_g2", (0.092, -0.400, 0.408), (0.086, -0.276, 0.420), (0.095, -0.394, 0.312)),
    ("avant", "_D"): ("av_d", (-0.048, -0.220, 0.590), "av_d2", (-0.084, -0.206, 0.390), (-0.074, -0.214, 0.490), (-0.088, -0.218, 0.240)),
    ("arriere", "_G"): ("ar_g", (0.080, 0.205, 0.580), "ar_g2", (0.104, 0.250, 0.240), (0.104, 0.160, 0.380), (0.104, 0.232, 0.150)),
    ("arriere", "_D"): ("ar_d", (-0.080, 0.175, 0.580), "ar_d2", (-0.104, 0.190, 0.240), (-0.104, 0.110, 0.380), (-0.104, 0.162, 0.150)),
}
OS = [("racine", None, (0, 0, 0)),
      ("corps", "racine", (0.0, 0.120, 0.540)),                 # vers les hanches : il se cabre autour de son arrière-main
      ("cou", "corps", (0.0, -0.170, 0.560)),                   # le pied de l'encolure
      ("tete", "cou", (0.037, -0.342, 0.908)),                  # la nuque (REPERES["nuque"])
      ("oreille_g", "tete", (0.084, -0.336, 1.014)),
      ("oreille_d", "tete", (-0.019, -0.378, 1.003)),
      ("queue", "corps", (0.0, 0.215, 0.610))]
for _h, _ph, _b, _pb, _av, _ap in JAMBES.values():
    OS += [(_h, "corps", _ph), (_b, _h, _pb)]


def _jambe(rang):
    """Une pièce de jambe : l'os du haut au-dessus du genou, celui du bas en dessous, avec un fondu de quelques cm.
    (Les points d'une pièce de droite arrivent en miroir, X retourné : on retourne le genou de même.)"""
    def poids(points, cote):
        h, _ph, b, genou, avant, apres = JAMBES[(rang, cote)]
        m = np.array([-1.0, 1.0, 1.0]) if cote == "_D" else np.ones(3)
        g, u, v = np.array(genou) * m, np.array(avant) * m, np.array(apres) * m
        sens = (g - u) / np.linalg.norm(g - u) + (v - g) / np.linalg.norm(v - g)
        w = K.lisse((points - g) @ (sens / np.linalg.norm(sens)) / 0.04 + 0.5)
        return {h: 1 - w, b: w}
    return poids


def _bas(rang):
    """Le sabot et les fanons : tout sur l'os du bas de leur jambe."""
    return lambda points, cote: {JAMBES[(rang, cote)][2]: np.ones(len(points))}


def _oreille(points, cote):
    return {"oreille_g" if cote == "_G" else "oreille_d": np.ones(len(points))}


PORTEURS = [("corps", "corps"), ("cou", "cou"), ("criniere", "cou"), ("queue", "queue"),
            ("tete", "tete"), ("naseau", "tete"), ("blanc", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("toupet", "tete"),
            ("oreille", _oreille, "oreille_g"), ("pavillon", _oreille, "oreille_g"),
            ("patte_avant", _jambe("avant"), "av_g"), ("patte_arriere", _jambe("arriere"), "ar_g"),
            ("sabot_avant", _bas("avant"), "av_g2"), ("sabot_arriere", _bas("arriere"), "ar_g2"),
            ("fanon_avant", _bas("avant"), "av_g2"), ("fanon_arriere", _bas("arriere"), "ar_g2"),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def leve(p, nom, x):
    """Une jambe de devant pliée haut (x = 1, comme l'antérieur gauche du modèle) ou dépliée sous lui (x = 0)."""
    if nom == "av_g":
        p.add("av_g", rot=(42 * (1 - x), 0, 0))
        p.add("av_g2", rot=(-42 * (1 - x), 0, 0))
    else:
        p.add(nom, rot=(-40 * x, 0, 0))
        p.add(nom + "2", rot=(40 * x, 0, 0))


def campe(p, demi=0.35):
    """La pose d'attente : l'antérieur gauche à demi reposé (il frappe du pied de là), les autres sous lui."""
    leve(p, "av_g", demi)
    return p


def repos(t):
    """Il se tient fier, l'encolure haute : il respire, gratte deux fois le sol du pied gauche (il s'impatiente), tourne
    la tête vers nous, fouette de la queue, tourne une oreille ; il cligne."""
    p = Pose()
    r = onde(t, 2)
    gratte = cloche(t, 0.30, 0.05) + cloche(t, 0.42, 0.05)
    p.add("corps", ech=(1 + 0.010 * r, 1, 1 + 0.014 * r))
    leve(p, "av_g", 0.35 + 0.35 * gratte)
    p.add("cou", rot=(2 * r, 0, 6 * cloche(t, 0.62, 0.14)))
    p.add("tete", rot=(0, 0, 10 * cloche(t, 0.62, 0.14)))
    p.add("queue", rot=(0, 0, 14 * cloche(t, 0.80, 0.06) * onde(t, 6)))
    p.add("oreille_d", rot=(0, 0, -30 * cloche(t, 0.15, 0.05)))
    p.add("oreille_g", rot=(0, 0, 25 * cloche(t, 0.70, 0.05)))
    p.ouvert = 1 - cloche(t, 0.52, 0.02)
    return p


def avance(t):
    """Son passage : un trot cadencé, les genoux montés haut. Les diagonales vont ensemble (antérieur gauche et
    postérieur droit, puis l'autre paire) ; l'encolure hoche, la queue balance."""
    p = Pose()
    g = 0.5 + 0.5 * math.cos(math.tau * t)                 # 1 : l'antérieur gauche est en l'air (la pose du modèle)
    d = 1 - g
    leve(p, "av_g", g)
    leve(p, "av_d", d)
    p.add("ar_d", rot=(-14 * g, 0, 0))
    p.add("ar_d2", rot=(26 * g, 0, 0))
    p.add("ar_g", rot=(-14 * d, 0, 0))
    p.add("ar_g2", rot=(26 * d, 0, 0))
    p.add("corps", pos=(0, 0, 0.018 * abs(onde(t, 1))), rot=(0, 2 * onde(t, 1), 0))
    p.add("cou", rot=(4 * onde(t, 2), 0, 0))
    p.add("tete", rot=(-3 * onde(t, 2), 0, 0))
    p.add("queue", rot=(0, 0, 8 * onde(t, 1)))
    return p


def mange(t):
    """Il baisse l'encolure jusqu'à l'herbe, broute (de petits coups de tête), puis relève la tête en mâchant et nous
    regarde."""
    p = campe(Pose(), 0.0)
    bas = 1 - cloche(t, 0.86, 0.14)
    broute = abs(onde(t, 6)) * bas
    p.add("cou", rot=(58 * bas, 0, -6 * bas))
    p.add("tete", rot=(22 * bas + 6 * broute, 0, -8 * bas))
    p.add("queue", rot=(0, 0, 8 * onde(t, 3)))
    p.ouvert = 1 - cloche(t, 0.92, 0.02)
    return p


def joie(t):
    """Il se cabre : l'avant-main monte haut, les deux antérieurs battent l'air, la queue en panache ; puis il retombe
    sur ses quatre pieds et reprend la pose de repos."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85)) if t < 0.85 else 0.0
    bat = onde(t, 4) * env
    p.add("corps", rot=(-30 * env, 0, 0), pos=(0, 0, 0.02 * env))
    p.add("ar_g", rot=(30 * env, 0, 0))                         # les postérieurs restent plantés : ils compensent
    p.add("ar_d", rot=(30 * env, 0, 0))
    leve(p, "av_g", 0.35 + (0.30 + 0.25 * bat) * env)
    leve(p, "av_d", (0.65 - 0.25 * bat) * env)
    p.add("cou", rot=(-10 * env, 0, 0))
    p.add("tete", rot=(-14 * env, 0, 0))
    p.add("queue", rot=(-25 * env, 0, 10 * onde(t, 5) * env))
    return p


def dort(t):
    """Il dort debout, comme les chevaux : l'encolure basse, un postérieur au repos sur la pince, les oreilles de côté,
    les yeux fermés ; il respire lentement."""
    p = campe(Pose(), 0.0)
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", ech=(1 + 0.012 * r, 1, 1 + 0.018 * r))
    p.add("cou", rot=(26, 0, 0))
    p.add("tete", rot=(14, 0, 0))
    p.add("ar_g2", rot=(14, 0, 0))
    p.add("oreille_g", rot=(0, -20, 0))
    p.add("oreille_d", rot=(0, 20, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("cheval", styles.style_de("cheval"), sys.modules[__name__]),
              "Cheval" if ROBE == CHOISIE else "Cheval " + ROBE)
