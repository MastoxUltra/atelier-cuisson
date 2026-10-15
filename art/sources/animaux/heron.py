"""Le héron en peluche : le dos et les ailes bleu gris cendré, le cou et le ventre blancs, une ligne de tirets noirs
sur le devant du cou, la calotte blanche entre deux bandeaux noirs qui se rejoignent à la nuque en une longue
aigrette, un grand bec jaune en poignard. Un pêcheur immobile et dédaigneux : debout sur UNE échasse, l'autre patte
repliée sous le ventre, le cou replié en S entre les épaules, la paupière lourde, l'œil en coin.

    python heron.py        fabrique la fiche art/apercus/animaux/heron.png
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

CENDRE = M.hexa("#8590a6")                    # le dos : un bleu gris de cendre (le poil le bleuit : il faut le prendre plus gris)
ORAGE = M.hexa("#6c7890")                     # les ailes, un ton plus bas
ENCRE = M.hexa("#1b1c25")                     # l'aigrette, les bandeaux, les tirets, le bout des ailes
BEC = M.hexa("#ffc31c")                       # le bec
OCRE = M.hexa("#d9a22a")                      # les échasses et le fil
BIAIS, DETOURNE = 0.0, 15.0                   # pour la fiche, BIAIS = -28 (posé de profil, tourné vers sa droite) ; 0 pour le jeu ;
                                              # la tête revient un peu vers sa gauche


def cap(degres):
    """Pour un cap donné (0 = droit devant, négatif = vers sa droite) : la direction de l'avant et celle du flanc gauche."""
    t = math.radians(degres)
    return Vector((math.sin(t), -math.cos(t), 0.0)), np.array([math.cos(t), math.sin(t), 0.0])


POSE = A.repere((0, 0, 0), (0, 0, BIAIS))     # tout ce qui est dit « dans son repère » (X la gauche, -Y l'avant) passe par là
CORPS = Vector((0.0, 0.03, 0.80))
FIER = POSE @ A.repere(CORPS, (-55, 0, 0))    # le corps, presque debout : les épaules en haut, la queue en bas
AVANT, FLANC = cap(BIAIS + DETOURNE)          # le plan du cou
BASE = POSE @ Vector((0.0, -0.075, 0.900))    # le pied du cou, enfoui entre les épaules
# le cou : chaque point (ce qu'il avance, ce qu'il monte) depuis la base. Il tombe devant le poitrail, revient en arrière
# au-dessus des épaules, et repart vers l'avant porter la tête : un S serré.
S = [(0.0, 0.0), (0.075, -0.045), (0.148, -0.030), (0.170, 0.045), (0.125, 0.115), (0.058, 0.150), (0.022, 0.205),
     (0.042, 0.265), (0.102, 0.292), (0.162, 0.284)]


class Fil:
    """Un chemin lissé, tenu dans un plan debout : de quoi coucher une pièce tournée le long d'un cou en S."""

    def __init__(self, points, flanc, pas=8):
        self.p = A.courbe(points, pas)
        self.fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(self.p, axis=0), axis=1))])
        self.sens = np.gradient(self.p, self.fait, axis=0)
        self.long = float(self.fait[-1])
        self.flanc = np.asarray(flanc, float)

    def cadre(self, s):
        """À s mètres de la base : le centre du fil, la direction où il va, et sa nuque (le dessus, là où il est couché)."""
        centre = np.stack([np.interp(s, self.fait, self.p[:, k]) for k in range(3)], axis=-1)
        avant = np.stack([np.interp(s, self.fait, self.sens[:, k]) for k in range(3)], axis=-1)
        avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
        return centre, avant, np.cross(avant, self.flanc)

    def couche(self, v):
        """Couche une pièce tournée toute droite (son axe Z) le long du fil : son +X devient le flanc gauche, son +Y la nuque."""
        s = np.clip(v[:, 2], 0.0, self.long)
        centre, avant, nuque = self.cadre(s)
        return centre + avant * (v[:, 2] - s)[:, None] + v[:, 0:1] * self.flanc + v[:, 1:2] * nuque

    def vise(self, s, devant, cote, haut):
        """Depuis le centre du fil à la hauteur s : ce centre, et une direction (vers l'avant, vers la gauche, vers la nuque)."""
        centre, avant, nuque = self.cadre(s)
        return Vector(centre), Vector(avant * devant + self.flanc * cote + nuque * haut)


