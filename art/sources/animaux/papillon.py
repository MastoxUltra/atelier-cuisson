"""Le papillon en peluche, deuxième dessin : le dandy du jardin, qui fait sécher ses ailes au soleil. Haut perché sur
quatre pattes fines comme des échasses, le poitrail engoncé dans un col de fourrure abricot, il tient grandes ouvertes
ses ailes de feutrine orange, bordées d'un large ourlet marine semé de perles crème, nervurées de marine, la base
roussie ; celles de derrière finissent en queue-de-pie, chacune marquée d'une lunule bleu ciel : son seul éclat. Le
menton levé, la tête tournée vers nous par-dessus l'épaule, l'œil mi-clos sous une paupière lourde, la trompe roulée
sous le nez comme une moustache, une antenne plus haute que l'autre : il pose, et il sait qu'on le regarde.

    python papillon.py        fabrique la fiche art/apercus/animaux/papillon.png
    (le premier dessin, jamais gardé : papillon_ancien.py)
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

ORANGE = M.hexa("#ff8a2a")                    # la dominante : le panneau des ailes, la tête
ROUILLE = M.hexa("#c9541e")                   # la base roussie des ailes, le fil des coutures
ABRICOT = M.hexa("#ffd3a0")                   # le col de fourrure
MARINE = M.hexa("#25305f")                    # la bordure, les nervures, le corps, les pattes
CIEL = M.hexa("#8fd0f2")                      # l'accent : la lunule des queues-de-pie
TOURNE = 0                                   # -100 sur la fiche : il nous tourne le dos pour offrir ses ailes ; 0 pour le jeu
POSE = A.repere((0, 0, 0.065), (-30, 0, 0))   # le corps se cabre, le poitrail en avant : le dessus des ailes s'offre au soleil, derrière lui
THORAX = POSE @ Vector((0.0, -0.016, 0.084))
TETE = POSE @ Vector((0.0, -0.058, 0.104))
PORT = POSE @ A.repere((0.0, -0.058, 0.104), (6, -14, 104))   # le menton levé, la tête tournée vers nous par-dessus l'épaule gauche

# les ailes de gauche, à plat : (vers le dehors, vers l'arrière), depuis l'attache
AVANT = [(0.0, -0.010), (0.050, -0.042), (0.110, -0.080), (0.168, -0.106), (0.212, -0.116), (0.216, -0.088),
         (0.202, -0.046), (0.176, -0.004), (0.132, 0.034), (0.074, 0.050), (0.026, 0.034), (0.0, 0.012)]
ARRIERE = [(0.0, 0.0), (0.050, 0.002), (0.100, 0.014), (0.140, 0.044), (0.152, 0.082), (0.136, 0.116), (0.108, 0.132),
           (0.098, 0.150), (0.104, 0.196), (0.094, 0.214), (0.080, 0.200), (0.074, 0.156), (0.060, 0.136),
           (0.034, 0.118), (0.012, 0.078), (0.0, 0.030)]
# les panneaux orange cousus dessus : la marine dépasse tout autour et fait l'ourlet
PANNEAU_AVANT = [(0.012, -0.004), (0.056, -0.032), (0.110, -0.064), (0.160, -0.086), (0.190, -0.092), (0.190, -0.066),
                 (0.178, -0.034), (0.156, 0.000), (0.120, 0.026), (0.070, 0.036), (0.024, 0.022)]
PANNEAU_ARRIERE = [(0.010, 0.008), (0.052, 0.012), (0.094, 0.024), (0.122, 0.048), (0.130, 0.078), (0.116, 0.104),
                   (0.088, 0.116), (0.050, 0.106), (0.024, 0.080), (0.010, 0.040)]
PERLES_AVANT = [(0.200, -0.104), (0.205, -0.078), (0.196, -0.046), (0.178, -0.016), (0.154, 0.014), (0.120, 0.038)]
PERLES_ARRIERE = [(0.146, 0.072), (0.138, 0.102), (0.116, 0.124), (0.060, 0.124), (0.036, 0.106)]
NERVURES_AVANT = [[(0.020, 0.0), (0.090, -0.040), (0.170, -0.080)], [(0.024, 0.006), (0.100, -0.016), (0.160, -0.036)],
                  [(0.024, 0.012), (0.080, 0.020), (0.140, 0.010)]]
NERVURES_ARRIERE = [[(0.018, 0.012), (0.070, 0.030), (0.112, 0.060)], [(0.016, 0.020), (0.050, 0.060), (0.072, 0.096)]]


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête, rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def etoffe(contour, epaisseur, roussi=0.0):
    """Une étoffe d'aile découpée ; roussi > 0 : la base roussie jusqu'à cette distance de l'attache."""
    m = A.decoupe(A.courbe(contour, 5, fermee=True), epaisseur, 0.0015)
    if roussi:
        loin = np.hypot(m.v[:, 0], m.v[:, 1]) > roussi
        m.teinte = np.where(loin[:, None], np.asarray(ORANGE), np.asarray(ROUILLE))
    return m


