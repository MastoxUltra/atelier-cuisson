"""Le poisson rouge en peluche, deuxième dessin : la diva du bocal, échouée dans l'herbe comme sur un sofa. Un ryukin :
un œuf de velours orange vif, court et profond, une bosse haute derrière la tête, le dos vermillon, le ventre pêche ; une
haute dorsale de feutrine dorée qui retombe d'un côté, lasse. Couchée sur le ventre et roulée sur le flanc, elle étale
derrière elle sa queue double, deux grands voiles d'or plissés qui traînent dans l'herbe comme la traîne d'une robe du
soir. Les yeux globuleux à moitié voilés de paupières lourdes, la bouche en cul-de-poule tendue vers vous : elle attend
qu'on la remette à l'eau, et qu'on s'excuse.

    python poisson_rouge.py        fabrique la fiche art/apercus/animaux/poisson_rouge.png
    (le premier dessin, jamais gardé : poisson_rouge_ancien.py)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import garnitures as G
import matieres as M
import peluche as K

ORANGE = M.hexa("#ff8a1c")                    # le velours : un orange vif (le poil le fonce en orange profond)
VERMILLON = M.hexa("#e8471f")                 # le dos, la bosse, les paupières, les écailles
PECHE = M.hexa("#ffd2a8")                     # le ventre, les lèvres
OR = M.hexa("#ffc23d")                        # l'accent : les voiles de feutrine dorée
OR_FONCE = M.hexa("#d98a1a")                  # les rayons brodés sur les voiles
TOURNE = 0                                    # -40 pour la fiche, posée de biais (on lit la bosse et la traîne) ; 0 pour le jeu
ROULE = math.radians(16)                      # elle roule sur son flanc droit : le gauche se tourne vers le ciel
# l'échine, de la queue au nez : couchée, le nez un peu relevé vers vous
DOS = K.Fil([(0.0, 0.088, 0.050), (0.0, 0.040, 0.055), (0.0, -0.010, 0.058), (0.004, -0.050, 0.064), (0.012, -0.080, 0.072)],
            flanc=(math.cos(ROULE), 0.0, math.sin(ROULE)))
GALBE = [(0, 0), (0.013, 0.004), (0.016, 0.020), (0.030, 0.040), (0.052, 0.070), (0.062, 0.100), (0.062, 0.122), (0.054, 0.144),
         (0.040, 0.160), (0.024, 0.170), (0, 0.176)]


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def robe(m):
    """Peint l'œuf (tourné tout droit, son +Y est le dos) : le dos et la bosse vermillon, les flancs orange, le ventre pêche."""
    rho = np.maximum(np.hypot(m.v[:, 0], m.v[:, 1]), 1e-9)
    haut = m.v[:, 1] / rho
    dos = 0.50 - 0.22 * np.exp(-((m.v[:, 2] - 0.118) / 0.030) ** 2)       # le vermillon descend plus bas sur la bosse
    m.teinte = np.where((haut > dos)[:, None], np.asarray(VERMILLON), np.where((haut < -0.50)[:, None], np.asarray(PECHE), np.asarray(ORANGE)))
    return m


def eventail(long, large):
    """Le contour d'un voile : étroit à la racine, il s'ouvre en éventail et son bord se fend en deux lobes ronds."""
    return A.courbe([(0.0, -0.010), (0.24 * long, -0.18 * large), (0.55 * long, -0.36 * large), (0.82 * long, -0.46 * large),
                     (1.00 * long, -0.36 * large), (0.86 * long, -0.06 * large), (0.94 * long, 0.18 * large), (0.98 * long, 0.42 * large),
                     (0.72 * long, 0.44 * large), (0.42 * long, 0.30 * large), (0.18 * long, 0.14 * large), (0.0, 0.010)], 6, fermee=True)


def hauteur(racine, x, y, monte, tombe):
    """La hauteur du voile à la distance x de sa racine : il monte, puis retombe, en faisant des plis."""
    return racine.z + monte * x - tombe * x * x + 0.0065 * np.sin(y * 60.0 + 0.6) * K.lisse((x - 0.02) / 0.07)


