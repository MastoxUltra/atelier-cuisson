"""L'ours en peluche, troisième dessin : l'ours brun adulte des sapins, debout sur ses pattes de derrière, noisette cendré,
les jambes et les bras plus sombres. Les cinq traits de l'ours brun (trois photos de l'espèce, 15/10) : une masse
trapue, la poitrine profonde et une bosse de muscle au-dessus des épaules ; une tête large et ronde, les bajoues
pleines, les petites oreilles rondes plantées loin l'une de l'autre sur les coins du crâne ; un museau moyen, large,
plus clair, au gros nez noir ; de petits yeux rapprochés, calmes ; des membres épais qui finissent en larges pattes à
griffes pâles. Debout, un bras levé de côté comme pour saluer (il ne cache plus la tête), l'autre qui pend devant le
ventre. Bouche fermée : un trait cousu, pas de crocs (le contrôleur voyait des crocs détachés).

    python ours.py        fabrique la fiche art/apercus/animaux/ours.png (style du palier : B, peluche de magasin)
    (1er dessin : « le nounours de supermarché » ; 2e : « très géométrique » ; 3e : volumes de la marmotte gardée —
    poire bombée, bajoues, pattes en mitaines et orteils, plus aucun cylindre à bout coupé ; base gonflée de l'Artiste)
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
import garnitures as G
import matieres as M
import peluche as K
import outils_a as O

GONFLAGE = True                               # la base aux volumes de l'Artiste (fusion + gonflage), validée le 15/10

NOISETTE = np.array(M.hexa("#7a5c46"))        # la dominante (registre : brun noisette cendré #6e5846), un peu plus chaud (style B)
CLAIR = np.array(M.hexa("#a88c70"))           # le museau, le ventre, le givre de la bosse
SOMBRE = np.array(M.hexa("#5a4435"))          # les bras, les jambes
GRIFFE = M.hexa("#e8dcc4")
NEZ = M.hexa("#16110e")
FIL = M.hexa("#2a1c14")

CORPS = Vector((0.0, 0.040, 0.100))
TETE = Vector((0.0, -0.165, 0.905))


def gauss(x):
    return np.exp(-x * x)


def mitaine(long, large, haut):
    """Une patte : une boule bombée au bout franc (jamais un cylindre), longue sur Z."""
    return A.boule(1.0, 28, 14).sculpte(lambda v: K.emousse(v, 0.86)).etire(large, haut, long)


def construire():
    a = K.Animal("ours")
    a.taille = 2.50

    # ----- le corps : une poire bombée et dressée, les épaules larges, la bosse entre elles, le ventre rond ; le ventre clair -----
    pc = A.profil([(0, 0.0), (0.125, 0.010), (0.222, 0.080), (0.262, 0.200), (0.276, 0.340), (0.284, 0.470), (0.258, 0.590),
                   (0.190, 0.672), (0.100, 0.716), (0, 0.738)], 6)
    corps = A.tour(pc, 48)
    G.sillons(corps, [12], 0.004, 1.1)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    z = corps.v[:, 2]
    t = np.tile(NOISETTE, (len(ang), 1))
    t[(ang > 2.25) & (z > 0.10) & (z < 0.60)] = CLAIR * 0.92                          # le ventre
    t[(ang < 1.0) & (z > 0.50)] = NOISETTE * 0.60 + CLAIR * 0.40                      # le dos givré
    t[z < 0.12] = SOMBRE
    corps.teinte = t

    def campe(v):
        s = v.copy()
        zz = v[:, 2]
        dos = v[:, 1] > 0
        s[:, 1] += 0.095 * gauss((zz - 0.60) / 0.11) * dos                            # la bosse entre les épaules
        s[:, 2] += 0.040 * gauss((zz - 0.60) / 0.14) * dos
        s[:, 1] -= 0.055 * gauss((zz - 0.30) / 0.20) * (~dos)                         # le ventre rond
        s[:, 1] += 0.06 * zz                                                          # un peu renversé en arrière
        return s
    a.piece("corps", corps.sculpte(campe), None, pos=CORPS)

    # ----- la tête : large et ronde, les bajoues pleines, le front bas ; le dessous du visage plus clair -----
    RT = A.repere(TETE, (6, 0, -10))

    def crane(v):
        for c in (1, -1):
            v = K.bosse(v, (c * 0.9, -0.35, -0.30), 0.30, 0.34)                       # les bajoues
            v = K.bosse(v, (c * 0.45, -0.70, 0.40), 0.10, 0.18)                       # les arcades
        v = K.emousse(v, 0.90)
        return v * [0.170, 0.150, 0.140]
    tete = A.boule(1.0, 56, 28)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    tt = np.tile(NOISETTE, (len(u), 1))
    tt[(u[:, 2] < -0.30) & (u[:, 1] < 0.10)] = NOISETTE * 0.55 + CLAIR * 0.45          # les joues et le menton plus clairs
    tete.teinte = tt
    a.piece("tete", tete.sculpte(crane), None, mat=RT)
    a.tete = RT @ Vector((0.0, -0.20, -0.02))

    # ----- le museau : moyen, large, plus clair, le gros nez noir, la bouche fermée d'un trait cousu -----
    MZ = RT @ A.repere((0.0, -0.172, -0.044), (-6, 0, 0))
    museau = A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.80)).etire(0.084, 0.108, 0.068)
    museau.teinte = np.tile(CLAIR, (len(museau.v), 1))
    a.piece("museau", museau, None, mat=MZ)
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.040, 0.027, 0.030), NEZ, mat=RT @ A.repere((0.0, -0.274, -0.026)), poil=False)
    MZ3 = MZ.to_3x3()
    centre = MZ @ Vector((0.0, 0.0, 0.0))
    levre = [a.trace("museau", centre, [MZ3 @ Vector(d)])[0] for d in ((0, -0.95, 0.20), (0, -1.0, -0.20), (0, -0.85, -0.55))]
    a.broderie("levre", A.courbe(levre, 4), 0.0030, FIL)
    for nom, c in (("G", 1), ("D", -1)):
        bouche = [a.trace("museau", centre, [MZ3 @ Vector((c * x, -0.85, -0.55 + 0.20 * x))])[0] for x in (0.0, 0.30, 0.55, 0.75)]
        a.broderie("bouche_" + nom, A.courbe(bouche, 4), 0.0030, FIL)

    # ----- les yeux : petits, rapprochés, ouverts et pareils (la tête est tournée : R=RT) ; pas de paupière lourde -----
    O.paire_yeux(a, "tete", TETE, (0.58, -0.76, 0.20), 0.0165, decolle=0.002, R=RT)

    # ----- les oreilles : de petits bols ronds, loin l'un de l'autre sur les coins du crâne -----
    def coupe(v):
        s = v.copy()
        s[:, 2] += 1.5 * (v[:, 0] ** 2 + v[:, 1] ** 2)
        return s * [0.046, 0.044, 0.016]
    for nom, c in (("G", 1), ("D", -1)):
        E = RT @ A.cadre(Vector((c * 0.118, 0.026, 0.098)), (c * 0.42, -0.30, 0.85), (0, 0.2, 1.0))
        a.piece("oreille_" + nom, A.boule(1.0, 28, 14).sculpte(coupe), None, mat=E)

    # ----- les bras : épais en haut, en jambon, qui s'affinent au poignet et finissent en larges pattes à griffes -----
    haut = {"G": [(0.270, 0.020, 0.745), (0.400, 0.000, 0.800), (0.500, -0.070, 0.920), (0.550, -0.120, 1.020)],
            "D": [(-0.270, 0.020, 0.745), (-0.385, 0.000, 0.620), (-0.365, -0.110, 0.500), (-0.305, -0.200, 0.440)]}
    paw_dir = {"G": Vector((0.30, -0.35, 0.88)), "D": Vector((0.30, -0.80, -0.50))}
    for nom, c in (("G", 1), ("D", -1)):
        pts = haut[nom]
        rayons = [0.140, 0.128, 0.108, 0.092]
        bras = A.tube(A.courbe(pts, 6), lambda t_: float(np.interp(t_, np.linspace(0, 1, len(rayons)), rayons)), 22)
        bras.teinte = np.tile(SOMBRE, (len(bras.v), 1))
        a.piece("bras_" + nom, bras, None)
        d = paw_dir[nom].normalized()
        fin = Vector(pts[-1]) + d * 0.050
        patte = mitaine(0.115, 0.088, 0.075)
        patte.teinte = np.tile(SOMBRE * 0.88, (len(patte.v), 1))
        a.piece("main_" + nom, patte, None, mat=A.cadre(fin, d, (0, 0, 1)))
        side = d.cross(Vector((0, 0, 1))).normalized()
        for k, dx in enumerate((-0.040, -0.014, 0.014, 0.040)):
            g = O.couche(O.teinte(O.griffe(0.060, 0.0115), np.array(GRIFFE)),
                         A.cadre(fin + d * 0.100 + side * dx - Vector((0, 0, 0.004)), d + Vector((0, 0, -0.18)), (0, 0, 1)))
            a.piece("griffe_%s%d" % (nom, k), g, None, poil=False)

    # ----- les jambes : la cuisse en poire, le bas de jambe qui s'affine, le large pied plantigrade à orteils et griffes -----
    for nom, c in (("G", 1), ("D", -1)):
        cuisse = A.boule(1.0, 32, 16).sculpte(lambda v: K.emousse(v, 0.88)).etire(0.125, 0.150, 0.150)
        cuisse.teinte = np.tile(SOMBRE, (len(cuisse.v), 1))
        a.piece("cuisse_" + nom, cuisse, None, pos=(c * 0.185, 0.040, 0.275), rot=(10, 0, c * 6))
        pts = [(c * 0.195, 0.010, 0.250), (c * 0.200, -0.040, 0.150), (c * 0.198, -0.085, 0.075)]
        ray = [0.118, 0.098, 0.088]
        jambe = A.tube(A.courbe(pts, 6), lambda t_: float(np.interp(t_, np.linspace(0, 1, len(ray)), ray)), 22)
        jambe.teinte = np.tile(SOMBRE, (len(jambe.v), 1))
        a.piece("jambe_" + nom, jambe, None)
        pied = A.boule(1.0, 32, 16).sculpte(lambda v: K.emousse(v, 0.86)).etire(0.100, 0.185, 0.050)
        pied.teinte = np.tile(SOMBRE * 0.85, (len(pied.v), 1))
        a.piece("pied_" + nom, pied, None, pos=(c * 0.198, -0.140, 0.050), rot=(0, 0, c * -8), poil=False)
        for k, dx in enumerate((-0.062, -0.031, 0.0, 0.031, 0.062)):
            xx = c * 0.198 + dx
            yy = -0.318 - 0.008 * (2 - abs(k - 2))
            orteil = A.boule(1.0, 16, 8).etire(0.0285, 0.030, 0.030)
            orteil.teinte = np.tile(SOMBRE * 0.82, (len(orteil.v), 1))
            a.piece("orteil_%s%d" % (nom, k), orteil, None, pos=(xx, yy, 0.032), poil=False)
            g = O.couche(O.teinte(O.griffe(0.046, 0.0105), np.array(GRIFFE)), A.cadre(Vector((xx, yy - 0.020, 0.030)), (0.0, -1.0, -0.12), (0, 0, 1)))
            a.piece("griffe_pied_%s%d" % (nom, k), g, None, poil=False)

    # ----- la queue : un moignon rond derrière -----
    queue = A.boule(1.0, 20, 10).sculpte(lambda v: K.emousse(v, 0.9)).etire(0.060, 0.062, 0.058)
    queue.teinte = np.tile(NOISETTE, (len(queue.v), 1))
    a.piece("queue", queue, None, pos=(0.0, 0.340, 0.250))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("ours", styles.style_de("ours"), sys.modules[__name__]), "Ours")
