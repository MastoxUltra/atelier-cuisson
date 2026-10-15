"""Le mille-pattes en peluche : un long corps de quinze segments bombés en feutrine rase acajou, un anneau de peluche
caramel dans chaque creux, une soixantaine de petites pattes jaune orangé bien rangées, dont la vague de la marche se
lit d'un bout à l'autre, deux antennes couchées par la vitesse, deux crochets à l'arrière. Un employé pressé : l'avant
du corps redressé et penché vers l'avant, la tête tournée vers nous sans ralentir, le sourcil inquiet, le corps qui
ondule en S derrière lui.

    python mille_pattes.py        fabrique la fiche art/apercus/animaux/mille_pattes.png
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

ACAJOU = M.hexa("#561a12")                    # la feutrine rase des segments : un acajou sombre (la feutrine sort plus claire et plus rouge)
BRUNI = M.hexa("#7a2a1c")                     # le même en peluche, pour l'arrière de la tête (le poil le fonce)
CARAMEL = M.hexa("#d99a55")                   # les anneaux et le visage, en peluche
ORANGE = M.hexa("#ffac1c")                    # le jaune orangé des pattes, des antennes et des crochets

# Sur la fiche, il était posé de biais (TOURNE = -42) : il filait vers la gauche et nous jetait un regard au passage.
# Pour le jeu, TOURNE est à 0 : il marche droit vers -Y, et c'est dans ce repère que sont donnés ses os.
TOURNE = 0
LOC = A.repere((0, 0, 0), (0, 0, TOURNE))

RAYON, SEGMENTS, GARDE = 0.036, 15, 0.062     # le rayon du corps, le nombre de segments, la hauteur de son fil au-dessus du sol
# Le fil du corps, du bout de la queue à la nuque : un S couché dans l'herbe, puis l'avant se redresse, penché en avant.
CHEMIN = [(0.060, 0.400, GARDE), (-0.060, 0.300, GARDE), (-0.090, 0.190, GARDE), (0.000, 0.110, GARDE), (0.090, 0.030, GARDE),
          (0.080, -0.070, GARDE), (0.000, -0.135, 0.072), (-0.022, -0.200, 0.118), (-0.030, -0.255, 0.185), (-0.030, -0.295, 0.250)]


def fil(chemin):
    """Prépare un chemin lissé : rend sa longueur, et repere(s) -> (centre, avant, dos, côté gauche) à la distance s
    du départ ; le dos de la pièce cherche le ciel."""
    pts = A.courbe(chemin, 16)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    sens = np.gradient(pts, fait, axis=0)

    def repere(s):
        s = np.asarray(s, float)
        centre = np.stack([np.interp(s, fait, pts[:, k]) for k in range(3)], axis=-1)
        avant = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
        dos = np.array([0.0, 0.0, 1.0]) - avant[..., 2:3] * avant
        dos = dos / np.linalg.norm(dos, axis=-1, keepdims=True)
        return centre, avant, dos, np.cross(dos, avant)
    return float(fait[-1]), repere


LONG, REPERE = fil(CHEMIN)
PAS = LONG / SEGMENTS                         # la longueur d'un segment
NUQUE = [Vector(q) for q in REPERE(LONG)]     # le bout du fil : son centre, sa direction, son dos, sa gauche
TETE = NUQUE[0] + NUQUE[1] * 0.036 + NUQUE[2] * 0.010
PORT = LOC @ A.repere(TETE, (4, -9, 58))      # la tête : tournée vers nous par-dessus l'épaule gauche, un peu penchée
CENTRE = PORT @ Vector((0, 0, 0))


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def rayon(s):
    """Le rayon du corps à la distance s du bout de la queue : chaque segment est bombé, pincé à ses deux bouts ;
    la queue s'affine et finit ronde."""
    s = np.asarray(s, float)
    galbe = 0.72 + 0.28 * np.abs(np.sin(np.pi * s / PAS)) ** 0.5
    fuseau = 0.52 + 0.48 * K.lisse(s / (2.6 * PAS))
    return RAYON * galbe * fuseau * np.sqrt(np.clip(s / 0.016, 0.0, 1.0))


