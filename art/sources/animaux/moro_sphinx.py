"""Le moro-sphinx en peluche : le papillon-colibri. Un corps trapu et velu, gris-beige dessus, blanc dessous, l'abdomen
fini par un éventail en damier noir et blanc relevé comme une queue d'oiseau ; les ailes avant brun gris barrées de
sépia, les ailes arrière orange vif, et une très longue trompe de feutrine orange qui se déroule vers le bas.
Un gourmand pressé : dressé sur ses pattes fines, le derrière en l'air, les ailes en V (l'une déjà plus haute que
l'autre), deux gros yeux ronds, il pique du nez vers une fleur qu'on ne voit pas.

    python moro_sphinx.py        fabrique la fiche art/apercus/animaux/moro_sphinx.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K

GREIGE = M.hexa("#d8c7ab")                    # le poil du dos : il fonce, et sort gris-beige
BRUN_GRIS = M.hexa("#705c4c")                 # la feutrine des ailes avant (au soleil elle sort plus claire et plus grise)
SEPIA = M.hexa("#3d2f28")                     # les barres des ailes, le liseré des ailes arrière, les antennes, les pattes
ORANGE = M.hexa("#ff6600")                    # l'accent : les ailes arrière et la trompe
CORPS = A.repere((0, -0.015, 0.152), (20, 4, 6))                  # le corps pique du nez, le derrière en l'air
PORT = CORPS @ A.repere((0, -0.086, -0.012), (10, -6, 22))         # la tête : plus basse encore, penchée, tournée vers nous
TETE = PORT @ Vector((0, 0, 0))

# les contours des ailes de gauche, à plat : (vers le dehors, vers l'arrière), depuis l'attache
AVANT = [(0.0, -0.018), (0.066, -0.034), (0.134, -0.038), (0.192, -0.027), (0.208, -0.009), (0.180, 0.018),
         (0.124, 0.042), (0.056, 0.046), (0.0, 0.025)]
BARRES = [[(0.058, -0.027), (0.078, -0.030), (0.096, 0.038), (0.074, 0.040)],
          [(0.132, -0.034), (0.150, -0.032), (0.166, 0.019), (0.146, 0.028)]]
ARRIERE = [(0.0, 0.0), (0.060, -0.014), (0.120, -0.007), (0.144, 0.014), (0.122, 0.050), (0.072, 0.064), (0.018, 0.048)]


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête, rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def robe(m):
    """Peint le corps : le dos gris-beige, tout le dessous blanc (par méridiens : le +Y de la pièce est le dos),
    et au bout de l'abdomen une bague noire puis une bague blanche qui annoncent le damier."""
    tour = np.degrees(np.arctan2(m.v[:, 1], m.v[:, 0]))
    ventre = ((tour < -22) & (tour > -158))[:, None]
    m.teinte = np.where(ventre, K.BLANC, GREIGE)
    m.teinte[m.v[:, 2] < 0.046] = K.BLANC
    m.teinte[m.v[:, 2] < 0.028] = K.NOIR
    return m


def aile_avant():
    """Une aile avant : un long triangle de feutrine brun gris, et deux barres sépia plus épaisses que l'aile, qui la
    traversent : on les voit dessus comme dessous."""
    m = A.decoupe(A.courbe(AVANT, 5, fermee=True), 0.005, 0.002).peint(BRUN_GRIS)
    for barre in BARRES:
        m = m + A.decoupe(np.array(barre), 0.0080, 0.0015).peint(SEPIA)
    return m


def aile_arriere():
    """Une aile arrière : un fond sépia qui fait le liseré, et un panneau orange plus épais, visible des deux côtés."""
    bord = A.courbe(ARRIERE, 5, fermee=True)
    coeur = np.array((0.070, 0.024))
    return A.decoupe(bord, 0.005, 0.002).peint(SEPIA) + A.decoupe(coeur + (bord - coeur) * 0.80, 0.0088, 0.002).peint(ORANGE)


