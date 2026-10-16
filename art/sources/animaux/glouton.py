"""Le glouton en peluche : le petit trapu des sapins, brun suie, le pelage hirsute, avec une large bande dorée qui part
des épaules et descend de chaque côté pour se rejoindre à la queue : une selle de cuir doré. Bas sur pattes, les épaules
remontées, le dos en arc, la tête basse et tournée sur le côté, les yeux petits sous un front plissé, un masque gris givré
sur le museau : il a trouvé quelque chose de gros et de mort, et il compte bien le garder. La queue, touffue, traîne par
terre. Il mange vraiment de tout ; personne ne lui a jamais demandé son avis.

    python glouton.py        fabrique la fiche art/apercus/animaux/glouton.png (style du palier : B, peluche de magasin)
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

SUIE = np.array(M.hexa("#54433a"))            # la dominante (registre : brun suie #4a3a32) ; le style B éclaircit un peu
OR = np.array(M.hexa("#cf9f58"))              # l'accent : la bande dorée
GIVRE = np.array(M.hexa("#a89c92"))           # le masque, le museau
NOIRC = np.array(M.hexa("#241a15"))           # les pattes, le bout de la queue
NEZ = M.hexa("#16110e")
DENT = M.hexa("#f2ead8")
FIL = M.hexa("#241812")
H = Vector((0.0, -0.350, 0.310))              # le centre de la tête, bas, devant


def construire():
    a = K.Animal("glouton")
    a.taille = 0.95

    # ----- le corps : un trapu, la croupe plus haute que les épaules, le dos en arc ; la bande dorée peinte en selle -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        f = m.v[:, 2] / L
        t = np.tile(SUIE, (len(ang), 1))
        bande = (ang > 0.95) & (ang < 2.05) & (f > 0.06) & (f < 0.78)                           # la bande des flancs
        bande &= np.abs(ang - 1.50 + 0.55 * (f - 0.42)) < 0.52
        t[bande] = OR
        t[(f > 0.80) & (ang > 1.5)] = SUIE * 0.8
        return t
    rayon = O.interp([(0.0, 0.0), (0.05, 0.110), (0.20, 0.168), (0.50, 0.182), (0.80, 0.186), (0.94, 0.160), (1.0, 0.120)])
    O.corps_h(a, "corps", (0.0, 0.230, 0.340), 0.52, rayon, peint, None, cotes=48, pitch=-3.0,
              deforme=O.gabarit(poitrail=0.14, taille=0.03, croupe=0.14, garrot=0.34, ventre=0.02))

    # ----- la tête : large et basse, le front plissé, les joues pleines, le masque givré ; la gueule qui retrousse la lèvre -----
    RT = A.repere(H, (-6, 0, 28))
    tete = A.boule(1.0, 52, 26)
    for c in (1, -1):
        tete.sculpte(lambda v, c=c: K.bosse(v, (c * 0.9, -0.3, -0.25), 0.22, 0.30))
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(SUIE, (len(u), 1))
    t[(u[:, 1] < -0.10) & (np.abs(u[:, 2] - 0.0) < 0.55) & (np.abs(u[:, 0]) > 0.15)] = GIVRE         # le masque givré
    t[(u[:, 1] < -0.60) & (np.abs(u[:, 0]) < 0.45)] = GIVRE * 0.9
    tete.teinte = t
    a.piece("tete", tete.etire(0.142, 0.130, 0.110), None, mat=RT)
    museau = A.boule(1.0, 28, 14).etire(0.068, 0.082, 0.050)
    a.piece("museau", O.teinte(museau, GIVRE * 0.9), None, mat=RT @ A.repere((0.0, -0.105, -0.036)))
    a.piece("nez", A.boule(1.0, 16, 8).etire(0.026, 0.020, 0.018), NEZ, mat=RT @ A.repere((0.0, -0.176, -0.018)), poil=False)
    O.paire_yeux(a, "tete", H, (0.62, -0.74, 0.16), 0.0165, couleur_lourde=tuple(SUIE), coupe=0.60, decolle=0.003, R=RT)
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.boule(1.0, 20, 10).etire(0.040, 0.020, 0.040)
        a.piece("oreille_" + nom, O.teinte(ore, SUIE * 0.9), None, mat=RT @ A.repere((c * 0.100, 0.020, 0.090)))
        dent = O.pointe(0.020, 0.0062, 8)
        a.piece("croc_" + nom, O.couche(O.teinte(dent, np.array(DENT)), RT @ A.cadre(Vector((c * 0.028, -0.150, -0.068)), (0.0, 0.1, -1.0), (0, 1, 0))), None, poil=False)
    O.broder(a, "gueule", "museau", RT @ Vector((0, -0.105, -0.036)), [(0.55 * u_, -0.80, -0.50 + 0.10 * u_ * u_) for u_ in np.linspace(-1, 1, 7)], 0.0022, FIL, R=RT)
    a.tete = H + Vector((0.0, -0.17, 0.0))

    # ----- les pattes : courtes et très fortes, les épaules remontées, les grosses griffes pâles ; l'antérieur gauche avancé -----
    for sgn, nom in ((1, "G"), (-1, "D")):
        O.jambe(a, "avant_" + nom, (sgn * 0.100, -0.120, 0.340), (sgn * 0.115, -0.215 if sgn < 0 else -0.280, 0.052), 0.092, SUIE, bas=NOIRC, bas_frac=0.50,
                sorte="av", plie=0.030, pied_dim=(0.060, 0.095, 0.030), griffes=4, griffes_bout=True)
        O.jambe(a, "arriere_" + nom, (sgn * 0.100, 0.130, 0.360), (sgn * 0.118, 0.200, 0.052), 0.100, SUIE, bas=NOIRC, bas_frac=0.50,
                sorte="ar", plie=0.06, pied_dim=(0.062, 0.100, 0.030), griffes=4, griffes_bout=True)

    # ----- la queue : touffue, traînante, plus claire sur le dessus, le bout noir -----
    queue = K.tube_peint(A.courbe([(0.0, 0.250, 0.370), (0.0, 0.370, 0.290), (0.040, 0.450, 0.160), (0.040, 0.440, 0.060)], 6),
                         lambda t_: 0.062 + 0.040 * math.sin(math.pi * min(t_ * 1.15, 1.0)) ** 0.8, [(0.80, SUIE), (1.0, NOIRC)], 18)
    a.piece("queue", queue, None)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("glouton", styles.style_de("glouton"), sys.modules[__name__]), "Glouton")
