"""Le mégapode en peluche : le bâtisseur des cendres chaudes, brun cendré presque noir, la tête et le cou nus d'un rouge
orangé, une grosse caroncule jaune sous la gorge, la queue dressée en éventail vertical, les pieds énormes. Il a la
dignité de celui qui couve ses œufs dans un tas de sable et de feuilles, à la chaleur du volcan, sans jamais s'asseoir
dessus. Un pied gratte déjà le sol : le travail n'est jamais fini.

    python megapode.py        fabrique la fiche art/apercus/animaux/megapode.png (style du palier : C, velours ras)
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

CENDRE = np.array(M.hexa("#4a3d37"))          # la dominante (registre : brun cendré noirâtre), un cran plus clair (style C)
VENTRE = np.array(M.hexa("#5e4e46"))          # le ventre, le bas du cou emplumé
NOIR = np.array(M.hexa("#2c2623"))            # la queue, le bout des ailes
ROUGE = np.array(M.hexa("#e0552a"))           # l'accent : la tête et le cou nus, rouge orangé
JAUNE = np.array(M.hexa("#eac844"))           # la caroncule
BEC = M.hexa("#3a302a")
PATTE = np.array(M.hexa("#8a6e56"))           # les pattes et les gros pieds


def construire():
    a = K.Animal("megapode")
    a.taille = 0.62

    r = O.oiseau(a, dos=CENDRE, ventre=VENTRE, tete=ROUGE, aile=CENDRE * 0.96, queue=NOIR, bec=BEC, patte=PATTE, long=0.40, ray=0.140,
                 incline=26.0, z0=0.185, tete_r=(0.070, 0.078, 0.068), tete_pos=(0.0, -0.100, 0.070), bec_long=0.050, bec_ray=0.016,
                 aile_dim=(0.024, 0.098, 0.190), aile_pos=(0.0, 0.020, 0.0), queue_dim=(0.016, 0.130, 0.150), queue_haut=14.0,
                 patte_long=0.140, patte_ray=0.024, oeil_r=0.0140, oeil_dir=(0.42, -0.88, 0.20), bout_aile=NOIR)
    H, T, haut = r["H"], r["T"], r["haut"]

    # ----- le cou nu : un tube rouge orangé de l'épaule à la tête, la caroncule jaune qui pend dessous -----
    cou = O.tube_r([tuple(haut + Vector((0.0, -0.020, -0.025))), tuple(haut + Vector((0.0, -0.075, 0.040))), tuple(H + Vector((0.0, 0.010, -0.040)))],
                   [0.080, 0.066, 0.060], 18)
    a.piece("cou", O.teinte(cou, ROUGE), None)
    caro = A.boule(1.0, 28, 14).etire(0.062, 0.052, 0.080)
    a.piece("caroncule", O.teinte(caro, JAUNE), None, pos=tuple(haut + Vector((0.0, -0.075, -0.020))), poil=False)
    col = A.tore(0.062, 0.020, 28, 8)
    a.piece("collerette", O.teinte(col, VENTRE), None, pos=tuple(haut + Vector((0.0, -0.018, -0.030))), rot=(70, 0, 0))

    # ----- l'éventail de la queue : une lame verticale ronde, au bord à peine festonné, dressée derrière le dos -----
    # (16/10, planche 21 : les sept lobes pointus faisaient une queue à pointes ; les ailes en plateaux sont amincies)
    pts = [(0.0, 0.0)]
    for k in range(29):
        th = math.radians(-74 + 148 * k / 28)
        r = 0.226 + 0.008 * math.cos(math.pi * k / 2.0)
        pts.append((r * math.sin(th), r * math.cos(th)))
    eventail = A.decoupe(pts, 0.014, 0.005)
    eventail.teinte = np.tile(NOIR * 1.15, (len(eventail.v), 1))
    a.piece("eventail", O.couche(eventail, O.plan(Vector((0.0, 0.250, 0.215)), Vector((1.0, 0.0, 0.0)), Vector((0.0, 0.22, 1.0)))), None, poil=False)

    # ----- les pieds énormes : trois grands doigts devant, un petit derrière, de grosses griffes ; le pied droit gratte -----
    for nom, c in (("G", 1), ("D", -1)):
        base = Vector((c * 0.044, -0.030, 0.010))
        doigts = None
        for dx, an in ((-0.036, -0.34), (0.0, 0.0), (0.036, 0.34)):
            d = O.tube_r([(base.x + dx * 0.2, base.y + 0.010, base.z + 0.004), (base.x + dx * 1.0 + 0.040 * math.sin(an), base.y - 0.060, base.z + 0.002),
                          (base.x + dx * 1.5 + 0.090 * math.sin(an), base.y - 0.125, base.z + 0.001)], [0.0125, 0.0105, 0.0070], 8)
            d = O.teinte(d, PATTE)
            doigts = d if doigts is None else doigts + d
        arriere = O.tube_r([(base.x, base.y + 0.012, base.z + 0.004), (base.x, base.y + 0.052, base.z + 0.002)], [0.010, 0.0072], 8)
        doigts = doigts + O.teinte(arriere, PATTE)
        a.piece("doigts_" + nom, doigts, None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("megapode", styles.style_de("megapode"), sys.modules[__name__]), "Mégapode")
