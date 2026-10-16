"""La tortue de mer en peluche, quatrième dessin, sur une autre base (le plateau et les palettes en lames tirées d'un contour,
d'après les photos de référence art/sources/references/tortue_de_mer/) : la tortue verte échouée sur le sable. Une
carapace ovale en cœur, large aux épaules et qui se resserre en pointe émoussée, basse (le tiers de sa largeur), chocolat
bordé de sable, aux grandes écailles caramel posées à plat ; le plastron sable dessous, posé au sol. Un cou court et
épais, une petite tête ronde au museau émoussé, les yeux sombres sous des paupières ridées. Les deux palettes avant sont
longues, étroites, en aile : bord d'attaque droit, bord de fuite bombé, balayées vers l'arrière et vers le dehors, le bout
pointu qui touche le sable. Les arrière sont petites et la queue un simple moignon.

    python tortue_de_mer.py        fabrique la fiche art/apercus/animaux/tortue_de_mer.png (style du palier : B, peluche de magasin)
    (refusés le 15/10 : « un galet avec quatre palettes », « des petits pains », « un cou d'oiseau et des palettes en galets »)
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

CARAMEL = np.array(M.hexa("#cf9450"))         # la dominante (registre : carapace caramel) ; le style B adoucit
ECAILLE = np.array(M.hexa("#7a4a24"))         # le joint chocolat : le fond de la carapace
SABLE = np.array(M.hexa("#ecd0a0"))           # la peau, le plastron
BEC = M.hexa("#8a6a44")
FIL = M.hexa("#5a3a22")
CENTRE = Vector((0.0, 0.05, 0.068))           # le centre de la carapace
RX, RY, RZ = 0.34, 0.44, 0.21                 # ses demi-axes : large 0,68 ; longue 0,88 ; haute 0,21 au-dessus de son centre


def coeur(v):
    """L'ellipsoïde devient une carapace en cœur : large aux épaules (devant, -Y), resserrée vers l'arrière, le dessous plat."""
    s = v.copy()
    arriere = np.clip((v[:, 1] + 0.05) / 0.60, 0.0, 1.0)                    # 0 devant, 1 au bout
    s[:, 0] *= 1.0 - 0.40 * arriere ** 1.3
    s[:, 1] *= 1.0 + 0.10 * arriere ** 2
    avant = np.clip(-v[:, 1] / 0.50, 0.0, 1.0)
    s[:, 0] *= 1.0 + 0.04 * avant                                           # les épaules un rien plus larges
    s[:, 2] = np.where(v[:, 2] < 0, v[:, 2] * 0.16, v[:, 2])                # le dessous : un plateau, presque plat
    return s


def hexagone(r0):
    return lambda th: r0 / max(math.cos((th % (math.pi / 3)) - math.pi / 6), 0.5)


def palette(L, large, droop=0.05):
    """Une palette en lame : le bord d'attaque droit (y = 0), le bord de fuite bombé (y < 0), le bout pointu ; épaisseur 0,030,
    le bout qui s'incline vers le sol. Le contour va de la racine (x = 0) au bout (x = L)."""
    pts = [(0.00, 0.012), (0.18 * L, 0.020), (0.52 * L, 0.014), (0.86 * L, 0.004), (1.00 * L, 0.0),
           (0.92 * L, -0.30 * large), (0.74 * L, -0.74 * large), (0.50 * L, -1.00 * large), (0.26 * L, -0.92 * large),
           (0.08 * L, -0.66 * large), (0.00, -0.38 * large)]
    m = A.decoupe(pts, 0.092, 0.040)                      # épaisse et bombée : une nageoire charnue (à 0,066, une lame plate)
    m = m.sculpte(lambda v: np.stack([v[:, 0], v[:, 1], v[:, 2] - droop * (v[:, 0] / L) ** 2 * (1 / 0.034) * 0.034], axis=1))
    m.teinte = np.tile(SABLE, (len(m.v), 1))
    return m


