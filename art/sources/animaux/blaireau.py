"""Le blaireau en peluche : un vieux grognon de terrier. Un corps en coin, large et bas, le dos gris argent bombé haut
sur les épaules, tout le dessous et les pattes en charbon ; la tête en pointe, blanche, barrée de deux bandes noires
nettes qui partent du nez, passent sur les yeux et finissent sur les oreilles. Trapu, planté sur quatre pattes courtes
et larges, l'antérieure gauche avancée, griffes de terrassier dehors ; le nez au sol, la tête un rien tournée vers
nous, deux petits yeux mi-clos sous une paupière lourde : il est chez lui, et il le sait.
Style du palier 3 (velours ras) : pas de couture, pas de rapiéçage, pas de bouton.

    python blaireau.py        fabrique la fiche art/apercus/animaux/blaireau.png (dans le style de son palier : voir styles.py)
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

ARGENT = M.hexa("#c9c8cc")                    # le dos : un gris argent (le poil le fonce, il faut le prendre clair)
CHARBON = M.hexa("#2e2c31")                   # le dessous, les pattes, les deux bandes du masque
NEIGE = K.BLANC                               # le masque
CORNE = M.hexa("#d8cdb8")                     # les griffes
TOURNE = 0                                    # -28 le pose de trois quarts sur la fiche ; 0 pour le jeu

# L'échine, de la croupe à la nuque : la croupe plus basse, le dos qui monte en bosse sur les épaules, puis la nuque qui
# plonge vers le sol.
ECHINE = [(0.0, 0.285, 0.160), (0.0, 0.160, 0.185), (0.0, 0.020, 0.205), (0.0, -0.105, 0.198), (0.0, -0.215, 0.160)]
GALBE = [(0.0, 0.0), (0.03, 0.085), (0.12, 0.132), (0.30, 0.150), (0.55, 0.158), (0.76, 0.146), (0.90, 0.116), (0.97, 0.088), (1.0, 0.0)]
LACET, PIQUE, PENCHE = 18.0, 30.0, -8.0       # la tête : un peu tournée vers nous, le nez vers le sol, à peine penchée
GROSSE = 1.22                                 # une tête franche : c'est le masque qu'on lit de loin


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def table(points, long=1.0):
    """Une fonction de z qui suit une table [(fraction de la longueur, valeur), ...]."""
    f, val = zip(*points)
    return lambda z: np.interp(z / long, f, val)


def patte(haut, avance=0.026, large=0.050):
    """Une patte courte, large comme un pilier, debout sur son pied dont le bout avance."""
    def pied(v):
        s = v.copy()
        s[:, 1] -= avance * K.lisse((0.050 - v[:, 2]) / 0.050)
        s[:, 0] *= 1.12
        return s
    return A.tour(A.profil([(0, 0), (large * 0.88, 0.006), (large, 0.026), (large * 0.82, 0.060), (large * 0.86, 0.10),
                            (large * 0.96, haut + 0.010), (large * 0.70, haut + 0.045), (0, haut + 0.055)], 6), 32).sculpte(pied)


def griffes(pied, cap):
    """Quatre longues griffes de fouisseur au bout d'une patte avant, couchées vers le sol."""
    tout = None
    for d in (-0.030, -0.010, 0.010, 0.030):
        c = Vector(pied) + A.tourne((0, 0, 1), cap, Vector((d, -0.066, 0.016)))
        bout = c + A.tourne((0, 0, 1), cap, Vector((d * 0.3, -0.030, -0.014)))
        m = A.tube(A.courbe([tuple(c), tuple((c + bout) * 0.5 + Vector((0, 0, 0.003))), tuple(bout)], 4), lambda t: 0.0072 * (1 - 0.7 * t), 12)
        tout = m if tout is None else tout + m
    return tout


