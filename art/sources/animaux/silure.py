"""Le silure en peluche : le vieux glouton du fond du lac. Une peluche longue et molle de brun très sombre, les flancs
marbrés d'un brun plus doux, le ventre crème. Une tête plate énorme, plus large que tout le reste, fendue d'une bouche
immense d'une joue à l'autre, aux lèvres épaisses relevées aux coins : il sourit de toute sa bouche, repu. Aux coins,
ses deux grandes moustaches crème qui ondulent, l'une traînée dans l'herbe de notre côté, l'autre levée en l'air de l'autre ; quatre petites
sous le menton. Deux yeux minuscules, très écartés, sous des paupières à moitié tombées. Derrière, le corps s'effile en
une longue queue qui serpente, bordée dessous d'une longue anale qui court jusqu'au bout. Il est vautré sur le ventre,
nonchalant, la queue en S : il digère.

    python silure.py        fabrique la fiche art/apercus/animaux/silure.png (style B, peluche de magasin : palier 4)
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

SOMBRE = M.hexa("#4a3a34")                    # le dos et la tête : brun très sombre
MARBRE = M.hexa("#6e5a4e")                    # les marbrures des flancs, un brun plus doux
CREME = M.hexa("#f0e4cc")                     # le ventre
LEVRE = M.hexa("#dcc8ae")                     # les lèvres épaisses, d'un beige rosé
GOSIER = M.hexa("#2a1f1c")                    # la fente de la bouche
MOUSTACHE = M.hexa("#f2e6cc")                 # l'accent : les moustaches, crème au bout
RACINE = M.hexa("#8a7262")                    # la racine des moustaches, fondue dans la tête
NAGEOIRE = M.hexa("#3e302b")                  # les nageoires, d'un ton plus sombre que le corps
TOURNE = 0                                    # -40 pour la fiche, posé de biais (on lit sa longueur) ; 0 pour le jeu
ROT = A.repere((0, 0, 0), (0, 0, TOURNE))
R3 = ROT.to_3x3()
HAUT = 0.050                                  # la hauteur de l'échine : chaque tranche du corps touche l'herbe par-dessous
# l'échine, de la queue au nez : vautré sur le ventre, la longue queue en S
DOS = K.Fil([ROT @ Vector(p) for p in ((0.120, 0.560, HAUT), (0.040, 0.420, HAUT), (-0.070, 0.250, HAUT), (-0.060, 0.070, HAUT),
                                       (0.030, -0.090, HAUT), (0.050, -0.240, HAUT), (0.020, -0.400, HAUT))], flanc=tuple(R3 @ Vector((1, 0, 0))))
LONG = 0.980                                  # la longueur du corps le long de l'échine, de la queue au museau
PROFIL = A.profil([(0, 0), (0.008, 0.004), (0.013, 0.050), (0.021, 0.140), (0.031, 0.260), (0.043, 0.400), (0.050, 0.540),
                   (0.053, 0.660), (0.055, 0.730), (0.068, 0.810), (0.080, 0.880), (0.076, 0.932), (0.054, 0.966), (0, LONG)], 12)


def rayon(z):
    """Le rayon du profil à la distance z de la queue."""
    return float(np.interp(z, PROFIL[:, 1], PROFIL[:, 0]))


def leve(z):
    """De combien la tranche décolle de l'herbe : l'arrière se soulève un peu, pour laisser pendre la longue anale."""
    return 0.016 * (1 - K.lisse((z - 0.380) / 0.200))


def axe(s):
    """Le milieu de la tranche du corps à la distance s de la queue (le corps a été remonté ou baissé tranche à tranche)."""
    return Vector(DOS.couche(forme(np.array([[0.0, 0.0, s]])))[0])


def forme(v):
    """Le corps (tourné tout droit : +X le flanc, +Y le dos, Z de la queue au museau) : la queue pincée sur les côtés,
    la tête aplatie et élargie comme une pelle ; chaque tranche est remontée ou baissée pour toucher l'herbe."""
    s = v.copy()
    z = v[:, 2]
    tete = K.lisse((z - 0.690) / 0.180)
    s[:, 0] *= (0.60 + 0.30 * K.lisse(z / 0.600)) * (1 + 1.25 * tete)
    plat = np.where(v[:, 1] < 0, 0.80, 1.0) * (1 - 0.42 * tete)
    s[:, 1] *= plat
    r = np.interp(z, PROFIL[:, 1], PROFIL[:, 0])
    s[:, 1] += r * 0.80 * (1 - 0.42 * tete) - HAUT + leve(z)
    return s


