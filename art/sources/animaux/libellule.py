"""La libellule en peluche : un long corps turquoise électrique bagué de marine, un thorax bossu barré de deux écharpes,
deux gros boutons qui se touchent presque, quatre ailes de feutrine gris perle nervurées de fil, et une queue relevée
en arc dont le bout est corail. Une acrobate fière : le menton levé, les ailes penchées comme un balancier, une patte en l'air.

    python libellule.py        fabrique la fiche art/apercus/animaux/libellule.png
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

TURQUOISE = M.hexa("#22f2ff")                 # le turquoise électrique du poil (il fonce et se sature une fois en peluche)
MARIN = M.hexa("#3a5fb0")                     # les bagues et les écharpes, en poil : sort marine foncé
PERLE = M.hexa("#dfe3ee")                     # la feutrine des ailes
THORAX = Vector((0.0, 0.0, 0.120))
TETE = Vector((0.0, -0.080, 0.142))
PORT = A.repere(TETE, (-8, 10, 18))           # la tête : le menton levé, penchée, tournée vers nous
QUEUE = Vector((0.0, 0.045, 0.118))           # là où la queue sort du thorax
LONG = 0.33                                   # la longueur de la queue
ARC = LONG / math.radians(75)                 # le rayon de l'arc qui la relève
BAGUES = (0.038, 0.076, 0.114, 0.152, 0.190, 0.228, 0.266, 0.304)      # le milieu de chaque bague marine, le long de la queue


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête, rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def rayon(z):
    """Le rayon de la queue à la distance z du thorax : épaisse au départ, fine au milieu, en massue vers le bout,
    et un peu serrée par chaque bague (c'est ce qui la fait segmentée)."""
    r = np.interp(z, [0, 0.03, 0.11, 0.23, 0.29, 0.318, LONG], [0.023, 0.020, 0.0130, 0.0120, 0.0155, 0.011, 0.0])
    return float(r) * (1 - 0.10 * sum(math.exp(-((z - b) / 0.005) ** 2) for b in BAGUES))


def cambre(v):
    """Relève la queue le long d'un arc (vers le -Y de la pièce, son dos) : couchée au départ, la pointe en l'air."""
    angle = v[:, 2] / ARC
    s = v.copy()
    s[:, 1] = (ARC + v[:, 1]) * np.cos(angle) - ARC
    s[:, 2] = (ARC + v[:, 1]) * np.sin(angle)
    return s


def aile(contour, tache, miroir):
    """Une aile de feutrine gris perle, dans son plan (X : vers le bout, Y : vers l'arrière), avec sa tache corail près
    du bout, contre le bord d'attaque. miroir : 1 à gauche, -1 à droite."""
    m = A.decoupe(A.courbe(np.array(contour) * [miroir, 1], 5, fermee=True), 0.0045, 0.0018).peint(PERLE)
    stigma = A.decoupe(A.cercle(1.0, 20) * [0.014, 0.0048], 0.003, 0.001).pose((tache[0] * miroir, tache[1], 0.0030)).peint(K.CORAIL)
    return m + stigma


def nervures(a, nom, rep, miroir, long, milieu):
    """Les nervures d'une aile, brodées au fil marine : une boucle qui longe le bord d'attaque puis revient par le
    milieu de l'aile, et quelques traverses entre les deux."""
    def point(f, w):
        return rep @ Vector((long * f * miroir, w, 0.0036))
    boucle = [point(f, -0.005) for f in (0.12, 0.35, 0.60, 0.72)] + [point(f, milieu) for f in (0.72, 0.60, 0.35, 0.12)]
    a.broderie(nom + "_boucle", boucle + [boucle[0]], 0.0014, K.MARINE)
    cases = [point(0.22, -0.005), point(0.22, milieu), point(0.42, milieu), point(0.42, -0.005), point(0.62, -0.005), point(0.62, milieu)]
    a.broderie(nom + "_cases", cases, 0.0013, K.MARINE)


def construire():
    a = K.Animal("libellule")
    a.taille = 0.46
    a.tete = PORT @ Vector((0, -0.040, 0.004))

    # ----- le thorax : une grosse bosse de peluche turquoise, le poitrail en avant, barrée de deux écharpes marine en biais -----
    #       (la boule est peinte par tranches puis couchée avant d'être sculptée : les écharpes suivent ses anneaux, leur bord reste net)
    thorax = K.bandes(A.boule(1.0, 56, 28), [(-0.60, TURQUOISE), (-0.34, MARIN), (0.0, TURQUOISE), (0.32, MARIN), (9, TURQUOISE)]).pose(rot=(-53, 0, 0))
    thorax.sculpte(lambda v: K.bosse(v, (0, -0.30, 0.95), 0.24, 0.4)).etire(0.050, 0.062, 0.056)
    a.piece("thorax", thorax, None, pos=THORAX, rot=(-12, 0, 0))

    # ----- la queue : un long fuseau tourné d'une pièce, bagué de marine, le bout corail, puis relevé en arc -----
    profil = [(rayon(z), z) for z in np.linspace(0, LONG, 110)]
    profil[0], profil[-1] = (0.0, 0.0), (0.0, LONG)
    bagues = [palier for b in BAGUES for palier in ((b - 0.007, TURQUOISE), (b + 0.007, MARIN))] + [(9, K.CORAIL)]
    queue = K.bandes(A.tour(profil, 40), bagues)
    a.piece("queue", queue.sculpte(cambre), None, pos=QUEUE, rot=(-98, 0, 0))

    # ----- la tête : large et basse, presque toute en yeux ; deux gros boutons qui se touchent presque -----
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.050, 0.038, 0.040), TURQUOISE, mat=PORT)
    # une calotte de feutrine marine cousue sur le crâne, au ras des yeux : avec ses deux gros boutons, un casque de voltige
    a.rustine("calotte", "tete", TETE, vers(0, 0.50, 0.86), 1.25, K.MARINE, 0.003, 22, fil=K.CREME)
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, vers(0.0238 * cote, -0.036, 0.010))
        a.bouton("oeil_" + nom, p + n * 0.0035, n, 0.0220)
        # deux antennes minuscules, comme des cils, au-dessus des yeux
        pied = PORT @ Vector((0.012 * cote, -0.022, 0.034))
        a.piece("antenne_" + nom, A.tube([pied, pied + vers(0.006 * cote, -0.008, 0.016), pied + vers(0.016 * cote, -0.012, 0.028)],
                                         lambda t: 0.0034 - 0.0012 * t, 12), K.MARINE, poil=False)
    # un sourire en coin, sûr de lui
    a.broderie("sourire", a.trace("tete", TETE, [vers(-0.18, -0.90, -0.62), vers(0.06, -0.90, -0.70), vers(0.32, -0.86, -0.56)], 0.0048), 0.0022, K.MARINE)

    # ----- les quatre ailes, ouvertes à plat : celles de devant filent vers l'avant, celles de derrière vers l'arrière ;
    #       le bord d'attaque plonge un peu, et tout le plan penche à gauche comme un balancier -----
    devant = ((0, -0.006), (0.05, -0.012), (0.12, -0.014), (0.175, -0.010), (0.195, 0.004), (0.180, 0.022), (0.12, 0.030), (0.05, 0.022), (0, 0.008))
    derriere = ((0, -0.006), (0.05, -0.012), (0.12, -0.013), (0.165, -0.008), (0.180, 0.006), (0.160, 0.026), (0.10, 0.040), (0.045, 0.042), (0.008, 0.022))
    for nom, cote, penche in (("G", 1, (9, 6)), ("D", -1, (5, 4))):
        rep = A.repere((0.020 * cote, -0.010, 0.170), (14, penche[0], -14 * cote))
        a.piece("aile_avant_" + nom, aile(devant, (0.160, -0.004), cote), None, mat=rep, poil=False)
        nervures(a, "avant_" + nom, rep, cote, 0.195, 0.012)
        rep = A.repere((0.020 * cote, 0.026, 0.164), (10, penche[1], 12 * cote))
        a.piece("aile_arriere_" + nom, aile(derriere, (0.146, -0.003), cote), None, mat=rep, poil=False)
        nervures(a, "arriere_" + nom, rep, cote, 0.180, 0.018)

    # ----- les six pattes, fines, groupées sous le thorax ; l'avant gauche est levée, comme un salut au public -----
    pattes = None
    for cote in (1, -1):
        for i, (hanche, genou, pied) in enumerate((((0.022, -0.030, 0.080), (0.060, -0.064, 0.102), (0.074, -0.112)),
                                                   ((0.024, -0.008, 0.078), (0.080, -0.012, 0.106), (0.114, -0.026)),
                                                   ((0.022, 0.014, 0.080), (0.068, 0.042, 0.102), (0.096, 0.084)))):
            if cote == 1 and i == 0:
                points = [hanche, (0.058, -0.072, 0.112), (0.078, -0.118, 0.098), (0.086, -0.134, 0.110)]
            else:
                loin = Vector((pied[0] - hanche[0], pied[1] - hanche[1], 0)).normalized() * 0.016
                px, py = pied[0], pied[1] + 0.012 * cote * (i - 1)      # aucun pied n'est posé comme son vis-à-vis
                points = [hanche, genou, (px, py, 0.011), (px + loin.x, py + loin.y, 0.0052)]
            une = A.tube(A.conges([(cote * x, y, z) for x, y, z in points], 0.009, 4), lambda t: 0.0066 - 0.0020 * t, 12)
            pattes = une if pattes is None else pattes + une
    a.piece("pattes", pattes, K.MARINE, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py libellule). Les mesures sont celles du modèle, avant a.taille.

