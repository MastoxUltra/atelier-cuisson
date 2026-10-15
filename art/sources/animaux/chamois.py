"""Le chamois en peluche : l'équilibriste des crêtes, farouche et sûr de lui. Il a mis une patte avant sur un rocher
qu'on ne voit pas, le poids sur l'arrière-train, le dos rond ; le cou haut, il a tourné la tête vers le vent, le nez
levé, une oreille pointée, l'autre qui écoute derrière. Une robe fauve miel, la raie noire sur l'échine, un liseré
sombre au bas du flanc, le ventre crème ; un visage crème barré de deux bandeaux noirs qui passent par les yeux ;
de petites cornes noires toutes droites, en crochet au bout. Les chaussettes noires, deux onglons au bout de chaque
patte, un toupet de queue noir sur un miroir crème.

    python chamois.py        fabrique la fiche art/apercus/animaux/chamois.png (style du palier : C, velours ras)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import matieres as M
import peluche as K
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

FAUVE = M.hexa("#cc8b4b")                     # la dominante (registre du 14/10 : fauve miel #d9a066) ; le velours ras
                                              # éclaircit : #d9a066 sortait pêche sur la première fiche
NOIRC = M.hexa("#1c1513")                     # l'accent : un noir chaud (raie, liseré, bandeaux, chaussettes, queue)
CORNE = M.hexa("#1d1a1a")                     # les cornes et les onglons, en feutrine
CREME = K.CREME

CROUPE = Vector((0.0, 0.245, 0.430))          # le bout arrière du corps (une pièce tournée, couchée vers l'avant)
CABRE = 10.0                                  # le poitrail plus haut que la croupe : le poids est sur l'arrière
LONG = 0.52                                   # la longueur du corps
COL = math.radians(8)                         # l'encolure part un peu vers sa gauche, du côté où il regarde
AVANT = Vector((math.sin(COL), -math.cos(COL), 0.0))
FLANC = np.array([math.cos(COL), math.sin(COL), 0.0])
BASE = Vector((0.0, -0.150, 0.470))           # le pied de l'encolure, enfoui entre les épaules
ARC = [(0.0, 0.0), (0.014, 0.090), (0.030, 0.170), (0.050, 0.236), (0.066, 0.268)]   # (avance, monte) : haute, qui se tend
LACET, PIQUE, PENCHE = 22.0, 4.0, -8.0        # la tête : tournée vers nous, le nez levé vers le vent, un rien penchée
GROSSE = 1.36                                 # une tête de peluche : c'est elle qu'on lit de loin
TOURNE = 0                                    # la fiche le prend de trois quarts sans le tourner
ALPHA, GAMMA = 64.0, 34.0                     # l'antérieur gauche posé sur le rocher : le haut part de 64° vers l'avant,
                                              # le bas de 34° (le genou plie de 30°) ; le sabot est à ~14 cm du sol


def gauss(x):
    return np.exp(-x * x)


def distance_ligne(y, z, ligne):
    """La distance de chaque point (y, z) à une ligne brisée, et où il tombe le long d'elle (de 0 à 1)."""
    d, ou = np.full(len(y), 9.0), np.zeros(len(y))
    total = sum(math.dist(ligne[i], ligne[i + 1]) for i in range(len(ligne) - 1))
    fait = 0.0
    for (y0, z0), (y1, z1) in zip(ligne[:-1], ligne[1:]):
        dy, dz = y1 - y0, z1 - z0
        n2 = dy * dy + dz * dz
        t = np.clip(((y - y0) * dy + (z - z0) * dz) / n2, 0.0, 1.0)
        e = np.hypot(y - (y0 + t * dy), z - (z0 + t * dz))
        mieux = e < d
        d[mieux], ou[mieux] = e[mieux], ((fait + t * math.sqrt(n2)) / total)[mieux]
        fait += math.sqrt(n2)
    return d, ou


def membre(points, rayons, paliers):
    """Une patte : un boudin qui passe par ses articulations, un rayon à chacune, peint par tronçons (la chaussette)."""
    return K.tube_peint(A.courbe(points, 6), lambda t: float(np.interp(t, np.linspace(0, 1, len(rayons)), rayons)), paliers, 20)