def construire():
    a = K.Animal("tortue_de_mer")
    a.taille = 1.40

    # ----- la carapace : UNE pièce en cœur, basse ; le bord et le plastron sable, le dessus chocolat -----
    car = A.boule(1.0, 64, 32)
    car = car.etire(RX, RY, RZ).sculpte(coeur)
    z = car.v[:, 2]
    t = np.tile(ECAILLE, (len(z), 1))
    t[z < 0.040] = SABLE                                                    # le plateau et le bord, sable
    car.teinte = t
    a.piece("carapace", car, None, pos=tuple(CENTRE))

    # ----- les écailles : des rustines à six côtés qui épousent le dôme, vues d'un point au centre de la carapace ;
    #       cinq au milieu, quatre de chaque côté -----
    c0 = CENTRE + Vector((0.0, 0.0, 0.040))
    k = 0
    plan = [((0.0, y), 0.36) for y in (-0.31, -0.155, 0.0, 0.155, 0.31)]
    for c in (1, -1):
        plan += [((c * 0.215, y), 0.33) for y in (-0.22, -0.07, 0.08, 0.23)]
    for (x, y), ouv in plan:
        axe = Vector((x, y, 0.26))
        a.rustine("ecaille_%d" % k, "carapace", c0, axe, hexagone(ouv), tuple(CARAMEL * (0.96 + 0.05 * ((k * 5) % 3))), 0.006, 0)
        k += 1

    # ----- le cou court et épais ; la petite tête ronde au museau émoussé, posée haut ; les yeux sous des paupières ridées -----
    cou = O.tube_r([(0.0, -0.36, 0.080), (0.0, -0.45, 0.115), (0.0, -0.52, 0.150)], [0.110, 0.092, 0.084], 22)
    cou.teinte = np.tile(SABLE, (len(cou.v), 1))
    a.piece("cou", cou, None)
    H = Vector((0.0, -0.585, 0.175))
    RT = A.repere(H, (-8, 0, 30))                        # tournée vers la caméra de la fiche : de face, les deux yeux se voient
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.tile(SABLE, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.088, 0.108, 0.074), None, mat=RT)
    museau = A.boule(1.0, 28, 14).sculpte(lambda v: K.emousse(v, 0.75)).etire(0.054, 0.052, 0.040)
    a.piece("museau", O.teinte(museau, SABLE * 0.97), None, mat=RT @ A.repere((0.0, -0.092, -0.020)))
    nez = A.boule(1.0, 14, 8).etire(0.024, 0.016, 0.012)
    a.piece("bec", nez, BEC, mat=RT @ A.repere((0.0, -0.133, -0.012)), poil=False)
    O.paire_yeux(a, "tete", H, (0.84, -0.46, 0.20), 0.0300, decolle=0.004, R=RT)
    O.broder(a, "gueule", "museau", RT @ Vector((0, -0.092, -0.020)), [(0.60 * u_, -0.82, -0.36 + 0.10 * u_ * u_) for u_ in np.linspace(-1, 1, 9)], 0.0030, FIL, R=RT)
    a.tete = H + Vector((0.0, -0.13, 0.0))

    # ----- les palettes avant : longues, étroites, en aile, balayées vers l'arrière et le dehors, le bout au sable ;
    #       les palettes arrière : petites, vers l'arrière ; le moignon de la queue -----
    for nom, c in (("G", 1), ("D", -1)):
        av = palette(0.64, 0.115)
        R = O.plan(Vector((c * 0.275, -0.130, 0.090)), Vector((c * 0.80, 0.58, -0.07)), Vector((c * 0.58, -0.80, 0.0)))
        a.piece("palette_avant_" + nom, O.couche(av, R), None)
        ar = palette(0.27, 0.075)
        R2 = O.plan(Vector((c * 0.150, 0.420, 0.070)), Vector((c * 0.48, 0.87, -0.05)), Vector((c * 0.87, -0.48, 0.0)))
        a.piece("palette_arriere_" + nom, O.couche(ar, R2), None)
    queue = A.tour(A.profil([(0.036, 0), (0.024, 0.046), (0.009, 0.088), (0, 0.100)], 4), 14)
    queue.teinte = np.tile(SABLE, (len(queue.v), 1))
    a.piece("queue", O.couche(queue, A.cadre((0.0, 0.50, 0.080), (0.0, 1.0, -0.10), (0, 0, 1))), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tortue_de_mer", styles.style_de("tortue_de_mer"), sys.modules[__name__]), "Tortue de mer")
