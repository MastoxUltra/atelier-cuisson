"""Le brochet en peluche : le chasseur à l'affût. Une torpille de velours ras bleu glacier, le dos d'un ton plus
profond, le ventre crème, et sur les flancs des rangées de taches crème allongées, comme des reflets de soleil sous
l'eau. Tout le caractère est dans le bec : un long bec de canard aplati, la mâchoire du bas qui dépasse, et tout le
long de la fente une rangée de dents de feutrine blanche. L'œil petit, haut sur le crâne plat, sous une lourde paupière
qui descend vers le nez. La dorsale et l'anale rejetées tout à l'arrière, au-dessus et au-dessous de la queue, comme
l'empennage d'une flèche ; toutes les nageoires ambre. Il est couché sur le ventre, le corps tendu en S comme un
ressort, la queue relevée : immobile, il va partir d'un coup.

    python brochet.py        fabrique la fiche art/apercus/animaux/brochet.png (style C, velours ras : palier 3)
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

GLACIER = M.hexa("#aac7dc")                   # les flancs : bleu glacier (le poil le fonce un peu)
PROFOND = M.hexa("#86a8c2")                   # le dos, d'un ton plus profond
CREME = M.hexa("#f6ecd6")                     # le ventre, la mâchoire du bas, les taches des flancs
AMBRE = M.hexa("#d98f2e")                     # l'accent : toutes les nageoires
NUIT = M.hexa("#2f3b4c")                      # la fente de la gueule
SOURCIL = M.hexa("#5d7d99")                   # la lourde paupière, plus sombre que le dos : le regard noir
DENT = M.hexa("#fffbf2")                      # les dents de feutrine
TOURNE = 0                                    # -40 pour la fiche, posé de biais (on lit sa torpille) ; 0 pour le jeu
ROT = A.repere((0, 0, 0), (0, 0, TOURNE))
# l'échine, de la queue au nez : couché sur le ventre, tendu en S, la queue relevée, le bec à ras de l'herbe
DOS = K.Fil([ROT @ Vector(p) for p in ((0.050, 0.410, 0.078), (0.032, 0.280, 0.052), (-0.026, 0.130, 0.047), (-0.030, -0.030, 0.047),
                                       (0.004, -0.170, 0.043), (0.022, -0.290, 0.029))], flanc=tuple(ROT.to_3x3() @ Vector((1, 0, 0))))
LONG = 0.700                                  # la longueur du corps le long de l'échine, de la queue au bout du bec
PROFIL = A.profil([(0, 0), (0.010, 0.004), (0.014, 0.030), (0.020, 0.070), (0.034, 0.140), (0.047, 0.220), (0.056, 0.310),
                   (0.059, 0.400), (0.057, 0.460), (0.052, 0.510), (0.045, 0.555), (0.037, 0.595), (0.030, 0.635), (0.025, 0.668),
                   (0.015, 0.692), (0, LONG)], 12)
FENTE = -0.10                                 # l'angle (en radians, sous le flanc) de la fente de la gueule, sur le bec


def rayon(z):
    """Le rayon du profil à la distance z de la queue."""
    return float(np.interp(z, PROFIL[:, 1], PROFIL[:, 0]))


def forme(v):
    """La torpille (tournée toute droite : +X le flanc, +Y le dos, Z de la queue au nez) : un peu plate sur les côtés,
    le ventre aplati pour se poser, et devant les yeux le bec de canard, large, plat et baissé vers l'herbe."""
    s = v.copy()
    bec = K.lisse((v[:, 2] - 0.540) / 0.100)
    s[:, 0] *= 0.74 + 0.30 * bec
    s[:, 1] *= np.where(v[:, 1] < 0, 0.80, 1.0) * (1 - 0.45 * bec)
    s[:, 1] -= 0.010 * bec
    return s