def sabot():
    """Un pied fourchu : deux onglons de feutrine noire, la pince un peu en avant."""
    def onglon(cote):
        def f(v):
            s = v.copy()
            s[:, 1] -= 0.009 * K.lisse((0.026 - v[:, 2]) / 0.026)
            s[:, 0] += cote * 0.002 * K.lisse((0.020 - v[:, 2]) / 0.020)        # les deux pinces s'écartent un peu
            return s
        m = A.tour(A.profil([(0, 0), (0.0125, 0.002), (0.0135, 0.012), (0.0105, 0.026), (0, 0.031)], 4), 24)
        return m.etire(0.82, 1.22, 1.0).sculpte(f).pose((cote * 0.0118, -0.004, 0.0))
    return onglon(1) + onglon(-1)


def corne(T, cote):
    """Une corne : elle monte toute droite du front, puis se recourbe en crochet vers l'arrière ; annelée à la base."""
    chemin = [(cote * 0.019, 0.044, 0.050), (cote * 0.021, 0.092, 0.058), (cote * 0.023, 0.134, 0.056),
              (cote * 0.025, 0.163, 0.040), (cote * 0.026, 0.176, 0.014), (cote * 0.026, 0.168, -0.013),
              (cote * 0.025, 0.148, -0.027), (cote * 0.024, 0.128, -0.028)]
    points = [T @ Vector(p) for p in A.courbe(chemin, 6)]

    def rayon(t):
        anneaux = 1 + 0.10 * math.cos(46 * t) * max(0.0, 1 - t / 0.42)
        return GROSSE * (0.0112 - 0.0078 * t ** 0.9) * anneaux
    return A.tube(points, rayon, 14)


# ---------------------------------------------------------------- les pattes : une seule source pour le modèle et le squelette
# Chaque patte : sept points, de l'épaule (ou de la hanche) au haut du sabot, avec le genou (ou le jarret) au troisième ;
# un rayon par point, le genou et le boulet marqués. (x : la gauche en +, y : l'arrière en +, z : la hauteur.)
RAYONS_AVANT = [0.058, 0.046, 0.034, 0.021, 0.027, 0.020, 0.019]       # le genou (3e) et le boulet (5e) gonflés
RAYONS_ARRIERE = [0.076, 0.062, 0.036, 0.022, 0.028, 0.020, 0.019]     # le jarret (3e) et le boulet (5e)
AVANT_D = [(-0.060, -0.150, 0.500), (-0.064, -0.134, 0.396), (-0.060, -0.122, 0.290), (-0.056, -0.108, 0.176),
           (-0.056, -0.094, 0.082), (-0.056, -0.088, 0.050), (-0.056, -0.084, 0.030)]          # posé, un peu en arrière
ARRIERE_D = [(-0.072, 0.200, 0.452), (-0.092, 0.148, 0.350), (-0.082, 0.272, 0.226), (-0.070, 0.244, 0.130),
             (-0.066, 0.232, 0.064), (-0.066, 0.224, 0.044), (-0.066, 0.218, 0.030)]            # le poids est sur lui : jarret marqué
ARRIERE_G = [(0.072, 0.200, 0.452), (0.092, 0.140, 0.350), (0.084, 0.228, 0.226), (0.074, 0.188, 0.130),
             (0.070, 0.158, 0.064), (0.070, 0.148, 0.044), (0.070, 0.142, 0.030)]               # passé en avant, sous le ventre


def tourne_x(v, degres):
    """Un vecteur tourné autour de X : > 0, ce qui est sous l'origine part vers l'arrière (comme les os du jeu)."""
    t = math.radians(degres)
    return np.array([v[0], v[1] * math.cos(t) - v[2] * math.sin(t), v[1] * math.sin(t) + v[2] * math.cos(t)])


