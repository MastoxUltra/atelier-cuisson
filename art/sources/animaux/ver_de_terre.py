"""Le ver de terre en peluche, deuxième dessin : le notable du potager. Un long boudin annelé rose pêche, lové en fer à
cheval sur l'herbe comme une corde sur un quai, d'où il se dresse tout droit, haut comme une colonne, le buste un peu
cambré en arrière ; tout en haut, la tête se penche vers vous, le nez levé : il vous toise. Les paupières tombent à
moitié sur deux petits yeux, un sourcil est haussé, la bouche fait la moue d'un côté. À mi-hauteur, son anneau clair
est une vraie manche de feutrine crème, gonflée, cousue de bleu canard à ses deux bords ; une pièce bleu canard est
reprisée sur la boucle couchée. Le bout de la queue relève en virgule.

    python ver_de_terre.py        fabrique la fiche art/apercus/animaux/ver_de_terre.png
    (le premier dessin, jamais gardé : ver_de_terre_ancien.py)
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

PECHE = np.array(M.hexa("#ffb4aa"))           # le corps : un rose pêche (le poil le fonce un peu)
VIEUX_ROSE = np.array(M.hexa("#d9868a"))      # le fond des sillons, les paupières
CLAIR = np.array(M.hexa("#fff0e2"))           # la manche (le clitellum) et le ventre
CANARD = M.hexa("#1f7680")                    # l'accent : les ourlets de la manche, la pièce reprisée
RAYON = 0.031                                 # le rayon du boudin
PAS = 0.020                                   # l'écart entre deux anneaux
COTES = 36

# Le fil du corps, de la queue au museau, donné par le BAS du boudin (le kit y ajoute le rayon) : la queue relevée en
# virgule, une boucle couchée en fer à cheval autour de (0, 0,035), puis la colonne qui monte, cambrée, et la tête
# qui se penche en avant, tournée vers sa gauche.
def _boucle():
    pts = [(0.084, -0.046, 0.022), (0.072, -0.030, 0.004)]
    for degres in np.linspace(-35, 228, 9):
        t = math.radians(degres)
        pts.append((0.078 * math.cos(t), 0.035 + 0.078 * math.sin(t), 0.0))
    return pts


CHEMIN = _boucle() + [(-0.030, -0.060, 0.004), (-0.012, -0.076, 0.040), (-0.004, -0.072, 0.095), (0.0, -0.056, 0.150),
                      (0.002, -0.042, 0.200), (0.006, -0.046, 0.246), (0.018, -0.074, 0.276), (0.036, -0.108, 0.286),
                      (0.050, -0.136, 0.282)]
_bas = A.courbe(CHEMIN, 14)
_fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(_bas, axis=0), axis=1))])
LONG = float(_fait[-1])
SELLE = (LONG - 0.205, LONG - 0.150)          # là où commence et finit la manche


def dans_la_selle(s):
    """1 dans la manche, 0 ailleurs, avec des bords francs."""
    return K.lisse((s - SELLE[0]) / 0.004) * K.lisse((SELLE[1] - s) / 0.004)


def sillon(s):
    """1 au creux entre deux anneaux, 0 sur le rond de l'anneau. Ni la manche, ni la tête, ni le bout de la queue n'en ont."""
    creux = np.exp(-((np.abs((s + PAS / 2) % PAS - PAS / 2)) / 0.0034) ** 2)
    return creux * (1 - dans_la_selle(s)) * K.lisse((LONG - 0.060 - s) / 0.01) * K.lisse((s - 0.03) / 0.02)


def rayon(s):
    """Le rayon du boudin : une queue effilée, des anneaux, l'avant plus fort, une manche gonflée, une tête ronde."""
    r = RAYON * min(1.0, (s / 0.11) ** 0.55) * (1 + 0.10 * float(K.lisse((s - (LONG - 0.36)) / 0.12)))
    r *= 1 + 0.12 * float(dans_la_selle(s)) + 0.08 * math.exp(-((s - (LONG - 0.040)) / 0.030) ** 2)
    r *= 1 - 0.15 * float(sillon(s))
    bout = 0.036                                        # la calotte ronde du museau
    if s > LONG - bout:
        r *= math.sqrt(max(0.0, 1 - ((s - (LONG - bout)) / bout) ** 2))
    return r


# le fil des centres : le bas du boudin relevé de son rayon (à plat sur la boucle, il pose sur l'herbe)
_r = np.array([RAYON * min(1.0, (s / 0.11) ** 0.55) for s in _fait])
FIL = _bas + np.outer(_r, [0, 0, 1]) * (1 - K.lisse((_bas[:, 2] - 0.02) / 0.06))[:, None] + np.outer(
    K.lisse((_bas[:, 2] - 0.02) / 0.06) * RAYON, [0, 0, 1])
