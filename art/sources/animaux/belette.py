"""La belette en peluche : le dos brun cannelle, tout le dessous blanc pur du menton au ventre, d'une ligne franche
soulignée par sa couture. Une tueuse minuscule et culottée : dressée en chandelle sur ses pattes arrière, le corps
interminable tordu en S, les petites mains gantées de blanc pendues devant elle, la tête plate penchée sur l'épaule,
le menton levé, deux yeux noirs sous un sourcil froncé : elle nous jauge.

    python belette.py        fabrique la fiche art/apercus/animaux/belette.png
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

CANNELLE = M.hexa("#9d5f36")                  # le dos (le poil le rougit : il faut le prendre plus brun que nature)
BIAIS = math.radians(0)                       # pour la fiche : -24 (posée de biais, le ventre un peu vers sa droite, on lit mieux le S) ; 0 pour le jeu
AVANT = Vector((math.sin(BIAIS), -math.cos(BIAIS), 0.0))         # là où regarde son ventre
FLANC = np.array([math.cos(BIAIS), math.sin(BIAIS), 0.0])        # son côté gauche
ASSISE = Vector((0.030, 0.030, 0.0))
# le corps et le cou, d'un seul trait : chaque point (ce qu'il avance, ce qu'il monte). La croupe au sol, le ventre en
# avant, les épaules en arrière, la tête de nouveau en avant : un S.
S = [(-0.062, 0.040), (-0.020, 0.046), (0.030, 0.082), (0.058, 0.150), (0.040, 0.220), (0.000, 0.272), (-0.018, 0.322),
     (-0.004, 0.368), (0.022, 0.398)]
PARTS = [0.03, 0.12, 0.30, 0.50, 0.68, 0.80, 0.92, 0.985]
RAYONS = [0.030, 0.042, 0.037, 0.031, 0.032, 0.027, 0.024, 0.021]


class Fil:
    """Un chemin lissé, tenu dans un plan debout : de quoi coucher une pièce tournée le long d'un corps en S."""

    def __init__(self, points, flanc, pas=8):
        self.p = A.courbe(points, pas)
        self.fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(self.p, axis=0), axis=1))])
        self.sens = np.gradient(self.p, self.fait, axis=0)
        self.long = float(self.fait[-1])
        self.flanc = np.asarray(flanc, float)

    def cadre(self, s):
        """À s mètres du départ : le centre du fil, la direction où il va, et son dos."""
        centre = np.stack([np.interp(s, self.fait, self.p[:, k]) for k in range(3)], axis=-1)
        avant = np.stack([np.interp(s, self.fait, self.sens[:, k]) for k in range(3)], axis=-1)
        avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
        return centre, avant, np.cross(avant, self.flanc)

    def couche(self, v):
        """Couche une pièce tournée toute droite (son axe Z) le long du fil : son +X devient le flanc gauche, son +Y le dos."""
        s = np.clip(v[:, 2], 0.0, self.long)
        centre, avant, dos = self.cadre(s)
        return centre + avant * (v[:, 2] - s)[:, None] + v[:, 0:1] * self.flanc + v[:, 1:2] * dos


