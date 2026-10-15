"""Le phasme en peluche : une brindille vivante. Un corps interminable brun noisette clair, à peine sinueux, trois nœuds
de bois cerclés d'écorce, un moignon de rameau coupé net, deux plaques de lichen jaune, une petite tête, six pattes
très longues renflées au genou comme des rameaux. Un flegmatique qui fait semblant d'être une branche : dressé en
oblique sur ses quatre pattes arrière, les deux de devant tendues droit devant lui dans le prolongement du corps,
la bouche plate, un œil fermé, et l'autre à demi ouvert pour vérifier qu'on y croit.

    python phasme.py        fabrique la fiche art/apercus/animaux/phasme.png
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

NOISETTE = M.hexa("#efd8b4")                  # la peluche du corps : elle sort brun noisette clair (le poil fonce et dore beaucoup)
BOIS = M.hexa("#c9a06c")                      # le même en feutrine, pour les pattes
ECORCE = M.hexa("#7a5230")                    # les nœuds, les genoux, le bout des pattes, les paupières
LICHEN = K.JAUNE                              # l'accent : deux plaques de lichen

# Sur la fiche, il était posé de biais (TOURNE = -25) : une brindille vue par le bout ne ressemble à rien.
# Pour le jeu, il regarde droit devant (vers -Y) : TOURNE = 0.
TOURNE = 0
LOC = A.repere((0, 0, 0), (0, 0, TOURNE))

RAYON = 0.034
# Le fil du corps, du bout de la queue au cou : une oblique à peine sinueuse ; les trois points du milieu sont ses nœuds.
CHEMIN = [(0.000, 0.360, 0.050), (0.022, 0.135, 0.200), (-0.020, -0.010, 0.280), (0.012, -0.150, 0.395), (0.000, -0.215, 0.445)]
_PTS = A.courbe(CHEMIN, 16)
_FAIT = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(_PTS, axis=0), axis=1))])
_SENS = np.gradient(_PTS, _FAIT, axis=0)
LONG = float(_FAIT[-1])
NOEUDS = [float(_FAIT[16 * k]) for k in (1, 2, 3)]      # la distance de chaque nœud au bout de la queue


def repere(s):
    """En un point du fil : le centre du corps, la direction où il va, son dos (vers le ciel) et son côté gauche."""
    s = np.asarray(s, float)
    centre = np.stack([np.interp(s, _FAIT, _PTS[:, k]) for k in range(3)], axis=-1)
    avant = np.stack([np.interp(s, _FAIT, _SENS[:, k]) for k in range(3)], axis=-1)
    avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
    dos = np.array([0.0, 0.0, 1.0]) - avant[..., 2:3] * avant
    dos = dos / np.linalg.norm(dos, axis=-1, keepdims=True)
    return centre, avant, dos, np.cross(dos, avant)


COU = [Vector(q) for q in repere(LONG)]
TETE = COU[0] + COU[1] * 0.048 + COU[2] * 0.006
PORT = LOC @ A.repere(TETE, (-24, 7, 18))     # la tête : dans l'axe de la brindille, à peine tournée vers nous
CENTRE = PORT @ Vector((0, 0, 0))


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def rayon(s):
    """Le rayon du corps à la distance s du bout de la queue : la queue plus fine, un renflement à chaque nœud, le cou pincé."""
    s = np.asarray(s, float)
    r = RAYON * (0.62 + 0.38 * K.lisse(s / 0.10))
    for n in NOEUDS:
        r = r * (1 + 0.42 * np.exp(-((s - n) / 0.020) ** 2))
    return r * (1 - 0.18 * K.lisse((s - (LONG - 0.055)) / 0.04))


def couche(v):
    """Pour sculpte() : couche le long du fil une pièce tournée toute droite (son X : la gauche, son Y : le dos)."""
    centre, _avant, dos, cote = repere(np.clip(v[:, 2], 0.0, LONG))
    return centre + v[:, 0:1] * cote + v[:, 1:2] * dos


def rameau(points, paliers=None):
    """Une patte : un rameau de feutrine le long d'une ligne brisée aux angles arrondis, renflé au premier angle (le
    genou), peint par tronçons nets : paliers = [(fraction du chemin, couleur), ...]. Par défaut, le genou et le bout
    sont en écorce. Le chemin est recoupé tous les 4 mm pour que la limite des couleurs reste nette."""
    pts = [np.asarray(p, float) for p in points]
    morceaux = [np.linalg.norm(b - a) for a, b in zip(pts[:-1], pts[1:])]
    genou = morceaux[0] / sum(morceaux)
    ch = A.conges(pts, 0.022, 5)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(ch, axis=0), axis=1))])
    t = np.linspace(0.0, 1.0, max(8, int(fait[-1] / 0.004)))
    ch = np.stack([np.interp(t * fait[-1], fait, ch[:, k]) for k in range(3)], axis=1)
    m = A.tube(ch, lambda u: 0.0140 - 0.0040 * u + 0.0050 * math.exp(-((u - genou) / 0.030) ** 2), 12)
    t = np.concatenate([np.repeat(t, 12), [0.0, 1.0]])           # les anneaux du tube, puis ses deux bouchons
    m.teinte = np.zeros((len(t), 3))
    for seuil, couleur in reversed(paliers or [(genou - 0.028, BOIS), (genou + 0.028, ECORCE), (0.91, BOIS), (9, ECORCE)]):
        m.teinte[t <= seuil] = couleur
    return m


def construire():
    a = K.Animal("phasme")
    a.taille = 0.55
    a.tete = PORT @ Vector((0.01, -0.050, 0.0))

    # ----- le corps : une longue baguette de peluche noisette, tournée toute droite avec ses trois nœuds, peinte par
    #       tranches (une bague d'écorce sur chaque nœud, le bout de la queue coupé net, clair comme du bois frais),
    #       puis couchée le long de son fil -----
    paliers = [(0.007, K.CREME)] + [q for n in NOEUDS for q in ((n - 0.010, NOISETTE), (n + 0.010, ECORCE))] + [(9, NOISETTE)]
    cotes = sorted(set(np.linspace(0.0, LONG, 150).tolist() + [z + e for z, _c in paliers[:-1] for e in (-0.0012, 0.0012)]))
    corps = K.bandes(A.tour([(0.0, 0.0)] + [(float(rayon(z)), z) for z in cotes[1:-1]] + [(0.0, LONG)], 32), paliers)
    a.piece("corps", corps.sculpte(couche), None, mat=LOC)
    a.couture("dos", "corps", 8, 0.36, 0.56, fil=ECORCE)

    # ----- le moignon : un rameau coupé net qui sort du nœud du milieu, sa tranche claire -----
    c, avant, dos, gauche = (Vector(q) for q in repere(NOEUDS[1]))
    pousse = (dos * 0.85 - avant * 0.50 + gauche * 0.15).normalized()
    moignon = A.tour(A.conges([(0, 0), (0.023, 0), (0.020, 0.086), (0.016, 0.096), (0, 0.096)], 0.004, 4), 24)
    a.piece("moignon", K.bandes(moignon, [(0.089, ECORCE), (9, K.CREME)]), None, mat=LOC @ A.repere(c + pousse * 0.012, A.viser(pousse)), poil=False)

    # ----- le lichen : deux plaques de feutrine jaune cousues sur le bois, allongées dans le sens de la brindille -----
    for nom, s, autour, grand, petit in (("lichen_1", 0.5 * (NOEUDS[0] + NOEUDS[1]) - 0.01, 0.9, 1.05, 0.62), ("lichen_2", 0.56 * NOEUDS[0], 0.35, 0.80, 0.50)):
        c, avant, dos, gauche = (Vector(q) for q in repere(s))
        axe = LOC.to_3x3() @ (dos * math.cos(autour) + gauche * math.sin(autour))
        e1 = axe.cross(Vector((0, 0, 1))).normalized()
        e2 = axe.cross(e1)
        file = LOC.to_3x3() @ avant
        penche = math.atan2(file.dot(e2), file.dot(e1))
        a.rustine(nom, "corps", LOC @ c, axe, lambda th, g=grand, p=petit, q=penche: g * p / math.hypot(p * math.cos(th - q), g * math.sin(th - q)),
                  LICHEN, 0.003, 12, fil=K.CREME)

    # ----- la tête : petite, en bourgeon ; deux globes sur les côtés, un bouton sur chacun -----
    a.piece("tete", A.boule(1.0, 48, 24).etire(0.047, 0.062, 0.045), NOISETTE, mat=PORT)
    for nom, cote in (("_G", 1), ("_D", -1)):
        globe = PORT @ Vector((0.038 * cote, -0.016, 0.026))
        regard = vers(0.80 * cote, -0.52, 0.30).normalized()
        a.piece("globe" + nom, A.boule(0.030, 32, 16), NOISETTE, pos=globe)
        a.bouton("oeil" + nom, globe + regard * 0.030, regard, 0.024)
        monte = vers(0, 0, 1)
        monte = (monte - regard * monte.dot(regard)).normalized()
        if cote > 0:
            # l'œil gauche, de notre côté : entrouvert sous une lourde paupière d'écorce
            lourde = A.boule(1.0, 28, 14).sculpte(lambda v: np.column_stack([v[:, 0], np.maximum(v[:, 1], 0.0), v[:, 2]])).etire(0.033, 0.034, 0.014)
            a.piece("lourde" + nom, lourde, ECORCE, mat=A.cadre(globe + regard * 0.027 + monte * 0.015, regard, monte), poil=False)
        else:
            # l'œil droit : fermé, la paupière tirée sur tout le bouton, un trait de fil pour les cils
            a.piece("lourde" + nom, A.boule(0.0355, 28, 14), ECORCE, pos=globe + regard * 0.0055, poil=False)
            travers = monte.cross(regard)
            cils = [globe + regard * 0.0055 + (regard * math.cos(t) + travers * math.sin(t) - monte * (0.20 + 0.25 * math.cos(t))).normalized() * 0.0375
                    for t in np.linspace(-0.95, 0.95, 11)]
            a.broderie("cils" + nom, cils, 0.0036, K.BRUN)
    # la bouche : un long trait tout plat, qui fait le tour du museau : celle de quelqu'un que rien n'étonne
    bouche = a.trace("tete", CENTRE, [vers(-0.45, -0.80, -0.34), vers(-0.15, -1, -0.36), vers(0.15, -1, -0.36), vers(0.45, -0.80, -0.34), vers(0.75, -0.48, -0.32)], 0.004)
    a.broderie("bouche", A.courbe(bouche, 5), 0.0034, K.BRUN)

    # ----- les deux pattes de devant : tendues droit devant lui, serrées sous le menton, dans le prolongement du corps -----
    c, avant, dos, gauche = (Vector(q) for q in repere(NOEUDS[2]))
    for nom, cote, portee in (("_G", 1, 0.325), ("_D", -1, 0.285)):
        hanche = c + gauche * (0.014 * cote) - dos * 0.016
        coude = c + avant * 0.070 + gauche * (0.028 * cote) - dos * 0.050
        bout = c + avant * portee + gauche * (0.013 * cote) - dos * (0.040 if cote > 0 else 0.026)
        a.piece("patte_avant" + nom, rameau([hanche, coude, bout]), None, mat=LOC, poil=False)

    # ----- les quatre pattes d'appui : très longues, plantées loin de chaque côté, celles de derrière rejetées en arrière -----
    for nom, noeud, genou, pose in (("milieu", NOEUDS[1], {1: (0.150, -0.035, 0.040), -1: (0.150, -0.045, 0.040)}, {1: (0.235, -0.105), -1: (0.225, -0.140)}),
                                    ("arriere", NOEUDS[0], {1: (0.140, 0.070, 0.022), -1: (0.135, 0.115, 0.005)}, {1: (0.205, 0.175), -1: (0.200, 0.205)})):
        c, avant, dos, gauche = (Vector(q) for q in repere(noeud))
        for cote_nom, cote in (("_G", 1), ("_D", -1)):
            hanche = c + gauche * (0.016 * cote) - dos * 0.008
            pied = Vector((c.x + pose[cote][0] * cote, c.y + pose[cote][1], 0.0105))
            points = [hanche, c + Vector((genou[cote][0] * cote, genou[cote][1], genou[cote][2])), pied, pied + Vector((0.026 * cote, -0.012, -0.002))]
            a.piece("patte_%s%s" % (nom, cote_nom), rameau(points), None, mat=LOC, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py phasme)

from poses import Pose, borne, cloche, onde

# Le corps est une brindille raide : il bascule tout entier autour du bout de sa queue, posé dans l'herbe, comme une
# branche dans le vent. Les quatre pattes d'appui sont souples : la cuisse suit le corps, le pied reste où il est posé
# (un os par pied, pendu à la racine), et la jambe se partage entre les deux. Il est cousu de travers (le corps ondule,
# chaque patte a sa pose) : les os de droite ne sont pas des miroirs, ils ont chacun leur place (noms en minuscules).
OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.355, 0.035)),           # le bout de la queue, posé dans l'herbe : la brindille bascule autour
    ("tete", "corps", (0, -0.205, 0.438)),            # le cou
    ("avant_g", "corps", (0.027, -0.159, 0.383)),     # les épaules des deux pattes de devant, tendues sous le menton
    ("avant_d", "corps", (-0.001, -0.161, 0.383)),
    ("pied_milieu_g", "racine", (0.215, -0.115, 0.010)),     # les quatre pieds posés
    ("pied_milieu_d", "racine", (-0.245, -0.150, 0.010)),
    ("pied_arriere_g", "racine", (0.227, 0.310, 0.010)),
    ("pied_arriere_d", "racine", (-0.178, 0.340, 0.010)),
]


def bras(points, cote):
    """Une patte de devant suit, toute raide, l'os de son épaule (à gauche ou à droite)."""
    return {"avant" + cote.lower(): np.ones(len(points))}


