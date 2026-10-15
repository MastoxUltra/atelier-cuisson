"""La huppe en peluche : la coquette des prés. Tête, cou et poitrail en velours ambre orangé, le ventre crème ; les ailes
et la queue zébrées de larges bandes noires et blanches ; un long bec fin, courbé comme une aiguille à broder. Et sur
la tête, son trait : un éventail de plumes ambre, chacune à pointe noire liserée de blanc, dressé tout grand, du front
jusqu'à la nuque. Elle fait la roue avec sa tête : le poitrail bombé, le menton haut, la tête penchée et présentée
de profil pour qu'on voie tout l'éventail, l'œil braqué sur nous, à demi fermé sous une paupière langoureuse : elle
sait qu'on la regarde.
Style du palier 3 (velours ras) : pas de couture, pas de rapiéçage, pas de bouton.

    python huppe.py        fabrique la fiche art/apercus/animaux/huppe.png (dans le style de son palier : voir styles.py)
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

AMBRE = M.hexa("#f6b26e")                     # la tête, le cou, le poitrail (le poil le fonce vers l'orangé)
VENTRE = M.hexa("#f7e6cc")                    # le bas du ventre, un crème rosé
NOIR = M.hexa("#232126")                      # les bandes des ailes et de la queue, la pointe des plumes
NEIGE = K.BLANC
BEC = M.hexa("#3b3538")                       # le bec, en feutrine
PATTE = M.hexa("#66606a")                     # les pattes, gris ardoise
TOURNE = 0                                    # -20 la pose de trois quarts sur la fiche ; 0 pour le jeu

CORPS = Vector((0.0, 0.0, 0.128))
DRESSE = A.repere(CORPS, (-14, 0, 0))         # le corps : le poitrail haut, le croupion bas
TETE = Vector((0.0, -0.080, 0.226))
LACET, PIQUE, PENCHE = -34.0, -8.0, 10.0      # la tête : de profil pour nous, l'œil gauche nous fixe, le menton haut, penchée


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def poser(maille, mat):
    """Applique une matrice aux points d'une maille (pour réunir des pièces déjà placées)."""
    m = np.array(mat)
    maille.v = maille.v @ m[:3, :3].T + m[:3, 3]
    return maille


def zebree(maille, depart, paliers):
    """Peint une pièce de bandes franches le long de son axe Z, à partir de « depart » : [(largeur, couleur), ...]."""
    seuils, z = [], depart
    for largeur, couleur in paliers:
        z += largeur
        seuils.append((z, couleur))
    seuils[-1] = (9, seuils[-1][1])
    return K.bandes(maille, seuils)


