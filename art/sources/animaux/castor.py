"""Le castor en peluche, deuxième dessin : l'ingénieur de la rivière, qui vient de claquer la queue pour prévenir tout le
monde. Marron glacé, assis sur ses grosses cuisses, il a levé la queue derrière lui : une pagaie noire quadrillée, plus
haute que sa tête, dressée sur la tranche comme un panneau ; une main au menton (il réfléchit à ce qu'on lui veut),
l'autre sur le ventre, la tête tournée de trois quarts avec un sourcil lourd. Deux incisives orange énormes, qui
dépassent de la lèvre fendue ; et les pieds palmés, larges comme des palmes, posés en V devant lui.

    python castor.py        fabrique la fiche art/apercus/animaux/castor.png (style du palier : C, velours ras)
    (le premier dessin, refusé le 15/10 : « deux poires avec des bras en tuyau »)
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
import outils_a as O

MARRON = np.array(M.hexa("#8f5c3c"))          # la dominante (registre : marron glacé) ; le velours éclaircit un peu
CLAIR = np.array(M.hexa("#b8895f"))           # le ventre, le bavoir, le museau
CHARBON = np.array(M.hexa("#322c2b"))         # la queue, les pieds, les oreilles
ORANGE = M.hexa("#f2860f")                    # l'accent : les incisives
NEZ = M.hexa("#171311")
FIL = M.hexa("#241810")
TETE = Vector((0.0, -0.060, 0.690))           # le centre de la tête


def pied_palme():
    """Un pied palmé : une large palme plate, quatre orteils en éventail devant, séparés par un sillon."""
    palme = A.boule(1.0, 36, 12).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.082, 0.150, 0.020)
    for k, dx in enumerate((-0.054, -0.018, 0.018, 0.054)):
        orteil = A.boule(1.0, 16, 8).etire(0.020, 0.036, 0.014).pose((dx, -0.150 + 0.008 * abs(dx) / 0.054, 0.0))
        palme = palme + orteil
    return palme


def construire():
    a = K.Animal("castor")
    a.taille = 0.95

    # ----- le corps : une poire assise, penchée en avant, la panse pleine, le dos rond, la croupe large ; ventre et bavoir plus clairs -----
    pc = A.profil([(0, 0.0), (0.120, 0.012), (0.200, 0.075), (0.235, 0.170), (0.225, 0.290), (0.190, 0.400), (0.140, 0.490), (0.075, 0.550), (0, 0.575)], 6)
    corps = A.tour(pc, 56)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))              # 0 : le dos ; pi : le ventre
    z = corps.v[:, 2]
    t = np.tile(MARRON, (len(z), 1))
    t[(ang > 2.2) & (z < 0.52)] = CLAIR
    corps.teinte = t

    def galbe(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 0] *= 1 + 0.10 * np.exp(-((z - 0.10) / 0.09) ** 2) - 0.08 * np.exp(-((z - 0.38) / 0.12) ** 2)      # les hanches, la taille
        dev = v[:, 1] < 0
        s[dev, 1] *= (1 + 0.20 * np.exp(-((z - 0.22) / 0.12) ** 2))[dev]                                          # la panse
        s[~dev, 1] *= (1 + 0.10 * np.exp(-((z - 0.34) / 0.14) ** 2))[~dev]                                        # le dos rond
        return s
    a.piece("corps", corps.sculpte(galbe), None, mat=A.repere((0.0, 0.060, 0.018), (11, 0, 0)))

    # ----- la tête : large, plate, les joues pleines et le front lourd ; tournée de trois quarts vers sa gauche -----
    tete = A.boule(1.0, 56, 28)
    for c in (1, -1):
        tete.sculpte(lambda v, c=c: K.bosse(v, (c * 0.85, -0.45, -0.25), 0.22, 0.30))            # les joues
        tete.sculpte(lambda v, c=c: K.bosse(v, (c * 0.45, -0.60, 0.72), 0.14, 0.18))             # les arcades
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(MARRON, (len(u), 1))
    t[(u[:, 1] < -0.45) & (u[:, 2] < 0.15)] = CLAIR
    tete.teinte = t
    RT = A.repere(TETE, (7, 0, 24))
    a.piece("tete", tete.etire(0.135, 0.120, 0.105), None, mat=RT)
    R3 = RT.to_3x3()

    # le museau : large et plat, le nez noir, la lèvre fendue, le menton qui fuit ; deux grandes incisives orange
    museau = A.boule(1.0, 36, 18).etire(0.080, 0.078, 0.060)
    a.piece("museau", O.teinte(museau, CLAIR), None, mat=RT @ A.repere((0.0, -0.100, -0.045)))
    a.piece("nez", A.boule(1.0, 16, 8).etire(0.032, 0.022, 0.020), NEZ, mat=RT @ A.repere((0.0, -0.172, -0.020)), poil=False)
    menton = A.boule(1.0, 24, 12).etire(0.046, 0.046, 0.030)
    a.piece("menton", O.teinte(menton, CLAIR * 0.92), None, mat=RT @ A.repere((0.0, -0.100, -0.108)))
    dents = None
    for c in (1, -1):
        d = A.boule(1.0, 16, 8).sculpte(lambda v: K.emousse(v, 0.75)).etire(0.0185, 0.0125, 0.056).pose((c * 0.0135, -0.158, -0.105))
        dents = d if dents is None else dents + d
    a.piece("incisives", dents, ORANGE, mat=RT, poil=False)

    # les yeux : petits, vivants, sous un sourcil lourd ; les petites oreilles rondes, sombres
    O.paire_yeux(a, "tete", TETE, (0.52, -0.80, 0.20), 0.0165, couleur_lourde=tuple(MARRON), coupe=0.14, decolle=0.003)
    for nom, c in (("G", 1), ("D", -1)):
        oreille = A.boule(1.0, 24, 12).etire(0.034, 0.016, 0.036)
        a.piece("oreille_" + nom, O.teinte(oreille, CHARBON), None, mat=RT @ A.repere((c * 0.104, 0.012, 0.100), (0, c * 18, 0)))
    a.tete = TETE + Vector((0.0, -0.17, 0.0))

    # ----- les bras : le gauche plié, la patte contre le menton ; le droit posé sur la panse ; trois petites griffes sombres -----
    for nom, c, pts, pat in (("G", 1, [(0.200, -0.020, 0.470), (0.330, -0.080, 0.430), (0.300, -0.170, 0.520), (0.185, -0.205, 0.560)], (0.165, -0.212, 0.565)),
                             ("D", -1, [(-0.200, -0.020, 0.470), (-0.290, -0.100, 0.370), (-0.220, -0.215, 0.300), (-0.110, -0.255, 0.300)], (-0.095, -0.262, 0.302))):
        bras = O.tube_r(pts, [0.082, 0.068, 0.058, 0.052], 20)
        bras.teinte = np.tile(MARRON, (len(bras.v), 1))
        main = A.boule(1.0, 24, 12).etire(0.052, 0.046, 0.040).pose(pat)
        main.teinte = np.tile(CHARBON, (len(main.v), 1))
        ens = bras + main
        for k, dx in enumerate((-0.026, 0.0, 0.026)):
            g = O.griffe(0.034, 0.0075)
            g.teinte = np.tile(CHARBON * 0.7, (len(g.v), 1))
            ens = ens + O.couche(g, A.cadre(Vector((pat[0] + dx, pat[1] - 0.040, pat[2] - 0.004)), (0.0, -1.0, -0.20), (0, 0, 1)))
        a.piece("bras_" + nom, ens, None)

    # ----- les cuisses (de grosses cuisses rondes, assises) et les pieds palmés posés en V devant -----
    for nom, c in (("G", 1), ("D", -1)):
        cuisse = A.boule(1.0, 36, 18).etire(0.120, 0.170, 0.130)
        a.piece("cuisse_" + nom, O.teinte(cuisse, MARRON), None, pos=(c * 0.185, 0.050, 0.140), rot=(8, 0, c * 10))
        pied = pied_palme()
        pied.teinte = np.tile(CHARBON, (len(pied.v), 1))
        a.piece("pied_" + nom, pied, None, pos=(c * 0.190, -0.185, 0.028), rot=(0, 0, c * -22), poil=False)

    # ----- la queue : un court pédoncule, puis la grande pagaie noire quadrillée, dressée derrière sa tête, bien plus haute -----
    pedoncule = O.tube_r([(0.0, 0.170, 0.070), (0.0, 0.250, 0.060), (0.0, 0.330, 0.085)], [0.040, 0.036, 0.034], 14)
    a.piece("pedoncule", O.teinte(pedoncule, CHARBON), None)

    def losanges(m):
        x, y = m.v[:, 0], m.v[:, 1]
        g = (np.sin((x + y) * 38) > 0.62) | (np.sin((x - y) * 38) > 0.62)
        t = np.tile(CHARBON, (len(x), 1))
        t[g] = CHARBON * 0.45 + MARRON * 0.55
        r = np.hypot(x / 0.190, y / 0.340)
        t[r > 0.86] = CHARBON * 0.6                                       # le bord, plus sombre
        m.teinte = t
        return m
    pagaie = A.boule(1.0, 48, 20).etire(0.190, 0.340, 0.030)
    losanges(pagaie)
    a.piece("pagaie", pagaie, None, pos=(0.0, 0.500, 0.350), rot=(64, 0, 4), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("castor", styles.style_de("castor"), sys.modules[__name__]), "Castor")