def voile(racine, sens, long, large, monte, tombe):
    """Un voile de feutrine dorée, déjà posé dans le jardin : il part de la racine vers « sens » (à plat), monte et
    retombe selon « monte » et « tombe », et ondule en plis."""
    m = A.decoupe(eventail(long, large), 0.0060, 0.0022)
    d = Vector(sens).normalized()
    t = Vector((-d.y, d.x, 0.0))
    x, y, z = m.v[:, 0].copy(), m.v[:, 1].copy(), m.v[:, 2].copy()
    m.v = np.stack([racine.x + d.x * x + t.x * y, racine.y + d.y * x + t.y * y, hauteur(racine, x, y, monte, tombe) + z], axis=1)
    return m


def rayons(a, nom, racine, sens, long, large, monte, tombe):
    """Trois rayons brodés sur un voile, de la racine vers le bord, posés sur sa face du dessus."""
    d = Vector(sens).normalized()
    t = Vector((-d.y, d.x, 0.0))
    for i, w in enumerate((-0.26, 0.04, 0.30)):
        pts = []
        for u in np.linspace(0.03 * long, 0.84 * long, 8):
            y = w * large * K.lisse(u / (0.5 * long))
            p = racine + d * u + t * y
            pts.append(Vector((p.x, p.y, float(hauteur(racine, u, y, monte, tombe)) + 0.0042)))
        a.broderie("%s%d" % (nom, i), A.courbe(pts, 3), 0.0015, OR_FONCE)