def pose_aile(cote, attache, leve, fleche):
    """Le repère d'une aile : attachée en « attache » (dans le repère du corps, côté gauche), levée de « leve » degrés,
    couchée vers l'arrière de « fleche » degrés. cote : 1 à gauche, -1 à droite."""
    l, f = math.radians(leve), math.radians(fleche)
    dehors = Vector((cote * math.cos(l) * math.cos(f), math.cos(l) * math.sin(f), math.sin(l)))
    return CORPS @ A.cadre((attache[0] * cote, attache[1], attache[2]), dehors.cross(Vector((0, 1, 0))), (0, 1, 0))


def eventail():
    """L'éventail de la queue, à plat (X : en travers, Y : vers l'arrière) : cinq secteurs sur deux rangs, en damier
    noir et blanc ; chaque carreau du bord est arrondi comme une plume."""
    tout = None
    for i in range(5):
        t0, t1 = math.radians(-70 + 28 * i), math.radians(-42 + 28 * i)
        for j, (r0, r1) in enumerate(((0.014, 0.054), (0.054, 0.090))):
            arc = np.linspace(t0, t1, 5)
            dehors = [((r1 + 0.007 * j * math.sin(math.pi * k / 4)) * math.sin(t), (r1 + 0.007 * j * math.sin(math.pi * k / 4)) * math.cos(t))
                      for k, t in enumerate(arc)]
            dedans = [(r0 * math.sin(t), r0 * math.cos(t)) for t in arc[::-1]]
            carreau = A.decoupe(np.array(dehors + dedans), 0.0065, 0.0015).peint(K.NOIR if (i + j) % 2 == 0 else K.BLANC)
            tout = carreau if tout is None else tout + carreau
    return tout


