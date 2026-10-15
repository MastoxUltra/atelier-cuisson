"""La martre en peluche : l'acrobate des branches. Un corps interminable en velours brun moka, arqué en pont comme
au milieu d'un bond, sur quatre pattes chocolat fines et longues ; une bavette ambre orangé, franche, qui part sous le
menton et s'arrête net au poitrail ; et derrière, un panache énorme qui file en arrière puis remonte en crosse, foncé
jusqu'au chocolat vers la pointe. Souple et maligne : la patte avant gauche levée en plein pas, la tête tournée vers
nous, penchée, les oreilles rondes bordées de crème, deux petits yeux rapprochés sous un sourcil levé et un sourire
en coin : elle sait déjà par où elle va filer.
Style du palier 3 (velours ras) : pas de couture, pas de rapiéçage, pas de bouton.

    python martre.py        fabrique la fiche art/apercus/animaux/martre.png (dans le style de son palier : voir styles.py)
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

MOKA = M.hexa("#93684d")                      # le corps : un brun moka (le poil le fonce et le dore)
CHOCOLAT = M.hexa("#4b3125")                  # les pattes, le bout du panache
AMBRE = M.hexa("#f2a23c")                     # l'accent : la bavette, ambre orangé
CREME = M.hexa("#f1e2c4")                     # le bord des oreilles
FIL_ = M.hexa("#3a261c")                      # le sourcil et le sourire, brodés
TOURNE = 0                                    # -30 la pose de trois quarts sur la fiche ; 0 pour le jeu

# L'échine, de la croupe au cou : arquée en pont, puis le cou qui se dresse d'un coup, comme au guet sur une branche.
ECHINE = [(0.0, 0.190, 0.105), (0.0, 0.110, 0.150), (0.0, 0.015, 0.164), (0.0, -0.075, 0.160), (0.0, -0.135, 0.190), (0.0, -0.160, 0.236)]
GALBE = [(0.0, 0.0), (0.03, 0.046), (0.12, 0.066), (0.35, 0.068), (0.60, 0.063), (0.80, 0.060), (0.92, 0.052), (0.98, 0.036), (1.0, 0.0)]
# Le panache : il sort de la croupe, file en arrière au ras du dos, puis remonte en crosse.
PANACHE = [(0.0, 0.170, 0.118), (0.0, 0.245, 0.110), (0.0, 0.330, 0.132), (0.0, 0.400, 0.192), (0.0, 0.425, 0.277),
           (0.0, 0.400, 0.347), (0.0, 0.345, 0.377)]
TOUFFE = [(0.0, 0.0), (0.02, 0.030), (0.10, 0.046), (0.30, 0.070), (0.52, 0.080), (0.70, 0.076), (0.84, 0.060), (0.94, 0.034), (1.0, 0.0)]
LACET, PIQUE, PENCHE = 12.0, -12.0, 16.0      # la tête : de trois quarts vers nous, le menton levé, penchée sur l'épaule


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


def patte(chemin, epais=0.021):
    """Une longue patte fine : moka en haut, chocolat dès le coude, un pied un peu plus large au bout."""
    return K.tube_peint(A.courbe(chemin, 6), lambda t: float(np.interp(t, [0, 0.35, 0.80, 1], [epais * 1.25, epais, epais * 0.80, epais * 0.92])),
                        [(0.22, MOKA), (9, CHOCOLAT)], 14)


def construire():
    a = K.Animal("martre")
    a.taille = 0.80

    # ----- le corps : une longue chaussette couchée le long de l'échine en pont. La bavette (le dessous du poitrail)
    #       est peinte en ambre sur les méridiens du bas : une limite franche -----
    fil = K.Fil(ECHINE, flanc=(1, 0, 0), pas=16)
    long = fil.long
    corps = A.tour(A.profil([(r, f * long) for f, r in GALBE], 8), 64)
    tour_ = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    bavette = table([(0.0, 9.0), (0.60, 9.0), (0.66, 2.20), (0.76, 1.70), (0.88, 1.40), (1.0, 1.35)], long)(corps.v[:, 2])
    corps.teinte = np.where((tour_ > bavette)[:, None], np.asarray(AMBRE), np.asarray(MOKA))

    def souple(v):                                        # un peu plus haut que large, le ventre rentré
        s = v.copy()
        s[:, 0] *= 0.92
        s[:, 1] *= np.where(v[:, 1] < 0, 0.86, 1.04)
        return s
    a.piece("corps", corps.sculpte(souple).sculpte(fil.couche), None)

    # ----- le panache : plus épais que le corps, aplati de côté pour qu'on le lise large de profil ; moka, puis chocolat
    #       sur le dernier tiers -----
    pfil = K.Fil(PANACHE, flanc=(1, 0, 0), pas=16)
    queue = A.tour(A.profil([(r, f * pfil.long) for f, r in TOUFFE], 8), 48)
    K.bandes(queue, [(0.62 * pfil.long, MOKA), (9, CHOCOLAT)])
    a.piece("queue", queue.sculpte(lambda v: v * [0.80, 1.15, 1.0]).sculpte(pfil.couche), None)

    # ----- la tête : un triangle au museau fin, le front large ; dans son repère, X la gauche, Y le dessus, Z vers la
    #       truffe. Le dessous, de la gorge au menton, prolonge la bavette -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0, 0, 0), nez) @ Matrix.Rotation(math.radians(PENCHE), 4, Vector((0, 0, 1)))
    cou = Vector(fil.cadre(long)[0])
    T = A.repere(cou - T.to_3x3() @ Vector((0, 0.004, 0.026))) @ T
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.012, 0.085))

    tete = A.tour(A.profil([(0, 0), (0.034, 0.006), (0.049, 0.024), (0.050, 0.042), (0.040, 0.066), (0.027, 0.092), (0.018, 0.118),
                            (0.011, 0.140), (0, 0.150)], 6), 56)
    tour_ = np.abs(np.arctan2(tete.v[:, 0], tete.v[:, 1]))
    gorge = table([(0.0, 1.50), (0.28, 1.62), (0.50, 1.95), (0.66, 2.40), (0.76, 9.0), (1.0, 9.0)], 0.150)(tete.v[:, 2])
    tete.teinte = np.where((tour_ > gorge)[:, None], np.asarray(AMBRE), np.asarray(MOKA))

    def fute(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 1] *= np.where(v[:, 1] > 0, 0.76, 0.78)
        s[:, 0] *= 1 + 0.16 * np.exp(-((z - 0.040) / 0.022) ** 2)       # les joues
        return s
    a.piece("tete", tete.sculpte(fute), None, mat=T)
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.0095, 0.0070, 0.0070), CHOCOLAT, mat=T @ A.repere((0, 0.003, 0.147)), poil=False)

    # ----- les yeux : petits et rapprochés, l'air malin ; un sourcil levé sur l'œil gauche, un sourire en coin -----
    centre = T @ Vector((0, 0, 0.060))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.46, 0.62, 0.50)))
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0072)
    leve = [T3 @ Vector((0.30 + 0.30 * u, 0.88 - 0.10 * u + 0.12 * math.sin(math.pi * u), 0.40 - 0.10 * u)) for u in np.linspace(0, 1, 6)]
    a.broderie("sourcil", A.courbe(a.trace("tete", centre, leve, 0.003), 4), 0.0022, FIL_)
    bouche = a.trace("tete", T @ Vector((0, 0, 0.090)), [T3 @ Vector(d) for d in ((0.10, -0.80, 0.60), (0.42, -0.80, 0.30), (0.66, -0.56, 0.10))], 0.003)
    a.broderie("bouche", A.courbe(bouche, 4), 0.0020, FIL_)

    # ----- les oreilles : rondes et larges, bien dressées, le bord crème et le dedans moka -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", T @ Vector((0, 0, 0.034)), T3 @ Vector((c * 0.74, 0.62, -0.10)))
        E = A.cadre(pos + n * 0.004, T3 @ Vector((c * 0.30, 0.10, 0.95)), n)
        a.piece("oreille_" + nom, A.boule(1.0, 28, 14).etire(0.016, 0.021, 0.007).pose((0, 0.010, 0)), CREME, mat=E)
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).etire(0.0105, 0.014, 0.004).pose((0, 0.009, 0.0035)), CHOCOLAT, mat=E, poil=False)

    # ----- les pattes : longues et fines ; les arrière sous les hanches, l'avant droite posée loin devant, la gauche levée
    #       en plein pas, le pied replié -----
    hanche = Vector(fil.cadre(0.14 * long)[0])
    for nom, c, pas in (("arriere_G", 1, 0.010), ("arriere_D", -1, -0.020)):
        h = hanche + Vector((c * 0.034, 0, -0.010))
        a.piece("cuisse_" + nom[-1], A.boule(1.0, 28, 14).etire(0.026, 0.050, 0.044), MOKA, mat=A.repere(h, (-30, 0, 0)))
        a.piece("patte_" + nom, patte([h, h + Vector((c * 0.010, 0.040, -0.060)), Vector((h.x + c * 0.008, h.y + 0.010 + pas, 0.034)),
                                       Vector((h.x + c * 0.008, h.y - 0.012 + pas, 0.018))], 0.019), None)
    epaule = Vector(fil.cadre(0.86 * long)[0])
    e = epaule + Vector((-0.030, 0, -0.016))
    a.piece("patte_avant_D", patte([e, e + Vector((-0.008, -0.030, -0.070)), Vector((e.x - 0.008, e.y - 0.050, 0.026)),
                                     Vector((e.x - 0.008, e.y - 0.068, 0.019))]), None)
    e = epaule + Vector((0.030, 0, -0.016))
    a.piece("patte_avant_G", patte([e, e + Vector((0.008, -0.036, -0.040)), e + Vector((0.010, -0.060, -0.052)),
                                     e + Vector((0.010, -0.068, -0.074))]), None)
    a.couleur_paupiere = MOKA
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py martre). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Le corps et le panache sont deux longues chaussettes couchées le long d'un fil : des pièces souples que des os se
# passent le long de leur fil. Elle est saisie en plein pas, la patte avant gauche levée : chaque patte a donc ses deux
# os à elle, à sa vraie place (pas de miroir), et ses pièces passent de l'os du haut à celui du bas au coude (ou au genou).

from poses import Pose, borne, cloche, onde

_ECHINE = K.Fil(ECHINE, flanc=(1, 0, 0), pas=16)
_PANACHE = K.Fil(PANACHE, flanc=(1, 0, 0), pas=16)
_JALONS = (("corps", 0.0), ("poitrail", 0.45), ("cou", 0.90))          # en fraction du fil de l'échine
_JALONS_QUEUE = (("queue", 0.0), ("queue2", 0.50))


def _point(v):
    return tuple(round(float(x), 4) for x in v)


def _au_fil(fil, f):
    """Le centre du fil à la fraction f de sa longueur : le pivot d'un os."""
    return _point(fil.cadre(f * fil.long)[0])


