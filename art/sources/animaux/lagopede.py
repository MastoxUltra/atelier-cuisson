"""Le lagopède en peluche, quatrième dessin, sur une autre base (l'oiseau debout de outils_a, comme le pigeon) : la perdrix
des neiges d'après la photo de référence (art/sources/references/lagopede/). Un gallinacé dodu, la poitrine en proue,
le corps incliné d'une quarantaine de degrés, la petite tête ronde sur un cou court, le bec court et sombre, le sourcil
rouge en croissant au-dessus de l'œil ; le dos et la poitrine grège moucheté de brun, les ailes et le ventre blancs, la
queue noire qui dépasse en pointe vers le sol. Les pattes sont emplumées de blanc jusqu'aux orteils : de gros chaussons.

    python lagopede.py        fabrique la fiche art/apercus/animaux/lagopede.png (style du palier : C, velours ras)
    (les trois premiers dessins, jugés le 15/10 : « une boule, des chaussons détachés, un œuf aux ailes en volets »)
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

GREGE = np.array(M.hexa("#bca586"))           # la dominante (registre : grège moucheté) ; le velours éclaircit un peu
MOUCHE = np.array(M.hexa("#7f6a55"))          # les mouchetures
BLANC = np.array(M.hexa("#fbf9f4"))           # les ailes, le ventre, les chaussons
NOIR = np.array(M.hexa("#26211f"))            # la queue
VERMILLON = M.hexa("#ee3b22")                 # l'accent : le sourcil
BEC = M.hexa("#241e1c")


def construire():
    a = K.Animal("lagopede")
    a.taille = 0.52

    r = O.oiseau(a, dos=GREGE, ventre=BLANC * 0.98, tete=GREGE * 0.97, aile=GREGE * 0.96, queue=NOIR, bec=BEC, patte=BLANC, long=0.40, ray=0.152,
                 incline=38.0, z0=0.150, tete_r=(0.058, 0.062, 0.056), tete_pos=(0.0, -0.062, 0.050), bec_long=0.036, bec_ray=0.0165,
                 bec_baisse=-0.12, aile_dim=(0.024, 0.088, 0.135), aile_pos=(-0.004, 0.030, -0.012), queue_dim=(0.046, 0.115, 0.014),
                 queue_haut=-30.0, patte_long=0.110, patte_ray=0.030, oeil_r=0.0135, oeil_dir=(0.42, -0.88, 0.22), bout_aile=BLANC,
                 coupe_dos=1.35)
    H, T, haut = r["H"], r["T"], r["haut"]

    # ----- les mouchetures : de petites taches brunes semées sur le dos, la poitrine et le cou, posées à plat sur le corps -----
    rng = np.random.default_rng(21)
    taches = None
    prof_z = [0.0, 0.010, 0.070, 0.160, 0.250, 0.315, 0.350, 0.362]
    prof_r = [0.0, 0.55, 0.90, 1.0, 0.88, 0.62, 0.34, 0.0]
    for k in range(95):
        th = rng.uniform(-2.2, 2.2)                                                  # 0 : le dos ; ±π : le ventre
        zz = rng.uniform(0.06, 0.34) * 0.40 / 0.34
        rr = 0.152 * float(np.interp(zz / (0.40 / 0.34), prof_z, prof_r))
        if rr < 0.04 or abs(th) > 2.0 and zz < 0.16:
            continue
        n = (T.to_3x3() @ Vector((math.sin(th), math.cos(th), 0.0))).normalized()
        pos = T @ Vector((rr * math.sin(th), rr * math.cos(th) + 0.001, zz))
        g = A.boule(1.0, 10, 6).etire(0.014 + 0.006 * rng.random(), 0.010 + 0.005 * rng.random(), 0.0035)
        g = O.couche(O.teinte(g, MOUCHE), A.cadre(pos, n, (0, 0, 1)))
        taches = g if taches is None else taches + g
    a.piece("mouchetures", taches, None, poil=False)

    # ----- le sourcil rouge : un croissant plat posé juste au-dessus de chaque œil -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", H, Vector((c * 0.74, -0.46, 0.50)))
        sourcil = A.boule(1.0, 16, 8).etire(0.0195, 0.0070, 0.0050)
        a.piece("sourcil_" + nom, O.couche(O.teinte(sourcil, np.array(VERMILLON)), A.cadre(pos + n * 0.001, n, (0, 0, 1))), None, poil=False)

    # ----- les chaussons : deux gros pieds emplumés de blanc, les orteils à peine visibles dessous ; le dessous de la queue blanc -----
    for nom, c in (("G", 1), ("D", -1)):
        chausson = A.boule(1.0, 28, 14).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.040, 0.082, 0.034)
        a.piece("chausson_" + nom, O.teinte(chausson, BLANC), None, pos=(c * 0.052, -0.040, 0.034))
    sous = A.boule(1.0, 20, 10).etire(0.034, 0.060, 0.026)
    a.piece("sous_queue", O.teinte(sous, BLANC), None, mat=T @ A.repere((0.0, 0.055, 0.020), (-10, 0, 0)))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lagopede", styles.style_de("lagopede"), sys.modules[__name__]), "Lagopède")
