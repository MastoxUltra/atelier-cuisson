"""L'autruche en peluche de velours ras : un noir velouté (un noir d'encre qui tire sur le brun), un gros corps ovoïde
aux ailes blanches en grands éventails de plumes bouclées, une queue blanche en panache, un long cou rosé presque nu
terminé par une toute petite tête au grand œil à longs cils et au bec plat, et deux jambes énormes d'un rose sale aux
cuisses nues et à deux orteils. La dame distraite : lancée en pleine foulée, un pied levé, le cou tendu en avant et
légèrement ondulé, les ailes à demi déployées pour garder l'équilibre.

    python autruche.py        fabrique la fiche art/apercus/animaux/autruche.png (velours ras, palier 3)
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


def propres(points, eps=2e-4):
    """Les points d'un tracé sans doublons consécutifs (deux points identiques à la suite déforment un tube en NaN)."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie


NOIR = np.array(M.hexa("#4a4448"))            # la dominante : noir velouté (le poil la fonce : on la prend plus claire)
BLANC = np.array(M.hexa("#fffaf0"))           # l'accent : les ailes, la queue
PEAU = np.array(M.hexa("#e8aaa0"))            # le cou, les cuisses : rose sale
BEC = M.hexa("#e8c8a8")
CHARBON = M.hexa("#2e2828")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def eventail(pos, rot, large, long, etages=6, couleur=BLANC, pointe=None):
    """Un éventail de plumes : « etages » gros pétales aplatis, en arc, qui partent du même point ; une seule pièce."""
    m = None
    for k in range(etages):
        u = (k / (etages - 1)) - 0.5
        long_k = long * (0.80 + 0.20 * math.cos(u * 2.4))
        pl = A.boule(1.0, 16, 8).etire(large, 0.026, long_k * 0.5)
        pl = pl.pose((0, 0, long_k * 0.5)).pose((0, 0, 0), (0, math.degrees(u) * 70, 0))
        m = pl if m is None else m + pl
    return m


def construire():
    a = K.Animal("autruche")
    a.taille = 2.40

    # ----- le corps : un gros œuf couché, la poitrine haute, la croupe qui monte ; noir velouté -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.500, 0.960), (0.300, 1.020), (0.020, 1.030), (-0.250, 1.050), (-0.380, 1.080))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.170), (0.15, 0.260), (0.45, 0.300), (0.75, 0.275), (0.92, 0.205), (1.0, 0.0)], L, 64, 0.010)
    corps.teinte = np.tile(NOIR, (len(corps.v), 1))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou : long, rosé, presque nu, tendu en avant et légèrement ondulé ; la tête minuscule, le bec plat, le grand œil -----
    BASE = Vector((0.0, -0.330, 1.110))
    pts = ((0.0, 0.0), (0.050, 0.130), (0.120, 0.300), (0.100, 0.500), (0.170, 0.680), (0.300, 0.780))      # (avance, monte)
    enc = K.Fil([tuple(BASE + Vector((0, -u, z))) for u, z in pts], (1, 0, 0))
    Lc = enc.long
    cou = fuseau([(0.0, 0.130), (0.10, 0.085), (0.40, 0.050), (0.80, 0.042), (1.0, 0.046)], Lc, 40, 0.008)
    cou.teinte = np.tile(PEAU, (len(cou.v), 1))
    a.piece("cou", cou.sculpte(enc.couche), None)
    centre, avant, nuque = enc.cadre(Lc)
    H = A.cadre(Vector(centre) + Vector((0.0, -0.020, 0.0)), Vector((0.20, -1.0, -0.10)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.052, 0.062, 0.050), tuple(PEAU), mat=H)
    bec = A.boule(1.0, 28, 14).etire(0.046, 0.074, 0.020)
    a.piece("bec", bec, BEC, mat=H @ A.repere((0, -0.080, -0.006)), poil=False)
    a.tete = H @ Vector((0, -0.100, 0.0))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.92, -0.20, 0.36))
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0200)
        a.piece("cils_" + nom, K.paupiere(0.0250, 0.30), CHARBON, mat=A.cadre(p + n * 0.006, n, H3 @ Vector((0, 0, 1))), poil=False)

    # ----- les ailes : de grands éventails de plumes blanches qui se déploient de chaque côté du corps ; la queue : un panache -----
    for nom, c, rot in (("G", 1, (0, 0, 52)), ("D", -1, (0, 0, -30))):
        ev = eventail((0, 0, 0), (0, 0, 0), 0.085, 0.52, 7)
        a.piece("aile_" + nom, ev, tuple(BLANC), mat=A.cadre(Vector((c * 0.240, 0.040, 1.120)), Vector((c * 0.55, 0.78, -0.30)), Vector((c * 0.2, 0, 1))), poil=False)
    queue = eventail((0, 0, 0), (0, 0, 0), 0.075, 0.46, 7)
    a.piece("queue", queue, tuple(BLANC), mat=A.cadre(Vector((0.0, 0.440, 1.090)), Vector((0.0, 0.85, 0.35)), Vector((1, 0, 0))), poil=False)

    # ----- les jambes : énormes, rosées, la cuisse nue ; une jambe plantée, l'autre levée en pleine foulée ; deux orteils -----
    def jambe(pts, r0):
        f = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.30, r0 * 0.70), (0.52, r0 * 0.56), (0.62, r0 * 0.66), (0.95, r0 * 0.50), (1.0, 0.0)], f.long, 32, 0.012)
        m.teinte = np.tile(PEAU, (len(m.v), 1))
        return m.sculpte(f.couche)
    plan_g = [(0.140, 0.100, 0.960), (0.150, 0.130, 0.680), (0.150, 0.090, 0.360), (0.150, 0.020, 0.040)]
    plan_d = [(-0.140, 0.100, 0.960), (-0.150, -0.040, 0.720), (-0.150, -0.240, 0.620), (-0.150, -0.330, 0.400)]
    for nom, pts in (("G", plan_g), ("D", plan_d)):
        a.piece("jambe_" + nom, jambe(pts, 0.105), None)
    for ang, dx in ((-14, -0.034), (10, 0.034)):
        a.piece("orteil_G%d" % ang, A.boule(1.0, 14, 8).etire(0.032, 0.090, 0.022), BEC, pos=(0.150 + dx, -0.040, 0.020), rot=(0, 0, ang), poil=False)
        a.piece("orteil_D%d" % ang, A.boule(1.0, 14, 8).etire(0.032, 0.090, 0.022), BEC, pos=(-0.150 + dx, -0.420, 0.360), rot=(-20, 0, ang), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("autruche", styles.style_de("autruche"), sys.modules[__name__]), "Autruche")
