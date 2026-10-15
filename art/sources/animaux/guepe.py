"""La guêpe en peluche, deuxième dessin : la bagarreuse du jardin, en garde. Dressée sur ses quatre longues pattes de
derrière, le thorax noir cabré, les épaulettes jaunes, elle tient ses deux pattes de devant levées comme des poings,
gantés de rouge coquelicot : la gauche en avant pour le direct, la droite qui protège le menton. Une taille étranglée
à l'extrême, un simple fil noir, et derrière, l'abdomen en fuseau bagué jaune et noir qui se recourbe sous elle,
le dard pointé vers l'avant, prêt. Le menton rentré, elle vous fixe sous des paupières noires qui tombent en biais
au-dessus d'un masque jaune, les mandibules croisées ; ses antennes pointent en avant comme deux cornes, les ailes
fumées plaquées en arrière.

    python guepe.py        fabrique la fiche art/apercus/animaux/guepe.png
    (le premier dessin, jamais gardé : guepe_ancien.py)
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

JAUNE = M.hexa("#ffd52a")                     # un jaune franc, plus acide que la moutarde de l'abeille
SOUFRE = M.hexa("#fff08a")                    # le jaune pâle des épaulettes
NOIRE = M.hexa("#24201f")                     # le noir où le poil se lit encore
FUME = M.hexa("#a8a4b6")                      # la feutrine des ailes, un verre fumé
PLOMB = M.hexa("#6c6880")                     # le fil de l'ourlet des ailes
COQUELICOT = M.hexa("#e8402c")                # l'accent : les gants et la pointe du dard
THORAX = Vector((0.0, 0.000, 0.186))
CABRE = A.repere(THORAX, (-45, 0, 0))         # le thorax cabré : l'avant monte
DEVANT = CABRE.to_3x3() @ Vector((0, -1, 0))
TETE = THORAX + DEVANT * 0.068 + Vector((0, 0, 0.004))
PORT = A.repere(TETE, (18, 6, 24))            # le menton rentré, la tête un peu tournée vers nous
# l'abdomen, de la taille au dard : il part en arrière, plonge, puis se recourbe sous elle vers l'avant
VENTRE = K.Fil([(0, 0.054, 0.142), (0, 0.110, 0.130), (0, 0.156, 0.100), (0, 0.170, 0.062), (0, 0.142, 0.040)], flanc=(1, 0, 0))
RAIES = [(0.022, NOIRE), (0.046, JAUNE), (0.060, NOIRE), (0.084, JAUNE), (0.098, NOIRE), (0.120, JAUNE), (0.132, NOIRE),
         (0.148, JAUNE), (9, NOIRE)]


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête, rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def masque(th):
    """L'ouverture du masque jaune selon l'angle : large autour des yeux, étroit au menton, et entaillé d'un V noir
    au milieu du front, qui lui fronce les sourcils."""
    u = (th - 0.5 * math.pi) % math.tau - math.pi       # 0 vers le haut, pi au menton
    return 0.98 + 0.30 * math.exp(-((abs(u) - 1.0) / 0.55) ** 2) - 0.66 * math.exp(-(u / 0.36) ** 2)


def lame(v):
    """Une aile étroite : fine à l'attache, une plaque et non une lentille."""
    s = v.copy()
    s[:, 0] *= 0.40 + 0.60 * K.lisse((v[:, 1] + 1.0) / 1.3)
    s[:, 2] = np.sign(v[:, 2]) * np.abs(v[:, 2]) ** 0.6
    return s