def construire():
    a = K.Animal("blaireau")
    a.taille = 0.90

    # ----- le corps : un coin couché le long de l'échine, plus large que haut, la bosse des épaules ; le gris argent
    #       couvre le dos et les flancs, le charbon prend tout le dessous (la limite suit les méridiens : elle reste nette) -----
    fil = K.Fil(ECHINE, flanc=(1, 0, 0), pas=16)
    long = fil.long
    corps = A.tour(A.profil([(r, f * long) for f, r in GALBE], 8), 64)
    tour_ = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))           # 0 sur la ligne du dos, pi sous le ventre
    limite = table([(0.0, 1.55), (0.25, 1.90), (0.60, 1.95), (0.85, 1.70), (1.0, 1.30)], long)(corps.v[:, 2])
    corps.teinte = np.where((tour_ < limite)[:, None], np.asarray(ARGENT), np.asarray(CHARBON))

    def trapu(v):                                         # les hanches et les épaules larges, le ventre plat, la bosse
        s = v.copy()
        f = v[:, 2] / long
        s[:, 0] *= 1.18 + 0.10 * np.exp(-((f - 0.22) / 0.16) ** 2) - 0.24 * K.lisse((f - 0.62) / 0.38)
        s[:, 1] *= np.where(v[:, 1] < 0, 0.70, 0.74 + 0.12 * np.exp(-((f - 0.66) / 0.16) ** 2))
        return s
    a.piece("corps", corps.sculpte(trapu).sculpte(fil.couche), None)

    # ----- la tête : un coin pointu, le crâne plat, les bajoues larges ; dans son repère, X la gauche, Y le dessus, Z vers
    #       la truffe. Le masque : une raie blanche sur le front, deux bandes noires du nez aux oreilles, les joues blanches,
    #       la gorge charbon, la nuque argent -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0, 0, 0), nez) @ Matrix.Rotation(math.radians(PENCHE), 4, Vector((0, 0, 1))) @ A.repere(ech=(GROSSE,) * 3)
    cou = Vector(fil.cadre(long)[0])
    T = A.repere(cou - T.to_3x3() @ Vector((0, 0.010, 0.030))) @ T
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.020, 0.150))

    tete = A.tour(A.profil([(0, 0), (0.060, 0.008), (0.088, 0.034), (0.094, 0.068), (0.086, 0.104), (0.066, 0.140), (0.044, 0.172),
                            (0.030, 0.196), (0.022, 0.212), (0, 0.222)], 6), 64)
    tour_ = np.abs(np.arctan2(tete.v[:, 0], tete.v[:, 1]))
    z = tete.v[:, 2]
    raie = table([(0.0, 0.30), (0.45, 0.30), (0.75, 0.24), (0.88, 0.20), (1.0, 0.20)], 0.222)(z)
    bord = table([(0.0, 1.30), (0.45, 1.30), (0.75, 1.18), (0.88, 1.05), (0.93, 0.0), (1.0, 0.0)], 0.222)(z)
    teinte = np.where(((tour_ > raie) & (tour_ < bord))[:, None], np.asarray(CHARBON), np.asarray(NEIGE))
    teinte[(tour_ > 2.45) & (z < 0.17)] = CHARBON                     # la gorge
    teinte[z < 0.030] = ARGENT                                         # la nuque, qui rentre dans le corps
    tete.teinte = teinte

    def caboche(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 1] *= np.where(v[:, 1] > 0, 0.74, 0.86)                   # le crâne plat
        s[:, 0] *= 1 + 0.16 * np.exp(-((z - 0.075) / 0.040) ** 2) * (v[:, 1] < 0.02)     # les bajoues
        s[:, 1] += 0.010 * np.exp(-((z - 0.110) / 0.025) ** 2) * (v[:, 1] > 0)           # l'arcade, au-dessus des yeux
        return s
    a.piece("tete", tete.sculpte(caboche), None, mat=T)
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.022, 0.015, 0.014), CHARBON, mat=T @ A.repere((0, 0.004, 0.214)), poil=False)

    # ----- les yeux : petits, à cheval sur le bord de la bande noire (le blanc de la joue les détache) ; une paupière
    #       lourde de charbon les coiffe à moitié : il est de mauvais poil -----
    centre = T @ Vector((0, 0, 0.100))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.70, 0.22, 0.66)))
        a.oeil("oeil_" + nom, pos + n * 0.003, n, 0.0145)
        monte = T3 @ Vector((0, 1, 0))
        monte = A.tourne(n, 14 * c, (monte - n * monte.dot(n)).normalized())
        a.piece("lourde_" + nom, K.paupiere(0.0168, 0.58), CHARBON, mat=A.cadre(pos + n * 0.002, n, monte), poil=False)

    # ----- les oreilles : petites, rondes, au bout des bandes noires, bordées de blanc -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", T @ Vector((0, 0, 0.040)), T3 @ Vector((c * 0.74, 0.62, -0.20)))
        E = A.cadre(pos + n * 0.006, T3 @ Vector((c * 0.40, 0.30, 0.86)), n + T3 @ Vector((0, 0.3, -0.5)))
        a.piece("oreille_" + nom, A.boule(1.0, 28, 14).etire(0.026, 0.024, 0.010), NEIGE, mat=E)
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).etire(0.019, 0.017, 0.006), CHARBON, mat=E @ A.repere((0, -0.003, 0.006)), poil=False)

    # ----- les pattes : quatre piliers courts, plantés large ; l'antérieure gauche avancée, griffes dehors -----
    for nom, f, ecart, avance, cap in (("arriere_G", 0.18, 0.112, 0.0, 6), ("arriere_D", 0.18, -0.112, 0.0, -6),
                                       ("avant_G", 0.80, 0.112, 0.050, 14), ("avant_D", 0.80, -0.108, -0.010, -10)):
        centre_, _avant, _nuque = fil.cadre(f * long)
        pied = (centre_[0] + ecart, centre_[1] - avance, 0.0)
        a.piece("patte_" + nom, patte(centre_[2] - 0.030), CHARBON, mat=A.repere(pied, (0, 0, cap)))
        if nom.startswith("avant"):
            a.piece("griffes_" + nom[-1], griffes(pied, cap), CORNE, poil=False)

    # ----- les cuisses : deux gros jambons argent sur les hanches, qui débordent du corps au-dessus des pattes arrière -----
    hanche, sens, nuque = fil.cadre(0.20 * long)
    for nom, c in (("G", 1), ("D", -1)):
        h = Vector(hanche) + Vector((c * 0.128, 0.0, -0.030))
        a.piece("cuisse_" + nom, A.boule(1.0, 32, 16).etire(0.050, 0.092, 0.084), ARGENT, mat=A.repere(h, (-18, 0, -8 * c)))

    # ----- la queue : un court pinceau argent, pointé vers le bas -----
    racine, sens, _n = fil.cadre(0.02 * long)
    queue = A.tour(A.profil([(0, 0), (0.034, 0.010), (0.036, 0.040), (0.022, 0.075), (0, 0.092)], 6), 32)
    a.piece("queue", queue, ARGENT, mat=A.cadre(Vector(racine) + Vector((0, 0.010, 0.020)), Vector((0, 1.0, -0.55)), (0, 0, 1)))
    a.couleur_paupiere = CHARBON                   # les paupières de l'usine : du charbon, comme la bande où sont les yeux
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py blaireau). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Les pattes avant ne sont pas symétriques (la gauche est avancée) : chacune a son os, nommé à la main (le miroir des
# « _G » la poserait de travers). Les pattes arrière, elles, sont en miroir ; chaque cuisse suit sa patte.

from poses import Pose, borne, cloche, onde

CORPS_PIVOT = (0.0, 0.030, 0.150)
JAMBES = {"av_g": (0.112, -0.169, 0.165), "av_d": (-0.108, -0.109, 0.165),     # le haut de chaque pilier, dans le corps
          "ar_G": (0.112, 0.195, 0.150), "ar_D": (-0.112, 0.195, 0.150)}
POINTE = {"av_g": 0.096, "av_d": 0.096, "ar_G": 0.070, "ar_D": 0.070}   # du pilier au bout des griffes (ou des doigts)
TALON = 0.050                                                            # du pilier à l'arrière du pied

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", CORPS_PIVOT),                    # le milieu du dos : il respire, roule, se tasse autour
    ("tete", "corps", (0.0, -0.200, 0.165)),             # la nuque
    ("oreille_g", "tete", (0.075, -0.203, 0.197)),
    ("oreille_d", "tete", (-0.052, -0.254, 0.214)),
    ("queue", "corps", (0.0, 0.285, 0.182)),             # la racine du pinceau
    ("av_g", "corps", JAMBES["av_g"]),                   # l'antérieure gauche, avancée, griffes dehors
    ("av_d", "corps", JAMBES["av_d"]),
    ("ar_G", "corps", JAMBES["ar_G"]),                   # la hanche ; son miroir porte la droite
]