def robe(m):
    """Peint le corps avant de le sculpter : la tête et le dos sombres, les flancs marbrés de brun doux, le ventre crème."""
    x, y, z = m.v[:, 0], m.v[:, 1], m.v[:, 2]
    a = np.arctan2(y, np.abs(x))                                    # -90° le ventre, 0 le flanc, 90° le dos
    marbre = (np.sin(z * 41.0 + 3.0 * np.sin(a * 2.3)) + np.sin(z * 17.0 - a * 5.0) * 0.8 + np.sin(a * 9.0 + z * 6.0) * 0.5) > 0.55
    marbre &= (a < 0.55) & (a > -0.45) & (z < 0.800)
    teinte = np.where(marbre[:, None], np.asarray(MARBRE), np.asarray(SOMBRE))
    m.teinte = np.where((a < -0.50 + 0.25 * K.lisse((z - 0.800) / 0.120))[:, None], np.asarray(CREME), teinte)
    return m


def poser(maille, rep):
    """Déplace une maille dans un repère (une matrice de A.cadre)."""
    r = np.array(rep)
    return maille.sculpte(lambda v: v @ r[:3, :3].T + r[:3, 3])


def construire():
    a = K.Animal("silure")
    a.taille = 1.60

    # ----- le corps : un long boudin couché le long de l'échine, la tête en pelle au bout -----
    corps = robe(A.tour(PROFIL, 64)).sculpte(forme).sculpte(DOS.couche)
    a.piece("corps", corps, None)
    _c, avant, nuque = (Vector(x) for x in DOS.cadre(0.900))
    tete = axe(0.900)
    flanc = Vector(DOS.flanc)
    a.tete = tete + avant * 0.040

    # ----- la bouche immense : une lèvre épaisse d'une joue à l'autre, les coins relevés, et la fente sombre dessus -----
    def tour_de_bouche(baisse, coins):
        return [avant * math.cos(u) + flanc * math.sin(u) + nuque * (baisse + coins * (abs(u) / 1.85) ** 3)
                for u in np.linspace(-1.85, 1.85, 27)]
    centre = tete + avant * 0.010
    levre = a.trace("corps", centre, tour_de_bouche(-0.22, 0.20), 0.004)
    a.piece("levre", A.tube(A.courbe(levre, 2), lambda t: 0.0085 + 0.0060 * math.sin(math.pi * t), 12), LEVRE)
    fente = a.trace("corps", centre, tour_de_bouche(-0.08, 0.20), 0.004)
    a.piece("fente", A.tube(A.courbe(fente[1:-1], 2), lambda t: 0.0035 + 0.0040 * math.sin(math.pi * t), 12), GOSIER, poil=False)

    # ----- les yeux : minuscules, très écartés, au ras du front, sous des paupières à moitié tombées -----
    for nom, cote in (("G", 1), ("D", -1)):
        _c, d = DOS.vise(0.905, 0.45, 0.80 * cote, 0.55)
        p, n = a.surface("corps", axe(0.905), d)
        a.bouton("oeil_" + nom, p + n * 0.001, n, 0.0085)
        a.piece("lourde_" + nom, K.paupiere(0.0095, -0.05), SOMBRE, mat=A.cadre(p + n * 0.003, n, nuque - avant * 0.25), poil=False)

    # ----- les moustaches : deux grandes aux coins de la bouche, qui ondulent, l'une traînée dans l'herbe, l'autre levée -----
    for nom, cote, envol in (("G", 1, 0.0), ("D", -1, 1.0)):
        coin = levre[0 if cote < 0 else -1]
        chemin = []
        for k in range(16):
            t = k / 15
            if envol:                                   # la levée : elle part en avant et de côté, monte et s'enroule au bout
                dehors = 0.040 + 0.230 * t + 0.016 * math.sin(t * 2.4 * math.pi)
                arriere = -0.010 - 0.040 * math.sin(t * math.pi) + 0.150 * t
                z = coin.z + 0.095 * math.sin(t * math.pi * 0.80) + 0.014 * math.sin(t * 3.0 * math.pi)
            else:                                       # la traînée : elle retombe vite dans l'herbe et serpente vers l'arrière
                dehors = 0.045 + 0.130 * t + 0.022 * math.sin(t * 2.6 * math.pi)
                arriere = -0.012 + 0.300 * t
                z = coin.z + (0.008 - coin.z) * min(1.0, t * 3.0)
            q = coin + flanc * (cote * dehors) - avant * arriere
            chemin.append(Vector((q.x, q.y, max(z, 0.007))))
        chemin = [coin - flanc * (cote * 0.006)] + chemin
        a.piece("moustache_" + nom, K.tube_peint(A.courbe(chemin, 4), lambda t: 0.0068 * (1 - 0.62 * t), [(0.10, RACINE), (1.0, MOUSTACHE)], 12),
                None, poil=False)
    # les quatre petites du menton, qui pendent sur l'herbe devant la lèvre
    menton = None
    bas = a.trace("corps", centre, [avant * math.cos(u) + flanc * math.sin(u) - nuque * 0.70 for u in (-0.75, -0.28, 0.28, 0.75)], -0.002)
    for k, p in enumerate(bas):
        u = (-0.75, -0.28, 0.28, 0.75)[k]
        sort = (avant * math.cos(u) + flanc * math.sin(u) * 1.6).normalized()
        long = 0.070 if abs(u) > 0.5 else 0.056
        ch = [p, p + sort * long * 0.45 + Vector((0, 0, -0.004)), p + sort * long + Vector((0, 0, 0.0))]
        ch = [Vector((q.x, q.y, max(q.z, 0.006))) for q in ch]
        une = A.tube(A.courbe(ch, 4), lambda t: 0.0042 * (1 - 0.55 * t), 12)
        menton = une if menton is None else menton + une
    a.piece("barbillons", menton, MOUSTACHE, poil=False)

    # ----- les nageoires : une dorsale minuscule, la longue anale qui borde la queue, une queue ronde -----
    _c, av, nu = (Vector(x) for x in DOS.cadre(0.620))
    rep = A.cadre(axe(0.620) + nu * (rayon(0.620) * 0.72), flanc, nu)
    a.piece("dorsale", poser(A.decoupe(A.courbe([(-0.004, -0.006), (0.000, 0.020), (0.014, 0.030), (0.030, 0.018), (0.036, -0.006)], 4, fermee=True),
                                       0.0060, 0.0020), rep), NAGEOIRE, poil=False)

    # l'anale : une bande de feutrine pendue sous la queue, qui suit le S de l'échine (dessinée en (s, profondeur))
    def anale(v):
        s_, h, e = v[:, 0], v[:, 1], v[:, 2]
        fond = -HAUT + leve(s_)                                                     # le dessous du corps, à cette distance
        return DOS.couche(np.stack([e, fond + 0.008 - h, s_], axis=1))
    bord = [(0.010, 0.000), (0.020, 0.012), (0.120, 0.022), (0.260, 0.024), (0.400, 0.019), (0.470, 0.008), (0.480, 0.000)]
    a.piece("anale", A.decoupe(A.courbe(bord, 4, fermee=True), 0.0055, 0.0020).sculpte(anale), NAGEOIRE, poil=False)

    bout, av, nu = (Vector(x) for x in DOS.cadre(0.004))
    rep = A.cadre(axe(0.010), (flanc - av * 0.20).normalized(), nu)
    a.piece("caudale", A.decoupe(A.courbe([(0.0, -0.008), (0.030, -0.020), (0.052, -0.012), (0.058, 0.006), (0.048, 0.024), (0.024, 0.026), (0.0, 0.010)], 4, fermee=True),
                                 0.0055, 0.0020), NAGEOIRE, mat=rep, poil=False)

    # les pectorales derrière la tête et les pelviennes, petites palettes posées à plat sur l'herbe
    for s, nom, long, large in ((0.790, "pectorale", 0.060, 0.020), (0.560, "pelvienne", 0.040, 0.015)):
        _c, av, nu = (Vector(x) for x in DOS.cadre(s))
        c = axe(s)
        for cote, cn in ((1, "_G"), (-1, "_D")):
            p, n = a.surface("corps", c, flanc * cote - nu * 0.55)
            vers = (flanc * (0.85 * cote) - av * 0.55).normalized()
            vers.z = -0.12
            vers.normalize()
            plat = vers.cross(av).normalized()
            if plat.z < 0:
                plat = -plat
            pale = [(-large * 0.5, 0.0), (large * 0.5, 0.0), (large * 0.8, long * 0.6), (large * 0.3, long), (-large * 0.4, long * 0.9), (-large * 0.7, long * 0.4)]
            a.piece(nom + cn, A.decoupe(A.courbe(pale, 4, fermee=True), 0.0050, 0.0018), NAGEOIRE, mat=A.cadre(p - n * 0.006, plat, vers), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py silure). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Le corps est un seul long boudin couché le long de l'échine en S : une pièce souple que six os se passent le long du
