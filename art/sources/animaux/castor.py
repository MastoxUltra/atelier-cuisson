"""Le castor en peluche, troisième dessin (16/10, planches 19-20 : « manque de réalisme ») : le castor À QUATRE PATTES, bas
et rond, d'après les vues d'un modèle de référence (references_3d/castor, CC-BY : vues seulement, rien d'importé).
Marron glacé, un gros corps en poire posé presque au sol, plus haut derrière ; la tête ronde au museau large et plat, le
nez noir, deux incisives orange qui dépassent ; de petits yeux, de petites oreilles rondes ; de petites mains sombres sous
le poitrail, de grands pieds palmés de chaque côté de la croupe ; la queue, une large pagaie noire quadrillée, couchée à
plat derrière lui. Il vient de sortir de l'eau et vous regarde, sans se presser.

    python castor.py        fabrique la fiche art/apercus/animaux/castor.png (style du palier : C, velours ras)
    (1er dessin : « deux poires avec des bras en tuyau » ; 2e : assis comme un homme, la queue dressée, refusé le 16/10)
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
CLAIR = np.array(M.hexa("#b8895f"))           # le ventre, le museau
CHARBON = np.array(M.hexa("#322c2b"))         # la queue, les pieds, les mains
ORANGE = M.hexa("#f2860f")                    # l'accent : les incisives
NEZ = M.hexa("#171311")
FIL = M.hexa("#241810")
H = Vector((0.0, -0.395, 0.360))              # le centre de la tête


def pied_palme():
    """Un pied palmé : une large palme plate, cinq orteils en éventail devant, réunis par la palmure."""
    palme = A.boule(1.0, 36, 12).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.072, 0.120, 0.020)
    for dx in (-0.056, -0.028, 0.0, 0.028, 0.056):
        orteil = A.boule(1.0, 16, 8).etire(0.016, 0.030, 0.013).pose((dx, -0.122 + 0.010 * abs(dx) / 0.056, 0.0))
        palme = palme + orteil
    return palme


def construire():
    a = K.Animal("castor")
    a.taille = 0.95

    # ----- le corps : une grosse poire couchée, plus haute et plus large derrière, le ventre presque au sol ; le ventre clair -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))              # 0 : le dos ; pi : le ventre
        t = np.tile(MARRON, (len(ang), 1))
        t[ang > 2.35] = CLAIR
        return t
    rayon = O.interp([(0.0, 0.0), (0.05, 0.160), (0.20, 0.252), (0.40, 0.270), (0.62, 0.254), (0.82, 0.208), (0.94, 0.158), (1.0, 0.070)])
    O.corps_h(a, "corps", (0.0, 0.220, 0.270), 0.520, rayon, peint, None, cotes=56, pitch=-6.0,
              deforme=O.gabarit(poitrail=0.02, taille=0.0, croupe=0.10, garrot=0.0, ventre=0.0, pos_croupe=0.30))

    # ----- la tête : ronde, les joues pleines ; le museau large et plat, plus clair ; le nez noir ; les incisives orange -----
    RT = A.repere(H, (4, 0, 14))
    R3 = RT.to_3x3()
    crane = A.boule(1.0, 52, 26).sculpte(lambda v: K.emousse(v, 0.82))
    for c in (1, -1):
        crane.sculpte(lambda v, c=c: K.bosse(v, (c * 0.85, -0.40, -0.25), 0.22, 0.28))   # les joues
    a.piece("tete", O.teinte(crane.etire(0.128, 0.130, 0.118), MARRON), None, mat=RT)
    museau = A.boule(1.0, 36, 18).sculpte(lambda v: K.emousse(v, 0.75)).etire(0.092, 0.070, 0.064)
    a.piece("museau", O.teinte(museau, CLAIR), None, mat=RT @ A.repere((0.0, -0.100, -0.040)))
    a.piece("nez", A.boule(1.0, 16, 8).etire(0.032, 0.020, 0.020), NEZ, mat=RT @ A.repere((0.0, -0.166, -0.016)), poil=False)
    for nom_d, c in (("G", 1), ("D", -1)):                       # deux incisives orange, côte à côte, qui sortent de la lèvre du haut, sous le nez
        # (16/10 : sous le bas du museau, elles flottaient sous le menton ; le devant du museau est à y = -0,167 pour z = -0,058)
        dent = A.boule(1.0, 16, 8).sculpte(lambda v: K.emousse(v, 0.70)).etire(0.0135, 0.0070, 0.0260)   # plus grandes : elles se voient de face
        a.piece("dent_" + nom_d, dent, ORANGE, mat=RT @ A.repere((c * 0.0136, -0.168, -0.058), (-8, 0, 0)), poil=False)   # sous le nez, collées au devant du museau
    O.broder(a, "bouche", "museau", RT @ Vector((0.0, -0.100, -0.040)), [(0.55 * u_, -0.70, -0.62 + 0.08 * u_ * u_) for u_ in np.linspace(-1, 1, 7)],
             0.0024, FIL, R=RT)
    O.paire_yeux(a, "tete", H, (0.60, -0.70, 0.40), 0.0170, decolle=0.003, R=RT)
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", H, R3 @ Vector((c * 0.70, 0.25, 0.66)))
        a.piece("oreille_" + nom, O.teinte(A.boule(1.0, 24, 12).etire(0.030, 0.014, 0.030), CHARBON * 1.4), None,
                mat=A.cadre(pos + n * 0.006, n, R3 @ Vector((0.0, -1.0, 0.0))))
    a.tete = RT @ Vector((0.0, -0.200, -0.020))

    # ----- les mains : de petites pattes sombres sous le poitrail ; les grands pieds palmés de chaque côté de la croupe -----
    for sgn, nom in ((1, "G"), (-1, "D")):
        O.jambe(a, "avant_" + nom, (sgn * 0.100, -0.250, 0.220), (sgn * 0.110, -0.320, 0.030), 0.060, MARRON, bas=CHARBON,
                bas_frac=0.55, sorte="av", plie=0.020, pied_dim=(0.040, 0.052, 0.020), griffes=0)
        cuisse = A.boule(1.0, 36, 18).etire(0.100, 0.150, 0.120)
        a.piece("cuisse_" + nom, O.teinte(cuisse, MARRON), None, pos=(sgn * 0.190, 0.060, 0.150), rot=(10, 0, sgn * 8))
        pied = pied_palme()
        pied.teinte = np.tile(CHARBON, (len(pied.v), 1))
        a.piece("pied_" + nom, pied, None, pos=(sgn * 0.215, -0.060, 0.021), rot=(0, 0, sgn * -14), poil=False)

    # ----- la queue : la grande pagaie noire quadrillée, couchée à plat derrière lui, au bout d'un court pédoncule -----
    pedoncule = O.tube_r([(0.0, 0.180, 0.120), (0.0, 0.270, 0.070), (0.0, 0.330, 0.040)], [0.060, 0.046, 0.036], 16)
    a.piece("pedoncule", O.teinte(pedoncule, CHARBON), None)

    def losanges(m):
        x, y = m.v[:, 0], m.v[:, 1]
        g = (np.sin((x + y) * 38) > 0.62) | (np.sin((x - y) * 38) > 0.62)
        t = np.tile(CHARBON * 0.92, (len(x), 1))
        t[g] = CHARBON * 1.55
        r = np.hypot(x / 0.130, y / 0.220)
        t[r > 0.86] = CHARBON * 0.6                                   # le bord, plus sombre
        m.teinte = t
        return m
    pagaie = A.boule(1.0, 48, 20).etire(0.130, 0.220, 0.026)
    losanges(pagaie)
    a.piece("pagaie", pagaie, None, pos=(0.0, 0.530, 0.030), rot=(-3, 0, 0), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("castor", styles.style_de("castor"), sys.modules[__name__]), "Castor")