def leve(points, alpha, gamma):
    """La même jambe, posée plus haut : le haut part de alpha° vers l'avant autour de l'épaule, le bas de gamma° autour du genou."""
    p = [np.array(q, float) for q in points]
    sortie = [p[0], p[0] + tourne_x(p[1] - p[0], -alpha), p[0] + tourne_x(p[2] - p[0], -alpha)]
    for q in p[3:]:
        sortie.append(sortie[2] + tourne_x(q - p[2], -gamma))
    return [tuple(float(x) for x in q) for q in sortie]


AVANT_G_POSE = [(0.060, y, z) for _x, y, z in AVANT_D]                                         # la même, à gauche, plantée
AVANT_G = [(x, y - 0.022, z) for x, y, z in leve(AVANT_G_POSE, ALPHA, GAMMA)]                  # posée sur le rocher
JAMBES = {                                    # le haut, son pivot, le bas, son pivot (le genou) et ses deux voisins
    ("avant", "_G"): ("av_g", AVANT_G[0], "av_g2", AVANT_G[2], AVANT_G[1], AVANT_G[3]),
    ("avant", "_D"): ("av_d", AVANT_D[0], "av_d2", AVANT_D[2], AVANT_D[1], AVANT_D[3]),
    ("arriere", "_G"): ("ar_g", ARRIERE_G[0], "ar_g2", ARRIERE_G[2], ARRIERE_G[1], ARRIERE_G[3]),
    ("arriere", "_D"): ("ar_d", ARRIERE_D[0], "ar_d2", ARRIERE_D[2], ARRIERE_D[1], ARRIERE_D[3]),
}


# ---------------------------------------------------------------- l'encolure et la tête : repères communs au modèle et au squelette
def _encolure():
    return K.Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in ARC], FLANC)


def _repere_tete(enc):
    """La matrice de la tête (X la gauche, Y le chanfrein, Z vers le nez) et le bout de l'encolure."""
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0, 0, 0), nez) @ Matrix.Rotation(math.radians(PENCHE), 4, Vector((0, 0, 1))) @ A.repere(ech=(GROSSE,) * 3)
    bout = Vector(enc.cadre(enc.long)[0])
    return A.repere(bout - T.to_3x3() @ Vector((0, -0.016, 0.052))) @ T, bout


_ENC = _encolure()
_T, _BOUT = _repere_tete(_ENC)