from poses import Pose, borne, cloche, onde

_QUEUE = np.array(A.repere(QUEUE, (-98, 0, 0)))          # la queue : de sa pièce (tournée tout droit) au jardin


def fil_queue(z):
    """Le milieu de la queue à la distance z du thorax, le long de son arc : là où cambre() l'a couchée."""
    z = np.atleast_1d(np.asarray(z, float))
    v = np.stack([np.zeros_like(z), ARC * np.cos(z / ARC) - ARC, ARC * np.sin(z / ARC), np.ones_like(z)], axis=-1)
    return (v @ _QUEUE.T)[:, :3]


# La queue plie en trois (à sa sortie du thorax, au premier tiers, au deuxième) ; les ailes ont chacune leur épaule
# (le modèle est droit : celles de droite sont les miroirs de celles de gauche) ; les pattes, une seule pièce, se
# partagent entre le thorax (les hanches), « pieds » (le bas, qui reste au sol quand le thorax bouge) et « salut »
# (l'avant gauche, levée). « pieds » pend à la racine mais tourne autour du même point que le thorax : en vol, on lui
# donne le geste du thorax et les pattes le suivent d'un bloc.
OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", tuple(THORAX)),                  # le milieu du thorax
    ("tete", "corps", (0.0, -0.050, 0.140)),             # la nuque, entre le thorax et la tête
    ("queue", "corps", tuple(QUEUE)),                    # là où la queue sort du thorax
    ("queue2", "queue", tuple(fil_queue(0.11)[0])),      # le premier tiers de la queue
    ("queue3", "queue2", tuple(fil_queue(0.22)[0])),     # le deuxième tiers, avant la massue
    ("aile_avant_G", "corps", (0.020, -0.010, 0.170)),   # l'attache de l'aile de devant
    ("aile_arriere_G", "corps", (0.020, 0.026, 0.164)),  # l'attache de l'aile de derrière
    ("salut", "corps", (0.022, -0.030, 0.080)),          # la hanche de la patte levée
    ("pieds", "racine", tuple(THORAX)),                  # le bas des pattes
]

