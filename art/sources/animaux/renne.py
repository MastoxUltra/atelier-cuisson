"""Le renne en peluche : un renne de velours ras, fauve taupe, le cou crème d'où pend une grande collerette en mèches,
le miroir crème sous la queue, le bas des jambes chocolat cerclé d'un bracelet crème au-dessus de gros sabots fendus.
Sur la tête, ses bois immenses, en velours ivoire : deux grandes crosses qui partent en arrière puis reviennent en
avant, et d'un seul côté la pelle qui avance au-dessus du nez. Un marcheur têtu qui fend le vent : tête basse, le nez
en avant, l'antérieur gauche levé pour le pas suivant, le sourcil froncé.

    python renne.py        fabrique la fiche art/apercus/animaux/renne.png (velours ras, palier 3)
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


def propres(points, eps=2e-4):
    """Les points d'un tracé sans doublons consécutifs (un tube dont deux points se suivent à l'identique se déforme en NaN) ;
    au moins deux points, écartés d'un millimètre au pire."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie

TAUPE = M.hexa("#b08f70")                     # la dominante : fauve taupe, café au lait foncé (le poil la fonce un peu)
CREME = M.hexa("#fbf3e2")                     # le cou, la collerette, le miroir, les bracelets
CHOCOLAT = M.hexa("#5e4030")                  # le bout du nez, le bas des jambes
IVOIRE = M.hexa("#f5ecd8")                    # l'accent : les bois, en velours
CHARBON = M.hexa("#2e2a2a")                   # les sabots, la truffe
TOURNE = -24                                  # sur la fiche, posé de biais (on voit les crosses de côté) ; 0 pour le jeu
CROUPE = Vector((0.0, 0.27, 0.50))
COL = math.radians(14)                        # l'encolure part un peu vers sa gauche, du côté où il regarde
AVANT = Vector((math.sin(COL), -math.cos(COL), 0.0))
FLANC = np.array([math.cos(COL), math.sin(COL), 0.0])
BASE = Vector((0.0, -0.200, 0.540))           # le pied de l'encolure, entre les épaules
ARC = [(0.0, 0.0), (0.060, 0.045), (0.130, 0.070), (0.200, 0.068), (0.255, 0.040)]    # (avance, monte) : presque à plat, tête basse
LACET, PIQUE, PENCHE = 20.0, 34.0, -6.0       # la tête : tournée vers nous, le nez bas et en avant
GROSSE = 1.35


def meche(chemin, large, face, plat=0.36, long_pointe=0.93, cotes=20):
    """Une mèche plate (le geste du cheval) : un fuseau tourné, aplati, couché le long d'un chemin ; « face » : la
    direction de son épaisseur."""
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


def jambe(points, rayons):
    """Une jambe : fauve en haut, chocolat sous le genou, un bracelet crème juste au-dessus du sabot."""
    chemin = A.courbe(points, 6)
    rayon = lambda t: float(np.interp(t, np.linspace(0, 1, len(rayons)), rayons))
    return K.tube_peint(chemin, rayon, [(0.50, TAUPE), (0.80, CHOCOLAT), (0.93, CREME), (1, CHOCOLAT)], 20)


def sabot():
    """Un gros sabot fendu en deux doigts écartés, qui s'étalent sur la neige."""
    tout = None
    for c in (1, -1):
        doigt = A.boule(1.0, 24, 12).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.028, 0.050, 0.030)
        doigt.pose((c * 0.024, -0.012, 0.030), (0, 0, c * 10))
        tout = doigt if tout is None else tout + doigt
    return tout


