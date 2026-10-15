"""L'anaconda en peluche de magasin : un bronze sombre à l'huile, des ocelles charbon cernés de crème qui courent le long
du dos, le ventre jaune pâle, un corps épais comme un tronc enroulé en grosses boucles de boudin, et une tête plate
posée haut sur le cou, les narines sur le dessus, deux petits yeux d'or à la fente verticale, et la langue fourchue
qui goûte l'air. Le roi de la rivière, qui ne fait jamais rien et n'en a pas besoin : lové sur lui-même, le cou dressé,
la tête tournée de trois quarts vers nous, la gueule fermée sur un demi-sourire.

    python anaconda.py        fabrique la fiche art/apercus/animaux/anaconda.png (peluche de magasin, palier 4)
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
BRONZE = M.hexa("#9a7a38")                    # la dominante : bronze sombre
OCELLE = M.hexa("#3a2c22")                    # l'accent : les ocelles charbon
ANNEAU = M.hexa("#e8d68a")                    # le cerne crème des ocelles, le ventre
OR = M.hexa("#ffcf2a")                        # les yeux
ROSE = M.hexa("#e0556a")                      # la langue
LACET = 28.0


def serpent(chemin, rayon, cotes=16, saut=0.085):
    """Un tube peint tout le long (comme K.tube_peint, mais en ocelles) : sur chaque anneau, quelques facettes charbon
    cernées de crème, décalées d'un bloc à l'autre ; le ventre (le dessous) crème."""
    ch = np.asarray(chemin, float)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(ch, axis=0), axis=1))])
    n = max(8, int(fait[-1] / 0.012))
    t = np.linspace(0.0, 1.0, n)
    ch = np.stack([np.interp(t * fait[-1], fait, ch[:, k]) for k in range(3)], axis=1)
    m = A.tube(ch, rayon, cotes)
    teinte = np.tile(np.asarray(BRONZE, float), (len(m.v), 1))
    bloc = max(1, int(saut / 0.012))
    for i in range(n):
        k = i // bloc
        suite = i % bloc
        if k % 2 == 0:
            deb = (3 * (k // 2)) % cotes
            for j in range(cotes):
                d = (j - deb) % cotes
                if d in (0, 1, 2) and 1 < suite < bloc - 2:
                    teinte[i * cotes + j] = OCELLE
                elif d in (cotes - 1, 3) and 0 < suite < bloc - 1:
                    teinte[i * cotes + j] = ANNEAU
                elif d in (0, 1, 2) and suite in (1, bloc - 2):
                    teinte[i * cotes + j] = ANNEAU
    m.teinte = teinte
    return m


def construire():
    a = K.Animal("anaconda")
    a.taille = 4.50

    # ----- le corps : une grosse boucle de boudin posée à plat (trois tours qui s'étagent), qui s'élève en cou à la fin -----
    pts = []
    for k in range(0, 71):
        u = k / 70.0
        ang = 2 * math.pi * 2.6 * u + 0.6
        r = 0.50 * (1.0 - 0.45 * u)
        haut = 0.095 + 0.100 * min(u * 3.0, 1.0) * 0 + 0.150 * u * 0.0
        z = 0.095 + 0.130 * (min(u, 0.90) / 0.90) ** 1.1
        pts.append((r * math.cos(ang), r * math.sin(ang), z))
    # le cou : il quitte la boucle et monte en S vers la tête
    x0, y0, z0 = pts[-1]
    sortie = np.array([-math.sin(2 * math.pi * 2.6 + 0.6), math.cos(2 * math.pi * 2.6 + 0.6), 0.0])
    cou = [(x0 + sortie[0] * 0.08, y0 + sortie[1] * 0.08, z0 + 0.03), (x0 + sortie[0] * 0.16, y0 + sortie[1] * 0.16, z0 + 0.12),
           (x0 + sortie[0] * 0.22, y0 + sortie[1] * 0.22, z0 + 0.25), (x0 + sortie[0] * 0.20, y0 + sortie[1] * 0.20, z0 + 0.38),
           (x0 + sortie[0] * 0.12, y0 + sortie[1] * 0.12, z0 + 0.48), (x0 + sortie[0] * 0.02, y0 + sortie[1] * 0.02, z0 + 0.56)]
    chemin = pts + cou
    gros = lambda t: 0.105 - 0.026 * max(0.0, (t - 0.72) / 0.28) ** 1.2 - 0.088 * max(0.0, (0.14 - t) / 0.14) ** 1.3
    queue = [(0.50 * 0.99 * math.cos(0.6) + 0.02, 0.50 * math.sin(0.6) + 0.04, 0.060)]
    a.piece("corps", serpent(chemin, gros, 16), None, poil=False)
    fin = Vector(chemin[-1])
    a.tete = fin + Vector((0.0, -0.14, 0.04))

    # ----- la tête : un coin plat, large derrière, le museau rond, tournée de trois quarts vers nous -----
    dirige = Vector((math.sin(math.radians(LACET)), -math.cos(math.radians(LACET)), -0.10)).normalized()
    H = A.cadre(fin + Vector((0, 0, 0.040)) + dirige * 0.050, dirige, Vector((0, 0, 1)))
    H3 = H.to_3x3()

    def tete_f(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 0] *= 0.55 + 0.45 * K.lisse((0.35 - z) / 0.9)
        s[:, 1] *= 0.55
        return s
    tete = A.tour(A.profil([(0, 0), (0.078, 0.010), (0.130, 0.065), (0.134, 0.150), (0.108, 0.235), (0.080, 0.300), (0.052, 0.345), (0, 0.370)], 6), 44)
    tete.teinte = np.tile(np.asarray(BRONZE, float), (len(tete.v), 1))
    tete.teinte[tete.v[:, 1] < -0.040] = ANNEAU
    a.piece("tete", tete.sculpte(tete_f), None, mat=H, poil=False)

    # ----- les yeux : deux petites billes d'or, haut sur les côtés, une fente de feutrine noire dessus ; les narines -----
    centre = H @ Vector((0, 0, 0.200))
    for nom, c in (("G", 1), ("D", -1)):
        vers = H3 @ Vector((c * 0.82, 0.54, 0.0))
        p, n = a.surface("tete", centre, vers)
        a.piece("bille_" + nom, A.boule(1.0, 20, 10).etire(0.034, 0.034, 0.020), OR, mat=A.cadre(p + n * 0.0015, n), poil=False)
        a.bouton("oeil_" + nom, p + n * 0.005, n, 0.017)
        a.piece("narine_" + nom, A.boule(1.0, 16, 8).etire(0.010, 0.010, 0.006), OCELLE, mat=A.cadre(H @ Vector((c * 0.052, 0.056, 0.325)), H3 @ Vector((c * 0.2, 0.9, 0.3))), poil=False)

    # ----- la langue : fourchue, qui sort entre les lèvres et goûte l'air ; la gueule : un trait de bouche brodé -----
    base = H @ Vector((0, -0.020, 0.368))
    tige = [base, base + H3 @ Vector((0, -0.005, 0.040)), base + H3 @ Vector((0, 0.000, 0.080))]
    a.piece("langue", A.tube(A.courbe([tuple(q) for q in tige], 4), 0.0075, 8), ROSE, poil=False)
    for c in (1, -1):
        fourche = [tige[-1], tige[-1] + H3 @ Vector((c * 0.018, 0.004, 0.030))]
        a.piece("fourche_" + ("G" if c > 0 else "D"), A.tube([tuple(q) for q in fourche], 0.0055, 8), ROSE, poil=False)
    for c in (1, -1):
        bouche = [H3 @ Vector(d) for d in ((c * 0.10, -0.30, 0.95), (c * 0.58, -0.40, 0.65), (c * 0.88, -0.28, 0.20))]
        a.broderie("bouche_" + ("G" if c > 0 else "D"), A.courbe(propres(a.trace("tete", centre, bouche, 0.002)), 4), 0.0030, OCELLE)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("anaconda", styles.style_de("anaconda"), sys.modules[__name__]), "Anaconda")
