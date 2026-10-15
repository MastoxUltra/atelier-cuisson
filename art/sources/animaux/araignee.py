"""L'araignée en peluche, deuxième dessin : la chasseuse à l'affût. Un abdomen de peluche prune en goutte, relevé haut
derrière elle comme une croupe de chat qui va sauter, marqué sur le dos d'un grand sablier de feutrine crème ; devant,
un céphalothorax d'aubergine, bas et bossu, qui porte un regard de tueuse : deux yeux noirs rapprochés cerclés de mauve,
coupés à plat par des paupières lourdes, et quatre petites perles noires au-dessus. Huit pattes coudées, les genoux très
hauts au-dessus du corps, bagués de mauve : les deux de derrière repliées sous elle comme des ressorts, la patte avant
droite levée haut, prête à frapper. Sous les yeux, deux chélicères prune terminées par des crochets crème.

    python araignee.py        fabrique la fiche art/apercus/animaux/araignee.png
    (le premier dessin, jamais gardé : araignee_ancien.py)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import garnitures as G
import matieres as M
import peluche as K

PRUNE = M.hexa("#9c5aa2")                     # l'abdomen : un prune franc (le poil le fonce)
AUBERGINE = M.hexa("#40234a")                 # le céphalothorax, les pattes : le prune le plus sombre, en feutrine
MAUVE = M.hexa("#c99bd4")                     # le prune le plus clair : le tour des yeux, les genoux, le bout des pattes
CREME = M.hexa("#f6ead0")                     # l'accent : le sablier et les crochets
CEPHALO = Vector((0.0, -0.040, 0.080))
PORT = A.repere(CEPHALO, (12, 0, 14))         # le nez bas, tourné vers sa gauche : elle a vu quelque chose
ABDOMEN = A.cadre((0.0, 0.016, 0.104), (0.0, 0.80, 0.60), (0, -0.6, 0.8))   # la goutte part en arrière et vers le haut


def vers(x, y, z):
    """Une direction donnée dans le repère du céphalothorax (devant = -y), rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def sablier(th):
    """L'ouverture du sablier selon l'angle autour de son axe : deux triangles pointe à pointe, dans le sens du corps,
    la taille étroite (le sens du corps est l'angle pi/2 dans le repère de la rustine)."""
    d = abs((th % math.pi) - math.pi / 2)               # l'écart à l'axe du dos
    return 0.08 + (0.66 / math.cos(min(d, 0.62)) - 0.08) * float(K.lisse((0.64 - d) / 0.10))


def patte(points, gros=0.0130):
    """Une patte coudée de feutrine : aubergine, un genou bagué de mauve au premier coude, le bout mauve."""
    p = [np.array(q, float) for q in points]
    longs = [np.linalg.norm(p[i + 1] - p[i]) for i in range(len(p) - 1)]
    genou = longs[0] / sum(longs)
    return K.tube_peint(A.conges(points, 0.020, 6), lambda t: gros * (1 - 0.55 * t),
                        [(genou - 0.040, AUBERGINE), (genou + 0.030, MAUVE), (0.86, AUBERGINE), (9, MAUVE)])