def construire():
    a = K.Animal("poisson_rouge")
    a.taille = 0.36

    # ----- le corps : un œuf court et profond, aplati sur les côtés, la bosse haute derrière la tête, le ventre posé à plat -----
    corps = robe(A.tour(A.profil(GALBE, 9), 64))

    def bossu(v):
        s = v * [0.80, 1.0, 1.0]
        s[:, 1] *= np.where(v[:, 1] > 0, 1.0 + 0.30 * np.exp(-((v[:, 2] - 0.112) / 0.034) ** 2), 1.06)
        s[:, 1] = np.maximum(s[:, 1], -0.052)                            # le ventre à plat sur l'herbe
        return s
    corps.sculpte(bossu)
    G.sillons(corps, [16], 0.004, 1.1)
    a.piece("corps", corps.sculpte(DOS.couche), None)
    a.couture("dos", "corps", 16, 0.32, 0.92, fil=OR, large=0.008, haut=0.004, pas=0.012)
    # les écailles : trois pastilles vermillon en file sur le flanc qu'elle tend vers le ciel
    for i, (s, h, o) in enumerate(((0.104, 0.24, 0.17), (0.078, 0.30, 0.16), (0.054, 0.36, 0.14))):
        centre, d = DOS.vise(s, 0.0, 0.90, h)
        a.rustine("ecaille%d" % i, "corps", centre, d, o, VERMILLON, 0.0025, 11, fil=OR_FONCE)

    nez, avant, nuque = (Vector(x) for x in DOS.cadre(DOS.long))
    a.tete = nez - avant * 0.030

    # ----- les yeux globuleux : deux boules qui sortent de la tête, l'œil dessus, à moitié voilé d'une paupière lourde -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, d = DOS.vise(0.146, 0.25, 0.92 * c, 0.42)
        p, n = a.surface("corps", centre, d)
        globe = p + n * 0.006
        a.piece("globe_" + nom, A.boule(1.0, 32, 16).etire(0.021), ORANGE, pos=globe)
        regard = (n + avant * 0.55 + nuque * 0.10).normalized()
        q = globe + regard * 0.021
        a.oeil("oeil_" + nom, q, regard, 0.0130)
        a.piece("lourde_" + nom, K.paupiere(0.0130, 0.05), VERMILLON, mat=A.cadre(q + regard * 0.001, regard, (nuque - avant * 0.2).normalized()), poil=False)

    # ----- la bouche en cul-de-poule : un anneau de lèvres pêche, tendu en avant ; l'ouïe brodée derrière l'œil -----
    bouche = nez - avant * 0.002
    levres = A.tour(A.profil([(0.0125, -0.004), (0.0150, 0.004), (0.0158, 0.011), (0.0135, 0.0165), (0.0085, 0.0175), (0.0068, 0.013),
                               (0, 0.010)], 4), 32)                          # une coupe : le bourrelet des lèvres et le creux de la bouche
    a.piece("levres", levres, PECHE, mat=A.cadre(bouche, avant, nuque), poil=False)
    a.piece("gosier", A.boule(1.0, 16, 8).etire(0.0068, 0.0068, 0.0020), VERMILLON, mat=A.cadre(bouche + avant * 0.0115, avant, nuque), poil=False)
    centre, _d = DOS.vise(0.128, 0.0, 0.0, 0.0)
    ouie = a.trace("corps", centre, [Vector(DOS.flanc) * 0.9 + nuque * math.sin(t) * 0.7 + avant * (0.30 * math.cos(t) - 0.22) for t in np.linspace(-0.6, 0.6, 7)], 0.004)
    a.broderie("ouie", A.courbe(ouie, 4), 0.0020, VERMILLON)

    # ----- la dorsale : une haute voile dorée plantée sur la bosse, qui retombe vers sa droite, lasse -----
    pied, av_, nu_ = (Vector(x) for x in DOS.cadre(0.112))
    haut_ = a.trace("corps", Vector(pied), [nu_], 0.0)[0]
    crete = A.courbe([(0.0, -0.014), (0.003, 0.030), (0.012, 0.054), (0.024, 0.060), (0.036, 0.050), (0.056, 0.034), (0.080, 0.020),
                      (0.104, 0.008), (0.092, -0.010), (0.062, -0.030), (0.026, -0.026)], 5, fermee=True)
    fl = Vector(DOS.flanc)
    penche, face = (nu_ - fl * 0.45).normalized(), (fl + nu_ * 0.45).normalized()   # son X file vers la queue, elle penche vers sa droite
    a.piece("dorsale", A.decoupe(crete, 0.0055, 0.0020), OR, mat=A.cadre(haut_, face, penche), poil=False)

    # ----- la queue double : deux grands voiles plissés qui traînent dans l'herbe, l'un à gauche, l'autre à droite -----
    racine, av_q, _nu = (Vector(x) for x in DOS.cadre(0.006))
    for nom, sens, long_, large in (("G", (0.86, 1.0, 0.0), 0.160, 0.150), ("D", (-0.66, 1.0, 0.0), 0.142, 0.130)):
        a.piece("voile_" + nom, voile(racine, sens, long_, large, 0.42, 2.9), OR, poil=False)
        rayons(a, "rayon_" + nom, racine, sens, long_, large, 0.42, 2.9)

    # ----- les pectorales : deux petits éventails dorés posés dans l'herbe de chaque côté du ventre -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, d = DOS.vise(0.128, -0.10, 0.85 * c, -0.55)
        p, n = a.surface("corps", centre, d)
        sens = Vector((c * 0.80, 0.60, 0.0))
        a.piece("pectorale_" + nom, voile(p - n * 0.004, sens, 0.052, 0.046, -0.15, 1.5), OR, poil=False)
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py poisson_rouge). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# L'œuf est une pièce souple le long de l'échine (la queue, le milieu, la tête). Chaque voile de la queue est souple
# lui aussi : sa racine suit la queue, son milieu « voile_g » (ou _d), son bord « pli_g » (ou _d). Elle est roulée sur
# le flanc et ses deux voiles ne s'étalent pas pareil : les os des voiles et des pectorales sont nommés à la main.

from poses import Pose, borne, cloche, onde


def _ou(v):
    return tuple(round(float(x), 4) for x in v)


_RACINE = np.array(DOS.cadre(0.006)[0])                      # là où les deux voiles sortent du pédoncule
_SENS = {"_G": np.array([0.86, 1.0, 0.0]) / math.hypot(0.86, 1.0), "_D": np.array([-0.66, 1.0, 0.0]) / math.hypot(0.66, 1.0)}

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.003, 0.010)),              # sous le ventre, posé dans l'herbe : elle roule autour
    ("queue", "corps", _ou(DOS.cadre(0.045)[0])),          # le pédoncule
    ("tete", "corps", _ou(DOS.cadre(0.125)[0])),           # derrière les ouïes
    ("levres", "tete", (0.011, -0.078, 0.071)),            # le fond de la bouche
    ("dorsale", "corps", (-0.020, -0.015, 0.134)),         # le pied de la dorsale, sur la bosse
    ("voile_g", "queue", _ou(_RACINE)),                    # la racine des voiles, au bout du pédoncule
    ("voile_d", "queue", _ou(_RACINE)),
    ("pli_g", "voile_g", (0.046, 0.135, 0.066)),           # le milieu de chaque voile, d'où le bord ondule
    ("pli_d", "voile_d", (-0.036, 0.136, 0.066)),
    ("pecto_g", "corps", (0.048, -0.037, 0.047)),          # la racine de chaque pectorale, contre le ventre
    ("pecto_d", "corps", (-0.030, -0.036, 0.024)),
]