def couche(v):
    """Pour sculpte() : couche le long du fil une pièce faite toute droite (son X : la gauche, son Y : le dos)."""
    centre, _avant, dos, cote = REPERE(np.clip(v[:, 2], 0.0, LONG))
    return centre + v[:, 0:1] * cote + v[:, 1:2] * dos


def rangee(cote):
    """Toutes les pattes d'un côté, deux par segment : la hanche sous le flanc, un genou écarté, le pied au sol.
    D'une patte à l'autre le pied avance ou recule un peu : c'est la vague de la marche. Là où le corps se redresse,
    les pattes ne touchent plus terre et restent tendues devant lui, comme de petits bras."""
    toutes = None
    for i in range(1, 2 * SEGMENTS):
        s = PAS * (0.25 + 0.5 * i)
        c, avant, dos, gauche = REPERE(s)
        r = float(rayon(s))
        chute = min((c[2] - 0.006) / max(dos[2], 0.3), r + 0.032)
        vague = 0.015 * math.sin(math.tau * i / 7.0 + (0.0 if cote > 0 else math.pi))
        hanche = c + gauche * (cote * 0.55 * r) - dos * (0.50 * r)
        genou = c + gauche * (cote * (r + 0.020)) - dos * (0.40 * r) + avant * (0.4 * vague)
        pied = c + gauche * (cote * (r + 0.032)) - dos * chute + avant * vague
        une = A.tube(A.conges([hanche, genou, pied], 0.012, 4), lambda t: 0.0070 - 0.0018 * t, 12)
        toutes = une if toutes is None else toutes + une
    return toutes


