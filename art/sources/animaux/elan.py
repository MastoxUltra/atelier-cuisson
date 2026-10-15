"""L'élan en peluche : le géant des sapins, brun presque noir, les jambes pâles et longues, le garrot en bosse. Il porte sa
tête comme un mât de pavillon : un museau énorme, bulbeux, qui tombe en gros nez mou ; une cloche de poils sous la gorge ;
et sur le crâne les bois, deux palmes immenses dentelées de pointes, larges comme des portes, qui font toute sa silhouette.
Une patte avant levée, la tête de trois quarts : il hésite à traverser la clairière, et la clairière hésite aussi.

    python elan.py        fabrique la fiche art/apercus/animaux/elan.png (style du palier : B, peluche de magasin)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import matieres as M
import peluche as K
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

GONFLAGE = True                               # la base aux volumes de l'Artiste (fusion + gonflage), validée le 15/10

SOMBRE = np.array(M.hexa("#4a3629"))          # la dominante (registre : brun très sombre #3e2c22) ; le style B éclaircit un peu
PALE = np.array(M.hexa("#bfa98c"))            # les jambes, le ventre
BOIS = np.array(M.hexa("#c9984f"))            # l'accent : les bois, ocre
MUFLE = np.array(M.hexa("#6a5242"))           # le museau
NEZ = M.hexa("#1a1411")
FIL = M.hexa("#2a1c14")
H = Vector((0.080, -0.520, 1.340))            # le centre de la tête


def palme(L, W, n, plat=0.040):
    """Une palme d'élan : une main plate dont le bord avant porte n doigts tendus, le bord arrière lisse. x : vers le dehors
    (long), y : vers l'avant ; l'épaisseur est sur Z, aux arêtes arrondies."""
    pts = [(0.0, 0.10 * W)]
    for t in np.linspace(0.06, 1.0, 10):
        pts.append((L * t, -0.42 * W * math.sin(math.pi * min(t, 1.0) ** 0.85)))
    for k in range(n - 1, -1, -1):
        uk = L * (0.22 + 0.74 * k / (n - 1))
        wf = 0.52 * W * math.sin(math.pi * min(uk / L, 1.0) ** 0.8)
        pts += [(uk + 0.050 * L, wf), (uk + 0.020 * L, wf + 0.95 * W * (0.75 + 0.25 * k / (n - 1))), (uk - 0.045 * L, wf)]
    return A.decoupe(pts, plat, 0.014)


def gauss(x):
    return np.exp(-np.asarray(x) ** 2)


def construire():
    a = K.Animal("elan")
    a.taille = 2.30

    # ----- le corps : haut sur jambes, le garrot en bosse, la poitrine profonde, la croupe qui s'abaisse ; pâle sous le ventre -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(SOMBRE, (len(ang), 1))
        t[(ang > 2.30) & (m.v[:, 2] / L < 0.78)] = PALE * 0.55 + SOMBRE * 0.45
        return t
    rayon = O.interp([(0.0, 0.0), (0.05, 0.115), (0.20, 0.175), (0.50, 0.195), (0.78, 0.235), (0.93, 0.200), (1.0, 0.140)])
    O.corps_h(a, "corps", (0.0, 0.54, 0.92), 0.92, rayon, peint, None, cotes=52, pitch=9.0,
              deforme=O.gabarit(poitrail=0.20, taille=0.10, croupe=0.06, garrot=0.46, ventre=0.14))

    # ----- le cou court et fort ; la tête : un long chanfrein à l'arc doux, un mufle bulbeux dont la lèvre déborde, la cloche -----
    cou = O.tube_r([(0.0, -0.310, 1.060), (0.030, -0.390, 1.180), (0.060, -0.460, 1.270)], [0.185, 0.150, 0.120], 22)
    a.piece("cou", O.teinte(cou, SOMBRE), None)
    RT = A.repere(H, (14, 0, 24))              # le nez baissé, la tête de trois quarts
    HF = RT @ A.cadre(Vector((0.0, 0.060, 0.020)), (0.0, -1.0, -0.22), (0, 0, 1))      # x : la gauche, y : le haut, z : vers le nez
    HF3 = HF.to_3x3()
    pt = A.profil([(0, 0), (0.072, 0.008), (0.096, 0.050), (0.100, 0.095), (0.090, 0.155), (0.080, 0.220), (0.084, 0.268),
                   (0.098, 0.312), (0.102, 0.350), (0.092, 0.385), (0.060, 0.412), (0, 0.430)], 6)
    crane = A.tour(pt, 48)

    def chanfrein(v):
        s_ = v.copy()
        z_ = v[:, 2]
        s_[:, 1] += 0.020 * gauss((z_ - 0.27) / 0.10) * (v[:, 1] > 0)                  # l'arc du nez
        s_[:, 1] -= 0.024 * K.lisse((z_ - 0.34) / 0.08) * (v[:, 1] < 0)                # la lèvre qui pend
        return s_
    crane.teinte = np.where((crane.v[:, 2] > 0.30)[:, None], MUFLE, SOMBRE * 1.04)
    a.piece("tete", crane.sculpte(chanfrein).etire(1.0, 0.92, 1.0), None, mat=HF)
    a.piece("narine_G", A.boule(1.0, 14, 8).etire(0.016, 0.008, 0.024), NEZ, mat=HF @ A.repere((0.036, 0.062, 0.388), (-20, 0, 0)), poil=False)
    a.piece("narine_D", A.boule(1.0, 14, 8).etire(0.016, 0.008, 0.024), NEZ, mat=HF @ A.repere((-0.036, 0.062, 0.388), (-20, 0, 0)), poil=False)
    # la cloche : la barbe de peau qui pend sous la gorge, une goutte velue
    cl = A.tour(A.profil([(0, 0), (0.026, 0.008), (0.056, 0.055), (0.062, 0.125), (0.048, 0.200), (0.024, 0.255), (0, 0.285)], 5), 24).etire(0.78, 1.0, 1.0)
    cl.teinte = np.tile(SOMBRE * 1.05, (len(cl.v), 1))
    a.piece("cloche", cl, None, mat=A.cadre(HF @ Vector((0.0, -0.070, 0.090)), (0.0, -0.10, -1.0), (0, 0, 1)))
    # les yeux : deux boutons ouverts, de même taille, sur les côtés du chanfrein (la tête est tournée : R=HF)
    O.paire_yeux(a, "tete", HF @ Vector((0.0, 0.0, 0.140)), (0.98, 0.26, 0.0), 0.0190, decolle=0.003, R=HF)
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.tour(A.profil([(0.050, 0), (0.046, 0.055), (0.030, 0.115), (0.011, 0.158), (0, 0.172)], 4), 20).etire(1.0, 0.40, 1.0)
        a.piece("oreille_" + nom, O.couche(O.teinte(ore, SOMBRE), A.cadre(HF @ Vector((c * 0.088, 0.060, 0.045)), HF3 @ Vector((c * 0.90, 0.35, -0.05)), (0, 0, 1))), None)
        # le bois : une perche courte et forte, puis la palme à doigts, étalée vers le dehors et un peu vers l'avant
        base = HF @ Vector((c * 0.050, 0.085, 0.040))
        mid = HF @ Vector((c * 0.110, 0.135, 0.060))
        bout = HF @ Vector((c * 0.165, 0.160, 0.080))
        perche = O.tube_r([tuple(base), tuple(mid), tuple(bout)], [0.034, 0.030, 0.027], 14)
        a.piece("perche_" + nom, O.teinte(perche, BOIS * 0.92), None, poil=False)
        pal = palme(0.34, 0.115, 5)
        pal.teinte = np.where((np.hypot(pal.v[:, 0] / 0.34 - 0.5, pal.v[:, 1] / 0.20) > 0.40)[:, None], BOIS * 1.08, BOIS * 0.94)
        ex = HF3 @ Vector((c * 0.88, 0.20, 0.40))
        ey = HF3 @ Vector((0.0, 0.10, 1.0))
        a.piece("bois_" + nom, O.couche(pal, O.plan(bout, ex, ey)), None, poil=False)
    a.tete = HF @ Vector((0.0, 0.0, 0.50))

    # ----- les jambes : longues et pâles, les genoux marqués ; l'antérieur gauche levé, la patte pendante -----
    O.jambe(a, "avant_D", (-0.090, -0.270, 0.950), (-0.098, -0.340, 0.064), 0.098, SOMBRE, bas=PALE, bas_frac=0.58, sorte="av", plie=0.055,
            pied_dim=(0.052, 0.092, 0.030))
    lev = O.points_jambe((0.100, -0.280, 0.920), (0.110, -0.500, 0.470), "av", 0.13)
    a.piece("patte_avant_G", O.membre(lev, [0.098 * k for k in O.RAYONS_AV], [(0.58, tuple(SOMBRE)), (1.0, tuple(PALE))], 22), None)
    a.piece("pied_avant_G", O.teinte(A.boule(1.0, 24, 12).etire(0.044, 0.078, 0.030), PALE * 0.85), None, pos=(0.110, -0.512, 0.440), rot=(30, 0, 0), poil=False)
    for sgn, nom in ((1, "G"), (-1, "D")):
        O.jambe(a, "arriere_" + nom, (sgn * 0.100, 0.420, 0.960), (sgn * 0.108, 0.500, 0.064), 0.118, SOMBRE, bas=PALE, bas_frac=0.58, sorte="ar", plie=0.11,
                pied_dim=(0.048, 0.090, 0.028))
    queue = O.tube_r([(0.0, 0.520, 0.960), (0.0, 0.570, 0.920), (0.0, 0.580, 0.870)], [0.040, 0.034, 0.028], 12)
    a.piece("queue", O.teinte(queue, SOMBRE), None)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("elan", styles.style_de("elan"), sys.modules[__name__]), "Élan")
