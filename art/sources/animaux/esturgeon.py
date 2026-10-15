"""L'esturgeon en peluche : l'ancêtre du lac, un fossile vivant. Une longue peluche ivoire, le dos d'un grège plus
soutenu, le ventre blanc crème, cuirassée de cinq rangées d'écussons osseux en feutrine crème dorée : une crête sur
l'échine, une sur chaque flanc, une de chaque côté du ventre, chaque écusson une petite pyramide en losange. Le museau
s'allonge en pointe rosée, un peu relevé, et sous lui pendent quatre barbillons en frange, devant la petite bouche.
L'œil petit, sous une paupière lourde de vieux sage. La queue de requin : le haut, qui porte l'échine, bien plus long
que le bas. Il est posé sur le ventre, le corps en une longue courbe tranquille, le nez levé : il en a vu d'autres.

    python esturgeon.py        fabrique la fiche art/apercus/animaux/esturgeon.png (style B, peluche de magasin : palier 4)
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

IVOIRE = M.hexa("#eae2cf")                    # les flancs : la dominante
GREGE = M.hexa("#d6cab0")                     # le dos, un ton plus soutenu
BLANC = M.hexa("#f8f3e6")                     # le ventre
ECUSSON = M.hexa("#e2c27f")                   # les écussons osseux, en feutrine crème dorée
ROSE = M.hexa("#eab3a2")                      # l'accent : le museau en pointe et les barbillons
NAGEOIRE = M.hexa("#cbbd9f")                  # les nageoires, un grège plus sourd
TOURNE = 0                                    # -40 pour la fiche, posé de biais (on lit sa longueur) ; 0 pour le jeu
ROT = A.repere((0, 0, 0), (0, 0, TOURNE))
R3 = ROT.to_3x3()
HAUT = 0.055                                  # la hauteur de l'échine : chaque tranche du corps touche l'herbe par-dessous
# l'échine, de la queue au nez : une longue courbe tranquille, la queue qui remonte vers son lobe du haut
DOS = K.Fil([ROT @ Vector(p) for p in ((0.095, 0.520, HAUT + 0.030), (0.040, 0.380, HAUT + 0.004), (-0.012, 0.200, HAUT), (-0.030, 0.010, HAUT),
                                       (-0.012, -0.180, HAUT), (0.030, -0.390, HAUT + 0.004))], flanc=tuple(R3 @ Vector((1, 0, 0))))
LONG = 0.935                                  # la longueur du corps le long de l'échine, de la queue au bout du museau
PROFIL = A.profil([(0, 0), (0.009, 0.004), (0.012, 0.050), (0.021, 0.120), (0.037, 0.220), (0.053, 0.340), (0.065, 0.460),
                   (0.071, 0.560), (0.069, 0.640), (0.062, 0.710), (0.051, 0.770), (0.038, 0.825), (0.025, 0.870), (0.014, 0.902),
                   (0.007, 0.922), (0, LONG)], 12)
MUSEAU = 0.835                                # là où commence le museau rosé


def rayon(z):
    """Le rayon du profil à la distance z de la queue."""
    return float(np.interp(z, PROFIL[:, 1], PROFIL[:, 0]))


def leve(z):
    """De combien la tranche décolle de l'herbe : le museau se relève doucement, la queue un peu aussi."""
    return 0.046 * K.lisse((z - 0.720) / 0.200) ** 1.5 + 0.010 * (1 - K.lisse(z / 0.250))


def forme(v):
    """Le corps (tourné tout droit : +X le flanc, +Y le dos, Z de la queue au nez) : un peu plat sur les côtés, le ventre
    aplati, le museau en pelle ; chaque tranche est remontée ou baissée pour toucher l'herbe (ou s'en lever un peu)."""
    s = v.copy()
    z = v[:, 2]
    museau = K.lisse((z - 0.760) / 0.120)
    s[:, 0] *= 0.86 + 0.12 * museau
    bas = 0.76 * (1 - 0.25 * museau)
    s[:, 1] *= np.where(v[:, 1] < 0, bas, 1.0 - 0.30 * museau)
    r = np.interp(z, PROFIL[:, 1], PROFIL[:, 0])
    s[:, 1] += r * bas - HAUT + leve(z)
    return s


