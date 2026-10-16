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


TOURNE = 25                                   # la fiche tourne la bête vers la caméra (25° devant) : on compte les DEUX yeux ; 0 pour le jeu


def construire():
    a = K.Animal("taupe_a_nez_etoile")
    a.taille = 0.58                                # plus gros : il se noyait dans l'herbe (« flou »)

    # ----- le corps : un rouleau trapu, les épaules fortes, le dos rond ; un cou presque nul -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(VELOURS, (len(ang), 1))
        t[ang > 2.2] = DESSOUS
        return t
    rayon = O.interp([(0.0, 0.0), (0.05, 0.075), (0.20, 0.125), (0.50, 0.150), (0.78, 0.148), (0.93, 0.118), (1.0, 0.075)])
    # (16/10, planche 27) : un corps CYLINDRIQUE, sans épaules ni croupe sculptées (il faisait une patate bosselée)
    O.corps_h(a, "corps", (0.0, 0.34, 0.150), 0.74, rayon, peint, None, cotes=48, pitch=-3.0,
              deforme=O.gabarit(poitrail=0.0, taille=0.0, croupe=0.0, garrot=0.0, ventre=0.0))

    # ----- la tête : un cône court qui se prolonge en groin ; les yeux grains de poivre ; l'étoile rose au bout -----
    RT = A.repere(H, (6, 0, 12))
    tete = A.boule(1.0, 40, 20)
    tete.teinte = np.tile(VELOURS, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.088, 0.118, 0.076), None, mat=RT)
    groin = A.boule(1.0, 28, 14).etire(0.044, 0.060, 0.040)
    a.piece("groin", O.teinte(groin, VELOURS * 0.96), None, mat=RT @ A.repere((0.0, -0.140, -0.010)))
    # l'étoile (16/10, planche 27 : une scie plate, illisible) : au bout du groin, un disque rose et ses deux narines, et
    # autour, en couronne, VINGT-DEUX doigts charnus au bout rond (onze de chaque côté, les deux du bas plus courts), qui
    # rayonnent et pointent un peu vers l'avant ; gardés à part (fondus, ils faisaient un disque)
    a.piece("nez", A.boule(1.0, 24, 12).etire(0.030, 0.014, 0.030), tuple(ROSE * 0.95), mat=RT @ A.repere((0.0, -0.200, -0.008)), poil=False)
    for nom_n, c in (("G", 1), ("D", -1)):
        a.piece("narine_" + nom_n, A.boule(1.0, 12, 6).etire(0.0060, 0.0040, 0.0085), NEZ, mat=RT @ A.repere((c * 0.0105, -0.2135, -0.006)), poil=False)
    doigt = A.tour(A.profil([(0.0068, 0.0), (0.0066, 0.012), (0.0060, 0.024), (0.0044, 0.032), (0.0, 0.0365)], 4), 12)
    etoile = None
    for k in range(22):
        th = 2.0 * math.pi * (k + 0.5) / 22 - math.pi / 2                     # le bas : th = -90 degrés, entre deux doigts
        bas = abs(math.sin(th) + 1.0) < 0.12                                  # les deux doigts du bas, plus courts
        dire = Vector((math.cos(th), -0.42, math.sin(th))).normalized()
        pos = Vector((0.0, -0.204, -0.008)) + Vector((math.cos(th) * 0.024, 0.0, math.sin(th) * 0.024))
        d = O.teinte(doigt.copie().etire(1.0, 1.0, 0.70 if bas else 1.0), ROSE)
        d = O.couche(d, RT @ A.cadre(pos, dire, (0, 1, 0)))
        etoile = d if etoile is None else etoile + d
    a.piece("etoile", etoile, None, poil=False)
    a.fusion_a_part = ("etoile", "narine", "main", "griffe")
    O.paire_yeux(a, "tete", H, (0.60, -0.72, 0.26), 0.0165, decolle=0.002, R=RT)

    # ----- les mains : de grosses pelles roses brandies devant, les cinq griffes claires dehors ; l'arrière : petits pieds roses -----
    for nom, c in (("G", 1), ("D", -1)):
        # (16/10, planche 27) : les mains en PELLES sont en bas, de chaque côté de la poitrine, la paume tournée vers
        # l'extérieur et vers l'arrière, comme pour creuser (levées à hauteur d'épaule, elles faisaient des ailes)
        bras = O.tube_r([(c * 0.110, -0.160, 0.170), (c * 0.165, -0.250, 0.110), (c * 0.190, -0.310, 0.075)], [0.072, 0.058, 0.046], 18)
        a.piece("bras_" + nom, O.teinte(bras, VELOURS), None)
        paume = Vector((c * 0.85, 0.30, -0.10)).normalized()                       # la paume regarde dehors et un peu derrière
        P_ = A.cadre(Vector((c * 0.205, -0.335, 0.062)), paume, (0, 0, 1))
        pelle = A.boule(1.0, 28, 14).sculpte(lambda v: K.emousse(v, 0.75)).etire(0.060, 0.072, 0.017)   # large et haute, plate
        a.piece("main_" + nom, O.teinte(pelle, ROSE), None, mat=P_, poil=False)
        for k, dz in enumerate((-0.044, -0.022, 0.0, 0.022, 0.044)):
            base_g = P_ @ Vector((c * -0.050, dz, 0.0))                              # sur le bord de devant de la pelle
            g = O.couche(O.teinte(O.griffe(0.040, 0.0095), GRIFFE),
                         A.cadre(base_g, Vector((c * 0.25, -1.0, -0.10 + dz * 1.5)), (0, 0, 1)))
            a.piece("griffe_%s%d" % (nom, k), g, None, poil=False)
        cuisse = O.tube_r([(c * 0.120, 0.320, 0.170), (c * 0.140, 0.350, 0.100), (c * 0.135, 0.320, 0.040)], [0.085, 0.062, 0.042], 16)
        a.piece("cuisse_" + nom, O.teinte(cuisse, VELOURS), None)
        pied = A.boule(1.0, 24, 12).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.040, 0.066, 0.016)
        a.piece("pied_" + nom, O.teinte(pied, ROSE), None, pos=(c * 0.135, 0.280, 0.017), rot=(0, 0, c * -10), poil=False)
    # ----- la queue : fine, du velours du corps, un peu courbée (16/10 : grasse et rose, elle faisait une saucisse) -----
    queue = K.tube_peint(A.courbe([(0.0, 0.390, 0.140), (0.0, 0.470, 0.115), (0.022, 0.540, 0.090), (0.040, 0.590, 0.080)], 5),
                         lambda t_: 0.016 - 0.007 * t_, [(1.0, tuple(VELOURS * 0.92))], 12)
    a.piece("queue", queue, None)
    a.tete = H + Vector((0.0, -0.20, 0.0))
    if TOURNE:
        O.tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("taupe_a_nez_etoile", styles.style_de("taupe_a_nez_etoile"), sys.modules[__name__]), "Taupe à nez étoilé")