def perles(points, r, z):
    """Des ronds de feutrine posés à plat sur l'étoffe, à la hauteur z."""
    tous = [A.decoupe(A.cercle(r, 24), 0.0020, 0.0008).pose((u, w, z)) for u, w in points]
    return sum(tous[1:], tous[0])


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def construire():
    a = K.Animal("papillon")
    a.taille = 0.42
    a.tete = PORT @ Vector((0, -0.030, 0.0))

    # ----- les ailes : grandes ouvertes au soleil, celles de devant relevées en V léger, celles de derrière plus à plat
    #       et glissées dessous ; la marine fait le fond et l'ourlet, le panneau orange roussi à la base est cousu dessus -----
    for nom, contour, panneau, semis, nervures, attache, monte, base in (
            ("avant", AVANT, PANNEAU_AVANT, PERLES_AVANT, NERVURES_AVANT, (0.010, -0.026, 0.094), 8, 0.050),
            ("arriere", ARRIERE, PANNEAU_ARRIERE, PERLES_ARRIERE, NERVURES_ARRIERE, (0.010, -0.004, 0.086), 0, 0.040)):
        t = math.radians(monte)
        rep = POSE @ A.cadre(attache, (-math.sin(t), 0.0, math.cos(t)), (0, 1, 0))
        a.piece("aile_" + nom, etoffe(contour, 0.0050), MARINE, mat=rep, poil=False, paire=True)
        a.piece("panneau_" + nom, etoffe(panneau, 0.0030, base), None, mat=rep @ A.repere((0, 0, 0.0036)), poil=False, paire=True)
        a.piece("perles_" + nom, perles(semis, 0.0060, 0.0030), K.CREME, mat=rep, poil=False, paire=True)
        # le revers des ailes, lui aussi orange (un vrai papillon se lit de dessous) : de face, en jeu, la caméra voit le
        # dessous des ailes ; sans lui, elles sortent marine et le papillon passe pour un moustique (Artiste, 15/10)
        a.piece("panneau_" + nom + "_revers", etoffe(panneau, 0.0030, base), None, mat=rep @ A.repere((0, 0, -0.0036)), poil=False, paire=True)
        a.piece("perles_" + nom + "_revers", perles(semis, 0.0060, -0.0030), K.CREME, mat=rep, poil=False, paire=True)
        for k, ligne in enumerate(nervures):
            a.broderie("nervure%d_%s" % (k, nom), [rep @ Vector((u, w, 0.0056)) for u, w in A.courbe(ligne, 4)], 0.0017, MARINE, paire=True)
        if nom == "arriere":
            # la lunule bleu ciel au pied de la queue-de-pie
            a.piece("lunule", perles([(0.088, 0.172)], 0.0085, 0.0032), CIEL, mat=rep, poil=False, paire=True)

    # ----- le corps : un abdomen fin de velours marine couché entre les ailes de derrière, et le thorax pris dans son col
    #       de fourrure abricot -----
    ventre = A.tour(A.profil([(0, 0), (0.008, 0.006), (0.014, 0.030), (0.017, 0.070), (0.015, 0.100), (0.011, 0.118), (0, 0.126)], 6), 40)
    a.piece("abdomen", ventre, MARINE, mat=POSE @ A.cadre((0.0, 0.119, 0.050), (0, -1, 0.26), (0, 0, 1)))
    a.couture("dos", "abdomen", 10, 0.18, 0.82, "droit", fil=ROUILLE, large=0.006, haut=0.0025, pas=0.010)

    def col(v):
        v = K.bosse(v, (0, -0.8, 0.5), 0.18, 0.35)            # le poitrail bombé
        return v * [0.026, 0.032, 0.026]
    a.piece("col", A.boule(1.0, 48, 24).sculpte(col), ABRICOT, mat=POSE @ A.repere((0.0, -0.016, 0.084)))
    a.poil_long = 0.0045

    # ----- la tête : une petite boule orange, le menton levé ; l'œil mi-clos sous une paupière marine, un sourire en coin -----
    a.piece("tete", A.boule(1.0, 48, 24).etire(0.027, 0.025, 0.025), ORANGE, mat=PORT)
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, vers(0.62 * cote, -0.64, 0.30))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0078)
        a.piece("lourde_" + nom, K.paupiere(0.0078, 0.04), MARINE, mat=A.cadre(p + n * 0.003, n, vers(0, 0.10, 1)), poil=False)
    sourire = a.trace("tete", TETE, [vers(x, -0.95, z) for x, z in ((0.34, -0.10), (0.18, -0.24), (0.00, -0.28), (-0.12, -0.26))], 0.003)
    a.broderie("sourire", A.courbe(sourire, 4), 0.0016, MARINE)

    # ----- les antennes en massue : longues, en arc vers l'arrière, la gauche plus haute (un sourcil levé) -----
    for nom, cote, leve in (("G", 1, 1.25), ("D", -1, 0.90)):
        p, n = a.surface("tete", TETE, vers(0.30 * cote, -0.30, 0.90))
        fil = A.courbe([p - n * 0.003, p + vers(0.012 * cote, -0.010, 0.030 * leve), p + vers(0.030 * cote, -0.004, 0.062 * leve),
                        p + vers(0.052 * cote, 0.016, 0.080 * leve)], 6)
        a.piece("antenne_" + nom, K.tube_peint(fil, lambda u: 0.0024 + 0.0034 * float(K.lisse((u - 0.80) / 0.20)),
                                               [(0.80, MARINE), (9, ORANGE)]), None, poil=False)

    # ----- la trompe : roulée sous le nez comme une moustache cirée -----
    bouche = PORT @ Vector((0, -0.020, -0.012))
    spire = [bouche + vers(0, -math.sin(t) * 0.012 * (1 - 0.13 * t), -0.012 + math.cos(t) * 0.012 * (1 - 0.13 * t)) for t in np.linspace(0.3, 2.0 * math.tau, 40)]
    a.piece("trompe", A.tube(spire, lambda u: 0.0026 - 0.0010 * u, 12), MARINE, poil=False)

    # ----- les pattes : quatre longues échasses marine, la chaussette rouille ; la paire de devant, atrophiée, repliée
    #       sous le col -----
    for nom, cote in (("G", 1), ("D", -1)):
        pattes = None
        for hanche, genou, pied in (((0.010, -0.010, 0.068), (0.042, -0.040, 0.100), (0.050, -0.070, 0.006)),
                                    ((0.010, 0.004, 0.068), (0.046, 0.016, 0.098), (0.062, 0.044, 0.006))):
            h, g = POSE @ Vector((cote * hanche[0], hanche[1], hanche[2])), POSE @ Vector((cote * genou[0], genou[1], genou[2]))
            chemin = A.conges([h, g, (cote * pied[0], pied[1], pied[2])], 0.010, 5)
            une = K.tube_peint(chemin, lambda u: 0.0034 - 0.0010 * u, [(0.82, MARINE), (9, ROUILLE)])
            pattes = une if pattes is None else pattes + une
        bras = A.courbe([POSE @ Vector(q) for q in ((cote * 0.010, -0.030, 0.070), (cote * 0.018, -0.044, 0.064), (cote * 0.012, -0.048, 0.072))], 4)
        pattes = pattes + K.tube_peint(bras, 0.0030, [(9, MARINE)])
        a.piece("pattes_" + nom, pattes, None, poil=False)
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py papillon). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Les ailes et les pattes sont posées en miroir (un os « _G », recopié en « _D ») ; la tête, tournée de 104° vers sa
# gauche, ne l'est pas : ses antennes ont chacune leur os (antenne_g, antenne_d). Les pattes pendent à la racine : posées,
# elles restent au sol quand le corps se penche ; en vol, elles suivent le corps.

