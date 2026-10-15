"""Le lagopède en peluche, deuxième dessin : la perdrix des neiges. Un corps de gallinacé incliné de trente degrés, la poitrine
en proue, la tête rentrée dans les épaules, les ailes blanches repliées comme des volets, la queue courte noire relevée
en virgule. Le dos grège moucheté de brun, la caroncule vermillon dressée en dents de scie au-dessus de l'œil. Et ses
pattes : des « pantoufles » de plumes blanches qui font corps avec le ventre, jusqu'au sol, sans qu'on voie une patte.
Il avance de ce petit pas décidé de celui qui sait que la neige, c'est chez lui.

    python lagopede.py        fabrique la fiche art/apercus/animaux/lagopede.png (style du palier : C, velours ras)
    (le premier dessin, refusé le 15/10 : « une boule avec deux gros chaussons blancs détachés »)
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

GREGE = np.array(M.hexa("#bca586"))           # la dominante (registre : grège moucheté) ; le velours éclaircit un peu
MOUCHE = np.array(M.hexa("#7f6a55"))          # les mouchetures
BLANC = np.array(M.hexa("#fbf9f4"))           # les ailes, le ventre, les chaussons
NOIR = np.array(M.hexa("#26211f"))            # la queue
VERMILLON = M.hexa("#ee3b22")                 # l'accent : la caroncule
BEC = M.hexa("#241e1c")
T = A.repere((0.0, 0.270, 0.150), (76, 0, 0)) # le corps en goutte : presque à l'horizontale, l'avant à 14° plus haut


def construire():
    a = K.Animal("lagopede")
    a.taille = 0.52

    # ----- le corps : un œuf de gallinacé, grège moucheté dessus, blanc dessous ; les pantoufles de plumes en font partie -----
    pc = A.profil([(0, 0.0), (0.042, 0.012), (0.080, 0.090), (0.114, 0.200), (0.140, 0.320), (0.142, 0.410), (0.116, 0.480), (0.070, 0.525), (0, 0.550)], 6)
    corps = A.tour(pc, 52)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    z = corps.v[:, 2]
    t = np.tile(GREGE, (len(z), 1))
    t[(ang > 1.90) & (z > 0.02)] = GREGE * 1.14                # la poitrine, un ton plus clair, mouchetée
    t[(ang > 2.55) & (z < 0.20) & (z > 0.02)] = BLANC          # le bas du ventre seulement
    t = O.moucheter(corps, GREGE, MOUCHE, graine=21, nombre=170, taille=0.075, depart=t)
    t[(ang > 2.55) & (z < 0.20) & (z > 0.02)] = BLANC
    corps.teinte = t
    # les pantoufles : deux gros chaussons blancs fondus dans le bas du ventre, jusqu'au sol (ajoutés à la même pièce)
    R3 = np.array(T.to_3x3())
    Tt = np.array(T.to_translation())
    for c in (1, -1):
        boot = A.boule(1.0, 28, 14).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.042, 0.078, 0.042).pose((c * 0.056, -0.010, 0.046))
        boot.v = (boot.v - Tt) @ R3
        boot.teinte = np.tile(BLANC, (len(boot.v), 1))
        corps = corps + boot
        for dx in (-0.030, 0.0, 0.030):                                         # les touffes de plumes devant : trois lobes
            lobe = A.boule(1.0, 12, 6).etire(0.013, 0.022, 0.012).pose((c * 0.056 + dx * 0.60, -0.092, 0.016))
            lobe.v = (lobe.v - Tt) @ R3
            lobe.teinte = np.tile(BLANC, (len(lobe.v), 1))
            corps = corps + lobe
    a.piece("corps", corps, None, mat=T)
    haut = Vector(T @ Vector((0, 0, 0.500)))

    # ----- la tête rentrée : une petite boule contre la poitrine, le bec court et sombre, la caroncule en dents de scie, l'œil vif -----
    H = haut + Vector((0.0, -0.012, 0.008))
    tete = A.boule(1.0, 40, 20)
    tete.teinte = np.tile(GREGE * 0.96, (len(tete.v), 1))
    RT = A.repere(H, (4, 0, 14))
    a.piece("tete", tete.etire(0.064, 0.066, 0.058), None, mat=RT)
    bec = A.tour(A.profil([(0.020, 0), (0.017, 0.016), (0.010, 0.034), (0.004, 0.046), (0, 0.052)], 4), 18).etire(0.84, 0.82, 1.0)
    bec = bec.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] - 0.012 * (v[:, 2] / 0.052) ** 2, v[:, 2]], axis=1))
    a.piece("bec", bec, BEC, mat=RT @ A.cadre(Vector((0.0, -0.056, -0.010)), (0.0, -1.0, -0.20), (0, 1, 0)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", H, RT.to_3x3() @ Vector((c * 0.74, -0.52, 0.18)))
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0125)
        h = Vector((0, 0, 1))
        a.piece("lourde_" + nom, K.paupiere(0.0125, 0.18), tuple(GREGE * 0.96), mat=A.cadre(pos + n * 0.002, n, (h - n * n.dot(h)).normalized()), poil=False)
        # la caroncule : une crête festonnée au-dessus de l'œil (cinq dents de scie)
        base = pos + Vector((0.0, 0.0, 0.016)) + n * 0.001
        dents = None
        for k in range(4):
            d = O.pointe(0.016 - 0.002 * abs(k - 1.5), 0.0070, 8)
            d = O.couche(O.teinte(d, np.array(VERMILLON)), A.cadre(base + Vector(((k - 1.5) * 0.0100, -0.002 * abs(k - 1.5), 0.0)),
                                                                     (0.0, 0.10, 1.0), (0, 1, 0)))
            dents = d if dents is None else dents + d
        a.piece("caroncule_" + nom, dents, None, poil=False)
    a.tete = H + Vector((0.0, -0.10, 0.0))

    # ----- les ailes : blanches, repliées comme des volets sur les flancs, le bout moucheté ; la queue courte, noire, relevée -----
    for nom, c in (("G", 1), ("D", -1)):
        al = A.boule(1.0, 32, 16).etire(0.034, 0.072, 0.150)
        f = al.v[:, 2] / 0.200
        tl = np.tile(BLANC, (len(f), 1))
        tl[f < -0.50] = GREGE * 0.9 + MOUCHE * 0.1
        al.teinte = tl
        a.piece("aile_" + nom, al, None, mat=T @ A.repere((c * 0.122, 0.020, 0.300), (0, 0, c * 4)))
    queue = A.boule(1.0, 24, 12).etire(0.040, 0.075, 0.016)
    queue.teinte = np.tile(NOIR, (len(queue.v), 1))
    a.piece("queue", queue, None, mat=T @ A.repere((0.0, 0.080, 0.030), (-34, 0, 0)))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lagopede", styles.style_de("lagopede"), sys.modules[__name__]), "Lagopède")
