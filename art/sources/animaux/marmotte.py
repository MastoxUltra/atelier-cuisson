"""La marmotte en peluche : la sentinelle des crêtes. Dressée de toute sa hauteur sur ses pattes de derrière, la
queue posée en béquille, le ventre rond en avant et les mains pendantes sur la poitrine, elle monte la garde : la
tête levée et tournée vers le ciel, d'où vient l'aigle, deux sourcils crème froncés sous la calotte ardoise. Une
robe brun gris cendré, un ventre clair rapiécé, un museau crème large et plat, et ses deux incisives orange.

    python marmotte.py        fabrique la fiche art/apercus/animaux/marmotte.png (style du palier : A, cousu main)
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
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

BRUN = M.hexa("#a08a7a")                     # la dominante (registre du 14/10 : brun gris cendré #8f7a6c) ; un cran
                                             # plus clair, le poil cousu main fonce
VENTRE = M.hexa("#cbb6a2")                   # le ventre, plus clair, de la même famille
CALOTTE = K.ARDOISE                          # le dessus de la tête et le bout de la queue
PATTES = M.hexa("#463a36")                   # les mains et les pieds, en feutrine
IVOIRE = M.hexa("#efdcb0")                   # l'accent : les incisives, petites, d'un ivoire chaud (l'auteur, 15/10)
CORPS = Vector((0.0, 0.020, 0.0))
TETE = Vector((0.0, 0.006, 0.548))


def gauss(x):
    return np.exp(-x * x)


def construire():
    a = K.Animal("marmotte")
    a.taille = 0.72

    # ----- le corps : une poire dressée, un peu renversée en arrière, le ventre rond qui pousse en avant -----
    def campe(v):
        s = v.copy()
        z = v[:, 2]
        devant = np.clip(-v[:, 1] / 0.16, 0.0, 1.0)
        s[:, 1] -= 0.030 * gauss((z - 0.20) / 0.09) * devant              # la panse
        s[:, 1] += 0.10 * z                                               # renversée en arrière
        return s
    corps = A.tour(A.profil([(0, 0.022), (0.092, 0.030), (0.142, 0.072), (0.160, 0.140), (0.157, 0.222), (0.140, 0.300),
                             (0.114, 0.368), (0.094, 0.424), (0.082, 0.470), (0, 0.500)], 6), 48)
    G.sillons(corps, [12], 0.005, 1.1)
    a.piece("corps", corps.sculpte(campe), BRUN, pos=CORPS)
    a.couture("dos", "corps", 12, 0.30, 0.94)
    a.rustine("ventre", "corps", CORPS + Vector((0, 0.010, 0.200)), (0, -1, 0.08),
              lambda th: 0.55 - 0.09 * math.cos(2 * th), VENTRE, feston=28)

    # ----- la tête : large et plate, les bajoues, levée et tournée vers sa gauche (le ciel, et nous) -----
    H = A.repere(TETE, (-24, -8, 30))
    H3 = H.to_3x3()
    a.tete = H @ Vector((0, -0.088, -0.006))

    def crane(v):
        for c in (1, -1):
            v = K.bosse(v, (c * 0.9, -0.35, -0.35), 0.16, 0.30)            # les bajoues
        v = K.emousse(v, 0.88)
        return v * [0.094, 0.086, 0.074]
    tete = A.boule(1.0, 56, 28)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    tete.teinte = np.where((u[:, 2] + 0.25 * np.abs(u[:, 1]) > 0.55)[:, None], np.asarray(CALOTTE), np.asarray(BRUN))
    a.piece("tete", tete.sculpte(crane), None, mat=H)
    a.couture("crane", "tete", 14, 0.56, 0.98)

    # ----- le museau : large, plat et crème ; la truffe, la bouche en Y, et les deux petites incisives ivoire -----
    museau = A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.80)).etire(0.054, 0.042, 0.037)
    a.piece("museau", museau, K.CREME, mat=H @ A.repere((0, -0.074, -0.022)))
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.017, 0.010, 0.011), PATTES, mat=H @ A.repere((0, -0.114, -0.004)), poil=False)
    centre = H @ Vector((0, -0.074, -0.022))
    levre = [a.trace("museau", centre, [H3 @ Vector(d)])[0] for d in ((0, -0.95, 0.30), (0, -1.0, -0.05), (0, -0.85, -0.52))]
    a.broderie("levre", A.courbe(levre, 4), 0.0020, PATTES)
    for nom, c in (("G", 1), ("D", -1)):
        bouche = [a.trace("museau", centre, [H3 @ Vector((c * x, -0.85, -0.52 + 0.10 * x))])[0] for x in (0.0, 0.30, 0.55, 0.72)]
        a.broderie("bouche_" + nom, A.courbe(bouche, 4), 0.0020, PATTES)

    # les incisives : petites, d'un ivoire chaud, cousues DANS la bouche, au point où les lèvres se rejoignent ; le haut est
    # enfoncé sous la feutrine, elles ne dépassent que d'un demi-centimètre
    p0 = a.trace("museau", centre, [H3 @ Vector((0, -0.85, -0.52))], 0.0)[0]
    loc = H.inverted() @ p0
    for nom, c in (("G", 1), ("D", -1)):
        dent = A.boule(1.0, 16, 8).sculpte(lambda v: K.emousse(v, 0.70)).etire(0.0049, 0.0032, 0.0098)
        a.piece("dent_" + nom, dent, IVOIRE, mat=H @ A.repere((loc.x + c * 0.0052, loc.y + 0.0012, loc.z - 0.0042), (-6, 0, c * -3)), poil=False)

    # ----- les yeux vivants, juste sous la calotte, et deux sourcils crème froncés : elle monte la garde -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, vers = a.surface("tete", TETE, H3 @ Vector((c * 0.64, -0.62, 0.26)))
        a.oeil("oeil_" + nom, pos + vers * 0.002, vers, 0.0165)
        fronce = [H3 @ Vector((c * (0.020 + 0.040 * t), -0.088 + 0.030 * t, 0.046 + 0.016 * t)) for t in np.linspace(0, 1, 6)]
        a.broderie("sourcil_" + nom, a.trace("tete", TETE, fronce), 0.0026, K.CREME)

    # ----- les petites oreilles rondes, plantées bas sur les côtés du crâne -----
    def coupe(v):
        s = v.copy()
        s[:, 2] += 1.6 * (v[:, 0] ** 2 + v[:, 1] ** 2)
        return s * [0.024, 0.022, 0.007]
    for nom, c in (("G", 1), ("D", -1)):
        E = H @ A.cadre((c * 0.080, 0.012, 0.040), (c * 0.55, -0.70, 0.45), (0, 0.2, 1.0))
        a.piece("oreille_" + nom, A.boule(1.0, 28, 14).sculpte(coupe), CALOTTE, mat=E, poil=False)

    # ----- les bras courts, les mains pendantes sur la poitrine -----
    for nom, c in (("G", 1), ("D", -1)):
        bras = A.courbe([(c * 0.086, 0.024, 0.425), (c * 0.100, -0.026, 0.392), (c * 0.072, -0.070, 0.362), (c * 0.046, -0.086, 0.350)], 6)
        a.piece("bras_" + nom, A.tube(bras, lambda t: 0.028 - 0.006 * t, 14), BRUN)
        a.piece("main_" + nom, A.boule(1.0, 20, 10).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.018, 0.014, 0.025), PATTES,
                mat=A.repere((c * 0.042, -0.092, 0.330), (-28, 0, c * -12)), poil=False)

    # ----- les cuisses rondes cousues sur leur tranche, les grands pieds plats posés devant -----
    cuisse = A.boule(1.0, 32, 16).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.054, 0.088, 0.074)
    a.piece("cuisse", cuisse, BRUN, pos=(0.112, 0.020, 0.088), rot=(14, 0, 8), paire=True)
    a.couture("cuisse", "cuisse", 8, 0.15, 0.85, "droit", paire=True)
    pied = A.boule(1.0, 24, 12).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.030, 0.064, 0.016)
    a.piece("pied", pied, PATTES, pos=(0.086, -0.064, 0.016), rot=(0, 0, 12), poil=False, paire=True)

    # ----- la queue : épaisse, posée au sol derrière elle comme une béquille, le bout ardoise relevé -----
    queue = A.courbe([(0, 0.118, 0.118), (0, 0.192, 0.068), (0.010, 0.266, 0.040), (0.040, 0.322, 0.040), (0.066, 0.350, 0.074)], 8)
    a.piece("queue", K.tube_peint(queue, lambda t: (0.041 - 0.010 * t) * math.sqrt(1 - K.lisse((t - 0.84) / 0.16)), [(0.68, BRUN), (1, CALOTTE)], 16), None)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("marmotte", styles.style_de("marmotte"), sys.modules[__name__]), "Marmotte")
