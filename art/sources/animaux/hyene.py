"""La hyène en peluche de velours ras (4e dessin, d'après le husky gardé par l'auteur : même corps campé, mêmes pattes, même
tête de canidé, mêmes oreilles en feuilles, la gueule ouverte sur un rire) : un gris-brun froid semé de GRANDES taches
sombres irrégulières, le ventre plus clair, l'AVANT plus haut que l'arrière (le dos qui descend), une grosse tête large au
museau sombre, court et large, deux grandes oreilles rondes, une courte crinière hérissée le long de l'échine, une courte
queue pendante. Elle rit, la tête basse, un œil d'ambre sur nous.

Les 5 traits de l'espèce (photos de Commons, 15/10) : 1. le dos qui descend de l'épaule vers la croupe (avant haut,
arrière bas) ; 2. une grosse tête large, le museau sombre court et large, les mâchoires puissantes ; 3. de grandes
oreilles rondes, hautes ; 4. le pelage gris-brun taché de grandes plaques sombres, une crinière courte et hérissée ;
5. une queue courte, pendante, à bout sombre.

    python hyene.py        fabrique la fiche art/apercus/animaux/hyene.png (velours ras)
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

GRIS = M.hexa("#c4b8a4")                      # le manteau : gris-brun froid du registre (le poil le fonce)
ARDOISE = M.hexa("#7a6a58")                   # la selle, la calotte, les lunettes, le dos des oreilles, la queue
BLANC = M.hexa("#e8dccb")                     # le masque, le ventre, les pattes, le bout de la queue
GLACIER = M.hexa("#c8962c")                   # l'accent : les yeux d'ambre
GORGE = M.hexa("#5a2f3a")                     # le fond de la gueule
MUSEAU = M.hexa("#4a4040")                    # le museau et la crinière sombres
TOURNE = 0                                    # -30 pour la fiche, posé de biais (on lit sa longueur) ; 0 pour le jeu
CORPS = Vector((0.0, 0.040, 0.300))
LARGE, LONG, HAUT = 0.100, 0.285, 0.102       # les demi-mesures du corps
TETE = Vector((0.0, -0.320, 0.560))
PORT = A.repere(TETE, (10, 0, 0))             # la tête basse et DROITE : le museau en avant, les deux yeux de face
OEIL = (0.48, -0.76, 0.30)                    # la direction de l'œil gauche, dans le repère de la tête


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


def unite(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def epouse(v):
    """Pour sculpte() : le bas d'une oreille s'incurve pour épouser le crâne."""
    s = v.copy()
    s[:, 2] -= v[:, 0] ** 2 / 0.17 * (1 - K.lisse(v[:, 2] / 0.05))
    return s


def patte(chemin, blanc_depuis):
    """Une patte de coureur : le velours gris en haut, blanche à partir de la fraction « blanc_depuis » du chemin."""
    return K.tube_peint(A.courbe(chemin, 5), lambda t: 0.031 - 0.006 * t, [(blanc_depuis, GRIS), (9, BLANC)], 16)


def construire():
    a = K.Animal("hyene")
    a.taille = 1.05
    a.tete = PORT @ Vector((0.0, -0.110, -0.016))

    # ----- le corps : un coureur de traîneau, le poitrail bombé, la croupe ferme ; selle ardoise, flancs gris, dessous
    #       blanc qui monte sur le poitrail -----
    def coque(v):
        y = v[:, 1]
        rond = np.sqrt(np.maximum(1 - y * y, 1e-9))
        boudin = np.maximum(1 - np.abs(y) ** 2.4, 0.0) ** (1 / 2.4)
        k = boudin / rond
        s = np.stack([v[:, 0] * k, y, v[:, 2] * k], axis=1)
        s = K.bosse(s, (0, -0.70, -0.55), 0.26, 0.22)                 # le poitrail bombé
        s = K.bosse(s, (0, 0.80, 0.35), 0.04, 0.22)                   # la croupe : basse
        s = K.bosse(s, (0, -0.55, 0.78), 0.22, 0.34)                  # le garrot : une bosse d'épaules hautes
        s = K.bosse(K.bosse(s, (0.85, -0.50, -0.10), 0.05, 0.10), (-0.85, -0.50, -0.10), 0.05, 0.10)   # les épaules
        avant = K.lisse((-s[:, 1] - 0.1) / 0.8)
        arriere = K.lisse((s[:, 1] + 0.1) / 0.9)
        s = s * [LARGE, LONG, HAUT]
        s[:, 0] *= 1 + 0.08 * avant - 0.06 * arriere
        s[:, 2] *= np.where(s[:, 2] < 0, 1 + 0.10 * avant - 0.30 * arriere, 1.0)
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    cv = corps.v
    dessous = cv[:, 2] < -0.032 + 0.100 * K.lisse((-cv[:, 1] - 0.12) / 0.13)
    selle = cv[:, 2] > 9.0                                                 # pas de selle : de grandes taches
    corps.teinte = np.where(dessous[:, None], np.asarray(BLANC), np.where(selle[:, None], np.asarray(ARDOISE), np.asarray(GRIS)))
    # de grandes taches sombres irrégulières (un quadrillage 3D de sphères) sur le manteau, pas sous le ventre
    def taches(v, cote, rayon, graine, proba=0.70):
        base = np.floor(v / cote).astype(np.int64)
        dedans = np.zeros(len(v), bool)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    c = base + np.array([dx, dy, dz], dtype=np.int64)
                    h = ((c[:, 0] * 73856093) ^ (c[:, 1] * 19349663) ^ (c[:, 2] * 83492791) ^ (graine * 40503)) & 0x7FFFFFFF
                    al = lambda m, h=h: ((((h * m) + 12345) >> 9) & 0xFFFF) / 65535.0
                    centre = (c + np.stack([al(214013), al(1664525), al(22695477)], axis=1)) * cote
                    r = rayon * (0.65 + 0.70 * al(134775813))
                    dedans |= (al(1103515245) < proba) & (np.linalg.norm(v - centre, axis=1) < r)
        return dedans
    corps.teinte = np.where((taches(cv, 0.058, 0.025, 7, 0.86) & ~dessous)[:, None], np.asarray(ARDOISE), corps.teinte)
    a.piece("corps", corps, None, pos=CORPS, rot=(-26, 0, 0))       # le dos qui descend FRANCHEMENT vers la croupe basse
    # la crinière : une courte brosse hérissée le long de l'échine, de la nuque au milieu du dos
    crin = None
    for yy in np.linspace(-0.24, 0.02, 12):
        zz = 0.300 + 0.094 * math.cos(math.radians(26)) + (0.040 - yy) * math.sin(math.radians(26)) + 0.006
        e = A.boule(1.0, 10, 6).etire(0.020, 0.034, 0.072).pose((0.0, float(yy), float(zz)))
        crin = e if crin is None else crin + e
    a.piece("criniere", crin, MUSEAU, poil=False)

    # ----- le cou : épais comme une collerette, ardoise sur la nuque, blanc devant -----
    fil_cou = K.Fil([(0.0, -0.150, 0.400), (0.003, -0.230, 0.470), (0.008, -0.290, 0.535)], flanc=(1, 0, 0))
    cou = A.tour(A.profil([(0, -0.02), (0.084, 0.0), (0.082, 0.07), (0.072, 0.14), (0.064, 0.19), (0, 0.225)], 5), 32)
    cou.teinte = np.where((cou.v[:, 1] < -0.015)[:, None], np.asarray(BLANC), np.asarray(ARDOISE))
    a.piece("cou", cou.sculpte(fil_cou.couche), None)

    # ----- la tête : un crâne de loup, les joues pleines ; le masque blanc, la calotte ardoise et sa pointe entre les
    #       yeux, les lunettes ardoise autour des yeux, les deux taches blanches au-dessus -----
    def crane(v):
        v = K.bosse(v, (0, -0.50, 0.85), 0.08, 0.25)                 # le front
        v = K.bosse(K.bosse(v, (0.80, -0.40, -0.30), 0.10, 0.22), (-0.80, -0.40, -0.30), 0.10, 0.22)   # les joues
        return v * [0.104, 0.108, 0.096]                              # une grosse tête large
    tete = A.boule(1.0, 56, 28).sculpte(crane)
    u = tete.v / np.array([0.086, 0.090, 0.080])
    u /= np.maximum(np.linalg.norm(u, axis=1, keepdims=True), 1e-9)
    calotte = u[:, 2] > 0.30 - 0.30 * np.maximum(u[:, 1], 0.0)
    pointe = (np.abs(u[:, 0]) < 0.09 + 0.35 * np.maximum(u[:, 2], 0.0)) & (u[:, 1] < 0) & (u[:, 2] > -0.12)
    sombre = (u[:, 1] > 0.10) & False
    for c in (1, -1):
        oeil = unite((OEIL[0] * c, OEIL[1], OEIL[2]))
        tache = unite((0.30 * c, -0.66, 0.68))
    tete.teinte = np.where(sombre[:, None], np.asarray(ARDOISE), np.asarray(BLANC))
    a.piece("tete", tete, None, mat=PORT)

    # ----- le museau : blanc, l'arête ardoise ; la gueule ouverte sur la tirade : la mâchoire tombe, le fond sombre ;
    #       la truffe noire -----
    MU = PORT @ A.repere((0, -0.050, -0.030), (98, 0, 0))     # dans ce repère : X la gauche, Y le haut, Z vers la truffe
    museau = A.tour(A.profil([(0, -0.015), (0.058, 0.0), (0.054, 0.04), (0.044, 0.085), (0.035, 0.115), (0.028, 0.135),
                              (0, 0.148)], 6), 40)
    museau.etire(1.22, 0.92, 0.76)
    angle = np.degrees(np.arctan2(museau.v[:, 1], museau.v[:, 0]))
    arete = (np.abs(angle - 90) < 20) & (museau.v[:, 2] < 0.075)
    palais = (np.abs(angle + 90) < 40) & (museau.v[:, 2] > 0.075)
    museau.teinte = np.where(arete[:, None], np.asarray(MUSEAU), np.where(palais[:, None], np.asarray(GORGE), np.asarray(MUSEAU)))
    a.piece("museau", museau, None, mat=MU)
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.024, 0.017, 0.016), K.NOIR, mat=MU @ A.repere((0, 0.005, 0.108)), poil=False)
    machoire = A.tour(A.profil([(0, -0.012), (0.042, 0.0), (0.040, 0.035), (0.033, 0.075), (0.025, 0.100), (0, 0.112)], 6), 32)
    machoire.etire(1.15, 0.70, 0.78)
    ang = np.degrees(np.arctan2(machoire.v[:, 1], machoire.v[:, 0]))
    machoire.teinte = np.where(((np.abs(ang - 90) < 50) & (machoire.v[:, 2] > 0.050))[:, None], np.asarray(GORGE), np.asarray(MUSEAU))
    a.piece("machoire", machoire, None, mat=MU @ A.repere((0, -0.030, 0.010), (20, 0, 0)))
    a.piece("gorge", A.boule(1.0, 24, 12).etire(0.026, 0.014, 0.036), GORGE, mat=MU @ A.repere((0, -0.034, 0.066)), poil=False)

    # ----- les yeux : un iris de feutrine bleu glacier, la pupille vivante par-dessus -----
    for nom, c in (("G", 1), ("D", -1)):
        d = vers(OEIL[0] * c, OEIL[1], OEIL[2])
        a.rustine("iris_" + nom, "tete", TETE, d, 0.16, GLACIER, 0.0025, 0)
        p, n = a.surface("tete", TETE, d)
        a.oeil("oeil_" + nom, p + n * 0.0035, n, 0.0125)

    # ----- les oreilles : deux triangles épais, dressés haut et serrés, le dos ardoise, le creux blanc -----
    po = A.profil([(0, 0), (0.052, 0.010), (0.064, 0.036), (0.056, 0.066), (0.032, 0.090), (0.010, 0.104), (0, 0.108)], 6)
    for nom, c in (("G", 1), ("D", -1)):
        m = A.tour(po, 32).etire(1.0, 0.40, 1.0)
        creux = (m.v[:, 1] > 0.004) & (np.abs(m.v[:, 0]) < 0.028 - 0.22 * m.v[:, 2]) & (m.v[:, 2] > 0.008)
        m.teinte = np.where(creux[:, None], np.asarray(BLANC), np.asarray(ARDOISE))
        m.sculpte(epouse)
        p, n = a.surface("tete", TETE, vers(0.58 * c, 0.06, 0.78))
        dresse = vers(0.46 * c, -0.04, 0.88).normalized()
        a.piece("oreille_" + nom, m, None, mat=A.cadre(p - dresse * 0.018, dresse, vers(0, -1, 0.12)))

    # ----- les pattes : campé, les pattes avant un peu écartées, la droite avancée ; gris en haut, blanc en bas -----
    a.piece("patte_avant_G", patte([(0.052, -0.150, 0.420), (0.062, -0.165, 0.150), (0.070, -0.172, 0.060), (0.074, -0.176, 0.020)], 0.35), None)
    a.piece("pied_avant_G", A.boule(1.0, 24, 12).etire(0.034, 0.043, 0.017).pose((0.076, -0.190, 0.0168), (0, 0, 10)), BLANC)
    a.piece("patte_avant_D", patte([(-0.052, -0.150, 0.420), (-0.060, -0.180, 0.150), (-0.066, -0.200, 0.060), (-0.068, -0.208, 0.020)], 0.35), None)
    a.piece("pied_avant_D", A.boule(1.0, 24, 12).etire(0.034, 0.043, 0.017).pose((-0.069, -0.222, 0.0168), (0, 0, -10)), BLANC)
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.boule(1.0, 32, 16).etire(0.046, 0.072, 0.076), GRIS, pos=(0.064 * c, 0.200, 0.130), rot=(-22, 0, 0))
        a.piece("patte_arriere_" + nom, patte([(0.060 * c, 0.210, 0.170), (0.070 * c, 0.170, 0.105), (0.072 * c, 0.262, 0.065),
                                               (0.072 * c, 0.248, 0.020)], 0.45), None)
        a.piece("pied_arriere_" + nom, A.boule(1.0, 24, 12).etire(0.033, 0.042, 0.017).pose((0.073 * c, 0.234, 0.0168), (0, 0, 6 * c)), BLANC)

    # ----- la queue : un gros panache qui monte de la croupe, roule par-dessus le dos et vient poser son bout blanc
    #       sur l'échine, du côté qu'il nous tend -----
    queue = K.tube_peint(A.courbe([(0.0, 0.250, 0.320), (0.0, 0.320, 0.300), (0.008, 0.365, 0.235), (0.010, 0.380, 0.150)], 6),
                         lambda t: 0.026 - 0.008 * t, [(0.70, GRIS), (9, ARDOISE)], 16)
    a.piece("queue", queue, None)
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py hyene). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Un grand chien : chaque patte a deux os, et ses pièces passent de l'os du haut à celui du bas au coude (devant) ou au
# genou (derrière). Les pattes avant ne sont pas en miroir (la droite est avancée) : leurs os sont nommés à la main ;
# celles de derrière, oui. Les oreilles non plus (la tête est penchée et tournée). La mâchoire a son os : il parle.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.040, 0.300)),          # le milieu du corps
    ("cou", "corps", (0.0, -0.145, 0.345)),            # le pied de la collerette, dans le poitrail
    ("tete", "cou", (0.007, -0.258, 0.488)),           # la nuque, en haut du cou
    ("machoire", "tete", (0.030, -0.364, 0.505)),      # la charnière de la mâchoire, sous le museau
    ("oreille_g", "tete", (0.042, -0.240, 0.592)),     # l'attache de chaque oreille sur le crâne
    ("oreille_d", "tete", (-0.021, -0.264, 0.606)),
    ("queue", "corps", (0.0, 0.250, 0.340)),           # la naissance du panache, sur la croupe
    ("av_g", "corps", (0.052, -0.150, 0.275)),         # l'épaule gauche, puis le coude (à mi-patte)
    ("av_g2", "av_g", (0.062, -0.165, 0.150)),
    ("av_d", "corps", (-0.052, -0.150, 0.275)),        # l'épaule droite et son coude (la patte est avancée)
    ("av_d2", "av_d", (-0.060, -0.180, 0.150)),
    ("arriere_G", "corps", (0.062, 0.205, 0.285)),     # la hanche, dans la cuisse (la droite est son miroir)
    ("genou_G", "arriere_G", (0.070, 0.170, 0.180)),   # le genou, la pointe avant de la patte arrière
]

# chaque patte : l'os du haut, l'os du bas, l'articulation qui les sépare, et les deux points du chemin de la patte qui
# l'encadrent (dans les mesures du modèle)
_ARTICULE = {
    ("avant", "_G"): ("av_g", "av_g2", (0.062, -0.165, 0.150), (0.052, -0.150, 0.275), (0.070, -0.172, 0.060)),
    ("avant", "_D"): ("av_d", "av_d2", (-0.060, -0.180, 0.150), (-0.052, -0.150, 0.275), (-0.066, -0.200, 0.060)),
    ("arriere", "_G"): ("arriere_G", "genou_G", (0.070, 0.170, 0.180), (0.060, 0.210, 0.300), (0.072, 0.262, 0.090)),
    ("arriere", "_D"): ("arriere_D", "genou_D", (-0.070, 0.170, 0.180), (-0.060, 0.210, 0.300), (-0.072, 0.262, 0.090)),
}


def _jambe(rang):
    """Une pièce de patte : l'os du haut avant l'articulation, celui du bas après, avec un fondu de quelques cm.
    (Les points d'une pièce de droite arrivent en miroir, X retourné : on retourne l'articulation de même.)"""
    def poids(points, cote):
        haut, bas, g, u, v = _ARTICULE[(rang, cote)]
        m = np.array([-1.0, 1.0, 1.0]) if cote == "_D" else np.ones(3)
        g, u, v = np.array(g) * m, np.array(u) * m, np.array(v) * m
        sens = (g - u) / np.linalg.norm(g - u) + (v - g) / np.linalg.norm(v - g)
        w = K.lisse((points - g) @ (sens / np.linalg.norm(sens)) / 0.05 + 0.5)
        return {haut: 1 - w, bas: w}
    return poids


def _bas(rang):
    """Le pied : tout sur l'os du bas de sa patte."""
    return lambda points, cote: {_ARTICULE[(rang, cote)][1]: np.ones(len(points))}


