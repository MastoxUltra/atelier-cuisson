"""Le lama en peluche : le snob des crêtes. Planté haut sur ses pattes fines, il tire son long cou en arrière et
lève le nez pour nous regarder de haut, la paupière à demi baissée, la lèvre fendue en moue : on ne sait pas s'il va
nous ignorer ou nous cracher dessus. Une toison bouclée vieux rose, le cou et le poitrail crème, deux grandes
oreilles en banane qui se regardent, au bout chocolat ; les pieds chocolat, et un toupet de queue dressé.

    python lama.py        fabrique la fiche art/apercus/animaux/lama.png (style du palier : C, velours ras)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import matieres as M
import peluche as K
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

ROSE = M.hexa("#cc8e8b")                      # la dominante (registre du 14/10 : vieux rose #d9a3a0) ; un cran plus
                                              # soutenue, le velours ras éclaircit
CREME = K.CREME                               # la toison du cou et du poitrail
CHOCO = M.hexa("#4a2e28")                     # l'accent : le bout des oreilles, les pieds

CROUPE = Vector((0.0, 0.270, 0.600))
CABRE = 4.0
LONG = 0.62
COL = math.radians(8)
AVANT = Vector((math.sin(COL), -math.cos(COL), 0.0))
FLANC = np.array([math.cos(COL), math.sin(COL), 0.0])
BASE = Vector((0.0, -0.215, 0.655))           # le pied du cou, enfoui dans le poitrail
ARC = [(0.0, 0.0), (0.030, 0.110), (0.040, 0.220), (0.026, 0.320), (0.000, 0.388), (-0.020, 0.420)]   # haut, tiré en arrière
LACET, PIQUE, PENCHE = 52.0, -6.0, -6.0        # la tête : tournée vers nous, le nez droit (en l'air, le gros plan ne montrait que le dessous du museau)
GROSSE = 1.25                                 # une tête plus petite au bout du long cou (référence)


def gauss(x):
    return np.exp(-x * x)


def boucles(v, fort=0.03):
    """Pour une pièce tournée (avant de la coucher) : la toison bouclée, des bosses qui courent autour et le long."""
    a = np.arctan2(v[:, 1], v[:, 0])
    z = v[:, 2]
    f = np.sin(7 * a + 2 * np.sin(18 * z)) * np.sin(40 * z + 2 * a)
    s = v.copy()
    s[:, 0:2] *= (1 + fort * f)[:, None]
    return s


def membre(points, rayons, paliers):
    return K.tube_peint(A.courbe(points, 6), lambda t: float(np.interp(t, np.linspace(0, 1, len(rayons)), rayons)), paliers, 20)


def pied():
    """Un pied de lama : une semelle ronde et deux ongles devant."""
    def doigt(cote):
        def f(v):
            s = v.copy()
            s[:, 1] -= 0.010 * K.lisse((0.026 - v[:, 2]) / 0.026)
            return s
        m = A.tour(A.profil([(0, 0), (0.0150, 0.002), (0.0160, 0.012), (0.0125, 0.026), (0, 0.031)], 4), 24)
        return m.etire(0.86, 1.30, 1.0).sculpte(f).pose((cote * 0.0140, -0.006, 0.0))
    return doigt(1) + doigt(-1)


def construire():
    a = K.Animal("lama")
    a.taille = 1.70

    # ----- le corps : un tonneau bouclé, couché vers l'avant ; X la gauche, Y le dos, Z l'avant ; le poitrail crème -----
    pc = A.profil([(0, 0), (0.090, 0.012), (0.134, 0.060), (0.148, 0.140), (0.146, 0.300), (0.150, 0.440),
                   (0.140, 0.540), (0.102, 0.600), (0, LONG)], 6)      # moins tonneau, plus allongé (vues de la référence, 16/10)
    corps = A.tour(pc, 48)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(np.asarray(ROSE), (len(ang), 1))
    t[(corps.v[:, 2] > 0.50) & (ang > 1.30)] = CREME                  # le poitrail
    corps.teinte = t

    def galbe(v):
        s = boucles(v, 0.045)
        z = v[:, 2]
        dessous = v[:, 1] < 0
        s[dessous, 1] *= (1 - 0.10 * gauss((z - 0.28) / 0.14))[dessous]
        return s
    a.piece("corps", corps.sculpte(galbe), None, pos=CROUPE, rot=(90 - CABRE, 0, 0))

    # ----- le cou : très long, crème et bouclé, tiré en arrière en haut -----
    enc = K.Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in ARC], FLANC)
    L = enc.long
    parts, rayons = [0.03, 0.18, 0.40, 0.65, 0.85, 0.985], [0.135, 0.118, 0.104, 0.096, 0.092, 0.086]
    cou = A.tour(A.profil([(0, 0)] + [(r, p * L) for r, p in zip(rayons, parts)] + [(0, 1.01 * L)], 6), 40)
    a.piece("cou", cou.sculpte(lambda v: boucles(v, 0.045)).etire(0.90, 1.0, 1.0).sculpte(enc.couche), CREME)

    # ----- la tête : un museau court et carré, le front bombé ; X la gauche, Y le chanfrein, Z vers le nez -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0, 0, 0), nez) @ Matrix.Rotation(math.radians(PENCHE), 4, Vector((0, 0, 1))) @ A.repere(ech=(GROSSE,) * 3)
    bout = Vector(enc.cadre(L)[0])
    T = A.repere(bout - T.to_3x3() @ Vector((0, -0.024, 0.040))) @ T
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.020, 0.110))

    def tete_(v):
        s = v.copy()
        z, haut = v[:, 2], v[:, 1] > 0
        s[:, 0] *= 0.90 + 0.06 * gauss((z - 0.050) / 0.040)
        s[:, 1] *= np.where(haut, 1 + 0.12 * gauss((z - 0.040) / 0.035), 1 + 0.10 * gauss((z - 0.150) / 0.030))   # le front, la lèvre
        return s
    tete = A.tour(A.profil([(0, 0), (0.044, 0.008), (0.060, 0.034), (0.060, 0.074), (0.050, 0.112), (0.045, 0.145),
                            (0.043, 0.178), (0.040, 0.204), (0.030, 0.222), (0, 0.230)], 6), 56)
    a.piece("tete", tete.sculpte(tete_), ROSE, mat=T)
    a.piece("toupet", A.boule(1.0, 32, 16).sculpte(lambda v: boucles(v * [1, 1, 1], 0.10)).etire(0.046, 0.034, 0.040), CREME,
            mat=T @ A.repere((0, 0.052, 0.040)))
    # les lèvres : un vrai museau de lama — la lèvre du haut fendue en deux lobes, celle du bas plus avancée, les narines au-dessus
    LEVRE = np.array(ROSE) * 0.92 + np.array(CHOCO) * 0.08
    for nom, c in (("G", 1), ("D", -1)):
        lobe = A.boule(1.0, 20, 10).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.0165, 0.0150, 0.021)
        a.piece("levre_" + nom, O.teinte(lobe, LEVRE), None, mat=T @ A.repere((c * 0.0185, -0.010, 0.214)), poil=False)
    bas_ = A.boule(1.0, 20, 10).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.026, 0.013, 0.025)
    a.piece("levre_bas", O.teinte(bas_, LEVRE * 0.92), None, mat=T @ A.repere((0.0, -0.036, 0.196)), poil=False)
    centre = T @ Vector((0, 0, 0.160))
    for nom, c in (("G", 1), ("D", -1)):
        narine = [a.trace("tete", centre, [T3 @ Vector((c * (0.30 + 0.10 * u), 0.55 - 0.20 * u, 0.80))])[0] for u in (0.0, 0.5, 1.0)]
        a.broderie("narine_" + nom, A.courbe(narine, 3), 0.0022, CHOCO)

    # ----- les yeux : grands, vivants, sous une paupière lourde à demi baissée : il nous regarde de haut -----
    centre = T @ Vector((0, 0, 0.070))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.64, 0.42, 0.42)))     # plus en avant : les deux yeux de face
        a.oeil("oeil_" + nom, pos + n * 0.003, n, 0.020)
        haut = (T3 @ Vector((0, 1, 0)) - n * n.dot(T3 @ Vector((0, 1, 0)))).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.020, 0.60), ROSE, mat=A.cadre(pos + n * 0.003, n, haut), poil=False)

    # ----- les oreilles en banane : longues, dressées, les pointes qui se courbent l'une vers l'autre, le bout chocolat -----
    po = A.profil([(0, 0), (0.024, 0.010), (0.032, 0.040), (0.030, 0.085), (0.020, 0.120), (0.008, 0.140), (0, 0.146)], 6)
    for nom, c in (("G", 1), ("D", -1)):
        def banane(v, c=c):
            s = v.copy()
            s[:, 0] -= c * 2.0 * np.clip(v[:, 2] - 0.03, 0, None) ** 2
            return s
        oreille = K.bandes(A.tour(po, 32).etire(1.0, 0.55, 1.45), [(0.150, ROSE), (9, CHOCO)])     # longues bananes (référence)
        vers = (T3 @ Vector((c * 0.42, 0.88, -0.24))).normalized()
        E = A.cadre(T @ Vector((c * 0.040, 0.044, 0.034)) - vers * 0.012, vers, T3 @ Vector((c * 0.25, 0.10, 0.96)))
        a.piece("oreille_" + nom, oreille.sculpte(banane), None, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 24).etire(0.55, 0.40, 1.05).pose((0, 0.009, 0.012)).sculpte(banane), CREME, mat=E,
                poil=False)

    # ----- la queue : un toupet bouclé, dressé -----
    queue = A.tube(A.courbe([(0, 0.262, 0.660), (0, 0.312, 0.690), (0, 0.346, 0.682)], 6), lambda t: 0.040 - 0.012 * t, 16)
    a.piece("queue", queue, ROSE)

    # ----- les pattes : longues et fines, la culotte bouclée en haut ; l'antérieur gauche un pas en avant -----
    pattes = (("avant_G", [(0.078, -0.200, 0.560), (0.088, -0.236, 0.400), (0.084, -0.258, 0.220), (0.082, -0.266, 0.080), (0.082, -0.268, 0.034)]),
              ("avant_D", [(-0.078, -0.190, 0.560), (-0.088, -0.180, 0.400), (-0.086, -0.176, 0.220), (-0.084, -0.172, 0.080), (-0.084, -0.170, 0.034)]),
              ("arriere_G", [(0.084, 0.220, 0.580), (0.100, 0.180, 0.410), (0.096, 0.236, 0.240), (0.092, 0.218, 0.080), (0.092, 0.212, 0.034)]),
              ("arriere_D", [(-0.084, 0.220, 0.580), (-0.100, 0.190, 0.410), (-0.096, 0.246, 0.240), (-0.092, 0.230, 0.080), (-0.092, 0.224, 0.034)]))
    for nom, points in pattes:
        a.piece("patte_" + nom, membre(points, [0.086, 0.066, 0.034, 0.029, 0.029], [(1, ROSE)]), None)
        a.piece("pied_" + nom, pied(), CHOCO, pos=(points[-1][0], points[-1][1], 0.0), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lama", styles.style_de("lama"), sys.modules[__name__]), "Lama")