def construire():
    a = K.Animal("mille_pattes")
    a.taille = 0.45
    a.tete = PORT @ Vector((0, -0.066, 0.0))

    # ----- le corps : un seul boudin de feutrine rase, tourné tout droit avec ses quinze bosses, puis couché le long du fil -----
    cotes = np.linspace(0.0, LONG, 15 * SEGMENTS + 1)
    corps = A.tour([(0.0, 0.0)] + [(float(rayon(s)), float(s)) for s in cotes[1:-1]] + [(0.0, LONG)], 36)
    a.piece("corps", corps.sculpte(couche), ACAJOU, mat=LOC, poil=False)

    # ----- les anneaux : un bourrelet de peluche caramel dans chaque creux, entre deux segments -----
    anneaux = None
    for k in range(1, SEGMENTS + 1):
        s = min(k * PAS, LONG - 0.004)
        un = A.tore(float(rayon(s + 0.5 * PAS)) * 0.80, 0.0085, 36, 10).etire(1.0, 1.0, 1.45).pose((0, 0, s))
        anneaux = un if anneaux is None else anneaux + un
    a.piece("anneaux", anneaux.sculpte(couche), CARAMEL, mat=LOC)

    # ----- la tête : une boule de peluche plus grosse que le corps, le visage caramel devant, l'arrière acajou.
    #       Dans la pièce : X la gauche, Y le dessus, Z vers le visage -----
    tranches = sorted(set((-np.cos(np.linspace(0.0, math.pi, 29))).round(5).tolist() + [-0.062, -0.038]))
    tete = K.bandes(A.tour([(math.sqrt(max(0.0, 1 - z * z)), z) for z in tranches], 48), [(-0.05, BRUNI), (9, CARAMEL)])
    a.piece("tete", tete.etire(0.073, 0.068, 0.070), None, mat=PORT @ A.repere((0, 0, 0), (90, 0, 0)))
    a.couture("raie", "tete", 9, 0.06, 0.47, fil=ORANGE)             # la raie sur le côté, bien peignée

    # ----- le visage : deux gros boutons rapprochés, deux sourcils qui remontent au milieu (il est en retard),
    #       et une petite bouche pincée -----
    for nom, cote in (("_G", 1), ("_D", -1)):
        p, n = a.surface("tete", CENTRE, vers(0.43 * cote, -0.84, 0.24))
        a.bouton("oeil" + nom, p + n * 0.001, n, 0.025)
        sourcil = a.trace("tete", CENTRE, [vers(0.16 * cote, -0.78, 0.76), vers(0.42 * cote, -0.74, 0.70), vers(0.68 * cote, -0.62, 0.50)], 0.004)
        a.broderie("sourcil" + nom, A.courbe(sourcil, 5), 0.0046, ACAJOU)
    bouche = a.trace("tete", CENTRE, [vers(-0.17, -1, -0.42), vers(0.0, -1, -0.34), vers(0.17, -1, -0.42)], 0.005)
    a.broderie("bouche", A.courbe(bouche, 5), 0.0046, ACAJOU)

    # ----- les antennes : deux longs brins de feutrine orange, couchés en arrière par la vitesse (dans le sens de
    #       sa course, pas dans celui de son regard) -----
    for nom, cote in (("_G", 1), ("_D", -1)):
        pied = PORT @ Vector((0.026 * cote, -0.022, 0.058))
        brin = A.courbe([pied] + [pied + LOC.to_3x3() @ Vector((x * cote, y, z)) for x, y, z in ((0.012, -0.012, 0.050), (0.034, 0.040, 0.092), (0.050, 0.115, 0.098), (0.058, 0.185, 0.070))], 8)
        a.piece("antenne" + nom, A.tube(brin, lambda t: 0.0085 - 0.0038 * t, 12), ORANGE, poil=False)

    # ----- les pattes : une rangée de chaque côté, en feutrine jaune orangé -----
    a.piece("pattes_G", rangee(1), ORANGE, mat=LOC, poil=False)
    a.piece("pattes_D", rangee(-1), ORANGE, mat=LOC, poil=False)

    # ----- les deux crochets de l'arrière, qui rebiquent -----
    c, avant, dos, gauche = (Vector(q) for q in REPERE(0.012))
    for nom, cote in (("_G", 1), ("_D", -1)):
        croc = A.courbe([c + gauche * (0.008 * cote), c - avant * 0.030 + gauche * (0.022 * cote) + dos * 0.004,
                         c - avant * 0.052 + gauche * (0.036 * cote) + dos * 0.022, c - avant * 0.058 + gauche * (0.040 * cote) + dos * 0.046], 6)
        a.piece("crochet" + nom, A.tube(croc, lambda t: 0.0085 - 0.0050 * t, 12), ORANGE, mat=LOC, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py mille_pattes)

from poses import Pose, borne, cloche, onde

# Il n'est pas symétrique (le corps ondule en S, la tête est tournée) : chaque côté a ses os à lui, nommés _g et _d,
# sans miroir. Un os par segment, qui plie sur l'anneau du côté du « corps » ; le « corps » est le onzième segment,
# là où l'avant se redresse : de lui part une chaîne vers la queue et une autre vers la tête. Et un os par patte,
# numérotées depuis la tête : la vague de la marche passe d'une patte à sa voisine.
MILIEU = 10
SEG = ["corps" if k == MILIEU else "seg%02d" % k for k in range(SEGMENTS)]
PARENT = ["racine" if k == MILIEU else SEG[k + 1] if k < MILIEU else SEG[k - 1] for k in range(SEGMENTS)]
PIVOT = [REPERE((k + 1) * PAS if k < MILIEU else (k + 0.5) * PAS if k == MILIEU else k * PAS) for k in range(SEGMENTS)]
NUQUE_ = REPERE(LONG)


