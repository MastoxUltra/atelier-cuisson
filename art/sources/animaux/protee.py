"""Le protée en peluche : le « dragon des grottes », long comme un serpent pâle, chair tiède presque translucide, un long
museau plat en spatule, des yeux couverts de peau (à peine deux points rosés), trois panaches de branchies d'un rouge vif qui
s'ouvrent derrière la tête, quatre pattes minuscules aux trois doigts. Il glisse en S sur la pierre mouillée, la tête haute
dans le noir, et ne vieillit presque pas : on dit qu'il peut jeûner dix ans sans que personne s'en aperçoive.

    python protee.py        fabrique la fiche art/apercus/animaux/protee.png (style du palier : B, peluche de magasin)
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

CHAIR = np.array(M.hexa("#f6e2d9"))           # la dominante (registre : chair pâle tiède #f2dcd4), un cran plus clair (style B)
DESSOUS = np.array(M.hexa("#fbeee8"))         # le ventre
ROUGE = np.array(M.hexa("#e0332f"))           # l'accent : les branchies rouges
OEIL = np.array(M.hexa("#d9a49c"))            # les yeux sous la peau
FIL = M.hexa("#9a6a5c")

# du bout de la queue au bout du museau : un long S sur le sol, la tête qui se relève à peine
CHEMIN = [(0.32, 0.72, 0.016), (0.34, 0.62, 0.022), (0.28, 0.52, 0.030), (0.16, 0.44, 0.038), (0.04, 0.36, 0.044), (-0.08, 0.26, 0.048),
          (-0.12, 0.14, 0.050), (-0.08, 0.02, 0.052), (0.00, -0.08, 0.054), (0.08, -0.18, 0.054), (0.10, -0.29, 0.054), (0.04, -0.39, 0.054),
          (-0.04, -0.46, 0.056), (-0.12, -0.52, 0.060), (-0.20, -0.57, 0.064)]
CORPS = O.interp([(0.0, 0.0), (0.02, 0.008), (0.12, 0.020), (0.34, 0.036), (0.52, 0.048), (0.70, 0.052), (0.82, 0.050),
                  (0.88, 0.046), (0.93, 0.040), (0.965, 0.034), (0.985, 0.026), (1.0, 0.0)])


def construire():
    a = K.Animal("protee")
    a.taille = 0.55

    # ----- le corps : un long fuseau couché sur son fil, un peu aplati ; le museau en spatule ; le ventre plus clair ;
    #       les plis des flancs en anneaux très doux -----
    def rayon(f):
        return CORPS(f) * (1.0 + 0.045 * math.cos(2.0 * math.pi * 14.0 * f))

    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        f = m.v[:, 2] / L
        t = np.tile(CHAIR, (len(f), 1))
        t[ang > 2.1] = DESSOUS
        t[np.cos(2.0 * math.pi * 14.0 * f) < -0.82] = CHAIR * 0.95
        return t

    def spatule(L):
        def g(v):
            s = v.copy()
            fr = v[:, 2] / L
            s[:, 1] *= 1.0 - 0.14 * np.clip(fr * 2.0, 0.0, 1.0) - 0.28 * np.clip((fr - 0.90) / 0.08, 0.0, 1.0)     # le museau plat
            s[:, 0] *= 1.0 + 0.30 * np.clip((fr - 0.92) / 0.06, 0.0, 1.0)                                         # et large au bout
            return s
        return g
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=36, flanc=(1.0, 0.0, 0.0), deforme=spatule)

    # ----- le visage : deux points rosés sous la peau, une bouche fine, deux narines -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, direction = fil.vise(0.945 * L, 0.10, c * 0.80, 0.60)
        pos, n = a.surface("corps", centre, direction)
        point = A.boule(1.0, 10, 6).etire(0.0075, 0.0075, 0.0040)
        a.piece("oeil_" + nom, O.couche(O.teinte(point, OEIL), A.cadre(pos + n * 0.0005, n, (0, 0, 1))), None, poil=False)
        pts_b = []
        for u_ in np.linspace(0.0, 1.0, 9):
            cc, dd = fil.vise((0.998 - 0.060 * u_) * L, 0.0, c * 1.0, -0.30 + 0.06 * u_)
            q = a.trace("corps", cc, [dd], 0.002)
            if q:
                pts_b.append(q[0])
        if len(pts_b) > 1:
            a.broderie("bouche_" + nom, A.courbe(pts_b, 3), 0.0022, FIL)

    # ----- les branchies : trois panaches rouges de chaque côté, qui s'ouvrent en éventail derrière la tête ; les petites pattes -----
    for c, nm in ((1, "G"), (-1, "D")):
        cen, av, nq = (Vector(q) for q in fil.cadre(0.862 * L))
        cote = nq.cross(av)
        base = cen + cote * (c * CORPS(0.862) * 0.95) + nq * 0.010
        axe = cote * (c * 1.0) + av * (-0.70) + nq * 0.30
        a.piece("branchies_" + nm, O.plumes(base, axe, nq, n=3, long=0.100, ray=0.0085, couleur=tuple(ROUGE), filaments=7), None, poil=False)
        for pos_f, nom, doigts in ((0.790, "avant", 3), (0.420, "arriere", 2)):
            cn, avn, nqn = (Vector(q) for q in fil.cadre(pos_f * L))
            cn2 = nqn.cross(avn)
            r = cn + cn2 * (c * 0.040) - nqn * 0.012
            coude = cn + cn2 * (c * 0.072)
            coude.z = 0.028
            main = Vector((cn.x + c * 0.085, cn.y - 0.016 if nom == "avant" else cn.y + 0.014, 0.008))
            m = O.tube_r([tuple(r), tuple(coude), tuple(main + Vector((0, 0, 0.004)))], [0.016, 0.0125, 0.010], 10)
            for k in range(doigts):
                dx = (k - (doigts - 1) / 2.0) * 0.014
                m = m + O.tube_r([tuple(main), tuple(main + Vector((c * 0.018 + dx, -0.026, -0.001)))], [0.0052, 0.0036], 6)
            m.teinte = np.tile(CHAIR, (len(m.v), 1))
            a.piece("patte_%s_%s" % (nom, nm), m, None, poil=False)
    a.tete = Vector(fil.cadre(0.97 * L)[0]) + Vector((-0.05, -0.04, 0.02))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad", souple=True)


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("protee", styles.style_de("protee"), sys.modules[__name__]), "Protée")