def construire():
    a = K.Animal("moro_sphinx")
    a.taille = 0.34
    a.tete = PORT @ Vector((0, -0.040, 0.0))
    a.poil_long = 0.0042                      # velu : un poil plus long que celui des autres petites bêtes

    # ----- le corps : une grosse goutte de peluche tournée de la queue au cou, le thorax bossu -----
    profil = A.profil([(0, 0), (0.026, 0.004), (0.040, 0.028), (0.050, 0.062), (0.060, 0.096), (0.066, 0.130),
                       (0.060, 0.160), (0.044, 0.182), (0, 0.192)], 6)

    def bossu(v):
        s = v.copy()
        s[:, 1] *= np.where(v[:, 1] > 0, 1.0 + 0.14 * np.exp(-((v[:, 2] - 0.132) / 0.040) ** 2), 0.94)
        return s
    a.piece("corps", robe(A.tour(profil, 56)).sculpte(bossu), None, mat=CORPS @ A.repere((0, 0.128, 0), (90, 0, 0)))

    # ----- l'éventail : la queue en damier, relevée un cran de plus que le corps -----
    a.piece("eventail", eventail(), None, mat=CORPS @ A.cadre((0, 0.116, 0.006), (0, -0.30, 0.95), (0, 0.95, 0.30)), poil=False)

    # ----- la tête : une grosse boule velue, deux gros boutons cerclés de blanc, deux antennes en massue dressées -----
    a.piece("tete", A.boule(1.0, 56, 28).etire(0.054, 0.050, 0.048), GREIGE, mat=PORT)
    for nom, cote in (("G", 1), ("D", -1)):
        regard = vers(0.80 * cote, -0.52, 0.28)
        a.rustine("cerne_" + nom, "tete", TETE, regard, 0.62, K.BLANC, 0.003, 0)
        p, n = a.surface("tete", TETE, regard)
        a.bouton("oeil_" + nom, p + n * 0.003, n, 0.0235)
        pied = PORT @ Vector((0.014 * cote, -0.004, 0.046))
        fil = A.courbe([pied - Vector((0, 0, 0.006))] + [pied + Vector((x * cote, y, z)) for x, y, z in
                                                          ((0.006, -0.012, 0.022), (0.022, -0.030, 0.046), (0.044, -0.044, 0.062))], 6)
        a.piece("antenne_" + nom, A.tube(fil, lambda t: 0.0044 + 0.0032 * float(K.lisse(t / 0.8)) - 0.0044 * float(K.lisse((t - 0.8) / 0.2)), 12),
                SEPIA, poil=False)

    # ----- la trompe : très longue, elle part droit devant, plonge vers la fleur et finit en crosse -----
    p, n = a.surface("tete", TETE, vers(0, -0.80, -0.60))
    fil = A.courbe([p - n * 0.006] + [p + Vector(q) for q in ((0.004, -0.028, 0.006), (0.012, -0.060, 0.002), (0.022, -0.084, -0.018),
                                                               (0.028, -0.090, -0.038), (0.028, -0.080, -0.053), (0.028, -0.064, -0.051),
                                                               (0.028, -0.060, -0.038), (0.028, -0.070, -0.032))], 8)
    a.piece("trompe", A.tube(fil, lambda t: 0.0080 - 0.0026 * t, 12), ORANGE, poil=False)

    # ----- les ailes, en V : la droite déjà haute, la gauche plus couchée ; l'aile arrière orange dépasse derrière l'autre -----
    for nom, cote, leve in (("G", 1, 17), ("D", -1, 44)):
        a.piece("aile_avant_" + nom, aile_avant(), None, mat=pose_aile(cote, (0.040, -0.030, 0.048), leve, 12), poil=False)
        a.piece("aile_arriere_" + nom, aile_arriere(), None, mat=pose_aile(cote, (0.040, 0.014, 0.036), leve - 8, 42), poil=False)

    # ----- les six pattes : fines, sépia, plantées en étoile sous le thorax -----
    hanches = ((0.034, -0.040, -0.056), (0.036, -0.010, -0.058), (0.034, 0.022, -0.054))
    genoux = ((0.056, -0.082, 0.098), (0.080, -0.030, 0.106), (0.068, 0.030, 0.108))
    pieds = {1: ((0.062, -0.108), (0.088, -0.022), (0.072, 0.052)), -1: ((0.056, -0.094), (0.084, -0.038), (0.076, 0.040))}
    for cote, nom in ((1, "pattes_G"), (-1, "pattes_D")):
        pattes = None
        for i in range(3):
            (hx, hy, hz), (gx, gy, gz), (px, py) = hanches[i], genoux[i], pieds[cote][i]
            hanche = CORPS @ Vector((hx * cote, hy, hz))
            loin = Vector((px * cote - hanche.x, py - hanche.y, 0)).normalized() * 0.014
            points = [hanche, (gx * cote, gy, gz), (px * cote, py, 0.010), (px * cote + loin.x, py + loin.y, 0.0050)]
            une = A.tube(A.conges(points, 0.010, 4), lambda t: 0.0072 - 0.0020 * t, 12)
            pattes = une if pattes is None else pattes + une
        a.piece(nom, pattes, SEPIA, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py moro_sphinx). Les mesures sont celles du modèle, avant a.taille.

from poses import Pose, borne, cloche, onde

# Le modèle n'est pas symétrique (le corps est un peu tourné, les ailes en V, l'une plus haute que l'autre) : chaque
# aile et chaque antenne a son os à elle, à sa vraie place, nommé _g ou _d, sans miroir. Le corps, d'une seule pièce,
# se partage entre le thorax (« corps ») et l'abdomen, qui porte l'éventail. Les pattes se partagent entre le thorax
# (les hanches) et « pieds » (le bas, qui reste au sol) ; « pieds » pend à la racine mais tourne autour du même point
# que le thorax : en vol, on lui donne le geste du thorax et les pattes le suivent d'un bloc.
B3 = np.array(CORPS.to_3x3())                 # les axes du corps, en colonnes : sa gauche, son arrière, son dos
T3 = np.array(PORT.to_3x3())                  # ceux de la tête
_ORIGINE = np.array(CORPS @ Vector((0, 0, 0)))