# les quatre pattes, comme dans construire() : la hanche (ou l'épaule), le genou (ou le coude), le pied, l'orteil
_H = Vector(_ECHINE.cadre(0.14 * _ECHINE.long)[0])
_E = Vector(_ECHINE.cadre(0.86 * _ECHINE.long)[0])
_PATTES = {}
for _n, _c, _pas in (("ar_g", 1, 0.010), ("ar_d", -1, -0.020)):
    _h = _H + Vector((_c * 0.034, 0, -0.010))
    _PATTES[_n] = [_h, _h + Vector((_c * 0.010, 0.040, -0.060)), Vector((_h.x + _c * 0.008, _h.y + 0.010 + _pas, 0.034)),
                   Vector((_h.x + _c * 0.008, _h.y - 0.012 + _pas, 0.018))]
_e = _E + Vector((-0.030, 0, -0.016))
_PATTES["av_d"] = [_e, _e + Vector((-0.008, -0.030, -0.070)), Vector((_e.x - 0.008, _e.y - 0.050, 0.026)),
                   Vector((_e.x - 0.008, _e.y - 0.068, 0.019))]
_e = _E + Vector((0.030, 0, -0.016))
_PATTES["av_g"] = [_e, _e + Vector((0.008, -0.036, -0.040)), _e + Vector((0.010, -0.060, -0.052)), _e + Vector((0.010, -0.068, -0.074))]
_PATTES = {n: np.array([tuple(q) for q in ch]) for n, ch in _PATTES.items()}

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", _point(_H)),                   # les hanches : elle se cabre et se couche autour
    ("poitrail", "corps", _au_fil(_ECHINE, 0.45)),     # le milieu du pont : l'échine s'arque et se tord là
    ("cou", "poitrail", _au_fil(_ECHINE, 0.90)),       # le pied du cou, juste devant les épaules
    ("tete", "cou", _point(_ECHINE.cadre(_ECHINE.long)[0])),      # la nuque, au bout du cou
    ("queue", "corps", _au_fil(_PANACHE, 0.0)),        # la racine du panache
    ("queue2", "queue", _au_fil(_PANACHE, 0.50)),      # le haut de la crosse
]
for _n, _parent in (("ar_g", "corps"), ("ar_d", "corps"), ("av_g", "poitrail"), ("av_d", "poitrail")):
    OS += [(_n, _parent, _point(_PATTES[_n][0])), (_n + "2", _n, _point(_PATTES[_n][1]))]


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