def construire():
    a = K.Animal("guepe")
    a.taille = 0.34
    a.tete = PORT @ Vector((0, -0.036, 0.0))

    # ----- le thorax : un œuf de velours noir cabré, deux épaulettes jaune soufre cousues au feston -----
    thorax = A.boule(1.0, 48, 24).sculpte(lambda v: K.bosse(v, (0, -0.6, 0.8), 0.10, 0.35) * [0.034, 0.046, 0.036])
    G.sillons(thorax, [12], 0.003, 1.1)
    a.piece("thorax", thorax, NOIRE, mat=CABRE)
    a.couture("echine", "thorax", 12, 0.55, 0.98, "droit", fil=JAUNE, large=0.007, haut=0.0035, pas=0.011)
    a.rustine("epaulette", "thorax", THORAX, CABRE.to_3x3() @ Vector((0.80, -0.40, 0.45)), 0.40, SOUFRE, 0.0025, 12, fil=NOIRE, paire=True)

    # ----- la taille de guêpe : un fil noir, presque rien -----
    arriere = THORAX - DEVANT * 0.040
    a.piece("taille", A.tube(A.courbe([arriere, (arriere + Vector((0, 0.060, 0.141))) * 0.5 + Vector((0, 0, 0.002)), (0, 0.060, 0.141)], 4),
                             0.0050, 12), NOIRE, poil=False)

    # ----- l'abdomen : un fuseau bagué, tourné d'une pièce, couché le long de sa courbe ; le dard au bout -----
    long = VENTRE.long
    profil = [(0.040 * math.sin(math.pi * min(1.0, 0.94 * t ** 0.70)) ** 0.85, t * long) for t in np.linspace(0, 1, 48)]
    profil[0], profil[-1] = (0.0, 0.0), (0.0, long)
    abdomen = K.bandes(A.tour(profil, 40), [(f / 0.165 * long, c) for f, c in RAIES]).sculpte(VENTRE.couche)
    a.piece("abdomen", abdomen, None)
    a.couture("dos", "abdomen", 30, 0.10, 0.80, "droit", fil=JAUNE, large=0.007, haut=0.0030, pas=0.011)
    bout, sens, _ = VENTRE.cadre(long)
    bout, sens = Vector(bout), Vector(sens)
    dard = K.tube_peint([bout - sens * 0.006, bout + sens * 0.012, bout + sens * 0.026], lambda u: 0.0062 * (1 - 0.92 * u),
                        [(0.55, NOIRE), (9, COQUELICOT)])
    a.piece("dard", dard, None, poil=False)

    # ----- la tête : un triangle noir, large au front, pointu au menton, et son masque jaune ; les yeux mauvais sous
    #       des paupières noires qui tombent en biais vers le milieu -----
    def triangle(v):
        s = v * [0.041, 0.034, 0.039]
        s[:, 0] *= 1 + 0.22 * v[:, 2]
        return s
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(triangle), NOIRE, mat=PORT)
    a.rustine("masque", "tete", TETE, vers(0, -1, -0.10), masque, JAUNE, 0.0025, 20, fil=NOIRE)
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, vers(0.50 * cote, -0.80, 0.26))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0086)
        # une paupière jaune taillée en biais, qui mange le haut de l'œil vers le milieu : l'œil mauvais
        a.piece("lourde_" + nom, K.paupiere(0.0086, 0.0), JAUNE, mat=A.cadre(p + n * 0.004, n, vers(-0.60 * cote, 0.10, 1)), poil=False)
        # les antennes : coudées, pointées en avant comme deux cornes, le bout jaune
        p, n = a.surface("tete", TETE, vers(0.26 * cote, -0.55, 0.80))
        fil = A.conges([p - n * 0.003, p + vers(0.012 * cote, 0.000, 0.030), p + vers(0.030 * cote, -0.040, 0.044),
                        p + vers(0.044 * cote, -0.084, 0.040)], 0.010, 5)
        a.piece("antenne_" + nom, K.tube_peint(fil, lambda u: 0.0036 - 0.0008 * u, [(0.78, NOIRE), (9, JAUNE)]), None, poil=False)
    # les mandibules : deux crochets jaunes qui se croisent sous le masque
    pinces = None
    for cote in (1, -1):
        p, n = a.surface("tete", TETE, vers(0.30 * cote, -0.70, -0.62))
        crochet = A.courbe([p - n * 0.002, p + n * 0.008 + vers(0.002 * cote, -0.006, -0.004), p + n * 0.010 + vers(-0.010 * cote, -0.010, -0.006)], 4)
        une = K.tube_peint(crochet, lambda u: 0.0040 * (1 - 0.55 * u), [(0.65, JAUNE), (9, NOIRE)])
        pinces = une if pinces is None else pinces + une
    a.piece("mandibules", pinces, None, poil=False)

    # ----- les ailes : deux lames fumées plaquées en arrière, au-dessus de l'abdomen -----
    for nom, cote in (("G", 1), ("D", -1)):
        attache = THORAX + CABRE.to_3x3() @ Vector((0.016 * cote, 0.010, 0.030))
        elan = Vector((0.18 * cote, 0.94, 0.16)).normalized()
        aile = A.boule(1.0, 40, 20).sculpte(lame).etire(0.017, 0.074, 0.0032)
        a.piece("aile_" + nom, aile, FUME, mat=A.cadre(attache + elan * 0.068, (0.30 * cote, -0.10, 0.95), elan), poil=False)
        a.ourlet("ourlet_" + nom, "aile_" + nom, 0.75, fil=PLOMB, haut=0.0010, pas=0.009)

    # ----- les quatre pattes de marche, longues et coudées, la cuisse noire, le reste jaune : elle se tient haut, les
    #       pieds bien écartés -----
    for nom, cote in (("G", 1), ("D", -1)):
        pattes = None
        for hanche, genou, pied in (((0.018, -0.004, 0.156), (0.072, -0.022, 0.188), (0.102, -0.064, 0.006)),
                                    ((0.016, 0.020, 0.150), (0.076, 0.050, 0.180), (0.114, 0.104, 0.006))):
            h, g, f = (Vector((cote * q[0], q[1], q[2])) for q in (hanche, genou, pied))
            chemin = A.conges([h, g, f, f + Vector((cote * 0.012, -0.010, 0.0))], 0.010, 5)
            une = K.tube_peint(chemin, lambda u: 0.0058 - 0.0020 * u, [(0.30, NOIRE), (9, JAUNE)])
            pattes = une if pattes is None else pattes + une
        a.piece("pattes_" + nom, pattes, None, poil=False)

    # ----- les poings : les pattes de devant levées en garde, gantées de coquelicot ; la gauche en avant, la droite
    #       qui protège le menton -----
    for nom, cote, coude, poing in (("G", 1, (0.056, -0.064, 0.150), (0.052, -0.124, 0.176)),
                                    ("D", -1, (0.046, -0.040, 0.156), (0.014, -0.086, 0.170))):
        epaule = THORAX + CABRE.to_3x3() @ Vector((0.020 * cote, -0.032, -0.016))
        chemin = A.conges([epaule, Vector((cote * coude[0], coude[1], coude[2])), Vector((cote * poing[0], poing[1], poing[2]))], 0.012, 5)
        bras = K.tube_peint(chemin, lambda u: 0.0052 - 0.0008 * u, [(0.38, NOIRE), (9, JAUNE)])
        sens = Vector(chemin[-1]) - Vector(chemin[-4])
        gant = A.boule(1.0, 28, 14).etire(0.0115, 0.0105, 0.0135).pose(tuple(Vector(chemin[-1]) + sens.normalized() * 0.004), A.viser(sens))
        a.piece("poing_" + nom, bras + gant.peint(COQUELICOT), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py guepe). Les mesures sont celles du modèle, avant a.taille.