def _abscisse(points):
    """Pour chaque point : sa place le long de l'échine, au pied de la perpendiculaire sur le tronçon le plus proche."""
    a, ab = DOS.p[:-1], np.diff(DOS.p, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    ap = points[:, None, :] - a[None, :, :]
    u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
    j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
    return DOS.fait[j] + u[np.arange(len(points)), j] * np.sqrt(l2[j])


def souple(points, cote):
    """L'œuf et ce qui y est cousu : l'arrière suit la queue, le milieu le corps, l'avant la tête."""
    s = _abscisse(points * ([-1, 1, 1] if cote == "_D" else [1, 1, 1]))
    q = 1 - K.lisse((s - 0.025) / 0.050)
    t = K.lisse((s - 0.105) / 0.040)
    return {"queue": q, "corps": 1 - q - t, "tete": t}


def _voile(points, cote):
    """Un voile de la queue (cote : son côté) : la racine suit la queue, le milieu son os, le bord son pli."""
    x = (points - _RACINE) @ _SENS[cote]
    a, b = K.lisse(x / 0.030), K.lisse((x - 0.060) / 0.060)
    c = cote[1].lower()
    return {"queue": 1 - a, "voile_" + c: a - b, "pli_" + c: b}


def _voiles(points, cote):
    """Les deux voiles : l'usine retourne en miroir celui de droite avant de le donner, on le remet à sa place."""
    return _voile(points * ([-1, 1, 1] if cote == "_D" else [1, 1, 1]), cote)


def _pecto(points, cote):
    """Une pectorale, toute sur l'os de son côté."""
    return {"pecto_g" if cote == "_G" else "pecto_d": np.ones(len(points))}


# les rayons brodés suivent leur voile, et se rangent avec lui (avec la queue)
PORTEURS = [("corps", souple, "corps"), ("dos", souple, "corps"), ("ecaille", souple, "corps"), ("ouie", souple, "corps"),
            ("globe", "tete"), ("oeil", "tete"), ("lourde", "tete"), ("levres", "levres"), ("gosier", "levres"),
            ("dorsale", "dorsale"), ("voile", _voiles, "queue"),
            ("rayon_G", lambda points, cote: _voile(points, "_G"), "queue"),
            ("rayon_D", lambda points, cote: _voile(points, "_D"), "queue"),
            ("pectorale", _pecto),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]

COUCHEE = 12.0                                # dort : de combien elle roule encore sur son flanc droit


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _traine(p, t, force, tours, phase=0.0):
    """Les deux voiles ondulent comme une traîne : une vague lente qui court de la racine vers le bord."""
    for c, decale in (("g", 0.0), ("d", 0.18)):
        p.add("voile_" + c, rot=(0, 3 * force * onde(t, tours, phase + decale), 4 * force * onde(t, tours, phase + decale)))
        p.add("pli_" + c, rot=(0, 7 * force * onde(t, tours, phase + decale - 0.2), 6 * force * onde(t, tours, phase + decale - 0.2)))


def _moue(p, force):
    """La bouche en cul-de-poule se tend (force > 0) ou s'ouvre en grand (force < 0)."""
    p.add("levres", ech=(1 + 0.15 * force, 1 + 0.25 * force, 1 + 0.15 * force) if force > 0 else
          (1 - 0.30 * force, 1 - 0.10 * force, 1 - 0.30 * force))


def repos(t):
    """La diva attend qu'on s'excuse : elle respire en soupirant, la bouche fait des bisous boudeurs, la traîne ondule
    languissamment ; elle détourne la tête, vexée, laisse retomber sa dorsale d'un air las, donne un coup de queue
    agacé ; elle cligne lentement sous ses paupières lourdes."""
    p = Pose()
    r = onde(t, 2)
    p.add("corps", ech=(1 + 0.014 * r, 1, 1 + 0.018 * r))
    _moue(p, 0.6 * max(0.0, onde(t, 6)))
    _traine(p, t, 1.0, 2)
    vexee = cloche(t, 0.42, 0.16)
    p.add("tete", rot=(-3 * vexee, 4 * vexee, -12 * vexee))
    p.add("dorsale", rot=(0, -8 * cloche(t, 0.60, 0.10), 0))
    p.add("queue", rot=(0, 0, 14 * cloche(t, 0.80, 0.05)))
    p.add("pecto_g", rot=(0, 0, 10 * onde(t, 4)))
    p.add("pecto_d", rot=(0, 0, -10 * onde(t, 4, 0.2)))
    p.ouvert = 1 - cloche(t, 0.16, 0.05) - cloche(t, 0.70, 0.05)
    return p


def avance(t):
    """Elle frétille dans l'herbe pour avancer, comme un poisson hors de l'eau : deux grands coups de reins par cycle,
    le corps qui se courbe d'un côté puis de l'autre en sautillant à peine, la traîne qui fouette derrière, les
    pectorales qui battent."""
    p = Pose()
    c = onde(t, 2)
    p.add("corps", pos=(0, 0, 0.010 * abs(c)), rot=(0, 0, 6 * c))
    p.add("tete", rot=(0, 0, 8 * onde(t, 2, 0.1)))
    p.add("queue", rot=(0, 0, -16 * onde(t, 2, -0.08)))
    _traine(p, t, 2.6, 2, -0.2)
    p.add("pecto_g", rot=(0, 0, 18 * onde(t, 4)))
    p.add("pecto_d", rot=(0, 0, -18 * onde(t, 4)))
    p.add("dorsale", rot=(0, 6 * onde(t, 2, 0.15), 0))
    return p


def mange(t):
    """Elle tend la bouche vers la miette, la gobe trois fois d'un coup sec (la bouche s'ouvre en grand), puis mâche
    d'un air pincé, à petits bisous, la traîne qui ondule de satisfaction."""
    p = Pose()
    vers_ = _plateau(t, 0.38, 0.22, 0.10)
    gobe = max(0.0, onde(t, 9)) * _plateau(t, 0.38, 0.18, 0.05)
    p.add("tete", rot=(6 * vers_, 0, 4 * vers_), pos=(0, -0.006 * vers_ - 0.004 * gobe, 0))
    _moue(p, -gobe + 0.5 * cloche(t, 0.80, 0.12) * max(0.0, onde(t, 10)))
    _traine(p, t, 1.2, 2)
    p.add("queue", rot=(0, 0, 8 * gobe))
    p.ouvert = 1 - cloche(t, 0.92, 0.03)
    return p


def joie(t):
    """Sa joie de diva : un grand saut cambré hors de l'herbe, comme hors de l'eau, la dorsale qui se dresse, les voiles
    qui tournoient en éventail, un bisou en l'air ; elle retombe sur le flanc, comblée."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85)) if t < 0.85 else 0.0
    saut = math.sin(math.pi * borne((t - 0.12) / 0.55))
    p.add("corps", pos=(0, 0, 0.050 * saut), rot=(-4 * saut, 0, 10 * onde(t, 2) * env))
    p.add("tete", rot=(-12 * saut, 0, 0))
    p.add("queue", rot=(18 * saut, 0, 14 * onde(t, 4) * env))        # cambrée en C : la queue remonte
    _traine(p, t, 3.0 * env, 3)
    for c in ("g", "d"):
        p.add("voile_" + c, rot=(16 * saut, 0, 0))
    p.add("dorsale", rot=(0, 14 * env, 0))
    p.add("pecto_g", rot=(0, 0, 24 * onde(t, 6) * env))
    p.add("pecto_d", rot=(0, 0, -24 * onde(t, 6) * env))
    _moue(p, env)
    return p


def dort(t):
    """Elle se laisse aller tout à fait sur le flanc, la traîne étalée sans un pli, la dorsale couchée, les yeux
    fermés ; la bouche fait de lents petits bisous, comme des bulles, au rythme d'une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", rot=(0, -COUCHEE, 0), ech=(1 + 0.012 * r, 1, 1 + 0.016 * r))
    p.add("dorsale", rot=(0, -14, 0))
    _moue(p, 0.4 * (0.5 + 0.5 * r))
    _traine(p, t, 0.4, 1)
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Poisson rouge")