FAIT = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(FIL, axis=0), axis=1))])
FAIT *= LONG / FAIT[-1]


def _cadres():
    """Le long du fil, des repères qui ne vrillent pas (transport parallèle) : la direction, le dos, le flanc.
    Sur la boucle couchée, le dos regarde le ciel ; sur la colonne, il passe derrière ; sur la tête, il revient en haut."""
    sens = np.gradient(FIL, FAIT, axis=0)
    sens /= np.linalg.norm(sens, axis=1, keepdims=True)
    dos = np.zeros_like(sens)
    d = np.array([0.0, 0.0, 1.0]) - sens[0, 2] * sens[0]
    dos[0] = d / np.linalg.norm(d)
    for i in range(1, len(sens)):
        d = dos[i - 1] - np.dot(dos[i - 1], sens[i]) * sens[i]
        dos[i] = d / np.linalg.norm(d)
    return sens, dos, np.cross(dos, sens)


SENS, DOS, FLANC = _cadres()


def repere(s):
    """En un point du fil : le centre du boudin, la direction où il va, son dos et son flanc gauche."""
    def lu(t):
        return np.stack([np.interp(s, FAIT, t[:, k]) for k in range(3)], axis=-1)
    centre, avant, dos = lu(FIL), lu(SENS), lu(DOS)
    avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
    dos = dos - np.sum(dos * avant, axis=-1, keepdims=True) * avant
    dos = dos / np.linalg.norm(dos, axis=-1, keepdims=True)
    return centre, avant, dos, np.cross(dos, avant)


def couche(v):
    """Couche le boudin droit le long du fil : son +Y devient le dos, son +X le flanc."""
    centre, _avant, dos, flanc = repere(np.clip(v[:, 2], 0.0, LONG))
    return centre + v[:, 0:1] * flanc + v[:, 1:2] * dos


def construire():
    a = K.Animal("ver_de_terre")
    a.taille = 0.44
    a.poil_long = 0.0026                                # une peluche rase : les anneaux doivent se lire

    # ----- le corps : un boudin tourné tout droit, annelé, peint, puis couché le long de son fil -----
    pas = np.arange(0.0, LONG, PAS / 12)                # douze tours par anneau : un tour tombe pile au fond de chaque sillon
    profil = [(rayon(s), s) for s in pas] + [(0.0, LONG)]
    profil[0] = (0.0, 0.0)
    corps = A.tour(profil, COTES)
    s, bas = corps.v[:, 2], K.lisse((-corps.v[:, 1] / RAYON - 0.30) / 0.35)
    robe = PECHE + (CLAIR - PECHE) * np.maximum(dans_la_selle(s), 0.40 * bas)[:, None]       # la manche et le ventre, clairs
    corps.teinte = robe + (VIEUX_ROSE - robe) * (0.65 * sillon(s) * (1 - bas))[:, None]       # le fond des sillons, vieux rose
    G.sillons(corps, [9], 0.003, 1.0)                   # la couture du dos creuse un peu le tissu
    a.piece("corps", corps.sculpte(couche), None)
    a.couture("dos", "corps", 9, 0.06, 0.52, fil=M.hexa("#c46f76"), large=0.008, haut=0.0035, pas=0.013)
    for nom, bord in (("manche_bas", SELLE[0]), ("manche_haut", SELLE[1])):                  # la manche, ourlée aux deux bords
        a.ourlet(nom, "corps", bord / LONG, fil=CANARD, haut=0.0040, pas=0.010)
    a.couture("manche", "corps", 27, SELLE[0] / LONG + 0.004, SELLE[1] / LONG - 0.004, "droit", fil=CANARD,
              large=0.007, haut=0.0025, pas=0.009)                                          # et fermée d'une couture sur le côté

    # ----- une pièce reprisée bleu canard, sur la boucle couchée, de notre côté -----
    centre, avant, dos, flanc = (Vector(q) for q in repere(0.20 * LONG))
    a.rustine("piece", "corps", centre, flanc * 0.80 + dos * 0.60, 0.50, CANARD, 0.003, 14, fil=tuple(CLAIR))

    # ----- le visage, en haut de la colonne : deux petits yeux à demi fermés, un sourcil haussé, la moue -----
    centre, avant, dos, flanc = (Vector(q) for q in repere(LONG - 0.040))
    a.tete = centre + avant * 0.030
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("corps", centre, avant * 0.78 + flanc * (0.56 * cote) + dos * 0.30)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0105)
        a.piece("lourde_" + nom, K.paupiere(0.0105, -0.05 if cote > 0 else 0.05), tuple(VIEUX_ROSE),
                mat=A.cadre(p + n * 0.004, n, dos + flanc * (0.15 * cote)), poil=False)
    # le sourcil gauche, haussé très haut au-dessus de l'œil : le dédain
    sourcil = [avant * (0.78 - 0.12 * u) + flanc * (0.28 + 0.44 * u) + dos * (0.68 + 0.14 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 6)]
    a.broderie("sourcil", A.courbe(a.trace("corps", centre, sourcil, 0.004), 3), 0.0024, K.BRUN)
    # la moue : un trait court, pincé, qui tombe d'un seul côté
    moue = [avant * 0.92 + flanc * x + dos * y for x, y in ((-0.20, -0.30), (-0.04, -0.32), (0.10, -0.36), (0.20, -0.46))]
    a.broderie("moue", A.courbe(a.trace("corps", centre, moue, 0.004), 4), 0.0022, K.BRUN)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py ver_de_terre). Les mesures sont celles du modèle, avant a.taille.