from poses import Pose, borne, cloche, onde

AXE = np.array(POSE.to_3x3() @ Vector((0, 1, 0)))      # l'axe du corps cabré, vers l'arrière : les ailes battent autour

OS = [("racine", None, (0, 0, 0)),
      ("corps", "racine", (0.0, 0.0281, 0.1457)),            # le thorax, dans son col
      ("tete", "corps", (0.0, 0.0120, 0.1680)),              # la nuque, entre le col et la tête
      ("antenne_g", "tete", (0.0079, 0.0153, 0.1997)),       # la racine de chaque antenne
      ("antenne_d", "tete", (0.0111, 0.0027, 0.2032)),
      ("trompe", "tete", (0.0173, 0.0017, 0.1684)),          # la bouche, d'où part la trompe roulée
      ("abdomen", "corps", (0.0, 0.0400, 0.1300)),           # l'attache de l'abdomen, sous le col
      ("aile_avant_G", "corps", (0.010, 0.0245, 0.1594)),    # l'attache de chaque aile (celles de droite sont leur miroir)
      ("aile_arriere_G", "corps", (0.010, 0.0395, 0.1415)),
      ("pattes_G", "racine", (0.010, 0.0300, 0.1250))]       # les hanches, sous le col


def _antenne(points, cote):
    return {"antenne" + cote.lower(): np.ones(len(points))}