def construire():
    a = K.Animal("huppe")
    a.taille = 0.55

    # ----- le corps : un œuf au poitrail bombé, le croupion effilé ; l'ambre en haut et devant, le crème dessous -----
    def oeuf(v):
        v = K.bosse(v, (0, -0.9, 0.2), 0.12, 0.35)              # le poitrail
        arriere = K.lisse((v[:, 1] - 0.1) / 0.9)
        s = v * [0.058, 0.126, 0.062]
        s[:, 0] *= 1 - 0.40 * arriere
        s[:, 2] *= 1 - 0.35 * arriere
        return s
    corps = A.boule(1.0, 56, 28)
    ventre = (corps.v[:, 2] < -0.35) & (corps.v[:, 1] > -0.55)
    corps.sculpte(oeuf)
    corps.teinte = np.where(ventre[:, None], np.asarray(VENTRE), np.asarray(AMBRE))
    a.piece("corps", corps, None, mat=DRESSE)

    # ----- la tête et le cou : une boule ambre sur un cou court et fort -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.repere(TETE) @ A.cadre((0, 0, 0), nez) @ Matrix.Rotation(math.radians(PENCHE), 4, Vector((0, 0, 1)))
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, -0.004, 0.050))
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(lambda v: K.bosse(v, (0, 0.3, 1), 0.10, 0.4)).etire(0.037, 0.040, 0.047), AMBRE, mat=T)
    a.piece("cou", A.tube([tuple(DRESSE @ Vector((0, -0.050, 0.040))), tuple(T @ Vector((0, -0.014, -0.018)))], 0.030, 24), AMBRE)

    # ----- le bec : une aiguille longue et fine, courbée vers le bas -----
    bec = A.courbe([T @ Vector(q) for q in ((0, -0.004, 0.028), (0, -0.008, 0.078), (0, -0.022, 0.124), (0, -0.044, 0.160))], 6)
    a.piece("bec", A.tube(bec, lambda t: 0.0095 * (1 - 0.75 * t), 16), BEC, poil=False)

    # ----- les yeux : petits, sur le côté ; une paupière ambre langoureuse les coiffe à demi -----
    centre = T @ Vector((0, 0, 0))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.80, 0.20, 0.56)))
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0080)
        monte = T3 @ Vector((0, 1, 0))
        monte = (monte - n * monte.dot(n)).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.0100, 0.16), AMBRE, mat=A.cadre(pos + n * 0.002, n, monte), poil=False)

    # ----- la huppe : neuf plumes en éventail, dressées du front à la nuque ; chacune ambre, liserée de blanc, la pointe
    #       noire. Réunies en une seule pièce de feutrine -----
    pivot = T @ Vector((0, 0.024, -0.004))
    huppe = None
    for k in range(9):
        u = k / 8
        angle = math.radians(68 - 172 * u)                   # de l'avant (au-dessus du bec) jusqu'à l'arrière (sur la nuque)
        long = 0.058 + 0.040 * math.sin(math.pi * (0.15 + 0.75 * u))
        d = T3 @ Vector((0, math.cos(angle), math.sin(angle)))
        plume = A.boule(1.0, 20, 28).sculpte(lambda v: K.bosse(v, (0, 0, 1), 0.25, 0.5)).etire(0.012, 0.0045, long * 0.5)
        plume.pose((0, 0, long * 0.5))
        zebree(plume, 0.0, [(long * 0.68, AMBRE), (long * 0.09, NEIGE), (1.0, NOIR)])
        poser(plume, A.cadre(pivot, d, T3 @ Vector((1, 0, 0))))
        huppe = plume if huppe is None else huppe + plume
    a.piece("huppe", huppe, None, poil=False)

    # ----- les ailes : deux grandes feuilles couchées le long des flancs, zébrées de larges bandes noires et blanches
    #       (l'épaule reste ambre) -----
    def feuille(v):
        s = K.emousse(v, 0.85)
        s[:, 1] *= 1 - 0.35 * K.lisse((v[:, 2] - 0.2) / 0.8)    # elle s'affine vers la pointe
        return s
    aile = A.boule(1.0, 40, 32).sculpte(feuille).etire(0.014, 0.050, 0.104)
    zebree(aile, -0.104, [(0.036, AMBRE), (0.026, NOIR), (0.022, NEIGE), (0.026, NOIR), (0.022, NEIGE), (0.026, NOIR), (0.022, NEIGE), (1.0, NOIR)])
    a.piece("aile", aile, None, mat=A.cadre(DRESSE @ Vector((0.054, 0.034, 0.020)), (0.10, 1.0, -0.16), (0.40, 0, 1)), paire=True)

    # ----- la queue : une palette noire barrée d'une large bande blanche, qui tombe en arrière -----
    queue = A.boule(1.0, 32, 16).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.034, 0.008, 0.084)
    queue.sculpte(lambda v: v * np.stack([1 + 0.30 * K.lisse((v[:, 2] + 0.084) / 0.168), np.ones(len(v)), np.ones(len(v))], axis=1))
    zebree(queue, -0.084, [(0.074, NOIR), (0.034, NEIGE), (1.0, NOIR)])
    a.piece("queue", queue, None, mat=A.cadre(DRESSE @ Vector((0, 0.170, 0.012)), DRESSE.to_3x3() @ Vector((0, 1.0, -0.12)), (0, 0, 1)))

    # ----- les pattes : courtes et grises, trois doigts devant et un derrière -----
    def doigt(degres, long=0.020):
        t = math.radians(degres)
        return A.boule(1.0, 16, 8).etire(0.0055, long, 0.0050).pose((long * 0.8 * math.sin(t), -long * 0.8 * math.cos(t), 0), (0, 0, degres))
    patte = doigt(-30) + doigt(0) + doigt(30) + doigt(180, 0.014) + A.tube([(0, 0.004, 0.090), (0, 0.0, 0.004)], 0.0060, 12)
    a.piece("patte", patte, PATTE, pos=(0.026, 0.004, 0.005), poil=False, paire=True)
    a.couleur_paupiere = AMBRE
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py huppe). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Les pattes pendent à la racine (comme le canard) : une patte posée ne bouge pas quand le corps se dandine au-dessus.
# L'éventail est une seule pièce de neuf plumes : quatre os se le partagent, plume par plume (deux plumes par os devant,
# trois sur la nuque), tous au pied de l'éventail. Dans le modèle il est grand ouvert ; replié, toutes les plumes se
# couchent en arrière le long de la nuque, comme chez la vraie huppe.

