"""La chauve-souris en peluche, deuxième dessin : la petite grise violacée des grottes, un corps velu en poire, une tête ronde à
museau en groin et feuille nasale, deux oreilles immenses, deux dents pointues, et les ailes : un bras plié qui monte au
poignet, quatre longs doigts d'une feutrine plus foncée, comme les baleines d'un parapluie, et entre eux la membrane tendue,
festonnée au bord, qui retombe jusqu'au sol de chaque côté comme une cape. Debout sur ses petits pieds, elle vient de
descendre du plafond ; elle fait comme si elle avait atterri exprès.

    python chauve_souris.py        fabrique la fiche art/apercus/animaux/chauve_souris.png (style du palier : A, cousu main)
    (le premier dessin, jugé le 15/10 : « le corps est une quille lisse et les ailes sont deux plaques plantées dessus »)
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

GRIS = np.array(M.hexa("#6c6475"))            # la dominante (registre : gris souris sombre violacé #5c5560), un cran plus clair
VENTRE = np.array(M.hexa("#8b8294"))          # le ventre, la poitrine
MEMBRANE = np.array(M.hexa("#857b92"))        # la membrane tendue
FELTRE = np.array(M.hexa("#4a4256"))          # les bras et les doigts : la feutrine plus foncée
ROSE = np.array(M.hexa("#e6a0b0"))            # l'accent : l'intérieur des oreilles, la feuille nasale
DENT = M.hexa("#f4ecd8")
FIL = M.hexa("#2e2833")
H = Vector((0.0, -0.050, 0.405))              # le centre de la tête


def membrane(c):
    """La membrane d'une aile (c = +1 : gauche) : un éventail de bandes tendues entre le bras, quatre doigts et la hanche, le
    bord festonné ; double face. Rend (maille, bouts des doigts, (épaule, coude, poignet))."""
    S = np.array([c * 0.085, 0.000, 0.300])
    E = np.array([c * 0.165, 0.050, 0.340])
    W = np.array([c * 0.270, -0.040, 0.395])
    T = [np.array([c * 0.540, -0.230, 0.030]), np.array([c * 0.610, -0.050, 0.022]),
         np.array([c * 0.520, 0.150, 0.022]), np.array([c * 0.350, 0.270, 0.024])]
    Hh = np.array([c * 0.090, 0.130, 0.120])

    def rail(fin, s):
        return W + (fin - W) * (s ** 0.9) + np.array([0.0, 0.0, 0.03 * math.sin(math.pi * s)])

    def bord(s):                                           # le bord d'attaque : épaule, coude, poignet, puis le premier doigt
        if s < 0.30:
            return S + (E - S) * (s / 0.30)
        if s < 0.60:
            return E + (W - E) * ((s - 0.30) / 0.30)
        return rail(T[0], (s - 0.60) / 0.40)
    rails = [bord, lambda s: rail(T[1], s), lambda s: rail(T[2], s), lambda s: rail(T[3], s), lambda s: W + (Hh - W) * s]
    nfin = 4
    pts, faces = [], []
    ns, nu = 14, 5
    for k in range(nfin):
        base = len(pts)
        for j in range(ns + 1):
            for i in range(nu + 1):
                u = i / nu
                sc = 1.0 - (0.20 * math.sin(math.pi * u) if k < nfin - 1 else 0.0)
                s = (j / ns) * sc
                pts.append(rails[k](s) * (1 - u) + rails[k + 1](s) * u)
        for j in range(ns):
            for i in range(nu):
                v0 = base + j * (nu + 1) + i
                faces.append((v0, v0 + 1, v0 + nu + 2, v0 + nu + 1))
    n = len(pts)
    P = np.array(pts)
    allp = np.vstack([P + np.array([0.0, 0.0, 0.0030]), P - np.array([0.0, 0.0, 0.0030])])
    allf = list(faces) + [tuple(i + n for i in reversed(f)) for f in faces]
    if c < 0:
        allf = [tuple(reversed(f)) for f in allf]
    m = A.Maille(allp, allf)
    m.teinte = np.tile(MEMBRANE, (len(allp), 1))
    return m, T, (S, E, W)


def construire():
    a = K.Animal("chauve_souris")
    a.taille = 0.52

    # ----- le corps : une poire velue, plus claire devant ; des mèches de poil sur la poitrine et le dos -----
    pc = A.profil([(0, 0.0), (0.060, 0.012), (0.105, 0.080), (0.128, 0.170), (0.115, 0.250), (0.082, 0.320), (0.040, 0.368), (0, 0.384)], 6)
    corps = A.tour(pc, 44)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(GRIS, (len(ang), 1))
    t[(ang > 1.9) & (corps.v[:, 2] > 0.04)] = VENTRE
    corps.teinte = t
    a.piece("corps", corps, None, mat=A.repere((0.0, 0.030, 0.034), (-8, 0, 0)))
    rng = np.random.default_rng(12)
    meches = None
    for k in range(70):
        th = rng.uniform(0, math.tau)
        zz = rng.uniform(0.07, 0.34)
        rr = float(np.interp(zz, [0.012, 0.08, 0.17, 0.25, 0.32, 0.368], [0.06, 0.105, 0.128, 0.115, 0.082, 0.040]))
        pos = Vector((rr * math.sin(th) * 0.98, 0.030 + rr * math.cos(th) * 0.98, 0.034 + zz))
        n = Vector((math.sin(th), math.cos(th), 0.25)).normalized()
        d = n + Vector((0.0, 0.0, -0.45))
        couleur = VENTRE * 1.02 if abs(th - math.pi) < 1.0 else GRIS * 1.03
        m = O.couche(O.teinte(O.pointe(0.036 + 0.014 * rng.random(), 0.016, 6), couleur), A.cadre(pos, d.normalized(), (0, 0, 1)))
        meches = m if meches is None else meches + m
    # (plus de pointes claires sur le ventre : « pointes blanches » au contrôle ; le poil du style suffit)

    # ----- la tête ronde, le museau en groin, la feuille nasale rose, deux dents, deux perles pour yeux, les oreilles immenses -----
    RT = A.repere(H, (10, 0, 0))
    tete = A.boule(1.0, 40, 20)
    tete.teinte = np.tile(GRIS * 1.02, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.078, 0.070, 0.072), None, mat=RT)
    groin = A.tour(A.profil([(0.036, 0.0), (0.034, 0.018), (0.028, 0.034), (0.024, 0.044)], 3), 20).etire(1.0, 0.85, 1.0)
    groin.teinte = np.tile(VENTRE * 1.05, (len(groin.v), 1))
    a.piece("groin", O.couche(groin, RT @ A.cadre(Vector((0.0, -0.062, -0.014)), Vector((0.0, -1.0, -0.12)), (0, 0, 1))), None)
    feuille = A.boule(1.0, 20, 10).etire(0.030, 0.010, 0.034)
    feuille.teinte = np.tile(ROSE, (len(feuille.v), 1))
    a.piece("feuille", O.couche(feuille, RT @ A.cadre(Vector((0.0, -0.110, -0.004)), Vector((0.0, -1.0, 0.25)), (0, 0, 1))), None, poil=False)
    for c in (1, -1):
        a.piece("narine_%d" % c, A.boule(1.0, 10, 6).etire(0.0065, 0.0045, 0.0065), FIL, mat=RT @ A.repere((c * 0.0125, -0.1085, -0.012)), poil=False)
        dent = O.couche(O.teinte(O.pointe(0.018, 0.0058, 6), np.array(DENT)), RT @ A.cadre(Vector((c * 0.0175, -0.092, -0.044)), Vector((0.0, 0.10, -1.0)), (0, 1, 0)))
        a.piece("dent_%d" % c, dent, None, poil=False)
    O.paire_yeux(a, "tete", H, (0.52, -0.76, 0.24), 0.0125, decolle=0.002, R=RT)
    for nom, c in (("G", 1), ("D", -1)):
        contour = [(0.0, 0.0), (0.068, 0.007), (0.111, 0.050), (0.124, 0.108), (0.081, 0.155), (0.019, 0.173), (-0.019, 0.148), (-0.041, 0.086),
                   (-0.046, 0.029)]
        ore = A.decoupe([(c * x_, y_) for x_, y_ in contour][::c], 0.008, 0.004)
        ore.teinte = np.tile(GRIS * 0.98, (len(ore.v), 1))
        R = O.plan(H + Vector((c * 0.050, 0.020, 0.052)), Vector((c * 0.55, 0.0, 0.0)), Vector((c * 0.30, 0.10, 1.0)))
        a.piece("oreille_" + nom, O.couche(ore, R), None)
        dedans = A.decoupe([(c * 0.6 * x_ + c * 0.004, y_ * 0.82 + 0.014) for x_, y_ in contour][::c], 0.004, 0.002)
        dedans.teinte = np.tile(ROSE, (len(dedans.v), 1))
        R2 = O.plan(H + Vector((c * 0.050, 0.014, 0.052)), Vector((c * 0.55, 0.0, 0.0)), Vector((c * 0.30, 0.10, 1.0)))
        a.piece("dedans_" + nom, O.couche(dedans, R2), None, poil=False)
    O.broder(a, "bouche", "groin", RT @ Vector((0.0, -0.062, -0.014)), [(0.60 * u_, -0.80, -0.42 + 0.08 * u_ * u_) for u_ in np.linspace(-1, 1, 7)], 0.0019, FIL, R=RT)
    a.tete = H + Vector((0.0, -0.13, 0.0))

    # ----- les ailes : le bras plié qui monte au poignet, quatre doigts de feutrine foncée, la membrane tendue entre eux ; le pouce -----
    for nom, c in (("G", 1), ("D", -1)):
        m, T, (S, E, W) = membrane(c)
        a.piece("aile_" + nom, m, None, poil=False)
        bras = O.tube_r([tuple(S), tuple(E), tuple(W)], [0.020, 0.016, 0.013], 10)
        a.piece("aile_bras_" + nom, O.teinte(bras, FELTRE), None, poil=False)
        for k, tip in enumerate(T):
            mid = W + (tip - W) * 0.55 + np.array([0.0, 0.0, 0.020])
            d = O.tube_r([tuple(W), tuple(mid), tuple(tip)], [0.0095, 0.0075, 0.0050], 8)
            a.piece("aile_doigt_%s%d" % (nom, k), O.teinte(d, FELTRE), None, poil=False)
        pouce = O.couche(O.teinte(O.griffe(0.034, 0.0085), np.array(DENT)),
                         A.cadre(Vector(tuple(W)) + Vector((c * 0.004, -0.012, 0.004)), Vector((c * 0.2, -1.0, 0.4)), (0, 0, 1)))
        a.piece("aile_pouce_" + nom, pouce, None, poil=False)
        jb = O.tube_r([(c * 0.050, 0.055, 0.060), (c * 0.058, 0.040, 0.030)], [0.015, 0.012], 8)
        a.piece("patte_" + nom, O.teinte(jb, GRIS), None, poil=False)
        pied = A.boule(1.0, 18, 8).etire(0.024, 0.040, 0.010)
        a.piece("pied_" + nom, O.teinte(pied, VENTRE * 0.9), None, pos=(c * 0.058, 0.010, 0.012), rot=(0, 0, c * -8), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("chauve_souris", styles.style_de("chauve_souris"), sys.modules[__name__]), "Chauve-souris")
