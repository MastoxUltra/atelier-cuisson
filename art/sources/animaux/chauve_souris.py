"""La chauve-souris en peluche : la petite grise violacée des grottes, debout sur ses pieds, les ailes à demi ouvertes comme
une cape de chef d'orchestre qui traîne par terre, de très grandes oreilles dressées doublées de rose, une feuille nasale,
deux dents pointues au coin de la bouche, deux perles noires pour yeux. Elle se tient bien droite : elle vient de
descendre du plafond, elle ne s'en est pas encore remise, et elle fait comme si elle avait atterri exprès.

    python chauve_souris.py        fabrique la fiche art/apercus/animaux/chauve_souris.png (style du palier : A, cousu main)
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

GRIS = np.array(M.hexa("#6c6475"))            # la dominante (registre : gris souris sombre violacé #5c5560), un cran plus clair (cousu main)
VENTRE = np.array(M.hexa("#8b8294"))          # le ventre
MEMBRANE = np.array(M.hexa("#7d7388"))        # la membrane des ailes
OS = np.array(M.hexa("#4f4859"))              # les doigts de l'aile
ROSE = np.array(M.hexa("#e6a0b0"))            # l'accent : l'intérieur des oreilles, la feuille nasale
DENT = M.hexa("#f4ecd8")
FIL = M.hexa("#2e2833")
H = Vector((0.0, -0.040, 0.420))              # le centre de la tête


def aile(c, L=1.0):
    """Une aile ouverte : une membrane festonnée entre quatre doigts, posée de côté, le bout pendu vers le sol ; rend (maille, repère)."""
    contour = [(0.000, 0.000), (0.080, -0.014), (0.180, -0.010), (0.300, -0.002), (0.372, 0.004), (0.332, 0.056), (0.316, 0.128),
               (0.262, 0.094), (0.222, 0.206), (0.164, 0.150), (0.120, 0.262), (0.062, 0.196), (0.000, 0.176)]
    contour = [(x * L, y * L) for x, y in contour]
    m = A.decoupe(contour, 0.006, 0.002)
    m.teinte = np.tile(MEMBRANE, (len(m.v), 1))
    return m


def construire():
    a = K.Animal("chauve_souris")
    a.taille = 0.52

    # ----- le corps : un œuf debout, plus clair devant ; la tête ronde ; les grandes oreilles dressées, doublées de rose -----
    pc = A.profil([(0, 0.0), (0.050, 0.010), (0.085, 0.060), (0.100, 0.150), (0.090, 0.250), (0.066, 0.330), (0.034, 0.375), (0, 0.392)], 6)
    corps = A.tour(pc, 40)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(GRIS, (len(ang), 1))
    t[(ang > 2.0) & (corps.v[:, 2] > 0.04)] = VENTRE
    corps.teinte = t
    a.piece("corps", corps, None, mat=A.repere((0.0, 0.020, 0.040), (-6, 0, 0)))
    tete = A.boule(1.0, 36, 18)
    tete.teinte = np.tile(GRIS, (len(tete.v), 1))
    RT = A.repere(H, (6, 0, 0))
    a.piece("tete", tete.etire(0.066, 0.058, 0.060), None, mat=RT)
    museau = A.boule(1.0, 20, 10).etire(0.034, 0.034, 0.026)
    a.piece("museau", O.teinte(museau, VENTRE), None, mat=RT @ A.repere((0.0, -0.058, -0.016)))
    feuille = O.couche(O.teinte(O.pointe(0.030, 0.016, 8), ROSE), RT @ A.cadre(Vector((0.0, -0.084, -0.004)), Vector((0.0, -0.55, 1.0)), (1, 0, 0)))
    a.piece("feuille", feuille, None, poil=False)
    a.piece("nez", A.boule(1.0, 12, 6).etire(0.010, 0.007, 0.007), FIL, mat=RT @ A.repere((0.0, -0.092, -0.012)), poil=False)
    for c in (1, -1):
        dent = O.couche(O.teinte(O.pointe(0.017, 0.0055, 6), np.array(DENT)), RT @ A.cadre(Vector((c * 0.016, -0.082, -0.036)), Vector((0.0, 0.10, -1.0)), (0, 1, 0)))
        a.piece("dent_%d" % c, dent, None, poil=False)
    O.paire_yeux(a, "tete", H, (0.50, -0.78, 0.22), 0.0120, decolle=0.002)
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.tour(A.profil([(0.044, 0), (0.040, 0.040), (0.026, 0.092), (0.010, 0.140), (0, 0.158)], 4), 24).etire(1.0, 0.26, 1.0)
        ore.teinte = np.tile(GRIS, (len(ore.v), 1))
        a.piece("oreille_" + nom, O.couche(ore, RT @ A.cadre(Vector((c * 0.046, 0.010, 0.046)), Vector((c * 0.28, 0.0, 1.0)), (0, 1, 0))), None)
        dedans = A.tour(A.profil([(0.030, 0), (0.026, 0.040), (0.016, 0.092), (0.006, 0.132), (0, 0.146)], 4), 20).etire(1.0, 0.18, 1.0)
        dedans.teinte = np.tile(ROSE, (len(dedans.v), 1))
        a.piece("dedans_" + nom, O.couche(dedans, RT @ A.cadre(Vector((c * 0.046, -0.004, 0.052)), Vector((c * 0.28, 0.0, 1.0)), (0, 1, 0))), None, poil=False)
    O.broder(a, "bouche", "museau", RT @ Vector((0, -0.058, -0.016)), [(0.54 * u_, -0.82, -0.40 + 0.08 * u_ * u_) for u_ in np.linspace(-1, 1, 7)], 0.0019, FIL)
    a.tete = H + Vector((0.0, -0.12, 0.0))

    # ----- les ailes : à demi ouvertes de chaque côté, la membrane festonnée, quatre doigts sombres, le pouce crochu ; elles traînent -----
    for nom, c in (("G", 1), ("D", -1)):
        pos = Vector((c * 0.080, 0.000, 0.300))
        ex = Vector((c * 0.92, -0.08, -0.40))
        ey = Vector((c * 0.06, 0.96, 0.30))
        R = O.plan(pos, ex, ey)
        m = aile(c)
        a.piece("aile_" + nom, O.couche(m, R), None, poil=False)
        for k, (tx, ty) in enumerate(((0.372, 0.004), (0.316, 0.128), (0.222, 0.206), (0.120, 0.262))):
            p0 = Vector((0.080, -0.010, 0.0))
            p1 = Vector((tx, ty, 0.0))
            os_ = O.tube_r([tuple(R @ p0), tuple(R @ (p0 + (p1 - p0) * 0.5 + Vector((0, 0.006, 0)))), tuple(R @ p1)], [0.0075, 0.0060, 0.0042], 8)
            a.piece("doigt_%s%d" % (nom, k), O.teinte(os_, OS), None, poil=False)
        pouce = O.couche(O.teinte(O.griffe(0.034, 0.0085), np.array(DENT)),
                         A.cadre(R @ Vector((0.082, -0.018, 0.0)), R.to_3x3() @ Vector((0.25, -1.0, 0.0)), (0, 0, 1)))
        a.piece("pouce_" + nom, pouce, None, poil=False)
        # le petit pied : une patte courte, trois orteils
        jb = O.tube_r([(c * 0.036, 0.020, 0.050), (c * 0.040, 0.010, 0.026)], [0.014, 0.012], 8)
        a.piece("jambe_" + nom, O.teinte(jb, GRIS), None, poil=False)
        pied = A.boule(1.0, 18, 8).etire(0.022, 0.040, 0.010)
        a.piece("pied_" + nom, O.teinte(pied, VENTRE * 0.9), None, pos=(c * 0.040, -0.014, 0.011), rot=(0, 0, c * -8), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("chauve_souris", styles.style_de("chauve_souris"), sys.modules[__name__]), "Chauve-souris")
