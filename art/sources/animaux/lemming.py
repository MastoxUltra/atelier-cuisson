"""Le lemming en peluche, cousu main : une poire caramel doré, la calotte et la grande selle charbon qui lui couvre les épaules, le ventre et le
museau crème, les petites pattes roses. Il se dresse sur ses pattes de derrière, le torse bombé, un poing levé au ciel
et l'autre sur la hanche, les sourcils froncés vers le museau : il va sauter de la falaise, et c'est une décision.

    python lemming.py        fabrique la fiche art/apercus/animaux/lemming.png (cousu main, palier 2)
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

CARAMEL = M.hexa("#f1c06a")                   # la dominante : caramel doré (le poil le fonce : on le prend nettement plus clair)
CHARBON = M.hexa("#35302f")                   # la calotte et la selle
CREME = M.hexa("#fff3dc")                     # le ventre, le museau
ROSE = M.hexa("#ee9aa6")                      # l'accent : les pattes, le nez, le dedans des oreilles
CORPS = Vector((0.0, 0.020, 0.185))
TETE = Vector((0.0, -0.040, 0.395))
LACET = 16.0                                  # la tête tournée vers nous


def peindre(m, region):
    """Peint la boule encore unité : region(v) rend « charbon », « creme » ou « caramel » pour chaque point."""
    t = np.zeros((len(m.v), 3))
    noms = region(m.v)
    for nom, c in (("caramel", CARAMEL), ("charbon", CHARBON), ("creme", CREME)):
        t[noms == nom] = c
    m.teinte = t
    return m


def construire():
    a = K.Animal("lemming")
    a.taille = 0.55

    # ----- le corps : une poire dodue, le torse bombé, penchée en arrière (il se cambre) ; la selle charbon couvre le dos -----
    def poire(v):
        v = K.bosse(v, (0, -0.9, 0.35), 0.14, 0.45)
        s = v * [0.118, 0.108, 0.150]
        s[:, 0] *= 1 + 0.12 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        s[:, 1] *= 1 + 0.10 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s

    def zone(v):
        x = np.abs(v[:, 0])                                   # une selle en lentille : large sur le dos, qui s'effile sur les flancs
        sel = (v[:, 1] > -0.22) & (v[:, 2] > -0.40 + 0.80 * x) & (v[:, 2] < 0.86 - 0.35 * x)
        ventre = (v[:, 1] < -0.30) & (v[:, 2] < 0.55)
        return np.where(sel, "charbon", np.where(ventre, "creme", "caramel"))
    corps = peindre(A.boule(1.0, 56, 28), zone).sculpte(poire)
    G.sillons(corps, [14], 0.005, 1.1)
    a.piece("corps", corps, None, pos=CORPS, rot=(-8, 0, 0))
    a.couture("dos", "corps", 14, 0.20, 0.95, fil=CARAMEL)
    a.rustine("ventre", "corps", CORPS + Vector((0, -0.01, 0.0)), (0, -0.90, -0.15), lambda th: 0.62 - 0.08 * math.cos(2 * th),
              K.CREME, 0.003, 24)

    # ----- la tête : large et ronde, les joues pleines, la calotte charbon qui descend jusqu'à la nuque -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()

    def large(v):
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.9, -0.25, -0.35), 0.18, 0.30)
        return v * [0.104, 0.096, 0.092]

    def calotte(v):
        return np.where((v[:, 2] > 0.18) & (v[:, 1] > -0.55), "charbon", np.where((v[:, 1] < -0.55) & (v[:, 2] < -0.10), "creme", "caramel"))
    a.piece("tete", peindre(A.boule(1.0, 48, 24), calotte).sculpte(large), None, mat=H)
    a.couture("crane", "tete", 14, 0.45, 0.98, fil=CARAMEL)
    a.tete = H @ Vector((0, -0.095, -0.005))

    # ----- le museau : court et rond, crème, le nez rose, la bouche serrée -----
    a.piece("museau", A.boule(1.0, 28, 14).etire(0.044, 0.046, 0.038), CREME, mat=H @ A.repere((0, -0.083, -0.030)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.013, 0.009, 0.010), ROSE, mat=H @ A.repere((0, -0.124, -0.019)), poil=False)
    bouche = [H3 @ Vector(d) for d in ((-0.22, -0.84, -0.50), (0.0, -0.90, -0.56), (0.22, -0.84, -0.50))]
    a.broderie("bouche", A.courbe(propres(a.trace("museau", H @ Vector((0, -0.083, -0.030)), bouche, 0.003)), 4), 0.0022, CHARBON)
    for nom, c in (("G", 1), ("D", -1)):                      # deux moustaches charbon
        for k, dz in enumerate((0.010, -0.014)):
            depart = H @ Vector((c * 0.030, -0.100, -0.026 + dz * 0.4))
            a.broderie("moustache_%s%d" % (nom, k), [depart, depart + H3 @ Vector((c * 0.050, 0.004, dz * 0.8)),
                                                      depart + H3 @ Vector((c * 0.092, 0.010, dz * 1.5))], 0.0013, CHARBON)

    # ----- les yeux : vivants, serrés ; deux gros sourcils charbon brodés, froncés vers le museau : la décision est prise -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, H3 @ Vector((c * 0.46, -0.82, 0.18)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0165)
        brow = [H3 @ Vector((c * (0.16 + 0.44 * t), -0.92 + 0.22 * t, 0.30 + 0.26 * t)) for t in np.linspace(0, 1, 6)]
        a.broderie("sourcil_" + nom, propres(a.trace("tete", TETE, brow, 0.004)), 0.0040, CHARBON)

    # ----- les oreilles : deux petits ronds, le dedans rose -----
    po = A.profil([(0, 0), (0.026, 0.008), (0.030, 0.028), (0.022, 0.048), (0.008, 0.058), (0, 0.062)], 5)
    for nom, c in (("G", 1), ("D", -1)):
        E = A.cadre(H @ Vector((c * 0.066, 0.004, 0.066)), H3 @ Vector((c * 0.55, 0.05, 0.84)), H3 @ Vector((c * 0.40, -0.90, 0.0)))
        a.piece("oreille_" + nom, A.tour(po, 28).etire(1.0, 0.40, 1.0), CHARBON, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 20).etire(0.58, 0.30, 0.70).pose((0, 0.006, 0.008)), ROSE, mat=E, poil=False)

    # ----- les bras : le gauche lève un poing au ciel, le droit sur la hanche ; poings roses -----
    for nom, c, chemin in (("G", 1, [(0.100, -0.015, 0.290), (0.150, -0.050, 0.350), (0.158, -0.080, 0.425), (0.150, -0.085, 0.470)]),
                           ("D", -1, [(-0.100, -0.015, 0.290), (-0.158, 0.005, 0.230), (-0.150, -0.025, 0.170), (-0.108, -0.055, 0.185)])):
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.034 - 0.008 * t, 14), CARAMEL)
        a.piece("poing_" + nom, A.boule(1.0, 24, 12).etire(0.032, 0.034, 0.034), ROSE, pos=chemin[-1])

    # ----- les jambes courtes, les grosses pattes roses plantées en canard ; la queue : un petit moignon -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.boule(1.0, 28, 14).etire(0.052, 0.068, 0.070), CARAMEL, pos=(c * 0.072, 0.030, 0.075))
        a.piece("pied_" + nom, A.boule(1.0, 28, 14).etire(0.046, 0.074, 0.024), ROSE, pos=(c * 0.082, -0.040, 0.022), rot=(0, 0, c * 14))
        a.ourlet("orteils_" + nom, "pied_" + nom, 0.50)
    a.piece("queue", A.boule(1.0, 20, 10).etire(0.030, 0.034, 0.030), CARAMEL, pos=(0, 0.132, 0.080))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lemming", styles.style_de("lemming"), sys.modules[__name__]), "Lemming")