def troncons(tube, cotes, paliers):
    """Peint un tube par tronçons le long de son chemin : [(0.6, CANNELLE), (9, K.BLANC)] -> cannelle jusqu'à 60 % du
    chemin, blanc au-delà. À poser ensuite avec couleur=None."""
    n = (len(tube.v) - 2) // cotes
    t = np.minimum(np.arange(len(tube.v)) // cotes, n - 1) / (n - 1)
    t[-2], t[-1] = 0.0, 1.0                               # les deux bouchons du tube
    teinte = np.tile(np.asarray(paliers[-1][1], float), (len(tube.v), 1))
    for seuil, couleur in reversed(paliers):
        teinte[t <= seuil] = couleur
    tube.teinte = teinte
    return tube


def construire():
    a = K.Animal("belette")
    a.taille = 0.42
    fil = Fil([tuple(ASSISE + AVANT * u + Vector((0, 0, z))) for u, z in S], FLANC)
    L = fil.long

    # ----- le corps et le cou : une seule chaussette couchée le long du S. Le ventre (le côté 36) est peint en blanc
    #       sur dix-sept côtés, du bas jusqu'à la gorge : la limite suit les mailles, elle sort nette dans le poil. -----
    corps = A.tour(A.profil([(0, 0)] + [(r, p * L) for r, p in zip(RAYONS, PARTS)] + [(0, 1.01 * L)], 6), 48)
    teinte = np.tile(np.asarray(CANNELLE, float), (len(corps.v), 1))
    for anneau in corps.anneaux:
        for j, k in enumerate(anneau):
            if len(anneau) > 1 and abs(j - 36) <= 8 and corps.v[k, 2] > 0.035 * L:
                teinte[k] = K.BLANC
    corps.teinte = teinte
    G.sillons(corps, [27, 45], 0.0025, 1.0)             # les deux coutures du plastron creusent un peu le tissu
    a.piece("corps", corps.sculpte(fil.couche), None)
    a.couture("plastron_G", "corps", 45, 0.10, 0.93, fil=K.CHOCOLAT, large=0.006, haut=0.003, pas=0.011)
    a.couture("plastron_D", "corps", 27, 0.10, 0.93, fil=K.CHOCOLAT, large=0.006, haut=0.003, pas=0.011)
    a.couture("dos", "corps", 12, 0.16, 0.90, "droit", fil=K.CHOCOLAT, large=0.006, haut=0.003, pas=0.011)

    # ----- la tête : petite, plate, en coin ; le dessus cannelle, tout le dessous blanc. Penchée sur l'épaule gauche,
    #       tournée vers nous, le menton levé. Dans son repère : X la gauche, -Y le nez, Z le dessus. -----
    bout, monte, dos = fil.cadre(L)
    H = A.repere(Vector(bout) + AVANT * 0.021 + Vector((0, 0, 0.014)), (-7, 19, math.degrees(BIAIS) + 46))
    H3 = H.to_3x3()
    a.tete = H @ Vector((0, -0.045, 0.004))

    def coin(v):
        s = v.copy()
        nez = K.lisse((-v[:, 1] - 0.05) / 0.95)
        s[:, 0] *= 1 - 0.62 * nez
        s[:, 2] *= (1 - 0.52 * nez) * np.where(v[:, 2] > 0, 0.80, 1.0)
        return s
    tete = A.boule(1.0, 48, 24)
    K.bandes(tete, [(-0.14, K.BLANC), (9, CANNELLE)])
    a.piece("tete", tete.sculpte(coin).etire(0.047, 0.071, 0.034), None, mat=H)
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.0090, 0.0072, 0.0068), K.ROSE, mat=H @ A.repere((0, -0.0705, 0.0010)), poil=False)

    # ----- les yeux : deux boutons noirs rapprochés, juste au-dessus de la ligne blanche ; un sourcil brodé plonge vers le nez -----
    centre = H @ Vector((0, 0, 0))
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", centre, H3 @ Vector((0.44 * c, -0.80, 0.33)))
        a.bouton("oeil_" + nom, p + n * 0.001, n, 0.0135)
        sourcil = a.trace("tete", centre, [H3 @ Vector(d) for d in ((0.80 * c, -0.44, 0.66), (0.52 * c, -0.72, 0.66), (0.20 * c, -0.92, 0.50))], 0.0035)
        a.broderie("sourcil_" + nom, A.courbe(sourcil, 5), 0.0032, K.CHOCOLAT)

    # ----- les oreilles : deux petits ronds plaqués bas sur les côtés du crâne, le dedans chocolat -----
    for nom, c in (("G", 1), ("D", -1)):
        vers = (H3 @ Vector((0.86 * c, 0.44, 0.30))).normalized()
        p, n = a.surface("tete", centre, vers)
        E = A.cadre(p + vers * 0.005, H3 @ Vector((0.55 * c, -0.82, 0.15)), vers)       # Z regarde devant, Y part du crâne
        a.piece("oreille_" + nom, A.boule(1.0, 24, 12).etire(0.0140, 0.0135, 0.0060), CANNELLE, mat=E)
        a.piece("pavillon_" + nom, A.boule(1.0, 20, 10).etire(0.0082, 0.0080, 0.0038).pose((0, 0.001, 0.0044)), K.CHOCOLAT, mat=E, poil=False)

    # ----- les cuisses et les longs pieds blancs : elle est assise dessus, les pieds en canard -----
    for nom, c in (("G", 1), ("D", -1)):
        hanche = ASSISE + AVANT * 0.004 + Vector(FLANC * (0.037 * c)) + Vector((0, 0, 0.047))
        a.piece("cuisse_" + nom, A.boule(1.0, 28, 14).etire(0.021, 0.044, 0.032), CANNELLE,
                mat=A.repere(hanche, (-32, 0, math.degrees(BIAIS) + 8 * c)))
        pied = ASSISE + AVANT * 0.046 + Vector(FLANC * (0.050 * c)) + Vector((0, 0, 0.0095))
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.0135, 0.034, 0.0095), K.BLANC,
                mat=A.repere(pied, (0, 0, math.degrees(BIAIS) + 20 * c)))

    # ----- les petits bras : pendus devant la poitrine, la main blanche ; la gauche plus haute que la droite -----
    for nom, c, s, leve in (("G", 1, 0.735, 0.012), ("D", -1, 0.715, 0.0)):
        epaule, monte, dos = fil.cadre(s * L)
        devant, cote, haut = -dos, FLANC * c, np.array([0.0, 0.0, 1.0])
        racine = epaule + cote * 0.022 + devant * 0.006
        bras = [racine, racine + cote * 0.010 + devant * 0.024 - haut * (0.018 - leve), racine + cote * 0.002 + devant * 0.046 - haut * (0.030 - 2 * leve),
                racine - cote * 0.004 + devant * 0.052 - haut * (0.052 - 2 * leve)]
        tube = A.tube(A.courbe(bras, 6), lambda t: float(np.interp(t, [0, 0.5, 0.85, 1], [0.0125, 0.0105, 0.0110, 0.0085])), 14)
        a.piece("bras_" + nom, troncons(tube, 14, [(0.62, CANNELLE), (9, K.BLANC)]), None)

    # ----- la queue : un long fouet cannelle couché dans l'herbe, qui revient vers nous en crosse -----
    queue = [(-0.060, 0.000, 0.034), (-0.105, 0.004, 0.020), (-0.150, 0.030, 0.016), (-0.168, 0.078, 0.016), (-0.150, 0.126, 0.018), (-0.112, 0.150, 0.024)]
    queue = [tuple(ASSISE + AVANT * u + Vector(FLANC * f) + Vector((0, 0, z))) for u, f, z in queue]
    a.piece("queue", A.tube(A.courbe(queue, 8), lambda t: float(np.interp(t, [0, 0.2, 0.8, 1], [0.016, 0.0125, 0.0150, 0.0100])), 14), CANNELLE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py belette)