_Z_QUEUE = np.linspace(0.0, LONG, 400)
_FIL_QUEUE = fil_queue(_Z_QUEUE)


def queue(points, cote):
    """La queue : chaque point retrouve sa distance au thorax (le point de l'arc le plus proche), puis passe en douceur
    d'un os à l'autre entre deux attaches."""
    z = np.empty(len(points))
    for d in range(0, len(points), 2000):
        q = points[d:d + 2000]
        z[d:d + 2000] = _Z_QUEUE[np.argmin(((q[:, None, :] - _FIL_QUEUE[None, :, :]) ** 2).sum(-1), axis=1)]
    f1, f2 = K.lisse(z / 0.11), K.lisse((z - 0.11) / 0.11)
    return {"queue": 1 - f1, "queue2": f1 - f2, "queue3": f2}


def pattes(points, cote):
    """Les six pattes : la levée (l'avant gauche, seule à passer devant y = -0,04) suit « salut » ; des autres, les
    hanches et les genoux suivent le thorax, et le bas passe peu à peu à « pieds » en descendant vers le sol."""
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    salut = K.lisse((-y - 0.040) / 0.016) * (x > 0.005)
    bas = (1 - salut) * (1 - K.lisse((z - 0.010) / 0.065))
    return {"salut": salut, "pieds": bas, "corps": 1 - salut - bas}


