"""Le poisson-hache en peluche : la lame d'argent des plateaux, un corps haut et plat comme le fer d'une hache, la quille du
ventre en tranchant, une queue fine et courte, et deux yeux en tubes jaunes, dressés vers le haut : il regarde toujours au-dessus
de lui, d'où tombe le peu de jour qui reste. Il reflète la moindre lueur ; il ne se voit donc jamais : il n'y a que ce qu'il
renvoie.

    python poisson_hache.py        fabrique la fiche art/apercus/animaux/poisson_hache.png (style du palier : voir styles.py)
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

ARGENT = np.array(M.hexa("#cfd8e2"))          # la dominante (registre : argent miroir)
DOS = np.array(M.hexa("#8fa0b6"))             # le dos plus sombre
ORBE = np.array(M.hexa("#f1c93c"))            # l'accent : les yeux tubulaires jaunes
LUEUR = np.array(M.hexa("#bfe6ff"))           # les photophores du ventre
FIL = M.hexa("#5a6c86")


TOURNE = 34                                   # la fiche tourne le poisson (très plat) presque de face : on compte les DEUX yeux ; 0 pour le jeu


def construire():
    a = K.Animal("poisson_hache")
    a.taille = 0.30                                # plus gros : il se noyait dans l'herbe

    # ----- le corps : un disque haut et mince, la quille en bas qui avance en tranchant, le dos plus sombre ; le pédoncule de
    #       la queue : un fuseau fin derrière -----
    def lame(v):
        s = v.copy()
        z = v[:, 2]
        y = v[:, 1]
        s[:, 2] = np.where(z < 0, z * (1.0 + 0.42 * np.clip(-y, 0, 1)), z)                 # la quille en lame de hache : très basse devant
        s[:, 1] = y * (1.0 + 0.10 * np.clip(z, 0, 1))
        s[:, 0] *= 1.0 - 0.45 * np.clip(-z, 0, 1) ** 1.2                                   # le ventre en tranchant
        return s
    corps = A.boule(1.0, 52, 26)
    u = corps.v / np.maximum(np.linalg.norm(corps.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(ARGENT, (len(u), 1))
    t[u[:, 2] > 0.55] = DOS
    corps.teinte = t
    a.piece("corps", corps.sculpte(lame).etire(0.044, 0.120, 0.160), None, pos=(0.0, 0.0, 0.200), poil=False)      # argenté et lisse : le corps plat en hache
    pedoncule = A.tour(A.profil([(0.0, 0.0), (0.040, 0.020), (0.024, 0.090), (0.012, 0.170), (0.010, 0.200)], 4), 20)
    pedoncule.teinte = np.tile(ARGENT * 0.96, (len(pedoncule.v), 1))
    a.piece("pedoncule", O.couche(pedoncule, A.cadre(Vector((0.0, 0.080, 0.225)), Vector((0.0, 1.0, 0.05)), (0, 0, 1))), None, poil=False)

    # ----- la queue en fourche et les petites nageoires -----
    queue = O.nageoire([(0, 0.010), (0.04, 0.045), (0.11, 0.090), (0.075, 0.0), (0.11, -0.090), (0.04, -0.045), (0, -0.010)], 0.012, ARGENT * 0.92)
    a.piece("caudale", O.couche(queue, O.plan_vertical(Vector((0.0, 0.262, 0.209)), Vector((0.0, 1.0, 0.0)))), None, poil=False)
    dor = O.nageoire([(0, 0), (0.030, 0.070), (0.060, 0.050), (0.080, 0.0)], 0.010, DOS)
    a.piece("dorsale", O.couche(dor, O.plan_dos(Vector((0.0, 0.065, 0.320)), Vector((0, 0, 1)))), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        pec = A.boule(1.0, 16, 8).etire(0.006, 0.040, 0.016)
        pec.teinte = np.tile(ARGENT * 0.9, (len(pec.v), 1))
        a.piece("pectorale_" + nom, pec, None, pos=(c * 0.030, -0.040, 0.170), rot=(0, 0, c * -20), poil=False)

    # ----- les yeux : deux tubes jaunes dressés vers le haut, la pupille au bout ; la bouche petite, dirigée vers le haut -----
    for nom, c in (("G", 1), ("D", -1)):
        tube = A.tour(A.profil([(0.014, 0.0), (0.014, 0.050), (0.012, 0.074), (0.0, 0.082)], 4), 18)
        tube.teinte = np.tile(ORBE, (len(tube.v), 1))
        # (plus de tubes à tiges : les yeux sont posés directement sur la tête)
        pupille = A.boule(1.0, 14, 8).etire(0.016, 0.016, 0.010)
        a.oeil("oeil_" + nom, Vector((c * 0.036, -0.100, 0.292)), Vector((c * 0.40, -0.86, 0.32)).normalized(), 0.022)      # sur le front, regardant vers l'avant : les deux se voient de face
    bouche = A.tour(A.profil([(0.014, 0.0), (0.011, 0.014), (0.006, 0.026), (0.0, 0.030)], 3), 18).etire(1.0, 0.6, 1.0)
    bouche.teinte = np.tile(ARGENT * 0.92, (len(bouche.v), 1))
    a.piece("bouche", O.couche(bouche, A.cadre(Vector((0.0, -0.110, 0.285)), Vector((0.0, -1.0, 0.70)), (0, 0, 1))), None, poil=False)      # lisse : plus de boule grise sur la face

    # ----- les photophores : un rang de points bleu pâle le long de la quille, de chaque côté -----
    pts = []
    for c in (1, -1):
        for k in range(9):
            y = -0.075 + 0.0185 * k
            z = 0.178 - 0.150 * math.sqrt(max(1 - (y / 0.105) ** 2, 0.0)) * (1.0 + 0.10 * (-y) / 0.1) + 0.012
            pts.append((Vector((c * 0.0125, y, z)), Vector((c * 1.0, 0.0, -0.45)).normalized()))
    a.piece("photophores", O.points_lumineux(pts, 0.0075, LUEUR), None, poil=False)
    a.tete = Vector((0.0, -0.11, 0.30))
    if TOURNE:
        O.tourner(a, TOURNE)
    th_ = math.radians(TOURNE)
    a.cap_tete = (math.sin(th_), -math.cos(th_), 0.0)         # l'avant de la tête, en monde : la vue de près se place devant lui (peluche.py, 16/10)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("poisson_hache", styles.style_de("poisson_hache"), sys.modules[__name__]), "Poisson-hache")