def echasse(points, rayons, doigts):
    """Une patte de feutrine : un boudin qui passe par ses articulations (un rayon à chacune), et au bout des doigts,
    donnés par leur cap en degrés et leur piqué vers le sol."""
    patte = A.tube(A.courbe(points, 6), lambda t: float(np.interp(t, np.linspace(0, 1, len(rayons)), rayons)), 14)
    for lacet, pique, long in doigts:
        doigt = A.boule(1.0, 16, 8).etire(0.0125, long, 0.0115).pose((0, -long * 0.82, 0)).pose((0, 0, 0), (pique, 0, lacet))
        patte = patte + doigt.pose(points[-1])
    return patte


def construire():
    a = K.Animal("heron")
    a.taille = 1.50
    P3 = POSE.to_3x3()

    # ----- le corps : un œuf presque debout, les épaules marquées ; le dessous est blanc, tenu par un point avant ocre -----
    def oeuf(v):
        v = K.bosse(v, (0, -0.70, 0.50), 0.12, 0.40)
        arriere = K.lisse(v[:, 1])
        s = v * [0.128, 0.205, 0.142]
        s[:, 0] *= 1 - 0.45 * arriere
        s[:, 2] *= 1 - 0.35 * arriere
        return s
    corps = K.bandes(A.boule(1.0, 56, 28), [(-0.33, K.BLANC), (9, CENDRE)])
    a.piece("corps", corps.sculpte(oeuf), None, mat=FIER)
    a.ourlet("ventre", "corps", 0.415, fil=OCRE)
    a.couture("dos", "corps", 14, 0.58, 0.97, fil=OCRE)

    # ----- le cou et la tête, d'une seule chaussette blanche couchée le long du S. Peints dans le poil : les tirets noirs
    #       du devant du cou (le côté 36), les deux bandeaux des tempes, et la nuque noire où ils se rejoignent. -----
    fil = Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in S], FLANC)
    L = fil.long
    pc = A.profil([(0, 0), (0.050, 0.02 * L), (0.046, 0.10 * L), (0.038, 0.25 * L), (0.034, 0.50 * L), (0.034, 0.74 * L),
                   (0.040, 0.82 * L), (0.055, 0.90 * L), (0.053, 0.94 * L), (0.037, 0.985 * L), (0, 1.005 * L)], 6)
    cou = A.tour(pc, 48)
    teinte = np.tile(np.asarray(K.BLANC, float), (len(cou.v), 1))
    for anneau in cou.anneaux:
        s = cou.v[anneau[0], 2] / L
        for j, k in enumerate(anneau):
            if len(anneau) < 2:
                continue
            tiret = abs(j - 36) <= 2 and 0.17 < s < 0.76 and ((s - 0.17) * L) % 0.084 < 0.050
            bandeau = 0.850 < s < 0.996 and (3 <= j <= 9 or 15 <= j <= 21)
            derriere = 0.775 < s <= 0.850 and 3 <= j <= 21
            if tiret or bandeau or derriere:
                teinte[k] = ENCRE
    cou.teinte = teinte
    a.piece("cou", cou.sculpte(fil.couche), None)
    centre, avant, nuque = fil.cadre(0.93 * L)
    a.tete = Vector(centre + avant * 0.06 + FLANC * 0.035)

    # ----- les yeux : un rond de feutrine jaune sous le bandeau, et dessus un bouton noir poussé dans le coin arrière
    #       (il nous regarde de côté, sans tourner la tête) ; une paupière d'encre, en biais vers le bec, ferme le haut -----
    for nom, c in (("G", 1), ("D", -1)):
        milieu, regard = fil.vise(0.925 * L, 0.20, 0.95 * c, 0.08)
        a.rustine("cerne_" + nom, "cou", milieu, regard, 0.58, BEC, 0.003, 0)
        p, n = a.surface("cou", milieu, regard)
        P = A.cadre(p + n * 0.010, n, Vector(nuque))                        # Z regarde dehors, Y monte vers la calotte
        paupiere = A.boule(1.0, 24, 12).etire(0.036, 0.017, 0.008).pose((0, 0.021, 0)).pose((0, 0, 0), (-22, 0, 14 * c))   # couchée sur le crâne
        a.piece("lourde_" + nom, paupiere, ENCRE, mat=P, poil=False)       # « paupiere » est réservé à l'usine
        p, n = a.surface("cou", *fil.vise(0.925 * L, 0.06, 0.95 * c, 0.02))
        a.bouton("oeil_" + nom, p + n * 0.0035, n, 0.0185)

    # ----- le bec : un grand poignard de feutrine jaune ; son trait brodé retombe au coin (la moue) -----
    centre, avant, nuque = fil.cadre(0.965 * L)
    B = A.cadre(Vector(centre - nuque * 0.004), Vector(avant), Vector(nuque))    # X la gauche, Y le dessus du bec, Z vers la pointe
    B3 = B.to_3x3()
    bec = A.tour(A.profil([(0, 0), (0.033, 0.006), (0.031, 0.030), (0.024, 0.095), (0.015, 0.170), (0.006, 0.232), (0, 0.240)], 6), 32)
    a.piece("bec", bec.etire(0.78, 1.0, 1.0), BEC, mat=B, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        moue = [a.trace("bec", B @ Vector((0, 0, z)), [B3 @ Vector((c * math.cos(math.radians(d)), math.sin(math.radians(d)), 0))], 0.0015)[0]
                for z, d in ((0.200, -8), (0.150, -6), (0.105, -6), (0.065, -10), (0.038, -22), (0.020, -40))]
        a.broderie("moue_" + nom, A.courbe(moue, 4), 0.0026, K.CHOCOLAT)

    # ----- l'aigrette : deux longues plumes d'encre plantées dans la nuque, qui filent en arrière et retombent -----
    centre, avant, nuque = fil.cadre(0.835 * L)
    pied, recul, haut = centre + nuque * 0.034, -np.asarray(AVANT), np.array([0.0, 0.0, 1.0])
    aigrette = None
    for c in (1, -1):
        brin = [pied, pied + recul * 0.075 + haut * 0.040 + FLANC * (0.010 * c), pied + recul * 0.180 + haut * 0.030 + FLANC * (0.024 * c),
                pied + recul * 0.275 - haut * 0.040 + FLANC * (0.036 * c), pied + recul * 0.335 - haut * 0.135 + FLANC * (0.042 * c)]
        plume = A.tube(A.courbe(brin, 6), lambda t: float(np.interp(t, [0, 0.25, 0.6, 0.85, 1], [0.011, 0.017, 0.017, 0.012, 0.004])), 12)
        aigrette = plume if aigrette is None else aigrette + plume
    a.piece("aigrette", aigrette, ENCRE, poil=False)

    # ----- les ailes : deux longs galets bleu orage plaqués sur les flancs, l'épaule d'encre, et trois rémiges d'encre
    #       qui dépassent la queue -----
    def galet(v):
        s = K.emousse(v, 0.85)
        s[:, 2] *= 1 - 0.55 * K.lisse((v[:, 1] + 0.2) / 1.2)
        return s
    for nom, c in (("G", 1), ("D", -1)):
        AILE = FIER @ A.repere((0.108 * c, 0.060, 0.030), (0, -6 * c, -9 * c))
        a.piece("aile_" + nom, A.boule(1.0, 40, 20).sculpte(galet).etire(0.030, 0.235, 0.110), ORAGE, mat=AILE)
        a.rustine("epaule_" + nom, "aile_" + nom, AILE @ Vector((0, -0.150, 0.030)), AILE.to_3x3() @ Vector((c, -0.55, 0.55)), 1.05, ENCRE, 0.003, 0)
        remiges = None
        for bas, degres in ((0.020, 9), (0.000, -7), (-0.020, -23)):
            t = math.radians(degres)
            plume = A.boule(1.0, 20, 10).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.012, 0.095, 0.028)
            plume.pose((0, 0.150 + 0.095 * math.cos(t), bas + 0.095 * math.sin(t)), (degres, 0, 0))
            remiges = plume if remiges is None else remiges + plume
        a.piece("remiges_" + nom, remiges, ENCRE, mat=AILE, poil=False)

    # ----- l'échasse : une seule patte plantée, longue et fine, le genou noué, trois doigts devant et un derrière ;
    #       en haut, une culotte de peluche blanche -----
    debout = [POSE @ Vector(q) for q in ((-0.040, 0.050, 0.720), (-0.036, 0.072, 0.500), (-0.033, 0.082, 0.370), (-0.030, 0.062, 0.240), (-0.028, 0.034, 0.0125))]
    a.piece("patte_D", echasse(debout, [0.021, 0.019, 0.028, 0.018, 0.020], [(BIAIS - 32, 0, 0.066), (BIAIS, 0, 0.074), (BIAIS + 32, 0, 0.066), (BIAIS + 180, 0, 0.040)]),
            OCRE, poil=False)
    pcu = A.profil([(0, 0), (0.050, 0.015), (0.047, 0.060), (0.031, 0.130), (0.022, 0.175), (0, 0.185)], 5)
    a.piece("culotte_D", A.tour(pcu, 28), K.BLANC, mat=POSE @ A.repere((-0.040, 0.052, 0.715), (186, 0, 0)))

    # ----- l'autre patte, repliée sous le ventre : le genou pointe en arrière, les doigts fermés pendent devant -----
    pliee = [POSE @ Vector(q) for q in ((0.045, 0.040, 0.720), (0.052, 0.112, 0.632), (0.056, 0.156, 0.572), (0.060, 0.086, 0.548), (0.064, -0.004, 0.560))]
    a.piece("patte_G", echasse(pliee, [0.021, 0.019, 0.028, 0.018, 0.019], [(BIAIS - 10, 48, 0.044), (BIAIS, 40, 0.050), (BIAIS + 10, 48, 0.044)]),
            OCRE, poil=False)
    a.piece("culotte_G", A.tour(pcu, 28).etire(1.0, 1.0, 0.75), K.BLANC, mat=POSE @ A.repere((0.045, 0.040, 0.715), (-141, 0, 0)))
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py heron)