PORTEURS = [("thorax", "corps"), ("queue", queue, "queue"), ("tete", "tete"), ("calotte", "tete"), ("oeil", "tete"),
            ("sourire", "tete"), ("antenne", "tete"),
            ("aile_avant", "aile_avant", True), ("aile_arriere", "aile_arriere", True),
            # les nervures brodées suivent leur aile
            ("avant_G", "aile_avant_G"), ("avant_D", "aile_avant_D"), ("arriere_G", "aile_arriere_G"), ("arriere_D", "aile_arriere_D"),
            ("pattes", pattes, "corps"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def doux(x):
    """De 0 à 1 en douceur, pour un geste qui part et s'arrête sans à-coup."""
    x = borne(x)
    return x * x * (3 - 2 * x)


def ailes(p, avant, arriere, roulis=0.0):
    """Les ailes se lèvent de « avant » et « arriere » degrés des deux côtés (autour de l'axe du corps) ; roulis > 0
    lève celles de gauche et baisse celles de droite : le balancier."""
    p.paire("aile_avant", rot=(0, -avant, 0))
    p.paire("aile_arriere", rot=(0, -arriere, 0))
    for nom in ("aile_avant_G", "aile_arriere_G", "aile_avant_D", "aile_arriere_D"):
        p.add(nom, rot=(0, -roulis, 0))


def vol(p, haut, devant=0.0, tangage=0.0, roulis=0.0, replie=1.0):
    """En l'air : le thorax monte de « haut », file de « devant » vers l'avant, pique du nez de « tangage » degrés et
    roule de « roulis » ; le bas des pattes le suit d'un bloc, ramassé sous lui (replie de 0 à 1), et la patte levée
    se rabat contre les autres."""
    rot, pos = (tangage, roulis, 0.0), (0.0, -devant, haut)
    p.add("corps", rot=rot, pos=pos)
    p.add("pieds", rot=rot, pos=(0.0, -devant, haut + 0.022 * replie))
    p.add("salut", rot=(26 * replie, 0, 0))


def repos(t):
    """L'acrobate attend son public : elle respire, l'abdomen pompe, la tête pivote par à-coups (à gauche, en l'air, à
    droite), les ailes balancent comme un balancier ; elle cligne, et de sa patte levée elle fait coucou."""
    p = Pose()
    r = onde(t, 2)
    pompe = onde(t, 4)
    gauche, droite, ciel = cloche(t, 0.22, 0.08), cloche(t, 0.50, 0.08), cloche(t, 0.36, 0.06)
    coucou = cloche(t, 0.74, 0.10)
    p.add("corps", ech=(1 + 0.010 * r, 1 + 0.006 * r, 1 + 0.014 * r))
    p.add("queue", rot=(1.5 * pompe, 0, 0))
    p.add("queue2", rot=(1.2 * pompe, 0, 0))
    p.add("tete", rot=(-8 * ciel, 6 * gauche - 8 * droite, 28 * gauche - 24 * droite))
    ailes(p, 0.0, 0.0, 5 * onde(t, 1))
    p.add("salut", rot=(-14 * coucou, 0, 24 * coucou * onde(t, 12)))
    p.ouvert = 1 - cloche(t, 0.10, 0.02) - cloche(t, 0.60, 0.02)
    return p


def avance(t):
    """Elle fait du vol stationnaire, posée sur l'air à vingt centimètres, puis file d'un coup d'aile, le nez plongé
    et la queue tendue derrière elle, avant de se rasseoir sur l'air. Les ailes de devant et de derrière battent à
    contretemps, comme chez les vraies ; les pattes sont ramassées sous le thorax."""
    p = Pose()
    file = cloche(t, 0.70, 0.22)
    vol(p, 0.20 + 0.010 * onde(t, 2), devant=0.050 * file, tangage=16 * file)
    p.add("tete", rot=(-12 * file, 0, 0))                    # la tête reste d'aplomb, les yeux sur la route
    p.add("queue", rot=(-6 - 6 * file, 0, 0))
    p.add("queue2", rot=(-8 * file, 0, 0))
    p.add("queue3", rot=(-8 * file, 0, 0))
    ailes(p, 8 + 36 * onde(t, 6), 8 + 36 * onde(t, 6, 0.5))
    return p


def mange(t):
    """Elle tient sa proie dans sa patte levée et la porte à sa bouche : penchée dessus, elle croque à petits coups de
    tête, la queue relevée en contrepoids, les ailes frémissent ; puis elle se redresse et regarde alentour."""
    p = Pose()
    leve = cloche(t, 0.88, 0.10)
    bas = 1 - leve
    croque = onde(t, 10) * bas
    p.add("corps", rot=(5 * bas, 0, 0))
    p.add("tete", rot=(16 * bas + 3 * croque - 6 * leve, 0, 10 * leve * onde(t, 2)))
    p.add("salut", rot=(-6 * bas, 0, -26 * bas))
    p.add("queue", rot=(4 * bas, 0, 0))
    frisson = 2.5 * cloche(t, 0.40, 0.08) * onde(t, 30)
    ailes(p, frisson, frisson)
    p.ouvert = 1 - cloche(t, 0.55, 0.02)
    return p


def joie(t):
    """Sa fête d'acrobate : elle décolle, fait un tonneau complet sur elle-même, la patte levée en l'air comme pour
    saluer, et se repose d'aplomb sur ses cinq pattes, le menton levé."""
    p = Pose()
    air = doux(t / 0.18) * (1 - doux((t - 0.70) / 0.22))
    tonneau = doux((t - 0.22) / 0.40)
    vol(p, 0.20 * air, tangage=-8 * air, roulis=360 * tonneau, replie=air)
    p.add("salut", rot=(-26 * air - 30 * air, 0, 0))         # elle défait le repli du vol, et lève la patte encore plus haut
    p.add("tete", rot=(-10 * air, 0, 0))
    p.add("queue", rot=(8 * air * onde(t, 3), 0, 0))
    ailes(p, (10 + 34 * onde(t, 12)) * air, (10 + 34 * onde(t, 12, 0.5)) * air)
    return p


def dort(t):
    """Elle dort perchée : le thorax tassé sur les pattes, la tête qui pique du nez, la queue retombée, les ailes un
    peu basses, la patte levée enfin posée ; les yeux fermés, elle respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.016), rot=(4, 0, 0), ech=(1 + 0.008 * r, 1, 1 + 0.012 * r))
    p.add("tete", rot=(18 + 1.5 * r, 6, 0))
    p.add("queue", rot=(-10 - 1.0 * r, 0, 0))
    p.add("queue2", rot=(-8, 0, 0))
    p.add("queue3", rot=(-6, 0, 0))
    ailes(p, -9, -7)
    p.add("salut", rot=(34, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Libellule")
