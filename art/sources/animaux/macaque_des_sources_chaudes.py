"""Le macaque des sources chaudes en peluche, deuxième dessin : le singe des neiges au bain. Une fourrure épaisse et
hirsute en mèches de gris brume, plus épaisse encore aux épaules et autour de la face ; la face nue rose rouge, plate et
ronde, le front bas sous les mèches, deux petits yeux mi-clos, un sourire de félicité. Assis dans l'eau chaude comme on
s'assoit dans un bon fauteuil : les épaules rentrées, les mains posées sur les genoux, une calotte de neige sur la tête
(de la feutrine blanche, c'est la neige, rien d'autre). Rien ne le fera sortir de là.

    python macaque_des_sources_chaudes.py        fabrique la fiche art/apercus/animaux/macaque_des_sources_chaudes.png
                                                (style du palier : B, peluche de magasin)
    (le premier dessin, jugé le 15/10 : « le corps en œuf aux bras-tuyaux et la face de masque de cochon »)
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

BRUME = np.array(M.hexa("#aaa29b"))           # la dominante (registre : gris brume #a59d96), un cran plus clair (style B)
PALE = np.array(M.hexa("#cdc6bd"))            # le ventre, la collerette de la face
SOMBRE = np.array(M.hexa("#8d857f"))          # les mèches du dos
ROSE = np.array(M.hexa("#e2736a"))            # l'accent : la face nue rose rouge
CHAIR = np.array(M.hexa("#c9857d"))           # les mains, les pieds, les oreilles
NEIGE = np.array(M.hexa("#f4f6f8"))           # la calotte de neige
NEZ = M.hexa("#2a1a18")
FIL = M.hexa("#4a2420")
H = Vector((0.0, -0.040, 0.600))              # le centre de la tête, enfoncée dans les épaules


def meche(pos, direction, long, ray, couleur):
    """Une mèche de poil : un petit cône mou posé sur la peau, la pointe vers `direction`."""
    d = Vector(direction).normalized()
    haut = Vector((0.0, 0.0, 1.0)) if abs(d.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    return O.couche(O.teinte(O.pointe(long, ray, 8), couleur), A.cadre(Vector(pos), d, haut))


def construire():
    a = K.Animal("macaque_des_sources_chaudes")
    a.taille = 0.78

    # ----- le corps : assis bas, le dos rond, les épaules rentrées ; le ventre plus clair ; des mèches sur le dos et les flancs -----
    pc = A.profil([(0, 0.0), (0.140, 0.012), (0.220, 0.090), (0.245, 0.220), (0.228, 0.340), (0.180, 0.430), (0.110, 0.490), (0, 0.520)], 6)
    corps = A.tour(pc, 56)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    z = corps.v[:, 2]
    t = np.tile(BRUME, (len(ang), 1))
    t[(ang > 2.05) & (z > 0.10)] = PALE
    t[(ang < 0.95) & (z > 0.20)] = SOMBRE * 0.5 + BRUME * 0.5                         # la selle du dos, plus sombre
    corps.teinte = t

    def galbe(v):
        s = v.copy()
        s[:, 1] += 0.070 * np.exp(-((v[:, 2] - 0.40) / 0.12) ** 2) * (v[:, 1] > 0)       # le dos rond, les épaules rentrées
        s[:, 1] -= 0.035 * np.exp(-((v[:, 2] - 0.20) / 0.14) ** 2) * (v[:, 1] < 0)       # la panse
        return s
    RC = A.repere((0.0, 0.070, 0.026), (-14, 0, 0))
    a.piece("corps", corps.sculpte(galbe), None, mat=RC)
    rng = np.random.default_rng(31)
    meches = None
    for k in range(110):
        an = rng.uniform(-math.pi * 0.95, math.pi * 0.95)                                 # autour du corps (0 : sur le dos)
        zz = rng.uniform(0.08, 0.48)
        r = float(np.interp(zz, [0.0, 0.09, 0.22, 0.34, 0.43, 0.49], [0.14, 0.22, 0.245, 0.228, 0.18, 0.11]))
        x, y = r * math.sin(an), r * math.cos(an)
        if abs(an) > 2.0:                                                                 # pas sur le ventre
            continue
        n = Vector((math.sin(an), math.cos(an), 0.0))
        d = n * 0.75 + Vector((0.0, 0.0, -0.55 if zz > 0.15 else 0.1))
        bos = 0.070 * math.exp(-((zz - 0.40) / 0.12) ** 2) if y > 0 else 0.0
        pos = RC @ Vector((x * 0.97, y * 0.97 + bos, zz))
        d = RC.to_3x3() @ d
        m = meche(pos, d, rng.uniform(0.036, 0.058), 0.026, BRUME if k % 3 else PALE * 0.96)
        meches = m if meches is None else meches + m
    a.piece("meches", meches, None, poil=False)

    # ----- la tête : large et plate, le front bas ; la face nue ronde et plate, entourée de mèches ; la calotte de neige -----
    RT = A.repere(H, (8, 0, 14))                                                       # le menton rentré, un peu de côté
    tete = A.boule(1.0, 52, 26)
    for c in (1, -1):
        tete.sculpte(lambda v, c=c: K.bosse(v, (c * 0.85, -0.40, -0.25), 0.22, 0.24))
    tete.sculpte(lambda v: np.stack([v[:, 0], np.where(v[:, 1] < 0, v[:, 1] * (1.0 - 0.18 * np.exp(-(v[:, 0] / 0.7) ** 2 - ((v[:, 2] + 0.05) / 0.7) ** 2)), v[:, 1]),
                                     v[:, 2]], axis=1))                              # la face aplatie
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(BRUME, (len(u), 1))
    t[(u[:, 1] < -0.10) & ((u[:, 0] / 0.92) ** 2 + ((u[:, 2] + 0.04) / 0.78) ** 2 < 1.0)] = PALE                 # le cadre de poils clairs
    t[(u[:, 1] < -0.36) & ((u[:, 0] / 0.66) ** 2 + ((u[:, 2] + 0.06) / 0.56) ** 2 < 1.0)] = ROSE                  # la face nue : un disque
    t[(u[:, 2] > 0.38) & (u[:, 1] < -0.10) & (np.abs(u[:, 0]) < 0.8)] = BRUME * 0.94                              # le front bas, sous les mèches
    tete.teinte = t
    a.piece("tete", tete.etire(0.124, 0.106, 0.110), None, mat=RT)
    a.piece("nez", A.boule(1.0, 14, 8).etire(0.024, 0.010, 0.014), tuple(CHAIR * 0.80), mat=RT @ A.repere((0.0, -0.103, -0.026)), poil=False)
    for c in (1, -1):
        a.piece("narine_%d" % c, A.boule(1.0, 10, 6).etire(0.0065, 0.004, 0.006), NEZ, mat=RT @ A.repere((c * 0.0105, -0.1105, -0.027)), poil=False)
    O.paire_yeux(a, "tete", H, (0.34, -0.90, 0.10), 0.0135, couleur_lourde=tuple(ROSE * 0.93), coupe=-0.10, decolle=0.002)
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.boule(1.0, 22, 12).etire(0.034, 0.014, 0.032)
        a.piece("oreille_" + nom, O.teinte(ore, CHAIR), None, mat=RT @ A.repere((c * 0.122, 0.018, 0.006)), poil=False)
    # la collerette : de longues mèches claires autour du disque rouge, qui retombent sur les joues et sur le menton
    colle = None
    for k in range(30):
        an = -math.pi * 0.20 + math.pi * 1.40 * k / 29                                   # de la joue droite, par le menton, à la joue gauche
        cx, cz = 0.098 * math.cos(an + math.pi), 0.092 * math.sin(an + math.pi)
        p = RT @ Vector((cx, -0.062 - 0.030 * math.cos(an * 1.5) ** 2, cz - 0.018))
        d = Vector((cx * 5.0, -0.35, cz * 3.0 - 0.45 if cz < 0 else cz * 2.0)).normalized()
        m = meche(p, RT.to_3x3() @ d, 0.044 + 0.010 * (k % 3), 0.0210, PALE * 0.98)
        colle = m if colle is None else colle + m
    a.piece("collerette", colle, None, poil=False)
    # le front : des mèches grises qui tombent sur le haut de la face
    front = None
    for k in range(9):
        x = -0.074 + 0.0185 * k
        p = RT @ Vector((x, -0.080 + 0.005 * abs(k - 4), 0.052 + 0.010 * math.cos(k)))
        d = Vector((x * 1.5, -0.45, -0.85)).normalized()
        m = meche(p, RT.to_3x3() @ d, 0.040, 0.0190, BRUME * 0.96)
        front = m if front is None else front + m
    a.piece("front", front, None, poil=False)
    neige = A.boule(1.0, 28, 14).etire(0.084, 0.076, 0.034)
    a.piece("neige", O.teinte(neige, NEIGE), None, mat=RT @ A.repere((0.0, 0.004, 0.092), (-8, 0, 0)))
    bouche = [tuple(RT @ Vector((0.050 * u_, -0.092 - 0.010 * (1 - u_ * u_), -0.058 + 0.020 * u_ * u_))) for u_ in np.linspace(-1, 1, 7)]
    a.broderie("bouche", A.courbe(bouche, 3), 0.0022, FIL)
    a.tete = H + Vector((0.0, -0.17, 0.0))

    # ----- les bras : tombent des épaules rentrées, les mains posées sur les genoux ; les jambes pliées, les genoux remontés -----
    for nom, c in (("G", 1), ("D", -1)):
        epaule = A.boule(1.0, 24, 12).etire(0.110, 0.110, 0.115)
        a.piece("epaule_" + nom, O.teinte(epaule, BRUME), None, pos=(c * 0.190, 0.020, 0.430))
        bras = O.tube_r([(c * 0.190, 0.020, 0.420), (c * 0.238, -0.070, 0.330), (c * 0.205, -0.190, 0.292)], [0.100, 0.080, 0.056], 20)
        bras = bras + A.boule(1.0, 16, 8).etire(0.056, 0.056, 0.056).pose((c * 0.205, -0.190, 0.292))
        a.piece("bras_" + nom, O.teinte(bras, BRUME), None)
        main = A.boule(1.0, 24, 12).etire(0.050, 0.056, 0.028)
        a.piece("main_" + nom, O.teinte(main, CHAIR), None, pos=(c * 0.205, -0.232, 0.298), rot=(10, 0, c * -8), poil=False)
        cuisse = O.tube_r([(c * 0.160, 0.060, 0.125), (c * 0.215, -0.140, 0.230), (c * 0.155, -0.318, 0.066)], [0.125, 0.102, 0.062], 22)
        cuisse = cuisse + A.boule(1.0, 16, 8).etire(0.062, 0.062, 0.062).pose((c * 0.155, -0.318, 0.066))
        a.piece("jambe_" + nom, O.teinte(cuisse, BRUME), None)
        pied = A.boule(1.0, 28, 12).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.054, 0.084, 0.028)
        a.piece("pied_" + nom, O.teinte(pied, CHAIR), None, pos=(c * 0.156, -0.372, 0.030), rot=(0, 0, c * -10), poil=False)

    # ----- le moignon de queue, derrière -----
    a.piece("queue", O.teinte(A.boule(1.0, 16, 8).etire(0.034, 0.042, 0.032), BRUME), None, pos=(0.0, 0.290, 0.075))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("macaque_des_sources_chaudes", styles.style_de("macaque_des_sources_chaudes"), sys.modules[__name__]), "Macaque des sources chaudes")