def robe(m):
    """Peint le corps avant de le sculpter : le dos profond, les flancs glacier marbrés de taches crème allongées
    (les mêmes des deux côtés), le ventre crème qui monte jusqu'à la fente de la gueule sur le bec."""
    x, y, z = m.v[:, 0], m.v[:, 1], m.v[:, 2]
    a = np.arctan2(y, np.abs(x))                                    # l'angle autour du corps : -90° ventre, 0 flanc, 90° dos
    ventre = -0.50 + (0.50 + FENTE) * K.lisse((z - 0.520) / 0.070)
    dos = 0.95 - 0.25 * K.lisse((z - 0.520) / 0.080)
    taches = np.zeros(len(z), bool)
    for rang, (ac, z0, z1, pas) in enumerate(((0.60, 0.170, 0.480, 0.072), (0.20, 0.110, 0.500, 0.064), (-0.20, 0.150, 0.470, 0.070))):
        for k, zc in enumerate(np.arange(z0 + (0.032 if rang == 1 else 0.0), z1, pas)):
            zc += 0.012 * math.sin(7.3 * k + 2.1 * rang)               # un semis irrégulier, comme un marbré
            ac_ = ac + 0.08 * math.sin(5.1 * k + 1.3 * rang)
            long = (0.024 + 0.008 * math.sin(3.7 * k + rang)) * (0.55 + 0.45 * min(1.0, zc / 0.30))   # plus petites vers la queue
            incline = (z - zc) * 1.6 * math.sin(2.3 * k + rang)          # chacune un peu de travers
            taches |= ((z - zc) / long) ** 2 + ((a - ac_ - incline) / 0.13) ** 2 < 1.0
    teinte = np.where((a > dos)[:, None], np.asarray(PROFOND), np.asarray(GLACIER))
    teinte = np.where(taches[:, None], np.asarray(CREME), teinte)
    m.teinte = np.where((a < ventre)[:, None], np.asarray(CREME), teinte)
    return m


def peau(s, a, cote, enfonce=0.0):
    """Le point du tissu à la distance s de la queue, à l'angle a (0 = flanc, + vers le dos), du côté cote (1 gauche,
    -1 droite), et la direction qui sort du tissu là. enfonce : de combien (en rayons) le point rentre dans la peluche."""
    r = rayon(s)
    v = np.array([[cote * r * math.cos(a), r * math.sin(a), s], [cote * r * 1.05 * math.cos(a), r * 1.05 * math.sin(a), s]])
    v[0, :2] *= 1 - enfonce
    p, q = (Vector(x) for x in DOS.couche(forme(v)))
    return p, (q - p).normalized()


def poser(maille, rep):
    """Déplace une maille dans un repère (une matrice de A.cadre)."""
    r = np.array(rep)
    return maille.sculpte(lambda v: v @ r[:3, :3].T + r[:3, 3])


def plantee(s, sens, contour, epaisseur=0.0040):
    """Une nageoire de feutrine plantée sur l'arête du dos (sens 1) ou du ventre (sens -1) à la distance s de la queue :
    le contour est dessiné X vers la queue, Y qui s'éloigne du corps."""
    centre, avant, nuque = (Vector(x) for x in DOS.cadre(s))
    pied = centre + nuque * (sens * rayon(s) * (0.82 if sens > 0 else 0.62))
    rep = A.cadre(pied, Vector(DOS.flanc) * sens, nuque * sens)
    return poser(A.decoupe(A.courbe(contour, 4, fermee=True), epaisseur, 0.0014), rep)