def construire():
    a = K.Animal("chamois")
    a.taille = 1.20

    # ----- le corps : tourné de la croupe au poitrail, puis couché ; dans la pièce, X est la gauche, Y le dos, Z l'avant.
    #       Une croupe ronde, un flanc creusé, un poitrail qui bombe : l'équilibriste. -----
    pc = A.profil([(0, 0), (0.078, 0.012), (0.116, 0.050), (0.128, 0.110), (0.116, 0.200), (0.106, 0.290),
                   (0.124, 0.380), (0.122, 0.445), (0.092, 0.495), (0, LONG)], 6)
    corps = A.tour(pc, 48)
    x, y, z = corps.v[:, 0], corps.v[:, 1], corps.v[:, 2]
    ang = np.abs(np.arctan2(x, y))                                   # 0 sur l'échine, pi sous le ventre
    t = np.tile(np.asarray(FAUVE), (len(x), 1))
    t[(ang > 2.22) & (z < 0.40)] = CREME                             # le ventre (le poitrail reste fauve)
    t[(ang > 1.88) & (ang <= 2.22) & (z > 0.08) & (z < 0.37)] = NOIRC        # le liseré du flanc
    t[(ang < 0.21) & (z > 0.07) & (z < 0.45)] = NOIRC                # la raie de mulet, du garrot à la queue
    t[(z < 0.062) & (ang > 0.30)] = CREME                            # le miroir, autour de la queue
    corps.teinte = t

    def galbe(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 0] *= 0.90 * (1 + 0.18 * gauss((z - 0.11) / 0.08) - 0.12 * gauss((z - 0.26) / 0.10) + 0.14 * gauss((z - 0.41) / 0.08))
        dessous = v[:, 1] < 0
        s[dessous, 1] *= (1 - 0.26 * gauss((z - 0.23) / 0.10) + 0.24 * gauss((z - 0.41) / 0.08))[dessous]   # le flanc creusé, le poitrail
        s[~dessous, 1] *= (1 + 0.08 * gauss((z - 0.41) / 0.06) + 0.06 * gauss((z - 0.10) / 0.07))[~dessous]  # le garrot, la croupe
        s[:, 1] += 0.032 * np.sin(np.pi * np.clip(z / LONG, 0, 1))                                  # le dos rond
        return s
    a.piece("corps", corps.sculpte(galbe), None, pos=CROUPE, rot=(90 - CABRE, 0, 0))

    # ----- l'encolure : une pièce couchée le long de son arc ; la gorge crème, la raie qui monte jusqu'à la nuque -----
    enc = _ENC
    L = enc.long
    parts, rayons = [0.03, 0.20, 0.45, 0.70, 0.90, 0.985], [0.106, 0.098, 0.084, 0.073, 0.066, 0.060]
    cou = A.tour(A.profil([(0, 0)] + [(r, p * L) for r, p in zip(rayons, parts)] + [(0, 1.01 * L)], 6), 40)
    ang = np.abs(np.arctan2(cou.v[:, 0], cou.v[:, 1]))
    t = np.tile(np.asarray(FAUVE), (len(ang), 1))
    t[(ang > 2.35) & (cou.v[:, 2] > 0.55 * L)] = CREME            # la gorge
    t[(ang < 0.20) & (cou.v[:, 2] < 0.80 * L)] = NOIRC
    cou.teinte = t
    a.piece("cou", cou.etire(0.80, 1.0, 1.0).sculpte(enc.couche), None)

    # ----- la tête : courte, le crâne large où naissent les cornes, le museau fin ; dans son repère, X la gauche,
    #       Y le chanfrein, Z vers le nez. Crème, barrée de deux bandeaux noirs qui passent par les yeux. -----
    T, bout = _T, _BOUT
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.020, 0.125))

    tete = A.tour(A.profil([(0, 0), (0.040, 0.006), (0.058, 0.030), (0.062, 0.066), (0.055, 0.106), (0.044, 0.146),
                            (0.037, 0.176), (0.032, 0.192), (0.020, 0.203), (0, 0.208)], 6), 56)
    x, y, z = tete.v[:, 0], tete.v[:, 1], tete.v[:, 2]
    d, ou = distance_ligne(y, z, [(0.052, 0.026), (0.022, 0.080), (-0.024, 0.170)])
    cote_ = np.abs(x) > 0.42 * np.hypot(x, y)
    t = np.tile(np.asarray(CREME), (len(x), 1))
    t[cote_ & (d < 0.022 - 0.009 * ou)] = NOIRC                      # les bandeaux (larges : le velours les grise sur les bords)
    t[z > 0.200] = NOIRC                                             # la truffe, au bout du nez
    tete.teinte = t

    def crane(v):
        s = v.copy()
        z, haut = v[:, 2], v[:, 1] > 0
        s[:, 0] *= 0.86 + 0.08 * gauss((z - 0.070) / 0.045)
        s[:, 1] *= np.where(haut, 0.94 + 0.06 * gauss((z - 0.050) / 0.040), 1 + 0.26 * gauss((z - 0.070) / 0.050))
        return s
    a.piece("tete", tete.sculpte(crane), None, mat=T)

    # ----- les yeux : petits et vivants, resserrés vers l'avant du masque, sous une paupière qui lui donne l'air vif et sûr de lui -----
    centre = T @ Vector((0, 0, 0.080))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.62, 0.56, 0.26)))
        a.oeil("oeil_" + nom, pos + n * 0.003, n, 0.0140)
        haut_oeil = (T3 @ Vector((0, 1, 0)) - n * n.dot(T3 @ Vector((0, 1, 0)))).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.0140, 0.16), NOIRC, mat=A.cadre(pos + n * 0.003, n, haut_oeil), poil=False)
        # la bouche : un trait fin sous le nez, qui remonte un peu vers la joue
        bouche = [a.trace("tete", T @ Vector((0, -0.006, 0.199 - 0.036 * u)),
                          [T3 @ Vector((c * (0.12 + 0.78 * u), -0.98 + 0.50 * u + 0.30 * u * u, 0.0))])[0] for u in np.linspace(0, 1, 7)]
        a.broderie("bouche_" + nom, A.courbe(bouche, 4), 0.0021, NOIRC)

    # ----- les cornes -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("corne_" + nom, corne(T, c), CORNE, poil=False)

    # ----- les oreilles : longues et pointues, plantées derrière les cornes ; la gauche pointée vers nous, la droite
    #       tournée en arrière : il écoute ce qui vient d'en bas -----
    po = A.profil([(0, 0), (0.020, 0.010), (0.027, 0.034), (0.022, 0.064), (0.010, 0.090), (0, 0.100)], 6)
    for nom, c, regard, dedans in (("G", 1, Vector((0.82, 0.42, -0.10)), Vector((0.10, 0.30, 0.95))),
                                   ("D", -1, Vector((-0.66, 0.40, -0.62)), Vector((-0.70, 0.20, -0.40)))):
        vers = (T3 @ regard).normalized()
        E = A.cadre(T @ Vector((c * 0.040, 0.036, 0.020)) - vers * 0.010, vers, T3 @ dedans)
        a.piece("oreille_" + nom, A.tour(po, 32).etire(1.0, 0.42, 1.0), FAUVE, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 24).etire(0.62, 0.36, 0.80).pose((0, 0.007, 0.012)), CREME, mat=E, poil=False)

    # ----- la queue : un petit toupet noir, levé (il est aux aguets), sur le miroir crème -----
    queue = A.tube(A.courbe([(0, 0.232, 0.470), (0, 0.272, 0.494), (0, 0.300, 0.506), (0, 0.318, 0.505)], 6),
                   lambda t: 0.021 - 0.006 * t, 16)
    a.piece("queue", queue, NOIRC)

    # ----- les pattes : longues et fines, le genou et le boulet marqués ; la chaussette noire depuis le genou
    #       (ou le jarret). L'antérieur gauche est posé sur le rocher : son sabot est plus haut que les autres. -----
    pattes = (("patte_avant_D", AVANT_D, RAYONS_AVANT, 0.50), ("patte_avant_G", AVANT_G, RAYONS_AVANT, 0.50),
              ("patte_arriere_D", ARRIERE_D, RAYONS_ARRIERE, 0.46), ("patte_arriere_G", ARRIERE_G, RAYONS_ARRIERE, 0.46))
    for nom, points, rayons_, chaussette in pattes:
        a.piece(nom, membre(points, rayons_, [(chaussette, FAUVE), (1, NOIRC)]), None)
        a.piece("sabot" + nom[5:], sabot(), CORNE, pos=(points[-1][0], points[-1][1], points[-1][2] - 0.030), poil=False)

    return a