PORTEURS = [("col", "corps"), ("abdomen", "abdomen"), ("dos", "abdomen"),
            ("tete", "tete"), ("oeil", "tete"), ("lourde", "tete"), ("sourire", "tete"), ("trompe", "trompe"),
            ("antenne", _antenne),
            ("aile_avant", "aile_avant", True), ("panneau_avant", "aile_avant", True), ("perles_avant", "aile_avant", True),
            ("nervure0_avant", "aile_avant", True), ("nervure1_avant", "aile_avant", True), ("nervure2_avant", "aile_avant", True),
            ("aile_arriere", "aile_arriere", True), ("panneau_arriere", "aile_arriere", True), ("perles_arriere", "aile_arriere", True),
            ("nervure0_arriere", "aile_arriere", True), ("nervure1_arriere", "aile_arriere", True), ("lunule", "aile_arriere", True),
            ("pattes", "pattes", True),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


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


def ailes(p, avant, arriere=None):
    """Lève les ailes (en degrés, autour de l'axe du corps) : 0 grandes ouvertes au soleil, 80 refermées dressées
    au-dessus du dos ; un peu moins pour celles de derrière, qui suivent."""
    arriere = avant * 0.85 if arriere is None else arriere
    p.paire("aile_avant", rot=_angles(_tour(AXE, -avant)))
    p.paire("aile_arriere", rot=_angles(_tour(AXE, -arriere)))


def envol(p, haut, pend=1.0):
    """Le corps monte de « haut » et les pattes le suivent, pendues sous lui (pend de 0, posées, à 1, ballantes)."""
    p.add("corps", pos=(0, 0, haut))
    p.paire("pattes", rot=(-20 * pend, -14 * pend, 0), pos=(0, 0, haut))


def repos(t):
    """Il pose au soleil : il ferme lentement ses ailes et les rouvre (deux fois, pour qu'on admire le dessus et le
    dessous), l'abdomen qui respire ; il lève son antenne gauche comme un sourcil, d'un air entendu, et tourne la tête
    vers nous un peu plus ; il cligne, paresseusement."""
    p = Pose()
    r = onde(t, 2)
    ailes(p, 34 * (0.5 - 0.5 * math.cos(math.tau * 2 * t)))
    p.add("abdomen", rot=(3 * r, 0, 0), ech=(1 + 0.04 * r, 1, 1 + 0.04 * r))
    sourcil = cloche(t, 0.62, 0.08)
    p.add("antenne_g", rot=(-14 * sourcil + 3 * onde(t, 3), 0, 0))
    p.add("antenne_d", rot=(3 * onde(t, 3, 0.3), 0, 0))
    p.add("tete", rot=(-4 * sourcil, 0, 10 * cloche(t, 0.62, 0.12)))
    p.ouvert = 1 - cloche(t, 0.30, 0.04) - cloche(t, 0.88, 0.04)
    return p


def avance(t):
    """Il vole, en dansant : le corps monte haut et sautille en l'air à chaque coup d'aile, les ailes battent à
    grands coups (six par boucle), les pattes ballantes, l'abdomen qui suit le mouvement, les antennes au vent."""
    p = Pose()
    bat = 0.5 - 0.5 * math.cos(math.tau * 6 * t)              # 0 ouvertes à plat, 1 levées
    envol(p, 0.20 + 0.020 * onde(t, 6, 0.25) + 0.010 * onde(t, 1))
    p.add("corps", rot=(-6 + 3 * onde(t, 1), 0, 4 * onde(t, 1, 0.25)))
    ailes(p, -20 + 80 * bat)
    p.add("abdomen", rot=(8 * onde(t, 6, 0.1), 0, 0))
    p.add("antenne_g", rot=(-8, 0, 0))
    p.add("antenne_d", rot=(-8, 0, 0))
    return p


def mange(t):
    """Il butine : il se penche sur la fleur à ses pieds, plonge sa trompe, boit à petites gorgées, les ailes qui
    s'ouvrent et se ferment doucement d'aise ; puis il se redresse et se lisse, content de lui."""
    p = Pose()
    bas = cloche(t, 0.45, 0.34)
    gorgee = max(0.0, onde(t, 6)) ** 2 * cloche(t, 0.45, 0.28)
    p.add("corps", rot=(14 * bas, 0, 0))
    p.add("tete", rot=(18 * bas, 0, -10 * bas))
    p.add("trompe", rot=(30 * bas + 6 * gorgee, 0, 0))
    p.add("abdomen", rot=(-10 * bas, 0, 0), ech=(1 + 0.05 * gorgee, 1, 1 + 0.05 * gorgee))
    ailes(p, 30 * (0.5 - 0.5 * math.cos(math.tau * 3 * t)))
    p.add("antenne_g", rot=(10 * bas, 0, 0))
    p.add("antenne_d", rot=(10 * bas, 0, 0))
    p.ouvert = borne(1 - 0.5 * bas - cloche(t, 0.90, 0.02))
    return p


def joie(t):
    """Il s'envole en spirale, fait un grand tour en l'air en battant des ailes, et se repose exactement où il était,
    les ailes grandes ouvertes : la pose."""
    p = Pose()
    air = math.sin(math.pi * borne(t / 0.82))
    tour_ = borne((t - 0.06) / 0.72)
    tour_ = tour_ * tour_ * (3 - 2 * tour_)
    envol(p, 0.22 * air, air)
    p.add("corps", rot=(-8 * air, 10 * air, 360 * tour_))
    bat = 0.5 - 0.5 * math.cos(math.tau * 6 * borne(t / 0.82))
    ailes(p, (-20 + 80 * bat) * air)
    p.add("antenne_g", rot=(-12 * air, 0, 0))
    p.add("antenne_d", rot=(-12 * air, 0, 0))
    return p


def dort(t):
    """Il dort perché sur ses échasses, les ailes refermées et dressées au-dessus du dos comme une voile, la tête
    rentrée dans son col, les antennes couchées en arrière ; les yeux fermés, l'abdomen respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    ailes(p, 78, 74)
    p.add("tete", rot=(14, 0, -20))
    p.add("antenne_g", rot=(-20, 0, 0))
    p.add("antenne_d", rot=(-24, 0, 0))
    p.add("abdomen", rot=(2 * r, 0, 0), ech=(1 + 0.04 * r, 1, 1 + 0.04 * r))
    p.add("corps", pos=(0, 0, -0.004))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Papillon")
