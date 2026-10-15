"""La mante en peluche : une mante orchidée, ivoire et rose orchidée. Un long cou dressé, une tête en triangle tournée
vers nous, deux lourdes paupières roses à demi baissées, les pattes ravisseuses jointes « en prière » sous le menton,
des lobes en pétale sur les pattes, l'abdomen qui remonte comme une fleur. Élégante et glaciale : elle a tout son temps.

    python mante.py        fabrique la fiche art/apercus/animaux/mante.png
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

IVOIRE = M.hexa("#fff5e0")                    # le poil et la feutrine du corps
PALE = M.hexa("#f6bfe6")                      # le rose qui commence : entre l'ivoire et l'orchidée
ORCHIDEE = M.hexa("#dc6cc8")                  # le bord des ailes, le bout des pattes, les pétales, les paupières
POIL_PALE, POIL_ORCHIDEE = M.hexa("#fcd6f0"), M.hexa("#f0a3e2")    # les mêmes en poil, qui fonce et sature les teintes
GRIFFE = M.hexa("#8e2b7c")                    # l'accent : les crochets des pattes ravisseuses, la moue
TAILLE = Vector((0.0, 0.010, 0.112))          # là où l'abdomen sort du thorax
LONG, ARC = 0.176, 0.24                       # la longueur de l'abdomen, et le rayon de l'arc qui le relève
TETE = Vector((0.0, -0.132, 0.332))
PORT = A.repere(TETE, (-6, -7, 38))           # la tête : le menton levé, penchée, tournée vers nous par-dessus l'épaule


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête, rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def tube_peint(chemin, rayon, paliers, cotes=12):
    """Un tube peint par tronçons le long de son fil : paliers = [(fraction du chemin, couleur), ...], la dernière
    fraction à 1 ou plus. Le chemin est recoupé tous les 4 mm pour que la limite des couleurs reste nette."""
    ch = np.asarray(chemin, float)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(ch, axis=0), axis=1))])
    t = np.linspace(0.0, 1.0, max(6, int(fait[-1] / 0.004)))
    ch = np.stack([np.interp(t * fait[-1], fait, ch[:, k]) for k in range(3)], axis=1)
    m = A.tube(ch, rayon, cotes)
    t = np.concatenate([np.repeat(t, cotes), [0.0, 1.0]])           # les anneaux du tube, puis ses deux bouchons
    m.teinte = np.zeros((len(t), 3))
    for seuil, couleur in reversed(paliers):
        m.teinte[t <= seuil] = couleur
    return m


def cambre(v):
    """Relève l'abdomen le long d'un arc (vers le -Y de la pièce, son dos) : couché à la taille, la pointe en l'air."""
    angle = v[:, 2] / ARC
    s = v.copy()
    s[:, 1] = (ARC + v[:, 1]) * np.cos(angle) - ARC
    s[:, 2] = (ARC + v[:, 1]) * np.sin(angle)
    return s


def petale(hanche, genou):
    """Le lobe en pétale d'une patte : une languette de feutrine qui pend sous la cuisse, ivoire en haut, rose au bord.
    Rend la pièce et son repère (son X file le long de la cuisse, son Y pend vers le sol)."""
    cuisse = (Vector(genou) - Vector(hanche)).normalized()
    pend = (Vector((0, 0, -1)) + cuisse * cuisse.z).normalized()
    contour = A.courbe([(0.0, -0.004), (0.026, -0.007), (0.052, -0.004), (0.065, 0.014), (0.059, 0.040), (0.038, 0.058),
                        (0.015, 0.044), (0.001, 0.018)], 5, fermee=True)
    lobe = K.bandes(A.decoupe(contour, 0.005, 0.002), [(0.016, IVOIRE), (0.031, PALE), (9, ORCHIDEE)], axe=1)
    return lobe, A.cadre(Vector(hanche) + (Vector(genou) - Vector(hanche)) * 0.46, cuisse.cross(pend), pend)