from poses import Pose, borne, cloche, onde

PIED_HUPPE = (0.001, -0.072, 0.249)           # le pied de l'éventail (T @ (0, 0.024, -0.004) dans construire)
REPERE_TETE = np.array([[0.830, -0.067, -0.554],   # les axes de la tête en colonnes : sa gauche, son dessus, vers le bec
                        [-0.531, 0.211, -0.821],
                        [0.172, 0.975, 0.139]])
TRAVERS = tuple(REPERE_TETE[:, 0])            # les plumes tournent autour de l'axe « gauche » de la tête pour se coucher
REPLI = (-157.0, -114.0, -71.0, -18.0)        # de combien chaque os couche ses plumes pour replier l'éventail (vers -100°)
ECART = (8.0, 4.0, -3.0, -8.0)                # et de combien il les écarte encore quand elle fait la roue
GROUPES = (0, 0, 1, 1, 2, 2, 3, 3, 3)         # plume 0 (au-dessus du bec) ... plume 8 (sur la nuque) -> huppe_1 ... huppe_4
COU_BAS, COU_HAUT = (0.0, -0.039, 0.179), (0.011, -0.068, 0.210)

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.010, 0.120)),            # au-dessus des pattes : elle se penche, se gonfle autour
    ("cou", "corps", COU_BAS),                           # le pied du cou, dans le poitrail
    ("tete", "cou", COU_HAUT),                           # la nuque
    ("huppe_1", "tete", PIED_HUPPE),                     # les deux plumes de devant
    ("huppe_2", "tete", PIED_HUPPE),
    ("huppe_3", "tete", PIED_HUPPE),
    ("huppe_4", "tete", PIED_HUPPE),                     # les trois de la nuque
    ("aile_G", "corps", (0.046, -0.045, 0.158)),         # l'épaule
    ("queue", "corps", (0.0, 0.095, 0.126)),             # le croupion
    ("patte_G", "racine", (0.026, 0.008, 0.095)),        # la hanche, cachée dans le ventre
]


