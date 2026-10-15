"""Le zèbre en peluche de velours ras (3e dessin) : un blanc franc zébré de rayures charbon nettes qui suivent le corps
(elles partent de l'échine, descendent en s'infléchissant vers l'arrière et s'effilent en pointe sous le ventre ; sur
la croupe elles tournent en arcs ; sur le cou elles sont obliques ; sur le museau elles sont fines et serrées), une
longue tête de cheval, le museau gris sombre, de petits yeux, une crinière en brosse droite noire et blanche, des
jambes à bracelets, la queue à houppe noire. Tête haute, il renâcle : le cou arqué, les naseaux dilatés, une jambe
avant levée qui racle le sol, la queue qui fouette.

    python zebre.py        fabrique la fiche art/apercus/animaux/zebre.png (velours ras, palier 3)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K

BLANC = np.array(M.hexa("#fffdf6"))           # la dominante : blanc franc
CHARBON = np.array(M.hexa("#26222a"))         # l'accent : les rayures
GRIS = np.array(M.hexa("#6a6064"))            # le museau
SABOT = M.hexa("#3a3436")
PAS = 0.007                                   # l'écart entre deux anneaux : assez fin pour que les rayures soient nettes


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    """Une pièce tournée très finement échantillonnée : points = [(fraction de la longueur, rayon), ...]."""
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def rayer(m, phase, seuil, ventre=0.80):
    """Peint une pièce tournée droite : blanc, et charbon là où frac(phase(z, u)) est sous seuil(z, u) ; u = l'écart au
    dos (0 sur l'échine, 1 sous le ventre). Les rayures s'effilent : le seuil baisse vers le ventre."""
    x, y, z = m.v[:, 0], m.v[:, 1], m.v[:, 2]
    u = np.abs(np.arctan2(x, y)) / math.pi
    f = phase(z, u) % 1.0
    noir = f < np.maximum(seuil(z, u), 0.0)
    t = np.tile(BLANC, (len(z), 1))
    t[noir & (u < ventre)] = CHARBON
    m.teinte = t
    return m


def construire():
    a = K.Animal("zebre")
    a.taille = 2.40

    # ----- le corps : un tonneau élancé couché le long d'un fil (la croupe ronde, le garrot haut) ; rayures qui partent de
    #       l'échine, s'infléchissent vers l'arrière et s'effilent sous le ventre ; sur la croupe elles tournent en arcs -----
    chemin = [(0.0, y, z) for y, z in ((0.560, 0.640), (0.440, 0.690), (0.200, 0.700), (-0.050, 0.700), (-0.290, 0.720), (-0.450, 0.720))]
    fil = K.Fil(chemin, (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.03, 0.12), (0.12, 0.205), (0.30, 0.225), (0.55, 0.225), (0.80, 0.238), (0.94, 0.190), (1.0, 0.0)], L)

    def phase(z, u):
        sw = 0.075 * u ** 1.6 + 0.020 * np.exp(-((z - 0.20 * L) / 0.15) ** 2) * u        # vers l'arrière en descendant ; arcs sur la croupe
        return (z + sw) / 0.115

    def seuil(z, u):
        large = 0.50 + 0.08 * np.sin(z * 17.0)                                              # des rayures de largeur variable
        return large * (1.0 - 0.80 * u ** 1.4)
    rayer(corps, phase, seuil)
    a.piece("corps", corps.sculpte(lambda v: v * [1.04, 1.0, 1.0]).sculpte(fil.couche), None)

    # ----- le cou : arqué, haut ; les rayures y sont obliques ; la crinière en brosse droite, noire et blanche -----
    BASE = Vector((0.0, -0.310, 0.750))
    enc = K.Fil([tuple(BASE + Vector((0, -u, z))) for u, z in ((0.0, 0.0), (0.030, 0.140), (0.080, 0.290), (0.140, 0.400), (0.200, 0.470))], (1, 0, 0))
    Lc = enc.long
    cou = fuseau([(0.0, 0.10), (0.10, 0.150), (0.25, 0.138), (0.5, 0.108), (0.8, 0.088), (1.0, 0.078)], Lc, 56)
    rayer(cou, lambda z, u: (z + 0.060 * u) / 0.085, lambda z, u: 0.52 * (1.0 - 0.55 * u ** 1.5), ventre=0.86)
    a.piece("cou", cou.sculpte(lambda v: v * [0.82, 1.0, 1.0]).sculpte(enc.couche), None)
    for i, f in enumerate(np.linspace(0.05, 0.97, 18)):
        c_, av, nq = enc.cadre(f * Lc)
        r = float(np.interp(f, [0.0, 0.10, 0.25, 0.5, 0.8, 1.0], [0.10, 0.150, 0.138, 0.108, 0.088, 0.078]))
        pied = c_ + nq * r * 0.96
        brin = A.boule(1.0, 12, 6).etire(0.012, 0.022, 0.078).pose(tuple(pied + nq * 0.050))
        a.piece("crin_%02d" % i, brin, tuple(CHARBON if i % 2 == 0 else BLANC), poil=False)

    # ----- la tête : longue, de cheval, tenue haute, le museau gris ; les rayures fines et serrées ; petits yeux -----
    centre, avant, nuque = enc.cadre(Lc)
    l, p = math.radians(30.0), math.radians(-42.0)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), math.sin(p)))
    T = A.cadre(Vector(centre) + Vector((0, 0.030, 0.040)), nez, Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.05, 0.070), (0.20, 0.090), (0.45, 0.074), (0.68, 0.062), (0.84, 0.066), (0.96, 0.056), (1.0, 0.0)], 0.360, 48)
    rayer(tete, lambda z, u: (z + 0.030 * u) / 0.050, lambda z, u: 0.50 * (1.0 - 0.5 * u), ventre=0.84)
    tete.teinte[tete.v[:, 2] > 0.280] = GRIS
    a.piece("tete", tete.sculpte(lambda v: v * [0.86, 1.0, 1.0]), None, mat=T @ A.repere((0, 0.060, -0.050), (0, 0, 0)))
    a.tete = T @ Vector((0, 0.060, 0.200))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", T @ Vector((0, 0.050, 0.110)), T3 @ Vector((c * 0.80, 0.40, 0.00)))
        a.rustine("cerne_" + nom, "tete", T @ Vector((0, 0.050, 0.110)), T3 @ Vector((c * 0.80, 0.40, 0.00)), 0.30, tuple(CHARBON), 0.003, 0)
        a.oeil("oeil_" + nom, pos + n * 0.004, n, 0.0140)
        po = A.profil([(0, 0), (0.026, 0.012), (0.036, 0.050), (0.028, 0.092), (0.010, 0.120), (0, 0.130)], 6)
        vers = Vector((c * 0.22, 0.22, 0.95)).normalized()
        E = A.cadre(T @ Vector((c * 0.052, 0.098, -0.026)) - vers * 0.012, vers, Vector((c * 0.5, -0.9, 0.0)))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 28).etire(1.0, 0.45, 1.0), [(0.060, tuple(CHARBON)), (9, tuple(BLANC))]), None, mat=E)
    for nom, c in (("G", 1), ("D", -1)):                  # les naseaux dilatés : deux ovales sombres cousues sur le bout du museau
        a.rustine("naseau_" + nom, "tete", T @ Vector((0, 0.060, 0.200)), T3 @ Vector((c * 0.34, 0.10, 0.94)), 0.17, tuple(CHARBON), 0.0025, 0)
    a.piece("toupet", A.boule(1.0, 12, 6).etire(0.010, 0.016, 0.040), tuple(CHARBON), mat=T @ A.repere((0, 0.138, 0.068), (-20, 0, 0)), poil=False)

    # ----- les jambes : fines, en bracelets noirs et blancs, le genou et le boulet marqués, les sabots noirs ;
    #       l'antérieur gauche levé : il racle le sol -----
    def jambe(points, r0):
        ch = A.courbe(points, 8)
        fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(ch, axis=0), axis=1))])
        n = max(int(fait[-1] / 0.040), 2)
        bandes = [((k + 1) / n, tuple(CHARBON) if k % 2 else tuple(BLANC)) for k in range(n)]
        return K.tube_peint(ch, lambda t: r0 * (1 - 0.40 * t) + 0.012 * math.exp(-((t - 0.50) / 0.08) ** 2) + 0.010 * math.exp(-((t - 0.88) / 0.05) ** 2),
                            bandes, 18)
    plantees = (("av_D", [(-0.110, -0.320, 0.640), (-0.118, -0.330, 0.480), (-0.118, -0.322, 0.300), (-0.116, -0.330, 0.050)], 0.062),
                ("ar_G", [(0.120, 0.420, 0.620), (0.135, 0.380, 0.470), (0.132, 0.440, 0.300), (0.130, 0.420, 0.050)], 0.074),
                ("ar_D", [(-0.120, 0.420, 0.620), (-0.135, 0.380, 0.470), (-0.132, 0.440, 0.300), (-0.130, 0.420, 0.050)], 0.074))
    for nom, pts, r0 in plantees:
        a.piece("patte_" + nom, jambe(pts, r0), None)
        a.piece("sabot_" + nom, A.boule(1.0, 24, 12).etire(0.048, 0.060, 0.034), SABOT, pos=(pts[-1][0], pts[-1][1] - 0.010, 0.032), poil=False)
    levee = [(0.110, -0.320, 0.640), (0.118, -0.350, 0.500), (0.120, -0.450, 0.440), (0.120, -0.500, 0.300)]
    a.piece("patte_av_G", jambe(levee, 0.062), None)
    a.piece("sabot_av_G", A.boule(1.0, 24, 12).etire(0.048, 0.060, 0.034), SABOT, pos=(0.120, -0.520, 0.270), rot=(-48, 0, 0), poil=False)

    # ----- la queue : un fouet fin, rayé, à houppe noire, qui balaie un côté -----
    chemin = [(0.0, 0.540, 0.640), (0.070, 0.620, 0.520), (0.120, 0.640, 0.360)]
    a.piece("queue", A.tube(A.courbe(chemin, 5), 0.016, 12), tuple(BLANC))
    a.piece("houppe", A.boule(1.0, 24, 12).etire(0.032, 0.040, 0.100), tuple(CHARBON), pos=(0.130, 0.640, 0.270), rot=(0, -10, 0))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("zebre", styles.style_de("zebre"), sys.modules[__name__]), "Zèbre")