def construire():
    a = K.Animal("mante")
    a.taille = 0.42
    a.tete = PORT @ Vector((0, -0.030, 0.0))

    # ----- l'abdomen : une goutte tournée d'une pièce, qui rosit vers la pointe, puis relevée en arc comme un bouton de fleur -----
    profil = A.profil([(0, 0), (0.022, 0.006), (0.034, 0.040), (0.042, 0.085), (0.038, 0.125), (0.024, 0.158), (0, LONG)], 6)
    abdomen = K.bandes(A.tour(profil, 40), [(0.085, IVOIRE), (0.125, POIL_PALE), (9, POIL_ORCHIDEE)])
    a.piece("abdomen", abdomen.sculpte(cambre), None, pos=TAILLE, rot=(-92, 0, 0))

    # ----- le thorax, puis le cou : un long tube dressé qui s'épaissit aux épaules -----
    a.piece("thorax", A.boule(1.0, 48, 24).etire(0.034, 0.040, 0.034), IVOIRE, pos=(0, -0.006, 0.116))
    cou = A.courbe([(0, -0.012, 0.122), (0, -0.046, 0.180), (0, -0.084, 0.246), (0, -0.110, 0.306)], 8)
    a.piece("cou", A.tube(cou, lambda t: 0.019 - 0.007 * t + 0.0055 * math.exp(-((t - 0.70) / 0.12) ** 2), 20), IVOIRE)

    # ----- la tête : un triangle plat, large du haut, dont le menton pointu avance ; le cou s'y plante par-derrière -----
    def triangle(v):
        haut = K.lisse((v[:, 2] + 1.0) / 1.45)
        s = v * [0.064, 0.027, 0.046]
        s[:, 0] *= 0.16 + 0.84 * haut
        s[:, 1] -= 0.012 * (1 - haut)
        return s
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(triangle), IVOIRE, mat=PORT)

    # ----- les yeux : deux globes aux coins du triangle, un bouton sur chacun qui nous regarde, et par-dessus une lourde
    #       paupière de feutrine rose, à demi baissée : le regard de quelqu'un qui n'est pas pressé -----
    for nom, cote in (("G", 1), ("D", -1)):
        globe = PORT @ Vector((0.050 * cote, -0.008, 0.020))
        a.piece("globe_" + nom, A.boule(0.020, 32, 16), IVOIRE, pos=globe)
        regard = vers(0.22 * cote, -0.96, 0.05).normalized()
        a.bouton("oeil_" + nom, globe + regard * 0.020, regard, 0.0130)
        a.rustine("paupiere_" + nom, "globe_" + nom, globe, vers(-0.20 * cote, -0.25, 0.95), 1.15, ORCHIDEE, 0.005, 11, fil=GRIFFE)
    # la moue : un petit trait qui tombe aux deux coins
    a.broderie("moue", a.trace("tete", TETE, [vers(-0.30, -0.85, -0.44), vers(0, -0.85, -0.36), vers(0.30, -0.85, -0.44)], 0.0045), 0.0021, GRIFFE)

    # ----- les antennes : deux fils fins qui partent en arrière -----
    for nom, cote in (("G", 1), ("D", -1)):
        pied = PORT @ Vector((0.013 * cote, 0.0, 0.041))
        fil = A.courbe([pied] + [pied + vers(x * cote, y, z) for x, y, z in ((0.010, 0.010, 0.030), (0.026, 0.030, 0.052), (0.044, 0.060, 0.060))], 6)
        a.piece("antenne_" + nom, A.tube(fil, lambda t: 0.0036 - 0.0016 * t, 12), ORCHIDEE, poil=False)

    # ----- les pattes ravisseuses, jointes « en prière » sous le menton : la hanche descend de l'épaule, la cuisse remonte,
    #       épaisse, et le crochet violet se replie contre elle. La main gauche est un rien plus haute -----
    for nom, cote, haut in (("G", 1, 0.007), ("D", -1, 0.0)):
        epaule, coude = (0.015 * cote, -0.094, 0.250), (0.030 * cote, -0.160, 0.205)
        poing, pointe, crochet = (0.016 * cote, -0.186, 0.292 + haut), (0.013 * cote, -0.208, 0.226 + haut), (0.013 * cote, -0.198, 0.212 + haut)
        bras = A.tube([epaule, coude], 0.0100, 14).peint(IVOIRE) \
            + A.tube(np.linspace(coude, poing, 12), lambda t: 0.009 + 0.009 * math.sin(math.pi * t), 14).peint(IVOIRE) \
            + A.tube(A.conges([poing, pointe, crochet], 0.006, 4), lambda t: 0.0090 - 0.0058 * t, 12).peint(GRIFFE)
        a.piece("bras_" + nom, bras, None, poil=False)

    # ----- les quatre pattes de marche : longues, fines, le bout rosé, chacune avec son pétale sous la cuisse -----
    hanches = ((0.026, -0.022, 0.106), (0.026, 0.012, 0.106))
    genoux = ((0.116, -0.022, 0.168), (0.106, 0.084, 0.174))
    pieds = {1: ((0.150, -0.090), (0.150, 0.170)), -1: ((0.146, -0.056), (0.144, 0.186))}
    for cote, nom in ((1, "G"), (-1, "D")):
        pattes = None
        for i in range(2):
            hanche, genou = (hanches[i][0] * cote, hanches[i][1], hanches[i][2]), (genoux[i][0] * cote, genoux[i][1], genoux[i][2])
            px, py = pieds[cote][i][0] * cote, pieds[cote][i][1]
            fil = A.conges([hanche, genou, (px, py, 0.012), (px + 0.008 * cote, py - 0.022, 0.0058)], 0.010, 5)
            une = tube_peint(fil, lambda t: 0.0078 - 0.0026 * t, [(0.62, IVOIRE), (0.80, PALE), (9, ORCHIDEE)])
            pattes = une if pattes is None else pattes + une
            lobe, pose = petale(hanche, genou)
            a.piece("petale%d_%s" % (i, nom), lobe, None, mat=pose, poil=False)
        a.piece("pattes_" + nom, pattes, None, poil=False)

    # ----- les ailes : deux pétales de feutrine posés en toit sur l'abdomen, l'ivoire cousu sur le rose qui dépasse et fait le bord -----
    bord = A.courbe([(0, 0), (0.035, 0.009), (0.105, 0.011), (0.162, 0.007), (0.190, -0.005), (0.162, -0.033), (0.092, -0.047), (0.035, -0.028)], 5, fermee=True)
    coeur = np.array((0.098, -0.016))
    file = Vector((0.165, 0.937, 0.309)).normalized()                # l'aile part vers l'arrière, en montant et en s'écartant
    dessus = Vector((0.42, 0.0, 0.91))
    dessus = (dessus - file * dessus.dot(file)).normalized()
    pose = A.cadre(Vector((0.010, -0.004, 0.149)), dessus, dessus.cross(file))
    a.piece("aile", A.decoupe(bord, 0.005, 0.002), ORCHIDEE, mat=pose, poil=False, paire=True)
    a.piece("aile_coeur", A.decoupe(coeur + (bord - coeur) * 0.80, 0.003, 0.0012).pose((0, 0, 0.0038)), IVOIRE, mat=pose, poil=False, paire=True)
    a.broderie("nervure", [pose @ Vector((u, -0.016, 0.0064)) for u in (0.028, 0.098, 0.164)], 0.0016, ORCHIDEE, paire=True)
    # le point avant qui tient l'ivoire sur le rose, tout le tour de l'aile
    piste = [(coeur[0] + (q[0] - coeur[0]) * 0.71, coeur[1] + (q[1] - coeur[1]) * 0.71, 0.0056) for q in bord]
    piste.append(piste[0])
    a.piece("aile_points", G.couture(piste, [(0, 0, 1)] * len(piste), 0.012, 0.0070, 0.0011, 0.0010), GRIFFE, mat=pose, poil=False, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py mante). Les mesures sont celles du modèle, avant a.taille.

