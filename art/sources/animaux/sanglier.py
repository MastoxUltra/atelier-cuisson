"""Le sanglier en peluche : un vieux solitaire bourru et têtu, qui ne reculera pas. Tout est devant : un avant-train
énorme, le garrot en bosse, des épaules de lutteur, et derrière, presque rien, une petite croupe sur de petites pattes.
Il a planté les antérieurs écartés, les postérieurs en arrière qui poussent déjà : la tête basse, le groin en avant,
il va foncer. Velours ardoise bleutée ; le long de l'échine, du front jusqu'aux reins, une crête de soies charbon
hérissées, plus hautes sur la bosse ; des favoris gris clair sur les joues. Une grosse tête en coin qui finit en groin
rose-gris, deux défenses ivoire recourbées qui sortent des babines (l'accent), deux petits yeux enfoncés sous des
paupières lourdes et froncées, deux oreilles pointues dressées. La queue raide, levée, finie d'un pinceau : il est
fâché.

    python sanglier.py        fabrique la fiche art/apercus/animaux/sanglier.png (style C, velours ras : palier 3)
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

ARDOISE = M.hexa("#4f5868")                   # la robe
CHARBON = M.hexa("#2a2c33")                   # les soies, les oreilles, le bas des pattes, le pinceau de la queue
FAVORIS = M.hexa("#8e98a8")                   # les joues
GROIN = M.hexa("#b9a3a3")                     # le groin, rose-gris
NARINE = M.hexa("#4a3a3c")
IVOIRE = M.hexa("#f2ead8")                    # l'accent : les défenses
CORNE = M.hexa("#24252b")                     # les sabots
TOURNE = 0                                    # -24 pour la fiche (il pose de trois quarts) ; 0 pour le jeu
CROUPE = Vector((0.0, 0.300, 0.255))          # le bout arrière du corps (une pièce tournée, couchée vers l'avant)
CABRE = 12.0                                  # l'avant plus haut que l'arrière : la bosse du garrot
LONG = 0.640                                  # la longueur du corps
ATTACHE = Vector((0.020, -0.270, 0.360))      # là où la tête entre dans le poitrail
LACET, PIQUE, PENCHE = 16.0, 30.0, 0.0        # la tête : un peu tournée vers nous, basse, le groin en avant


def gauss(x):
    return np.exp(-x * x)


def meche(chemin, large, face, plat=0.45, cotes=12):
    """Une mèche plate : un fuseau tourné, aplati, couché le long d'un chemin (une soie, un pinceau).
    « face » : la direction de son épaisseur ; sa largeur se met d'équerre avec le chemin, en chaque point."""
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
                     (0.30 * large, 0.92 * L), (0.06 * large, 0.985 * L), (0, L)], 5)
    return A.tour(prof, cotes).etire(1.0, plat, 1.0).sculpte(couche)


def jambe(points, rayons, genou=0.55):
    """Une patte : un boudin qui passe par ses articulations, ardoise en haut, charbon sous le genou."""
    rayon = lambda t: float(np.interp(t, np.linspace(0, 1, len(rayons)), rayons))
    return K.tube_peint(A.courbe(points, 6), rayon, [(genou, ARDOISE), (1, CHARBON)], 18)


def sabot():
    """Un petit sabot fendu : la pince avance, une rainure sépare les deux onglons devant."""
    def fendu(v):
        s = v.copy()
        s[:, 1] -= 0.010 * K.lisse((0.030 - v[:, 2]) / 0.030)
        devant = K.lisse(-v[:, 1] / 0.016)
        s[:, 1] += 0.006 * devant * gauss(v[:, 0] / 0.004) * K.lisse((0.032 - v[:, 2]) / 0.016)
        return s
    return A.tour(A.profil([(0, 0), (0.030, 0.003), (0.032, 0.014), (0.026, 0.034), (0.022, 0.044), (0, 0.048)], 5), 28).sculpte(fendu)


