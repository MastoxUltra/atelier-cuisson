"""Le chameau (de Bactriane) en peluche de velours ras : un brun chocolat clair tout laineux, DEUX bosses qui retombent un
peu, couronnées de mèches ; un cou bas en S barbu de longs poils, une tête lourde au front frisé et à la grosse lèvre,
des pattes épaisses en pantalon de laine, de larges pieds plats. L'endurant : debout, le cou tendu vers nous, la tête
un peu haute, mâchant lentement une pensée qu'il ne dira pas.

    python chameau.py        fabrique la fiche art/apercus/animaux/chameau.png (velours ras, palier 3)
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


LAINE = np.array(M.hexa("#c09c6c"))           # la dominante : brun chocolat clair laineux (le poil le fonce)
CLAIR = np.array(M.hexa("#dcc49a"))           # le ventre, le dedans des pattes, le museau
FONCE = np.array(M.hexa("#7e5c3c"))           # les mèches : bosses, barbe, front, pantalons
COUSSIN = M.hexa("#8a6a48")
NOIR = np.array(M.hexa("#3a2e28"))
PAS = 0.007


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def meche(longueur, largeur):
    """Une mèche : un fuseau pendant (axe Z, pointe vers le bas)."""
    return A.boule(1.0, 12, 6).etire(largeur, largeur * 0.8, longueur)


def construire():
    a = K.Animal("chameau")
    a.taille = 2.00

    # ----- le corps : un gros tonneau laineux, DEUX bosses qui s'affaissent, le ventre clair -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.450, 0.930), (0.280, 0.960), (0.040, 0.980), (-0.200, 0.990), (-0.400, 0.980))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.140), (0.14, 0.225), (0.42, 0.245), (0.72, 0.250), (0.90, 0.205), (0.97, 0.140), (1.0, 0.0)], L, 80)
    f = corps.v[:, 2] / L
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    haut = np.clip(corps.v[:, 1] / 0.22, 0.0, 1.0)
    for centre, h in ((0.36, 0.200), (0.64, 0.185)):
        g = np.exp(-((f - centre) / 0.085) ** 2) * haut
        corps.v[:, 1] += h * g
        corps.v[:, 0] *= 1 - 0.16 * g
    corps.teinte = np.where((th > 2.2)[:, None], CLAIR, np.where((corps.v[:, 1] > 0.26)[:, None], FONCE, LAINE))
    a.piece("corps", corps.sculpte(fil.couche), None)
    mech = None
    for centre, h in ((0.36, 0.200), (0.64, 0.185)):                                # les mèches au sommet des bosses
        c_, av, nq = fil.cadre(centre * L)
        for dy, dx, hh in ((0.0, 0.0, 0.080), (0.045, 0.020, 0.062), (-0.045, -0.020, 0.062), (0.0, 0.040, 0.050)):
            m = meche(hh, 0.030).pose(tuple(np.array(c_) + np.array(nq) * (0.235 + h * 0.94) + np.array([dx, dy, 0.0])))
            mech = m if mech is None else mech + m
    a.piece("meches_bosses", mech, tuple(FONCE))

    # ----- le cou : bas et large, en S, d'une seule pièce ; la barbe de longs poils dessous -----
    BASE = Vector((0.0, -0.400, 1.010))
    arc = ((0.0, 0.0), (0.080, 0.100), (0.170, 0.240), (0.200, 0.380), (0.150, 0.500), (0.040, 0.580))
    enc = K.Fil([tuple(BASE + Vector((0, -u, z))) for u, z in arc], (1, 0, 0))
    Lc = enc.long
    rr = [(0.0, 0.165), (0.12, 0.140), (0.40, 0.108), (0.80, 0.088), (1.0, 0.084)]
    cou = fuseau(rr, Lc, 56)
    cou.teinte = np.where((cou.v[:, 1] > 0.020)[:, None], FONCE, LAINE)
    a.piece("cou", cou.sculpte(enc.couche), None)
    barbe = None
    for fr in np.linspace(0.08, 0.96, 9):
        c_, av, nq = enc.cadre(fr * Lc)
        r = float(np.interp(fr, [p[0] for p in rr], [p[1] for p in rr]))
        m = meche(0.095, 0.034).pose(tuple(np.array(c_) - np.array(nq) * (r * 0.92) + np.array([0.0, 0.0, -0.040])))
        barbe = m if barbe is None else barbe + m
    a.piece("barbe", barbe, tuple(FONCE))
    centre, avant, nuque = enc.cadre(Lc)
    bout = Vector(centre)

    # ----- la tête : lourde, le museau large, la grosse lèvre ; le front frisé ; tournée vers nous -----
    T = A.cadre(bout + Vector((0.0, -0.030, 0.020)), Vector((0.36, -1.0, -0.12)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.066), (0.22, 0.092), (0.46, 0.078), (0.72, 0.068), (0.90, 0.070), (0.97, 0.052), (1.0, 0.0)], 0.330, 52, 0.005)
    tete.teinte = np.where((tete.v[:, 2] > 0.20)[:, None], tuple(CLAIR), tuple(LAINE))
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.080)))
    a.tete = T @ Vector((0, 0.0, 0.180))
    a.piece("levre", A.boule(1.0, 24, 12).etire(0.050, 0.026, 0.062), tuple(CLAIR), mat=T @ A.repere((0.0, -0.074, 0.190), (10, 0, 0)))
    a.piece("frisette", A.boule(1.0, 24, 12).etire(0.060, 0.044, 0.050), tuple(FONCE), mat=T @ A.repere((0.0, 0.074, -0.010), (-14, 0, 0)))
    for nom, c in (("G", 1), ("D", -1)):
        pn, nn = a.surface("tete", T @ Vector((0, 0.0, 0.200)), T3 @ Vector((c * 0.45, 0.89, 0.0)))
        a.piece("narine_" + nom, A.boule(1.0, 14, 8).etire(0.006, 0.014, 0.012), tuple(NOIR), mat=A.cadre(pn + nn * 0.002, nn, T3 @ Vector((0, 0, 1))), poil=False)
        regard = T3 @ Vector((c * 0.84, 0.34, 0.06))
        p, n = a.surface("tete", T @ Vector((0, 0.0, 0.030)), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0180)
        a.piece("cils_" + nom, K.paupiere(0.0230, 0.20), tuple(FONCE), mat=A.cadre(p + n * 0.005, n, T3 @ Vector((0, 1, 0))), poil=False)
        po = A.profil([(0, 0), (0.026, 0.008), (0.032, 0.032), (0.024, 0.056), (0.009, 0.074), (0, 0.082)], 5)
        a.piece("oreille_" + nom, A.tour(po, 20).etire(1.0, 0.45, 1.0), tuple(FONCE),
                mat=A.cadre(T @ Vector((c * 0.052, 0.058, -0.030)), T3 @ Vector((c * 0.50, 0.64, -0.30)), T3 @ Vector((c * 0.3, 0.0, 1.0))))

    # ----- les pattes : épaisses, le genou net, le pantalon de laine, le large pied plat ; l'antérieur gauche avancé -----
    def jambe(pts, r0):
        ft = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.26, r0 * 0.74), (0.44, r0 * 0.54), (0.50, r0 * 0.68), (0.58, r0 * 0.52), (0.80, r0 * 0.58), (0.94, r0 * 0.50), (1.0, 0.0)],
                   ft.long, 32, 0.007)
        zz = m.v[:, 2] / ft.long
        m.teinte = np.where(((zz > 0.60) & (zz < 0.86))[:, None], tuple(FONCE), tuple(LAINE))
        return m.sculpte(ft.couche)
    for nom, pts, r0 in (("av_D", [(-0.150, -0.330, 0.900), (-0.155, -0.335, 0.600), (-0.155, -0.325, 0.320), (-0.155, -0.335, 0.030)], 0.105),
                         ("ar_G", [(0.155, 0.360, 0.880), (0.165, 0.310, 0.600), (0.165, 0.380, 0.330), (0.165, 0.370, 0.030)], 0.115),
                         ("ar_D", [(-0.155, 0.360, 0.880), (-0.165, 0.310, 0.600), (-0.165, 0.380, 0.330), (-0.165, 0.370, 0.030)], 0.115),
                         ("av_G", [(0.150, -0.330, 0.900), (0.155, -0.370, 0.620), (0.155, -0.440, 0.350), (0.155, -0.450, 0.030)], 0.105)):
        a.piece("jambe_" + nom, jambe(pts, r0), None)
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.066, 0.092, 0.028), COUSSIN, pos=(pts[-1][0], pts[-1][1] - 0.020, 0.028), poil=False)
    a.piece("queue", A.tube(A.courbe(propres([(0.0, 0.520, 0.940), (0.0, 0.580, 0.840), (0.0, 0.590, 0.690)]), 5), lambda t: 0.026 - 0.008 * t, 12), tuple(LAINE))
    a.piece("meche_queue", A.boule(1.0, 20, 10).etire(0.034, 0.034, 0.075), tuple(FONCE), pos=(0.0, 0.592, 0.640))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("chameau", styles.style_de("chameau"), sys.modules[__name__]), "Chameau")
