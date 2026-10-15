"""Le phoque en peluche : un phoque du Groenland de velours ras, gris tourterelle bleuté, le ventre argent, et sur le dos
sa signature : la selle en lyre, charbon, qui ferme ses deux bras sur les épaules et les laisse filer le long des
flancs jusqu'aux hanches. Le museau, une bande sur le front et la calotte sont charbon aussi, la truffe vieux rose.
Un farceur couché en banane sur le ventre : la tête et les palmes de derrière levées à la fois, les nageoires de
devant posées à plat, la tête penchée vers nous, de grands yeux curieux.

    python phoque.py        fabrique la fiche art/apercus/animaux/phoque.png (velours ras, palier 3)
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

TOURTERELLE = M.hexa("#a6aab7")               # la dominante : gris tourterelle bleuté (la lumière le blanchit : on le prend soutenu)
ARGENT = M.hexa("#dadde4")                    # le ventre
CHARBON = M.hexa("#2b2c33")                   # la lyre, le masque, le bout des palmes
VIEUX_ROSE = M.hexa("#d98f9a")                # l'accent : la truffe
# l'échine, de la queue à la nuque : chaque point (avance vers l'arrière, hauteur). Couché en banane : le ventre au sol,
# la queue et le cou relevés
ECHINE = [(0.50, 0.300), (0.40, 0.190), (0.25, 0.135), (0.07, 0.128), (-0.10, 0.155), (-0.22, 0.215), (-0.30, 0.300)]
GALBE = [(0.0, 0.0), (0.03, 0.045), (0.12, 0.078), (0.30, 0.126), (0.50, 0.150), (0.66, 0.146), (0.80, 0.122), (0.92, 0.100), (1.0, 0.0)]
TETE = Vector((0.0, -0.352, 0.382))
PIQUE, PENCHE, LACET = -8.0, 14.0, 22.0       # la tête : le nez un peu levé, penchée sur l'épaule, tournée vers nous


def quartiers(m, cotes, origine, nombres, bords, couleurs, eps=0.012):
    """Peint une pièce tournée encore droite par quartiers : de part et d'autre du méridien « origine », chaque anneau
    (à la cote z) est coupé aux angles bords(z) (entre 0 et pi, croissants, un de moins que de quartiers) et prend les
    couleurs couleurs(z). Chaque quartier garde le même nombre de méridiens d'un anneau à l'autre (nombres, leur somme
    fait la moitié des côtés plus un), tournés pour tomber pile sur ses bords : la limite reste nette sur le tissu comme
    sur le poil, même quand elle court en biais (le geste de la mouffette, pour autant de bandes qu'on veut). Un
    quartier qui doit disparaître se réduit à un fil (deux bords égaux) : on le peint de la couleur voisine."""
    demi = cotes // 2
    assert sum(nombres) == demi + 1
    teinte = np.zeros((len(m.v), 3))
    for anneau in m.anneaux:
        z = m.v[anneau[0], 2]
        cs = couleurs(z)
        if len(anneau) < 2:
            teinte[anneau[0]] = cs[0] if m.v[anneau[0], 2] < m.v[:, 2].mean() else cs[0]
            continue
        bs, avant = [], 0.0
        for b in bords(z):
            avant = min(max(b, avant + 2 * eps, 2 * eps), math.pi - 2 * eps)
            bs.append(avant)
        debuts, fins = [0.0] + bs, bs + [math.pi]
        ecart, couleur = [], []
        for i, (d, f) in enumerate(zip(debuts, fins)):
            d2, f2 = d + (eps if i else 0.0), f - (eps if i < len(bs) else 0.0)
            ecart += list(np.linspace(d2, max(f2, d2), nombres[i]))
            couleur += [cs[i]] * nombres[i]
        r = np.hypot(m.v[anneau, 0], m.v[anneau, 1])
        for j, i in enumerate(anneau):
            k = (j - origine) % cotes
            signe = 1.0 if k <= demi else -1.0
            k = min(k, cotes - k)
            angle = 2 * math.pi * origine / cotes + signe * ecart[k]
            m.v[i, 0], m.v[i, 1] = r[j] * math.cos(angle), r[j] * math.sin(angle)
            teinte[i] = couleur[k]
    m.teinte = teinte
    return m


def table(points):
    f, val = zip(*points)
    return lambda x: float(np.interp(x, f, val))


def construire():
    a = K.Animal("phoque")
    a.taille = 1.20

    # ----- le corps : une seule pièce couchée le long de l'échine, large et plate dessous ; peinte avant d'être couchée :
    #       le ventre argent, et la lyre charbon (fermée sur les épaules, ses deux bras le long des flancs) -----
    fil = K.Fil([(0.0, y, z) for y, z in ECHINE], (1, 0, 0))
    L = fil.long
    # (des bras de largeur égale, aux bouts arrondis : une lyre, pas une virgule)
    d1 = table([(0.26, 0.86), (0.268, 0.76), (0.285, 0.70), (0.32, 0.72), (0.42, 0.86), (0.55, 0.92), (0.64, 0.74), (0.70, 0.0), (0.76, 0.0)])
    d2 = table([(0.26, 0.86), (0.268, 0.96), (0.285, 1.04), (0.32, 1.10), (0.42, 1.28), (0.55, 1.34), (0.64, 1.20), (0.70, 1.00), (0.745, 0.55), (0.76, 0.0)])

    def lyre(f):
        """La lyre à la fraction f du corps : (bord du dedans, bord du dehors, fermée sur le dos ?)."""
        if not 0.26 < f < 0.76:
            return 0.62, 0.62, False
        return d1(f), max(d2(f), d1(f)), d1(f) < 0.05

    def bords(z):
        a1, a2, fermee = lyre(z / L)
        return [0.0 if fermee else a1, a2, 2.25]

    def couleurs(z):
        a1, a2, fermee = lyre(z / L)
        bande = CHARBON if a2 - a1 > 0.02 else TOURTERELLE
        return [CHARBON if fermee else TOURTERELLE, bande, TOURTERELLE, ARGENT]

    corps = A.tour(A.profil([(r, f * L) for f, r in GALBE], 8), 56)
    quartiers(corps, 56, 14, (7, 5, 7, 10), bords, couleurs)

    def plat(v):
        s = v * [1.18, 0.95, 1.0]
        s[:, 1] = np.where(s[:, 1] < 0, s[:, 1] * 0.82, s[:, 1])
        return s
    a.piece("corps", corps.sculpte(plat).sculpte(fil.couche), None)

    # ----- la tête : une boule ronde au museau court, posée au bout du cou ; dans la pièce, Z vers le nez, Y le dessus.
    #       Le masque charbon : une bande du nez au front, qui s'ouvre en calotte -----
    T = A.repere(TETE, (PIQUE, PENCHE, LACET)) @ A.repere((0, 0, 0), (90, 0, 0))
    T3 = T.to_3x3()
    masque = table([(-1.0, 0.05), (-0.75, 0.70), (-0.40, 0.95), (-0.10, 0.55), (0.20, 0.36), (0.55, 0.30), (0.85, 0.34), (1.0, 0.34)])
    tete = A.boule(1.0, 56, 28)
    quartiers(tete, 56, 14, (8, 21), lambda z: [masque(z)], lambda z: [CHARBON, TOURTERELLE])

    def ronde(v):
        s = v.copy()
        s[:, 0] *= 1 - 0.22 * K.lisse((v[:, 2] - 0.30) / 0.70)
        s[:, 1] *= 1 - 0.18 * K.lisse((v[:, 2] - 0.30) / 0.70)
        s = K.bosse(s, (0, 0.6, 0.4), 0.06, 0.4)
        return s * [0.118, 0.108, 0.135]
    a.piece("tete", tete.sculpte(ronde), None, mat=T)
    a.tete = T @ Vector((0, 0.010, 0.120))

    # ----- le museau : deux babines rondes argent, la truffe vieux rose posée dessus, deux moustaches charbon de chaque côté -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("babine_" + nom, A.boule(1.0, 28, 14).etire(0.040, 0.034, 0.036), ARGENT, mat=T @ A.repere((c * 0.030, -0.030, 0.108)))
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.022, 0.013, 0.015), VIEUX_ROSE, mat=T @ A.repere((0, 0.004, 0.142)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        for k, (monte, long) in enumerate(((0.010, 0.095), (-0.012, 0.085))):
            depart = T @ Vector((c * 0.060, -0.030 + monte, 0.118))
            brin = [depart + T3 @ Vector((c * long * u, (monte - 0.020 * u) * u, 0.012 * u)) for u in np.linspace(0, 1, 5)]
            a.broderie("moustache_%s%d" % (nom, k), A.courbe(brin, 4), 0.0020, CHARBON)

    # ----- sous les babines, un sourire en coin brodé, relevé du côté qu'il nous tend : le farceur -----
    coin = [T3 @ Vector(d) for d in ((-0.05, -0.76, 0.65), (0.10, -0.77, 0.63), (0.25, -0.71, 0.66), (0.36, -0.60, 0.71))]
    a.broderie("sourire", A.courbe(propres(a.trace("tete", TETE, coin, 0.004)), 4), 0.0024, CHARBON)

    # ----- les yeux : grands, vivants, sur le gris, de part et d'autre de la bande charbon du front -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, T3 @ Vector((c * 0.80, 0.42, 0.44)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.024)

    # ----- les nageoires de devant : deux pagaies posées à plat sur le sol, de part et d'autre du poitrail -----
    for nom, c in (("G", 1), ("D", -1)):
        sens = Vector((c * 0.62, -0.32, -0.55))
        W = A.cadre(Vector((c * 0.130, -0.150, 0.100)), sens, Vector((c * 0.32, 0.62, 0.0)))

        def pagaie(v):
            s = v.copy()
            s[:, 1] *= 0.70 + 0.30 * K.lisse((v[:, 2] + 0.6) / 1.0)
            return s * [0.022, 0.050, 0.072]
        a.piece("nageoire_" + nom, A.boule(1.0, 32, 16).sculpte(pagaie).pose((0, 0, 0.068)), TOURTERELLE, mat=W)

    # ----- les palmes de derrière : deux éventails levés au bout de la queue, en V, le bout charbon -----
    for nom, c in (("G", 1), ("D", -1)):
        palme = A.boule(1.0, 32, 16)
        palme.teinte = np.where((palme.v[:, 2] > 0.55)[:, None], np.asarray(CHARBON), np.asarray(TOURTERELLE))

        def eventail(v):
            s = v.copy()
            z = v[:, 2]
            s[:, 1] *= 0.40 + 0.60 * K.lisse((z + 1.0) / 1.6)
            s[:, 2] -= 0.18 * np.exp(-(v[:, 1] / 0.35) ** 2) * K.lisse((z - 0.6) / 0.4)      # l'encoche du bout
            return s * [0.020, 0.088, 0.085]
        W = A.cadre(Vector((c * 0.020, 0.475, 0.285)), Vector((c * 0.30, 0.66, 0.69)), Vector((c * 0.95, -0.30, 0.0)))
        a.piece("palme_" + nom, palme.sculpte(eventail).pose((0, 0, 0.070)), None, mat=W)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("phoque", styles.style_de("phoque"), sys.modules[__name__]), "Phoque")