# fil, de la queue au museau. Chaque os de la queue s'articule à son bout avant (là où il tient au tronçon d'avant).
# Rien n'est en miroir (le S, une moustache traînée et l'autre levée) : les moustaches et les pectorales ont chacune
# leur os, à leur vraie place.

from poses import Pose, borne, cloche, onde

# chaque os et le début de son tronçon, en mètres le long du fil depuis la queue
_TRONCONS = (("queue4", 0.0), ("queue3", 0.10), ("queue2", 0.22), ("queue", 0.36), ("corps", 0.50), ("tete", 0.76))


def _au_fil(s):
    return tuple(round(float(x), 4) for x in axe(s))


OS = [("racine", None, (0, 0, 0)),
      ("corps", "racine", _au_fil(0.62)),               # le ventre : il s'y tourne, s'y cambre, s'y gonfle
      ("tete", "corps", _au_fil(0.76)),                 # derrière la grosse tête plate
      ("queue", "corps", _au_fil(0.50)),                # quatre os de queue, chacun au bout avant de son tronçon
      ("queue2", "queue", _au_fil(0.36)),
      ("queue3", "queue2", _au_fil(0.22)),
      ("queue4", "queue3", _au_fil(0.10)),              # le bout, qui porte la queue ronde
      ("moustache_g", "tete", (0.206, -0.2204, 0.0334)),     # la racine de chaque moustache, au coin de la bouche
      ("moustache_d", "tete", (-0.105, -0.2194, 0.0333)),
      ("pect_g", "tete", (0.0967, -0.1428, 0.0142)),         # le pied de chaque pectorale
      ("pect_d", "tete", (-0.0074, -0.1436, 0.0144))]


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
    # l'usine retourne les pièces de droite en miroir avant de les donner (pelvienne_D...) : on les remet à leur place
    s = _abscisse(points * ([-1, 1, 1] if cote == "_D" else [1, 1, 1]), DOS.p)
    montees = [np.ones_like(s)] + [K.lisse((s - s0 + 0.05) / 0.10) for _o, s0 in _TRONCONS[1:]] + [np.zeros_like(s)]
    return {o: montees[i] - montees[i + 1] for i, (o, _s0) in enumerate(_TRONCONS)}