# Les ailes, les bras et les pattes sont attachés en miroir (un os « _G », recopié en « _D ») ; la tête est tournée de
# 24° : ses antennes ont chacune leur os (antenne_g, antenne_d). L'abdomen est une pièce souple que deux os se passent
# le long de sa courbe. Les pattes pendent à la racine : posées, elles restent au sol quand le corps boxe au-dessus.

from poses import Pose, borne, cloche, onde

_MI = 0.5 * VENTRE.long                                   # le milieu de l'abdomen, le long de sa courbe

OS = [("racine", None, (0, 0, 0)),
      ("corps", "racine", (0.0, 0.0, 0.186)),             # le cœur du thorax cabré
      ("tete", "corps", (0.0, -0.0283, 0.2143)),          # la nuque, devant le thorax
      ("antenne_g", "tete", (0.0211, -0.0674, 0.2578)),   # la racine de chaque antenne
      ("antenne_d", "tete", (0.0042, -0.0749, 0.2597)),
      ("abdomen", "corps", (0.0, 0.054, 0.142)),          # au bout de la taille de guêpe
      ("abdomen2", "abdomen", tuple(round(float(x), 4) for x in VENTRE.cadre(_MI)[0])),     # là où il se recourbe
      ("poing_G", "corps", (0.020, -0.0339, 0.1973)),     # l'épaule de chaque bras levé en garde
      ("aile_G", "corps", (0.016, 0.0283, 0.2001)),       # l'attache de chaque aile
      ("pattes_G", "racine", (0.017, 0.008, 0.153))]      # les hanches des quatre pattes de marche