def axe(zl):
    """Le point de l'axe du corps à zl mètres de la croupe (le corps est une pièce tournée, couchée vers l'avant)."""
    c = math.radians(CABRE)
    return CROUPE + Vector((0.0, -math.cos(c) * zl, math.sin(c) * zl))


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def construire():
    a = K.Animal("sanglier")
    a.taille = 1.20

    # ----- le corps : un coin, tourné de la croupe au poitrail puis couché ; dans la pièce, X la gauche, Y le dos,
    #       Z l'avant. Une petite croupe, puis tout gonfle jusqu'aux épaules ; la bosse du garrot sur le dessus. -----
    corps = A.tour(A.profil([(0, 0), (0.064, 0.010), (0.090, 0.060), (0.102, 0.150), (0.130, 0.270), (0.166, 0.400),
                             (0.182, 0.500), (0.174, 0.570), (0.122, 0.625), (0, LONG)], 6), 48)

    def coin(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 0] *= 0.80 + 0.10 * gauss((z - 0.48) / 0.10)                       # des épaules larges
        dessus = v[:, 1] > 0
        s[dessus, 1] *= (1 + 0.22 * gauss((z - 0.47) / 0.11))[dessus]          # la bosse du garrot
        s[~dessus, 1] *= (0.90 + 0.06 * gauss((z - 0.47) / 0.10))[~dessus]
        return s
    a.piece("corps", corps.sculpte(coin), ARDOISE, pos=CROUPE, rot=(90 - CABRE, 0, 0))

    # ----- la tête : un gros coin qui file en pointe jusqu'au groin ; dans son repère X la gauche, Y le front,
    #       Z vers le groin. Les favoris gris clair sur les joues. -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0, 0, 0), nez) @ Matrix.Rotation(math.radians(PENCHE), 4, Vector((0, 0, 1)))
    T = A.repere(ATTACHE - T.to_3x3() @ Vector((0, 0, 0.060))) @ T
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.030, 0.230))

    tete = A.tour(A.profil([(0, 0), (0.088, 0.010), (0.124, 0.050), (0.130, 0.100), (0.112, 0.170), (0.088, 0.240),
                            (0.070, 0.300), (0.063, 0.336), (0.061, 0.350), (0, 0.354)], 6), 56)
    z, x, y = tete.v[:, 2], tete.v[:, 0], tete.v[:, 1]
    joue = (np.abs(x) > 0.55 * np.hypot(x, y)) & (y < 0.25 * np.hypot(x, y) + 0.005) & (z > 0.050) & (z < 0.190)
    tete.teinte = np.where(joue[:, None], np.asarray(FAVORIS), np.asarray(ARDOISE))

    def hure(v):
        s = v.copy()
        z, dessus = v[:, 2], v[:, 1] > 0
        s[:, 0] *= 0.86 + 0.12 * gauss((z - 0.110) / 0.060)                     # les bajoues
        s[:, 1] *= np.where(dessus, 0.92 + 0.10 * gauss((z - 0.090) / 0.050), 0.95)
        return s
    a.piece("tete", tete.sculpte(hure), None, mat=T)

    # ----- le groin : un disque rose-gris au bout du nez, ses deux narines -----
    disque = A.tour(A.profil([(0, 0), (0.066, 0.000), (0.069, 0.012), (0.063, 0.026), (0, 0.030)], 4), 40).etire(1.0, 0.82, 1.0)
    G0 = T @ A.repere((0, -0.004, 0.338))
    a.piece("groin", disque, GROIN, mat=G0, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        a.rustine("narine_" + nom, "groin", G0 @ Vector((0, 0, 0.012)), G0.to_3x3() @ Vector((c * 0.42, 0.0, 1.0)), 0.22, NARINE, 0.0015, 0)

    # ----- les yeux : petits, enfoncés, sous des paupières lourdes et froncées (le bord descend vers le groin) -----
    centre = T @ Vector((0, 0, 0.130))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.70, 0.58, 0.40)))
        a.oeil("oeil_" + nom, pos + n * 0.001, n, 0.0120)
        a.piece("lourde_" + nom, K.paupiere(0.0120, 0.18), CHARBON, mat=A.cadre(pos + n * 0.002, n, T3 @ Vector((-c * 0.40, 1.0, 0.45))), poil=False)

    # ----- les oreilles : pointues, dressées, un peu en avant -----
    po = A.profil([(0, 0), (0.022, 0.010), (0.029, 0.036), (0.024, 0.074), (0.010, 0.110), (0, 0.122)], 6)
    for nom, c in (("G", 1), ("D", -1)):
        vers = (T3 @ Vector((c * 0.36, 0.90, 0.05)) + Vector((0, 0, 0.7))).normalized()
        racine = T @ Vector((c * 0.066, 0.092, 0.050))
        E = A.cadre(racine - vers * 0.014, vers, T3 @ Vector((0, 0.2, 1)))
        a.piece("oreille_" + nom, A.tour(po, 32).etire(1.0, 0.40, 1.0), CHARBON, mat=E)

    # ----- les défenses : elles sortent des babines, de chaque côté du groin, et se recourbent vers le haut et l'arrière -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [T @ Vector(q) for q in ((c * 0.040, -0.034, 0.290), (c * 0.070, -0.026, 0.300), (c * 0.094, 0.000, 0.296),
                                          (c * 0.112, 0.030, 0.278), (c * 0.116, 0.056, 0.250), (c * 0.108, 0.070, 0.226))]
        a.piece("defense_" + nom, A.tube(A.courbe(chemin, 8), lambda t: 0.017 * (1 - 0.78 * t ** 1.3), 14), IVOIRE, poil=False)

    # ----- la crête de soies : du front jusqu'aux reins, hérissées, plus hautes sur la bosse, couchées vers l'arrière -----
    arriere = Vector((0.0, 1.0, 0.25)).normalized()
    soies = None
    for zl in np.linspace(0.20, 0.62, 12):
        pos, n = a.surface("corps", axe(zl), (0, 0.12, 1))
        h = 0.040 + 0.085 * float(gauss((zl - 0.47) / 0.12))
        q = Vector(pos)
        m = meche([q - n * 0.012, q + n * h * 0.55 + arriere * h * 0.10, q + n * h + arriere * h * 0.45], 0.026, (1, 0, 0), 0.55)
        soies = m if soies is None else soies + m
    for zt in (0.040, 0.085, 0.130):                     # et le toupet du front, entre les oreilles
        pos, n = a.surface("tete", T @ Vector((0, 0, zt)), T3 @ Vector((0, 1, -0.15)))
        h = 0.055 - 0.10 * (zt - 0.040)
        q = Vector(pos)
        dos = (T3 @ Vector((0, 0.3, -1))).normalized()
        m = meche([q - n * 0.010, q + n * h * 0.55 + dos * h * 0.12, q + n * h + dos * h * 0.45], 0.024, T3 @ Vector((1, 0, 0)), 0.55)
        soies = soies + m
    a.piece("soies", soies, CHARBON)

    # ----- la queue : raide, levée, finie d'un pinceau charbon -----
    tige = A.tube(A.courbe([(0, 0.290, 0.315), (0, 0.330, 0.357), (0, 0.364, 0.383), (0, 0.392, 0.395)], 6), lambda t: 0.013 - 0.004 * t, 12)
    pinceau = meche([(0, 0.386, 0.393), (0, 0.410, 0.401), (0, 0.436, 0.389), (0, 0.452, 0.365)], 0.020, (1, 0, 0), 0.6)
    a.piece("queue", tige.peint(ARDOISE) + pinceau.peint(CHARBON), None)

    # ----- les pattes : courtes ; les antérieurs écartés et plantés en avant, les postérieurs en arrière qui poussent -----
    avant = [0.056, 0.064, 0.044, 0.030, 0.022, 0.024, 0.021]
    arriere_ = [0.046, 0.056, 0.034, 0.024, 0.020, 0.022, 0.020]
    pattes = (("avant_G", [(0.060, -0.200, 0.307), (0.090, -0.220, 0.244), (0.100, -0.250, 0.182), (0.104, -0.272, 0.127),
                           (0.106, -0.290, 0.080), (0.108, -0.302, 0.046), (0.108, -0.306, 0.028)], avant, 0.50),
              ("avant_D", [(-0.060, -0.200, 0.307), (-0.088, -0.214, 0.244), (-0.098, -0.236, 0.182), (-0.102, -0.254, 0.127),
                           (-0.104, -0.268, 0.080), (-0.106, -0.278, 0.046), (-0.106, -0.282, 0.028)], avant, 0.50),
              ("arriere_G", [(0.036, 0.240, 0.242), (0.066, 0.230, 0.198), (0.070, 0.270, 0.142), (0.070, 0.322, 0.099),
                             (0.070, 0.346, 0.068), (0.070, 0.360, 0.044), (0.070, 0.364, 0.028)], arriere_, 0.50),
              ("arriere_D", [(-0.036, 0.240, 0.242), (-0.066, 0.226, 0.198), (-0.070, 0.256, 0.142), (-0.070, 0.300, 0.099),
                             (-0.070, 0.318, 0.068), (-0.070, 0.330, 0.044), (-0.070, 0.334, 0.028)], arriere_, 0.50))
    for nom, points, rayons, genou in pattes:
        a.piece("patte_" + nom, jambe(points, rayons, genou), None)
        a.piece("sabot_" + nom, sabot(), CORNE, pos=(points[-1][0], points[-1][1] - 0.006, 0.0), poil=False)
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py sanglier). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Les quatre pattes ne sont pas symétriques (il est campé, les antérieurs écartés, les postérieurs qui poussent) : chacune
# a son os, nommé à la main (le miroir des « _G » la poserait de travers), au haut de la patte, et son sabot la suit.
# La crête de soies est une seule pièce de quinze mèches : les douze de l'échine suivent le corps, les trois du toupet
# (sur le front) suivent la tête.