# Le boudin est une seule pièce souple que neuf os se passent le long de son fil : du « corps », au pied de la colonne
# (là où il quitte l'herbe), une chaîne part vers la queue le long de la boucle couchée, une autre monte la colonne
# jusqu'à la tête. Tout ce qui est cousu dessus (la couture, la manche, la pièce, le sourcil, la moue) suit le même fil.

from poses import Pose, borne, cloche, onde

# chaque os et sa place le long du fil (en mètres depuis le bout de la queue), de la queue à la tête
NOMS = ["queue", "boucle1", "boucle2", "corps", "col1", "col2", "col3", "cou", "tete"]
OU = np.array([0.040, 0.160, 0.300, 0.430, 0.500, 0.570, 0.640, 0.700, 0.760])
MILIEU = 3
PARENT = ["racine" if k == MILIEU else NOMS[k + 1] if k < MILIEU else NOMS[k - 1] for k in range(len(NOMS))]
_PIVOTS = repere(OU)[0]

OS = [("racine", None, (0, 0, 0))] + [(NOMS[k], PARENT[k], tuple(round(float(x), 4) for x in _PIVOTS[k]))
                                      for k in [MILIEU] + list(range(MILIEU - 1, -1, -1)) + list(range(MILIEU + 1, len(NOMS)))]