def axe(s):
    """Le milieu de la tranche du corps à la distance s de la queue."""
    return Vector(DOS.couche(forme(np.array([[0.0, 0.0, s]])))[0])


def robe(m):
    """Peint le corps avant de le sculpter : le dos grège, les flancs ivoire, le ventre blanc, le museau rosé."""
    x, y, z = m.v[:, 0], m.v[:, 1], m.v[:, 2]
    a = np.arctan2(y, np.abs(x))
    teinte = np.where((a > 0.70)[:, None], np.asarray(GREGE), np.asarray(IVOIRE))
    teinte = np.where((a < -0.55)[:, None], np.asarray(BLANC), teinte)
    fondu = K.lisse((z - MUSEAU) / 0.040)[:, None]
    m.teinte = teinte * (1 - fondu) + np.asarray(ROSE) * fondu
    return m


def poser(maille, rep):
    """Déplace une maille dans un repère (une matrice de A.cadre)."""
    r = np.array(rep)
    return maille.sculpte(lambda v: v @ r[:3, :3].T + r[:3, 3])


def construire():
    a = K.Animal("esturgeon")
    a.taille = 1.40
    flanc = Vector(DOS.flanc)

    # ----- le corps : une longue peluche couchée le long de l'échine, le museau en pointe rosée -----
    corps = robe(A.tour(PROFIL, 64)).sculpte(forme).sculpte(DOS.couche)
    a.piece("corps", corps, None)
    a.tete = axe(0.800)

    # ----- les cinq rangées d'écussons : de petites pyramides en losange, plus grandes au milieu du corps -----
    def ecusson(longueur, large, haut):
        pyramide = A.tour(A.profil([(0, -0.002), (1.0, 0.0), (0.62, 0.45), (0, 1.0)], 3), 4)
        return pyramide.sculpte(lambda v: v * [large, longueur, haut])
    for nom, angle, cote, debut, fin, pas, taille in (("ecussons_dos", 90, 1, 0.200, 0.740, 0.046, 1.15),
                                                      ("ecussons_G", 8, 1, 0.090, 0.700, 0.040, 0.90),
                                                      ("ecussons_D", 8, -1, 0.090, 0.700, 0.040, 0.90),
                                                      ("ecussons_bas_G", -42, 1, 0.240, 0.640, 0.044, 0.72),
                                                      ("ecussons_bas_D", -42, -1, 0.240, 0.640, 0.044, 0.72)):
        rang = None
        for s in np.arange(debut, fin, pas):
            _c, avant, nuque = (Vector(x) for x in DOS.cadre(s))
            d = flanc * (cote * math.cos(math.radians(angle))) + nuque * math.sin(math.radians(angle))
            p, n = a.surface("corps", axe(s), d)
            k = taille * (0.55 + 0.45 * min(1.0, rayon(s) / 0.066))
            une = poser(ecusson(0.016 * k, 0.010 * k, 0.010 * k), A.cadre(p - n * 0.002, n, avant))
            rang = une if rang is None else rang + une
        a.piece(nom, rang, ECUSSON, poil=False)

    # ----- les yeux : petits, sur le côté de la tête, sous une paupière lourde de vieux sage -----
    for nom, cote in (("G", 1), ("D", -1)):
        _c, avant, nuque = (Vector(x) for x in DOS.cadre(0.765))
        p, n = a.surface("corps", axe(0.765), flanc * (0.88 * cote) + nuque * 0.42 - avant * 0.05)
        a.bouton("oeil_" + nom, p + n * 0.001, n, 0.0085)
        a.piece("lourde_" + nom, K.paupiere(0.0095, 0.08), GREGE, mat=A.cadre(p + n * 0.003, n, nuque - avant * 0.20), poil=False)

    # ----- sous le museau : la frange de quatre barbillons rosés, et derrière la petite bouche en bourrelet -----
    _c, avant, nuque = (Vector(x) for x in DOS.cadre(0.862))
    frange = None
    for x in (-0.50, -0.17, 0.17, 0.50):
        p, n = a.surface("corps", axe(0.862), flanc * x - nuque)
        ch = [p + nuque * 0.003, p - nuque * 0.010 + avant * 0.004, p - nuque * 0.018 + avant * 0.002 + flanc * (x * 0.030)]
        ch = [Vector((q.x, q.y, max(q.z, 0.005))) for q in ch]
        une = A.tube(A.courbe(ch, 4), lambda t: 0.0032 * (1 - 0.40 * t), 12)
        frange = une if frange is None else frange + une
    a.piece("barbillons", frange, ROSE, poil=False)
    _c, avant, nuque = (Vector(x) for x in DOS.cadre(0.800))
    p, n = a.surface("corps", axe(0.800), -nuque + avant * 0.10)
    a.piece("bouche", A.tore(0.0110, 0.0042, 32, 10), ROSE, mat=A.cadre(p + n * 0.001, n, avant), poil=False)

    # ----- les nageoires : la petite dorsale et l'anale rejetées vers l'arrière, la queue de requin -----
    for nom, s, sens, bord in (("dorsale", 0.205, 1, [(0.0, -0.006), (0.006, 0.020), (0.020, 0.038), (0.034, 0.036), (0.056, 0.012), (0.066, -0.006)]),
                               ("anale", 0.180, -1, [(0.0, -0.006), (0.006, 0.006), (0.022, 0.010), (0.042, 0.005), (0.050, -0.006)])):
        _c, avant, nuque = (Vector(x) for x in DOS.cadre(s))
        pied = axe(s) + nuque * (sens * rayon(s) * (0.80 if sens > 0 else 0.62))
        a.piece(nom, poser(A.decoupe(A.courbe(bord, 4, fermee=True), 0.0050, 0.0018), A.cadre(pied, flanc * sens, nuque * sens)),
                NAGEOIRE, poil=False)

    bout, avant, nuque = (Vector(x) for x in DOS.cadre(0.010))
    rep = A.cadre(axe(0.020), (flanc - avant * 0.20).normalized(), nuque)
    requin = A.courbe([(-0.010, -0.008), (0.010, -0.008), (0.032, -0.026), (0.046, -0.034), (0.040, -0.014), (0.050, 0.004),
                       (0.090, 0.036), (0.128, 0.068), (0.120, 0.074), (0.070, 0.044), (0.020, 0.016), (-0.010, 0.010)], 4, fermee=True)
    a.piece("caudale", A.decoupe(requin, 0.0050, 0.0018), NAGEOIRE, mat=rep, poil=False)

    # les pectorales, amples, posées à plat derrière la tête, et les pelviennes, petites, au milieu du ventre
    for s, nom, long, large in ((0.680, "pectorale", 0.070, 0.026), (0.330, "pelvienne", 0.040, 0.018)):
        _c, av, nu = (Vector(x) for x in DOS.cadre(s))
        for cote, cn in ((1, "_G"), (-1, "_D")):
            p, n = a.surface("corps", axe(s), flanc * cote - nu * 0.60)
            vers = (flanc * (0.80 * cote) - av * 0.60).normalized()
            vers.z = -0.10
            vers.normalize()
            plat = vers.cross(av).normalized()
            if plat.z < 0:
                plat = -plat
            pale = [(-large * 0.5, 0.0), (large * 0.5, 0.0), (large * 0.85, long * 0.55), (large * 0.25, long), (-large * 0.35, long * 0.92),
                    (-large * 0.65, long * 0.40)]
            a.piece(nom + cn, A.decoupe(A.courbe(pale, 4, fermee=True), 0.0050, 0.0018), NAGEOIRE, mat=A.cadre(p - n * 0.006, plat, vers), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py esturgeon). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Le corps est une seule longue peluche couchée le long de l'échine : une pièce souple que cinq os se passent le long
