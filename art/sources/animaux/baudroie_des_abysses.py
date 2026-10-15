"""La baudroie des abysses en peluche : une grosse boule aubergine toute en bouche, posée au fond du noir. Une
gueule énorme coupée à l'équerre, bordée de dents de feutrine blanche mal alignées, deux petits yeux de rien, et au bout
d'une tige qui part du front une lanterne jaune citron qui pend devant le museau : elle attend qu'on s'approche pour
voir ce que c'est. Les nageoires sont des moignons posés sur le sable comme des mains.

    python baudroie_des_abysses.py        fabrique la fiche art/apercus/animaux/baudroie_des_abysses.png (style du palier : B)
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

AUBERGINE = np.array(M.hexa("#4a3248"))       # la dominante (registre : aubergine sombre) ; le style B éclaircit un peu
GRIS = np.array(M.hexa("#7b6a7a"))            # le dessous, les nageoires
CITRON = M.hexa("#fff04a")                    # l'accent : la lanterne
DENT = M.hexa("#fbf7ea")
BOUCHE = np.array(M.hexa("#241522"))          # l'intérieur de la gueule
FIL = M.hexa("#16101a")


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def construire():
    a = K.Animal("baudroie_des_abysses")
    a.taille = 1.00

    # ----- le corps : une grosse boule aplatie, la gueule en dessous du front ; plus sombre dessus -----
    def forme(v):
        s = v.copy()
        s[:, 0] *= 0.96
        s[:, 1] *= 1.06
        s[:, 2] = np.where(v[:, 2] < 0, v[:, 2] * 0.75, v[:, 2] * 1.0)
        r_ = np.clip(v[:, 1] / 1.0, 0.0, 1.0)
        s[:, 0] *= 1.0 - 0.32 * r_ ** 1.4                               # le derrière s'effile en queue
        s[:, 2] *= 1.0 - 0.22 * r_ ** 1.4
        return s
    corps = A.boule(1.0, 64, 32)
    u = corps.v / np.maximum(np.linalg.norm(corps.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(AUBERGINE, (len(u), 1))
    t[u[:, 2] < -0.25] = GRIS
    corps.teinte = t
    a.piece("corps", corps.sculpte(forme).etire(0.280, 0.300, 0.250), None, pos=(0.0, 0.0, 0.250))

    # ----- la gueule : une fente énorme sur le devant, l'intérieur sombre, deux rangées de dents irrégulières -----
    CENTRE = Vector((0.0, 0.0, 0.240))
    haut, bas = [], []
    for u_ in np.linspace(-1.0, 1.0, 13):
        haut.append(Vector((0.92 * u_, -0.98, 0.10 + 0.14 * u_ * u_)))
        bas.append(Vector((0.92 * u_, -0.92, -0.12 + 0.20 * u_ * u_)))
    lèvre = [a.trace("corps", CENTRE, [d], 0.004)[0] for d in haut]
    a.broderie("gueule_haut", A.courbe(lèvre, 4), 0.0075, FIL)
    menton = [a.trace("corps", CENTRE, [d], 0.004)[0] for d in bas]
    a.broderie("gueule_bas", A.courbe(menton, 4), 0.0075, FIL)
    # l'intérieur de la gueule : une bande sombre qui suit la peau entre la lèvre du haut et celle du bas
    rangs = []
    for r_ in np.linspace(0.0, 1.0, 5):
        ligne = []
        for h_, b_ in zip(haut, bas):
            q = a.trace("corps", CENTRE, [h_ * (1 - r_) + b_ * r_], 0.0035)
            ligne.append(np.array(q[0]) if q else None)
        rangs.append(ligne)
    pts_g, faces_g = [], []
    for r_ in range(5):
        for c_ in range(13):
            p_ = rangs[r_][c_]
            pts_g.append(p_ if p_ is not None else rangs[r_][max(c_ - 1, 0)])
    for r_ in range(4):
        for c_ in range(12):
            q0 = r_ * 13 + c_
            faces_g.append((q0, q0 + 1, q0 + 14, q0 + 13))
    P_ = np.array(pts_g)
    n_ = len(P_)
    toutes_ = list(faces_g) + [tuple(q + n_ for q in reversed(f)) for f in faces_g]
    bande = A.Maille(np.vstack([P_, P_]), toutes_)
    bande.teinte = np.tile(BOUCHE, (2 * n_, 1))
    a.piece("palais", bande, None, poil=False)

    # la mâchoire du bas : une vraie pièce, qui avance en avant du museau ; ses crocs sont plantés sur son bord
    JC = Vector((0.0, -0.205, 0.140))
    jaw = A.boule(1.0, 40, 20).etire(0.185, 0.205, 0.066)
    jt = np.tile(AUBERGINE * 1.05, (len(jaw.v), 1))
    jt[jaw.v[:, 2] < -0.01] = GRIS
    jaw.teinte = jt
    a.piece("machoire", jaw, None, pos=tuple(JC))
    rng = np.random.default_rng(4)
    for k_, phi in enumerate(np.linspace(-1.20, 1.20, 9)):
        d_ = Vector((math.sin(phi) * 0.95, -math.cos(phi), 0.46))
        try:
            pb, nb = a.surface("machoire", JC, d_)
        except ValueError:
            continue
        long = 0.060 + 0.050 * rng.random()
        sens = Vector((0.0, 0.18, 1.0)).normalized()
        dent = A.tour(A.profil([(0.017, 0), (0.0115, 0.026), (0.0050, 0.056), (0, long)], 3), 8)
        a.piece("dent_bas%d" % k_, couche(dent, A.cadre(pb - sens * 0.010, sens, (0, 1, 0))), DENT, poil=False)
    # les grands crocs du haut : plantés dans la lèvre, longs, un peu courbés vers l'intérieur
    courbe_h = A.courbe([tuple(p_) for p_ in lèvre], 3)
    for k in range(4, len(courbe_h) - 4, 3):
        base = Vector(tuple(courbe_h[k]))
        long = 0.060 + 0.055 * rng.random()
        sens = Vector((0.0, 0.22, -1.0)).normalized()
        dent = A.tour(A.profil([(0.018, 0), (0.0120, 0.026), (0.0052, 0.058), (0, long)], 3), 8)
        a.piece("dent_haut%d" % k, couche(dent, A.cadre(base - sens * 0.010, sens, (0, 1, 0))), DENT, poil=False)

    # ----- la lanterne : une tige qui part du front, se penche devant le museau et finit par une boule jaune citron -----
    tige = A.tube(A.courbe([(0.0, -0.06, 0.470), (0.0, -0.18, 0.640), (0.0, -0.36, 0.680), (0.0, -0.46, 0.580)], 5),
                  lambda t_: 0.014 - 0.006 * t_, 12)
    tige.teinte = np.tile(AUBERGINE * 1.1, (len(tige.v), 1))
    a.piece("tige", tige, None, poil=False)
    a.piece("lanterne", A.boule(1.0, 28, 14).etire(0.056, 0.056, 0.062), CITRON, pos=(0.0, -0.46, 0.540), poil=False)
    for k in range(5):
        th = math.tau * k / 5.0 + 0.4
        d_ = Vector((math.cos(th) * 0.8, -0.35 + 0.2 * math.sin(th), 0.55 * math.sin(th) - 0.55))
        fil_ = A.tour(A.profil([(0.010, 0), (0.0065, 0.016), (0.0035, 0.032), (0, 0.044)], 3), 8)
        a.piece("filament_%d" % k, couche(fil_, A.cadre(Vector((0.0, -0.46, 0.540)) + d_.normalized() * 0.050, d_, (0, 0, 1))), CITRON, poil=False)

    # ----- la queue : le derrière de la poire se prolonge en un pédoncule, et la caudale en éventail -----
    ped = O.tube_r([(0.0, 0.22, 0.250), (0.0, 0.34, 0.252), (0.0, 0.46, 0.262), (0.0, 0.54, 0.270)], [0.115, 0.080, 0.050, 0.034], 20)
    ped.teinte = np.tile(AUBERGINE, (len(ped.v), 1))
    a.piece("queue", ped, None)
    caud = O.nageoire([(0.0, 0.0), (0.05, 0.05), (0.13, 0.11), (0.19, 0.08), (0.15, 0.025), (0.20, 0.0), (0.15, -0.025), (0.19, -0.08),
                       (0.13, -0.11), (0.05, -0.05)], 0.014, GRIS * 0.9, 0.005)
    a.piece("caudale", couche(caud, O.plan_vertical((0.0, 0.54, 0.270), (0.0, 1.0, 0.0))), None, poil=False)

    # ----- les yeux : tout petits, haut sur le côté, l'air pas content ; les nageoires moignons -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("corps", Vector((0.0, 0.0, 0.250)), Vector((c * 0.80, -0.62, 0.34)))      # sur les flancs de la tête, bien visibles
        a.oeil("oeil_" + nom, pos + n * 0.003, n, 0.0340)
        feuille = O.nageoire([(0.0, 0.0), (0.04, 0.030), (0.10, 0.044), (0.17, 0.030), (0.21, 0.0), (0.17, -0.030), (0.10, -0.040), (0.04, -0.028)],
                             0.012, GRIS, 0.004)
        ex = Vector((c * 0.25, 0.78, -0.50))
        ey = Vector((0.0, 0.50, 0.80))
        a.piece("pectorale_" + nom, couche(feuille, O.plan((c * 0.270, 0.020, 0.170), ex, ey)), None, poil=False)
    a.tete = Vector((0.0, -0.30, 0.240))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("baudroie_des_abysses", styles.style_de("baudroie_des_abysses"), sys.modules[__name__]),
              "Baudroie des abysses")