def _jambes():
    """Chaque patte telle que rangee() la dessine : son os, son côté, son rang depuis la queue, sa hanche, son genou,
    son pied, l'axe et le dos du corps à cet endroit, son segment, et de combien de degrés elle est cousue en avant."""
    jambes = []
    for cote, lettre in ((1, "g"), (-1, "d")):
        for i in range(1, 2 * SEGMENTS):
            s = PAS * (0.25 + 0.5 * i)
            c, avant, dos, gauche = REPERE(s)
            r = float(rayon(s))
            chute = min((c[2] - 0.006) / max(dos[2], 0.3), r + 0.032)
            vague = 0.015 * math.sin(math.tau * i / 7.0 + (0.0 if cote > 0 else math.pi))
            jambes.append({"os": "patte%02d_%s" % (2 * SEGMENTS - i, lettre), "cote": cote, "i": i, "seg": int(s // PAS),
                           "hanche": c + gauche * (cote * 0.55 * r) - dos * (0.50 * r),
                           "genou": c + gauche * (cote * (r + 0.020)) - dos * (0.40 * r) + avant * (0.4 * vague),
                           "pied": c + gauche * (cote * (r + 0.032)) - dos * chute + avant * vague,
                           "avant": avant, "dos": dos, "cousue": math.degrees(math.atan2(vague, 0.45 * r + 0.032))})
    return jambes


JAMBES = _jambes()
DEVANT = [j for j in JAMBES if j["seg"] > MILIEU]          # les « petits bras » : les pattes du buste, qui ne touchent pas terre

OS = ([("racine", None, (0, 0, 0))]
      + [(SEG[k], PARENT[k], tuple(PIVOT[k][0])) for k in [MILIEU] + list(range(MILIEU - 1, -1, -1)) + list(range(MILIEU + 1, SEGMENTS))]
      + [("tete", SEG[-1], tuple(NUQUE_[0]))]
      + [("antenne_" + l, "tete", tuple(PORT @ Vector((0.026 * c, -0.022, 0.058)))) for l, c in (("g", 1), ("d", -1))]
      + [("crochet_" + l, SEG[0], tuple(REPERE(0.012)[0] + REPERE(0.012)[3] * (0.008 * c))) for l, c in (("g", 1), ("d", -1))]
      + [(j["os"], SEG[j["seg"]], tuple(j["hanche"])) for j in JAMBES])

_S_FIL = np.linspace(0.0, LONG, 1200)
_FIL = REPERE(_S_FIL)[0]


def souple(points, cote):
    """Le corps et ses anneaux : chaque segment suit son os ; sur un anneau, le tissu passe en deux centimètres
    d'un os à l'autre (c'est là que le corps plie). On repère chaque point par sa distance le long du fil."""
    s = np.empty(len(points))
    for d in range(0, len(points), 2000):
        q = points[d:d + 2000]
        s[d:d + 2000] = _S_FIL[np.argmin(((q[:, None, :] - _FIL[None, :, :]) ** 2).sum(-1), axis=1)]
    k = np.clip(np.floor(s / PAS), 0, SEGMENTS - 1).astype(int)
    pli = np.clip(np.round(s / PAS), 1, SEGMENTS - 1).astype(int)          # l'anneau le plus proche
    f = K.lisse((s - pli * PAS + 0.010) / 0.020)                          # 0 côté queue, 1 côté tête
    pres = np.abs(s - pli * PAS) < 0.010
    return {n: np.where(pres, np.where(pli == j, f, 0.0) + np.where(pli - 1 == j, 1.0 - f, 0.0), (k == j).astype(float))
            for j, n in enumerate(SEG)}


def pattes(points, cote):
    """Toutes les pattes d'un côté sont une seule pièce : chaque point suit la patte dont le fil passe le plus près.
    L'usine retourne les pièces de droite en miroir avant de les donner : on les remet à leur place."""
    c = 1 if cote == "_G" else -1
    q = points * [c, 1, 1]
    miennes = [j for j in JAMBES if j["cote"] == c]
    ecarts = []
    for j in miennes:
        e = np.full(len(q), 9.0)
        for a, b in ((j["hanche"], j["genou"]), (j["genou"], j["pied"])):
            u = np.clip((q - a) @ (b - a) / ((b - a) @ (b - a)), 0.0, 1.0)
            e = np.minimum(e, np.linalg.norm(q - a - u[:, None] * (b - a), axis=1))
        ecarts.append(e)
    proche = np.argmin(ecarts, axis=0)
    return {j["os"]: (proche == n).astype(float) for n, j in enumerate(miennes)}


def _cote(nom):
    """Une pièce d'un côté (antenne_G, crochet_D) suit l'os de son côté (antenne_g, crochet_d)."""
    return lambda points, cote: {nom + cote.lower(): np.ones(len(points))}


PORTEURS = [("corps", souple, "corps"), ("anneaux", souple, "corps"), ("tete", "tete"), ("raie", "tete"), ("oeil", "tete"),
            ("sourcil", "tete"), ("bouche", "tete"), ("antenne", _cote("antenne")), ("crochet", _cote("crochet")),
            ("pattes", pattes),
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


TETE_AXES = np.array(PORT.to_3x3())                         # en colonnes : sa gauche, son arrière, son haut


def tete(p, hoche=0.0, tourne=0.0, penche=0.0, cou=None):
    """Tourne la tête autour de ses axes à elle (elle regarde de côté) : hoche > 0, le nez plonge ; tourne > 0, elle
    regarde vers sa gauche ; penche > 0, elle se couche sur son épaule gauche. cou : la rotation que le buste a déjà
    donnée à la tête (ce que rendent les plie), qu'on défait d'abord pour qu'elle reste d'aplomb."""
    G, AR, H = TETE_AXES[:, 0], TETE_AXES[:, 1], TETE_AXES[:, 2]
    R = tour(H, tourne) @ tour(G, hoche) @ tour(AR, penche)
    p.add("tete", rot=angles(R if cou is None else cou.T @ R))


def plie(p, k, degres, lacet=0.0):
    """Plie le segment k sur son anneau : « degres » vers le bas (autour de sa gauche), « lacet » vers sa gauche.
    Rend la rotation donnée."""
    R = tour(PIVOT[k][2], lacet) @ tour(PIVOT[k][3], degres)
    p.add(SEG[k], rot=angles(R))
    return R


def patte(p, j, avant, leve):
    """Tourne une patte sur sa hanche : « avant » degrés vers l'avant (autour du dos), « leve » degrés vers le haut
    (autour de l'axe du corps). Les angles se comptent depuis la pose cousue."""
    p.add(j["os"], rot=angles(tour(j["dos"], -j["cote"] * avant) @ tour(j["avant"], j["cote"] * leve)))


def phase(j, t, tours):
    """La phase d'une patte dans la vague de la marche : la vague court de la tête vers la queue, sept pattes par
    longueur d'onde, les deux côtés à contretemps. Au départ (t = 0), c'est la vague cousue sur le modèle."""
    return math.tau * (j["i"] / 7.0 + tours * t) + (0.0 if j["cote"] > 0 else math.pi)


def poser_corps(p, W):
    """W[k] = (rotation, où va son pivot) : la place voulue de chaque segment dans le monde. Écrit dans la pose ce que
    chaque os doit faire par rapport à son parent pour l'y mettre."""
    for k in range(SEGMENTS):
        Q, P = W[k]
        h = PIVOT[k][0]
        if k == MILIEU:
            R, d = Q, P - h
        else:
            kp = SEG.index(PARENT[k])
            Qp, Pp = W[kp]
            R, d = Qp.T @ Q, Qp.T @ (P - Pp) - (h - PIVOT[kp][0])
        p.add(SEG[k], rot=angles(R), pos=tuple(d))


def _cadre(a, b):
    """Le repère d'un segment posé de a à b, en colonnes : son axe (vers la tête), son dos (vers le ciel), sa gauche."""
    t = (b - a) / np.linalg.norm(b - a)
    dos = np.array([0.0, 0.0, 1.0]) - t[2] * t
    dos = dos / np.linalg.norm(dos)
    return np.column_stack([t, dos, np.cross(dos, t)])


BOUTS = [(REPERE(k * PAS)[0], REPERE((k + 1) * PAS)[0]) for k in range(SEGMENTS)]


def spirale(serre, centre=(0.03, 0.05), debut=-1.0, pas_=0.105, dedans=0.07, haut=0.044, nuque=0.07):
    """Le fil du corps roulé à plat pour dormir : une spirale, la tête au milieu, la queue dehors ; le cou remonte pour
    poser la tête sur le tour d'à côté, comme sur un oreiller. Rend, pour chaque segment, sa rotation et où va son pivot
    (de quoi nourrir poser_corps). serre (≈ 1) la resserre un peu : il respire."""
    th = np.linspace(0.0, 4 * math.pi, 3000)
    rho = dedans * serre + pas_ / math.tau * th
    xy = np.column_stack([centre[0] + rho * np.cos(debut + th), centre[1] + rho * np.sin(debut + th)])
    u = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))])

    def point(s):
        x, y = np.interp(LONG - s, u, xy[:, 0]), np.interp(LONG - s, u, xy[:, 1])
        return np.array([x, y, haut + nuque * float(K.lisse((s - 12.0 * PAS) / (3.0 * PAS)))])
    W = []
    for k in range(SEGMENTS):
        a, b = BOUTS[k]
        a2, b2 = point(k * PAS), point((k + 1) * PAS)
        Q = _cadre(a2, b2) @ _cadre(a, b).T
        W.append((Q, Q @ (PIVOT[k][0] - (a + b) / 2) + (a2 + b2) / 2))
    return W