def dans_corps(x, y, z):
    """Un point donné dans le repère du corps, rendu dans celui du jardin."""
    return tuple(CORPS @ Vector((x, y, z)))


def dans_tete(x, y, z):
    return tuple(PORT @ Vector((x, y, z)))


OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", dans_corps(0, 0, 0)),                     # le milieu du thorax
    ("abdomen", "corps", dans_corps(0, 0.020, 0)),                # la taille, entre le thorax et l'abdomen
    ("tete", "corps", dans_corps(0, -0.058, -0.008)),             # la nuque
    ("trompe", "tete", dans_tete(0, -0.039, -0.030)),             # là où la trompe sort de la tête
    ("antenne_g", "tete", dans_tete(0.014, -0.004, 0.040)),
    ("antenne_d", "tete", dans_tete(-0.014, -0.004, 0.040)),
    ("aile_avant_g", "corps", dans_corps(0.040, -0.030, 0.048)),  # les attaches des ailes (celles de pose_aile)
    ("aile_avant_d", "corps", dans_corps(-0.040, -0.030, 0.048)),
    ("aile_arriere_g", "corps", dans_corps(0.040, 0.014, 0.036)),
    ("aile_arriere_d", "corps", dans_corps(-0.040, 0.014, 0.036)),
    ("pieds", "racine", dans_corps(0, 0, 0)),                     # le bas des pattes
]


def souple(points, cote):
    """Le corps : devant la taille il suit le thorax, derrière elle l'abdomen (on le repère dans le repère du corps,
    où l'arrière est +Y), avec quatre centimètres et demi de passage en douceur."""
    y = (points - _ORIGINE) @ B3[:, 1]
    w = K.lisse((y - 0.005) / 0.045)
    return {"corps": 1 - w, "abdomen": w}


def pattes(points, cote):
    """Les pattes d'un côté : les hanches et les genoux suivent le thorax, le bas passe peu à peu à « pieds » en
    descendant vers le sol."""
    bas = 1 - K.lisse((points[:, 2] - 0.008) / 0.070)
    return {"pieds": bas, "corps": 1 - bas}


def _cote(nom):
    """Une pièce d'un côté (aile_avant_G, antenne_D) suit l'os de son côté (aile_avant_g, antenne_d)."""
    return lambda points, cote: {nom + cote.lower(): np.ones(len(points))}