def construire():
    a = K.Animal("araignee")
    a.taille = 0.40
    a.tete = PORT @ Vector((0.0, -0.050, 0.010))

    # ----- l'abdomen : une goutte tournée, ronde devant, pointue derrière, dressée en arrière ; la couture du dos
    #       file du pédicelle aux filières, le sablier crème posé dessus -----
    prof = A.profil([(0, 0), (0.036, 0.006), (0.062, 0.030), (0.074, 0.068), (0.071, 0.106), (0.056, 0.140), (0.034, 0.164),
                     (0.014, 0.178), (0, 0.184)], 6)
    goutte = K.bandes(A.tour(prof, 56).sculpte(lambda v: v * [1.0, 0.90, 1.0]), [(0.168, PRUNE), (9, AUBERGINE)])
    G.sillons(goutte, [14], 0.005, 1.1)
    a.piece("abdomen", goutte, None, mat=ABDOMEN)
    a.couture("dos", "abdomen", 14, 0.10, 0.88, fil=AUBERGINE)
    a.couture("flanc", "abdomen", 0, 0.22, 0.78, "droit", fil=MAUVE)
    milieu = ABDOMEN @ Vector((0, 0, 0.085))
    a.rustine("sablier", "abdomen", milieu, ABDOMEN.to_3x3() @ Vector((0, 1, 0)), sablier, CREME, 0.0035, 22, fil=AUBERGINE)
    # un rapiéçage mauve sur le flanc droit, au point de feston
    a.rustine("rapiecage", "abdomen", milieu, ABDOMEN.to_3x3() @ Vector((-0.9, 0.35, -0.15)), 0.30, MAUVE, 0.003, 14, fil=AUBERGINE)

    # ----- le céphalothorax : bas et bossu, le front haut et carré qui porte les yeux -----
    def bosse(v):
        v = K.bosse(v, (0, -0.70, 0.70), 0.22, 0.25)          # le front qui monte
        s = K.emousse(v, 0.90) * [0.056, 0.066, 0.042]
        return s
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(bosse), AUBERGINE, mat=PORT, poil=False)

    # ----- les yeux : deux gros, rapprochés, cerclés de mauve, coupés à plat par la paupière ; quatre petites perles -----
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", CEPHALO, vers(0.38 * cote, -0.80, 0.46))
        a.rustine("cerne_" + nom, "tete", CEPHALO, n, 0.42, MAUVE, 0.0025, 0)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0165)
        a.piece("lourde_" + nom, K.paupiere(0.0165, 0.22), AUBERGINE, mat=A.cadre(p + n * 0.004, n, vers(-0.18 * cote, 0.1, 1)), poil=False)
    perles = None
    for regard, r in (((0.62, -0.62, 0.48), 0.0062), ((-0.62, -0.62, 0.48), 0.0062), ((0.36, -0.30, 0.88), 0.0055),
                      ((-0.36, -0.30, 0.88), 0.0055)):
        p, n = a.surface("tete", CEPHALO, vers(*regard))
        une = A.boule(1.0, 16, 8).etire(r, r, r * 0.7).pose(tuple(p + n * 0.001), A.viser(n))
        perles = une if perles is None else perles + une
    a.piece("perles", perles, K.NOIR, poil=False)

    # ----- les chélicères : deux courts boudins prune sous les yeux, au bout des crochets crème recourbés en dedans -----
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", CEPHALO, vers(0.24 * cote, -0.80, -0.20))
        chemin = A.courbe([p - n * 0.006, p + vers(0.004 * cote, -0.012, -0.010), p + vers(0.003 * cote, -0.020, -0.022),
                           p + vers(-0.004 * cote, -0.018, -0.032), p + vers(-0.009 * cote, -0.011, -0.037)], 6)
        a.piece("crochet_" + nom, K.tube_peint(chemin, lambda t: 0.0100 - 0.0080 * t, [(0.40, PRUNE), (9, CREME)]), None, poil=False)
        # les pédipalpes : deux petits bras pliés de chaque côté de la bouche
        p, n = a.surface("tete", CEPHALO, vers(0.62 * cote, -0.62, -0.30))
        palpe = [tuple(p - n * 0.004), tuple(p + vers(0.016 * cote, -0.020, 0.010)), tuple(p + vers(0.016 * cote, -0.042, 0.004)),
                 tuple(p + vers(0.010 * cote, -0.052, -0.014))]
        a.piece("palpe_" + nom, patte(palpe, 0.0068), None, poil=False)

    # ----- les huit pattes, en arche : la cuisse monte au genou, très haut, le tibia redescend en s'écartant, le tarse
    #       se couche au sol. Celles de derrière, repliées court sous l'abdomen, genou haut : des ressorts. La patte avant
    #       droite est levée, le bout pointé vers l'avant -----
    #       (cap en degrés depuis +X, portée, hauteur du genou) ; à droite le cap est pris en miroir
    reglages = {"G": [(-44, 0.235, 0.105), (-6, 0.220, 0.172), (28, 0.200, 0.174), (66, 0.135, 0.205)],
                "D": [None, (-26, 0.215, 0.168), (22, 0.200, 0.178), (58, 0.130, 0.210)]}
    for nom, cote in (("G", 1), ("D", -1)):
        for k, reglage in enumerate(reglages[nom]):
            if reglage is None:
                continue
            cap, portee, genou = reglage
            d = Vector((cote * math.cos(math.radians(cap)), math.sin(math.radians(cap)), 0))
            h = CEPHALO + Vector((cote * 0.036, max(-0.026, min(0.020, d.y * 0.030)), -0.012))
            une = patte([tuple(h), tuple(h + d * 0.34 * portee + Vector((0, 0, genou - h.z))),
                         tuple(h + d * 0.66 * portee + Vector((0, 0, 0.52 * genou - h.z))),
                         tuple(h + d * 0.92 * portee + Vector((0, 0, 0.020 - h.z))), tuple(h + d * portee + Vector((0, 0, 0.004 - h.z)))])
            a.piece("patte%d_%s" % (k + 1, nom), une, None, poil=False)            # une pièce par patte : chacune marche à son tour
    h = CEPHALO + Vector((-0.034, -0.026, -0.006))
    a.piece("patte_levee", patte([tuple(h), tuple(h + Vector((-0.060, -0.040, 0.140))), tuple(h + Vector((-0.080, -0.118, 0.168))),
                                  tuple(h + Vector((-0.078, -0.170, 0.140))), tuple(h + Vector((-0.072, -0.184, 0.118)))]), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py araignee). Les mesures sont celles du modèle, avant a.taille.
