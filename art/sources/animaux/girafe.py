"""La girafe en peluche de magasin (2e dessin) : un jaune miel couvert de vraies plaques châtain à bords nets, cousues en
pavés polygonaux sur le fond clair (le corps, le cou et le haut des jambes) ; un long cou en courbe douce, la croupe
plus basse que le garrot, les genoux noueux, de longs cils, de petits yeux, deux ossicônes à houppette sombre, des
oreilles en feuille, une crinière en brosse brune, une queue à pinceau noir. Une dame qui n'a pas de hâte : le cou
infléchi en S, la tête penchée vers nous d'en haut, un œil par-dessus l'épaule, les antérieurs un peu écartés.

    python girafe.py        fabrique la fiche art/apercus/animaux/girafe.png (peluche de magasin, palier 4)
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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
MIEL = np.array(M.hexa("#ffd070"))            # la dominante : jaune miel
CHATAIGNE = np.array(M.hexa("#b86a30"))       # l'accent : les plaques
CREME = np.array(M.hexa("#fff2d6"))           # le museau, le ventre, le bas des jambes
BRUN = M.hexa("#5a3a28")                      # la crinière, les houppes, le pinceau
CORNE = M.hexa("#3a2e2c")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=80, pas=PAS):
    """Une pièce tournée très finement échantillonnée : points = [(fraction de la longueur, rayon), ...]."""
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def paver(m, graine, taille, joint=0.020, clair=None):
    """Peint une pièce encore droite en pavés châtain à joints miel (un pavage de Voronoï : le plus proche de quelques
    graines tirées dans la boîte de la pièce ; le joint, là où deux graines sont presque à égale distance). clair(v) vrai :
    la crème des bas de jambes et du ventre, sans plaques."""
    rng = np.random.default_rng(graine)
    v = m.v
    lo, hi = v.min(axis=0), v.max(axis=0)
    n = int(np.clip(np.prod(np.maximum((hi - lo) / taille, 1.0)) * 1.6, 8, 160))
    graines = lo + rng.random((n, 3)) * (hi - lo)
    d = np.sort(np.linalg.norm(v[:, None, :] - graines[None, :, :], axis=2), axis=1)[:, :2]
    t = np.tile(CHATAIGNE, (len(v), 1))
    t[(d[:, 1] - d[:, 0]) < joint] = MIEL
    if clair is not None:
        t[clair(v)] = CREME
    m.teinte = t
    return m


def construire():
    a = K.Animal("girafe")
    a.taille = 5.00

    # ----- le corps : un tonneau élancé en pente (le garrot haut, la croupe basse), couché le long d'un fil -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.480, 1.000), (0.320, 1.040), (0.080, 1.090), (-0.140, 1.150), (-0.300, 1.190), (-0.380, 1.200))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.130), (0.15, 0.212), (0.40, 0.245), (0.70, 0.255), (0.90, 0.228), (1.0, 0.0)], L)
    paver(corps, 3, 0.22, 0.020, clair=lambda v: (np.abs(np.arctan2(v[:, 0], v[:, 1])) > 2.7))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou : long, en courbe douce, d'une seule pièce ; des pavés plus petits ; la crinière en brosse -----
    BASE = Vector((0.0, -0.250, 1.160))
    pts = ((0.0, 0.0), (-0.050, 0.280), (-0.090, 0.560), (-0.040, 0.860), (0.090, 1.120), (0.210, 1.280))      # (recul, monte) : S doux
    enc = K.Fil([tuple(BASE + Vector((0, -u, z))) for u, z in pts], (1, 0, 0))
    Lc = enc.long
    tab = [(0.0, 0.130), (0.10, 0.170), (0.30, 0.132), (0.60, 0.104), (0.85, 0.086), (1.0, 0.074)]
    cou = fuseau(tab, Lc, 64)
    paver(cou, 5, 0.17, 0.016)
    a.piece("cou", cou.sculpte(lambda v: v * [0.86, 1.0, 1.0]).sculpte(enc.couche), None)
    for i, f in enumerate(np.linspace(0.04, 0.97, 24)):
        c_, av, nq = enc.cadre(f * Lc)
        r = float(np.interp(f, [q[0] for q in tab], [q[1] for q in tab]))
        e = A.boule(1.0, 10, 6).etire(0.012, 0.022, 0.034).pose(tuple(c_ + nq * r * 0.98 + np.array([0.0, 0.0, 0.0])))
        a.piece("crin_%02d" % i, e, BRUN, poil=False)

    # ----- la tête : petite, étroite, le museau crème ; penchée vers nous d'en haut ; deux ossicônes à houppe, les oreilles -----
    centre, avant, nuque = enc.cadre(Lc)
    l, p = math.radians(40.0), math.radians(-26.0)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), math.sin(p)))
    T = A.cadre(Vector(centre) + Vector((0.0, -0.020, 0.040)), nez, Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.05, 0.062), (0.22, 0.078), (0.50, 0.062), (0.75, 0.056), (0.92, 0.056), (1.0, 0.0)], 0.300, 56, 0.006)
    tete.teinte = np.where((np.arctan2(tete.v[:, 0], tete.v[:, 1]) > 2.4)[:, None] | (tete.v[:, 2] > 0.235)[:, None], CREME, MIEL)
    a.piece("tete", tete.sculpte(lambda v: v * [0.84, 1.0, 1.0]), None, mat=T @ A.repere((0, 0.040, -0.060)))
    a.tete = T @ Vector((0, 0.040, 0.140))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.034, 0.026, 0.026), CORNE, mat=T @ A.repere((0, 0.030, 0.240)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", T @ Vector((0, 0.040, 0.050)), T3 @ Vector((c * 0.84, 0.42, 0.06)))
        a.oeil("oeil_" + nom, pos + n * 0.004, n, 0.0155)
        a.piece("cils_" + nom, K.paupiere(0.019, 0.20), BRUN, mat=A.cadre(pos + n * 0.005, n, T3 @ Vector((0, 1, 0))), poil=False)
        oss = A.tour(A.profil([(0, 0), (0.024, 0.006), (0.019, 0.060), (0.013, 0.108), (0, 0.118)], 5), 18)
        a.piece("ossicone_" + nom, oss, tuple(MIEL), mat=A.cadre(T @ Vector((c * 0.030, 0.092, -0.040)), Vector((c * 0.10, 0.20, 0.97)), (0, 1, 0)))
        a.piece("houppe_" + nom, A.boule(1.0, 16, 8).etire(0.024, 0.024, 0.026), BRUN, pos=tuple(T @ Vector((c * 0.034, 0.108, -0.040)) + Vector((c * 0.012, 0.024, 0.116))))
        po = A.profil([(0, 0), (0.030, 0.008), (0.040, 0.032), (0.030, 0.060), (0.010, 0.078), (0, 0.084)], 5)
        E = A.cadre(T @ Vector((c * 0.064, 0.056, -0.034)), Vector((c * 0.95, 0.10, 0.28)), (0, 0, 1))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 24).etire(1.0, 0.36, 1.0), [(0.060, tuple(MIEL)), (9, BRUN)]), None, mat=E)

    # ----- les jambes : quatre longues, fines, les genoux noueux ; pavés en haut, crème en bas ; les sabots sombres -----
    def jambe(depart, plan, graine):
        x, y, z = depart
        pts = [(x, y + dy, z - dz) for dy, dz in plan]
        f = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, 0.092), (0.20, 0.072), (0.42, 0.046), (0.50, 0.078), (0.57, 0.044), (0.90, 0.040), (0.96, 0.048), (1.0, 0.0)], f.long, 36, 0.010)
        paver(m, graine, 0.13, 0.016, clair=lambda v: v[:, 2] > 0.80 * f.long)
        return m.sculpte(f.couche), pts[-1], pts[len(pts) // 2 + 0]
    pieds = []
    for nom, dep, plan, g in (("av_G", (0.130, -0.150, 1.040), [(0.0, 0.0), (0.0, 0.33), (-0.01, 0.62), (0.0, 0.86), (-0.01, 1.04)], 11),
                              ("av_D", (-0.130, -0.150, 1.040), [(0.0, 0.0), (-0.01, 0.33), (-0.03, 0.62), (-0.04, 0.86), (-0.04, 1.04)], 12),
                              ("ar_G", (0.140, 0.420, 0.980), [(0.0, 0.0), (-0.03, 0.30), (-0.07, 0.56), (0.03, 0.80), (0.02, 0.98)], 13),
                              ("ar_D", (-0.140, 0.420, 0.980), [(0.0, 0.0), (-0.03, 0.30), (-0.07, 0.56), (0.03, 0.80), (0.02, 0.98)], 14)):
        m, bout, genou = jambe(dep, plan, g)
        a.piece("jambe_" + nom, m, None)
        a.piece("sabot_" + nom, A.boule(1.0, 24, 12).etire(0.048, 0.060, 0.034), CORNE, pos=(bout[0], bout[1] - 0.010, 0.032), poil=False)
    queue = A.tube(A.courbe([(0.0, 0.520, 1.010), (0.0, 0.580, 0.850), (0.0, 0.590, 0.600)], 5), 0.018, 12)
    a.piece("queue", queue, tuple(MIEL))
    a.piece("pinceau", A.boule(1.0, 20, 10).etire(0.040, 0.040, 0.110), BRUN, pos=(0, 0.592, 0.520))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("girafe", styles.style_de("girafe"), sys.modules[__name__]), "Girafe")
