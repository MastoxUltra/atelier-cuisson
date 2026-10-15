"""Le lézard de lave en peluche : le trapu des coulées, noir basalte, qui porte sa chaleur dessus : des veines orange magma
courent en zigzag sur son dos comme des fissures où le feu serait resté, et les bouts de ses doigts rougeoient. Large tête
plate, yeux cerclés d'orange, une queue épaisse retroussée au bout. Il se hisse sur ses pattes de devant, la gorge haute,
pour sentir la pierre refroidir. Il aime que ça refroidisse un peu, pas trop.

    python lezard_de_lave.py        fabrique la fiche art/apercus/animaux/lezard_de_lave.png (style du palier : C, velours ras)
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

BASALTE = np.array(M.hexa("#35353b"))         # la dominante (registre : noir basalte #2b2b30), un cran plus clair pour que la forme se lise
CENDRE = np.array(M.hexa("#4a4a52"))          # le dessous, les pattes
MAGMA = np.array(M.hexa("#ff7a1c"))           # l'accent : les veines orange magma
BRAISE = np.array(M.hexa("#ffb347"))          # le cœur des veines, le bout des doigts
FIL = M.hexa("#17171a")

# du bout de la queue au bout du nez : la queue retroussée au bout, le corps trapu, le cou qui se hisse, la tête haute
CHEMIN = [(0.18, 0.54, 0.060), (0.12, 0.56, 0.044), (0.06, 0.48, 0.040), (0.00, 0.38, 0.046), (-0.04, 0.26, 0.062), (-0.03, 0.14, 0.080),
          (0.00, 0.02, 0.092), (0.02, -0.10, 0.102), (0.02, -0.20, 0.120), (0.00, -0.29, 0.142), (-0.02, -0.38, 0.160), (-0.04, -0.45, 0.162)]
CORPS = O.interp([(0.0, 0.0), (0.03, 0.012), (0.12, 0.028), (0.32, 0.056), (0.48, 0.076), (0.66, 0.090), (0.78, 0.082),
                  (0.86, 0.064), (0.92, 0.070), (0.97, 0.062), (0.99, 0.042), (1.0, 0.0)])


def construire():
    a = K.Animal("lezard_de_lave")
    a.taille = 0.55

    # ----- le corps : une pièce couchée sur son fil ; les veines de magma en zigzag (des fissures transversales qui se
    #       rejoignent à une veine du dos) ; le dessous cendré ; le bout des doigts rougeoie -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        f = m.v[:, 2] / L
        t = np.tile(BASALTE, (len(f), 1))
        t[ang > 2.1] = CENDRE
        zig = np.abs(np.sin(f * math.pi * 11.0 + 1.9 * np.sin(ang * 3.0 + f * 9.0)))
        long_ = np.abs(np.sin(ang * 2.6 + f * 14.0 * 0.6 + 0.4 * np.sin(f * 30.0)))
        veine = ((zig < 0.085) | (ang < 0.07) | ((long_ < 0.05) & (f > 0.25))) & (ang < 2.0) & (f > 0.04) & (f < 0.90)
        t[veine] = MAGMA
        t[veine & (zig < 0.035)] = BRAISE
        return t

    def tete(L):
        def g(v):
            s = v.copy()
            fr = v[:, 2] / L
            h = np.clip((fr - 0.88) / 0.05, 0.0, 1.0)
            h = h * h * (3 - 2 * h)
            s[:, 1] *= 1.0 - 0.22 * h
            s[:, 0] *= 1.0 + 0.20 * h
            return s
        return g
    fil, L = O.fil_corps(a, "corps", CHEMIN, CORPS, peint, None, cotes=40, flanc=(1.0, 0.0, 0.0), deforme=tete)

    # ----- le visage : des yeux vivants cerclés de magma, la bouche large, deux narines -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, direction = fil.vise(0.945 * L, 0.10, c * 0.80, 0.70)
        pos, n = a.surface("corps", centre, direction)
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0185)
        h = (Vector((0.0, 0.0, 1.0)) - n * n.z).normalized()
        a.piece("cerne_" + nom, K.paupiere(0.0215, 0.30), tuple(MAGMA), mat=A.cadre(pos + n * 0.0015, n, h), poil=False)
    for c in (1, -1):
        pts = []
        for u_ in np.linspace(0.0, 1.0, 9):
            cc, dd = fil.vise((0.994 - 0.080 * u_) * L, 0.0, c * 1.0, -0.30 + 0.12 * u_)
            q = a.trace("corps", cc, [dd], 0.002)
            if q:
                pts.append(q[0])
        if len(pts) > 1:
            a.broderie("bouche_" + ("G" if c > 0 else "D"), A.courbe(pts, 3), 0.0026, FIL)

    # ----- les pattes : les antérieures tendues qui hissent la poitrine, les postérieures repliées ; le bout des doigts rougeoie -----
    def pied(pos, direction):
        m = A.boule(1.0, 16, 8).etire(0.028, 0.010, 0.030)
        m.teinte = np.tile(CENDRE, (len(m.v), 1))
        for dx, an in ((-0.024, -0.30), (-0.008, -0.10), (0.008, 0.10), (0.024, 0.30)):
            d = K.tube_peint([(dx * 0.4, 0.0, 0.018), (dx + 0.020 * math.sin(an), 0.0, 0.040), (dx * 1.8 + 0.036 * math.sin(an), 0.0, 0.066)],
                             lambda t: 0.0100 - 0.003 * t, [(0.70, tuple(CENDRE)), (1.0, tuple(BRAISE))], 8)
            m = m + d
        return O.couche(m, A.cadre(pos, direction, (0, 0, 1)))

    for c, nm in ((1, "G"), (-1, "D")):
        cen, av, nq = (Vector(q) for q in fil.cadre(0.700 * L))
        cote = nq.cross(av)
        racine = cen + cote * (c * 0.070) - nq * 0.020
        coude = cen + cote * (c * 0.130)
        coude.z = 0.082
        main = Vector((cen.x + c * 0.112, cen.y - 0.040, 0.016))
        pts = [tuple(racine), tuple(racine + (coude - racine) * 0.55), tuple(coude), tuple(main + Vector((0, 0, 0.012)))]
        a.piece("bras_" + nm, O.membre(pts, [0.046, 0.039, 0.033, 0.028], [(1.0, tuple(BASALTE * 0.96))], 16), None)
        a.piece("main_" + nm, pied(Vector((main.x, main.y, 0.012)), Vector((c * 0.30, -0.95, 0.0))), None, poil=False)
        ch, avh, nqh = (Vector(q) for q in fil.cadre(0.380 * L))
        coteh = nqh.cross(avh)
        rh = ch + coteh * (c * 0.070) - nqh * 0.015
        genou = ch + coteh * (c * 0.140) + avh * (-0.060)
        genou.z = 0.070
        pd = Vector((ch.x + c * 0.118, ch.y + 0.020, 0.016))
        pts = [tuple(rh), tuple(rh + (genou - rh) * 0.55), tuple(genou), tuple(pd + Vector((0, 0, 0.012)))]
        a.piece("jambe_" + nm, O.membre(pts, [0.056, 0.046, 0.036, 0.029], [(1.0, tuple(BASALTE * 0.96))], 16), None)
        a.piece("pied_" + nm, pied(Vector((pd.x, pd.y, 0.012)), Vector((c * 0.45, -0.90, 0.0))), None, poil=False)
    a.tete = Vector(fil.cadre(0.97 * L)[0]) + Vector((0.0, -0.06, 0.02))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad", souple=True)


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lezard_de_lave", styles.style_de("lezard_de_lave"), sys.modules[__name__]), "Lézard de lave")