from poses import Pose, borne, cloche, onde

# Le corps et le cou sont une seule chaussette couchée le long du S : une pièce souple que six os se partagent le long
# du fil (corps à la croupe, reins dans le ventre, dos, épaules, cou, tete au bout du cou). Elle est assise à x = 0,03 :
# le miroir automatique des os ne tombe pas juste, les os des bras et des pattes sont donc nommés à la main, en minuscules.
_FIL = Fil([tuple(ASSISE + AVANT * u + Vector((0, 0, z))) for u, z in S], FLANC)
_JALONS = (("corps", 0.0), ("reins", 0.30), ("dos", 0.55), ("epaules", 0.68), ("cou", 0.86), ("tete", 0.97))
_QUEUE = Fil([tuple(ASSISE + AVANT * u + Vector(FLANC * f) + Vector((0, 0, z))) for u, f, z in
              ((-0.060, 0.000, 0.034), (-0.105, 0.004, 0.020), (-0.150, 0.030, 0.016), (-0.168, 0.078, 0.016), (-0.150, 0.126, 0.018), (-0.112, 0.150, 0.024))],
             (0, 0, 1), 8)
_JALONS_QUEUE = (("queue1", 0.0), ("queue2", 0.35), ("queue3", 0.70))


def _au_fil(fil, f):
    """Le centre du fil à la fraction f de sa longueur : le pivot d'un os."""
    return tuple(round(float(x), 4) for x in fil.cadre(f * fil.long)[0])