from poses import Pose, borne, cloche, onde

# Le long cou dressé (le corselet des mantes) porte la tête et les deux pattes ravisseuses : en se penchant, il les
# emmène. Les épaules et les hanches sont symétriques : leurs os finissent en _G et l'usine les recopie en _D. La tête,
# elle, est tournée de 38° : ses antennes ont chacune leur os à sa vraie place (antenne_g, antenne_d, pas de miroir).
# Les deux pattes de marche d'un côté sont une seule pièce (pattes_G, pattes_D) : chaque point suit la patte dont le fil
# passe le plus près ; elles pendent à la racine, un pied posé ne bouge pas quand le corps se balance au-dessus de lui.
T3 = np.array(PORT.to_3x3())                   # les axes de la tête, en colonnes : sa gauche, son arrière, son dessus
_HANCHES = ((0.026, -0.022, 0.106), (0.026, 0.012, 0.106))                    # les mêmes que dans construire
_GENOUX = ((0.116, -0.022, 0.168), (0.106, 0.084, 0.174))
_PIEDS = {1: ((0.150, -0.090), (0.150, 0.170)), -1: ((0.146, -0.056), (0.144, 0.186))}
FILS = {"%d_%s" % (i, l): [np.array((c * _HANCHES[i][0], _HANCHES[i][1], _HANCHES[i][2])),
                           np.array((c * _GENOUX[i][0], _GENOUX[i][1], _GENOUX[i][2])),
                           np.array((c * _PIEDS[c][i][0], _PIEDS[c][i][1], 0.012))]
        for l, c in (("G", 1), ("D", -1)) for i in range(2)}

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, -0.005, 0.106)),                 # le thorax, à hauteur des hanches : elle s'y balance
    ("abdomen", "corps", (0.0, 0.012, 0.112)),                 # la taille, d'où l'abdomen remonte en fleur
    ("ailes_G", "abdomen", (0.010, -0.004, 0.149)),            # la racine des ailes, couchées sur l'abdomen
    ("cou", "corps", (0.0, -0.012, 0.124)),                    # le pied du long cou
    ("tete", "cou", (-0.004, -0.114, 0.308)),                  # la nuque, en haut du cou
    ("antenne_g", "tete", (0.004, -0.124, 0.374)),             # le pied des antennes (la tête est tournée : pas de miroir)
    ("antenne_d", "tete", (-0.017, -0.140, 0.371)),
    ("bras_G", "cou", (0.015, -0.094, 0.250)),                 # l'épaule d'une patte ravisseuse
    ("patte0_G", "racine", _HANCHES[0]),                       # la hanche de la patte de marche de devant
    ("patte1_G", "racine", _HANCHES[1]),                       # et de celle de derrière
]


