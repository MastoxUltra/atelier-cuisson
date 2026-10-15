"""Le guépard en peluche de magasin : un or pâle doré, le ventre crème, des taches rondes noires nettes semées sur tout
le corps (petites, serrées), une petite tête ronde aux « larmes » noires qui coulent de l'œil à la gueule, un corps
d'une finesse de lévrier, de très longues pattes, la queue annelée. Le sprinter à l'affût : le corps bas et tendu, le
dos creusé, l'avant-main penché, la tête haute tournée vers nous, un antérieur levé : il se décide.

    python guepard.py        fabrique la fiche art/apercus/animaux/guepard.png (peluche de magasin, palier 4)
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


# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
OR = np.array(M.hexa("#f8d890"))              # la dominante : or pâle doré
CREME = np.array(M.hexa("#fff4dc"))           # le ventre, le museau, le dessous
NOIR = np.array(M.hexa("#2e2824"))            # l'accent : les taches
OEIL = M.hexa("#e8b84a")
CHARBON = M.hexa("#2e2824")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=72, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def tacheter(m, graine, n, rayon, couleur=NOIR, base=OR, ventre=None, ecart=0.0):
    """Peint une pièce encore droite en « base » et y sème n taches rondes nettes (rayon donné, ±30 %), sur des sommets pris au
    hasard ; ventre(v) vrai : crème sans taches."""
    rng = np.random.default_rng(graine)
    v = m.v
    t = np.tile(base, (len(v), 1))
    cibles = v[rng.choice(len(v), size=min(n, len(v)), replace=False)]
    r = rayon * (0.7 + 0.6 * rng.random(len(cibles)))
    d = np.linalg.norm(v[:, None, :] - cibles[None, :, :], axis=2)
    t[(d < r[None, :]).any(axis=1)] = couleur
    if ventre is not None:
        t[ventre(v)] = CREME
    m.teinte = t
    return m


def construire():
    a = K.Animal("guepard")
    a.taille = 1.80

    # ----- le corps : un long fuseau de lévrier, le dos creusé, le poitrail profond ; tacheté de rondes nettes -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.540, 0.660), (0.340, 0.720), (0.080, 0.690), (-0.180, 0.700), (-0.380, 0.690), (-0.470, 0.690))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.03, 0.095), (0.12, 0.135), (0.30, 0.125), (0.50, 0.110), (0.70, 0.135), (0.90, 0.150), (1.0, 0.0)], L, 80, 0.007)
    tacheter(corps, 2, 330, 0.026, ventre=lambda v: (np.abs(np.arctan2(v[:, 0], v[:, 1])) > 2.5))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- la tête : petite et ronde, le museau court, les larmes noires de l'œil à la gueule ; haute, tournée vers nous -----
    H = A.cadre(Vector((0.0, -0.600, 0.840)), Vector((0.40, -1.0, -0.14)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.08, 0.075), (0.28, 0.092), (0.55, 0.076), (0.82, 0.056), (0.96, 0.046), (1.0, 0.0)], 0.250, 56, 0.005)
    tacheter(tete, 8, 60, 0.012, ventre=lambda v: (v[:, 2] > 0.190) | (np.abs(np.arctan2(v[:, 0], v[:, 1])) > 2.5))
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0, -0.060)))
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.022, 0.016, 0.014), CHARBON, mat=H @ A.repere((0, 0.034, 0.178)), poil=False)
    a.tete = H @ Vector((0, 0.020, 0.120))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.80, 0.40, 0.14))
        a.rustine("iris_" + nom, "tete", H @ Vector((0, 0.020, 0.040)), regard, 0.20, OEIL, 0.003, 0)
        p, n = a.surface("tete", H @ Vector((0, 0.020, 0.040)), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0145)
        larme = [H3 @ Vector((c * (0.80 - 0.10 * t), 0.20 - 0.42 * t, 0.14 + 0.22 * t)) for t in np.linspace(0, 1, 6)]
        a.broderie("larme_" + nom, A.courbe(propres(a.trace("tete", H @ Vector((0, 0.020, 0.040)), larme, 0.003)), 4), 0.0032, tuple(NOIR))
        po = A.profil([(0, 0), (0.030, 0.008), (0.038, 0.030), (0.030, 0.052), (0.012, 0.066), (0, 0.072)], 5)
        E = A.cadre(H @ Vector((c * 0.058, 0.060, -0.020)), H3 @ Vector((c * 0.30, 0.25, 0.92)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 24).etire(1.0, 0.42, 1.0), [(0.050, tuple(OR)), (9, tuple(NOIR))]), None, mat=E)
    a.piece("cou", A.tube(A.courbe([(0.0, -0.420, 0.740), (0.0, -0.520, 0.800), (0.0, -0.590, 0.830)], 5), lambda t: 0.090 - 0.026 * t, 18), tuple(OR))

    # ----- les pattes : très longues et fines, tachetées ; un antérieur levé et replié ; les pieds aux griffes sorties -----
    def patte(points, r0):
        m = fuseau([(0.0, r0), (0.40, r0 * 0.62), (0.52, r0 * 0.74), (0.62, r0 * 0.52), (0.95, r0 * 0.46), (1.0, 0.0)],
                   float(np.sum(np.linalg.norm(np.diff(np.asarray(points), axis=0), axis=1))), 28, 0.008)
        return m
    for nom, x, y, r0, plan in (("ar_G", 0.115, 0.430, 0.070, [(0.0, 0.0), (-0.07, 0.30), (0.05, 0.52), (0.04, 0.66)]),
                                ("ar_D", -0.115, 0.430, 0.070, [(0.0, 0.0), (-0.07, 0.30), (0.05, 0.52), (0.04, 0.66)]),
                                ("av_D", -0.095, -0.320, 0.058, [(0.0, 0.0), (0.02, 0.28), (0.00, 0.52), (-0.01, 0.66)])):
        pts = [(x, y + dy, 0.680 - dz) for dy, dz in plan]
        f = K.Fil(pts, (1, 0, 0))
        m = patte(pts, r0)
        m.v *= 1.0
        # reprend la longueur du fil pour la pièce
        m = fuseau([(0.0, r0), (0.40, r0 * 0.62), (0.52, r0 * 0.74), (0.62, r0 * 0.52), (0.95, r0 * 0.46), (1.0, 0.0)], f.long, 28, 0.008)
        tacheter(m, 20 + int(abs(x) * 100), 40, 0.020, ventre=lambda v, L=f.long: v[:, 2] > 0.86 * L)
        a.piece("patte_" + nom, m.sculpte(f.couche), None)
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.048, 0.078, 0.026), tuple(CREME), pos=(x, pts[-1][1] - 0.030, 0.026))
    levee = [(0.095, -0.320, 0.680), (0.102, -0.340, 0.470), (0.105, -0.420, 0.440), (0.105, -0.460, 0.340)]
    a.piece("patte_av_G", K.tube_peint(A.courbe(levee, 6), lambda t: 0.050 - 0.016 * t, [(0.86, tuple(OR)), (1, tuple(CREME))], 14), None)
    a.piece("pied_av_G", A.boule(1.0, 20, 10).etire(0.044, 0.070, 0.026), tuple(CREME), pos=(0.105, -0.490, 0.316), rot=(-40, 0, 0))

    # ----- la queue : longue, annelée de noir, qui pend et se relève au bout ; le pinceau noir -----
    chemin = [(0.0, 0.540, 0.640), (0.040, 0.760, 0.470), (0.120, 0.920, 0.260), (0.230, 0.980, 0.150), (0.340, 0.940, 0.110)]
    bagues, f, c = [], 0.0, tuple(OR)
    while f < 0.84:
        f += 0.085
        bagues.append((min(f, 0.84), c))
        c = tuple(NOIR) if c == tuple(OR) else tuple(OR)
    bagues[-1] = (0.84, bagues[-1][1])
    bagues.append((1.0, tuple(NOIR)))
    a.piece("queue", K.tube_peint(A.courbe(chemin, 6), lambda t: 0.046 - 0.014 * t, bagues, 16), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("guepard", styles.style_de("guepard"), sys.modules[__name__]), "Guépard")