def construire():
    a = K.Animal("brochet")
    a.taille = 0.90

    # ----- le corps : une torpille de velours couchée le long de l'échine, le bec de canard au bout -----
    corps = robe(A.tour(PROFIL, 80)).sculpte(forme).sculpte(DOS.couche)
    a.piece("corps", corps, None)
    a.tete = peau(0.600, 0.3, 1)[0] * 0.5 + Vector(DOS.cadre(0.600)[0]) * 0.5

    # la mâchoire du bas, qui dépasse du bec : un menton crème au bout
    bout, avant, nuque = (Vector(x) for x in DOS.cadre(LONG - 0.012))
    menton = A.boule(1.0, 32, 16).etire(0.017, 0.008, 0.024)
    a.piece("menton", menton, CREME, mat=A.cadre(bout - nuque * 0.010 + avant * 0.004, avant, nuque))

    # ----- les yeux : petits, hauts sur le crâne plat, sous une lourde paupière qui descend vers le nez -----
    for nom, cote in (("G", 1), ("D", -1)):
        centre, d = DOS.vise(0.566, 0.22, 0.80 * cote, 0.62)
        p, n = a.surface("corps", centre, d)
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0115)
        _c, avant, nuque = (Vector(x) for x in DOS.cadre(0.566))
        a.piece("lourde_" + nom, K.paupiere(0.0115, 0.02), SOURCIL, mat=A.cadre(p + n * 0.003, n, nuque + avant * 0.75), poil=False)

    # ----- la gueule : la fente le long du bec, et la rangée de dents de feutrine qui en pend, des deux côtés -----
    dents = None
    for nom, cote in (("G", 1), ("D", -1)):
        fente = [peau(s, FENTE, cote)[0] + peau(s, FENTE, cote)[1] * 0.0012 for s in np.linspace(LONG - 0.006, 0.578, 12)]
        a.broderie("gueule_" + nom, A.courbe(fente, 3), 0.0023, NUIT)
        for k, s in enumerate(np.linspace(0.684, 0.588, 9)):
            p, n = peau(s, FENTE + 0.06, cote, 0.12)
            _c, avant, nuque = (Vector(x) for x in DOS.cadre(s))
            haut = 0.0105 if k % 2 == 0 else 0.0070
            une = poser(A.tour(A.profil([(0.0034, 0), (0.0026, haut * 0.5), (0, haut)], 4), 12),
                        A.cadre(p, (-nuque * 0.80 + n * 0.45 + avant * 0.15).normalized(), avant))
            dents = une if dents is None else dents + une
    a.piece("dents", dents, DENT, poil=False)

    # ----- l'empennage : la dorsale et l'anale rejetées tout à l'arrière, l'une au-dessus de l'autre -----
    a.piece("dorsale", plantee(0.205, 1, [(0.0, -0.006), (0.004, 0.022), (0.016, 0.044), (0.036, 0.052), (0.060, 0.044), (0.082, 0.024),
                                          (0.096, 0.004), (0.100, -0.006)]), AMBRE, poil=False)
    a.piece("anale", plantee(0.190, -1, [(0.0, -0.006), (0.006, 0.012), (0.022, 0.022), (0.050, 0.024), (0.074, 0.014), (0.086, -0.006)]),
            AMBRE, poil=False)

    # ----- la queue : un éventail fourchu, profond, au bout du pédoncule relevé -----
    bout, avant, nuque = (Vector(x) for x in DOS.cadre(0.006))
    rep = A.cadre(bout, (Vector(DOS.flanc) - avant * 0.25).normalized(), nuque)
    fourche = A.courbe([(0.0, -0.010), (0.034, -0.036), (0.078, -0.068), (0.090, -0.062), (0.066, -0.016), (0.058, 0.0),
                        (0.066, 0.016), (0.090, 0.064), (0.078, 0.072), (0.034, 0.038), (0.0, 0.010)], 4, fermee=True)
    a.piece("caudale", A.decoupe(fourche, 0.0045, 0.0015), AMBRE, mat=rep, poil=False)

    # ----- les nageoires paires : les pectorales derrière la tête et les pelviennes au milieu, posées à plat sur l'herbe -----
    for s, nom, long in ((0.500, "pectorale", 0.050), (0.300, "pelvienne", 0.040)):
        for cote, cn in ((1, "_G"), (-1, "_D")):
            p, n = peau(s, -0.85, cote, 0.20)
            _c, avant, nuque = (Vector(x) for x in DOS.cadre(s))
            vers = (Vector(DOS.flanc) * (0.75 * cote) - avant * 0.65 - nuque * 0.18).normalized()   # en arrière, écartée
            plat = vers.cross(avant).normalized() * cote                                                # la face vers le ciel
            if plat.z < 0:
                plat = -plat
            pale = [(-0.010, 0.0), (0.010, 0.0), (0.016, long * 0.55), (0.008, long), (-0.004, long * 0.95), (-0.012, long * 0.45)]
            a.piece(nom + cn, A.decoupe(A.courbe(pale, 4, fermee=True), 0.0035, 0.0012), AMBRE,
                    mat=A.cadre(p, plat, vers), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py brochet). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Le corps est une seule torpille couchée le long de l'échine en S : une pièce souple que cinq os se passent le long