def _cote(nom):
    """Une pièce d'un côté (antenne_G, antenne_D) suit l'os de son côté (antenne_g, antenne_d)."""
    return lambda points, cote: {nom + cote.lower(): np.ones(len(points))}


def _pattes(points, cote):
    """Les deux pattes de marche d'un côté, une seule pièce : chaque point suit la patte dont le fil passe le plus près.
    L'usine retourne les pièces de droite en miroir avant de les donner : on les remet à leur place."""
    q = points * ([1, 1, 1] if cote == "_G" else [-1, 1, 1])
    ecarts = []
    for i in range(2):
        f = FILS["%d%s" % (i, cote)]
        e = np.full(len(q), 9.0)
        for a, b in zip(f[:-1], f[1:]):
            u = np.clip((q - a) @ (b - a) / ((b - a) @ (b - a)), 0.0, 1.0)
            e = np.minimum(e, np.linalg.norm(q - a - u[:, None] * (b - a), axis=1))
        ecarts.append(e)
    proche = np.argmin(ecarts, axis=0)
    return {"patte%d%s" % (i, cote): (proche == i).astype(float) for i in range(2)}


PORTEURS = [("abdomen", "abdomen"), ("thorax", "corps"), ("cou", "cou"),
            ("aile", "ailes", True), ("nervure", "ailes", True),          # aile, aile_coeur, aile_points
            ("tete", "tete"), ("globe", "tete"), ("oeil", "tete"), ("moue", "tete"), ("antenne", _cote("antenne")),
            ("bras", "bras", True), ("petale0", "patte0", True), ("petale1", "patte1", True), ("pattes", _pattes),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os ;
            # ses lourdes paupières roses à elle (paupiere_G, paupiere_D) sont cousues sur les globes et suivent la tête
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1"),
            ("paupiere", "tete")]


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