def repos(t):
    """L'employé pressé attend : il respire du buste, regarde la montre qu'il n'a pas (son petit bras gauche se lève,
    la tête se penche dessus), soupire, puis pianote de toutes ses pattes, une vague qui descend de la tête à la queue.
    Les antennes frémissent, les crochets battent la mesure, il cligne deux fois."""
    p = Pose()
    r = onde(t, 2)
    montre = cloche(t, 0.38, 0.14)
    soupir = cloche(t, 0.60, 0.07)
    plie(p, 11, -1.5 * r + 5 * soupir)
    plie(p, 12, -1.0 * r - 6 * montre + 4 * soupir)
    tete(p, 22 * montre - 5 * soupir, 12 * montre, 4 * soupir)
    bras = next(j for j in JAMBES if j["os"] == "patte02_g")
    patte(p, bras, 45 * montre, 52 * montre)
    for j in JAMBES:
        d = (2 * SEGMENTS - 1 - j["i"]) / (2 * SEGMENTS - 2) - (t - 0.70) / 0.24
        patte(p, j, 0.0, 26 * cloche(d, 0.0, 0.10, False))
    p.add("antenne_g", rot=(6 * onde(t, 3) + 10 * soupir, 0, 5 * onde(t, 2)))
    p.add("antenne_d", rot=(-6 * onde(t, 4) + 10 * soupir, 0, 5 * onde(t, 2)))
    p.add("crochet_g", rot=(0, 0, 14 * cloche(t, 0.84, 0.03) + 14 * cloche(t, 0.92, 0.03)))
    p.add("crochet_d", rot=(0, 0, -14 * cloche(t, 0.88, 0.03) - 14 * cloche(t, 0.96, 0.03)))
    p.ouvert = 1 - cloche(t, 0.18, 0.02) - cloche(t, 0.72, 0.02)
    return p