PORTEURS = [("corps", souple, "corps"), ("eventail", "abdomen"), ("tete", "tete"), ("cerne", "tete"), ("oeil", "tete"),
            ("antenne", _cote("antenne")), ("trompe", "trompe"),
            ("aile_avant", _cote("aile_avant")), ("aile_arriere", _cote("aile_arriere")),
            ("pattes", pattes, "corps"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def doux(x):
    """De 0 à 1 en douceur, pour un geste qui part et s'arrête sans à-coup."""
    x = borne(x)
    return x * x * (3 - 2 * x)


def tour(axe, degres):
    """La rotation de « degres » autour d'un axe, en matrice 3 × 3."""
    x, y, z = np.asarray(axe, float) / np.linalg.norm(axe)
    a = math.radians(degres)
    c, s, u = math.cos(a), math.sin(a), 1 - math.cos(a)
    return np.array([[c + x * x * u, x * y * u - z * s, x * z * u + y * s],
                     [y * x * u + z * s, c + y * y * u, y * z * u - x * s],
                     [z * x * u - y * s, z * y * u + x * s, c + z * z * u]])


def angles(R):
    """Les angles qu'attend Pose (degrés, autour des axes du monde : X, puis Y, puis Z) pour la rotation R."""
    return (math.degrees(math.atan2(R[2, 1], R[2, 2])), math.degrees(math.asin(-max(-1.0, min(1.0, R[2, 0])))),
            math.degrees(math.atan2(R[1, 0], R[0, 0])))


def tete(p, hoche=0.0, tourne=0.0, penche=0.0):
    """La tête, autour de ses axes à elle : hoche > 0, le nez plonge ; tourne > 0, elle regarde vers sa gauche ;
    penche > 0, elle se couche sur son épaule gauche."""
    p.add("tete", rot=angles(tour(T3[:, 2], tourne) @ tour(T3[:, 0], hoche) @ tour(T3[:, 1], penche)))


def trompe(p, plonge=0.0, roule=1.0):
    """La trompe tourne sur sa base : plonge > 0, la pointe descend et revient sous la tête ; roule < 1 la raccourcit
    vers la tête (elle s'enroule)."""
    p.add("trompe", rot=angles(tour(T3[:, 0], plonge)), ech=(roule, roule, roule))


def antennes(p, g, d):
    """Les antennes se couchent vers l'arrière de g et d degrés (négatif : elles se dressent vers l'avant)."""
    p.add("antenne_g", rot=angles(tour(T3[:, 0], -g)))
    p.add("antenne_d", rot=angles(tour(T3[:, 0], -d)))


# En vol, les ailes battent autour d'un même angle des deux côtés : la gauche monte de 13,5°, la droite descend
# d'autant (au repos, l'une est levée de 17°, l'autre de 44°).
EGAL = 13.5


def ailes(p, g, d, recule=0.0):
    """Les ailes de chaque côté se lèvent de g et d degrés autour de l'axe du corps (celle de derrière suit celle de
    devant, comme chez les vrais sphinx), et se couchent vers l'arrière de « recule » degrés."""
    for l, c, leve in (("g", 1, g), ("d", -1, d)):
        R = angles(tour(B3[:, 2], c * recule) @ tour(B3[:, 1], -c * leve))
        p.add("aile_avant_" + l, rot=R)
        p.add("aile_arriere_" + l, rot=R)


def vol(p, haut, devant=0.0, cote=0.0, tangage=0.0, roulis=0.0, lacet=0.0):
    """En l'air : le thorax monte de « haut », glisse de « cote » vers sa gauche, se cabre (tangage < 0) ou pique ;
    le bas des pattes le suit d'un bloc, ramassé sous lui."""
    rot, pos = (tangage, roulis, lacet), (cote, -devant, haut)
    p.add("corps", rot=rot, pos=pos)
    p.add("pieds", rot=rot, pos=(cote, -devant, haut + 0.020 * borne(haut / 0.05)))


def repos(t):
    """Le gourmand pressé ne tient pas en place : il respire, l'abdomen pompe, il fait vibrer ses ailes par saccades
    (il se chauffe, prêt à repartir), relève deux fois son éventail comme une queue d'oiseau, tourne la tête vers nous
    puis de l'autre côté, tâte l'air de sa trompe et de ses antennes, cligne."""
    p = Pose()
    r = onde(t, 2)
    frisson = cloche(t, 0.36, 0.07) + cloche(t, 0.82, 0.05)
    queue = cloche(t, 0.56, 0.05) + cloche(t, 0.64, 0.04)
    regard = cloche(t, 0.18, 0.10) - cloche(t, 0.68, 0.09)
    p.add("corps", ech=(1 + 0.010 * r, 1 + 0.006 * r, 1 + 0.012 * r))
    p.add("abdomen", rot=(1.5 * r + 12 * queue, 0, 0), ech=(1 + 0.02 * r, 1, 1 + 0.02 * r))
    vibre = 5 * frisson * onde(t, 40)
    ailes(p, vibre, vibre)
    tete(p, -4 * cloche(t, 0.18, 0.10), 16 * regard, 4 * regard)
    trompe(p, 5 * onde(t, 3))
    antennes(p, 6 * onde(t, 3), 6 * onde(t, 4))
    p.ouvert = 1 - cloche(t, 0.12, 0.02) - cloche(t, 0.72, 0.02)
    return p


def avance(t):
    """Il vole sur place comme un colibri : le corps à l'horizontale, à quinze centimètres du sol, les ailes en un
    flou de huit battements par cycle, il se balance d'un côté à l'autre en penchant dans le virage ; l'éventail
    gouverne, la trompe pointe devant lui vers la fleur, les antennes sont couchées par le vent."""
    p = Pose()
    balance = onde(t, 1)
    vol(p, 0.15 + 0.008 * onde(t, 2), cote=0.020 * balance, tangage=-18 + 2 * onde(t, 2, 0.25), roulis=6 * balance)
    tete(p, 8)                                                   # le thorax s'est cabré : la tête regarde devant elle
    bat = 46 * onde(t, 8)
    ailes(p, EGAL + bat, -EGAL + bat)
    p.add("abdomen", rot=(-6 + 3 * onde(t, 2, 0.3), 0, 4 * balance))
    trompe(p, -18)
    antennes(p, 10 + 3 * onde(t, 4), 10 + 3 * onde(t, 4, 0.3))
    return p


def mange(t):
    """Il se penche sur la fleur et la trompe y plonge par petites gorgées, quatre fois ; l'abdomen se remplit, les ailes
    frémissent d'aise, les antennes se penchent vers la fleur ; puis il relève la tête, repu, et regarde alentour."""
    p = Pose()
    leve = cloche(t, 0.86, 0.12)
    bas = 1 - leve
    gorgee = max(0.0, onde(t, 4, -0.25)) ** 2 * bas
    plein = doux(t / 0.8) * (1 - doux((t - 0.84) / 0.14))
    aise = cloche(t, 0.30, 0.08) + cloche(t, 0.60, 0.08)
    p.add("corps", rot=(6 * bas, 0, 0))
    tete(p, 8 * bas - 6 * leve, 10 * leve * onde(t, 2))
    trompe(p, -21 * bas + 7 * gorgee)                           # sous le nez qui plonge, la pointe effleure le sol
    p.add("abdomen", ech=(1 + 0.12 * plein, 1 + 0.04 * plein, 1 + 0.12 * plein))
    vibre = 4 * aise * onde(t, 30)
    ailes(p, vibre, vibre)
    antennes(p, -12 * bas, -12 * bas)
    p.ouvert = 1 - 0.35 * plein * bas
    return p


def joie(t):
    """Il décolle d'un coup, les ailes à plein régime, fait une pirouette en l'air en agitant son éventail, la trompe
    déroulée comme un ruban, puis se repose sur ses pattes."""
    p = Pose()
    air = doux(t / 0.16) * (1 - doux((t - 0.72) / 0.20))
    pirouette = doux((t - 0.18) / 0.50)
    vol(p, 0.13 * air, tangage=-16 * air, lacet=360 * pirouette)
    tete(p, 8 * air)
    bat = 46 * onde(t, 16)
    ailes(p, (EGAL + bat) * air, (-EGAL + bat) * air)
    p.add("abdomen", rot=(8 * air * onde(t, 4), 0, 10 * air * onde(t, 3)))
    trompe(p, -20 * air)
    antennes(p, -14 * air, -14 * air)
    return p


def dort(t):
    """Posé, il dort : le corps tassé sur ses pattes, les ailes rabattues en toit le long du corps, la tête basse, la
    trompe roulée sous elle, les antennes couchées en arrière ; les yeux fermés, il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", rot=(-6, 0, 0), pos=(0, 0, -0.020), ech=(1 + 0.010 * r, 1, 1 + 0.015 * r))
    ailes(p, -10, -37, 25)
    tete(p, 14 + 1.5 * r)
    trompe(p, -15, 0.55)
    antennes(p, 35, 35)
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Moro-sphinx")