# du fil, de la queue au bec. Chaque os de la queue s'articule à son bout avant (là où il tient au tronçon d'avant) ;
# le S n'est pas symétrique, les pectorales ont donc chacune leur os (pect_g, pect_d), à leur vraie place.

from poses import Pose, borne, cloche, onde

# chaque os et le début de son tronçon, en mètres le long du fil depuis la queue
_TRONCONS = (("queue3", 0.0), ("queue2", 0.10), ("queue", 0.21), ("corps", 0.34), ("tete", 0.54))


def _au_fil(s):
    return tuple(round(float(x), 4) for x in DOS.cadre(s)[0])


def _base(cote):
    """Le pied d'une pectorale, comme dans construire()."""
    return tuple(round(float(x), 4) for x in peau(0.500, -0.85, cote, 0.20)[0])


OS = [("racine", None, (0, 0, 0)),
      ("corps", "racine", _au_fil(0.42)),            # le milieu du corps : il se tourne, s'élance, se cambre autour
      ("tete", "corps", _au_fil(0.54)),              # derrière les ouïes
      ("queue", "corps", _au_fil(0.34)),             # trois os de queue, chacun au bout avant de son tronçon
      ("queue2", "queue", _au_fil(0.21)),
      ("queue3", "queue2", _au_fil(0.10)),           # le pédoncule, qui porte l'éventail
      ("pect_g", "corps", _base(1)),
      ("pect_d", "corps", _base(-1))]


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
    """Le corps : chaque os porte son tronçon, et cède au suivant en douceur sur ± 4 cm."""
    # l'usine retourne les pièces de droite en miroir avant de les donner (pelvienne_D...) : on les remet à leur place
    s = _abscisse(points * ([-1, 1, 1] if cote == "_D" else [1, 1, 1]), DOS.p)
    montees = [np.ones_like(s)] + [K.lisse((s - s0 + 0.04) / 0.08) for _o, s0 in _TRONCONS[1:]] + [np.zeros_like(s)]
    return {o: montees[i] - montees[i + 1] for i, (o, _s0) in enumerate(_TRONCONS)}


def _pectorale(points, cote):
    return {"pect" + cote.lower(): np.ones(len(points))}