def bois(c, pelle):
    """Un bois, dans le repère du crâne (X sa gauche, -Y l'avant, Z le haut) : un gros merrain de velours qui s'écarte,
    part en arrière, monte et revient en crosse vers l'avant, trois andouillers tournés vers l'avant ; et parfois la
    pelle, une lame aplatie debout au-dessus du nez."""
    def p(x, y, z):
        return (c * x, y, z)
    merrain = A.courbe([p(0.035, 0.0, 0.0), p(0.100, 0.035, 0.065), p(0.180, 0.080, 0.140), p(0.250, 0.085, 0.230),
                        p(0.285, 0.040, 0.315), p(0.270, -0.030, 0.370), p(0.230, -0.080, 0.385)], 6)
    tout = A.tube(merrain, lambda t: 0.024 - 0.013 * t, 16)
    for depart, vers, long in (((0.180, 0.080, 0.140), (0.20, -0.85, 0.50), 0.100), ((0.250, 0.085, 0.230), (0.15, -0.70, 0.70), 0.110),
                               ((0.285, 0.040, 0.315), (0.25, -0.30, 0.92), 0.085)):
        d = np.array(p(*depart))
        v = np.array(p(*vers)) / np.linalg.norm(vers)
        bout = d + v * long + np.array([0, 0, 0.015])
        tout = tout + A.tube(A.courbe([d, d + v * long * 0.55, bout], 4), lambda t: 0.015 - 0.008 * t, 14)
    if pelle:
        chemin = A.courbe([p(0.045, -0.005, 0.030), p(0.060, -0.070, 0.055), p(0.050, -0.130, 0.048), p(0.030, -0.172, 0.020)], 6)
        lame = A.tube(chemin, lambda t: 0.012 + 0.024 * math.sin(math.pi * min(t * 1.3, 1.0)), 16)
        lame.v[:, 0] = c * 0.048 + (lame.v[:, 0] - c * 0.048) * 0.40                 # aplatie de côté : une lame debout
        tout = tout + lame
    return tout


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement : le geste du cheval)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def construire():
    a = K.Animal("renne")
    a.taille = 1.60

    # ----- le corps : un tonneau tourné de la croupe au poitrail puis couché (X la gauche, Y le dos, Z l'avant) ;
    #       le miroir crème autour de la queue -----
    def galbe(v):
        s = v.copy()
        s[:, 0] *= 0.96 * (1 + 0.12 * np.exp(-((v[:, 2] - 0.48) / 0.08) ** 2))                # les épaules
        s[:, 1] *= np.where(v[:, 1] > 0, 1 + 0.10 * np.exp(-((v[:, 2] - 0.44) / 0.07) ** 2), 0.94)  # le garrot, le ventre
        return s
    corps = A.tour(A.profil([(0, 0), (0.118, 0.010), (0.168, 0.060), (0.182, 0.140), (0.176, 0.250), (0.166, 0.340),
                             (0.178, 0.430), (0.172, 0.500), (0.132, 0.555), (0, 0.598)], 6), 56)
    K.bandes(corps, [(0.070, CREME), (9, TAUPE)])
    a.piece("corps", corps.sculpte(galbe), None, pos=CROUPE, rot=(87, 0, 0))

    # ----- l'encolure : crème, couchée presque à plat le long de son arc -----
    enc = K.Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in ARC], FLANC)
    L = enc.long
    parts, rayons = [0.03, 0.20, 0.45, 0.70, 0.90, 0.985], [0.178, 0.168, 0.142, 0.116, 0.098, 0.086]
    pc = A.profil([(0, 0)] + [(r, f * L) for r, f in zip(rayons, parts)] + [(0, 1.01 * L)], 6)
    a.piece("cou", A.tour(pc, 40).etire(0.86, 1.0, 1.0).sculpte(enc.couche), CREME)

    # ----- la collerette : de longues mèches crème qui pendent sous le cou, comme une barbe -----
    haut = np.array([0.0, 0.0, 1.0])
    collerette = None
    for i, f in enumerate(np.linspace(0.10, 0.94, 8)):
        c_, av, nq = enc.cadre(f * L)
        r = float(np.interp(f, parts, rayons))
        k = (1.05 + 0.65 * math.sin(math.pi * f)) * (0.82 if i % 2 else 1.0)
        dessous = c_ - nq * r * 0.80
        chemin = [dessous + nq * 0.030, dessous - nq * 0.010 + av * 0.008, dessous - haut * 0.090 * k + av * 0.022,
                  dessous - haut * 0.170 * k + av * 0.012]
        m = meche(chemin, 0.054 if i % 2 else 0.060, FLANC, 0.40)
        collerette = m if collerette is None else collerette + m
    a.piece("collerette", collerette, CREME)

    # ----- la tête : longue, le museau large et velu ; dans son repère, X la gauche, Y le chanfrein, Z vers le nez.
    #       Le bout du nez chocolat -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0, 0, 0), nez) @ Matrix.Rotation(math.radians(PENCHE), 4, Vector((0, 0, 1))) @ A.repere(ech=(GROSSE,) * 3)
    bout = Vector(enc.cadre(L)[0])
    T = A.repere(bout - T.to_3x3() @ Vector((0, -0.020, 0.060))) @ T
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.050, 0.160))

    def museau(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 0] *= 0.84 + 0.14 * np.exp(-((z - 0.245) / 0.035) ** 2)
        s[:, 1] *= np.where(v[:, 1] > 0, 1.0, 1.0 + 0.22 * np.exp(-((z - 0.080) / 0.045) ** 2))      # la ganache
        return s
    tete = A.tour(A.profil([(0, 0), (0.042, 0.008), (0.064, 0.040), (0.068, 0.085), (0.058, 0.135), (0.050, 0.180),
                            (0.054, 0.215), (0.058, 0.245), (0.048, 0.272), (0, 0.286)], 6), 56)
    K.bandes(tete, [(0.240, TAUPE), (9, CHOCOLAT)])
    a.piece("tete", tete.sculpte(museau), None, mat=T)
    for nom, c in (("G", 1), ("D", -1)):
        a.rustine("naseau_" + nom, "tete", T @ Vector((0, 0, 0.262)), T3 @ Vector((c * 0.55, 0.40, 0.73)), 0.20, CHARBON, 0.0025, 0)

    # ----- les yeux : petits et vivants ; un sourcil crème froncé vers le nez, du côté qu'il nous tend -----
    centre = T @ Vector((0, 0, 0.100))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.66, 0.60, 0.20)))
        a.oeil("oeil_" + nom, pos + n * 0.004, n, 0.017)
    fronce = [T3 @ Vector((0.42 + 0.10 * u, 0.90 - 0.14 * u * u, 0.02 + 0.30 * u)) for u in np.linspace(0, 1, 7)]
    a.broderie("sourcil_g", A.courbe(propres(a.trace("tete", centre, fronce, 0.004)), 4), 0.0040, CREME)

    # ----- les oreilles : courtes et rondes, basses sur les côtés, couchées en arrière contre le vent -----
    po = A.profil([(0, 0), (0.024, 0.010), (0.030, 0.034), (0.024, 0.060), (0.010, 0.078), (0, 0.083)], 6)
    for nom, c in (("G", 1), ("D", -1)):
        vers = (T3 @ Vector((c * 0.85, 0.30, -0.40))).normalized()
        E = A.cadre(T @ Vector((c * 0.052, 0.030, 0.035)) - vers * 0.010, vers, T3 @ Vector((0, 1, 0)))
        a.piece("oreille_" + nom, A.tour(po, 28).etire(1.0, 0.45, 1.0), TAUPE, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 20).etire(0.60, 0.40, 0.78).pose((0, 0.010, 0.012)), CREME, mat=E, poil=False)

    # ----- les bois : en velours ivoire, plantés sur le crâne ; la pelle à gauche seulement -----
    crane = T @ Vector((0, 0.058, 0.060))
    C = A.repere(crane, (0, 0, LACET))
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("bois_" + nom, bois(c, c > 0), IVOIRE, mat=C)

    # ----- la queue : une petite houppe crème, relevée sur le miroir -----
    a.piece("queue", A.boule(1.0, 24, 12).etire(0.034, 0.040, 0.058), CREME, pos=(0, 0.292, 0.585), rot=(-30, 0, 0))

    # ----- les jambes : trois plantées, l'antérieur gauche levé pour le pas suivant ; au bout, les gros sabots fendus -----
    hanche = [0.088, 0.118, 0.092, 0.058, 0.040, 0.046, 0.042]
    epaule = [0.088, 0.104, 0.078, 0.058, 0.040, 0.046, 0.042]
    plantees = (("avant_D", [(-0.048, -0.220, 0.580), (-0.074, -0.214, 0.480), (-0.084, -0.236, 0.380), (-0.088, -0.226, 0.240),
                             (-0.088, -0.210, 0.150), (-0.088, -0.212, 0.080), (-0.088, -0.222, 0.050)], epaule),
                ("arriere_G", [(0.080, 0.205, 0.570), (0.102, 0.170, 0.470), (0.106, 0.140, 0.370), (0.106, 0.270, 0.245),
                               (0.106, 0.232, 0.150), (0.106, 0.216, 0.080), (0.106, 0.206, 0.050)], hanche),
                ("arriere_D", [(-0.080, 0.175, 0.570), (-0.102, 0.135, 0.470), (-0.106, 0.095, 0.370), (-0.106, 0.215, 0.245),
                               (-0.106, 0.162, 0.150), (-0.106, 0.138, 0.080), (-0.106, 0.122, 0.050)], hanche))
    for nom, points, rayons_ in plantees:
        a.piece("patte_" + nom, jambe(points, rayons_), None)
        a.piece("sabot_" + nom, sabot(), CHARBON, pos=(points[-1][0], points[-1][1] - 0.006, 0.0), poil=False)
    levee = [(0.048, -0.220, 0.580), (0.072, -0.226, 0.480), (0.084, -0.272, 0.410), (0.090, -0.392, 0.398),
             (0.093, -0.388, 0.302), (0.093, -0.362, 0.232), (0.093, -0.342, 0.205)]
    a.piece("patte_avant_G", jambe(levee, epaule), None)
    pend = (Vector(levee[-1]) - Vector(levee[-2])).normalized()
    a.piece("sabot_avant_G", sabot(), CHARBON, mat=A.cadre(Vector(levee[-1]) + pend * 0.032, -pend, (0, 1, 0)), poil=False)
    if TOURNE:
        tourner(a, TOURNE)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("renne", styles.style_de("renne"), sys.modules[__name__]), "Renne")
