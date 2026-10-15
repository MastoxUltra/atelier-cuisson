"""Le fennec en peluche de velours ras (2e dessin) : un petit RENARD de sable, crème sable (jamais blanc), la face
fine et le museau long et pointu, de grands yeux sombres en amande, et deux oreilles immenses, triangulaires et larges
à la base, aussi hautes que la tête est longue, le dedans rose et poilu ; une queue en panache au bout noir. Couché
comme un sphinx, les pattes avant allongées, la tête relevée et tournée vers nous, le nez un peu en l'air, les
oreilles chacune d'un côté : il écoute tout le désert.

    python fennec.py        fabrique la fiche art/apercus/animaux/fennec.png (velours ras, palier 3)
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


SABLE = np.array(M.hexa("#f2cf94"))           # la dominante : crème sable (le poil le fonce)
DOS = np.array(M.hexa("#e8bc7c"))             # le dos, le dessus du crâne, le dos des oreilles
CREME = np.array(M.hexa("#fff0d0"))           # le ventre, la face, le poitrail, les pattes
ROSE = M.hexa("#f4c8b0")                      # l'accent : le dedans des oreilles
NOIR = np.array(M.hexa("#2e2826"))            # le nez, le bout de la queue, le trait des yeux
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("fennec")
    a.taille = 0.60

    # ----- le corps : un petit corps de renard couché, long et bas, le dos sable, le ventre et la poitrine crème -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.230, 0.075), (0.130, 0.090), (0.010, 0.100), (-0.100, 0.118), (-0.160, 0.140))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.06, 0.062), (0.22, 0.088), (0.55, 0.092), (0.84, 0.082), (0.96, 0.062), (1.0, 0.0)], L, 64)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.where((th > 2.2)[:, None], CREME, np.where((th < 1.1)[:, None], DOS, SABLE))
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou et la tête : un cou fin qui relève la tête ; le crâne petit, le MUSEAU long et pointu, la face crème ;
    #       tournée vers nous, le nez un peu en l'air -----
    a.piece("cou", A.tube(A.courbe([(0.0, -0.130, 0.140), (0.0, -0.170, 0.190), (0.0, -0.190, 0.240)], 5), lambda t: 0.060 - 0.016 * t, 20), tuple(CREME))
    T = A.cadre(Vector((0.0, -0.225, 0.270)), Vector((0.48, -1.0, 0.22)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.044), (0.20, 0.060), (0.36, 0.058), (0.56, 0.044), (0.76, 0.030), (0.92, 0.021), (0.98, 0.014), (1.0, 0.0)],
                  0.190, 48, 0.004)
    tt = np.where((tete.v[:, 1] > 0.020)[:, None], DOS, CREME)
    tt[(tete.v[:, 2] > 0.045) & (tete.v[:, 1] > 0.0) & (tete.v[:, 1] < 0.035)] = SABLE
    tete.teinte = tt
    a.piece("tete", tete.sculpte(lambda v: v * [1.0, 0.86, 1.0]), None, mat=T @ A.repere((0, 0, -0.045)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.014, 0.011, 0.012), tuple(NOIR), mat=T @ A.repere((0, 0.002, 0.146)), poil=False)
    a.tete = T @ Vector((0, 0.0, 0.100))

    # ----- les yeux : grands, sombres, en amande, relevés vers les tempes, cernés d'un trait noir ; les oreilles : immenses
    #       triangles dressés, larges à la base, le dedans rose et poilu ; l'une tournée vers nous, l'autre de côté -----
    po = A.profil([(0, 0), (0.060, 0.010), (0.062, 0.036), (0.052, 0.090), (0.038, 0.150), (0.022, 0.210), (0.008, 0.256), (0, 0.272)], 7)
    for nom, c, ecart in (("G", 1, 0.0), ("D", -1, 1.0)):
        regard = T3 @ Vector((c * 0.70, 0.26, 0.30))
        a.rustine("cerne_" + nom, "tete", T.to_translation(), regard, 0.25, tuple(NOIR), 0.003, 0)
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0165)
        a.piece("amande_" + nom, K.paupiere(0.0190, 0.30), tuple(DOS), mat=A.cadre(p + n * 0.005, n, T3 @ Vector((c * -0.5, 1, 0.1))), poil=False)
        vers = (T3 @ Vector((c * (0.46 + 0.30 * ecart), 0.86 - 0.10 * ecart, -0.30 - 0.15 * ecart))).normalized()
        E = A.cadre(T @ Vector((c * 0.036, 0.040, -0.040)) - vers * 0.008, vers, T3 @ Vector((c * 0.2, 0.0, 1.0)))
        a.piece("oreille_" + nom, A.tour(po, 40).etire(1.0, 0.26, 1.0), tuple(DOS), mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 32).etire(0.68, 0.26, 0.86).pose((0, 0.010, 0.012)), ROSE, mat=E, poil=False)

    # ----- les pattes : les deux avant allongées devant lui (d'une seule pièce, crème, le poignet fin, la petite patte) ;
    #       les cuisses repliées sous les hanches, les pieds arrière devant elles -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.056, -0.050, 0.140), (c * 0.054, -0.120, 0.070), (c * 0.052, -0.200, 0.034), (c * 0.050, -0.270, 0.026)]
        fa = K.Fil(ch, (1, 0, 0))
        av = fuseau([(0.0, 0.030), (0.08, 0.040), (0.40, 0.030), (0.70, 0.022), (0.82, 0.026), (0.94, 0.028), (1.0, 0.0)], fa.long, 24, 0.005)
        av.teinte = np.tile(CREME, (len(av.v), 1))
        a.piece("patte_av_" + nom, av.sculpte(fa.couche), None)
        cu = A.boule(1.0, 32, 16)
        cu.teinte = np.where((cu.v[:, 2] > 0.2)[:, None], SABLE, CREME)
        a.piece("cuisse_" + nom, cu.etire(0.046, 0.100, 0.064), None, pos=(c * 0.080, 0.140, 0.070), rot=(0, 0, c * 8))
        a.piece("pied_ar_" + nom, A.boule(1.0, 20, 10).etire(0.026, 0.070, 0.020), tuple(CREME), pos=(c * 0.066, 0.040, 0.020), rot=(0, 0, c * 4))

    # ----- la queue : un panache épais, qui part de la croupe et se recourbe sur le côté, le bout noir -----
    qf = K.Fil([(0.0, 0.190, 0.080), (0.0, 0.290, 0.072), (0.030, 0.390, 0.060), (0.100, 0.450, 0.052), (0.190, 0.430, 0.046), (0.235, 0.360, 0.042)], (1, 0, 0))
    LQ = qf.long
    queue = fuseau([(0.0, 0.034), (0.20, 0.052), (0.50, 0.062), (0.78, 0.054), (0.92, 0.036), (0.98, 0.018), (1.0, 0.0)], LQ, 40, 0.006)
    queue.teinte = np.where((queue.v[:, 2] > 0.82 * LQ)[:, None], NOIR, np.where((queue.v[:, 1] < -0.010)[:, None], CREME, SABLE))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("fennec", styles.style_de("fennec"), sys.modules[__name__]), "Fennec")
