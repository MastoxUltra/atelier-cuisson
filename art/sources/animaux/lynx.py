"""Le lynx en peluche, deuxième dessin : le grand chat des sapins, beige grisé moucheté de brun, les pinceaux noirs au bout des
oreilles, la collerette de favoris autour du visage, la queue-moignon au bout noir comme coupée net. Assis sur ses grosses
cuisses, une patte avant levée à demi (il va se lécher, ou frapper), l'autre plantée, le dos rond ; la tête tournée de trois
quarts, les yeux mi-clos, les oreilles dressées. Il a vu bouger quelque chose dans la neige, et déjà décidé que ce n'était pas
pour lui.

    python lynx.py        fabrique la fiche art/apercus/animaux/lynx.png (style du palier : B, peluche de magasin)
    (le premier dessin, jugé le 15/10 : « des pattes en bâtons, blocs »)
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

BEIGE = np.array(M.hexa("#bda48a"))           # la dominante (registre : beige grisé)
BRUN = np.array(M.hexa("#7a5e48"))            # les mouchetures
CREME = np.array(M.hexa("#efe6d4"))           # la poitrine, le ventre, le museau
NOIR = np.array(M.hexa("#1e1a18"))            # les pinceaux, le bout de la queue
NEZ = M.hexa("#c07a78")
FIL = M.hexa("#3a2c24")
H = Vector((0.0, -0.040, 0.700))


def construire():
    a = K.Animal("lynx")
    a.taille = 1.05

    # ----- le corps : assis, le dos rond, la poitrine claire et mouchetée, la panse sur les cuisses -----
    pc = A.profil([(0, 0.0), (0.100, 0.012), (0.178, 0.090), (0.198, 0.210), (0.182, 0.330), (0.140, 0.430), (0.092, 0.500), (0.040, 0.540), (0, 0.555)], 6)
    corps = A.tour(pc, 56)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(BEIGE, (len(ang), 1))
    t[(ang > 2.05) & (corps.v[:, 2] > 0.08)] = CREME
    t = O.moucheter(corps, BEIGE, BRUN, graine=14, nombre=140, taille=0.075, depart=t)
    corps.teinte = t

    def galbe(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 1] += 0.040 * np.exp(-((z - 0.38) / 0.12) ** 2) * (v[:, 1] > 0)              # le dos rond aux épaules
        s[:, 1] -= 0.035 * np.exp(-((z - 0.22) / 0.14) ** 2) * (v[:, 1] < 0)              # la panse
        return s
    a.piece("corps", corps.sculpte(galbe), None, mat=A.repere((0.0, 0.090, 0.090), (-10, 0, 0)))

    # ----- la tête : large et plate, tournée de trois quarts ; la collerette de favoris ; le museau court ; les yeux mi-clos -----
    RT = A.repere(H, (4, 0, 22))
    tete = A.boule(1.0, 52, 26)
    for c in (1, -1):
        tete.sculpte(lambda v, c=c: K.bosse(v, (c * 0.85, -0.50, -0.20), 0.18, 0.28))     # les joues
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(BEIGE, (len(u), 1))
    t[(u[:, 1] < -0.30) & (u[:, 2] < 0.05)] = CREME
    tete.teinte = t
    a.piece("tete", tete.etire(0.112, 0.098, 0.094), None, mat=RT)
    museau = A.boule(1.0, 32, 16).etire(0.054, 0.052, 0.040)
    a.piece("museau", O.teinte(museau, CREME), None, mat=RT @ A.repere((0.0, -0.088, -0.030)))
    a.piece("nez", A.boule(1.0, 14, 8).etire(0.017, 0.013, 0.012), NEZ, mat=RT @ A.repere((0.0, -0.136, -0.022)), poil=False)
    O.paire_yeux(a, "tete", H, (0.60, -0.76, 0.18), 0.0185, couleur_lourde=tuple(BEIGE), coupe=0.60, decolle=0.003, R=RT)
    for nom, c in (("G", 1), ("D", -1)):
        for k in range(5):
            ang_ = math.radians(-70 + 35 * k)
            fav = O.pointe(0.066, 0.013, 8)
            d = Vector((c * (0.30 + 0.5 * abs(math.sin(ang_))), -0.15, -0.65 + 0.35 * math.cos(ang_))).normalized()
            a.piece("favori_%s%d" % (nom, k), O.couche(O.teinte(fav, CREME * 0.95), RT @ A.cadre(Vector((c * 0.094, -0.020, -0.050 + 0.026 * k)), d, (0, 0, 1))),
                    None, poil=False)
        ore = A.tour(A.profil([(0.060, 0), (0.054, 0.030), (0.034, 0.068), (0.013, 0.096), (0, 0.106)], 4), 20).etire(1.0, 0.40, 1.0)      # des oreilles triangulaires, plus des oreilles de lapin
        a.piece("oreille_" + nom, O.couche(O.teinte(ore, BEIGE * 0.96), RT @ A.cadre(Vector((c * 0.074, 0.016, 0.078)), (c * 0.15, 0.10, 1.0), (0, 1, 0))), None)
        pinc = O.tube_r([(0, 0, 0), (c * 0.005, 0.002, 0.060), (c * 0.012, 0.002, 0.086)], [0.012, 0.020, 0.007], 10)               # de vrais pinceaux, bien longs
        a.piece("pinceau_" + nom, O.couche(O.teinte(pinc, NOIR), RT @ A.cadre(Vector((c * 0.084, 0.026, 0.198)), (c * 0.10, 0.05, 1.0), (0, 1, 0))), None, poil=False)
    O.broder(a, "bouche", "museau", RT @ Vector((0, -0.088, -0.030)), [(0.50 * u_, -0.82, -0.36 + 0.10 * u_ * u_) for u_ in np.linspace(-1, 1, 7)], 0.0021, FIL, R=RT)
    a.tete = H + Vector((0.0, -0.14, 0.0))

    # ----- les pattes : l'antérieur droit planté, genou marqué ; le gauche levé, le coude plié, la patte en l'air ; les cuisses
    #       de derrière, grosses, posées ; la queue-moignon -----
    for c in (1, -1):                                                             # les épaules : deux grosses masses, les jambes y plongent
        ep = A.boule(1.0, 28, 14).etire(0.088, 0.115, 0.115)
        a.piece("epaule_" + ("G" if c > 0 else "D"), O.teinte(ep, BEIGE), None, pos=(c * 0.118, -0.070, 0.400))
    O.jambe(a, "avant_D", (-0.100, -0.090, 0.440), (-0.092, -0.175, 0.050), 0.078, BEIGE, bas=CREME, sorte="av", plie=0.030,
            pied_dim=(0.056, 0.080, 0.028), griffes=0)
    levee = O.points_jambe((0.100, -0.090, 0.440), (0.100, -0.270, 0.250), "av", 0.07)
    a.piece("patte_avant_G", O.membre(levee, [0.078 * k for k in O.RAYONS_AV], [(0.60, tuple(BEIGE)), (1.0, tuple(CREME))], 22), None)
    a.piece("pied_avant_G", O.teinte(A.boule(1.0, 24, 12).etire(0.052, 0.074, 0.030), CREME * 0.95), None,
            pos=(0.095, -0.282, 0.240), rot=(-20, 0, 0), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        cuisse = A.boule(1.0, 36, 18).etire(0.095, 0.165, 0.125)
        a.piece("cuisse_" + nom, O.teinte(cuisse, BEIGE), None, pos=(c * 0.150, 0.130, 0.140), rot=(10, 0, c * 6))
        pd = A.boule(1.0, 28, 12).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.052, 0.125, 0.028)
        a.piece("pied_arriere_" + nom, O.teinte(pd, CREME * 0.92), None, pos=(c * 0.135, -0.040, 0.030), poil=False)
    queue = K.tube_peint(A.courbe([(0.0, 0.300, 0.080), (0.0, 0.390, 0.050), (0.040, 0.440, 0.054)], 5),
                         lambda t_: 0.056 - 0.006 * t_, [(0.55, BEIGE), (1.0, NOIR)], 14)
    a.piece("queue", queue, None)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lynx", styles.style_de("lynx"), sys.modules[__name__]), "Lynx")
