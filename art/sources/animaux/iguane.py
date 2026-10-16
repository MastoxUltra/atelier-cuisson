"""L'iguane en peluche : le grand lézard des roches chaudes, mauve poussiéreux, une crête de pointes ocre qui court de la
nuque jusqu'au milieu de la queue, le fanon rose en voile sous la gorge, une grosse écaille ronde pâle sur la joue, la
queue longue annelée de sombre. Dressé sur ses bras raides, la tête haute, l'œil lourd et glacé, il prend le soleil du
volcan avec l'air d'un notaire qui a décidé de ne pas bouger.

    python iguane.py        fabrique la fiche art/apercus/animaux/iguane.png (style du palier : C, velours ras)
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

MAUVE = np.array(M.hexa("#a88bad"))           # la dominante (registre : mauve poussiéreux #9a7fa0), un cran plus clair (style C)
BAGUE = np.array(M.hexa("#76627f"))           # les anneaux de la queue, les pattes
VENTRE = np.array(M.hexa("#cdb9cf"))          # le dessous
OCRE = np.array(M.hexa("#d1a95c"))            # l'accent : la crête
FANON = np.array(M.hexa("#dba6a0"))           # le fanon sous la gorge
JOUE = np.array(M.hexa("#e6d9c6"))            # la grosse écaille de la joue
FIL = M.hexa("#2c2230")

# du bout de la queue au bout du nez : la queue qui ondule au sol, le dos, puis le cou qui se dresse et la tête haute
CHEMIN = [(0.30, 0.86, 0.020), (0.22, 0.76, 0.026), (0.10, 0.64, 0.036), (-0.02, 0.52, 0.054), (-0.08, 0.40, 0.080), (-0.04, 0.28, 0.108),
          (0.00, 0.16, 0.130), (0.00, 0.04, 0.150), (0.00, -0.08, 0.168), (0.00, -0.18, 0.190), (0.00, -0.26, 0.235),
          (0.00, -0.32, 0.290), (0.00, -0.38, 0.340), (0.00, -0.45, 0.372), (0.00, -0.53, 0.378)]
CORPS = O.interp([(0.0, 0.0), (0.02, 0.006), (0.10, 0.016), (0.30, 0.030), (0.46, 0.048), (0.60, 0.070), (0.72, 0.078),
                  (0.79, 0.058), (0.85, 0.046), (0.89, 0.052), (0.925, 0.066), (0.950, 0.064), (0.972, 0.050), (0.988, 0.036), (0.998, 0.022), (1.0, 0.0)])


def construire():
    a = K.Animal("iguane")
    a.taille = 0.95

    # ----- le corps : une longue pièce couchée sur son fil, les anneaux de la queue, le dessous plus clair, la tête un
    #       peu large derrière, le museau court -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        f = m.v[:, 2] / L
        t = np.tile(MAUVE, (len(f), 1))
        t[ang > 2.1] = VENTRE
        anneau = (f < 0.52) & (np.sin(f * 2.0 * math.pi * 11.0) > 0.25)
        t[anneau] = BAGUE
        t[(f > 0.60) & (f < 0.78) & (np.sin((f - 0.60) * 2.0 * math.pi * 7.0) > 0.55) & (ang < 2.0)] = BAGUE * 0.9 + MAUVE * 0.1
        return t

    def tete(L):
        def g(v):
            s = v.copy()
            fr = v[:, 2] / L
            h = np.clip((fr - 0.885) / 0.045, 0.0, 1.0)                 # la tête : large derrière (les mâchoires), plate dessus
            h = h * h * (3 - 2 * h)
            s[:, 0] *= 1.0 + 0.34 * h
            s[:, 1] *= 1.0 - 0.30 * h
            pt = np.clip((fr - 0.955) / 0.045, 0.0, 1.0)                # le museau : un coin qui s'effile
            s[:, 0] *= 1.0 - 0.18 * pt
            return s
        return g
    fil, L = O.fil_corps(a, "corps", CHEMIN, CORPS, peint, None, cotes=34, flanc=(1.0, 0.0, 0.0), deforme=tete)

    # ----- la crête : des pointes ocre le long du dos, de la nuque jusque dans la queue, les plus hautes sur le cou -----
    crete = None
    for k, f in enumerate(np.linspace(0.30, 0.90, 24)):
        c, av, nq = (Vector(q) for q in fil.cadre(f * L))
        h = 0.034 + 0.058 * math.exp(-((f - 0.80) / 0.17) ** 2)         # des plaques triangulaires, les plus hautes sur la nuque
        base = c + nq * (CORPS(f) * 0.80)
        tri = [(-0.013, 0.0), (0.013, 0.0), (0.006, h * 0.50), (0.008 + 0.08 * h, h), (-0.004, h * 0.50)]
        pl = A.decoupe(tri, 0.0075, 0.0030)
        pl.teinte = np.tile(OCRE, (len(pl.v), 1))
        p = O.couche(pl, A.cadre(base, nq.cross(av), nq))
        crete = p if crete is None else crete + p
    a.piece("crete", crete, None, poil=False)

    # ----- le fanon : une voile rose sous la gorge, toute plate dans le plan du cou -----
    c0, av0, nq0 = (Vector(q) for q in fil.cadre(0.925 * L))
    dessous = -nq0
    pts = [(0.0, 0.0), (0.030, 0.010), (0.062, 0.040), (0.070, 0.082), (0.040, 0.106), (0.0, 0.100), (-0.030, 0.082),
           (-0.050, 0.050), (-0.028, 0.012)]
    fanon = A.decoupe([(0.42 * x_, 0.50 * y_) for x_, y_ in pts], 0.010, 0.004)
    fanon.teinte = np.tile(FANON, (len(fanon.v), 1))
    # le plan du fanon : x vers l'avant, y vers le bas, l'épaisseur sur le côté
    # (plus de fanon : en boule rose il se lisait comme une langue ; la gorge reste lisse)

    # ----- le visage : un œil lourd sous sa paupière, la grosse écaille ronde sur la joue, la bouche, deux narines -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, direction = fil.vise(0.950 * L, 0.80, c * 0.50, 0.12)
        pos, n = a.surface("corps", centre, direction)
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0155)
        h = (Vector((0.0, 0.0, 1.0)) - n * n.z).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.0155, 0.60), tuple(MAUVE * 0.9), mat=A.cadre(pos + n * 0.002, n, h), poil=False)
        cj, dj = fil.vise(0.915 * L, -0.25, c * 0.95, -0.15)
        pj, nj = a.surface("corps", cj, dj)
        ecaille = A.boule(1.0, 20, 10).etire(0.026, 0.024, 0.0045)
        ecaille.teinte = np.tile(JOUE, (len(ecaille.v), 1))
        a.piece("joue_" + nom, O.couche(ecaille, A.cadre(pj + nj * 0.001, nj, (0, 0, 1))), None, poil=False)
        pts_b = []
        for u_ in np.linspace(0.0, 1.0, 8):
            cc, dd = fil.vise((0.996 - 0.060 * u_) * L, 0.0, c * 1.0, -0.38 + 0.10 * u_)
            q = a.trace("corps", cc, [dd], 0.002)
            if q:
                pts_b.append(q[0])
        if len(pts_b) > 1:
            a.broderie("bouche_" + nom, A.courbe(pts_b, 3), 0.0024, FIL)

    # ----- les pattes : les antérieures raides qui dressent la poitrine, les postérieures repliées ; de longs doigts -----
    def doigts(dim_long, cuiss_pos, direction):
        m = A.boule(1.0, 16, 8).etire(0.024, 0.009, 0.026)
        for dx, an in ((-0.020, -0.38), (-0.007, -0.12), (0.007, 0.12), (0.020, 0.38)):
            d = O.tube_r([(dx * 0.4, 0.0, 0.020), (dx + 0.020 * math.sin(an), 0.0, 0.040 + 0.020 * math.cos(an)),
                          (dx * 1.8 + 0.030 * math.sin(an), 0.0, 0.040 + dim_long)], [0.0075, 0.0060, 0.0042], 8)
            d.teinte = np.tile(BAGUE, (len(d.v), 1))
            m = m + d
        m.teinte = np.tile(BAGUE, (len(m.v), 1))
        return O.couche(m, A.cadre(cuiss_pos, direction, (0, 0, 1)))

    for c, nm in ((1, "G"), (-1, "D")):
        # l'antérieure : de l'épaule droit vers le sol, le coude un peu au-dehors
        cen, av, nq = (Vector(q) for q in fil.cadre(0.665 * L))
        cote = nq.cross(av)
        r = cen + cote * (c * 0.060) - nq * 0.020
        coude = cen + cote * (c * 0.110) - nq * 0.075 + av * 0.0
        coude.z = 0.092
        main = Vector((cen.x + c * 0.100, cen.y - 0.030, 0.014))
        pts = [tuple(r), tuple(r + (coude - r) * 0.6), tuple(coude), tuple(main + Vector((0, 0, 0.012)))]
        a.piece("bras_" + nm, O.membre(pts, [0.036, 0.030, 0.026, 0.022], [(1.0, tuple(BAGUE * 0.6 + MAUVE * 0.4))], 16), None)
        a.piece("main_" + nm, doigts(0.034, Vector((main.x, main.y, 0.011)), Vector((c * 0.30, -0.95, 0.0))), None, poil=False)
        # la postérieure : la cuisse en avant, le genou plié, le pied plat sous
        ch, avh, nqh = (Vector(q) for q in fil.cadre(0.395 * L))
        coteh = nqh.cross(avh)
        rh = ch + coteh * (c * 0.060) - nqh * 0.015
        genou = ch + coteh * (c * 0.125) + avh * (-0.060)
        genou.z = 0.060
        pied = Vector((ch.x + c * 0.105, ch.y + 0.030, 0.014))
        pts = [tuple(rh), tuple(rh + (genou - rh) * 0.55), tuple(genou), tuple(pied + Vector((0, 0, 0.012)))]
        a.piece("jambe_" + nm, O.membre(pts, [0.046, 0.038, 0.030, 0.024], [(1.0, tuple(BAGUE * 0.6 + MAUVE * 0.4))], 16), None)
        a.piece("pied_" + nm, doigts(0.036, Vector((pied.x, pied.y, 0.011)), Vector((c * 0.45, -0.90, 0.0))), None, poil=False)
    a.tete = Vector(fil.cadre(0.97 * L)[0]) + Vector((0.0, -0.06, 0.0))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad", souple=True)


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("iguane", styles.style_de("iguane"), sys.modules[__name__]), "Iguane")
