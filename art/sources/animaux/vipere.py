"""La vipère en peluche : courte, épaisse, roulée sur elle-même comme une corde de montagne bien lovée (elle se prend
pour une corde). Du milieu de ses anneaux, le cou se dresse en S, tiré en arrière, prêt à partir ; la tête plate en
triangle tient à l'horizontale et nous fixe sous une lourde paupière, la langue vermillon dehors. Une robe cuivre
rouille, un zigzag chocolat tout le long du dos, le V sombre sur le crâne, le ventre ocre clair.

    python vipere.py        fabrique la fiche art/apercus/animaux/vipere.png (style du palier : A, cousu main)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import garnitures as G
import matieres as M
import peluche as K
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

CUIVRE = np.array(M.hexa("#d0844f"))          # la dominante (registre du 14/10 : cuivre rouille #c0703e) ; un cran plus
                                              # clair, le poil cousu main fonce
CHOCO = np.array(M.hexa("#4a2c22"))           # le zigzag, le V du crâne, le bandeau derrière l'œil
VENTRE = np.array(M.hexa("#e8bf8c"))          # le ventre ocre clair
VERMILLON = M.hexa("#ee3b22")                 # l'accent : la langue
RAYON, COTES, PAS = 0.031, 40, 0.004          # le rayon du boudin, ses côtés, l'écart entre deux anneaux


def _spirale():
    """Les anneaux, de la queue (dehors, devant à droite) vers le milieu : un tour et demi qui se resserre."""
    points = []
    for k in range(0, 61):
        u = k / 60
        th = math.radians(-130 + 560 * u)
        r = 0.168 - 0.106 * u
        points.append((r * math.cos(th), 0.030 + r * math.sin(th), RAYON * (0.60 + 0.52 * min(1.0, u * 5))))
    return points


# Le fil du corps, du bout de la queue au bout du nez : la spirale couchée, puis le cou qui monte du milieu en S, tiré
# en arrière, et la tête qui revient à plat, pointée vers l'avant.
CHEMIN = _spirale() + [(0.006, 0.084, 0.078), (-0.004, 0.068, 0.124), (-0.008, 0.030, 0.170), (0.000, -0.020, 0.196),
                       (0.010, -0.070, 0.204), (0.020, -0.118, 0.198)]
FIL = A.courbe(CHEMIN, 8)
FAIT = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(FIL, axis=0), axis=1))])
SENS = np.gradient(FIL, FAIT, axis=0)
LONG = float(FAIT[-1])
TETE = LONG - 0.058                           # le milieu de la tête, le long du fil


def rayon(s):
    """Le rayon du boudin : la queue courte et effilée, le corps épais, le cou pincé, la tête large derrière."""
    s = np.asarray(s, float)
    r = RAYON * (0.16 + 0.84 * K.lisse(s / 0.26)) * np.minimum(1.0, (s / 0.02) ** 0.5)
    r = r * (1 + 0.10 * np.exp(-((s - 0.55 * LONG) / (0.25 * LONG)) ** 2))
    r = r * (1 - 0.24 * np.exp(-((s - (LONG - 0.120)) / 0.035) ** 2) + 0.10 * np.exp(-((s - (LONG - 0.065)) / 0.030) ** 2))
    return r * np.sqrt(1 - np.clip((s - (LONG - 0.030)) / 0.030, 0, 1) ** 2)


def repere(s):
    """En un point du fil : le centre du boudin, la direction où il va, son dos et son flanc gauche."""
    centre = np.stack([np.interp(s, FAIT, FIL[:, k]) for k in range(3)], axis=-1)
    avant = np.stack([np.interp(s, FAIT, SENS[:, k]) for k in range(3)], axis=-1)
    avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
    dos = np.array([0.0, 0.0, 1.0]) - avant[..., 2:3] * avant
    dos = dos / np.linalg.norm(dos, axis=-1, keepdims=True)
    return centre, avant, dos, np.cross(dos, avant)


def triangle(s):
    """La forme de la tête le long du fil : 0 avant la nuque, 1 aux mâchoires, qui retombe vers le museau."""
    s = np.asarray(s, float)
    return K.lisse((s - (LONG - 0.108)) / 0.030) * (1 - 0.80 * K.lisse((s - (LONG - 0.072)) / 0.056))


def couche(v):
    """Couche le boudin droit le long du fil ; la tête s'élargit en triangle et s'aplatit."""
    s = np.clip(v[:, 2], 0.0, LONG)
    centre, _avant, dos, flanc = repere(s)
    t = triangle(s)
    return centre + (v[:, 0] * (1 + 0.55 * t))[:, None] * flanc + (v[:, 1] * (1 - 0.16 * t))[:, None] * dos


def zigzag(u):
    """Une onde en dents de scie, de -1 à 1."""
    return 2 * np.abs(2 * (u - np.floor(u + 0.5))) - 1


def construire():
    a = K.Animal("vipere")
    a.taille = 0.62

    # ----- le corps : un boudin tourné tout droit, peint (le zigzag, les taches des flancs, le ventre, le V du crâne),
    #       puis couché le long de son fil -----
    hauteurs = np.arange(0.0, LONG, PAS)
    corps = A.tour([(0.0, 0.0)] + [(float(rayon(s)), float(s)) for s in hauteurs[1:]] + [(0.0, LONG)], COTES)
    x, y, s = corps.v[:, 0], corps.v[:, 1], corps.v[:, 2]
    haut = np.degrees(np.arctan2(x, y))                               # 0 sur le dos, ±90 sur les flancs
    t = np.tile(CUIVRE, (len(s), 1))
    corps_ = (s > 0.07) & (s < LONG - 0.125)
    t[corps_ & (np.abs(haut - 34 * zigzag(s / 0.052)) < 19)] = CHOCO                         # le zigzag
    t[corps_ & (np.abs(np.abs(haut) - 84) < 11) & (zigzag(s / 0.052 + 0.5) > 0.35)] = CHOCO   # les taches des flancs
    t[np.abs(haut) > 122] = VENTRE
    tete = s > LONG - 0.112
    t[tete & (np.abs(np.abs(haut) - 52 * (LONG - 0.040 - s) / 0.066) < 10) & (s < LONG - 0.040)] = CHOCO   # le V
    t[tete & (np.abs(np.abs(haut) - 80) < 12) & (s < LONG - 0.050)] = CHOCO                    # le bandeau des tempes
    corps.teinte = t
    G.sillons(corps, [0], 0.003, 1.0)
    a.piece("corps", corps.sculpte(couche), None)
    a.couture("flanc", "corps", 0, 0.80, 0.88)

    # ----- le visage : deux yeux vivants sous une lourde paupière cuivre, l'air de nous avoir à l'œil -----
    centre, avant, dos, flanc = (Vector(q) for q in repere(TETE))
    a.tete = centre + avant * 0.030
    for nom, c in (("_G", 1), ("_D", -1)):
        p, n = a.surface("corps", centre, flanc * (0.78 * c) + dos * 0.40 + avant * 0.34)
        a.oeil("oeil" + nom, p + n * 0.002, n, 0.0120)
        h = (dos - n * n.dot(dos)).normalized()
        a.piece("lourde" + nom, K.paupiere(0.0120, 0.32), tuple(CUIVRE), mat=A.cadre(p + n * 0.002, n, h), poil=False)

    # ----- la langue fourchue, vermillon, qui sort du bout du nez -----
    centre, avant, dos, flanc = (Vector(q) for q in repere(LONG - 0.012))
    devant, dessus = avant * math.cos(0.25) - dos * math.sin(0.25), dos * math.cos(0.25) + avant * math.sin(0.25)
    fourche = [(0.0, -0.0028), (0.028, -0.0031), (0.046, -0.0115), (0.050, -0.0088), (0.036, 0.0), (0.050, 0.0088),
               (0.046, 0.0115), (0.028, 0.0031), (0.0, 0.0028)]
    a.piece("langue", A.decoupe(fourche, 0.0032, 0.0011), VERMILLON, mat=A.cadre(centre - dos * 0.006, dessus, dessus.cross(devant)),
            poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "dresse")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("vipere", styles.style_de("vipere"), sys.modules[__name__]), "Vipère")