# Rien n'est en miroir (la tête tournée, la patte avant droite levée, chaque patte à son cap) : chaque patte a son os à
# elle, à sa hanche (p1_g ... p4_d, et « levee »), et pend à la racine : posée, elle reste au sol quand le corps bouge ;
# pour un saut, « suivre » l'emmène avec le corps.

from poses import Pose, borne, cloche, onde

# chaque patte : sa hanche et son pied, mesurés sur le modèle
PATTES = {"p1_g": ((0.036, -0.0608, 0.068), (0.205, -0.2241, 0.004)), "p2_g": ((0.036, -0.0431, 0.068), (0.2548, -0.0661, 0.004)),
          "p3_g": ((0.036, -0.0259, 0.068), (0.2126, 0.0680, 0.004)), "p4_g": ((0.036, -0.0200, 0.068), (0.0909, 0.1033, 0.004)),
          "p2_d": ((-0.036, -0.0532, 0.068), (-0.2292, -0.1474, 0.004)), "p3_d": ((-0.036, -0.0288, 0.068), (-0.2214, 0.0462, 0.004)),
          "p4_d": ((-0.036, -0.0200, 0.068), (-0.1049, 0.0902, 0.004)), "levee": ((-0.034, -0.066, 0.074), (-0.106, -0.250, 0.192))}
_CENTRE = np.array(tuple(CEPHALO))

OS = ([("racine", None, (0, 0, 0)),
       ("corps", "racine", tuple(CEPHALO)),                # le céphalothorax : elle s'y tapit et s'y lance
       ("abdomen", "corps", (0.0, 0.016, 0.104)),          # le pédicelle, d'où part la goutte
       ("palpe_g", "corps", (0.0432, -0.0629, 0.0556)),    # le pied de chaque pédipalpe
       ("palpe_d", "corps", (-0.0274, -0.0805, 0.0556)),
       ("crochet_g", "corps", (0.0272, -0.0854, 0.0564)),  # la racine de chaque chélicère
       ("crochet_d", "corps", (-0.0027, -0.0929, 0.0564))]
      + [(n, "racine", h) for n, (h, _f) in PATTES.items()])


def _cote(os_):
    """Une pièce d'un côté (palpe_G, crochet_D) suit l'os de son côté (palpe_g, crochet_d)."""
    return lambda points, cote: {os_ + cote.lower(): np.ones(len(points))}


def _patte(k):
    """La patte numéro k d'un côté (patte2_D) suit son os (p2_d)."""
    return lambda points, cote: {"p%d%s" % (k, cote.lower()): np.ones(len(points))}