PORTEURS = [("corps", souple, "corps"), ("dents", souple, "corps"), ("gueule", souple, "corps"),
            ("dorsale", souple, "corps"), ("anale", souple, "corps"), ("pelvienne", souple, "corps"),
            ("menton", "tete"), ("oeil", "tete"), ("lourde", "tete"), ("caudale", "queue3"), ("pectorale", _pectorale),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def ondule(p, force, t, tours=1.0):
    """La nage : une vague qui court du corps vers la queue, de plus en plus large."""
    p.add("corps", rot=(0, 0, 3 * force * onde(t, tours)))
    p.add("queue", rot=(0, 0, -7 * force * onde(t, tours, -0.12)))
    p.add("queue2", rot=(0, 0, -11 * force * onde(t, tours, -0.24)))
    p.add("queue3", rot=(0, 0, -16 * force * onde(t, tours, -0.36)))


def pectorales(p, g, d):
    """Les pectorales se soulèvent du sol (en degrés), chacune autour de son pied."""
    p.add("pect_g", rot=(0, -g, 0))
    p.add("pect_d", rot=(0, d, 0))


def repos(t):
    """À l'affût, immobile comme un bout de bois : seules les pectorales godillent et le bout de la queue frémit ;
    l'œil suit une proie, la tête pivote d'un rien ; une fois il se ramasse en S, prêt à bondir, et se relâche.
    Il cligne à peine sous sa lourde paupière."""
    p = Pose()
    r = onde(t, 2)
    pectorales(p, 8 + 8 * onde(t, 6), 8 + 8 * onde(t, 6, 0.5))
    p.add("corps", ech=(1 + 0.012 * r, 1, 1 + 0.012 * r))
    ressort = cloche(t, 0.55, 0.12)
    p.add("corps", rot=(0, 0, -4 * ressort))
    p.add("queue", rot=(0, 0, 8 * ressort))
    p.add("queue2", rot=(0, 0, -10 * ressort))
    p.add("queue3", rot=(0, 0, 6 * onde(t, 4) * (1 - ressort) + 12 * ressort))
    p.add("tete", rot=(0, 0, 5 * cloche(t, 0.25, 0.10) - 4 * cloche(t, 0.80, 0.08)))
    p.ouvert = 1 - 0.8 * cloche(t, 0.90, 0.02)
    return p


def avance(t):
    """Il file : deux grands coups de queue par cycle, le corps qui ondule d'un bout à l'autre, les pectorales
    collées, la tête droite comme une flèche."""
    p = Pose()
    ondule(p, 1.0, t, 2)
    p.add("tete", rot=(0, 0, -2 * onde(t, 2)))
    p.add("corps", pos=(0, 0, 0.004))
    pectorales(p, -4, -4)
    return p


def mange(t):
    """L'attaque : il recule d'un rien en se ramassant, puis jaillit d'un coup de queue et happe, deux fois ; il
    secoue la proie d'un côté à l'autre, avale d'une grosse gorgée et se repose à l'affût."""
    p = Pose()
    for c in (0.18, 0.46):
        arme = cloche(t, c - 0.06, 0.05)
        coup = cloche(t, c, 0.05)
        p.add("corps", pos=(0, 0.008 * arme - 0.040 * coup, 0), rot=(-4 * coup, 0, 0))
        p.add("queue", rot=(0, 0, 10 * arme - 8 * coup))
        p.add("queue2", rot=(0, 0, -12 * arme + 16 * coup))
        p.add("queue3", rot=(0, 0, 14 * arme - 22 * coup))
    secoue = cloche(t, 0.66, 0.08)
    p.add("tete", rot=(0, 0, 12 * secoue * onde(t, 8)))
    gorgee = cloche(t, 0.82, 0.06)
    p.add("tete", ech=(1 + 0.10 * gorgee, 1, 1 + 0.06 * gorgee))
    p.add("corps", ech=(1 + 0.06 * cloche(t, 0.88, 0.06), 1, 1))
    pectorales(p, 6 + 6 * onde(t, 4), 6 + 6 * onde(t, 4, 0.5))
    p.ouvert = 1 - cloche(t, 0.95, 0.02)
    return p


def joie(t):
    """Un saut de brochet : il se cambre, jaillit en l'air en arc de cercle, la queue fouettant, et replonge le nez
    le premier ; il retombe à plat, à l'affût."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.80))
    tangue = 1 - 2 * borne(t / 0.80)                              # le nez monte, puis plonge
    p.add("corps", pos=(0, -0.03 * borne(t / 0.80) * env, 0.16 * env), rot=(-28 * env * tangue, 0, 0))
    p.add("tete", rot=(-8 * env, 0, 0))
    p.add("queue", rot=(10 * env, 0, 10 * env * onde(t, 5)))
    p.add("queue2", rot=(10 * env, 0, -16 * env * onde(t, 5, -0.15)))
    p.add("queue3", rot=(8 * env, 0, -22 * env * onde(t, 5, -0.30)))
    pectorales(p, 30 * env, 30 * env)
    return p


def dort(t):
    """Il dort posé au fond, le corps relâché en un S plus doux, les pectorales qui battent tout doucement, la queue
    qui retombe ; les yeux fermés, il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", ech=(1 + 0.015 * r, 1, 1 + 0.015 * r))
    p.add("queue", rot=(0, 0, -4))
    p.add("queue2", rot=(0, 0, 4))
    p.add("queue3", rot=(0, 0, 6 + 3 * onde(t, 1, 0.25)))
    pectorales(p, 3 + 3 * onde(t, 2), 3 + 3 * onde(t, 2, 0.5))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("brochet", styles.style_de("brochet"), sys.modules[__name__]), "Brochet")
