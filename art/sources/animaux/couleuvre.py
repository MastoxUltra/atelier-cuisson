"""La couleuvre en peluche : un long boudin gris perle, le dos ardoise, le ventre en damier crème et ardoise, un collier
jaune vif derrière la tête. Lovée en S dans l'herbe, le tiers avant dressé en col de cygne, la tête penchée sur le
côté, deux gros boutons écartés et un bout de langue fourchue : elle est curieuse de tout, et pas méchante pour un sou.

    python couleuvre.py        fabrique la fiche art/apercus/animaux/couleuvre.png
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

PERLE = np.array(M.hexa("#cfd3dc"))           # le gris perle des flancs
REFLET = np.array(M.hexa("#7d8698"))          # le reflet ardoise le long du dos
ARDOISE = np.array(K.ARDOISE)                 # les cases sombres du damier
OMBRE = np.array(M.hexa("#3c414e"))           # le liseré sombre derrière le collier
VIF = np.array(M.hexa("#ffd400"))             # le collier jaune vif
RAYON, COTES, PAS = 0.034, 40, 0.004          # le rayon du boudin, ses côtés, l'écart entre deux anneaux

# Le fil du corps, du bout de la queue au bout du nez : un grand S couché dans l'herbe (trois passes), puis le tiers
# avant se dresse en col de cygne, et la tête revient à plat tout en haut, tournée vers celui qui la regarde.
CHEMIN = [(0.34, -0.02, 0.012), (0.31, 0.13, 0.028), (0.14, 0.22, 0.035), (-0.04, 0.20, 0.035), (-0.20, 0.22, 0.035), (-0.30, 0.12, 0.035),
          (-0.27, -0.02, 0.035), (-0.13, -0.07, 0.035), (0.02, -0.02, 0.035), (0.15, 0.04, 0.035), (0.24, -0.03, 0.035), (0.22, -0.13, 0.038),
          (0.12, -0.19, 0.050), (0.00, -0.19, 0.085), (-0.07, -0.14, 0.16), (-0.06, -0.08, 0.25), (-0.01, -0.09, 0.315), (0.035, -0.14, 0.338),
          (0.072, -0.198, 0.360)]
FIL = A.courbe(CHEMIN, 16)
FAIT = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(FIL, axis=0), axis=1))])     # la distance parcourue jusqu'à chaque point
SENS = np.gradient(FIL, FAIT, axis=0)
LONG = float(FAIT[-1])
TETE = LONG - 0.065                           # le milieu de la tête, le long du fil


def rayon(s):
    """Le rayon du boudin à la distance s de la queue : une queue effilée, le cou un peu pincé, la tête ronde."""
    s = np.asarray(s, float)
    r = RAYON * (0.14 + 0.86 * K.lisse(s / 0.62)) * np.minimum(1.0, (s / 0.03) ** 0.5)
    r = r * (1 - 0.20 * np.exp(-((s - (LONG - 0.190)) / 0.060) ** 2) + 0.22 * np.exp(-((s - (LONG - 0.070)) / 0.045) ** 2))
    return r * np.sqrt(1 - np.clip((s - (LONG - 0.050)) / 0.050, 0, 1) ** 2)


def repere(s):
    """En un point du fil : le centre du boudin, la direction où il va, son dos et son flanc gauche.
    Vers la tête, le boudin tourne sur lui-même : c'est ce qui penche la tête sur le côté."""
    centre = np.stack([np.interp(s, FAIT, FIL[:, k]) for k in range(3)], axis=-1)
    avant = np.stack([np.interp(s, FAIT, SENS[:, k]) for k in range(3)], axis=-1)
    avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
    dos = np.array([0.0, 0.0, 1.0]) - avant[..., 2:3] * avant
    dos = dos / np.linalg.norm(dos, axis=-1, keepdims=True)
    flanc = np.cross(dos, avant)
    penche = np.radians(28) * K.lisse((np.asarray(s) - (LONG - 0.34)) / 0.24)[..., None]
    return centre, avant, dos * np.cos(penche) + flanc * np.sin(penche), flanc * np.cos(penche) - dos * np.sin(penche)


def couche(v):
    """Couche le boudin droit le long du fil ; la tête est un peu plus large que haute."""
    s = np.clip(v[:, 2], 0.0, LONG)
    centre, _avant, dos, flanc = repere(s)
    tete = K.lisse((s - (LONG - 0.135)) / 0.055)
    return centre + (v[:, 0] * (1 + 0.24 * tete))[:, None] * flanc + (v[:, 1] * (1 - 0.04 * tete))[:, None] * dos


