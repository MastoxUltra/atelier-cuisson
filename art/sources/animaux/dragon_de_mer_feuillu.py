"""Le dragon de mer feuillu en peluche, deuxième dessin, d'après les photos de Phycodurus eques : un hippocampe qui se prend
pour une algue. Une tête de cheval au long museau en tube, tendue vers l'avant ; un cou en arc ; un tronc ocre doré annelé de
bandes ; une queue fine qui s'enroule en spirale à son bout ; et partout, des feuilles : dix-huit lames plates orange et olive pâle,
translucides, qui s'insèrent sur le dos, le ventre et le front, et le font disparaître dans le varech. Quelques points bleu ciel
sur les flancs : sa seule coquetterie.

    python dragon_de_mer_feuillu.py        fabrique la fiche art/apercus/animaux/dragon_de_mer_feuillu.png (style du palier : B)
    (le premier dessin, jugé le 15/10 : « on dirait une chenille »)
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
import matieres as M
import peluche as K
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

OCRE = np.array(M.hexa("#d9a23a"))            # la dominante (registre : ocre doré)
ORANGE = np.array(M.hexa("#e8802f"))          # les feuilles orange
OLIVE = np.array(M.hexa("#c9b96a"))           # les feuilles olive pâle (jamais un vert franc)
CIEL = np.array(M.hexa("#8fd0ee"))            # l'accent : les points bleu ciel
BRUN = np.array(M.hexa("#9a6a24"))            # les bandes du tronc
FIL = M.hexa("#5a3a14")

# de l'enroulement du bout de la queue au bout du museau : la queue en spirale, le tronc à plat, le cou en arc, la tête tendue
CHEMIN = [(0.0, 0.60, 0.240), (0.0, 0.66, 0.200), (0.0, 0.68, 0.150), (0.0, 0.62, 0.115), (0.0, 0.50, 0.102), (0.0, 0.36, 0.100),
          (0.0, 0.20, 0.108), (0.0, 0.04, 0.126), (0.0, -0.10, 0.156), (0.0, -0.20, 0.200), (0.0, -0.26, 0.252), (0.0, -0.34, 0.276),
          (0.0, -0.48, 0.268)]


def rayon(f):
    return O.interp([(0.0, 0.0), (0.02, 0.006), (0.15, 0.012), (0.30, 0.020), (0.45, 0.034), (0.60, 0.050), (0.74, 0.050),
                     (0.82, 0.040), (0.88, 0.034), (0.93, 0.040), (0.96, 0.020), (0.985, 0.013), (1.0, 0.0)])(f)


def feuille(long, large, plan_pos, direction, haut, couleur, epaisseur=0.006):
    """Une feuille : une lame ovale pointue, posée par son pétiole sur le corps, qui part dans `direction`."""
    pts = []
    for k in range(14):
        u = k / 13
        w = large * math.sin(math.pi * u) ** 0.8 * (1 - 0.35 * u)
        pts.append((u * long, w))
    for k in range(13, -1, -1):
        u = k / 13
        w = large * math.sin(math.pi * u) ** 0.8 * (1 - 0.35 * u)
        pts.append((u * long, -w))
    pts = [p for i, p in enumerate(pts) if i == 0 or abs(p[0] - pts[i - 1][0]) + abs(p[1] - pts[i - 1][1]) > 1e-6]
    m = A.decoupe(pts, epaisseur, 0.002)
    m.teinte = np.tile(couleur, (len(m.v), 1))
    return O.couche(m, O.plan(plan_pos, direction, haut))


def construire():
    a = K.Animal("dragon_de_mer_feuillu")
    a.taille = 0.90                                # plus gros : il se noyait dans l'herbe (« flou »)

    # ----- le corps : un tronc annelé de bandes brunes, la queue qui s'enroule, le cou en arc, la tête de cheval au museau en tube -----
    def peint(m, L):
        f = m.v[:, 2] / L
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(OCRE, (len(f), 1))
        t[(f > 0.28) & (f < 0.82) & (np.sin(f * 2.0 * math.pi * 14.0) > 0.55)] = BRUN
        t[ang > 2.4] = OCRE * 1.08
        return t
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=30, flanc=(1.0, 0.0, 0.0))

    # ----- le visage : un petit œil rond au-dessus du museau ; la bouche au bout du tube ; une crête sur le front -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = O.sur_corps(fil, L, rayon, 0.915, 76, c, 1.0, 1.0, 0.002)
        a.oeil("oeil_" + nom, p, n, 0.0225)                                  # la tête se lit : un œil plus gros
    tip, ati, nti = (Vector(q) for q in fil.cadre(0.995 * L))
    bout = A.boule(1.0, 14, 8).etire(0.016, 0.016, 0.014)
    a.piece("bout", O.teinte(bout, OCRE * 0.92), None, pos=tuple(tip), poil=False)

    # ----- les feuilles : une rangée sur le dos, une sous le ventre, quelques-unes sur le cou et le front, deux sur la queue ;
    #       orange, olive, ocre en alternance, de tailles inégales -----
    feuilles = {"orange": None, "olive": None, "ocre": None}
    rng = np.random.default_rng(9)
    cfg = []
    for k in range(7):                                                                  # le dos
        cfg.append((0.30 + 0.085 * k, 0, 1))
    for k in range(5):                                                                  # le ventre
        cfg.append((0.34 + 0.095 * k, 180, 1))
    for k in range(3):                                                                  # le cou et le front
        cfg.append((0.80 + 0.050 * k, 20 + 25 * k, 1))
        cfg.append((0.80 + 0.050 * k, 20 + 25 * k, -1))
    cfg.append((0.10, 0, 1)); cfg.append((0.18, 180, 1))                                 # la queue
    for i, (f, ang, cote) in enumerate(cfg):
        p, n = O.sur_corps(fil, L, rayon, f, ang, cote, 1.0, 1.0, 0.0)
        c, av, nq = (Vector(q) for q in fil.cadre(f * L))
        fl = Vector(fil.flanc).normalized()
        long = (0.115 + 0.040 * rng.random() - (0.040 if f > 0.78 else 0.0)) * (0.62 if ang == 180 else 1.0)
        large = 0.034 + 0.012 * rng.random()
        dirv = (n * 0.80 + (-av) * 0.55 + fl * (0.30 * cote if 10 < ang < 170 else 0.0)).normalized()          # vers l'extérieur et l'arrière
        haut = (nq if abs(dirv.dot(nq)) < 0.9 else fl)
        cle = ("orange", "olive", "ocre")[(i + (1 if ang == 180 else 0)) % 3]
        coul = {"orange": ORANGE, "olive": OLIVE, "ocre": OCRE * 1.06}[cle]
        mesh = feuille(long, large, p, dirv, haut, coul)
        feuilles[cle] = mesh if feuilles[cle] is None else feuilles[cle] + mesh
    for cle, mesh in feuilles.items():
        if mesh is not None:
            a.piece("feuilles_" + cle, mesh, None, poil=False)

    # ----- les points bleu ciel sur les flancs ; de petites nageoires translucides derrière la tête -----
    pts = []
    for c in (1, -1):
        for k in range(8):
            pts.append(O.sur_corps(fil, L, rayon, 0.36 + 0.055 * k, 95, c, 1.0, 1.0, 0.0012))
    a.piece("points", O.points_lumineux(pts, 0.0085, CIEL), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        p, n = O.sur_corps(fil, L, rayon, 0.865, 100, c, 1.0, 1.0, -0.002)
        pec = A.boule(1.0, 14, 8).etire(0.004, 0.032, 0.026)
        pec.teinte = np.tile(OLIVE * 1.05, (len(pec.v), 1))
        a.piece("pectorale_" + nom, O.couche(pec, A.cadre(p, Vector((c * 0.7, 0.3, 0.3)), (0, 0, 1))), None, poil=False)
    a.tete = tip + Vector((0.0, -0.12, 0.03))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "serpent")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("dragon_de_mer_feuillu", styles.style_de("dragon_de_mer_feuillu"), sys.modules[__name__]), "Dragon de mer feuillu")