# du fil, de la queue au museau, et les écussons cousus dessus la suivent. Chaque os de la queue s'articule à son bout
# avant. La courbe n'est pas symétrique : les pectorales ont chacune leur os (pect_g, pect_d), à leur vraie place.

from poses import Pose, borne, cloche, onde

# chaque os et le début de son tronçon, en mètres le long du fil depuis la queue
_TRONCONS = (("queue3", 0.0), ("queue2", 0.14), ("queue", 0.27), ("corps", 0.40), ("tete", 0.70))


def _au_fil(s):
    return tuple(round(float(x), 4) for x in axe(s))


OS = [("racine", None, (0, 0, 0)),
      ("corps", "racine", _au_fil(0.50)),               # le milieu du corps
      ("tete", "corps", _au_fil(0.70)),                 # derrière la tête
      ("barbillons", "tete", (0.015, -0.318, 0.040)),   # la racine de la frange, sous le museau
      ("queue", "corps", _au_fil(0.40)),                # trois os de queue, chacun au bout avant de son tronçon
      ("queue2", "queue", _au_fil(0.27)),
      ("queue3", "queue2", _au_fil(0.14)),              # le pédoncule, qui porte la queue de requin
      ("pect_g", "corps", (0.0178, -0.1310, 0.0268)),   # le pied de chaque pectorale
      ("pect_d", "corps", (-0.0550, -0.1322, 0.0269))]


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
    """Le corps : chaque os porte son tronçon, et cède au suivant en douceur sur ± 5 cm."""
    # l'usine retourne les pièces de droite en miroir avant de les donner (ecussons_D...) : on les remet à leur place
    s = _abscisse(points * ([-1, 1, 1] if cote == "_D" else [1, 1, 1]), DOS.p)
    montees = [np.ones_like(s)] + [K.lisse((s - s0 + 0.05) / 0.10) for _o, s0 in _TRONCONS[1:]] + [np.zeros_like(s)]
    return {o: montees[i] - montees[i + 1] for i, (o, _s0) in enumerate(_TRONCONS)}