from poses import Pose, borne, cloche, onde

CORPS_PIVOT = (0.0, 0.020, 0.330)
JAMBES = {"av_g": ((0.060, -0.200, 0.307), (0.108, -0.306, 0.0)),      # le haut de la patte, et son pied au sol
          "av_d": ((-0.060, -0.200, 0.307), (-0.106, -0.282, 0.0)),
          "ar_g": ((0.036, 0.240, 0.242), (0.070, 0.364, 0.0)),
          "ar_d": ((-0.036, 0.240, 0.242), (-0.070, 0.334, 0.0))}
POINTE, TALON = 0.036, 0.030                  # du milieu du pied à la pince du sabot, et à son talon

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", CORPS_PIVOT),                    # au milieu, au-dessus des pattes : il souffle, roule, se tasse
    ("tete", "corps", (0.017, -0.259, 0.401)),           # la nuque, enfouie dans le poitrail
    ("oreille_g", "tete", (0.093, -0.287, 0.441)),
    ("oreille_d", "tete", (-0.033, -0.323, 0.441)),
    ("queue", "corps", (0.0, 0.290, 0.315)),             # la racine de la queue
] + [(nom, "corps", haut) for nom, (haut, _pied) in JAMBES.items()]


def _cote(g, d):
    """Une pièce posée de chaque côté, sans miroir : la gauche sur l'os g, la droite sur l'os d."""
    return lambda points, cote: {g if cote == "_G" else d: np.ones(len(points))}


