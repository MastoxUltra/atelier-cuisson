"""La taupe à nez étoilé en peluche : la petite brune de velours noir des galeries, trapue comme un rouleau, de grosses mains
roses en pelle brandies devant elle, pas d'oreilles, deux grains pour yeux, et au bout du museau l'étoile : vingt-deux
petits doigts roses qui rayonnent et tâtent tout ce qui passe, plus vite que l'œil ne voit. Elle trouve son repas en moins
d'une demi-seconde. Elle ne le regarde même pas : elle a le nez qui voit.

    python taupe_a_nez_etoile.py        fabrique la fiche art/apercus/animaux/taupe_a_nez_etoile.png (style du palier : C, velours ras)
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

VELOURS = np.array(M.hexa("#4a3d39"))         # la dominante (registre : brun noir velours #3a2f2c), un cran plus clair pour la lecture
DESSOUS = np.array(M.hexa("#5e504a"))         # le ventre
ROSE = np.array(M.hexa("#f0a0aa"))            # l'accent : l'étoile, les mains, les pieds, la queue
GRIFFE = np.array(M.hexa("#f2e6d6"))
NEZ = M.hexa("#241a18")
H = Vector((0.0, -0.480, 0.200))              # le centre de la tête


def construire():
    a = K.Animal("taupe_a_nez_etoile")
    a.taille = 0.40

    # ----- le corps : un rouleau trapu, les épaules fortes, le dos rond ; un cou presque nul -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(VELOURS, (len(ang), 1))
        t[ang > 2.2] = DESSOUS
        return t
    rayon = O.interp([(0.0, 0.0), (0.05, 0.075), (0.20, 0.125), (0.50, 0.150), (0.78, 0.148), (0.93, 0.118), (1.0, 0.075)])
    O.corps_h(a, "corps", (0.0, 0.34, 0.150), 0.74, rayon, peint, None, cotes=48, pitch=-3.0,
              deforme=O.gabarit(poitrail=0.12, taille=0.0, croupe=0.10, garrot=0.12, ventre=0.0))

    # ----- la tête : un cône court qui se prolonge en groin ; les yeux grains de poivre ; l'étoile rose au bout -----
    RT = A.repere(H, (6, 0, 12))
    tete = A.boule(1.0, 40, 20)
    tete.teinte = np.tile(VELOURS, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.088, 0.118, 0.076), None, mat=RT)
    groin = A.boule(1.0, 28, 14).etire(0.044, 0.060, 0.040)
    a.piece("groin", O.teinte(groin, VELOURS * 0.96), None, mat=RT @ A.repere((0.0, -0.140, -0.010)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.030, 0.022, 0.028), tuple(ROSE * 0.95), mat=RT @ A.repere((0.0, -0.200, -0.008)), poil=False)
    etoile = None
    for k in range(22):
        th = 2.0 * math.pi * k / 22
        dire = Vector((math.cos(th) * 0.95, -0.55, math.sin(th) * 0.95)).normalized()
        pos = Vector((0.0, -0.205, -0.008)) + Vector((math.cos(th) * 0.026, 0.0, math.sin(th) * 0.026))
        d = O.couche(O.teinte(O.pointe(0.040, 0.0070, 8), ROSE), RT @ A.cadre(pos, dire, (0, 1, 0)))
        etoile = d if etoile is None else etoile + d
    a.piece("etoile", etoile, None, poil=False)
    O.paire_yeux(a, "tete", H, (0.74, -0.52, 0.20), 0.0085, decolle=0.001)

    # ----- les mains : de grosses pelles roses brandies devant, les cinq griffes claires dehors ; l'arrière : petits pieds roses -----
    for nom, c in (("G", 1), ("D", -1)):
        bras = O.tube_r([(c * 0.130, -0.150, 0.230), (c * 0.185, -0.250, 0.200), (c * 0.170, -0.350, 0.205)], [0.080, 0.062, 0.050], 18)
        a.piece("bras_" + nom, O.teinte(bras, VELOURS), None)
        pelle = A.boule(1.0, 28, 14).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.082, 0.016, 0.056)
        a.piece("main_" + nom, O.teinte(pelle, ROSE), None, mat=A.repere((c * 0.178, -0.392, 0.210), (0, 0, c * -8)), poil=False)
        for k, dx in enumerate((-0.062, -0.031, 0.0, 0.031, 0.062)):
            g = O.couche(O.teinte(O.griffe(0.044, 0.0100), GRIFFE),
                         A.cadre(Vector((c * 0.178 + dx * 0.95, -0.428, 0.206)), Vector((dx * c * 0.9, -1.0, 0.0)), (0, 0, 1)))
            a.piece("griffe_%s%d" % (nom, k), g, None, poil=False)
        cuisse = O.tube_r([(c * 0.120, 0.470, 0.170), (c * 0.140, 0.500, 0.100), (c * 0.135, 0.470, 0.040)], [0.085, 0.062, 0.042], 16)
        a.piece("cuisse_" + nom, O.teinte(cuisse, VELOURS), None)
        pied = A.boule(1.0, 24, 12).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.040, 0.066, 0.016)
        a.piece("pied_" + nom, O.teinte(pied, ROSE), None, pos=(c * 0.135, 0.430, 0.017), rot=(0, 0, c * -10), poil=False)
    # ----- la queue : courte et grasse, rose, épaisse en son milieu -----
    queue = K.tube_peint(A.courbe([(0.0, 0.690, 0.150), (0.0, 0.780, 0.130), (0.020, 0.840, 0.100)], 5),
                         lambda t_: 0.034 + 0.014 * math.sin(math.pi * min(t_ * 1.1, 1.0)), [(1.0, tuple(ROSE * 0.96))], 14)
    a.piece("queue", queue, None)
    a.tete = H + Vector((0.0, -0.20, 0.0))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("taupe_a_nez_etoile", styles.style_de("taupe_a_nez_etoile"), sys.modules[__name__]), "Taupe à nez étoilé")