PORTEURS = [("abdomen", "abdomen"), ("dos", "abdomen"), ("flanc", "abdomen"), ("sablier", "abdomen"), ("rapiecage", "abdomen"),
            ("tete", "corps"), ("cerne", "corps"), ("oeil", "corps"), ("lourde", "corps"), ("perles", "corps"),
            ("palpe", _cote("palpe")), ("crochet", _cote("crochet")), ("patte_levee", "levee"),
            ("patte1", _patte(1)), ("patte2", _patte(2)), ("patte3", _patte(3)), ("patte4", _patte(4)),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _rot(r):
    """La matrice d'une rotation de Pose (degrés ; X, puis Y, puis Z, autour des axes du monde)."""
    x, y, z = (math.radians(a) for a in r)
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    return (np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
            @ np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]))


def _tour(axe, degres):
    """La rotation de « degres » autour d'un axe, en matrice 3 × 3."""
    x, y, z = np.asarray(axe, float) / np.linalg.norm(axe)
    a = math.radians(degres)
    c, s, u = math.cos(a), math.sin(a), 1 - math.cos(a)
    return np.array([[c + x * x * u, x * y * u - z * s, x * z * u + y * s],
                     [y * x * u + z * s, c + y * y * u, y * z * u - x * s],
                     [z * x * u - y * s, z * y * u + x * s, c + z * z * u]])


def _angles(R):
    """Les angles qu'attend Pose (degrés, autour des axes du monde : X, puis Y, puis Z) pour la rotation R."""
    return (math.degrees(math.atan2(R[2, 1], R[2, 2])), math.degrees(math.asin(-max(-1.0, min(1.0, R[2, 0])))),
            math.degrees(math.atan2(R[1, 0], R[0, 0])))


def leve(nom, degres, balaie=0.0):
    """La rotation qui lève une patte de « degres » (son bout monte, autour de l'axe couché en travers d'elle) et la
    balaie de « balaie » degrés autour de la verticale (> 0 : vers sa gauche)."""
    h, f = (np.array(q) for q in PATTES[nom])
    d = (f - h) * [1, 1, 0]
    return _tour((0, 0, 1), balaie) @ _tour(np.cross((0, 0, 1), d), -degres)


def suivre(p, rot, pos):
    """Le corps tourne de « rot » et se déplace de « pos » (autour de son pivot) : les pattes, pendues à la racine,
    suivent le même mouvement."""
    p.add("corps", rot=rot, pos=pos)
    m = _rot(rot)
    for n, (h, _f) in PATTES.items():
        h = np.array(h)
        p.add(n, rot=rot, pos=tuple(_CENTRE + np.asarray(pos, float) + m @ (h - _CENTRE) - h))


def repos(t):
    """À l'affût, immobile : l'abdomen respire, les palpes tambourinent ; la patte levée tâte l'air, se tend deux fois
    vers ce qu'elle guette, et elle se ramasse un instant sur ses pattes comme un ressort qu'on charge ; elle cligne."""
    p = Pose()
    r = onde(t, 2)
    p.add("abdomen", rot=(3 * r, 0, 0), ech=(1 + 0.03 * r, 1 + 0.02 * r, 1 + 0.03 * r))
    p.add("palpe_g", rot=(10 * onde(t, 6), 0, 0))
    p.add("palpe_d", rot=(10 * onde(t, 6, 0.5), 0, 0))
    tate = cloche(t, 0.30, 0.05) + cloche(t, 0.42, 0.05)
    p.add("levee", rot=_angles(leve("levee", 8 * onde(t, 3) - 14 * tate)))
    charge = cloche(t, 0.70, 0.08)
    p.add("corps", pos=(0, 0.004 * charge, -0.010 * charge), rot=(-4 * charge, 0, 0))
    p.add("abdomen", rot=(-8 * charge, 0, 0))
    p.ouvert = 1 - cloche(t, 0.55, 0.02)
    return p