def _cote(g, d):
    """Une pièce posée de chaque côté, sans miroir : la gauche sur l'os g, la droite sur l'os d."""
    return lambda points, cote: {g if cote == "_G" else d: np.ones(len(points))}


PORTEURS = [("corps", "corps"), ("tete", "tete"), ("truffe", "tete"), ("oeil", "tete"), ("lourde", "tete"),
            ("oreille", _cote("oreille_g", "oreille_d")), ("dedans", _cote("oreille_g", "oreille_d")),
            ("patte_avant", _cote("av_g", "av_d")), ("griffes", _cote("av_g", "av_d")),
            ("patte_arriere", "ar", True), ("cuisse", "ar", True), ("queue", "queue"),
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
    """Une patte qui reste plantée quoi que fasse le corps : elle se remet d'aplomb (le corps tourné, elle tourne à
    l'inverse), fait « angle » degrés avec la verticale (> 0 : le pied part en arrière, et sa pointe descend), lève le pied
    de « leve », et se tasse ou s'allonge juste assez pour que le pied touche terre. À appeler une fois le corps posé."""
    o = p.os.get("corps", {"rot": (0, 0, 0), "pos": (0, 0, 0), "ech": (1, 1, 1)})
    R, s = _matrice(o["rot"]), np.asarray(o["ech"], float)
    piv = np.asarray(JAMBES[nom], float)
    haut = (np.add(CORPS_PIVOT, o["pos"]) + R @ (s * (piv - CORPS_PIVOT)))[2]
    a = math.radians(angle)
    bout = (POINTE[nom] if a > 0 else TALON) * abs(math.sin(a))          # ce qui descend sous la semelle en tournant
    e = float(np.clip((haut - leve - bout) / (piv[2] * math.cos(a)), 0.5, 1.3))
    p.add(nom, rot=_angles(R.T @ _tourne((1, 0, 0), angle)), ech=(1 / s[0], 1 / s[1], e / s[2]))


def quatre(p, angles=None, leves=None):
    """Les quatre pattes plantées (par défaut d'aplomb, au sol)."""
    for nom in JAMBES:
        planter(p, nom, (angles or {}).get(nom, 0.0), (leves or {}).get(nom, 0.0))


# --- les cinq animations

def repos(t):
    """Chez lui, de mauvais poil : il respire, renifle deux fois le sol, gratte une fois la terre de sa patte griffue,
    puis relève le nez vers nous en bougonnant (les oreilles se couchent, la tête secoue un « non » bref) et revient à
    son affaire ; il cligne lentement."""
    p = Pose()
    r = onde(t, 2)
    renifle = cloche(t, 0.10, 0.035) + cloche(t, 0.18, 0.035)
    gratte = cloche(t, 0.32, 0.06)
    nous = float(_doux((t - 0.50) / 0.08) * (1 - _doux((t - 0.80) / 0.12)))
    p.add("corps", ech=(1 + 0.014 * r, 1, 1 + 0.010 * r), rot=(0, 0, 0))
    quatre(p, angles={"av_g": -18 * gratte}, leves={"av_g": 0.022 * gratte})
    p.add("tete", rot=(5 * renifle - 14 * nous, 6 * nous * onde(t, 6) * cloche(t, 0.66, 0.06), 12 * nous))
    p.add("oreille_g", rot=(0, -18 * nous, 0))
    p.add("oreille_d", rot=(0, 18 * nous, 0))
    p.add("queue", rot=(0, 0, 8 * cloche(t, 0.40, 0.05) * onde(t, 4)))
    p.ouvert = borne(1 - cloche(t, 0.44, 0.03) - cloche(t, 0.92, 0.03))
    return p


def avance(t):
    """Son trot de terrassier : bas, pressé, en roulant des épaules ; les diagonales vont ensemble (avant gauche et
    arrière droite, puis l'autre paire), le nez au ras du sol qui se balance, le pinceau qui suit."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 16.0
    p.add("corps", pos=(0, 0, 0.004 * abs(s)), rot=(0, 4 * s, 3 * c))
    leve = lambda x: 0.022 * max(0.0, x)
    quatre(p, angles={"av_g": -pas * c, "ar_D": -pas * c, "av_d": pas * c, "ar_G": pas * c},
           leves={"av_g": leve(s), "ar_D": leve(s), "av_d": leve(-s), "ar_G": leve(-s)})
    p.add("tete", rot=(-3 * onde(t, 2), -4 * s, -3 * c))
    p.add("queue", rot=(0, 0, -10 * c))
    return p


def mange(t):
    """Il fouille : deux grands coups de griffes de la patte gauche qui ratissent la terre, le museau plonge dans le
    trou, trois bouchées, puis il relève la tête en mâchant d'un air mécontent."""
    p = Pose()
    bas = float(_doux(t / 0.12) * (1 - _doux((t - 0.78) / 0.16)))
    griffe, leve = 0.0, 0.0
    for centre in (0.18, 0.34):                          # chaque coup : la patte part devant en l'air, retombe, ratisse
        u = borne((t - centre + 0.08) / 0.16)
        griffe += -22 * math.sin(math.tau * u)
        leve += 0.028 * max(0.0, math.sin(math.tau * u))
    fouille = cloche(t, 0.18, 0.08) + cloche(t, 0.34, 0.08)
    trou = float(_doux((t - 0.40) / 0.08) * (1 - _doux((t - 0.74) / 0.08)))
    bouchee = abs(onde(t, 6)) * trou
    p.add("corps", rot=(3 * bas, 0, 0), pos=(0, 0, -0.008 * bas))
    quatre(p, angles={"av_g": griffe}, leves={"av_g": leve})
    mache = cloche(t, 0.88, 0.08) * onde(t, 8)
    p.add("tete", rot=(-6 * fouille + 3 * trou + 2 * bouchee - 4 * cloche(t, 0.88, 0.08), 0, -6 * fouille + 3 * mache))
    p.add("oreille_g", rot=(0, -10 * trou, 0))
    p.add("oreille_d", rot=(0, 10 * trou, 0))
    p.ouvert = borne(1 - cloche(t, 0.92, 0.03))
    return p


def joie(t):
    """La danse de guerre des blaireaux (si, ça existe) : il se ramasse, bondit deux fois sur place en se tordant, le
    dos rond, la tête qui secoue et le pinceau dressé ; puis il se replante, l'air de rien, comme au début du repos."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.86)) if t < 0.86 else 0.0
    tasse = cloche(t, 0.10, 0.08, False)
    hop = abs(math.sin(math.tau * borne((t - 0.16) / 0.60))) * env
    torse = onde(t, 2) * env
    p.add("corps", pos=(0, 0, -0.016 * tasse + 0.060 * hop), rot=(-6 * hop, 6 * torse, 14 * torse),
          ech=(1, 1 - 0.04 * env, 1 + 0.05 * env))
    for nom in JAMBES:                                   # en l'air, les pattes pendent et s'écartent un peu
        planter(p, nom, (-14 if nom.startswith("av") else 14) * hop, 0.055 * hop)
    p.add("tete", rot=(-10 * env, 10 * onde(t, 4) * env, -10 * torse))
    p.add("oreille_g", rot=(0, 14 * env, 0))
    p.add("oreille_d", rot=(0, -14 * env, 0))
    p.add("queue", rot=(40 * env, 0, 12 * onde(t, 4) * env))
    return p


def dort(t):
    """Roulé en boule au fond du terrier : couché sur le ventre, les pattes repliées dessous, le corps courbé en
    croissant et le museau ramené contre sa cuisse ; les yeux fermés, une respiration lente et profonde."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.060), rot=(-3, 4, 14), ech=(1.04 + 0.016 * r, 1.0, 0.96 + 0.024 * r))
    p.add("av_g", rot=(-72, 0, -10))                     # les pattes avant allongées devant, sous le menton
    p.add("av_d", rot=(-72, 0, 10))
    p.paire("ar", rot=(-80, 0, 12))
    p.add("tete", rot=(-34 + 1.5 * r, 10, 50))
    p.add("oreille_g", rot=(0, -12, 0))
    p.add("oreille_d", rot=(0, 12, 0))
    p.add("queue", rot=(10, 0, 30))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("blaireau", styles.style_de("blaireau"), sys.modules[__name__]), "Blaireau")