def _doux(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def plumes(points, cote):
    """L'éventail : chaque plume sur l'os de son groupe. Les neuf plumes ont été réunies dans l'ordre, chacune avec le même
    nombre de points : la place d'un point dans la liste dit sa plume. (Sinon : l'angle du point autour du pied.)"""
    n = len(points)
    if n % 9 == 0:
        k = np.arange(n) * 9 // n
    else:
        d = (np.asarray(points, float) - PIED_HUPPE) @ REPERE_TETE
        angle = np.degrees(np.arctan2(d[:, 2], d[:, 1]))
        k = np.clip(np.round((68.0 - angle) / 21.5), 0, 8).astype(int)
    g = np.asarray(GROUPES)[k]
    return {"huppe_%d" % (i + 1): (g == i).astype(float) for i in range(4)}


def cou_souple(points, cote):
    """Le cou suit le corps en bas et la tête en haut, et se plie entre les deux."""
    b, h = np.asarray(COU_BAS), np.asarray(COU_HAUT)
    u = (np.asarray(points, float) - b) @ (h - b) / float((h - b) @ (h - b))
    w = _doux((u - 0.15) / 0.75)
    return {"cou": 1 - w, "tete": w}


PORTEURS = [("corps", "corps"), ("cou", cou_souple, "cou"), ("tete", "tete"), ("bec", "tete"), ("oeil", "tete"),
            ("lourde", "tete"), ("huppe", plumes, "huppe_2"), ("aile", "aile", True), ("queue", "queue"),
            ("patte", "patte", True),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 (l'œil gauche) et paupiere_1
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


# --- un peu de géométrie (les angles d'une Pose : X, puis Y, puis Z, autour des axes du monde)

def _tourne(axe, degres):
    k = np.asarray(axe, float) / np.linalg.norm(axe)
    c = np.array([[0.0, -k[2], k[1]], [k[2], 0.0, -k[0]], [-k[1], k[0], 0.0]])
    a = math.radians(degres)
    return np.eye(3) + math.sin(a) * c + (1 - math.cos(a)) * (c @ c)


def _angles(R):
    """Les angles d'une Pose pour une rotation quelconque."""
    return (math.degrees(math.atan2(R[2, 1], R[2, 2])), math.degrees(math.asin(-max(-1.0, min(1.0, R[2, 0])))),
            math.degrees(math.atan2(R[1, 0], R[0, 0])))


def eventail(p, ferme, roue=0.0):
    """L'éventail : ferme = 0, grand ouvert comme sur le modèle ; 1, replié à plat sur la nuque. roue > 0 l'écarte
    encore un peu plus (sa fête)."""
    for i in range(4):
        p.add("huppe_%d" % (i + 1), rot=_angles(_tourne(TRAVERS, REPLI[i] * ferme + ECART[i] * roue)))


def ailes(p, leve, ecarte=0.0):
    """Les deux ailes : leve > 0, le bout monte ; ecarte > 0, elles s'ouvrent sur les côtés (on voit les zébrures)."""
    p.paire("aile", rot=(0.4 * leve, -0.3 * leve, -ecarte))


# --- les cinq animations

def repos(t):
    """Elle respire, l'éventail à demi couché ; puis elle se met en valeur : elle dresse l'éventail et l'ouvre tout
    grand, penche la tête pour qu'on le voie bien, nous coule un regard, et le replie lentement. La queue pompe deux
    fois, elle cligne."""
    p = Pose()
    r = onde(t, 2)
    roue = float(_doux((t - 0.22) / 0.10) * (1 - _doux((t - 0.62) / 0.22)))
    p.add("corps", ech=(1 + 0.014 * r, 1 + 0.006 * r, 1 + 0.018 * r))
    p.add("cou", rot=(-4 * roue + 1.5 * r, 0, 0))
    p.add("tete", rot=(-6 * roue, 10 * roue, 8 * roue - 6 * cloche(t, 0.82, 0.07)))
    eventail(p, 0.6 * (1 - roue), 0.4 * roue * cloche(t, 0.42, 0.10))
    p.add("queue", rot=(-10 * (cloche(t, 0.08, 0.04) + cloche(t, 0.16, 0.04)), 0, 0))
    ailes(p, 3 * cloche(t, 0.34, 0.06))
    p.ouvert = borne(1 - cloche(t, 0.50, 0.02) - cloche(t, 0.88, 0.02))
    return p


def avance(t):
    """Elle marche à petits pas, l'éventail couché ; à chaque pas la tête pique en avant puis rattrape le corps (comme
    un pigeon), le corps roule doucement sur la patte d'appui, la queue suit."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    p.add("patte_G", rot=(14 * c, 0, 0), pos=(0, 0, 0.016 * max(0.0, s) + 0.005 * abs(c)))
    p.add("patte_D", rot=(-14 * c, 0, 0), pos=(0, 0, 0.016 * max(0.0, -s) + 0.005 * abs(c)))
    p.add("corps", pos=(0, 0, 0.004 * abs(s)), rot=(2, -3 * s, 0))
    p.add("cou", rot=(10 * onde(t, 2, 0.15), 0, 0))
    p.add("tete", rot=(-8 * onde(t, 2, 0.15), 0, 0))
    eventail(p, 0.85 + 0.05 * onde(t, 2))
    p.add("queue", rot=(4 * onde(t, 2, -0.1), 0, 3 * s))
    return p


def mange(t):
    """Elle plonge son long bec dans l'herbe : le corps penché, trois coups de sonde, puis elle relève la tête avec sa
    trouvaille, et l'éventail se dresse d'un coup de contentement avant de se recoucher."""
    p = Pose()
    bas = float(_doux(t / 0.16) * (1 - _doux((t - 0.70) / 0.16)))
    sonde = max(0.0, onde(t, 3, -0.08)) * bas
    fier = cloche(t, 0.86, 0.09)
    p.add("corps", rot=(22 * bas, 0, 0))
    p.add("cou", rot=(30 * bas + 6 * sonde - 6 * fier, 0, 0))
    p.add("tete", rot=(18 * bas + 10 * sonde - 6 * fier, 0, -4 * bas))
    eventail(p, 0.8 - 0.7 * fier)
    p.add("queue", rot=(-14 * bas, 0, 0))
    ailes(p, 2 * bas)
    p.ouvert = borne(1 - cloche(t, 0.93, 0.03))
    return p


def joie(t):
    """Sa fête : elle se gonfle, fait la roue avec sa tête (l'éventail grand ouvert, et plus encore), sautille deux fois
    en battant des ailes ouvertes (les zébrures !), la queue levée ; puis elle retombe et replie à demi l'éventail,
    comme au début de son repos."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.86)) if t < 0.86 else 0.0
    dresse = float(_doux(t / 0.18) * (1 - _doux((t - 0.70) / 0.26)))
    hop = abs(math.sin(math.tau * borne((t - 0.22) / 0.40))) * env
    bat = onde(t, 6) * env
    for nom in ("corps", "patte_G", "patte_D"):
        p.add(nom, pos=(0, 0, 0.030 * hop))
    p.add("corps", rot=(-8 * env, 0, 0), ech=(1 + 0.04 * env, 1, 1 + 0.03 * env))
    p.paire("patte", rot=(-10 * hop, 0, 0))
    p.add("cou", rot=(-10 * env, 0, 0))
    p.add("tete", rot=(-10 * env, 12 * env * math.sin(math.pi * borne((t - 0.10) / 0.70)), 0))
    eventail(p, 0.6 * (1 - dresse), dresse)
    ailes(p, 30 * env + 14 * bat, 20 * env + 10 * bat)
    p.add("queue", rot=(20 * env, 0, 6 * bat))
    return p


def dort(t):
    """Accroupie dans l'herbe, la tête rentrée dans les épaules et le bec couché sur le poitrail, l'éventail replié à
    plat sur la nuque, les yeux fermés ; elle respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.034), rot=(-4, 0, 0), ech=(1.04 + 0.014 * r, 1.0, 0.96 + 0.020 * r))
    p.add("cou", rot=(-28, 0, 0), pos=(0, 0.010, -0.020))
    p.add("tete", rot=(30 + 1.5 * r, 0, 10))
    eventail(p, 1.0)
    p.add("queue", rot=(6, 0, 0))
    ailes(p, 1 * r)
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("huppe", styles.style_de("huppe"), sys.modules[__name__]), "Huppe")