# les points du modèle que le squelette réclame, calculés une fois pour toutes (REPERES, comme chez le cheval)
REPERES = {"nuque": tuple(_BOUT), "tete": tuple(_T @ Vector((0, 0.020, 0.080))),
           "oreille_G": tuple(_T @ Vector((0.040, 0.036, 0.020))), "oreille_D": tuple(_T @ Vector((-0.040, 0.036, 0.020)))}


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py chamois). Les mesures sont celles du modèle (avant a.taille).
# Chaque patte a deux os : le haut (épaule ou hanche) et le bas (genou ou jarret) ; ses pièces passent de l'un à
# l'autre au genou, en fondu, comme celles du cheval. Le modèle est saisi l'antérieur gauche posé sur son rocher.

from poses import Pose, borne, cloche, onde

OS = [("racine", None, (0, 0, 0)),
      ("corps", "racine", (0.0, 0.040, 0.440)),                 # le milieu du dos : il se cabre, pique et se couche autour
      ("cou", "corps", tuple(float(x) for x in BASE)),          # le pied de l'encolure
      ("tete", "cou", REPERES["nuque"]),
      ("oreille_g", "tete", REPERES["oreille_G"]),
      ("oreille_d", "tete", REPERES["oreille_D"]),
      ("queue", "corps", (0.0, 0.236, 0.472))]