def jambe(points, cote):
    """Une patte d'appui : du bassin au genou (le point le plus haut), elle suit le corps ; du genou au pied, elle passe
    peu à peu au pied, qui reste posé. Une patte de droite arrive en miroir (x > 0) : la hanche est au plus petit x."""
    pied = ("pied_milieu" if points[:, 1].mean() < 0.05 else "pied_arriere") + cote.lower()
    genou = points[:, 2].max() - 0.020
    w = np.clip((genou - points[:, 2]) / (genou - 0.012), 0.0, 1.0) * K.lisse((points[:, 0] - points[:, 0].min()) / 0.05)
    return {"corps": 1 - w, pied: w}


PORTEURS = [("corps", "corps"), ("dos", "corps"), ("moignon", "corps"), ("lichen", "corps"), ("tete", "tete"), ("globe", "tete"),
            ("oeil", "tete"), ("lourde", "tete"), ("cils", "tete"), ("bouche", "tete"),
            ("patte_avant", bras, "corps"), ("patte_milieu", jambe, "corps"), ("patte_arriere", jambe, "corps"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]

PIEDS = ("pied_milieu_g", "pied_milieu_d", "pied_arriere_g", "pied_arriere_d")


def _vent(p, t, force):
    """Le balancement de la brindille : d'avant en arrière, inégal comme une rafale (deux grands, trois petits par
    boucle), avec un rien de roulis ; « force » en degrés. Le bout de la queue ne bouge pas, les pieds non plus."""
    avant = onde(t, 2) + 0.45 * onde(t, 3)
    p.add("corps", rot=(force * avant, 0.35 * force * onde(t, 1), -0.15 * force * onde(t, 2)), pos=(0, -0.0022 * force * avant, 0))
    return avant


def repos(t):
    """Il fait la branche : il se balance d'avant en arrière comme une brindille au vent, sans un geste de trop.
    Une fois par boucle, la tête se tourne à peine vers nous, l'œil entrouvert cligne (on y croit ?), puis reprend sa pose."""
    p = Pose()
    avant = _vent(p, t, 3.4)
    verifie = cloche(t, 0.62, 0.10)
    p.add("tete", rot=(-1.2 * avant + 4 * verifie, 0, 14 * verifie))
    p.add("avant_g", rot=(-1.5 * avant, 0, 0))
    p.add("avant_d", rot=(-1.2 * onde(t, 3), 0, 0))
    p.ouvert = 1 - cloche(t, 0.64, 0.025)
    return p


def _pas(u, long, haut):
    """Un pied dans son cycle (u de 0 à 1) : il se lève et file en avant d'un coup sec (le premier tiers), puis reste
    posé et glisse vers l'arrière pendant que le corps avance. Rend (y, z)."""
    if u < 0.34:
        v = K.lisse(u / 0.34)
        return long * (0.5 - v), haut * math.sin(math.pi * u / 0.34)
    return long * (-0.5 + (u - 0.34) / 0.66), 0.0


def avance(t):
    """Il avance à petits pas raides, en trépied : l'avant gauche (en l'air, elle tâte devant lui), le milieu droit et
    l'arrière gauche ensemble, puis les trois autres. À chaque pas, toute la brindille tangue d'avant en arrière."""
    p = Pose()
    for pied, phase in (("pied_milieu_d", 0.0), ("pied_arriere_g", 0.0), ("pied_milieu_g", 0.5), ("pied_arriere_d", 0.5)):
        y, z = _pas((t + phase) % 1.0, 0.050, 0.030)
        p.add(pied, pos=(0, y, z))
    for os_, phase in (("avant_g", 0.0), ("avant_d", 0.5)):
        u = (t + phase) % 1.0
        p.add(os_, rot=(10 * math.sin(math.pi * u / 0.34) if u < 0.34 else 0.0, 0, 0))
    tangue = onde(t, 2, 0.12)
    p.add("corps", rot=(2.4 * tangue, 0.8 * onde(t, 1), 0), pos=(0, -0.004 * tangue, 0.003 * abs(onde(t, 2))))
    p.add("tete", rot=(-1.5 * tangue, 0, 3 * onde(t, 1)))
    return p


def mange(t):
    """Il incline la brindille vers une feuille, la tient entre ses deux pattes de devant et la grignote à petits coups
    de tête ; puis il se redresse et reprend son air de branche."""
    p = Pose()
    leve = cloche(t, 0.86, 0.12)
    bas = 1 - leve
    grignote = (0.5 + 0.5 * onde(t, 9)) * bas
    p.add("corps", rot=(13 * bas, 0, 0))
    p.add("tete", rot=(26 * bas + 7 * grignote, 0, 3 * onde(t, 3) * bas))
    p.add("avant_g", rot=(24 * bas + 3 * grignote, 0, -5 * bas))
    p.add("avant_d", rot=(24 * bas + 3 * grignote, 0, 5 * bas))
    p.ouvert = 1 - 0.4 * bas - cloche(t, 0.92, 0.02)
    return p


def joie(t):
    """Sa fête à lui : une bourrasque. La brindille se balance de plus en plus fort, d'avant en arrière et de côté,
    les deux pattes de devant levées en V qui battent l'air, la tête qui dodeline ; puis le vent tombe et il redevient branche."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    p.add("corps", rot=(6 * onde(t, 2.5) * env, 5 * onde(t, 1.5) * env, 0))
    p.add("tete", rot=(-8 * env, 9 * onde(t, 3) * env, 0))
    bat = onde(t, 5) * env
    p.add("avant_g", rot=(6 * env, 0, 32 * env + 12 * bat))
    p.add("avant_d", rot=(6 * env, 0, -32 * env - 12 * bat))
    p.ouvert = 1 - 0.5 * env
    return p


def dort(t):
    """Il dort en branche morte : il se couche tout du long dans l'herbe, la brindille presque à plat, les pattes
    écartées, la tête dans l'axe, les yeux fermés ; à peine un souffle le balance."""
    p = Pose()
    p.ouvert = 0.0
    p.add("corps", rot=(26 + 0.6 * onde(t, 1), 0, 0))
    p.add("avant_g", rot=(2, 0, 5))
    p.add("avant_d", rot=(2, 0, -5))
    for pied, x in (("pied_milieu_g", 0.02), ("pied_milieu_d", -0.02), ("pied_arriere_g", 0.02), ("pied_arriere_d", -0.02)):
        p.add(pied, pos=(x, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Phasme")
