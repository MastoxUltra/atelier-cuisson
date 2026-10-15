"""Le kookaburra en peluche, cousu main (3e dessin) : un petit corps trapu crème, le dos et les ailes café avec la
plaque bleu ciel, la queue rousse barrée de brun ; une tête crème carrée au bandeau brun en travers de l'œil ; et un
bec LONG, ÉPAIS et DROIT qui sort franchement du visage : sombre dessus, clair dessous, la pointe vers le haut quand il
rit. Il rit : la tête rejetée en arrière, le bec ouvert vers le ciel, perché sur une patte.

    python kookaburra.py        fabrique la fiche art/apercus/animaux/kookaburra.png (cousu main, palier 2)
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

CREME = M.hexa("#fff2d6")                     # la dominante : crème chaud
CAFE = M.hexa("#8a6040")                      # le dos, le bandeau, la queue
CIEL = M.hexa("#58c0f0")                      # l'accent : la plaque bleu ciel de l'aile
ROUX = M.hexa("#d88a50")                      # la queue
CHARBON = M.hexa("#4a3a34")                   # le dessus du bec
CORNE = M.hexa("#f0dcb8")                     # le dessous du bec
CORPS = Vector((0.0, 0.040, 0.250))
TETE = Vector((0.0, -0.040, 0.440))
LACET, RENVERSE = 44.0, -6.0


def construire():
    a = K.Animal("kookaburra")
    a.taille = 0.60

    # ----- le corps : un petit œuf trapu ; le dos brun, le ventre crème -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(CREME, float), (len(v), 1))
    t[(v[:, 1] > 0.30) & (v[:, 2] > -0.30)] = CAFE
    corps.teinte = t

    def oeuf(v):
        return K.bosse(v, (0, -0.9, 0.2), 0.14, 0.45) * [0.118, 0.115, 0.150]
    G.sillons(corps, [14], 0.004, 1.1)
    a.piece("corps", corps.sculpte(oeuf), None, pos=CORPS, rot=(-4, 0, 0))

    # ----- la tête : carrée, le crâne brun, le bandeau café ; renversée en arrière -----
    H = A.repere(TETE, (RENVERSE, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(lambda v: K.emousse(v, 0.80) * [0.092, 0.090, 0.088]), CREME, mat=H)
    a.piece("calotte", A.boule(1.0, 32, 16).etire(0.086, 0.074, 0.044), CAFE, mat=H @ A.repere((0, 0.016, 0.050)))
    for c in (1, -1):
        a.rustine("bandeau_" + ("G" if c > 0 else "D"), "tete", H.to_translation(), H3 @ Vector((c * 0.88, -0.30, 0.08)),
                  lambda th: 0.20 + 0.36 * abs(math.cos(th)), CAFE, 0.003, 0)
    a.tete = H @ Vector((0, -0.170, -0.010))

    # ----- le bec : long, épais, DROIT, sombre dessus et clair dessous, sorti bien en avant de la tête ; entrouvert vers le haut -----
    B = A.cadre(H @ Vector((0, -0.070, -0.012)), H3 @ Vector((0, -1.0, 0.34)), H3 @ Vector((0, 0, 1)))
    haut = A.tour(A.profil([(0, 0), (0.048, 0.006), (0.050, 0.060), (0.046, 0.150), (0.040, 0.230), (0.028, 0.285), (0.010, 0.310), (0, 0.320)], 6), 32)
    a.piece("bec_haut", haut.etire(0.82, 0.62, 1.0).pose((0, 0.010, 0)), CHARBON, mat=B, poil=False)
    bas = A.tour(A.profil([(0, 0), (0.044, 0.006), (0.046, 0.060), (0.042, 0.140), (0.034, 0.210), (0.020, 0.255), (0, 0.272)], 6), 32)
    a.piece("bec_bas", bas.etire(0.82, 0.50, 1.0).pose((0, -0.064, 0.0), (14, 0, 0)), CORNE, mat=B, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.72, -0.56, 0.30)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0140)
        a.piece("lourde_" + nom, K.paupiere(0.0170, 0.02), CAFE, mat=A.cadre(p + n * 0.005, n, H3 @ Vector((0, 0, 1))), poil=False)

    # ----- les ailes : deux galets café avec la plaque bleu ciel ; la gauche entrouverte -----
    for nom, c, rot in (("G", 1, (-10, 0, 26)), ("D", -1, (-8, 0, -4))):
        aile = A.boule(1.0, 36, 18)
        t = np.tile(np.asarray(CAFE, float), (len(aile.v), 1))
        t[(aile.v[:, 2] > -0.10) & (aile.v[:, 2] < 0.55)] = CIEL
        aile.teinte = t

        def galet(v):
            s = K.emousse(v, 0.88)
            s[:, 1] *= 1 - 0.50 * K.lisse((v[:, 2] + 0.2) / 1.2)
            return s
        a.piece("aile_" + nom, aile.sculpte(galet).etire(0.030, 0.062, 0.160), None, pos=(c * 0.120, 0.050, 0.235), rot=rot)

    # ----- la queue : roux barré de café, qui pend et se relève ; une seule patte plantée -----
    queue = A.tour(A.profil([(0, 0), (0.044, 0.008), (0.048, 0.080), (0.042, 0.160), (0.028, 0.225), (0, 0.255)], 6), 28).etire(1.0, 0.36, 1.0)
    K.bandes(queue, [(0.060, ROUX), (0.100, CAFE), (0.135, ROUX), (0.170, CAFE), (0.205, ROUX), (9, CREME)])
    a.piece("queue", queue, None, pos=(0, 0.160, 0.255), rot=(128, 0, 0), poil=False)
    a.piece("patte_D", A.tube(A.courbe([(-0.040, 0.020, 0.140), (-0.044, 0.000, 0.080), (-0.046, -0.026, 0.026)], 5), 0.019, 12),
            M.hexa("#c8b090"), poil=False)
    doigts = None
    for ang in (-26, 0, 26):
        d = A.boule(1.0, 14, 8).etire(0.012, 0.046, 0.011).pose((0, -0.036, 0.0)).pose((0, 0, 0), (0, 0, ang))
        doigts = d if doigts is None else doigts + d
    a.piece("doigts_D", doigts, M.hexa("#c8b090"), pos=(-0.046, -0.026, 0.010), poil=False)
    a.piece("cuisse_G", A.boule(1.0, 24, 12).etire(0.034, 0.050, 0.042), CREME, pos=(0.062, 0.000, 0.150))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("kookaburra", styles.style_de("kookaburra"), sys.modules[__name__]), "Kookaburra")