def _pectorale(points, cote):
    return {"pect" + cote.lower(): np.ones(len(points))}


PORTEURS = [("corps", souple, "corps"), ("ecussons", souple, "corps"), ("dorsale", souple, "corps"), ("anale", souple, "corps"),
            ("pelvienne", souple, "corps"), ("caudale", "queue3"),
            ("oeil", "tete"), ("lourde", "tete"), ("bouche", "tete"), ("barbillons", "barbillons"), ("pectorale", _pectorale),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def ondule(p, force, t, tours=1.0):
    """La nage : une vague lente qui court du corps vers la queue, de plus en plus large."""
    p.add("corps", rot=(0, 0, 2 * force * onde(t, tours)))
    p.add("queue", rot=(0, 0, -6 * force * onde(t, tours, -0.12)))
    p.add("queue2", rot=(0, 0, -9 * force * onde(t, tours, -0.24)))
    p.add("queue3", rot=(0, 0, -13 * force * onde(t, tours, -0.36)))


def pectorales(p, g, d):
    """Les pectorales se soulèvent de l'herbe (en degrés), chacune autour de son pied."""
    p.add("pect_g", rot=(0, -g, 0))
    p.add("pect_d", rot=(0, d, 0))


def repos(t):
    """Le vieux sage médite : un souffle lent, la tête qui hoche une fois, gravement, comme pour dire « j'en ai vu
    d'autres » ; ses barbillons tâtent le fond sans arrêt, les pectorales godillent à peine, la queue balance ;
    il cligne lentement sous sa paupière lourde."""
    p = Pose()
    r = onde(t, 2)
    p.add("corps", ech=(1 + 0.015 * r, 1, 1 + 0.012 * r))
    hoche = cloche(t, 0.45, 0.10)
    p.add("tete", rot=(5 * hoche, 0, 3 * cloche(t, 0.75, 0.12)), pos=(0, 0, 0.005 * hoche))
    p.add("barbillons", rot=(10 * onde(t, 4), 0, 6 * onde(t, 3)))
    pectorales(p, 4 + 4 * onde(t, 2), 4 + 4 * onde(t, 2, 0.5))
    p.add("queue2", rot=(0, 0, 3 * onde(t, 1)))
    p.add("queue3", rot=(0, 0, 6 * onde(t, 1, -0.15)))
    p.ouvert = 1 - cloche(t, 0.20, 0.04)
    return p


def avance(t):
    """Il croise, majestueux : une seule grande vague lente par cycle, portée surtout par la queue ; la tête reste
    droite, les pectorales ouvertes comme des ailes."""
    p = Pose()
    ondule(p, 1.3, t, 1)
    p.add("tete", rot=(0, 0, -2 * onde(t, 1)))
    p.add("corps", pos=(0, 0, 0.004))
    pectorales(p, 8, 8)
    p.add("barbillons", rot=(-8, 0, 0))
    return p


def mange(t):
    """Il fouille le fond : il baisse le museau jusqu'au sol, et avance à petits coups en aspirant, les barbillons
    qui balaient l'herbe devant sa bouche ; puis il relève le nez, et avale."""
    p = Pose()
    bas = cloche(t, 0.42, 0.34)
    aspire = max(0.0, onde(t, 6)) ** 2 * cloche(t, 0.42, 0.28)
    p.add("tete", rot=(9 * bas + 3 * aspire, 0, 0), pos=(0, 0, 0.012 * bas))     # le dessous de la tête frôle l'herbe sans s'y enfoncer
    p.add("corps", pos=(0, -0.010 * aspire, 0))
    p.add("barbillons", rot=(-14 * bas, 0, 14 * bas * onde(t, 6)))
    gorgee = cloche(t, 0.85, 0.06)
    p.add("tete", ech=(1 + 0.06 * gorgee, 1, 1 + 0.04 * gorgee))
    pectorales(p, 5 + 5 * onde(t, 3), 5 + 5 * onde(t, 3, 0.5))
    p.add("queue3", rot=(0, 0, 6 * onde(t, 2)))
    p.ouvert = 1 - cloche(t, 0.92, 0.03)
    return p


def joie(t):
    """Le saut de l'esturgeon, lent et solennel : il jaillit nez au ciel, tout le corps hors de l'eau, se couche sur le
    flanc au sommet et retombe à plat dans une grande éclaboussure ; puis il se repose, digne, comme si de rien n'était."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.80))
    tangue = 1 - 2 * borne(t / 0.80)
    p.add("corps", pos=(0, 0, 0.20 * env), rot=(-34 * env * tangue, 22 * env * env, 0))
    p.add("tete", rot=(-6 * env, 0, 0))
    p.add("queue", rot=(8 * env, 0, 8 * env * onde(t, 3)))
    p.add("queue2", rot=(8 * env, 0, -12 * env * onde(t, 3, -0.15)))
    p.add("queue3", rot=(6 * env, 0, -18 * env * onde(t, 3, -0.30)))
    pectorales(p, 30 * env, 30 * env)
    p.add("barbillons", rot=(-20 * env, 0, 0))
    return p


def dort(t):
    """Il dort posé au fond, le museau baissé jusqu'à l'herbe, les barbillons immobiles, les pectorales à plat ; les
    yeux fermés, un souffle très lent ; le bout de la queue bouge une fois."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", ech=(1 + 0.02 * r, 1, 1 + 0.015 * r))
    p.add("tete", rot=(6, 0, 0), pos=(0, 0, 0.007))
    p.add("barbillons", rot=(-10, 0, 0))
    p.add("queue3", rot=(0, 0, 4 + 6 * cloche(t, 0.60, 0.06)))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("esturgeon", styles.style_de("esturgeon"), sys.modules[__name__]), "Esturgeon")
