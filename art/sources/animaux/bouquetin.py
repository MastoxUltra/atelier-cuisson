"""Le bouquetin en peluche, troisième dessin : le roi de la crête, bâti avec les volumes de la chèvre gardée par l'auteur.
Les cinq traits du bouquetin des Alpes (trois photos, 15/10) : un corps trapu et puissant, le cou épais, le poitrail
profond, les pattes courtes et fortes aux gros sabots ; une tête courte au nez busqué, la barbiche brune, de petites
oreilles ; et SURTOUT les deux cornes, très grosses, qui montent et se couchent en grand arc vers l'arrière, rayées de
nœuds en travers ; une robe gris lavande (registre), le ventre pâle, le poitrail et le devant des pattes chocolat.
Campé sur ses quatre pattes, la tête haute et un peu tournée : il toise la vallée.

    python bouquetin.py        fabrique la fiche art/apercus/animaux/bouquetin.png (style du palier : C, velours ras)
    (1er dessin : « maigre, sur des pattes en bâtons » ; 2e : « corps en blocs anguleux, cornes en bananes lisses »)
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

PIERRE = np.array(M.hexa("#9b8ba9"))          # la dominante (registre : gris lavande, pierre bleutée), un peu soutenue (velours)
PALE = np.array(M.hexa("#e2dbe6"))            # le ventre, l'arrière des cuisses
CHOCO = np.array(M.hexa("#3f2f30"))           # le plastron, les chaussettes, la barbiche
IVOIRE = np.array(M.hexa("#f1e6c8"))          # l'accent : les cornes
SABOT = M.hexa("#2a2324")
FIL = M.hexa("#2a1f20")

CROUPE = Vector((0.0, 0.300, 0.520))          # le bout arrière du corps (une pièce tournée, couchée vers l'avant)
TETE = Vector((0.02, -0.500, 0.960))
NARGUE = A.repere(TETE, (-4, 6, 14))          # la tête haute, un peu tournée : il toise


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y, haut = +z), rendue dans celui du jardin."""
    return NARGUE.to_3x3() @ Vector((x, y, z))


def gauss(x):
    return np.exp(-np.asarray(x) ** 2)