from poses import Pose, borne, cloche, onde

# Le cou et la tête : une seule chaussette couchée le long du S, une pièce souple que le corps et quatre os se partagent
# le long du fil (cou1 au sortir des épaules, cou2 dans le coude de devant, cou3 dans le creux de la nuque, tete
# derrière le crâne). Passé 0,85 du fil, tout est à « tete », comme le bec, les yeux, les paupières lourdes et l'aigrette.
_FIL = Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in S], FLANC)
_JALONS = (("corps", 0.0), ("cou1", 0.09), ("cou2", 0.33), ("cou3", 0.62), ("tete", 0.80))

# Les deux pattes, chacune un boudin d'une pièce qui passe par la hanche, le genou et la cheville : au repos, la droite
# est l'échasse plantée, la gauche est repliée sous le ventre, deux fois plus courte. Pour marcher, elles échangent leurs
# rôles : chaque patte a quatre os à elle (cuisse, jarret, pied, doigts), tous pendus à la racine, qu'on place là où l'on
# veut ; le boudin s'étire ou se tasse entre eux. Les noms sont en minuscules : pas de miroir automatique.
_JAMBES = {"g": [POSE @ Vector(q) for q in ((0.045, 0.040, 0.720), (0.052, 0.112, 0.632), (0.056, 0.156, 0.572), (0.060, 0.086, 0.548), (0.064, -0.004, 0.560))],
           "d": [POSE @ Vector(q) for q in ((-0.040, 0.050, 0.720), (-0.036, 0.072, 0.500), (-0.033, 0.082, 0.370), (-0.030, 0.062, 0.240), (-0.028, 0.034, 0.0125))]}
