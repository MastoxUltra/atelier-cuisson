"""Le diable de Tasmanie en peluche de magasin (3e dessin) : un corps bas et massif posé sur des pattes courtes et
écartées, un charbon profond, le plastron blanc en croissant et la tache blanche de croupe ; une tête PLUS LARGE QUE
LES ÉPAULES, plate devant, taillée en coin, et deux mâchoires séparées, grandes ouvertes : une gueule rose, deux crocs
en haut, deux en bas. Les oreilles rouge sang dressées. Il hurle : le museau levé, tout le corps ramassé et tendu.

    python diable_de_tasmanie.py        fabrique la fiche art/apercus/animaux/diable_de_tasmanie.png (peluche de magasin, palier 4)
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

# le style B adoucit les couleurs (vers leur gris) : le noir reste noir, le blanc doit rester franc
CHARBON = M.hexa("#3a3638")                   # la dominante : charbon profond
BLANC = M.hexa("#fffaf2")                     # l'accent : le plastron, la tache de croupe, les crocs
ROUGE = M.hexa("#ee3040")                     # les oreilles (rouge sang)
ROSE = M.hexa("#f07888")                      # l'intérieur de la gueule
CORPS = Vector((0.0, 0.200, 0.200))
TETE = Vector((0.0, -0.250, 0.300))
LACET = 18.0


def construire():
    a = K.Animal("diable_de_tasmanie")
    a.taille = 0.90

    # ----- le corps : bas, massif, large (plus étroit que la tête), le dos plat ; le plastron en croissant -----
    def masse(v):
        v = K.bosse(v, (0, -0.60, 0.40), 0.12, 0.45)
        s = v * [0.200, 0.340, 0.170]
        s[:, 2] = np.where(s[:, 2] < 0, s[:, 2] * 0.85, s[:, 2])
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(masse), CHARBON, pos=CORPS)
    a.rustine("plastron", "corps", CORPS + Vector((0, -0.060, 0.030)), (0, -0.96, 0.24),
              lambda th: 0.32 + 0.26 * max(0.0, math.sin(th)), BLANC, 0.004, 0)
    a.rustine("croupe", "corps", CORPS, (0.66, 0.62, 0.24), 0.26, BLANC, 0.004, 0)

    # ----- la tête : un coin large et PLAT devant (la mâchoire du haut), plus large que les épaules ; levée pour hurler -----
    H = A.repere(TETE, (-26, 0, LACET))
    H3 = H.to_3x3()

    def coin(v):
        s = K.emousse(v, 0.80)
        s[:, 0] *= 1 + 0.20 * K.lisse((-v[:, 1] + 0.1) / 0.9)                      # s'élargit vers l'avant
        s[:, 1] = np.where(v[:, 1] < 0, v[:, 1] * 0.66, v[:, 1])                    # plat devant
        return s * [0.250, 0.200, 0.110]
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(coin), CHARBON, mat=H @ A.repere((0, 0, 0.040)))
    a.piece("nez", A.boule(1.0, 24, 12).etire(0.040, 0.026, 0.020), M.hexa("#c07070"), mat=H @ A.repere((0, -0.150, 0.056)), poil=False)
    a.tete = H @ Vector((0, -0.170, 0.000))

    # ----- la mâchoire du bas : une pièce à part, abaissée loin, large ; entre les deux, la gueule rose ; deux crocs en haut,
    #       deux en bas -----
    bas = A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.82) * [0.200, 0.150, 0.056])
    a.piece("machoire", bas, CHARBON, mat=H @ A.repere((0, -0.090, -0.140), (34, 0, 0)))
    a.piece("gueule", A.boule(1.0, 32, 16).etire(0.170, 0.120, 0.034), ROSE, mat=H @ A.repere((0, -0.090, -0.052), (18, 0, 0)), poil=False)
    for c in (1, -1):
        a.piece("croc_h_" + ("G" if c > 0 else "D"), A.tour(A.profil([(0, 0), (0.020, 0.004), (0.012, 0.040), (0.004, 0.066), (0, 0.074)], 5), 14),
                BLANC, mat=H @ A.repere((c * 0.074, -0.140, -0.010), (178, 0, 0)), poil=False)
        a.piece("croc_b_" + ("G" if c > 0 else "D"), A.tour(A.profil([(0, 0), (0.020, 0.004), (0.012, 0.040), (0.004, 0.066), (0, 0.074)], 5), 14),
                BLANC, mat=H @ A.repere((c * 0.066, -0.150, -0.148), (-10, 0, 0)), poil=False)

    # ----- les yeux : minuscules, serrés, sous une arcade ; les oreilles : deux feuilles rouge sang dressées -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation() + Vector((0, 0, 0.040)), H3 @ Vector((c * 0.58, -0.62, 0.50)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0140)
        po = A.profil([(0, 0), (0.046, 0.010), (0.062, 0.046), (0.056, 0.086), (0.030, 0.116), (0, 0.132)], 6)
        E = A.cadre(H @ Vector((c * 0.150, 0.050, 0.100)), H3 @ Vector((c * 0.34, 0.14, 0.92)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, A.tour(po, 28).etire(1.0, 0.34, 1.0), CHARBON, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 20).etire(0.72, 0.30, 0.82).pose((0, 0.008, 0.012)), ROUGE, mat=E, poil=False)

    # ----- les pattes : courtes, épaisses et écartées sur les côtés, les pieds posés à plat ; la queue : un bout court -----
    for nom, x, y in (("av_G", 0.250, -0.080), ("av_D", -0.250, -0.080), ("ar_G", 0.240, 0.380), ("ar_D", -0.240, 0.380)):
        c = 1 if x > 0 else -1
        chemin = [(x * 0.70, y, 0.160), (x * 1.00, y - 0.010, 0.090), (x * 1.12, y - 0.030, 0.034)]
        a.piece("patte_" + nom, A.tube(A.courbe(chemin, 5), 0.062, 16), CHARBON)
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.062, 0.090, 0.030), CHARBON, pos=(x * 1.14, y - 0.070, 0.030), rot=(0, 0, c * 14))
    a.piece("queue", A.boule(1.0, 24, 12).etire(0.044, 0.130, 0.044), CHARBON, pos=(0, 0.540, 0.150), rot=(-12, 0, 0))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("diable_de_tasmanie", styles.style_de("diable_de_tasmanie"), sys.modules[__name__]), "Diable de Tasmanie")