def construire():
    a = K.Animal("bouquetin")
    a.taille = 1.55
    a.tete = NARGUE @ Vector((0, -0.14, 0.0))

    # ----- le corps : un tonneau tourné de la croupe au poitrail, puis couché (dans la pièce : X la gauche, Y le dos,
    #       Z l'avant) ; le garrot en bosse, le poitrail profond, le ventre qui remonte ; ventre pâle, plastron chocolat -----
    corps = A.tour(A.profil([(0, 0), (0.100, 0.016), (0.150, 0.090), (0.168, 0.200), (0.166, 0.330), (0.186, 0.470), (0.190, 0.580),
                             (0.142, 0.660), (0.072, 0.700), (0, 0.715)], 6), 52)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    z = corps.v[:, 2]
    t = np.tile(PIERRE, (len(z), 1))
    t[(ang > 2.20) & (z < 0.50)] = PALE
    t[(ang > 2.45) & (z > 0.60)] = CHOCO                                           # le plastron : sous la poitrine seulement
    corps.teinte = t

    def tonneau(v):
        s = v.copy()
        s[:, 0] *= 0.86
        dessous = v[:, 1] < 0
        s[dessous, 1] *= (1 - 0.20 * K.lisse((0.42 - v[:, 2]) / 0.30) + 0.08 * K.lisse((v[:, 2] - 0.42) / 0.18))[dessous]
        s[~dessous, 1] += 0.050 * gauss((v[:, 2] - 0.56) / 0.12)[~dessous]         # le garrot en bosse
        return s
    corps.sculpte(tonneau)
    G.sillons(corps, [13], 0.004, 1.1)
    a.piece("corps", corps, None, pos=CROUPE, rot=(90, 0, 0))

    # ----- la queue : un court moignon sombre, relevé -----
    queue = K.bandes(A.tour(A.profil([(0, 0), (0.036, 0.010), (0.034, 0.060), (0.018, 0.110), (0, 0.130)], 5), 24), [(9, CHOCO)])
    a.piece("queue", queue, None, pos=(0.0, 0.320, 0.570), rot=A.viser((0.0, 0.50, 0.86)))

    # ----- le cou : épais, porté haut -----
    cou = A.tour(A.profil([(0, 0), (0.150, 0.016), (0.140, 0.100), (0.120, 0.200), (0.104, 0.300), (0.092, 0.360), (0, 0.390)], 5), 32)
    cou.teinte = np.tile(PIERRE, (len(cou.v), 1))
    a.piece("cou", cou, None, pos=(0.0, -0.250, 0.600), rot=A.viser((0.02, -0.52, 0.85)))

    # ----- la tête : un crâne à bajoues, le nez busqué ; le museau clair, la truffe sombre -----
    def crane(v):
        for c in (1, -1):
            v = K.bosse(v, (c * 0.9, -0.2, -0.4), 0.12, 0.25)
        v = K.bosse(v, (0.0, -0.7, 0.5), 0.10, 0.25)                                # le front
        return v * [0.094, 0.108, 0.094]
    tete = A.boule(1.0, 56, 28)
    tete.teinte = np.tile(PIERRE, (len(tete.v), 1))
    a.piece("tete", tete.sculpte(crane), None, mat=NARGUE)
    pm = A.profil([(0.074, 0.0), (0.070, 0.040), (0.060, 0.090), (0.050, 0.130), (0.042, 0.158), (0, 0.178)], 6)
    Mu = NARGUE @ A.repere((0, -0.050, -0.030), (110, 0, 0))       # dans ce repère : X la gauche, Y le dessus du nez, Z vers le bout
    Mu3 = Mu.to_3x3()
    museau = A.tour(pm, 40).etire(1.0, 0.86, 1.0)
    museau.teinte = np.tile(PIERRE, (len(museau.v), 1))             # une face brune unie (Principal, 15/10)
    a.piece("museau", museau, None, mat=Mu)
    a.piece("nez", A.boule(1.0, 24, 12).etire(0.026, 0.015, 0.016), M.hexa("#3a2a2c"), mat=Mu @ A.repere((0, 0.010, 0.168)), poil=False)
    levre = [a.trace("museau", Mu @ Vector((0, 0, z_)), [Mu3 @ Vector((math.cos(math.radians(d)), math.sin(math.radians(d)), 0))])[0]
             for z_, d in ((0.160, -85), (0.148, -70), (0.134, -58), (0.118, -48), (0.100, -40), (0.082, -34))]
    a.broderie("bouche", A.courbe(levre, 4), 0.0028, FIL)

    # ----- les yeux : deux boutons ouverts, de côté, pareils (la tête est tournée : on vise par vers()) -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, vers(0.66 * c, -0.74, 0.14))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0165)

    # ----- la barbiche : un petit pinceau chocolat sous le menton -----
    barbiche = A.tour(A.profil([(0, 0), (0.016, 0.008), (0.017, 0.035), (0.010, 0.070), (0, 0.095)], 5), 24).etire(0.8, 1.0, 1.0)
    barbiche.teinte = np.tile(CHOCO * 1.1, (len(barbiche.v), 1))
    a.piece("barbiche", barbiche, None, pos=Mu @ Vector((0, -0.040, 0.100)), rot=A.viser(vers(0, -0.18, -1)))

    # ----- les petites oreilles : des feuilles courtes, tendues de côté -----
    def feuille(v):
        s = v.copy()
        s[:, 0] *= 1 - 0.45 * K.lisse((v[:, 2] + 0.2) / 1.2)
        return s
    for nom, c in (("G", 1), ("D", -1)):
        tombe = Vector((0.90 * c, 0.30, 0.05)).normalized()
        racine = Vector((0.086 * c, 0.030, 0.040))
        oreille = A.tour(A.profil([(0.040, 0), (0.038, 0.035), (0.026, 0.075), (0.010, 0.108), (0, 0.125)], 4), 24).etire(1.0, 0.38, 1.0)
        oreille.teinte = np.tile(PIERRE * 0.95, (len(oreille.v), 1))
        a.piece("oreille_" + nom, oreille, None, mat=NARGUE @ A.repere(racine + tombe * 0.020, A.viser(tombe)))

    # ----- les cornes : deux grands arcs d'ivoire, gros à la base, qui montent et se couchent en arrière, rayés de nœuds -----
    arc = ((0.058, 0.090, 0.060), (0.070, 0.150, 0.190), (0.086, 0.260, 0.290), (0.098, 0.390, 0.300), (0.102, 0.500, 0.225), (0.100, 0.590, 0.100))   # nés sur le crâne, DERRIÈRE les yeux
    for nom, c in (("G", 1), ("D", -1)):
        fil = A.courbe([tuple(NARGUE @ Vector((x * c, y, z_))) for x, y, z_ in arc], 12)
        corne = A.tube(fil, lambda t_: (0.050 - 0.036 * t_ ** 0.9) * (1 + 0.34 * max(0.0, math.cos(math.tau * 7.0 * t_)) ** 1.4), 18)
        corne.teinte = np.tile(IVOIRE, (len(corne.v), 1))
        a.piece("corne_" + nom, corne, None, poil=False)
        socle = A.boule(1.0, 24, 12).etire(0.060, 0.060, 0.046)                    # la touffe du crâne où naît la corne (l'ivoire ne bave plus sur le front)
        socle.teinte = np.tile(PIERRE, (len(socle.v), 1))
        a.piece("socle_" + nom, socle, None, mat=NARGUE @ A.repere((c * 0.060, 0.096, 0.050)))

    # ----- les quatre pattes : la jambe est une pièce tournée à sabot (comme celles de la chèvre), courte, forte, le genou
    #       gonflé ; l'épaule ou le gigot en haut ; la chaussette chocolat -----
    canon = [(0, 0), (0.046, 0.005), (0.054, 0.040), (0.042, 0.095), (0.038, 0.180), (0.043, 0.235), (0.041, 0.290)]
    devant = A.profil(canon + [(0.052, 0.360), (0.068, 0.440), (0.066, 0.500), (0, 0.545)], 6)                    # une épaule
    derriere = A.profil(canon + [(0.056, 0.360), (0.078, 0.440), (0.090, 0.500), (0.072, 0.560), (0, 0.590)], 6)  # un gigot

    def sabot(v):                                           # le bas de la patte avance un peu : un sabot
        s = v.copy()
        s[:, 1] -= 0.016 * K.lisse((0.060 - v[:, 2]) / 0.060)
        return s
    for nom, profil, pos, rot in (("avant_G", devant, (0.115, -0.230, 0.0), (-4, 0, 0)), ("avant_D", devant, (-0.115, -0.230, 0.0), (-4, 0, 0)),
                                  ("arriere_G", derriere, (0.120, 0.250, 0.004), (6, 0, 0)), ("arriere_D", derriere, (-0.120, 0.250, 0.004), (6, 0, 0))):
        patte = K.bandes(A.tour(profil, 32).sculpte(sabot), [(0.250, CHOCO), (9, PIERRE)])
        a.piece("patte_" + nom, patte, None, pos=pos, rot=rot)
        pieds = A.boule(1.0, 20, 10).etire(0.056, 0.074, 0.026)
        pieds.teinte = np.tile(np.asarray(SABOT, float), (len(pieds.v), 1))
        a.piece("sabot_" + nom, pieds, None, pos=(pos[0], pos[1] - 0.026, 0.020), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("bouquetin", styles.style_de("bouquetin"), sys.modules[__name__]), "Bouquetin")