for _h, _ph, _b, _pb, _av, _ap in JAMBES.values():
    OS += [(_h, "corps", tuple(float(x) for x in _ph)), (_b, _h, tuple(float(x) for x in _pb))]


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
    """Les onglons : tout sur l'os du bas de leur jambe."""
    return lambda points, cote: {JAMBES[(rang, cote)][2]: np.ones(len(points))}


def _oreille(points, cote):
    return {"oreille_g" if cote == "_G" else "oreille_d": np.ones(len(points))}


PORTEURS = [("corps", "corps"), ("cou", "cou"), ("queue", "queue"),
            ("tete", "tete"), ("oeil", "tete"), ("lourde", "tete"), ("bouche", "tete"), ("corne", "tete"),
            ("oreille", _oreille, "oreille_g"), ("pavillon", _oreille, "oreille_g"),
            ("patte_avant", _jambe("avant"), "av_g"), ("patte_arriere", _jambe("arriere"), "ar_g"),
            ("sabot_avant", _bas("avant"), "av_g2"), ("sabot_arriere", _bas("arriere"), "ar_g2"),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def rocher(p, x):
    """L'antérieur gauche : sur son rocher (x = 1, comme le modèle) ou planté sous l'épaule (x = 0)."""
    p.add("av_g", rot=(ALPHA * (1 - x), 0, 0))
    p.add("av_g2", rot=(-(ALPHA - GAMMA) * (1 - x), 0, 0))


def plie(p, cote, avant, arriere, genou_av=0.0, jarret=0.0):
    """Les deux pattes d'un côté : l'angle du haut (> 0 : le pied part en arrière) et le pli du genou ou du jarret."""
    c = cote.lower()
    p.add("av" + c, rot=(avant, 0, 0))
    p.add("av" + c + "2", rot=(genou_av, 0, 0))
    p.add("ar" + c, rot=(arriere, 0, 0))
    p.add("ar" + c + "2", rot=(jarret, 0, 0))


def repos(t):
    """Perché, aux aguets : il respire, le sabot gauche gratte un instant le rocher, il guette d'un côté puis de
    l'autre, une oreille pivote vers chaque bruit, la queue frémit ; il cligne. Un coup d'œil vers nous à la fin."""
    p = Pose()
    r = onde(t, 2)
    g, d, nous = cloche(t, 0.22, 0.13), cloche(t, 0.55, 0.12), cloche(t, 0.84, 0.10)
    gratte = cloche(t, 0.34, 0.04) + cloche(t, 0.44, 0.04)
    p.add("corps", ech=(1 + 0.010 * r, 1, 1 + 0.016 * r))
    rocher(p, 1.0 - 0.14 * gratte)
    p.add("cou", rot=(2 * r, 0, 10 * g - 12 * d + 4 * nous))
    p.add("tete", rot=(-4 * g, 4 * g - 5 * d, 16 * g - 18 * d + 6 * nous))
    p.add("oreille_g", rot=(0, 0, 28 * cloche(t, 0.40, 0.05) - 16 * g))
    p.add("oreille_d", rot=(0, 0, -30 * cloche(t, 0.12, 0.05) + 14 * d))
    p.add("queue", rot=(-18 * cloche(t, 0.68, 0.04) * (0.5 + 0.5 * onde(t, 12)), 0, 0))
    p.ouvert = 1 - cloche(t, 0.36, 0.02) - cloche(t, 0.78, 0.02)
    return p


def avance(t):
    """Il avance par petits bonds, comme d'un rocher à l'autre : les postérieurs poussent, il s'envole, les antérieurs
    se tendent devant, il se reçoit dessus, ramasse ses pattes sous lui et repart."""
    p = Pose()
    s, c = math.sin(math.tau * t), math.cos(math.tau * t)
    vol = max(0.0, s)                                          # en l'air pendant la première moitié
    rocher(p, 0.0)
    p.add("corps", pos=(0, 0, 0.075 * vol), rot=(-9 * s, 0, 0))
    plie(p, "_G", -34 * vol + 12 * max(0.0, -s), 30 * c, 26 * vol, -18 * vol)
    plie(p, "_D", -30 * vol + 10 * max(0.0, -s), 26 * c, 22 * vol, -16 * vol)
    p.add("cou", rot=(6 * s, 0, 0))
    p.add("tete", rot=(-5 * s, 0, 0))
    p.add("oreille_g", rot=(-12 * vol, 0, 0))
    p.add("oreille_d", rot=(-12 * vol, 0, 0))
    p.add("queue", rot=(-20 * vol, 0, 0))
    return p


def mange(t):
    """Il plonge l'encolure jusqu'à l'herbe, arrache trois bouchées, puis relève vivement la tête en mâchant et jette
    un coup d'œil autour : un chamois ne mange jamais tranquille."""
    p = Pose()
    leve_ = cloche(t, 0.84, 0.14)
    bas = 1 - leve_
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    rocher(p, 0.0)
    p.add("corps", rot=(6 * bas, 0, 0))
    plie(p, "_G", -10 * bas, 0, 0, 0)
    plie(p, "_D", -10 * bas, 0, 0, 0)
    p.add("cou", rot=(62 * bas - 4 * leve_, 0, -6 * bas + 10 * leve_))
    p.add("tete", rot=(18 * bas + 8 * coups + 2 * leve_ * onde(t, 14), 0, 14 * leve_))
    p.add("oreille_g", rot=(0, 0, 24 * leve_))
    p.add("oreille_d", rot=(0, 0, -20 * leve_))
    p.ouvert = 1 - cloche(t, 0.70, 0.02)
    return p


def joie(t):
    """La cabriole : il se ramasse, bondit tout droit en se tordant en l'air, les quatre pattes repliées, la tête qui
    fouette ; il retombe sur ses sabots serrés puis reprend sa pose sur le rocher."""
    p = Pose()
    tasse = cloche(t, 0.10, 0.10, False)
    vol = math.sin(math.pi * borne((t - 0.16) / 0.46))           # en l'air de 0,16 à 0,62
    recoit = cloche(t, 0.68, 0.10, False)
    retour = borne((t - 0.78) / 0.20)                            # le pied gauche remonte sur le rocher
    rocher(p, retour * retour * (3 - 2 * retour))
    p.add("corps", pos=(0, 0, -0.045 * tasse + 0.30 * vol - 0.030 * recoit), rot=(-10 * vol, 14 * vol * onde(t, 1), 26 * vol))
    plie(p, "_G", -26 * vol + 8 * tasse, 34 * vol - 8 * tasse, 60 * vol + 14 * tasse, -50 * vol - 14 * tasse)
    plie(p, "_D", -22 * vol + 8 * tasse, 30 * vol - 8 * tasse, 56 * vol + 14 * tasse, -46 * vol - 14 * tasse)
    p.add("cou", rot=(10 * tasse - 14 * vol, 0, -10 * vol))
    p.add("tete", rot=(-10 * vol, 12 * vol * onde(t, 2), -16 * vol))
    p.add("oreille_g", rot=(-30 * vol, 0, 0))
    p.add("oreille_d", rot=(-30 * vol, 0, 0))
    p.add("queue", rot=(-30 * vol, 0, 0))
    return p


def dort(t):
    """Couché, les antérieurs repliés sous le poitrail, les postérieurs ramenés sous le flanc ; l'encolure tournée,
    le menton posé sur l'épaule gauche ; il respire lentement, une oreille tressaille."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    rocher(p, 0.0)
    p.add("corps", pos=(0, 0, -0.300), rot=(0, 4, 0), ech=(1 + 0.012 * r, 1, 1 + 0.020 * r))
    plie(p, "_G", 74, -46, -150, 118)
    plie(p, "_D", 70, -44, -146, 114)
    p.add("cou", rot=(30, 0, 58))
    p.add("tete", rot=(18, 10, 34))
    p.add("oreille_g", rot=(0, -24, 0))
    p.add("oreille_d", rot=(0, 24, -26 * cloche(t, 0.55, 0.04)))
    p.add("queue", rot=(14, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("chamois", styles.style_de("chamois"), sys.modules[__name__]), "Chamois")