def _abscisse(points, fil):
    """Pour chaque point : sa place le long du fil (de 0 à 1), au pied de la perpendiculaire sur le tronçon le plus proche."""
    a, ab = fil.p[:-1], np.diff(fil.p, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    ap = points[:, None, :] - a[None, :, :]
    u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
    j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
    return (fil.fait[j] + u[np.arange(len(points)), j] * np.sqrt(l2[j])) / fil.long


def _relais(f, jalons, large):
    """Des os qui se passent la main le long d'un fil : chacun porte le tronçon qui suit son pivot, et cède au suivant
    en douceur sur ± large autour du pivot de celui-ci."""
    def marche(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3 - 2 * x)
    montees = [np.ones_like(f)] + [marche((f - f0 + large) / (2 * large)) for _o, f0 in jalons[1:]] + [np.zeros_like(f)]
    return {o: montees[i] - montees[i + 1] for i, (o, _f0) in enumerate(jalons)}


def _echine(points, cote):
    return _relais(_abscisse(points, _FIL), _JALONS, 0.05)


def _queue(points, cote):
    return _relais(_abscisse(points, _QUEUE), _JALONS_QUEUE, 0.08)


def _cote(os_):
    """Une pièce d'un côté (bras_G, cuisse_D...) portée tout entière par l'os de son côté : bras_g, cuisse_d..."""
    return lambda points, cote: {os_ + "_" + cote[1:].lower(): np.ones(len(points))}


OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.03, 0.03, 0.05)),          # les hanches, entre les cuisses : elle se dresse et se couche autour
    ("reins", "corps", _au_fil(_FIL, 0.30)),          # dans le ventre
    ("dos", "reins", _au_fil(_FIL, 0.55)),
    ("epaules", "dos", _au_fil(_FIL, 0.68)),          # entre les deux bras
    ("cou", "epaules", _au_fil(_FIL, 0.86)),
    ("tete", "cou", _au_fil(_FIL, 0.97)),             # la nuque
    ("bras_g", "epaules", (0.052, 0.0337, 0.2923)),   # les épaules
    ("bras_d", "epaules", (0.008, 0.0298, 0.2843)),
    ("cuisse_g", "racine", (0.067, 0.026, 0.047)),    # les hanches : les pattes arrière pendent à la racine, posées au sol
    ("cuisse_d", "racine", (-0.007, 0.026, 0.047)),
    ("queue1", "corps", _au_fil(_QUEUE, 0.0)),        # la queue : trois os, du croupion au bout
    ("queue2", "queue1", _au_fil(_QUEUE, 0.35)),
    ("queue3", "queue2", _au_fil(_QUEUE, 0.70)),
]
PORTEURS = [("corps", _echine, "corps"), ("plastron", _echine, "corps"), ("dos", _echine, "corps"),
            ("tete", "tete"), ("nez", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("oreille", "tete"), ("pavillon", "tete"),
            ("bras", _cote("bras"), "corps"), ("cuisse", _cote("cuisse"), "corps"), ("pied", _cote("cuisse"), "corps"),
            ("queue", _queue, "queue1"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


_CHAINE = ("corps", "reins", "dos", "epaules", "cou")


def _rot(r):
    """La matrice d'une rotation de Pose (degrés ; X, puis Y, puis Z, autour des axes du monde)."""
    x, y, z = (math.radians(a) for a in r)
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    return (np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
            @ np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]))


def _angles(m):
    """Les angles de Pose d'une matrice de rotation (l'inverse de _rot)."""
    y = math.asin(-max(-1.0, min(1.0, m[2, 0])))
    return math.degrees(math.atan2(m[2, 1], m[2, 2])), math.degrees(y), math.degrees(math.atan2(m[1, 0], m[0, 0]))


def _tete_vers(p, monde):
    """Tourne la tête pour qu'elle ait, dans le jardin, l'orientation « monde » (des angles de Pose) quelle que soit la
    pose de l'échine : (0, 0, -46) la remet droit devant, à niveau (au repos, elle regarde à 46° sur sa gauche)."""
    m = np.eye(3)
    for o in _CHAINE:
        if o in p.os:
            m = m @ _rot(p.os[o]["rot"])
    p.add("tete", rot=_angles(m.T @ _rot(monde)))


def _a_quatre(p, k, vague=0.0, phase=0.0):
    """Couchée à quatre pattes, à la fraction k (0 : dressée, 1 : à plat) : le corps bascule en avant sur les hanches,
    l'échine se déroule à l'horizontale et monte en voûte au milieu ; « vague » fait onduler l'échine (en degrés) : chaque
    tronçon penche de « vague » au plus, la vague partant de la croupe à « phase » et courant vers la nuque."""
    penche = [vague * math.sin(math.tau * (phase - 0.18 * i)) for i in range(5)]
    tourne = [b - a for a, b in zip([0.0] + penche[:-1], penche)]       # chaque os ne tourne que de l'écart avec son voisin
    for nom, base, d in zip(_CHAINE, (45, 38, 30, -22, -60), tourne):
        p.add(nom, rot=(base * k + d, 0, 0))
    p.add("queue1", rot=(-48 * k, 0, 0))


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def repos(t):
    """Dressée en chandelle, elle guette : elle respire, se hisse encore plus haut, tourne la tête par petits à-coups
    (devant, à gauche, à droite), les mains pendues qui tressaillent ; la queue fouette l'herbe ; elle cligne."""
    p = Pose()
    r = onde(t, 2)
    hisse = cloche(t, 0.45, 0.20)
    p.add("corps", rot=(-3 * hisse, 0, 0), ech=(1 + 0.012 * r, 1 + 0.012 * r, 1))
    p.add("reins", rot=(-6 * hisse, 0, 0))
    p.add("dos", rot=(4 * hisse, 0, 0))
    p.add("epaules", rot=(2 * r, 0, 0))
    p.add("tete", rot=(-2 * r, 0, -46 * _plateau(t, 0.25, 0.06, 0.02) + 22 * _plateau(t, 0.50, 0.05, 0.02) - 70 * _plateau(t, 0.72, 0.06, 0.02)))
    p.add("bras_g", rot=(8 * cloche(t, 0.60, 0.04), 0, 0))
    p.add("bras_d", rot=(8 * cloche(t, 0.64, 0.04), 0, 0))
    p.add("queue1", rot=(3 * hisse, 0, 0))                  # la queue reste couchée dans l'herbe quand le corps se hisse
    p.add("queue2", rot=(0, 0, 12 * onde(t, 1)))
    p.add("queue3", rot=(0, 0, 18 * onde(t, 1, -0.15) + 20 * cloche(t, 0.88, 0.05) * onde(t, 12)))
    p.ouvert = borne(1 - cloche(t, 0.10, 0.02) - cloche(t, 0.62, 0.02))
    return p


def avance(t):
    """Elle file à quatre pattes, au ras de l'herbe, par bonds souples : l'échine ondule de la croupe à la nuque,
    les mains se tendent devant pendant que les pattes arrière poussent, puis l'inverse ; la tête reste à niveau,
    droit devant ; la queue suit en serpentant."""
    p = Pose()
    s, c = math.sin(math.tau * t), math.cos(math.tau * t)
    saut = 0.016 * max(0.0, s)
    _a_quatre(p, 1.0, vague=8.0, phase=t)
    p.add("corps", pos=(0, 0, 0.006 + saut), rot=(0, 2 * c, 3 * s))
    p.add("bras_g", rot=(-36 + 26 * c, 0, 0))
    p.add("bras_d", rot=(-36 + 24 * math.cos(math.tau * (t - 0.06)), 0, 0))
    for nom, retard in (("cuisse_g", 0.0), ("cuisse_d", 0.05)):
        k = math.cos(math.tau * (t - retard))
        p.add(nom, rot=(-14 - 14 * k, 0, 0), pos=(0, 0, 0.006 + saut + 0.008 * max(0.0, k)))
    _tete_vers(p, (-4 * onde(t, 1, 0.1), 0, -46))
    p.add("queue1", rot=(6 * s, 0, 10 * onde(t, 1, -0.15)))
    p.add("queue2", rot=(0, 0, 16 * onde(t, 1, -0.30)))
    p.add("queue3", rot=(0, 0, 20 * onde(t, 1, -0.45)))
    return p


_HANCHES = np.array((0.03, 0.03, 0.05))
_CUISSES = {"cuisse_g": np.array((0.067, 0.026, 0.047)), "cuisse_d": np.array((-0.007, 0.026, 0.047))}


def _cuisses_suivent(p, rot, pos):
    """Les pattes arrière pendent à la racine : quand tout le corps saute ou pivote, elles suivent le même mouvement
    (autour des hanches)."""
    m = _rot(rot)
    for nom, h in _CUISSES.items():
        p.add(nom, rot=rot, pos=tuple(_HANCHES + np.asarray(pos, float) + m @ (h - _HANCHES) - h))


def mange(t):
    """Elle se laisse couler à quatre pattes, le museau dans l'herbe, mord cinq fois à petits coups secs, puis se
    redresse en chandelle pour mâcher en surveillant les alentours."""
    p = Pose()
    bas = _plateau(t, 0.40, 0.25, 0.14)
    coups = max(0.0, onde(t, 6)) ** 2 * _plateau(t, 0.40, 0.22, 0.04)
    _a_quatre(p, bas)
    p.add("cou", rot=(28 * bas, 0, 0))
    mache = cloche(t, 0.86, 0.10)
    _tete_vers(p, (38 * bas + 12 * coups + 4 * mache * onde(t, 10), 0, -46 * bas - 30 * cloche(t, 0.92, 0.05)))
    p.add("bras_g", rot=(-36 * bas, 0, 0))
    p.add("bras_d", rot=(-36 * bas, 0, 0))
    p.add("queue2", rot=(0, 0, 10 * onde(t, 2)))
    p.add("queue3", rot=(0, 0, 14 * onde(t, 2, -0.1)))
    p.ouvert = borne(1 - 0.5 * coups - cloche(t, 0.80, 0.02))
    return p


def joie(t):
    """La danse de guerre : elle se tasse, bondit en se tordant vers la gauche, retombe, rebondit en se tordant vers la
    droite, la queue fouettant l'air, puis se redresse dans sa pose de guet."""
    p = repos(0.0)
    tasse = cloche(t, 0.08, 0.08, False) + 0.6 * cloche(t, 0.42, 0.05, False)
    b1 = math.sin(math.pi * borne((t - 0.12) / 0.28))           # premier bond de 0,12 à 0,40
    b2 = math.sin(math.pi * borne((t - 0.45) / 0.26))           # second de 0,45 à 0,71
    fin = cloche(t, 0.84, 0.12, False)                           # elle se redresse fièrement avant de se figer
    rot = (6 * tasse - 8 * (b1 + b2), 0, 55 * b1 - 45 * b2)
    pos = (0, 0, -0.012 * tasse + 0.10 * b1 + 0.07 * b2)
    p.add("corps", rot=rot, pos=pos)
    _cuisses_suivent(p, rot, (0, 0, max(0.0, pos[2])))          # les pieds ne s'enfoncent pas quand elle se tasse
    p.add("reins", rot=(10 * tasse, 18 * b1 - 16 * b2, 0))
    p.add("dos", rot=(-6 * (b1 + b2), 16 * b1 - 14 * b2, 0))
    p.add("epaules", rot=(-4 * fin, 10 * b1 - 10 * b2, 0))
    p.add("tete", rot=(-10 * (b1 + b2) - 8 * fin, 0, -30 * b1 + 40 * b2))
    p.add("bras_g", rot=(-40 * (b1 + b2), 0, 0))
    p.add("bras_d", rot=(-46 * (b1 + b2), 0, 0))
    fouet = onde(t, 4) * math.sin(math.pi * borne(t / 0.8))
    p.add("queue1", rot=(25 * (b1 + b2), 0, 25 * fouet))
    p.add("queue2", rot=(0, 0, 30 * fouet))
    p.add("queue3", rot=(0, 0, 35 * onde(t, 4, -0.1) * math.sin(math.pi * borne(t / 0.8))))
    return p


def dort(t):
    """Roulée en boule à même l'herbe : couchée de tout son long, l'échine enroulée sur sa gauche jusqu'à poser le
    menton sur ses hanches, les mains repliées sous elle, les yeux fermés ; elle respire lentement, le bout de la queue
    frémit une fois."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    _a_quatre(p, 1.0)
    p.add("corps", pos=(0, 0, 0.020), rot=(-8, 0, 0), ech=(1 + 0.015 * r, 1 + 0.015 * r, 1))
    for nom, rx in (("reins", 0), ("dos", -6), ("epaules", 8), ("cou", 6)):
        p.add(nom, rot=(rx, 62, 0))
    _tete_vers(p, (12, -10, 205))
    p.add("bras_g", rot=(40, 0, 0))
    p.add("bras_d", rot=(40, 0, 0))
    p.add("queue1", rot=(6, 0, 0))
    p.add("queue3", rot=(0, 0, 16 * cloche(t, 0.55, 0.04)))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Belette")