def avance(t):
    """Il file : la vague de ses pattes court de la tête à la queue (deux foulées par boucle), chaque patte se lève
    en revenant vers l'avant et pousse au sol en reculant ; le corps ondule à peine, le buste dodeline à chaque pas,
    les antennes flottent."""
    p = Pose()
    for j in JAMBES:
        ph = phase(j, t, 2)
        patte(p, j, 24 * math.sin(ph) - j["cousue"], 22 * max(0.0, math.cos(ph)))
    for k in range(SEGMENTS):
        if k != MILIEU:
            plie(p, k, 0.0, 1.5 * math.sin(math.tau * (2 * t + k / 15.0)))
    plie(p, 11, 2 * onde(t, 4))
    plie(p, 13, -2 * onde(t, 4, 0.15))
    tete(p, -3 * onde(t, 4, 0.3), -4 * onde(t, 2))
    p.add("antenne_g", rot=(-8 + 5 * onde(t, 4), 0, 4 * onde(t, 2)))
    p.add("antenne_d", rot=(-8 + 5 * onde(t, 4, 0.2), 0, 4 * onde(t, 2)))
    p.add("crochet_g", rot=(0, 0, 8 * onde(t, 2)))
    p.add("crochet_d", rot=(0, 0, 8 * onde(t, 2)))
    return p