def _cote(os_):
    """Une pièce d'un côté (moustache_G, pectorale_D) suit l'os de son côté (moustache_g, pect_d)."""
    return lambda points, cote: {os_ + cote.lower(): np.ones(len(points))}


PORTEURS = [("corps", souple, "corps"), ("levre", souple, "corps"), ("fente", souple, "corps"),
            ("dorsale", souple, "corps"), ("anale", souple, "corps"), ("pelvienne", souple, "corps"),
            ("caudale", "queue4"), ("oeil", "tete"), ("lourde", "tete"), ("barbillons", "tete"),
            ("moustache", _cote("moustache")), ("pectorale", _cote("pect")),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def ondule(p, force, t, tours=1.0):
    """La nage : une vague lente qui court du ventre vers le bout de la queue, de plus en plus large."""
    p.add("corps", rot=(0, 0, 2 * force * onde(t, tours)))
    p.add("queue", rot=(0, 0, -5 * force * onde(t, tours, -0.10)))
    p.add("queue2", rot=(0, 0, -8 * force * onde(t, tours, -0.20)))
    p.add("queue3", rot=(0, 0, -11 * force * onde(t, tours, -0.30)))
    p.add("queue4", rot=(0, 0, -14 * force * onde(t, tours, -0.40)))


def moustaches(p, t, force=1.0, phase=0.0):
    """Les deux grandes moustaches ondulent : la traînée balaie l'herbe, la levée se balance en l'air."""
    p.add("moustache_g", rot=(0, 0, 6 * force * onde(t, 2, phase)))
    p.add("moustache_d", rot=(6 * force * onde(t, 2, phase + 0.3), 0, -8 * force * onde(t, 1, phase)))


def repos(t):
    """Il digère, vautré : un gros souffle lent qui lui gonfle le ventre, les moustaches qui ondulent toutes seules,
    le bout de la queue qui serpente paresseusement ; une fois il soulève sa grosse tête et lâche un rot (tout le
    devant se gonfle puis retombe), satisfait. Il cligne lentement sous ses paupières lourdes."""
    p = Pose()
    r = onde(t, 2)
    p.add("corps", ech=(1 + 0.025 * r, 1, 1 + 0.02 * r))
    moustaches(p, t)
    p.add("queue3", rot=(0, 0, 4 * onde(t, 1)))
    p.add("queue4", rot=(0, 0, 8 * onde(t, 1, -0.15)))
    rot_ = cloche(t, 0.55, 0.08)
    p.add("tete", rot=(-6 * rot_, 0, 0), ech=(1 + 0.08 * rot_, 1, 1 + 0.06 * rot_))
    p.add("moustache_d", rot=(-10 * rot_, 0, 0))
    p.add("pect_g", rot=(0, -4 - 4 * onde(t, 2), 0))
    p.add("pect_d", rot=(0, 4 + 4 * onde(t, 2, 0.5), 0))
    p.ouvert = 1 - cloche(t, 0.82, 0.04)
    return p


def avance(t):
    """Il nage en serpentant, sans se presser : une seule grande vague par cycle, de la tête au bout de la queue ;
    la grosse tête se balance à peine, les moustaches traînent derrière."""
    p = Pose()
    ondule(p, 1.4, t, 1)
    p.add("tete", rot=(0, 0, -2 * onde(t, 1)))
    moustaches(p, t, 0.6)
    p.add("moustache_g", rot=(0, 0, 6))
    p.add("moustache_d", rot=(0, 0, -6))
    p.add("pect_g", rot=(0, -6 - 6 * onde(t, 2), 0))
    p.add("pect_d", rot=(0, 6 + 6 * onde(t, 2, 0.5), 0))
    return p


def mange(t):
    """Il aspire : la tête se soulève, toute la gueule se gonfle d'un coup (il avale l'eau et ce qui passe), trois
    fois, en avançant d'un rien ; les moustaches se rabattent vers l'avant ; puis il mâchonne, content."""
    p = Pose()
    for c in (0.18, 0.40, 0.62):
        g = cloche(t, c, 0.07)
        p.add("tete", rot=(-5 * g, 0, 0), ech=(1 + 0.12 * g, 1, 1 + 0.08 * g))
        p.add("corps", pos=(0, -0.012 * g, 0))
        p.add("moustache_g", rot=(6 * g, 0, -8 * g))        # la traînée suit la tête qui se lève, sans plonger dans l'herbe
        p.add("moustache_d", rot=(0, 0, 8 * g))
    mache = cloche(t, 0.84, 0.10)
    p.add("tete", ech=(1 + 0.03 * mache * onde(t, 10), 1, 1))
    p.add("corps", ech=(1 + 0.04 * cloche(t, 0.70, 0.25), 1, 1))           # le ventre plein
    moustaches(p, t, 0.5)
    p.add("queue4", rot=(0, 0, 6 * onde(t, 1)))
    p.ouvert = 1 - cloche(t, 0.92, 0.03)
    return p


def joie(t):
    """Il se cambre de plaisir, la tête et la queue levées en banane, se tortille d'un bout à l'autre, les deux
    moustaches qui fouettent l'air ; puis il se laisse retomber, vautré."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85))
    p.add("corps", pos=(0, 0, 0.012 * env))
    p.add("tete", rot=(-14 * env, 0, 0))
    p.add("queue", rot=(8 * env, 0, 0))
    p.add("queue2", rot=(8 * env, 0, 0))
    p.add("queue3", rot=(8 * env, 0, 0))
    ondule(p, 1.6 * env, t, 3)
    p.add("moustache_g", rot=(30 * env, 0, 14 * env * onde(t, 4)))
    p.add("moustache_d", rot=(-10 * env, 0, -16 * env * onde(t, 4, 0.25)))
    p.add("pect_g", rot=(0, -20 * env, 0))
    p.add("pect_d", rot=(0, 20 * env, 0))
    return p


def dort(t):
    """Il dort, aplati de tout son long, la queue repliée en S plus serré, les moustaches retombées dans l'herbe ;
    les yeux fermés, un souffle très lent qui lui soulève le ventre."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", ech=(1 + 0.03 * r, 1, 1 + 0.02 * r))
    p.add("queue", rot=(0, 0, -6))
    p.add("queue2", rot=(0, 0, 10))
    p.add("queue3", rot=(0, 0, 10))
    p.add("queue4", rot=(0, 0, 8 + 3 * onde(t, 1, 0.3)))
    p.add("moustache_d", rot=(0, -12, 0))                  # la levée retombe vers l'herbe
    p.add("moustache_g", rot=(0, 0, 2 * r))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("silure", styles.style_de("silure"), sys.modules[__name__]), "Silure")