def _relais(s, jalons, large):
    """Des os qui se passent la main le long d'un fil : chacun porte le tronçon qui suit son pivot, et cède au suivant
    en douceur sur ± large (en mètres) autour du pivot de celui-ci."""
    montees = [np.ones_like(s)] + [K.lisse((s - s0 + large) / (2 * large)) for _o, s0 in jalons[1:]] + [np.zeros_like(s)]
    return {o: montees[i] - montees[i + 1] for i, (o, _s0) in enumerate(jalons)}


def _echine(points, cote):
    return _relais(_abscisse(points, _ECHINE.p), [(o, f * _ECHINE.long) for o, f in _JALONS], 0.035)


def _queue(points, cote):
    return _relais(_abscisse(points, _PANACHE.p), [(o, f * _PANACHE.long) for o, f in _JALONS_QUEUE], 0.05)


def _patte(rang):
    """Une patte : l'os du haut jusqu'au genou (ou au coude), celui du bas après lui, fondus sur deux centimètres.
    L'usine retourne les pièces de droite en miroir avant de les donner : on les remet à leur place."""
    def poids(points, cote):
        n = rang + cote.lower()
        q = points * ([-1, 1, 1] if cote == "_D" else [1, 1, 1])
        ch = _PATTES[n]
        w = K.lisse((_abscisse(q, ch) - float(np.linalg.norm(ch[1] - ch[0])) + 0.010) / 0.020)
        return {n: 1.0 - w, n + "2": w}
    return poids