def mange(t):
    """Il couche le buste jusqu'au sol, la tête en bas ; ses petits bras tiennent la bouchée et il croque à petits
    coups, les antennes tapotent ; puis il se redresse et regarde autour de lui, la bouche pleine."""
    p = Pose()
    leve = cloche(t, 0.86, 0.13)
    bas = 1 - leve
    coups = max(0.0, onde(t, 5)) ** 2 * bas
    cou = np.eye(3)
    for k, degres in ((11, 16), (12, 18), (13, 16), (14, 10)):
        cou = cou @ plie(p, k, degres * bas)
    tete(p, 24 * bas + 10 * coups - 6 * leve, -24 * bas + 18 * leve * onde(t, 4), cou=cou)
    for j in DEVANT:
        patte(p, j, 30 * bas, (40 + 8 * coups) * bas)
    p.add("antenne_g", rot=(18 * bas + 10 * coups, 0, 0))
    p.add("antenne_d", rot=(18 * bas + 10 * max(0.0, onde(t, 5, 0.5)) ** 2 * bas, 0, 0))
    return p


def joie(t):
    """La ola : il se dresse, antennes au ciel, et une vague de pattes levées court de la tête au bout de la queue,
    qui claque des crochets ; puis il se repose."""
    p = Pose()
    env = doux(t / 0.18) * (1 - doux((t - 0.74) / 0.22))
    cou = np.eye(3)
    for k, degres in ((11, -12), (12, -12), (13, -8)):
        cou = cou @ plie(p, k, degres * env)
    tete(p, -16 * env, 0.0, 12 * env * onde(t, 3), cou=cou)
    for j in JAMBES:
        d = (2 * SEGMENTS - 1 - j["i"]) / (2 * SEGMENTS - 2) - (t - 0.10) / 0.62
        ola = cloche(d, 0.0, 0.12, False)
        patte(p, j, 20 * ola, 48 * ola)
    p.add("antenne_g", rot=(-25 * env, 0, 6 * env * onde(t, 6)))
    p.add("antenne_d", rot=(-25 * env, 0, -6 * env * onde(t, 6)))
    clac = cloche(t, 0.76, 0.04, False) + cloche(t, 0.84, 0.04, False)
    p.add("crochet_g", rot=(0, 0, 30 * clac))
    p.add("crochet_d", rot=(0, 0, -30 * clac))
    return p


def dort(t):
    """Roulé en spirale à plat, la tête au milieu, les pattes rentrées, les antennes couchées, les yeux fermés ;
    la spirale se resserre et se relâche à peine, au rythme d'une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    poser_corps(p, spirale(1 + 0.03 * r))
    tete(p, 10 + 2 * r, 0.0, 12)
    for j in JAMBES:
        patte(p, j, (-50 if j["seg"] > MILIEU else -30) - j["cousue"], 40 if j["seg"] > MILIEU else 28)
    p.add("antenne_g", rot=(-50 - 3 * r, 0, 0))
    p.add("antenne_d", rot=(-46 + 3 * r, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Mille-pattes")