def tete(p, hoche=0.0, tourne=0.0, penche=0.0, cou=0.0):
    """La tête autour de ses axes à elle : hoche > 0, le menton plonge ; tourne > 0, elle regarde vers sa gauche ;
    penche > 0, elle se couche sur son épaule gauche. cou : de combien le cou s'est penché en avant (degrés), qu'on
    défait d'abord : le cou se balance, la tête reste d'aplomb et le regard ne bouge pas."""
    p.add("tete", rot=angles(tour((1, 0, 0), -cou) @ tour(T3[:, 2], tourne) @ tour(T3[:, 0], hoche) @ tour(T3[:, 1], penche)))


def jambe(p, nom, arriere=0.0, leve=0.0):
    """Tourne une patte de marche sur sa hanche : « arriere » degrés vers l'arrière (autour de la verticale), « leve »
    degrés vers le haut (le pied monte en s'écartant)."""
    H, F = FILS[nom][0], FILS[nom][2]
    c = 1 if nom.endswith("G") else -1
    R = tour((0, 0, 1), c * arriere) @ tour(np.cross((F - H) * [1, 1, 0], (0, 0, 1)), leve)
    p.add("patte" + nom, rot=angles(R))


def bras(p, leve=0.0, ouvre=0.0, gauche=(0.0, 0.0)):
    """Les pattes ravisseuses : « leve » > 0 les dresse vers l'avant et le haut, « ouvre » > 0 les écarte l'une de
    l'autre ; gauche = (leve, ouvre) en plus pour la seule patte gauche."""
    p.paire("bras", rot=(-leve, 0, ouvre))
    p.add("bras_G", rot=(-gauche[0], 0, gauche[1]))


def antennes(p, g, d):
    """Les antennes : de combien chacune se relève (degrés) ; < 0, elle se couche en arrière."""
    p.add("antenne_g", rot=(-g, 0, 0))
    p.add("antenne_d", rot=(-d, 0, 0))


def repos(t):
    """Elle a tout son temps : l'abdomen respire, le long cou se berce comme une tige dans le vent ; elle penche la
    tête de côté pour nous dévisager, longuement ; puis elle porte sa patte ravisseuse gauche à sa bouche et la
    nettoie à petits coups, sans nous quitter des yeux. Un clignement lent, les antennes qui frémissent."""
    p = Pose()
    r = onde(t, 2)
    berce = onde(t, 1)
    devisage = cloche(t, 0.28, 0.15)
    toilette = cloche(t, 0.66, 0.11)
    p.add("corps", rot=(0, 1.2 * berce, 0))
    p.add("abdomen", rot=(2 * r, 0, -2 * berce), ech=(1 + 0.025 * r, 1, 1 + 0.025 * r))
    p.add("cou", rot=(1.5 * onde(t, 1, 0.25) + 5 * toilette, 2.5 * onde(t, 1, 0.1), 0))
    tete(p, 10 * toilette + 4 * toilette * onde(t, 16), 6 * devisage, 18 * devisage, 5 * toilette)
    bras(p, 0, 0, (22 * toilette, -6 * toilette))
    antennes(p, 10 * cloche(t, 0.46, 0.05) + 3 * r, 10 * cloche(t, 0.50, 0.05) + 3 * r)
    p.ouvert = 1 - cloche(t, 0.12, 0.04) - cloche(t, 0.86, 0.04)
    return p