def avance(t):
    """Elle file au ras du sol, par quatre pattes à la fois : la première et la troisième d'un côté avec la deuxième et la
    quatrième de l'autre, puis l'inverse ; la patte levée bat la mesure, l'abdomen tressaute."""
    p = Pose()
    for n, phase in (("p1_g", 0.0), ("p3_g", 0.0), ("p2_d", 0.0), ("p4_d", 0.0), ("p2_g", 0.5), ("p4_g", 0.5), ("p3_d", 0.5)):
        phi = math.tau * (2 * t + phase)
        cote = 1 if n.endswith("g") else -1
        # en l'air pendant la première moitié de son tour, portée en avant ; posée, elle pousse vers l'arrière
        p.add(n, rot=_angles(leve(n, 18 * max(0.0, math.sin(phi)), -cote * 12 * math.cos(phi))))
    p.add("levee", rot=_angles(leve("levee", 10 * onde(t, 2))))
    p.add("corps", pos=(0, 0, -0.004 + 0.003 * onde(t, 4)), rot=(0, 2 * onde(t, 2), 0))
    p.add("abdomen", rot=(5 * onde(t, 4, 0.2), 0, 3 * onde(t, 2)))
    return p


def mange(t):
    """Elle bondit sur sa proie : elle se ramasse, se jette en avant, frappe de la patte levée, puis mâche longuement
    de ses chélicères pendant que les palpes retournent le morceau."""
    p = Pose()
    arme = cloche(t, 0.12, 0.08)
    coup = cloche(t, 0.24, 0.06)
    tenu = cloche(t, 0.60, 0.34)
    # les pattes restent plantées : seul le corps se ramasse et se jette en avant au-dessus d'elles
    p.add("corps", rot=(-4 * arme + 8 * coup + 5 * tenu, 0, 0), pos=(0, 0.006 * arme - 0.016 * coup - 0.006 * tenu, -0.006 * arme))
    p.add("levee", rot=_angles(leve("levee", -30 * coup - 16 * tenu)))
    mache = onde(t, 10) * tenu
    p.add("crochet_g", rot=(14 * mache, 0, 6 * mache))
    p.add("crochet_d", rot=(14 * mache, 0, -6 * mache))
    p.add("palpe_g", rot=(20 * tenu + 10 * onde(t, 5) * tenu, 0, 0))
    p.add("palpe_d", rot=(20 * tenu + 10 * onde(t, 5, 0.5) * tenu, 0, 0))
    p.ouvert = 1 - cloche(t, 0.90, 0.02)
    return p


def joie(t):
    """Le saut de l'araignée sauteuse : elle se tasse, bondit haut, toutes pattes écartées en étoile, tourne d'un quart
    en l'air et retombe pile en garde, la patte levée."""
    p = Pose()
    tasse = cloche(t, 0.10, 0.10, False)
    saut = math.sin(math.pi * borne((t - 0.18) / 0.52))
    vrille = borne((t - 0.18) / 0.52)
    vrille = vrille * vrille * (3 - 2 * vrille)
    p.add("corps", rot=(-6 * tasse, 0, 0), pos=(0, 0, -0.008 * tasse))           # elle se tasse sur ses pattes plantées
    suivre(p, (0, 0, 90 * math.sin(math.pi * vrille)), (0, 0, 0.14 * saut))       # puis tout part en l'air
    for n in PATTES:
        if n != "levee":
            p.add(n, rot=_angles(leve(n, 26 * saut)))
    p.add("levee", rot=_angles(leve("levee", 20 * saut)))
    p.add("abdomen", rot=(14 * saut, 0, 0))
    return p


def dort(t):
    """Elle dort tapie au sol, les pattes repliées sous elle, la patte levée enfin baissée ; l'abdomen respire lentement,
    les yeux fermés."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.018))
    p.add("abdomen", rot=(12, 0, 0), ech=(1 + 0.03 * r, 1 + 0.02 * r, 1 + 0.03 * r))
    for n in PATTES:
        if n != "levee":
            p.add(n, rot=_angles(leve(n, 14)))
    p.add("levee", rot=_angles(leve("levee", -40)))
    for o in ("palpe_g", "palpe_d", "crochet_g", "crochet_d"):        # repliés contre la bouche, à l'abri de l'herbe
        p.add(o, rot=(-22, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Araignée")
