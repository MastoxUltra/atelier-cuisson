"""Le kakapo en peluche de magasin (2e dessin) : le perroquet-hibou. Un jaune pâle moucheté de brun et de noir, un
corps lourd qui se dandine sur de gros pieds, une aile qui traîne par terre, et surtout cette face en disque de plumes
raides et fines qui entoure un bec crochu fort, crème, aux narines tubulaires : un masque de hibou, avec des
vibrisses. Le bougon : assis à la renverse sur sa queue, le disque tourné vers nous, l'œil mi-clos, les sourcils de
plumes tombants, une aile qui pend jusqu'au sol, l'air de quelqu'un qu'on a réveillé pour rien.

    python kakapo.py        fabrique la fiche art/apercus/animaux/kakapo.png (peluche de magasin, palier 4)
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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
PALE = M.hexa("#f4e888")                      # la dominante : jaune pâle (jamais vert)
BRUN = M.hexa("#7a5a30")                      # l'accent : les mouchetures
CREME = M.hexa("#fff6d0")                     # le disque, le ventre
BEC = M.hexa("#f4e0b8")                       # le bec
CHARBON = M.hexa("#3a3028")
CORPS = Vector((0.0, 0.060, 0.190))
TETE = Vector((0.0, -0.100, 0.330))
LACET = 22.0


def construire():
    a = K.Animal("kakapo")
    a.taille = 0.70

    # ----- le corps : un gros œuf bas et lourd, la poitrine en avant, la queue qui traîne ; moucheté de brun -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(PALE, float), (len(v), 1))
    n = np.sin(9.0 * v[:, 0] + 1.0) * np.sin(10.0 * v[:, 1] + 2.0) * np.sin(9.5 * v[:, 2] + 0.5)
    t[n > 0.38] = BRUN
    t[(v[:, 1] < -0.35) & (v[:, 2] < 0.55)] = CREME
    corps.teinte = t

    def oeuf(v):
        v = K.bosse(v, (0, -0.9, 0.2), 0.12, 0.5)
        return v * [0.175, 0.200, 0.180]
    a.piece("corps", corps.sculpte(oeuf), None, pos=CORPS, rot=(-12, 0, 0))

    # ----- la tête : un gros disque aplati de plumes raides, fondu dans le crâne (une seule pièce : le visage EST le disque) ;
    #       au milieu, un gros bec crochu clair ; de petits yeux noirs dans le disque ; les vibrisses -----
    H = A.repere(TETE, (0, 8, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 56, 28)
    tete.teinte = np.where((tete.v[:, 1] < -0.10)[:, None], np.asarray(CREME), np.asarray(PALE))

    def disque(v):
        s = v.copy()
        s[:, 1] = np.where(v[:, 1] < 0, v[:, 1] * 0.55, v[:, 1])                 # le devant s'aplatit en disque
        s = K.bosse(s, (0, -1, 0), 0.06, 0.40)
        return s * [0.112, 0.098, 0.108]
    tete = tete.sculpte(disque)
    a.piece("tete", tete, None, mat=H)
    plumes = G.franges(tete, 0.032, 0.012, 0.016, 0.010,
                       lambda rang, t: tuple(np.asarray(CREME) * (0.90 + 0.10 * (rang % 2)) - np.asarray([0.0, 0.05, 0.14]) * (1 - t)),
                       4, 1, 0.0, 0.92)
    a.piece("plumes_disque", plumes, None, mat=H, poil=False)
    a.tete = H @ Vector((0, -0.120, -0.010))

    # ----- le bec : gros, court, fort, crochu, clair, au milieu du disque ; de longues vibrisses de chaque côté -----
    B = A.cadre(H @ Vector((0, -0.060, -0.020)), H3 @ Vector((0, -0.90, -0.40)), H3 @ Vector((0, 0.4, -0.9)))
    bec = A.tour(A.profil([(0, 0), (0.052, 0.008), (0.060, 0.036), (0.048, 0.070), (0.028, 0.098), (0.008, 0.112), (0, 0.116)], 6), 32)
    a.piece("bec", bec.etire(0.92, 1.0, 1.0).sculpte(lambda v: np.stack([v[:, 0], v[:, 1] + 0.034 * np.clip(v[:, 2] / 0.116, 0, 1) ** 2.2, v[:, 2]], axis=1)),
            BEC, mat=B, poil=False)
    for c in (1, -1):
        for k, (dy, dz) in enumerate(((0.020, 0.010), (0.004, -0.010), (-0.014, -0.028))):
            dep = H @ Vector((c * 0.060, -0.076, -0.016 + dz))
            a.broderie("vibrisse_%s%d" % ("G" if c > 0 else "D", k),
                       [dep, dep + H3 @ Vector((c * 0.050, -0.012, dz * 1.4)), dep + H3 @ Vector((c * 0.104, -0.008, dz * 3.0))], 0.0015, CHARBON)
        regard = H3 @ Vector((c * 0.42, -0.86, 0.20))
        p, n_ = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + ("G" if c > 0 else "D"), p + n_ * 0.004, n_, 0.0120)

    # ----- les ailes : la gauche traîne par terre, mollement ; la droite plaquée au flanc ; les gros pieds à orteils -----
    for nom, c, rot, pos in (("G", 1, (0, 0, 66), (0.196, 0.040, 0.165)), ("D", -1, (-10, 0, -8), (-0.158, 0.050, 0.210))):
        aile = A.boule(1.0, 36, 18)
        aile.teinte = np.where((np.sin(11 * aile.v[:, 2] + aile.v[:, 0]) > 0.55)[:, None], np.asarray(BRUN), np.asarray(PALE))
        a.piece("aile_" + nom, aile.etire(0.030, 0.064, 0.170), None, pos=pos, rot=rot)
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.044, 0.080, 0.028), M.hexa("#c8b098"), pos=(c * 0.082, -0.080, 0.028), poil=False)
        for k in (-1, 0, 1):
            a.piece("orteil_%s%d" % (nom, k), A.boule(1.0, 12, 6).etire(0.012, 0.036, 0.011), M.hexa("#c8b098"),
                    pos=(c * 0.082 + k * 0.022, -0.148, 0.018), rot=(0, 0, k * 10), poil=False)
    a.piece("queue", A.boule(1.0, 24, 12).etire(0.060, 0.120, 0.030), PALE, pos=(0, 0.240, 0.115), rot=(-6, 0, 0))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("kakapo", styles.style_de("kakapo"), sys.modules[__name__]), "Kakapo")