def _oreille_os(points, cote):
    """Une oreille tout entière sur l'os de son côté (nommé à la main, sans miroir)."""
    return {"oreille_g" if cote == "_G" else "oreille_d": np.ones(len(points))}


PORTEURS = [("criniere", "corps"), ("corps", "corps"), ("dos", "corps"), ("echine", "corps"), ("rapiecage", "corps"),
            ("cou", "cou"),
            ("tete", "tete"), ("crane", "tete"), ("museau", "tete"), ("truffe", "tete"), ("iris", "tete"), ("oeil", "tete"),
            ("machoire", "machoire"), ("gorge", "machoire"),
            ("oreille", _oreille_os),
            ("patte_avant", _jambe("avant")), ("pied_avant", _bas("avant")),
            ("cuisse", "arriere", True), ("patte_arriere", _jambe("arriere")), ("pied_arriere", _bas("arriere")),
            ("queue", "queue"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]

FERME = -18.0                                  # de combien la mâchoire, ouverte sur le modèle, remonte pour fermer la gueule
PLONGE = (5.0, 60.0, 32.0)                     # mange : le corps penche, le cou et la tête plongent vers la gamelle
COUCHE = (-0.183, -36.0, 105.0, 62.0, -30.0)   # dort : le corps se pose, les cuisses se replient sous lui (la hanche, le
                                               # genou), le cou plonge et la tête se pose sur les pattes de devant

# chaque patte, posée et dépliée : l'angle sous l'horizontale, vers l'avant, de l'épaule ou de la hanche jusqu'au milieu
# du pied (plus de 90 : le pied est en arrière de la hanche), et cette longueur
_JAMBES = {"av_g": (81.2, 0.2613), "av_d": (74.4, 0.2681), "arriere_G": (96.2, 0.2698), "arriere_D": (96.2, 0.2698)}
_PIEDS = {"av": (0.043, 0.017), "arriere": (0.042, 0.017)}     # les demi-mesures d'un pied : sa longueur, son épaisseur
_PIVOT = {n: t for n, _p, t in OS}


def _hauteur(pivot, tangage, descente):
    """La hauteur d'un pivot porté par le corps quand le corps penche de « tangage » degrés (> 0 : l'avant plonge) et
    descend de « descente »."""
    th = math.radians(tangage)
    c = _PIVOT["corps"]
    return c[2] + descente + (pivot[1] - c[1]) * math.sin(th) + (pivot[2] - c[2]) * math.cos(th)


def _pied(p, os_, degres, tangage=0.0, descente=0.0, libre=False):
    """Une patte (dépliée) tourne de « degrés » par rapport au corps (> 0 : le pied part vers l'arrière) ; elle monte ou
    descend juste ce qu'il faut pour que son pied reste posé dans l'herbe, le corps penché de « tangage » et descendu de
    « descente ». libre : le pied peut quitter le sol, jamais s'y enfoncer."""
    a, long = _JAMBES[os_]
    pivot = _PIVOT[os_.replace("_D", "_G")]
    sol = pivot[2] - long * math.sin(math.radians(a))
    h = sol - _hauteur(pivot, tangage, descente) + long * math.sin(math.radians(a + tangage + degres))
    lg, ep = _PIEDS["av" if os_.startswith("av") else "arriere"]
    b = math.radians(tangage + degres)                                  # le pied penché enfonce son talon ou ses doigts
    h += math.hypot(lg * math.sin(b), ep * math.cos(b)) - ep
    p.add(os_, rot=(degres, 0, 0), pos=(0, 0, max(0.0, h) if libre else h))


def _tendu(os_, tangage=0.0, descente=0.0):
    """De combien tourner une patte pour que, tendue vers l'avant, son pied touche juste l'herbe (sans bouger son pivot)."""
    a, long = _JAMBES[os_]
    pivot = _PIVOT[os_.replace("_D", "_G")]
    x = (_hauteur(pivot, tangage, descente) - pivot[2] + long * math.sin(math.radians(a))) / long
    return math.degrees(math.asin(max(-1.0, min(1.0, x)))) - a - tangage


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _oreilles(p, avant, dehors=0.0):
    """Les deux oreilles ensemble : elles basculent vers l'avant (degrés > 0, vers l'arrière < 0) et s'écartent (dehors)."""
    p.add("oreille_g", rot=(avant, dehors, 0))
    p.add("oreille_d", rot=(avant, -dehors, 0))


def _bla(t, syllabes):
    """La gueule qui parle : de 0 (ouverte comme sur le modèle) à 1 (fermée), « syllabes » fois dans la boucle."""
    return 0.5 - 0.5 * onde(t, syllabes, 0.25)


_PATTES = ("av_g", "av_d", "arriere_G", "arriere_D")


def repos(t):
    """Il rouspète : deux tirades, la gueule qui claque à chaque syllabe et la tête qui ponctue ; entre les deux il
    penche la tête de l'autre côté et tape du pied d'impatience ; la seconde finit en hurlement, le museau au ciel et
    les oreilles rabattues ; il respire, cligne, le panache balance à peine."""
    p = Pose()
    r = onde(t, 2)
    p.add("corps", ech=(1 + 0.010 * r, 1, 1 + 0.014 * r))
    phrase = cloche(t, 0.24, 0.15) + cloche(t, 0.62, 0.12)
    hurle = cloche(t, 0.76, 0.07)
    bla = _bla(t, 22) * phrase
    penche = cloche(t, 0.44, 0.08)
    p.add("machoire", rot=(FERME * bla + 10 * hurle, 0, 0))
    p.add("cou", rot=(-2 * phrase - 6 * hurle, 0, 0))
    p.add("tete", rot=(4 * bla - 16 * hurle, -26 * penche, 6 * onde(t, 3) * phrase))
    p.add("av_g2", rot=(30 * (cloche(t, 0.40, 0.03) + cloche(t, 0.48, 0.03)), 0, 0))
    _oreilles(p, -16 * hurle + 6 * cloche(t, 0.10, 0.04), 4 * penche)
    p.add("queue", rot=(0, 0, 5 * onde(t, 2)))
    p.ouvert = 1 - cloche(t, 0.08, 0.03) - cloche(t, 0.88, 0.03)
    return p


def avance(t):
    """Le trot du chien de traîneau : de grandes foulées, les diagonales ensemble, chaque patte qui revient en l'air se
    plie au coude ou au genou ; le nez en avant, il continue de rouspéter en courant, les oreilles couchées par le vent,
    le panache qui balance."""
    p = Pose()
    for os_, bas, phase in (("av_g", "av_g2", 0.0), ("arriere_D", "genou_D", 0.0), ("av_d", "av_d2", 0.5), ("arriere_G", "genou_G", 0.5)):
        a = math.tau * (t + phase)
        _pied(p, os_, 16 * math.sin(a), libre=True)
        p.add(bas, rot=((44 if bas.startswith("av") else 34) * max(0.0, -math.cos(a)), 0, 0))
    p.add("corps", pos=(0, 0, 0.008 * (0.5 - 0.5 * math.cos(2 * math.tau * t))), rot=(0, 2 * onde(t, 1), 2 * onde(t, 1, 0.25)))
    p.add("cou", rot=(6, 0, -2 * onde(t, 1, 0.25)))
    p.add("tete", rot=(-4 + 3 * onde(t, 2), 0, 0))
    p.add("machoire", rot=(FERME * _bla(t, 4), 0, 0))
    _oreilles(p, -8 + 4 * onde(t, 2), 3)
    p.add("queue", rot=(0, 0, 10 * onde(t, 1)))
    return p


def mange(t):
    """Il penche son grand corps, plonge le museau dans la gamelle et engloutit à coups de mâchoire ; puis il relève
    la tête et râle encore, la bouche pleine."""
    p = Pose()
    bas = _plateau(t, 0.42, 0.26, 0.12)
    croque = 0.5 + 0.5 * onde(t, 10) * _plateau(t, 0.42, 0.20, 0.06)
    tangage, descente = PLONGE[0] * bas, -0.010 * bas
    p.add("corps", pos=(0, 0, descente), rot=(tangage, 0, 0))
    for os_ in _PATTES:
        _pied(p, os_, -tangage, tangage, descente)
    p.add("cou", rot=(PLONGE[1] * bas, 0, 0))
    p.add("tete", rot=(PLONGE[2] * bas + 2 * onde(t, 10) * bas, 0, -10 * bas))
    rale = cloche(t, 0.88, 0.06)
    p.add("machoire", rot=(FERME * (croque * bas + _bla(t, 30) * rale), 0, 0))
    _oreilles(p, 6 * bas, 4 * bas)
    p.add("queue", rot=(0, 0, 8 * onde(t, 4) * bas))
    p.ouvert = 1 - cloche(t, 0.95, 0.03)
    return p


def joie(t):
    """Sa fête : il se tasse, puis se dresse sur ses pattes arrière, les pattes de devant repliées en l'air, et lance un
    grand hurlement de joie, le museau au ciel, la gueule grande ouverte, le panache qui bat ; puis il retombe campé."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85)) if t < 0.85 else 0.0
    tasse = cloche(t, 0.14, 0.12, False)
    cabre = cloche(t, 0.50, 0.30, False)
    tangage = 5 * tasse - 16 * cabre
    hanche = _PIVOT["arriere_G"]
    descente = -0.020 * tasse + (hanche[2] - _hauteur(hanche, -16 * cabre, 0.0))     # dressé, il pivote autour des hanches
    p.add("corps", pos=(0, 0, descente), rot=(tangage, 0, 0))
    for os_ in ("arriere_G", "arriere_D"):
        _pied(p, os_, -tangage, tangage, descente)
    for os_ in ("av_g", "av_d"):
        _pied(p, os_, -tangage - 24 * cabre, tangage, descente, libre=True)
        p.add(os_ + "2", rot=(60 * cabre, 0, 0))
    p.add("cou", rot=(6 * tasse - 12 * cabre, 0, 0))
    p.add("tete", rot=(4 * tasse - 18 * cabre, 0, 0))
    p.add("machoire", rot=(10 * cabre + 5 * onde(t, 6) * cabre, 0, 0))
    _oreilles(p, -16 * cabre, 6 * cabre)
    p.add("queue", rot=(0, 0, 26 * onde(t, 8) * env))
    return p


def dort(t):
    """Couché en sphinx, les pattes de devant tendues, les cuisses repliées sous lui, la tête posée de biais sur les
    pattes et la gueule enfin fermée ; le panache retombé sur le flanc, les yeux fermés ; il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    d = COUCHE[0]
    p.add("corps", pos=(0, 0, d), ech=(1 + 0.012 * r, 1, 1 + 0.020 * r))
    for os_ in ("av_g", "av_d"):
        _pied(p, os_, _tendu(os_, 0.0, d), 0.0, d)
    p.paire("arriere", rot=(COUCHE[1], 0, 0))
    p.paire("genou", rot=(COUCHE[2], 0, 0))
    p.add("cou", rot=(COUCHE[3], 0, 18))
    p.add("tete", rot=(COUCHE[4], 0, 10))
    p.add("machoire", rot=(FERME, 0, 0))
    _oreilles(p, -16, 8)
    p.add("queue", rot=(0, 50, 20))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Hyène")
