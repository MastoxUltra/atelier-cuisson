"""Le renne en peluche : un renne de velours ras, fauve taupe, le cou crème d'où pend une grande collerette en mèches,
le miroir crème sous la queue, le bas des jambes chocolat cerclé d'un bracelet crème au-dessus de gros sabots fendus.
Sur la tête, ses bois immenses, en velours ivoire : deux grandes crosses qui partent en arrière puis reviennent en
avant, et d'un seul côté la pelle qui avance au-dessus du nez. Un marcheur têtu qui fend le vent : tête basse, le nez
en avant, l'antérieur gauche levé pour le pas suivant.

    python renne.py        fabrique la fiche art/apercus/animaux/renne.png (velours ras, palier 3)

Les 5 traits de l'espèce (photos de Commons, 15/10) : 1. un cervidé trapu, l'encolure épaisse et l'épais cou crème avec une
collerette de poils ; 2. les bois immenses, ramifiés, des deux sexes, avec une pelle au-dessus du nez ; 3. un museau large
et velu au nez sombre ; 4. de grands sabots larges et fendus ; 5. le pelage fauve taupe, le ventre, la croupe et la queue crème.
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

GONFLAGE = True       # la base aux volumes gonflés de l'Artiste (fusion.py) : jointures fondues, bouts arrondis
DEGONFLE = 0.86       # ... qui élargit les volumes d'environ 30 % : on part plus mince


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
TOURNE = 0                                  # sur la fiche, posé de biais (on voit les crosses de côté) ; 0 pour le jeu
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
    tout = A.tube(merrain, lambda t: 0.017 - 0.009 * t, 16)                  # fin : le gonflage les épaissit d'un tiers
    for depart, vers, long in (((0.180, 0.080, 0.140), (0.20, -0.85, 0.50), 0.100), ((0.250, 0.085, 0.230), (0.15, -0.70, 0.70), 0.110),
                               ((0.285, 0.040, 0.315), (0.25, -0.30, 0.92), 0.085)):
        d = np.array(p(*depart))
        v = np.array(p(*vers)) / np.linalg.norm(vers)
        bout = d + v * long + np.array([0, 0, 0.015])
        tout = tout + A.tube(A.courbe([d, d + v * long * 0.55, bout], 4), lambda t: 0.010 - 0.005 * t, 14)
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
    corps = A.tour(A.profil([(r * DEGONFLE, z) for r, z in ((0, 0), (0.118, 0.010), (0.168, 0.060), (0.182, 0.140), (0.176, 0.250),
                             (0.166, 0.340), (0.178, 0.430), (0.172, 0.500), (0.132, 0.555), (0, 0.598))], 6), 56)
    K.bandes(corps, [(0.070, CREME), (9, TAUPE)])
    a.piece("corps", corps.sculpte(galbe), None, pos=CROUPE, rot=(87, 0, 0))

    # ----- l'encolure : crème, couchée presque à plat le long de son arc -----
    enc = K.Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in ARC], FLANC)
    L = enc.long
    parts, rayons = [0.03, 0.20, 0.45, 0.70, 0.90, 0.985], [r * 0.90 for r in (0.178, 0.168, 0.142, 0.116, 0.098, 0.086)]
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
    # (plus de sourcil froncé : l'auteur y lit de la colère ; l'air têtu vient de la tête basse et du nez en avant)

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
    hanche = [r * 0.82 for r in (0.088, 0.118, 0.092, 0.058, 0.040, 0.046, 0.042)]
    epaule = [r * 0.82 for r in (0.088, 0.104, 0.078, 0.058, 0.040, 0.046, 0.042)]
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


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py renne). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.566                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.044, 0.645)),
    ('cou', 'corps', (-0.049, -0.112, 0.664)),
    ('tete', 'cou', (-0.114, -0.368, 0.593)),
    ('oreille_G', 'tete', (-0.049, -0.454, 0.641)),
    ('patte_av_D', 'corps', (-0.161, -0.155, 0.568)),
    ('patte_ar_G', 'corps', (0.166, 0.100, 0.562)),
    ('patte_av_G', 'corps', (-0.016, -0.235, 0.567)),
    ('queue', 'corps', (0.099, 0.232, 0.588)),
]

PORTEURS = [
    ('patte_arriere', 'patte_ar', True), ('sabot_arriere', 'patte_ar', True), ('patte_avant', 'patte_av', True),
    ('sabot_avant', 'patte_av', True), ('oeil_reflet', 'tete'), ('collerette', 'corps'), ('sourcil_g', 'tete'),
    ('pavillon', 'oreille', True), ('oreille', 'oreille', True), ('naseau', 'tete'), ('corps', 'corps'),
    ('queue', 'queue'), ('tete', 'tete'), ('oeil', 'tete'), ('bois', 'corps'), ('cou', 'cou'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('cou', rot=(2 * r, 0, 8 * g - 6 * d))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add('oreille_G', rot=(0, 0, 20 * cloche(t, 0.50, 0.05) - 8 * g))
    p.add('oreille_D', rot=(0, 0, -20 * cloche(t, 0.88, 0.05) + 6 * d))
    p.add('queue', rot=(0, 0, 10 * onde(t, 1)))
    p.ouvert = borne(1 - 0.3 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.62, 0.02))
    return p


def avance(t):
    """Sa marche : les pattes alternent, le corps oscille, la tête dodeline."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 26.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('cou', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('tete', rot=(3 - 2 * onde(t, 2, -0.2), -2 * c, -2 * s))
    p.paire('oreille', rot=(-8 + 3 * onde(t, 2, -0.25), 0, 0))
    p.add('queue', rot=(-6, 0, -10 * s))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('cou', rot=(34 * bas + 4 * coups, 0, 5 * leve))
    p.add('tete', rot=(18 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.paire('oreille', rot=(-6 * bas + 5 * leve, 0, 0))
    p.add('queue', rot=(0, 0, -7 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.170 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.311), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
