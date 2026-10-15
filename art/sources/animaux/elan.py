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

SOMBRE = np.array(M.hexa("#4a3629"))          # la dominante (registre : brun très sombre #3e2c22) ; le style B éclaircit un peu
PALE = np.array(M.hexa("#bfa98c"))            # les jambes, le ventre
BOIS = np.array(M.hexa("#c9984f"))            # l'accent : les bois, ocre
MUFLE = np.array(M.hexa("#6a5242"))           # le museau
NEZ = M.hexa("#1a1411")
FIL = M.hexa("#2a1c14")
H = Vector((0.080, -0.520, 1.340))            # le centre de la tête


def palme(L, W, dents, plat=0.034):
    """Une palme de bois : une grande lame ovale dont le bord avant porte `dents` pointes, extrudée sur Z (son épaisseur).
    x : vers le dehors (long), y : vers l'avant."""
    n = 64
    c = []
    for k in range(n):
        th = math.tau * k / n
        x = L * (0.5 + 0.5 * math.cos(th))
        r = W * math.sin(th)
        if r > 0:                                                                # le bord avant : des pointes
            ph = (dents * th / math.pi) % 1.0
            r *= 1.0 + 1.60 * (1.0 - abs(ph - 0.5) * 2.0) ** 1.0
            x += 0.20 * L * (1.0 - abs(ph - 0.5) * 2.0) ** 1.0 * (1 if math.cos(th) < 0 else 0.3)
        c.append((x, r))
    return A.decoupe(c, plat, 0.010)


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

    # ----- le cou court et fort ; la tête : un long chanfrein bombé, le museau en gros nez mou, la cloche sous la gorge -----
    cou = O.tube_r([(0.0, -0.310, 1.060), (0.030, -0.390, 1.180), (0.060, -0.460, 1.270)], [0.185, 0.150, 0.120], 22)
    a.piece("cou", O.teinte(cou, SOMBRE), None)
    RT = A.repere(H, (14, 0, 24))              # le nez baissé, la tête de trois quarts
    tete = A.boule(1.0, 52, 26)
    tete.sculpte(lambda v: K.bosse(v, (0.0, -0.7, 0.4), 0.16, 0.30))
    tete.teinte = np.tile(SOMBRE * 1.04, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.100, 0.150, 0.105), None, mat=RT)
    mufle = A.boule(1.0, 36, 18).etire(0.112, 0.150, 0.092)
    a.piece("mufle", O.teinte(mufle, MUFLE), None, mat=RT @ A.repere((0.0, -0.180, -0.060)))
    levre = A.boule(1.0, 28, 14).etire(0.102, 0.092, 0.062)
    a.piece("levre", O.teinte(levre, MUFLE * 0.95), None, mat=RT @ A.repere((0.0, -0.290, -0.115)))
    a.piece("nez", A.boule(1.0, 18, 8).etire(0.052, 0.034, 0.030), NEZ, mat=RT @ A.repere((0.0, -0.330, -0.080)), poil=False)
    cloche = K.tube_peint(A.courbe([tuple(RT @ Vector(p)) for p in ((0, -0.020, -0.100), (0, -0.040, -0.230), (0, -0.030, -0.420))], 4),
                          lambda t_: 0.058 * (1 - t_) ** 0.55 + 0.010, [(1.0, tuple(SOMBRE))], 14)
    a.piece("cloche", cloche, None)
    O.paire_yeux(a, "tete", H, (0.84, -0.46, 0.26), 0.0200, couleur_lourde=tuple(SOMBRE), coupe=0.05, decolle=0.003)
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.tour(A.profil([(0.046, 0), (0.040, 0.050), (0.024, 0.105), (0.009, 0.140), (0, 0.152)], 4), 20).etire(1.0, 0.42, 1.0)
        a.piece("oreille_" + nom, O.couche(O.teinte(ore, SOMBRE), RT @ A.cadre(Vector((c * 0.092, 0.060, 0.050)), (c * 0.85, 0.35, -0.10), (0, 0, 1))), None)
        # le bois : une courte perche, puis la grande palme dentelée, renversée vers le dehors et l'arrière
        perche = O.tube_r([tuple(RT @ Vector(p)) for p in ((c * 0.045, 0.035, 0.085), (c * 0.100, 0.060, 0.130), (c * 0.170, 0.075, 0.150))], [0.030, 0.026, 0.022], 14)
        a.piece("perche_" + nom, O.teinte(perche, BOIS), None, poil=False)
        pal = palme(0.54, 0.19, 5)
        pal.teinte = np.where((np.hypot(pal.v[:, 0] / 0.54 - 0.5, pal.v[:, 1] / 0.24) > 0.44)[:, None], BOIS * 1.08, BOIS * 0.94)
        base = RT @ Vector((c * 0.165, 0.075, 0.150))
        # la palme : son x va vers le dehors (c), son y vers l'avant, son épaisseur vers le haut incliné
        axe_x = (RT.to_3x3() @ Vector((c * 0.85, 0.22, 0.48))).normalized()
        norm = (RT.to_3x3() @ Vector((-c * 0.50, 0.12, 0.85))).normalized()
        y = norm.cross(axe_x).normalized()
        axe_x = y.cross(norm).normalized()
        R = Matrix.Identity(4)
        for i2, v in enumerate((axe_x, y, norm)):
            R[0][i2], R[1][i2], R[2][i2] = v
        R[0][3], R[1][3], R[2][3] = base
        a.piece("bois_" + nom, O.couche(pal, R), None, poil=False)
    a.tete = H + Vector((0.05, -0.24, -0.10))

    # ----- les jambes : longues et pâles, les genoux marqués ; l'antérieur gauche levé, la patte pendante -----
    O.jambe(a, "avant_D", (-0.090, -0.270, 0.950), (-0.098, -0.340, 0.064), 0.098, SOMBRE, bas=PALE, bas_frac=0.58, sorte="av", plie=0.055,
            pied_dim=(0.052, 0.092, 0.030))
    lev = O.points_jambe((0.100, -0.280, 0.920), (0.110, -0.500, 0.470), "av", 0.13)
    a.piece("patte_avant_G", O.membre(lev, [0.098 * k for k in O.RAYONS_AV], [(0.58, tuple(SOMBRE)), (1.0, tuple(PALE))], 22), None)
    a.piece("pied_avant_G", O.teinte(A.boule(1.0, 24, 12).etire(0.044, 0.078, 0.030), PALE * 0.85), None, pos=(0.110, -0.512, 0.440), rot=(30, 0, 0), poil=False)
    for sgn, nom in ((1, "G"), (-1, "D")):
        O.jambe(a, "arriere_" + nom, (sgn * 0.100, 0.660, 0.960), (sgn * 0.108, 0.730, 0.064), 0.118, SOMBRE, bas=PALE, bas_frac=0.58, sorte="ar", plie=0.11,
                pied_dim=(0.048, 0.090, 0.028))
    queue = O.tube_r([(0.0, 1.000, 0.960), (0.0, 1.050, 0.920), (0.0, 1.060, 0.870)], [0.040, 0.034, 0.028], 12)
    a.piece("queue", O.teinte(queue, SOMBRE), None)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("elan", styles.style_de("elan"), sys.modules[__name__]), "Élan")