def _abscisse(points):
    """Pour chaque point : sa place le long du fil des centres, au pied de la perpendiculaire sur le tronçon le plus proche."""
    a, ab = FIL[:-1], np.diff(FIL, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    s = np.empty(len(points))
    for d in range(0, len(points), 2000):
        q = points[d:d + 2000]
        ap = q[:, None, :] - a[None, :, :]
        u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
        j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
        s[d:d + 2000] = FAIT[j] + u[np.arange(len(q)), j] * (FAIT[j + 1] - FAIT[j])
    return s


def souple(points, cote):
    """Le boudin et ce qui y est cousu : chaque point se partage en douceur entre les deux os qui l'encadrent le long
    du fil ; le bout de la queue suit « queue », toute la tête suit « tete »."""
    s = np.clip(_abscisse(points), OU[0], OU[-1])
    j = np.clip(np.searchsorted(OU, s, side="right") - 1, 0, len(OU) - 2)
    f = K.lisse((s - OU[j]) / (OU[j + 1] - OU[j]))
    return {n: np.where(j == k, 1 - f, 0.0) + np.where(j + 1 == k, f, 0.0) for k, n in enumerate(NOMS)}


# Le boudin et tout ce qui y est cousu se rangent avec la tête : l'usine pend les paupières à l'os de rangement de la
# pièce voisine de l'œil, et elles doivent suivre la tête quand la colonne se plie.
PORTEURS = [("corps", souple, "tete"), ("dos", souple, "tete"), ("manche", souple, "tete"), ("piece", souple, "tete"),
            ("sourcil", souple, "tete"), ("moue", souple, "tete"), ("oeil", "tete"), ("lourde", "tete"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]

PENCHE_MANGE = (140.0, 22.0, 6.0)             # mange : le pli de la colonne, du cou, de la tête pour atteindre l'herbe
COUCHE = (-46.0, 0.0, -46.0, -46.0, 0.0, 0.0, 20.0)     # dort : col1 (cambré, tourné), col2, col3, cou, tete (cambrée, roulée)


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _plie(p, degres):
    """Plie la colonne vers l'avant (degrés > 0) ou la cambre en arrière (< 0), le pli réparti sur ses trois os."""
    for o in ("col1", "col2", "col3"):
        p.add(o, rot=(degres / 3, 0, 0))


def repos(t):
    """Le notable toise son potager : la colonne respire et se balance à peine, il détourne la tête vers sa droite
    d'un air las, puis revient à nous et lève le nez avec un petit « hmpf » qui le cambre ; le bout de la queue
    tapote l'herbe, impatient ; il cligne lentement sous ses paupières lourdes."""
    p = Pose()
    r = onde(t, 2)
    p.add("col2", ech=(1 + 0.025 * r, 1 + 0.025 * r, 1 + 0.008 * r))
    p.add("col1", rot=(1.5 * r, 2 * onde(t, 1), 0))
    p.add("col3", rot=(0, -1.5 * onde(t, 1, 0.1), 0))
    las = cloche(t, 0.28, 0.13)
    hmpf = cloche(t, 0.56, 0.08)
    p.add("cou", rot=(-5 * hmpf, 0, -12 * las))
    p.add("tete", rot=(-14 * hmpf + 4 * las, -6 * las, -22 * las))
    _plie(p, -6 * hmpf)
    p.add("queue", rot=(0, 0, 14 * cloche(t, 0.80, 0.09) * onde(t, 10)))
    p.ouvert = 1 - cloche(t, 0.12, 0.03) - cloche(t, 0.68, 0.03)
    return p


def avance(t):
    """Il rampe à la façon des vers : une vague de poussée court de la colonne vers la queue le long de la boucle
    couchée, qui glisse sur l'herbe en ondulant ; la colonne s'étire et se tasse comme un accordéon, et la tête,
    digne, garde le cap en dodelinant à peine."""
    p = Pose()
    p.add("boucle2", rot=(0, 0, 5 * onde(t, 1)))
    p.add("boucle1", rot=(0, 0, 7 * onde(t, 1, -0.2)))
    p.add("queue", rot=(0, 0, 10 * onde(t, 1, -0.4)))
    p.add("col1", rot=(6 * onde(t, 1), 0, 0))
    p.add("col2", rot=(-5 * onde(t, 1, -0.15), 0, 0), pos=(0, 0, 0.006 * onde(t, 1, 0.25)))
    p.add("col3", rot=(-3 * onde(t, 1, -0.3), 0, 0), pos=(0, 0, 0.005 * onde(t, 1, 0.10)))
    p.add("cou", rot=(2 * onde(t, 1, -0.45), 0, 0))
    p.add("tete", rot=(0, 3 * onde(t, 1, 0.25), 0))
    return p


def mange(t):
    """Il se penche de toute sa hauteur jusqu'à l'herbe devant lui, y mordille trois fois du bout du museau, puis se
    redresse et mâche en regardant ailleurs, l'air de rien."""
    p = Pose()
    bas = _plateau(t, 0.42, 0.24, 0.16)
    coups = max(0.0, onde(t, 6)) ** 2 * _plateau(t, 0.42, 0.18, 0.06)
    leve = cloche(t, 0.86, 0.10)
    _plie(p, PENCHE_MANGE[0] * bas)
    p.add("cou", rot=(PENCHE_MANGE[1] * bas, 0, 0))
    p.add("tete", rot=(PENCHE_MANGE[2] * bas + 10 * coups, 0, -14 * leve * onde(t, 2)))
    p.add("queue", rot=(0, 0, 6 * onde(t, 2) * bas))
    p.ouvert = 1 - cloche(t, 0.94, 0.03)
    return p


def joie(t):
    """Sa fête, toute en retenue : il se grandit tant qu'il peut, se cambre en arrière le nez au ciel, se dandine
    deux fois d'un côté à l'autre comme on salue la foule, et la virgule de sa queue frétille ; puis il reprend la pose."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85)) if t < 0.85 else 0.0
    dandine = onde(borne(t / 0.85), 2) * env
    _plie(p, -12 * env)
    p.add("col2", pos=(0, 0, 0.012 * env), rot=(0, 9 * dandine, 0))
    p.add("col3", pos=(0, 0, 0.010 * env), rot=(0, 5 * dandine, 0))
    p.add("cou", rot=(-8 * env, 0, 0))
    p.add("tete", rot=(-12 * env, -6 * dandine, 0))
    p.add("queue", rot=(0, 0, 26 * onde(t, 7) * env))
    p.add("boucle1", rot=(0, 0, 6 * onde(t, 3.5) * env))
    return p


def dort(t):
    """Il s'endort comme un notable dans son fauteuil : la colonne se renverse en arrière au-dessus de sa boucle, la tête
    retombe dans l'herbe derrière elle, la joue contre le boudin et le nez au ciel, les yeux fermés ; le boudin se gonfle
    et se dégonfle lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("col1", rot=(COUCHE[0], 0, COUCHE[1]))
    p.add("col2", rot=(COUCHE[2], 0, 0), ech=(1 + 0.03 * r, 1 + 0.03 * r, 1 + 0.01 * r))
    p.add("col3", rot=(COUCHE[3], 0, 0))
    p.add("cou", rot=(COUCHE[4], 0, 0))
    p.add("tete", rot=(COUCHE[5], COUCHE[6], 0))
    p.add("boucle2", ech=(1 + 0.02 * r, 1 + 0.02 * r, 1 + 0.02 * r))
    p.add("queue", rot=(0, 0, 10))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Ver de terre")