def construire():
    a = K.Animal("couleuvre")
    a.taille = 0.90

    # ----- le corps : un boudin tourné tout droit, peint case par case (le dos, le damier du ventre, le collier),
    #       puis couché le long de son fil -----
    hauteurs = np.arange(0.0, LONG, PAS)
    corps = A.tour([(0.0, 0.0)] + [(float(rayon(s)), float(s)) for s in hauteurs[1:]] + [(0.0, LONG)], COTES)
    corps.teinte = np.tile(PERLE, (len(corps.v), 1))
    for k, anneau in enumerate(corps.anneaux):
        for j, i in enumerate(anneau if len(anneau) > 1 else []):
            c = 360.0 * (j + 0.5) / COTES                              # le milieu de la case que ce point colore
            angle = c if c <= 90 else 180 - c if c <= 270 else c - 360
            s = corps.v[i, 2]
            if LONG - 0.208 < s < LONG - 0.140:
                corps.teinte[i] = VIF                                  # le collier, qui fait tout le tour,
            elif LONG - 0.238 < s <= LONG - 0.208:
                corps.teinte[i] = OMBRE                                # et son liseré sombre
            elif angle < -18 and s < LONG - 0.140:                     # le ventre : un damier de cases de quatre mailles
                corps.teinte[i] = K.CREME if (k // 4 + ((j - 22) % COTES) // 4) % 2 else ARDOISE
            elif angle > 66 and s < LONG - 0.238:
                corps.teinte[i] = REFLET                               # le reflet ardoise du dos
    G.sillons(corps, [10], 0.003, 1.0)                         # la couture du dos creuse un peu le tissu
    a.piece("corps", corps.sculpte(couche), None)
    a.couture("dos", "corps", 10, 0.33, 0.46)

    # ----- le visage, tout en haut du col : deux gros boutons écartés, un sourire d'une joue à l'autre -----
    centre, avant, dos, flanc = (Vector(q) for q in repere(TETE))
    a.tete = centre + avant * 0.040
    for nom, cote in (("_G", 1), ("_D", -1)):
        p, n = a.surface("corps", centre, flanc * (0.52 * cote) + dos * 0.22 + avant * 0.82)
        a.bouton("oeil" + nom, p + n * 0.0015, n, 0.020)
    sourire = [avant * math.cos(t) + flanc * math.sin(t) + dos * (-0.36 + 0.20 * t * t) for t in np.linspace(-1.0, 1.0, 17)]
    a.broderie("sourire", a.trace("corps", centre, sourire, 0.0045), 0.0024)

    # ----- la langue fourchue : un brin de feutrine framboise qui sort du bout du nez et retombe un peu -----
    centre, avant, dos, flanc = (Vector(q) for q in repere(LONG - 0.014))
    devant, dessus = avant * math.cos(0.40) - dos * math.sin(0.40), dos * math.cos(0.40) + avant * math.sin(0.40)
    fourche = [(0.0, -0.0032), (0.040, -0.0036), (0.064, -0.0150), (0.069, -0.0115), (0.050, 0.0), (0.069, 0.0115), (0.064, 0.0150), (0.040, 0.0036), (0.0, 0.0032)]
    a.piece("langue", A.decoupe(fourche, 0.0034, 0.0012), K.FRAMBOISE, mat=A.cadre(centre - dos * 0.010, dessus, dessus.cross(devant)), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py couleuvre). Les mesures sont celles du modèle, avant a.taille.

from poses import Pose, borne, cloche, onde

# Un os tous les seize centimètres le long du fil, jusqu'à la nuque ; le « corps » est au milieu de la partie couchée :
# de lui part une chaîne vers la queue et une autre vers la tête. La langue pend à la tête. Le boudin est une seule pièce
# souple : chaque point suit les deux os qui l'encadrent le long du fil, la tête entière suit « tete ».
NOMS = ["queue7", "queue6", "queue5", "queue4", "queue3", "queue2", "queue1", "corps",
        "dos1", "dos2", "cou1", "cou2", "cou3", "cou4", "tete"]
OU = np.array([0.08, 0.24, 0.40, 0.56, 0.72, 0.88, 1.04, 1.20, 1.36, 1.52, 1.68, 1.82, 1.96, 2.10, LONG - 0.13])
MILIEU = 7
PARENT = ["racine" if k == MILIEU else NOMS[k + 1] if k < MILIEU else NOMS[k - 1] for k in range(len(NOMS))]

# le fil en 800 points (plus un à chaque os), et ce qu'il est au repos : le centre, la direction, le dos, le flanc
_base = np.linspace(0.0, LONG, 800)
_S = np.sort(np.concatenate([_base[np.abs(_base[:, None] - OU[None, :]).min(axis=1) > 0.001], OU]))
_IDX = np.searchsorted(_S, OU)
_X, _T, _DOS, _FLANC = repere(_S)
_H = _X[_IDX]                                          # les pivots des os
_PENTE = np.arcsin(np.clip(_T[:, 2], -1.0, 1.0))
_c, _av, _d, _GAUCHE_LANGUE = (np.asarray(q, float) for q in repere(LONG - 0.014))
LANGUE = _c - _d * 0.010                               # là où la langue sort du nez
_face = np.asarray(repere(TETE)[1], float) * [1, 1, 0]
_face = _face / np.linalg.norm(_face)                  # où regarde la tête, à plat
GAUCHE_FACE = np.array([-_face[1], _face[0], 0.0])     # l'axe à plat, à sa gauche : la tête y plonge vers l'avant
AVANT_TETE = np.asarray(repere(TETE)[1], float)
_col = np.asarray(repere(1.85)[1], float)
GAUCHE_COL = np.cross([0.0, 0.0, 1.0], _col) / np.linalg.norm(np.cross([0.0, 0.0, 1.0], _col))
HAUT = np.array([0.0, 0.0, 1.0])

OS = ([("racine", None, (0, 0, 0))]
      + [(NOMS[k], PARENT[k], tuple(float(x) for x in _H[k])) for k in [MILIEU] + list(range(MILIEU - 1, -1, -1)) + list(range(MILIEU + 1, len(NOMS)))]
      + [("langue", "tete", tuple(float(x) for x in LANGUE))])


def souple(points, cote):
    """Le boudin et ce qui y est cousu : chaque point retrouve sa distance le long du fil (le point du fil le plus
    proche), puis se partage en douceur entre les deux os qui l'encadrent."""
    s = np.empty(len(points))
    for d in range(0, len(points), 2000):
        q = points[d:d + 2000]
        s[d:d + 2000] = _S[np.argmin(((q[:, None, :] - _X[None, :, :]) ** 2).sum(-1), axis=1)]
    s = np.clip(s, OU[0], OU[-1])
    j = np.clip(np.searchsorted(OU, s, side="right") - 1, 0, len(OU) - 2)
    f = K.lisse((s - OU[j]) / (OU[j + 1] - OU[j]))
    return {n: np.where(j == k, 1 - f, 0.0) + np.where(j + 1 == k, f, 0.0) for k, n in enumerate(NOMS)}


# Le corps, la couture du dos et le sourire se rangent avec la tête (et non avec « corps ») : l'usine pend les paupières
# à l'os de rangement de la pièce voisine de l'œil, et elles doivent suivre la tête quand le col se plie.
PORTEURS = [("corps", souple, "tete"), ("dos", souple, "tete"), ("sourire", souple, "tete"), ("oeil", "tete"), ("langue", "langue"),
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


def tours(axe, radians):
    """La même, pour tout un tableau d'angles (en radians) : un tableau de matrices."""
    x, y, z = np.asarray(axe, float) / np.linalg.norm(axe)
    k = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    s, c = np.sin(radians)[:, None, None], np.cos(radians)[:, None, None]
    return np.eye(3) + s * k + (1 - c) * (k @ k)


def angles(R):
    """Les angles qu'attend Pose (degrés, autour des axes du monde : X, puis Y, puis Z) pour la rotation R."""
    return (math.degrees(math.atan2(R[2, 1], R[2, 2])), math.degrees(math.asin(-max(-1.0, min(1.0, R[2, 0])))),
            math.degrees(math.atan2(R[1, 0], R[0, 0])))


def cadres(avant, s, penche=1.0):
    """Les repères du boudin (en colonnes : la direction, le dos, le flanc gauche) le long d'un fil, faits comme ceux
    de repere() : le dos cherche le ciel, et vers la tête le boudin tourne sur lui-même (penche : 1 comme le modèle)."""
    dos = np.array([0.0, 0.0, 1.0]) - avant[:, 2:3] * avant
    dos = dos / np.linalg.norm(dos, axis=1, keepdims=True)
    flanc = np.cross(dos, avant)
    pc = np.radians(28) * penche * K.lisse((np.asarray(s) - (LONG - 0.34)) / 0.24)[:, None]
    return np.stack([avant, dos * np.cos(pc) + flanc * np.sin(pc), flanc * np.cos(pc) - dos * np.sin(pc)], axis=-1)


_F0 = cadres(_T[_IDX], OU)                             # le repère de chaque os au repos


def coudre(E, a, depart):
    """Remet bout à bout les petits morceaux du fil E (un par intervalle de _S), depuis le point d'indice a posé en
    « depart » : rend la place de chaque point du fil."""
    C = np.empty((len(_S), 3))
    C[a] = depart
    C[a + 1:] = depart + np.cumsum(E[a:], axis=0)
    C[:a] = depart - np.cumsum(E[:a][::-1], axis=0)[::-1]
    return C


def plier(plis_tete=(), plis_queue=()):
    """Plie le boudin à partir du « corps », qui ne bouge pas. Un pli : (où, demi-largeur, axe, degrés) ; l'axe est
    donné au repos, et le pli tourne tout ce qui est au-delà de lui (vers la tête, ou vers la queue). Rend, pour chaque
    os, sa rotation et où va son pivot (de quoi nourrir poser)."""
    R = np.broadcast_to(np.eye(3), (len(_S), 3, 3)).copy()
    for s0, demi, axe, deg in sorted(plis_tete, key=lambda q: q[0]):
        R = R @ tours(axe, math.radians(deg) * K.lisse((_S - s0 + demi) / (2 * demi)))
    for s0, demi, axe, deg in sorted(plis_queue, key=lambda q: -q[0]):
        R = R @ tours(axe, math.radians(deg) * K.lisse((s0 + demi - _S) / (2 * demi)))
    E = np.einsum("nij,nj->ni", 0.5 * (R[:-1] + R[1:]), np.diff(_X, axis=0))
    a = _IDX[MILIEU]
    C = coudre(E, a, _X[a])
    return [(R[i], C[i]) for i in _IDX]


def suivre(C, penche=1.0):
    """Couche le boudin le long d'un autre fil C (un point par point de _S, à la même distance de la queue) : chaque
    os prend le repère du nouveau fil à sa place."""
    T = np.gradient(C, _S, axis=0)
    T = T / np.linalg.norm(T, axis=1, keepdims=True)
    F = cadres(T[_IDX], OU, penche)
    return [(F[k] @ _F0[k].T, C[_IDX[k]]) for k in range(len(OU))]


def poser(p, W):
    """W[k] = (rotation, où va son pivot) : la place voulue de chaque os dans le monde. Écrit dans la pose ce que chaque
    os doit faire par rapport à son parent pour l'y mettre."""
    for k, nom in enumerate(NOMS):
        Q, P = W[k]
        if k == MILIEU:
            R, d = Q, P - _H[k]
        else:
            kp = NOMS.index(PARENT[k])
            Qp, Pp = W[kp]
            R, d = Qp.T @ Q, Qp.T @ (P - Pp) - (_H[k] - _H[kp])
        p.add(nom, rot=angles(R), pos=tuple(float(x) for x in d))


def langue(p, t, force, coups):
    """Les coups de langue : la fourche bat de haut en bas et rentre à moitié dans le nez (elle rapetisse vers lui),
    « coups » fois dans l'animation, avec la force donnée (0 : la langue tranquille, sortie comme sur le modèle)."""
    rentre = 1 - 0.5 * force * (0.5 + 0.5 * onde(t, coups, 0.25))
    p.add("langue", rot=angles(tour(_GAUCHE_LANGUE, 20 * force * onde(t, coups))), ech=(rentre, rentre, rentre))


def repos(t):
    """Lovée, curieuse de tout : le col se balance doucement et respire, elle regarde à gauche puis à droite, penche la
    tête encore un peu plus pour mieux voir, goûte l'air de deux salves de coups de langue, frétille du bout de la queue
    et cligne de ses gros yeux."""
    p = Pose()
    regard = cloche(t, 0.24, 0.12) - cloche(t, 0.66, 0.10)
    curieuse = cloche(t, 0.45, 0.10)
    poser(p, plier([(1.90, 0.12, HAUT, 5 * onde(t, 1)),
                    (1.85, 0.10, GAUCHE_COL, 2.5 * onde(t, 2)),
                    (2.17, 0.06, HAUT, 20 * regard),
                    (2.20, 0.04, AVANT_TETE, 16 * curieuse)],
                   [(0.14, 0.10, HAUT, 14 * cloche(t, 0.80, 0.08) * onde(t, 12))]))
    langue(p, t, cloche(t, 0.36, 0.05) + cloche(t, 0.88, 0.04), 30)
    p.ouvert = 1 - cloche(t, 0.12, 0.02) - cloche(t, 0.58, 0.02)
    return p


def avance(t):
    """Elle se déroule et ondule en S : une vague court de la tête vers la queue (une longueur par cycle) et le boudin
    glisse dans ses propres courbes ; le col reste levé, droit devant, la tête qui dodeline à peine, et la langue
    goûte le chemin."""
    p = Pose()
    cap = (-math.pi / 2 + 0.50 * (1 - K.lisse((_S - 1.25) / 0.40)) * np.sin(math.tau * (_S / 0.78 + t))
           + 0.06 * math.sin(math.tau * t) * K.lisse((_S - 1.65) / 0.30))
    pente = _PENTE * (1 - 0.40 * K.lisse((_S - 1.55) / 0.25))     # le col un peu plus bas qu'au repos
    T = np.stack([np.cos(pente) * np.cos(cap), np.cos(pente) * np.sin(cap), np.sin(pente)], axis=-1)
    E = 0.5 * (T[:-1] + T[1:]) * np.diff(_S)[:, None]
    a = int(np.searchsorted(_S, 1.62))
    poser(p, suivre(coudre(E, a, np.array([0.0, 0.0, _X[a, 2]])), 0.5))
    langue(p, t, 0.8, 4)
    return p


def mange(t):
    """Elle plonge le col vers l'avant jusqu'à l'herbe (devant elle, là où son corps ne passe pas), y pique trois fois
    du nez en goûtant de la langue, puis relève la tête et regarde alentour."""
    p = Pose()
    leve = cloche(t, 0.86, 0.12)
    bas = 1 - leve
    coups = max(0.0, onde(t, 3, -0.25)) ** 2 * bas
    poser(p, plier([(1.98, 0.10, GAUCHE_FACE, 62 * bas + 10 * coups),
                    (2.17, 0.06, HAUT, 12 * leve * onde(t, 2)),
                    (2.20, 0.04, GAUCHE_FACE, 22 * bas + 8 * coups - 6 * leve)]))
    langue(p, t, cloche(t, 0.20, 0.08) + cloche(t, 0.52, 0.08), 18)
    p.ouvert = 1 - cloche(t, 0.92, 0.03)
    return p


def joie(t):
    """Sa fête : elle se dresse tout en haut de son col, se dandine de gauche à droite en penchant la tête d'un côté puis
    de l'autre, la langue qui frétille et le bout de la queue qui bat ; puis elle se relove comme au repos."""
    p = Pose()
    env = doux(t / 0.20) * (1 - doux((t - 0.68) / 0.24))
    poser(p, plier([(1.86, 0.12, GAUCHE_FACE, -22 * env),
                    (1.98, 0.12, HAUT, 18 * env * onde(t, 2)),
                    (2.20, 0.04, AVANT_TETE, 18 * env * onde(t, 2, 0.25)),
                    (2.20, 0.04, GAUCHE_FACE, 16 * env)],
                   [(0.14, 0.10, HAUT, 28 * env * onde(t, 6)), (0.40, 0.14, HAUT, 10 * env * onde(t, 3, 0.2))]))
    langue(p, t, env, 16)
    return p


def spirale(serre):
    """Le fil du corps roulé à plat pour dormir : une spirale, la tête au milieu, la queue dehors ; serre (≈ 1) la
    resserre un peu : elle respire."""
    th = np.linspace(0.0, 5 * math.pi, 4000)
    rho = 0.085 * serre + 0.086 / math.tau * th
    x, y = rho * np.cos(th + 2.0), 0.03 + rho * np.sin(th + 2.0)
    u = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    q = LONG - _S
    w = K.lisse((_S - 1.50) / 0.10)
    z = _X[:, 2] * (1 - w) + 0.035 * w + 0.024 * K.lisse((_S - (LONG - 0.25)) / 0.12)
    return np.stack([np.interp(q, u, x), np.interp(q, u, y), z], axis=-1)


def dort(t):
    """Roulée en spirale à plat, la tête au milieu posée sur la joue, la langue rentrée, les yeux fermés ; la spirale se
    resserre et se relâche à peine, au rythme d'une respiration lente."""
    p = Pose()
    p.ouvert = 0.0
    poser(p, suivre(spirale(1 + 0.03 * onde(t, 1)), 1.3))
    p.add("langue", ech=(0.35, 0.35, 0.35))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Couleuvre")