def _abscisse(points, chemin):
    """Pour chaque point : sa place le long d'un chemin (en mètres), au pied de la perpendiculaire sur le tronçon le plus proche."""
    c = np.asarray(chemin, float)
    a, ab = c[:-1], np.diff(c, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    ap = points[:, None, :] - a[None, :, :]
    u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
    j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
    fait = np.concatenate([[0.0], np.cumsum(np.sqrt(l2))])
    return fait[j] + u[np.arange(len(points)), j] * np.sqrt(l2[j])


def souple(points, cote):
    """L'abdomen : la première moitié sur « abdomen », la courbe et le dard sur « abdomen2 », fondus sur deux centimètres."""
    w = K.lisse((_abscisse(points, VENTRE.p) - _MI + 0.010) / 0.020)
    return {"abdomen": 1 - w, "abdomen2": w}


def _antenne(points, cote):
    return {"antenne" + cote.lower(): np.ones(len(points))}


PORTEURS = [("thorax", "corps"), ("echine", "corps"), ("epaulette", "corps"), ("taille", "corps"),
            ("abdomen", souple, "abdomen"), ("dos", souple, "abdomen"), ("dard", "abdomen2"),
            ("tete", "tete"), ("masque", "tete"), ("oeil", "tete"), ("lourde", "tete"), ("mandibules", "tete"),
            ("antenne", _antenne), ("poing", "poing", True), ("aile", "aile", True), ("ourlet", "aile", True),
            ("pattes", "pattes", True),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def envol(p, haut, pend=1.0):
    """Le corps monte de « haut », les pattes le suivent, pendues sous lui (pend de 0, posées, à 1, ballantes)."""
    p.add("corps", pos=(0, 0, haut))
    p.paire("pattes", rot=(-24 * pend, -16 * pend, 0), pos=(0, 0, haut))


def ailes(p, bat):
    """Les ailes, plaquées en arrière au repos (bat = 0), s'ouvrent sur les côtés et se lèvent (bat en degrés) : rz < 0
    écarte l'aile gauche vers le dehors, rx > 0 lève ce qui est derrière l'attache."""
    p.paire("aile", rot=(0.4 * bat, 0, -bat))


def repos(t):
    """En garde, elle sautille sur place comme une boxeuse : le corps qui danse, les poings qui roulent devant le menton ;
    deux fois elle envoie un direct du gauche (le corps suit), et le dard pique l'air en même temps ; les antennes
    tâtent, elle cligne d'un œil mauvais."""
    p = Pose()
    danse = onde(t, 4)
    p.add("corps", pos=(0, 0, 0.003 * danse), rot=(0, 0, 3 * onde(t, 2)))
    p.add("poing_G", rot=(6 * onde(t, 4, 0.25), 0, 0))
    p.add("poing_D", rot=(6 * onde(t, 4, 0.75), 0, 0))
    for c in (0.30, 0.38):
        direct = cloche(t, c, 0.03)
        p.add("poing_G", rot=(-30 * direct, 0, 10 * direct))
        p.add("corps", rot=(-4 * direct, 0, -8 * direct))
        p.add("abdomen2", rot=(-16 * direct, 0, 0))
    p.add("abdomen", rot=(3 * onde(t, 2), 0, 0))
    p.add("antenne_g", rot=(8 * onde(t, 3), 0, 5 * onde(t, 2)))
    p.add("antenne_d", rot=(-8 * onde(t, 3, 0.3), 0, 5 * onde(t, 2, 0.4)))
    p.add("tete", rot=(0, 0, 8 * cloche(t, 0.70, 0.10)))
    p.ouvert = borne(1 - cloche(t, 0.12, 0.02) - cloche(t, 0.60, 0.02))
    return p


def avance(t):
    """Elle vole à l'attaque : le corps monte haut, piqué en avant, les ailes vrombissent (douze battements par
    boucle), les pattes pendent derrière, les poings toujours levés ; l'abdomen pompe, le dard en avant."""
    p = Pose()
    envol(p, 0.18 + 0.012 * onde(t, 2) + 0.008 * onde(t, 1, 0.3))
    p.add("corps", rot=(10 + 2 * onde(t, 2), 0, 3 * onde(t, 1)))
    ailes(p, 40 + 30 * onde(t, 12))
    p.add("abdomen", rot=(6 * onde(t, 2, 0.2), 0, 0))
    p.add("abdomen2", rot=(-6 * onde(t, 2, 0.4), 0, 0))
    p.add("antenne_g", rot=(-8, 0, 0))
    p.add("antenne_d", rot=(-8, 0, 0))
    return p


def mange(t):
    """Elle se penche, baisse sa garde, et mâchonne ce qu'elle a trouvé à grands coups de mandibules (toute la tête
    qui travaille), un œil sur nous ; puis elle se redresse et remonte les poings."""
    p = Pose()
    bas = cloche(t, 0.42, 0.34)
    mache = max(0.0, onde(t, 10)) * cloche(t, 0.42, 0.28)
    p.add("corps", rot=(18 * bas, 0, 0), pos=(0, 0, -0.008 * bas))
    p.add("tete", rot=(20 * bas + 8 * mache, 0, 6 * mache * onde(t, 5)))
    p.paire("poing", rot=(26 * bas, 0, 0))
    p.add("antenne_g", rot=(14 * bas, 0, 0))
    p.add("antenne_d", rot=(14 * bas, 0, 0))
    p.add("abdomen2", rot=(6 * bas, 0, 0))
    p.ouvert = borne(1 - 0.4 * bas - cloche(t, 0.88, 0.02))
    return p


def joie(t):
    """La victoire : elle bondit, les deux poings levés au ciel, tourne sur elle-même en vrombissant comme une
    championne qui salue la foule, et retombe en garde."""
    p = repos(0.0)
    air = math.sin(math.pi * borne(t / 0.80))
    tour_ = borne((t - 0.10) / 0.60)
    tour_ = tour_ * tour_ * (3 - 2 * tour_)
    envol(p, 0.10 * air, air)
    p.add("corps", rot=(0, 0, 360 * tour_))
    p.paire("poing", rot=(-70 * air, 0, -14 * air))
    ailes(p, (40 + 30 * onde(t, 12)) * air)
    p.add("abdomen2", rot=(-12 * air, 0, 0))
    p.add("tete", rot=(-14 * air, 0, 0))
    return p


def dort(t):
    """Elle s'est endormie debout, la garde enfin baissée : les poings retombés, la tête qui pique du nez, les
    antennes couchées, l'abdomen qui pend ; les yeux fermés, elle respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", rot=(10, 0, 0), pos=(0, 0, -0.006))
    p.paire("poing", rot=(34, 0, 0))
    p.add("tete", rot=(22 + 2 * r, 0, 0))
    p.add("antenne_g", rot=(26, 0, 0))
    p.add("antenne_d", rot=(30, 0, 0))
    p.add("abdomen", rot=(4 + 2 * r, 0, 0), ech=(1 + 0.04 * r, 1, 1 + 0.04 * r))
    p.add("abdomen2", rot=(8, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Guêpe")