_REPOS = {c: (np.array(j[0]), np.array(j[2]), np.array(j[4])) for c, j in _JAMBES.items()}      # hanche, genou, cheville
_PIQUE = {"g": 45.0, "d": 0.0}                    # au repos, les doigts de la patte repliée pendent ; ceux de l'échasse sont à plat
_HANCHES = np.array(POSE @ Vector((0.0, 0.05, 0.72)))


def _au_fil(f):
    """Le centre du cou à la fraction f de sa longueur : le pivot d'un os."""
    return tuple(round(float(x), 3) for x in _FIL.cadre(f * _FIL.long)[0])


def _abscisse(points, fil):
    """Pour chaque point : sa place le long du fil (de 0 à 1), au pied de la perpendiculaire sur le tronçon le plus
    proche, et sa distance au bout du fil."""
    a, ab = fil.p[:-1], np.diff(fil.p, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    ap = points[:, None, :] - a[None, :, :]
    u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
    j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
    return (fil.fait[j] + u[np.arange(len(points)), j] * np.sqrt(l2[j])) / fil.long, np.linalg.norm(points - fil.p[-1], axis=1)


def _marche(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def _relais(f, jalons, large):
    """Des os qui se passent la main le long d'un fil : chacun porte le tronçon qui suit son pivot, et cède au suivant
    en douceur sur ± large autour du pivot de celui-ci."""
    montees = [np.ones_like(f)] + [_marche((f - f0 + large) / (2 * large)) for _o, f0 in jalons[1:]] + [np.zeros_like(f)]
    return {o: montees[i] - montees[i + 1] for i, (o, _f0) in enumerate(jalons)}


def _cou(points, cote):
    return _relais(_abscisse(points, _FIL)[0], _JALONS, 0.05)


_FILS_JAMBES = {c: Fil([tuple(q) for q in j], (1, 0, 0), 6) for c, j in _JAMBES.items()}
_GENOU = {c: float(_abscisse(np.array([tuple(_JAMBES[c][2])], float), f)[0][0]) for c, f in _FILS_JAMBES.items()}


def _patte(points, cote):
    """Une patte s'étire entre ses os : de la hanche au genou, la cuisse passe à « jarret » ; du genou à la cheville,
    « jarret » passe à « pied » ; au-delà de la cheville, les doigts suivent « doigts »."""
    c = cote[1:].lower()
    pts = points * ([-1, 1, 1] if cote == "_D" else [1, 1, 1])        # l'usine donne la patte droite en miroir : on la remet
    f, bout = _abscisse(pts, _FILS_JAMBES[c])
    g = _GENOU[c]
    haut = np.clip(f / g, 0.0, 1.0)
    bas = np.clip((f - g) / (1.0 - g), 0.0, 1.0)
    doigts = _marche((bout - 0.024) / 0.02) * (f > 0.97)
    return {"cuisse_" + c: (1 - haut), "jarret_" + c: haut * (1 - bas), "pied_" + c: bas * (1 - doigts), "doigts_" + c: bas * doigts}


def _culotte(points, cote):
    return {"cuisse_" + cote[1:].lower(): np.ones(len(points))}


OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", tuple(_HANCHES)),             # au-dessus des hanches : il se penche et se redresse autour
    ("cou1", "corps", _au_fil(0.09)),                 # le cou sort d'entre les épaules
    ("cou2", "cou1", _au_fil(0.33)),                  # le coude de devant
    ("cou3", "cou2", _au_fil(0.62)),                  # le creux de la nuque
    ("tete", "cou3", _au_fil(0.80)),                  # derrière le crâne
    ("aile_G", "corps", (0.075, -0.03, 0.935)),       # l'épaule
] + [(o + "_" + c, "racine", tuple(round(float(x), 4) for x in q))
     for c in ("g", "d") for o, q in (("cuisse", _REPOS[c][0]), ("jarret", _REPOS[c][1]), ("pied", _REPOS[c][2]), ("doigts", _REPOS[c][2]))]

PORTEURS = [("corps", "corps"), ("ventre", "corps"), ("dos", "corps"), ("cou", _cou, "tete"), ("cerne", "tete"), ("oeil", "tete"),
            ("lourde", "tete"), ("bec", "tete"), ("moue", "tete"), ("aigrette", "tete"),
            ("aile", "aile", True), ("epaule", "aile", True), ("remiges", "aile", True),
            ("patte", _patte, "corps"), ("culotte", _culotte, "corps"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


# ----- un peu de géométrie : les angles d'une Pose sont X puis Y puis Z, autour des axes du monde, en degrés

def _rot(r):
    x, y, z = (math.radians(a) for a in r)
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    return (np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
            @ np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]))


def _porte(rot, pos, q):
    """Où va le point q du corps quand le corps tourne de « rot » et se déplace de « pos » autour de ses hanches."""
    return _HANCHES + np.asarray(pos, float) + _rot(rot) @ (np.asarray(q, float) - _HANCHES)


def _angle(u, v):
    """L'angle autour de X (en degrés, entre -180 et 180) qui couche la direction u sur la direction v, vues de côté."""
    a = math.degrees(math.atan2(v[2], v[1]) - math.atan2(u[2], u[1]))
    return (a + 180.0) % 360.0 - 180.0


def _jambe(p, c, hanche, genou, cheville, pique):
    """Place la patte c ('g' ou 'd') : la hanche, le genou et la cheville là où on les veut (dans le jardin), les doigts
    piqués de « pique » degrés vers le sol (0 : à plat). Chaque tronçon tourne pour suivre sa nouvelle direction."""
    h0, g0, c0 = _REPOS[c]
    hanche, genou, cheville = (np.asarray(q, float) for q in (hanche, genou, cheville))
    cuisse, tibia = _angle(g0 - h0, genou - hanche), _angle(c0 - g0, cheville - genou)
    p.add("cuisse_" + c, rot=(cuisse, 0, 0), pos=tuple(hanche - h0))
    p.add("jarret_" + c, rot=((cuisse + tibia) / 2, 0, 0), pos=tuple(genou - g0))
    p.add("pied_" + c, rot=(tibia, 0, 0), pos=tuple(cheville - c0))
    p.add("doigts_" + c, rot=(pique - _PIQUE[c], 0, 0), pos=tuple(cheville - c0))


def _corps(p, rot=(0, 0, 0), pos=(0, 0, 0), ech=(1, 1, 1)):
    """Le corps, et la patte gauche repliée qui le suit."""
    p.add("corps", rot=rot, pos=pos, ech=ech)
    h, g, c = _REPOS["g"]
    _jambe(p, "g", _porte(rot, pos, h), _porte(rot, pos, g), _porte(rot, pos, c), _PIQUE["g"] + rot[0])
    return p


def _plante(p, rot=(0, 0, 0), pos=(0, 0, 0), recul=0.0, plie=0.0):
    """L'échasse droite plantée : la cheville au sol (reculée de « recul »), la hanche suit le corps ; le genou
    s'avance de « plie » quand la hanche descend."""
    h, g, c = _REPOS["d"]
    hanche = _porte(rot, pos, h)
    cheville = c + np.array([0.0, recul, 0.0])
    genou = (hanche + cheville) / 2 + np.array([0.0, 0.040 - plie, 0.0])
    _jambe(p, "d", hanche, genou, cheville, 0.0)


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def repos(t):
    """Planté sur son échasse, la patte gauche repliée sous le ventre : il respire, tourne la tête d'un air de dédain
    à gauche puis à droite, étire le cou vers le ciel une fois, ouvre et referme les doigts de sa patte repliée ; il cligne."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.18, 0.11), cloche(t, 0.40, 0.09)
    etire = cloche(t, 0.66, 0.12)
    _corps(p, rot=(1.0 * r, 0, 0), ech=(1 + 0.010 * r, 1, 1 + 0.014 * r))
    _plante(p, rot=(1.0 * r, 0, 0))
    p.add("cou1", rot=(-32 * etire, 0, 5 * g - 4 * d))
    p.add("cou2", rot=(48 * etire, 0, 0))
    p.add("cou3", rot=(-8 * etire, 0, 8 * g - 8 * d))
    p.add("tete", rot=(-6 * etire, 4 * g - 4 * d, 20 * g - 24 * d))
    p.add("doigts_g", rot=(-30 * cloche(t, 0.86, 0.05), 0, 0))
    p.ouvert = borne(1 - cloche(t, 0.08, 0.02) - cloche(t, 0.52, 0.02) - 0.3 * d)
    return p


_PIED_X = {"g": 0.032, "d": -0.028}
_PIED_Z = {"g": 0.026, "d": 0.0125}               # la cheville posée : le bout du boudin gauche est plus long sous elle
_FOULEE = 0.07                                    # la cheville posée glisse de 7 cm vers l'arrière, puis 7 de plus


def _pas(p, c, t, envol, rot, pos):
    """La patte c pendant la marche : elle quitte le sol à « envol » (fraction du cycle), reste en l'air 0,45 du cycle
    (le genou monte, la patte se replie haut sous le ventre comme au repos, puis se déplie loin devant), et porte le
    corps le reste du temps, la cheville glissant d'avant en arrière."""
    hanche = _porte(rot, pos, _REPOS[c][0])
    x, y0, z0 = _PIED_X[c], 0.034, _PIED_Z[c]
    arriere, devant = np.array([x, y0 + _FOULEE, z0]), np.array([x, y0 - _FOULEE, z0])

    def tendue(ch):
        return (hanche + ch) / 2 + np.array([0.0, 0.040, 0.0])
    u = (t - envol) % 1.0
    if u >= 0.45:
        ch = devant + (arriere - devant) * (u - 0.45) / 0.55
        _jambe(p, c, hanche, tendue(ch), ch, 0.0)
        return
    cles = [(0.0, tendue(arriere), arriere, 0.0),
            (0.40, hanche + np.array([0.0, 0.100, -0.190]), np.array([x, hanche[1] - 0.030, hanche[2] - 0.270]), 45.0),
            (0.75, hanche + np.array([0.0, -0.200, -0.220]), np.array([x, y0 - _FOULEE - 0.03, 0.100]), 25.0),
            (1.0, tendue(devant), devant, 0.0)]
    v = u / 0.45
    i = max(k for k in range(3) if cles[k][0] <= v)
    a, b = cles[i], cles[i + 1]
    k = float(_marche((v - a[0]) / (b[0] - a[0])))
    _jambe(p, c, hanche, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k, a[3] + (b[3] - a[3]) * k)


def avance(t):
    """La marche lente du pêcheur : il lève chaque patte très haut, la replie sous le ventre, la déplie loin devant et
    la pose avec précaution ; le corps se balance sur la patte d'appui, le cou pousse la tête en avant à chaque pas,
    puis la retient."""
    p = Pose()
    c2 = math.cos(math.tau * t)
    rot, pos = (2.0 * onde(t, 2, 0.21), -2.5 * c2, 0.0), (-0.012 * c2, 0.0, 0.006 * onde(t, 2, 0.21))
    p.add("corps", rot=rot, pos=pos)
    _pas(p, "g", t, 0.80, rot, pos)
    _pas(p, "d", t, 0.30, rot, pos)
    pousse = onde(t, 2, 0.05)
    p.add("cou1", rot=(3 + 5 * pousse, 0, 0))
    p.add("cou3", rot=(-3 * pousse, 0, 0))
    p.add("tete", rot=(-2 * pousse, 2.5 * c2, 0))
    p.paire("aile", rot=(2 * onde(t, 2), 0, 0))
    return p


_AFFUT = (25.0, 20.0, 50.0, -30.0, -10.0)          # penché, le cou tendu en avant, le bec vers l'eau : (corps, cou1, cou2, cou3, tete)
_FRAPPE = (45.0, 45.0, 105.0, -60.0, -40.0)         # le coup de bec : la pointe au ras du sol, devant la patte


def mange(t):
    """La pêche : il se penche lentement à l'affût, le cou tendu au-dessus de l'eau, se fige... et frappe d'un coup
    de bec jusqu'au sol ; il remonte sa prise, la tête en arrière, et l'avale en deux déglutitions, puis se redresse."""
    p = Pose()
    affut = borne((t - 0.04) / 0.26) if t < 0.62 else 1.0 - borne((t - 0.62) / 0.22)
    affut = affut * affut * (3 - 2 * affut)
    frappe = borne((t - 0.45) / 0.05) if t < 0.56 else 1.0 - borne((t - 0.56) / 0.10)
    frappe = frappe * frappe * (3 - 2 * frappe)
    avale = cloche(t, 0.76, 0.12)
    gorgee = (cloche(t, 0.72, 0.03) + cloche(t, 0.80, 0.03)) * avale
    tilt, c1, c2, c3, tt = (a * affut + (b - a) * frappe for a, b in zip(_AFFUT, _FRAPPE))
    rot = (tilt - 4 * avale, 0, 0)
    _corps(p, rot=rot)
    _plante(p, rot=rot)
    p.add("cou1", rot=(c1 - 4 * avale, 0, 0))
    p.add("cou2", rot=(c2 - 6 * gorgee, 0, 0))
    p.add("cou3", rot=(c3 + 8 * gorgee, 0, 0))
    p.add("tete", rot=(tt - 30 * avale, 0, 0))
    p.paire("aile", rot=(0, -3 * frappe, 0))
    p.ouvert = borne(1 - cloche(t, 0.53, 0.03) - cloche(t, 0.92, 0.02))
    return p


def joie(t):
    """Sa fête à lui, rare et solennelle : il ploie sur son échasse, bondit tout droit en ouvrant grand les ailes, le
    cou tendu et le bec au ciel, bat deux fois des ailes en retombant, les replie et reprend sa pose de statue."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.10, False) + 0.6 * cloche(t, 0.55, 0.08, False)       # il ploie avant le saut, et en se recevant
    vol = math.sin(math.pi * borne((t - 0.20) / 0.30))                                 # en l'air de 0,20 à 0,50
    ailes = math.sin(math.pi * borne((t - 0.08) / 0.78))
    bat = onde(t - 0.08, 2.5) * ailes
    cou = math.sin(math.pi * borne((t - 0.10) / 0.75))
    rot, pos = (8 * tasse - 6 * vol, 0, 0), (0, 0, -0.035 * tasse + 0.090 * vol)
    _corps(p, rot=rot, pos=pos)
    h, g, c = _REPOS["d"]
    hanche = _porte(rot, pos, h)
    cheville = c + np.array([0.0, 0.0, max(0.0, pos[2]) * 0.8])
    _jambe(p, "d", hanche, (hanche + cheville) / 2 + np.array([0.0, 0.040 - 0.05 * tasse, 0.0]), cheville, 30 * vol)
    p.add("cou1", rot=(-40 * cou, 0, 0))
    p.add("cou2", rot=(60 * cou, 0, 0))
    p.add("cou3", rot=(-10 * cou, 0, 0))
    p.add("tete", rot=(-45 * cou, 0, 0))
    p.add("aile_G", rot=(10 * ailes, -55 * ailes - 20 * bat, -45 * ailes), pos=(-0.010 * ailes, 0, 0))
    p.add("aile_D", rot=(10 * ailes, 55 * ailes + 20 * bat, 45 * ailes), pos=(0.010 * ailes, 0, 0))
    p.ouvert = borne(1 - 0.3 * vol)
    return p


def dort(t):
    """Il dort debout sur son échasse, la patte gauche repliée : le cou rentré entre les épaules, la tête posée
    dessus, le bec couché sur le jabot ; il gonfle un peu ses plumes et respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    _corps(p, rot=(3 + 1.0 * r, 0, 0), ech=(1.04 + 0.010 * r, 1.03, 1.0 + 0.014 * r))
    _plante(p, rot=(3 + 1.0 * r, 0, 0))
    p.add("cou1", rot=(-20, 0, 0))
    p.add("cou2", rot=(-60, 0, 0))
    p.add("cou3", rot=(80, 0, 0))
    p.add("tete", rot=(30 + 2 * r, 0, 0))
    p.paire("aile", rot=(0, -3, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Héron")
