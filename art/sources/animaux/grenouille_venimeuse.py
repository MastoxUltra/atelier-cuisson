"""La grenouille venimeuse en peluche, cousue main : un jaune citron vif, le dos barré de bandes noires en croissant,
le ventre et les cuisses marbrés de pois noirs, des ventouses rondes au bout de chaque doigt et deux gros yeux noirs
saillants. Une minuscule diva qui sait ce qu'elle vaut : assise bien droite sur ses pattes arrière, les mains en avant
comme un chanteur lyrique, le menton haut, la gorge qui se gonfle : elle va lancer la note qu'on n'oubliera pas.

    python grenouille_venimeuse.py        fabrique la fiche art/apercus/animaux/grenouille_venimeuse.png (cousu main, palier 2)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import garnitures as G
import matieres as M
import peluche as K


def propres(points, eps=2e-4):
    """Les points d'un tracé sans doublons consécutifs (un tube dont deux points se suivent à l'identique se déforme en NaN) ;
    au moins deux points, écartés d'un millimètre au pire."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie

CITRON = M.hexa("#ffe95a")                    # la dominante : jaune citron vif
NOIR = M.hexa("#26242c")                      # l'accent : les bandes et les pois
VENTRE = M.hexa("#fff8c0")                    # le ventre, la gorge
VENTOUSE = M.hexa("#fff4b0")                  # le bout des doigts
CORPS = Vector((0.0, 0.040, 0.105))
TETE = Vector((0.0, -0.045, 0.200))


def construire():
    a = K.Animal("grenouille_venimeuse")
    a.taille = 0.34

    # ----- le corps : une poire dressée, large du bas, le ventre en avant ; peinte de bandes noires en croissant sur le dos -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(CITRON, float), (len(v), 1))
    t[(v[:, 1] < -0.35)] = VENTRE
    onde = np.sin(7.5 * v[:, 2] + 1.7 * v[:, 0])
    t[(v[:, 1] > 0.10) & (onde > 0.55)] = NOIR
    corps.teinte = t

    def poire(v):
        s = v * [0.092, 0.086, 0.112]
        s[:, 0] *= 1 + 0.30 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        s[:, 1] *= 1 + 0.14 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s
    G.sillons(corps, [14], 0.004, 1.1)
    a.piece("corps", corps.sculpte(poire), None, pos=CORPS, rot=(-8, 0, 0))

    # ----- la tête : large et plate, la gorge qui se gonfle dessous ; le menton levé -----
    H = A.repere(TETE, (-12, 0, 14))
    H3 = H.to_3x3()

    def tete_f(v):
        s = v * [0.092, 0.082, 0.062]
        s[:, 1] += 0.010 * K.lisse((v[:, 2] + 0.2) / 1.0)
        return s
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(tete_f), CITRON, mat=H)
    a.piece("gorge", A.boule(1.0, 32, 16).etire(0.050, 0.036, 0.030), VENTRE, mat=H @ A.repere((0, -0.040, -0.040)))
    a.tete = H @ Vector((0, -0.095, 0.0))
    bouche = [H3 @ Vector(d) for d in ((-0.55, -0.72, -0.40), (-0.20, -0.90, -0.46), (0.20, -0.90, -0.46), (0.55, -0.72, -0.40))]
    a.broderie("bouche", A.courbe(propres(a.trace("tete", TETE, bouche, 0.003)), 4), 0.0020, NOIR)

    # ----- les yeux : deux gros globes noirs sur le dessus de la tête, un reflet blanc ; un point cousu autour -----
    for nom, c in (("G", 1), ("D", -1)):
        place = H @ Vector((c * 0.050, -0.030, 0.050))
        a.piece("globe_" + nom, A.boule(1.0, 28, 14).etire(0.036, 0.036, 0.034), CITRON, mat=A.repere(place))
        p, n = a.surface("globe_" + nom, place, H3 @ Vector((c * 0.30, -0.90, 0.30)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0245)

    # ----- les bras : deux petits bras en avant, les mains ouvertes, un pois noir sur le coude ; les ventouses rondes -----
    for nom, c in (("G", 1), ("D", -1)):
        bras = [(c * 0.060, -0.030, 0.150), (c * 0.085, -0.075, 0.130), (c * 0.075, -0.115, 0.115)]
        a.piece("bras_" + nom, A.tube(A.courbe(bras, 5), lambda t: 0.020 - 0.004 * t, 12), CITRON)
        a.piece("main_" + nom, A.boule(1.0, 20, 10).etire(0.022, 0.026, 0.014), CITRON, pos=bras[-1])
        for k in (-1, 0, 1):
            a.piece("doigt_%s%d" % (nom, k), A.boule(1.0, 16, 8).etire(0.0095, 0.0095, 0.0075), VENTOUSE,
                    pos=(bras[-1][0] + k * 0.019, bras[-1][1] - 0.028, bras[-1][2] - 0.003), poil=False)

    # ----- les pattes arrière : deux cuisses repliées marbrées de noir, les longs pieds aux trois ventouses -----
    for nom, c in (("G", 1), ("D", -1)):
        cuisse = A.boule(1.0, 36, 18)
        cu = np.tile(np.asarray(CITRON, float), (len(cuisse.v), 1))
        cu[np.sin(9 * cuisse.v[:, 0] + 5 * cuisse.v[:, 2]) * np.sin(8 * cuisse.v[:, 1] + 1.0) > 0.5] = NOIR
        cuisse.teinte = cu
        a.piece("cuisse_" + nom, cuisse.etire(0.034, 0.072, 0.056), None, pos=(c * 0.100, 0.050, 0.070), rot=(10, 0, c * 18))
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.020, 0.070, 0.012), CITRON, pos=(c * 0.115, -0.030, 0.014), rot=(0, 0, c * 16))
        for k in (-1, 0, 1):
            a.piece("orteil_%s%d" % (nom, k), A.boule(1.0, 16, 8).etire(0.0095, 0.0095, 0.0075), VENTOUSE,
                    pos=(c * 0.115 + k * 0.019 + c * 0.012, -0.100, 0.010), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("grenouille_venimeuse", styles.style_de("grenouille_venimeuse"), sys.modules[__name__]), "Grenouille venimeuse")