def soies(points, cote):
    """La crête : les mèches ont été réunies dans l'ordre, chacune avec le même nombre de points ; les douze premières
    sont sur l'échine, les trois dernières (le toupet) sur la tête."""
    n = len(points)
    tete = (np.arange(n) * 15 // n >= 12).astype(float) if n % 15 == 0 else np.zeros(n)
    return {"corps": 1 - tete, "tete": tete}


PORTEURS = [("corps", "corps"), ("soies", soies, "corps"), ("queue", "queue"),
            ("tete", "tete"), ("groin", "tete"), ("narine", "tete"), ("oeil", "tete"), ("lourde", "tete"), ("defense", "tete"),
            ("oreille", _cote("oreille_g", "oreille_d")),
            ("patte_avant", _cote("av_g", "av_d")), ("sabot_avant", _cote("av_g", "av_d")),
            ("patte_arriere", _cote("ar_g", "ar_d")), ("sabot_arriere", _cote("ar_g", "ar_d")),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 (l'œil gauche) et paupiere_1
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


# --- un peu de géométrie (les angles d'une Pose : X, puis Y, puis Z, autour des axes du monde)

def _tourne(axe, degres):
    k = np.asarray(axe, float) / np.linalg.norm(axe)
    c = np.array([[0.0, -k[2], k[1]], [k[2], 0.0, -k[0]], [-k[1], k[0], 0.0]])
    a = math.radians(degres)
    return np.eye(3) + math.sin(a) * c + (1 - math.cos(a)) * (c @ c)


def _matrice(rot):
    return _tourne((0, 0, 1), rot[2]) @ _tourne((0, 1, 0), rot[1]) @ _tourne((1, 0, 0), rot[0])


def _angles(R):
    """Les angles d'une Pose pour une rotation quelconque."""
    return (math.degrees(math.atan2(R[2, 1], R[2, 2])), math.degrees(math.asin(-max(-1.0, min(1.0, R[2, 0])))),
            math.degrees(math.atan2(R[1, 0], R[0, 0])))


def _doux(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def planter(p, nom, angle=0.0, leve=0.0):
    """Une patte qui reste plantée quoi que fasse le corps : elle reprend son aplomb du modèle (le corps tourné, elle
    tourne à l'inverse), tourne encore de « angle » degrés (> 0 : le pied part en arrière, et la pince descend), lève le
    pied de « leve », et se tasse ou s'allonge juste assez pour que le sabot touche terre. À appeler une fois le corps posé."""
    o = p.os.get("corps", {"rot": (0, 0, 0), "pos": (0, 0, 0), "ech": (1, 1, 1)})
    R, s = _matrice(o["rot"]), np.asarray(o["ech"], float)
    haut, pied = (np.asarray(x, float) for x in JAMBES[nom])
    z = (np.add(CORPS_PIVOT, o["pos"]) + R @ (s * (haut - CORPS_PIVOT)))[2]
    a = math.radians(angle)
    f = pied - haut
    bout = (POINTE if a > 0 else TALON) * abs(math.sin(a))
    e = float(np.clip((leve + bout - z - math.sin(a) * f[1]) / (math.cos(a) * f[2]), 0.5, 1.3))
    p.add(nom, rot=_angles(R.T @ _tourne((1, 0, 0), angle)), ech=(1 / s[0], 1 / s[1], e / s[2]))


def quatre(p, angles=None, leves=None):
    """Les quatre pattes plantées (par défaut comme sur le modèle)."""
    for nom in JAMBES:
        planter(p, nom, (angles or {}).get(nom, 0.0), (leves or {}).get(nom, 0.0))


# --- les cinq animations

def repos(t):
    """Campé, la tête basse, il souffle fort par le groin ; il gratte deux fois la terre du sabot avant gauche comme un
    taureau, s'ébroue (la tête donne un coup vers le haut, les oreilles claquent), fouette de la queue ; il ne lâche pas
    des yeux ce qui est devant lui, et cligne à peine."""
    p = Pose()
    r = onde(t, 2)
    gratte = [cloche(t, 0.24, 0.05), cloche(t, 0.36, 0.05)]
    ebroue = cloche(t, 0.62, 0.05)
    p.add("corps", ech=(1 + 0.018 * r, 1, 1 + 0.012 * r), rot=(1.5 * sum(gratte), 0, 0))
    angle = sum(-22 * math.sin(math.tau * borne((t - c0 + 0.05) / 0.10)) for c0 in (0.24, 0.36))
    quatre(p, angles={"av_g": angle}, leves={"av_g": 0.030 * sum(gratte)})
    p.add("tete", rot=(1.5 * r - 12 * ebroue, 5 * ebroue * onde(t, 8), 3 * sum(gratte)))
    p.add("oreille_g", rot=(0, 20 * ebroue, -10 * cloche(t, 0.84, 0.04)))
    p.add("oreille_d", rot=(0, -20 * ebroue, 0))
    p.add("queue", rot=(0, 0, 18 * cloche(t, 0.78, 0.08) * onde(t, 8)))
    p.ouvert = borne(1 - cloche(t, 0.50, 0.02))
    return p


def avance(t):
    """Son trot têtu, la tête basse comme pour foncer : les diagonales ensemble (avant gauche et arrière droite, puis
    l'autre paire), les épaules qui roulent, la tête qui hoche à chaque pas, la queue raide qui balance."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 15.0
    p.add("corps", pos=(0, 0, 0.008 * abs(s)), rot=(1.5 * onde(t, 2), 3 * s, 2 * c))
    leve = lambda x: 0.035 * max(0.0, x)
    quatre(p, angles={"av_g": -pas * c, "ar_d": -pas * c, "av_d": pas * c, "ar_g": pas * c},
           leves={"av_g": leve(s), "ar_d": leve(s), "av_d": leve(-s), "ar_g": leve(-s)})
    p.add("tete", rot=(4 * onde(t, 2, 0.1), -2 * s, -3 * c))
    p.add("oreille_g", rot=(4 * onde(t, 2, 0.2), 0, 0))
    p.add("oreille_d", rot=(4 * onde(t, 2, 0.2), 0, 0))
    p.add("queue", rot=(0, 0, 12 * c))
    return p


def mange(t):
    """Il fouille du groin : la tête plonge, trois grands coups de boutoir qui labourent la terre vers l'avant, puis il
    relève la hure en mâchant, les oreilles qui battent."""
    p = Pose()
    bas = float(_doux(t / 0.14) * (1 - _doux((t - 0.74) / 0.16)))
    boutoir = max(0.0, onde(t, 3, -0.05)) * bas
    mache = cloche(t, 0.88, 0.09) * abs(onde(t, 8))
    p.add("corps", rot=(5 * bas, 0, 0), pos=(0, -0.010 * boutoir, -0.012 * bas))
    quatre(p)
    p.add("tete", rot=(20 * bas - 8 * boutoir - 4 * mache, 0, -5 * bas), pos=(0, -0.014 * boutoir, 0))
    p.add("oreille_g", rot=(0, 10 * bas + 6 * mache, 0))
    p.add("oreille_d", rot=(0, -10 * bas - 6 * mache, 0))
    p.add("queue", rot=(0, 0, 10 * onde(t, 3)))
    p.ouvert = borne(1 - cloche(t, 0.90, 0.03))
    return p


def joie(t):
    """Sa joie de vieux bourru : une ruade. Il baisse la hure, bondit des quatre pieds en donnant un grand coup de tête
    vers le ciel (les défenses en l'air), retombe et lance les postérieurs en arrière, la queue dressée ; puis il se
    replante, campé comme au début du repos."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.88)) if t < 0.88 else 0.0
    baisse = cloche(t, 0.12, 0.10, False)
    bond = cloche(t, 0.36, 0.14, False)
    rue = cloche(t, 0.64, 0.12, False)
    p.add("corps", pos=(0, 0, -0.020 * baisse + 0.090 * bond + 0.030 * rue), rot=(-10 * bond + 16 * rue, 0, 3 * onde(t, 2) * env))
    for nom in JAMBES:
        devant = nom.startswith("av")
        planter(p, nom, (-14 * bond if devant else 10 * bond) + (0 if devant else 30 * rue), 0.080 * bond + (0.0 if devant else 0.10 * rue))
    p.add("tete", rot=(10 * baisse - 26 * bond + 10 * rue, 0, 8 * onde(t, 3) * env))
    p.add("oreille_g", rot=(0, 18 * env, 0))
    p.add("oreille_d", rot=(0, -18 * env, 0))
    p.add("queue", rot=(30 * env, 0, 14 * onde(t, 5) * env))
    return p


def dort(t):
    """Couché de tout son long sur le ventre, les pattes repliées sous lui, la hure posée par terre, les oreilles
    tombées ; les yeux fermés, il ronfle : un souffle lent et profond qui soulève ses épaules."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.150), rot=(-2, -2, 0), ech=(1.04 + 0.016 * r, 1.0, 0.97 + 0.024 * r))
    p.add("av_g", rot=(88, 0, 6), ech=(1, 1, 0.85))       # les antérieurs repliés en arrière sous le poitrail
    p.add("av_d", rot=(88, 0, -6), ech=(1, 1, 0.85))
    p.add("ar_g", rot=(-104, 0, -6), ech=(1, 1, 0.75))   # les postérieurs ramenés en avant sous le ventre
    p.add("ar_d", rot=(-104, 0, 6), ech=(1, 1, 0.75))
    p.add("tete", rot=(-8 + 1.5 * r, -6, 8))
    p.add("oreille_g", rot=(10, 30, 0))
    p.add("oreille_d", rot=(10, -30, 0))
    p.add("queue", rot=(-20, 0, 25))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("sanglier", styles.style_de("sanglier"), sys.modules[__name__]), "Sanglier")
