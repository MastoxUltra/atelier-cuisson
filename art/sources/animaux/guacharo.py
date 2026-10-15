"""Le guacharo en peluche : l'oiseau de nuit des grottes, brun roux semé de petites gouttes blanches du front à la queue,
les yeux immenses et noirs, le bec crochu cerné de longues soies raides, les ailes longues repliées, la queue en
éventail. Perché sur ses petites pattes roses, il guette dans le noir sans bouger, et quand il crie, la grotte entière le
sait. Il voit dans l'ombre ; il écoute encore mieux.

    python guacharo.py        fabrique la fiche art/apercus/animaux/guacharo.png (style du palier : C, velours ras)
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

ROUX = np.array(M.hexa("#966044"))            # la dominante (registre : brun roux tacheté de blanc #8c5a3a), un cran plus clair (style C)
VENTRE = np.array(M.hexa("#b58463"))          # le ventre, la poitrine
SOMBRE = np.array(M.hexa("#5e3b28"))          # le bout des ailes, de la queue
GOUTTE = np.array(M.hexa("#f6f0e4"))          # l'accent : les gouttes blanches
BEC = M.hexa("#c7b79a")
SOIE = M.hexa("#3a2a20")
PATTE = np.array(M.hexa("#d28a8c"))


def construire():
    a = K.Animal("guacharo")
    a.taille = 0.60

    r = O.oiseau(a, dos=ROUX, ventre=VENTRE, tete=ROUX * 1.02, aile=ROUX * 0.96, queue=SOMBRE, bec=BEC, patte=PATTE, long=0.40, ray=0.130,
                 incline=34.0, z0=0.140, tete_r=(0.066, 0.070, 0.064), tete_pos=(0.0, -0.105, 0.075), bec_long=0.058, bec_ray=0.0205,
                 bec_baisse=-0.10, aile_dim=(0.030, 0.140, 0.230), aile_pos=(0.0, 0.040, 0.0), queue_dim=(0.050, 0.150, 0.014), queue_haut=-18.0,
                 patte_long=0.100, patte_ray=0.0115, oeil_r=0.0215, oeil_dir=(0.74, -0.56, 0.26), bout_aile=SOMBRE, coupe_dos=1.40)
    H, T, haut = r["H"], r["T"], r["haut"]

    # ----- le crochet du bec, et les longues soies raides qui l'entourent comme une moustache -----
    crochet = O.couche(O.teinte(O.pointe(0.026, 0.0085, 8), np.array(M.hexa("#8a7a60"))),
                       A.cadre(H + Vector((0.0, -0.126, -0.012)), Vector((0.0, -0.25, -1.0)), (0, 1, 0)))
    a.piece("crochet", crochet, None, poil=False)
    soies = None
    for k in range(7):
        for c in (1, -1):
            dx = c * (0.014 + 0.007 * k)
            d = Vector((c * (0.40 + 0.06 * k), -0.85, -0.10 - 0.04 * k)).normalized()
            s_ = O.couche(O.teinte(O.pointe(0.052 + 0.003 * k, 0.0032, 5), np.array(SOIE)),
                          A.cadre(H + Vector((dx, -0.088, -0.020 - 0.004 * k)), d, (0, 0, 1)))
            soies = s_ if soies is None else soies + s_
    a.piece("soies", soies, None, poil=False)

    # ----- les gouttes blanches : des petits disques posés sur le dos, la tête, les ailes, la queue -----
    rng = np.random.default_rng(11)
    gouttes = None
    for k in range(70):
        th = rng.uniform(-1.30, 1.30)                                            # autour du dos (0 : sur la crête)
        zz = rng.uniform(0.04, 0.34) * 0.40 / 0.34
        ray_loc = 0.130 * float(np.interp(zz / (0.40 / 0.34), [0.0, 0.09, 0.20, 0.30, 0.34], [0.0, 0.9, 1.0, 0.62, 0.0]))
        if ray_loc < 0.03:
            continue
        pos = T @ Vector((ray_loc * math.sin(th) * 1.00, ray_loc * math.cos(th) * 1.00 + 0.002, zz))
        n = (T.to_3x3() @ Vector((math.sin(th), math.cos(th), 0.0))).normalized()
        g = A.boule(1.0, 10, 6).etire(0.0105, 0.0105, 0.0035)
        g = O.couche(O.teinte(g, GOUTTE), A.cadre(pos, n, (0, 0, 1)))
        gouttes = g if gouttes is None else gouttes + g
    a.piece("gouttes", gouttes, None, poil=False)
    for c in (1, -1):
        for k in range(6):
            zz = 0.050 + 0.052 * k
            dz = (zz - 0.194) / 0.230
            tt = Vector((c * (0.126 + 0.030 * math.sqrt(max(1.0 - dz * dz, 0.0)) + 0.003), 0.015 + 0.020 * (k % 3), zz))
            n = (T.to_3x3() @ Vector((c * 1.0, 0.0, 0.0))).normalized()
            g = O.couche(O.teinte(A.boule(1.0, 10, 6).etire(0.0105, 0.0105, 0.0035), GOUTTE), A.cadre(T @ tt, n, (0, 0, 1)))
            a.piece("goutte_aile_%d_%d" % (c, k), g, None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("guacharo", styles.style_de("guacharo"), sys.modules[__name__]), "Guacharo")