def _cuisse(points, cote):
    """La grosse cuisse, tout entière sur l'os du haut de sa patte arrière."""
    return {"ar" + cote.lower(): np.ones(len(points))}


PORTEURS = [("corps", _echine, "corps"), ("queue", _queue, "queue"),
            ("tete", "tete"), ("truffe", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("bouche", "tete"),
            ("oreille", "tete"), ("dedans", "tete"),
            ("cuisse", _cuisse), ("patte_arriere", _patte("ar")), ("patte_avant", _patte("av")),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _patte_posee(p, x):
    """La patte avant gauche, levée dans le modèle (x = 0), abaissée vers le sol (x = 1) : repliée au poignet, elle ne
    le touche jamais tout à fait, elle la porte."""
    p.add("av_g", rot=(40 * x, 0, 0))
    p.add("av_g2", rot=(-6 * x, 0, 0))


def _respire(p, r, k=1.0):
    """Le souffle : le ventre et le poitrail s'élargissent (en largeur seulement : les pattes, ses enfants, restent au sol)."""
    p.add("corps", ech=(1 + 0.014 * k * r, 1, 1))
    p.add("poitrail", ech=(1 + 0.016 * k * r, 1, 1))


def repos(t):
    """Au guet sur sa branche : elle respire, la patte avant toujours en l'air ; elle la pose, hésite, la relève
    (elle choisit par où filer) ; elle hume l'air le nez levé, jette un regard de côté puis revient vers nous, le
    panache qui ondule sans arrêt derrière elle ; elle cligne."""
    p = Pose()
    r = onde(t, 2)
    _respire(p, r)
    pose = cloche(t, 0.30, 0.10)
    _patte_posee(p, 0.8 * pose)
    p.add("poitrail", rot=(-2 * pose, 0, 0))
    hume = cloche(t, 0.55, 0.08)
    p.add("cou", rot=(-8 * hume, 0, 0))
    p.add("tete", rot=(-10 * hume + 4 * hume * onde(t, 12), 0, -28 * cloche(t, 0.75, 0.08) + 6 * cloche(t, 0.12, 0.06)))
    p.add("queue", rot=(2 * r, 0, 8 * onde(t, 1)))
    p.add("queue2", rot=(0, 0, 14 * onde(t, 1, -0.2)))
    p.ouvert = borne(1 - cloche(t, 0.45, 0.02) - cloche(t, 0.90, 0.02))
    return p


def avance(t):
    """Elle file par bonds, comme les martres : les pattes arrière poussent ensemble, l'échine se déroule, elle vole
    un instant, les pattes avant se tendent devant et se posent, puis l'arrière revient sous elle et le dos s'arque
    en pont ; le panache ondule derrière, la tête reste à niveau."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    vol = max(0.0, s)                                     # en l'air de 0 à 0,5
    p.add("corps", pos=(0, 0, 0.028 * vol), rot=(-6 * s, 0, 0))
    p.add("poitrail", rot=(8 * s, 0, 0))
    p.add("cou", rot=(-4 * s, 0, 0))
    p.add("tete", rot=(2 * s, 0, 0))
    for n, retard in (("ar_g", 0.0), ("ar_d", 0.04)):
        k = math.cos(math.tau * (t - retard))
        p.add(n, rot=(24 * k, 0, 0))                      # la poussée (le pied part en arrière), puis le retour sous elle
        p.add(n + "2", rot=(-16 * max(0.0, -k), 0, 0))
    _patte_posee(p, 1.0)
    for n, retard in (("av_g", 0.0), ("av_d", 0.05)):
        k = math.cos(math.tau * (t - retard))
        p.add(n, rot=(-18 * (1 + k), 0, 0))               # tendue devant en vol, ramenée à sa place à l'appui
        p.add(n + "2", rot=(-12 * max(0.0, k), 0, 0))
    p.add("queue", rot=(8 * s, 0, 0))
    p.add("queue2", rot=(-12 * math.sin(math.tau * (t - 0.15)), 0, 0))
    return p


def mange(t):
    """Elle plonge le museau entre ses pattes, fouille et croque à petits coups, puis se redresse d'un coup pour
    mâcher en surveillant, la tête tournée vers nous."""
    p = Pose()
    bas = cloche(t, 0.40, 0.32)
    coups = max(0.0, onde(t, 10)) ** 2 * cloche(t, 0.40, 0.26)
    _patte_posee(p, 1.0)
    p.add("poitrail", rot=(12 * bas, 0, 0))               # l'avant plonge : les pattes avant s'avancent pour tenir le sol
    p.add("av_g", rot=(-26 * bas, 0, 0))
    p.add("av_d", rot=(-38 * bas, 0, 0))
    p.add("cou", rot=(60 * bas, 0, 0))
    p.add("tete", rot=(30 * bas + 10 * coups, 0, -10 * bas))
    mache = cloche(t, 0.86, 0.10)
    p.add("tete", rot=(3 * mache * onde(t, 12), 0, 12 * mache))
    p.add("queue2", rot=(0, 0, 10 * onde(t, 2)))
    p.ouvert = borne(1 - 0.4 * coups - cloche(t, 0.80, 0.02))
    return p


def joie(t):
    """L'acrobatie : elle se ramasse, bondit en l'air en vrillant sur elle-même, le panache fouettant comme un
    balancier, retombe sur ses quatre pattes et reprend sa pose de guet, la patte levée."""
    p = repos(0.0)
    tasse = cloche(t, 0.10, 0.10, False)
    saut = math.sin(math.pi * borne((t - 0.18) / 0.50))           # en l'air de 0,18 à 0,68
    vrille = borne((t - 0.18) / 0.50)
    vrille = vrille * vrille * (3 - 2 * vrille)
    p.add("corps", pos=(0, 0, 0.16 * saut), rot=(-10 * saut, 0, 360 * vrille))
    p.add("poitrail", rot=(-14 * saut, 0, 0))
    p.add("cou", rot=(16 * tasse - 10 * saut, 0, 0))
    p.add("tete", rot=(-8 * saut, 0, 0))
    for n in ("ar_g", "ar_d"):
        p.add(n, rot=(30 * saut - 20 * tasse, 0, 0))
    for n in ("av_g", "av_d"):
        p.add(n, rot=(-36 * saut, 0, 0))
    fin = cloche(t, 0.80, 0.10, False)                                 # elle se pose et lève la tête, fière
    p.add("tete", rot=(-8 * fin, 0, 0))
    p.add("queue", rot=(-20 * saut, 0, 30 * saut * onde(t, 3)))
    p.add("queue2", rot=(0, 0, 35 * saut * onde(t, 3, -0.15)))
    return p


def dort(t):
    """Couchée sur le flanc gauche, de tout son long, les pattes allongées devant elle, la tête posée sur la joue,
    le panache étalé derrière son dos comme une couverture ; les yeux fermés, elle respire lentement, et le bout du
    panache frémit une fois."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.056), rot=(0, 80, 0))
    _respire(p, r, 1.6)
    _patte_posee(p, 0.6)
    for n, a in (("ar_g", 10), ("ar_d", -6), ("av_g", -14), ("av_d", -8)):
        p.add(n, rot=(a, 0, 0))
    p.add("cou", rot=(14 + 1.5 * r, 0, 0))
    p.add("tete", rot=(0, 10, 0))
    p.add("queue", rot=(0, 0, 10))
    p.add("queue2", rot=(0, 0, 10 + 14 * cloche(t, 0.60, 0.05)))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("martre", styles.style_de("martre"), sys.modules[__name__]), "Martre")
