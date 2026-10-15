"""Le béluga en peluche de magasin : un bleu glacier presque blanc, rond et doux comme un édredon, sans nageoire sur le
dos, le melon du front plus clair et bombé, des joues rebondies, de petits yeux noirs et un sourire brodé qui remonte à
la joue. Un gros chanteur bonne pâte, couché sur le ventre comme échoué sur la banquise : la tête levée, la queue
cambrée en l'air, les petites nageoires à plat de chaque côté.

    python beluga.py        fabrique la fiche art/apercus/animaux/beluga.png (peluche de magasin, palier 4)
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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
GLACIER = M.hexa("#cfe6fa")                   # la dominante : bleu glacier presque blanc
MELON = M.hexa("#f3faff")                     # l'accent : le melon, plus clair
NAGEOIRE = M.hexa("#9cc4e6")                  # les nageoires, la queue : un ton plus bas
MARINE = M.hexa("#3a5a82")                    # le sourire
# l'échine, de la queue (en l'air) à la tête : (avance vers l'arrière, hauteur)
ECHINE = [(0.64, 0.400), (0.54, 0.262), (0.36, 0.170), (0.12, 0.150), (-0.10, 0.172), (-0.24, 0.225), (-0.32, 0.275)]
GALBE = [(0.0, 0.0), (0.02, 0.012), (0.10, 0.034), (0.22, 0.072), (0.40, 0.135), (0.58, 0.178), (0.72, 0.184), (0.82, 0.166),
         (0.88, 0.150), (0.93, 0.158), (0.975, 0.122), (1.0, 0.0)]


def construire():
    a = K.Animal("beluga")
    a.taille = 5.00

    # ----- le corps : une seule pièce longue couchée le long de l'échine en banane ; un pli au cou, des joues pleines -----
    fil = K.Fil([(0.0, y, z) for y, z in ECHINE], (1, 0, 0))
    L = fil.long
    corps = A.tour(A.profil([(r, f * L) for f, r in GALBE], 8), 64)

    def douce(v):
        s = v.copy()
        s[:, 0] *= 1.12                                                             # un peu plus large que haut
        s[:, 1] = np.where(s[:, 1] < 0, s[:, 1] * 0.82, s[:, 1])                     # le ventre aplati sur la glace
        return s
    corps.sculpte(douce)
    corps.teinte = np.tile(np.asarray(GLACIER, float), (len(corps.v), 1))
    corps.teinte[corps.v[:, 2] < 0.16 * L] = NAGEOIRE                                 # le bout de la queue, un ton plus bas
    a.piece("corps", corps.sculpte(fil.couche), None)
    centre, avant, nuque = fil.cadre(0.93 * L)
    flanc = np.asarray(fil.flanc, float)

    # ----- le melon : le front bombé, plus clair, posé sur la tête -----
    M_ = A.cadre(Vector(centre + nuque * 0.092 + avant * 0.012), Vector(avant), Vector(nuque))
    a.piece("melon", A.boule(1.0, 40, 20).etire(0.112, 0.074, 0.112), MELON, mat=M_)
    a.tete = Vector(centre + avant * 0.10 + nuque * 0.03)

    # ----- le sourire : un trait brodé qui court le long du museau et remonte à la joue ; les yeux : de petites billes -----
    for c in (1, -1):
        pts = []
        for f, haut in ((0.992, -0.50), (0.972, -0.52), (0.950, -0.50), (0.928, -0.42), (0.908, -0.26), (0.894, -0.06)):
            cen, av, nq = fil.cadre(f * L)
            pts += propres(a.trace("corps", Vector(cen), [Vector(av * 0.10 + flanc * c + nq * haut)], 0.006))
        a.broderie("sourire_" + ("G" if c > 0 else "D"), A.courbe(pts, 4), 0.0030, MARINE)
        cen, av, nq = fil.cadre(0.905 * L)
        p, n = a.surface("corps", Vector(cen), Vector(av * 0.16 + flanc * c * 0.95 + nq * 0.30))
        a.bouton("oeil_" + ("G" if c > 0 else "D"), p + n * 0.002, n, 0.022)

    # ----- les nageoires : deux petites pagaies rondes posées à plat, sous le cou, qui pointent vers l'arrière -----
    cen, av, nq = fil.cadre(0.80 * L)
    for nom, c in (("G", 1), ("D", -1)):
        depart = Vector(cen + flanc * c * 0.150 - nq * 0.100)
        vers = Vector(flanc * c * 0.70 - av * 0.60 - nq * 0.10)
        W = A.cadre(depart, vers, Vector(nq))
        a.piece("nageoire_" + nom, A.boule(1.0, 32, 16).etire(0.058, 0.016, 0.108).pose((0, 0, 0.090)), NAGEOIRE, mat=W)

    # ----- la queue : deux lobes plats en V au bout de la cambrure, de profil dans le plan de la queue -----
    cen0, av0, nq0 = fil.cadre(0.0)
    T = A.cadre(Vector(cen0), Vector(-av0), Vector(nq0))
    for nom, c in (("G", 1), ("D", -1)):
        lobe = A.boule(1.0, 28, 14).etire(0.098, 0.014, 0.046).pose((c * 0.080, 0.0, 0.030), (0, -c * 24, 0))
        a.piece("queue_" + nom, lobe, NAGEOIRE, mat=T)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("beluga", styles.style_de("beluga"), sys.modules[__name__]), "Béluga")