def avance(t):
    """Elle marche en se balançant comme une feuille : à chaque pas tout le corps part en avant puis revient, le cou
    se berce avec un temps de retard et la tête, elle, reste d'aplomb, les yeux sur nous. Les pattes de marche vont
    par paires croisées (l'avant d'un côté, l'arrière de l'autre), les mains restent jointes."""
    p = Pose()
    s = onde(t, 1)
    balance = onde(t, 2)
    p.add("corps", rot=(2.5 * balance, 0, 0), pos=(0, -0.004 * balance, 0))
    cou = 6 * onde(t, 2, -0.08)
    p.add("cou", rot=(cou, 1.5 * s, 0))
    tete(p, 0, 0, 0, cou + 2.5 * balance)
    p.add("abdomen", rot=(-2 * balance, 0, -3 * s))
    for nom in FILS:
        ph = math.tau * t + (0.0 if nom in ("0_G", "1_D") else math.pi)
        jambe(p, nom, 12 * math.sin(ph), 12 * max(0.0, -math.cos(ph)))
    bras(p, 3 * onde(t, 2, -0.15))
    antennes(p, 4 * onde(t, 2, -0.2), 4 * onde(t, 2, -0.2))
    return p


def mange(t):
    """Penchée sur sa prise, qu'elle tient entre ses deux crochets sous le menton : le cou plié, elle grignote à petits
    coups secs, tourne la bouchée, recommence ; à la fin elle se redresse et lisse ses antennes."""
    p = Pose()
    bas = 1 - cloche(t, 0.88, 0.12)
    croque = max(0.0, onde(t, 8)) ** 2 * bas
    p.add("corps", rot=(4 * bas, 0, 0))
    p.add("cou", rot=(16 * bas, 0, 0))
    tete(p, 22 * bas + 8 * croque, 6 * bas * onde(t, 2), 0, 0)
    bras(p, 22 * bas + 4 * croque, 0, (3 * bas * onde(t, 2), 0))
    antennes(p, -6 * bas, -6 * bas)
    p.add("abdomen", rot=(2 * onde(t, 2), 0, 0))
    p.ouvert = 1 - 0.3 * bas
    return p


def joie(t):
    """Sa parade : elle se dresse de toute sa taille, ouvre grand ses ailes roses en éventail, lève les bras au ciel
    et recourbe l'abdomen comme une fleur qui s'ouvre ; elle frémit, puis replie tout, lentement, et reprend la pose."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.86)) ** 0.8 if t < 0.86 else 0.0
    fremit = env * onde(t, 9)
    p.add("corps", rot=(-4 * env, 0, 0), pos=(0, 0, 0.006 * env))
    p.add("cou", rot=(-10 * env, 0, 0))
    tete(p, -6 * env, 0, -10 * env, -14 * env)
    bras(p, 32 * env, 55 * env)
    p.paire("ailes", rot=(34 * env + 4 * fremit, 0, -36 * env))
    p.add("abdomen", rot=(14 * env, 0, 0))
    antennes(p, 20 * env, 20 * env)
    return p


def dort(t):
    """Elle dort debout, comme une fleur fanée : le cou plié en avant, la tête qui pend, les mains rentrées sous le
    menton, l'abdomen retombé, les antennes couchées ; les yeux fermés, elle respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", rot=(3, 0, 0), pos=(0, 0, -0.008))
    p.add("cou", rot=(14 + 1.0 * r, 0, 0))
    tete(p, 24 + 1.5 * r, 0, 6, 0)
    bras(p, -8)
    p.add("abdomen", rot=(-6, 0, 0), ech=(1 + 0.02 * r, 1, 1 + 0.02 * r))
    antennes(p, -22, -18)
    for nom in FILS:
        jambe(p, nom, 0.0, 0.0)
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Mante")
