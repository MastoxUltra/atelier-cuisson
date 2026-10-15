"""La salamandre en peluche : la petite noire du volcan, noir de jais luisant, deux rangées de grandes taches jaune citron
qui courent de la nuque au bout de la queue, deux plaques jaunes derrière les yeux, le ventre un peu plus clair. Un
corps rond posé bas sur quatre pattes écartées, en S, la tête tournée de côté, deux gros yeux noirs bombés, un large
sourire de crapaud : elle avance de ce pas lent qu'on a quand on sait que personne n'osera vous manger.

    python salamandre.py        fabrique la fiche art/apercus/animaux/salamandre.png (style du palier : C, velours ras)
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

NOIR = np.array(M.hexa("#2b2931"))            # la dominante (registre : noir de jais), un cran plus clair pour que la forme se lise
VENTRE = np.array(M.hexa("#46434d"))          # le ventre
JAUNE = np.array(M.hexa("#f4d21a"))           # l'accent : les taches jaune citron
FIL = M.hexa("#121014")

# du bout de la queue au bout du nez : la queue en S, le corps rond, le cou, la tête tournée de côté
CHEMIN = [(0.32, 0.18, 0.031), (0.30, 0.28, 0.039), (0.22, 0.36, 0.047), (0.10, 0.35, 0.055), (0.00, 0.26, 0.063),
          (-0.04, 0.14, 0.067), (-0.05, 0.02, 0.071), (0.00, -0.10, 0.071), (0.05, -0.20, 0.069), (0.06, -0.29, 0.067),
          (0.02, -0.37, 0.065), (-0.06, -0.43, 0.063), (-0.12, -0.47, 0.061)]
CORPS = O.interp([(0.0, 0.0), (0.02, 0.012), (0.10, 0.028), (0.30, 0.052), (0.46, 0.082), (0.62, 0.094), (0.76, 0.086),
                  (0.84, 0.068), (0.90, 0.072), (0.955, 0.070), (0.985, 0.050), (1.0, 0.0)])


def construire():
    a = K.Animal("salamandre")
    a.taille = 0.46

    # ----- le corps : une seule pièce couchée sur son fil ; la tête un peu aplatie et large, les taches jaunes en deux
    #       rangées alternées, les plaques derrière les yeux -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        f = m.v[:, 2] / L
        t = np.tile(NOIR, (len(f), 1))
        t[ang > 2.0] = VENTRE
        for k in range(11):
            fk = 0.10 + 0.074 * k
            for dec, signe in ((0.0, 1.0), (0.037, -1.0)):
                larg = 0.0125 + 0.006 * math.sin(2.3 * k + dec * 40.0)
                ici = (((f - (fk + dec)) / (1.15 * larg)) ** 2 + ((ang - 0.62 - 0.10 * signe) / 0.30) ** 2 < 1.0) & (f < 0.86)
                t[ici] = JAUNE
        t[(np.abs(f - 0.905) < 0.020) & (np.abs(ang - 0.95) < 0.40)] = JAUNE            # les plaques derrière les yeux
        return t

    def tete(L):
        def f(v):
            s = v.copy()
            fr = v[:, 2] / L
            g = np.clip((fr - 0.87) / 0.05, 0.0, 1.0)
            g = g * g * (3 - 2 * g)
            s[:, 1] *= 1.0 - 0.16 * g                                                   # la tête aplatie
            s[:, 0] *= 1.0 + 0.14 * g                                                   # et large
            return s
        return f
    fil, L = O.fil_corps(a, "corps", CHEMIN, CORPS, peint, None, cotes=34, flanc=(1.0, 0.0, 0.0), deforme=tete)

    # ----- le visage : deux gros yeux noirs bombés au-dessus de la tête, une large bouche en sourire, deux narines -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, direction = fil.vise(0.940 * L, 0.10, c * 0.78, 0.80)
        pos, n = a.surface("corps", centre, direction)
        a.oeil("oeil_" + nom, pos + n * 0.003, n, 0.0225)
    for c in (1, -1):
        pts = []
        for u_ in np.linspace(0.0, 1.0, 9):
            cc, dd = fil.vise((0.992 - 0.070 * u_) * L, 0.0, c * 1.0, -0.30 + 0.12 * u_)
            q = a.trace("corps", cc, [dd], 0.002)
            if q:
                pts.append(q[0])
        if len(pts) > 1:
            a.broderie("bouche_" + ("G" if c > 0 else "D"), A.courbe(pts, 3), 0.0026, FIL)

    # ----- les quatre pattes écartées, le genou en haut, la plante à plat ; une tache jaune sur chaque haut de patte -----
    def patte(nom, s, c, devant):
        centre, av, nq = (Vector(q) for q in fil.cadre(s))
        cote = nq.cross(av)
        sens = 1.0 if devant else -1.0                                                  # le pied se pose vers l'avant ou vers l'arrière
        racine = centre + cote * (c * 0.052) - nq * 0.010
        coude = centre + cote * (c * 0.118) + av * (0.020 * sens)
        coude.z = 0.046
        pied = centre + cote * (c * 0.140) + av * (0.052 * sens)
        pied.z = 0.012
        milieu = racine + (coude - racine) * 0.5 + Vector((0.0, 0.0, 0.010))
        pts = [tuple(racine), tuple(milieu), tuple(coude), tuple(pied + Vector((0.0, 0.0, 0.014)))]
        m = O.membre(pts, [0.040, 0.033, 0.027, 0.023], [(0.46, tuple(NOIR)), (0.66, tuple(JAUNE)), (1.0, tuple(NOIR))], 16)
        a.piece("patte_" + nom, m, None)
        doigts = A.boule(1.0, 20, 10).etire(0.030, 0.010, 0.036)
        for dx in (-0.020, 0.0, 0.020):
            doigts = doigts + A.boule(1.0, 12, 6).etire(0.009, 0.0075, 0.018).pose((dx, 0.0, 0.036))
        doigts.teinte = np.tile(NOIR, (len(doigts.v), 1))
        direction = Vector((c * 0.55, -0.85 if devant else -0.35, 0.0))
        a.piece("pied_" + nom, O.couche(doigts, A.cadre(Vector((pied.x, pied.y, 0.011)), direction, (0, 0, 1))), None, poil=False)

    for c, nm in ((1, "G"), (-1, "D")):
        patte("avant_" + nm, 0.765 * L, c, True)
        patte("arriere_" + nm, 0.320 * L, c, False)
    a.tete = Vector(fil.cadre(0.97 * L)[0]) + Vector((-0.04, -0.05, 0.02))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad", souple=True)


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("salamandre", styles.style_de("salamandre"), sys.modules[__name__]), "Salamandre")
