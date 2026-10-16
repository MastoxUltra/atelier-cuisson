"""Le dauphin en peluche : le farceur du lagon, gris ardoise bleuté sur le dos, gris perle sur les flancs, ventre crème,
avec une ligne nette entre les trois. Un long corps en arc, couché sur le ventre, le bec levé bien haut et fendu d'un
trait de sourire rose, le melon bombé, la queue en croissant qui se dresse derrière lui comme s'il allait repartir d'un
bond. Il attend qu'on lui demande un tour.

    python dauphin.py        fabrique la fiche art/apercus/animaux/dauphin.png (style du palier : B, peluche de magasin)
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

ARDOISE = np.array(M.hexa("#6f7f98"))         # la dominante (registre du 14/10 : gris ardoise bleuté), un peu soutenue
PERLE = np.array(M.hexa("#b9c2ce"))           # les flancs
CREME = np.array(M.hexa("#f7eedb"))           # le ventre
NAGEOIRE = np.array(M.hexa("#5d6b84"))        # les nageoires, la queue
ROSE = M.hexa("#e2778a")                      # l'accent : le trait du sourire

# le fil du corps, du bout du bec au bout de la queue : le bec haut, le ventre posé, la queue qui se redresse
CHEMIN = [(0.0, -0.84, 0.66), (0.0, -0.58, 0.54), (0.0, -0.28, 0.36), (0.0, 0.05, 0.255), (0.0, 0.42, 0.235),
          (0.0, 0.80, 0.265), (0.0, 1.08, 0.280), (0.0, 1.32, 0.290)]
FIL = K.Fil(CHEMIN, flanc=(-1.0, 0.0, 0.0), pas=10)       # avec ce flanc, le dos de la pièce est en haut
L = FIL.long


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def rayon(f):
    """Le rayon du corps à la fraction f de la longueur : le bec fin, le melon, le plus large au tiers, puis la queue."""
    pts = [(0.0, 0.0), (0.030, 0.010), (0.046, 0.035), (0.054, 0.075), (0.070, 0.120), (0.108, 0.170), (0.150, 0.230), (0.188, 0.320),
           (0.205, 0.420), (0.198, 0.540), (0.160, 0.680), (0.104, 0.800), (0.062, 0.900), (0.044, 0.970), (0.030, 1.0)]
    x = np.array([p[1] for p in pts])
    r = np.array([p[0] for p in pts])
    return float(np.interp(f, x, r))


TOURNE = 34                                   # la fiche tourne la bête vers la caméra (25° devant) : on compte les DEUX yeux ; 0 pour le jeu


def construire():
    a = K.Animal("dauphin")
    a.taille = 2.40

    # ----- le corps : un fuseau tourné, peint dos / flancs / ventre, puis couché le long du fil ; le bec est une pièce à part,
    #       lisse (sans poil : le contrôleur voyait un bec hérissé), qui se fond dans le melon -----
    F_BEC = 0.125

    def fuseau(f0, f1, n):
        fs = np.linspace(f0, f1, n)
        prof = [(0.0, f0 * L)] + [(rayon(f), f * L) for f in fs] + [(0.0, f1 * L)]
        m = A.tour(prof, 56)
        x, y = m.v[:, 0], m.v[:, 1]
        ang = np.abs(np.arctan2(x, y))                      # 0 : le dos (+Y local) ; pi : le ventre
        t = np.tile(ARDOISE, (len(x), 1))
        t[ang > 1.00] = PERLE
        t[ang > 2.05] = CREME
        t[(m.v[:, 2] / L > 0.10) & (ang > 1.00) & (ang <= 1.10)] = ARDOISE * 0.92        # la ligne reste nette
        m.teinte = t
        return m

    def melon(v):                                       # le front bombe franchement au-dessus du bec : le melon
        s = v.copy()
        f = v[:, 2] / L
        bosse = np.exp(-((f - 0.150) / 0.060) ** 2)
        s[:, 1] += np.where(v[:, 1] > 0, 0.062 * bosse, 0.0)
        s[:, 0] *= 1.0 + 0.10 * bosse
        return s
    a.piece("corps", fuseau(0.0, 1.0, 130).sculpte(melon).sculpte(FIL.couche), None)          # une seule peau, bec compris : plus de coque lisse collée

    # ----- la queue : un croissant horizontal, posé au bout du fil, un peu relevé -----
    croissant = [(-0.31, 0.10), (-0.23, 0.04), (-0.11, -0.04), (-0.03, -0.07), (0.03, -0.07), (0.11, -0.04), (0.23, 0.04), (0.31, 0.10),
                 (0.21, 0.19), (0.08, 0.11), (0.0, 0.07), (-0.08, 0.11), (-0.21, 0.19)]
    queue = A.decoupe(croissant, 0.036, 0.012)
    queue.teinte = np.tile(NAGEOIRE, (len(queue.v), 1))
    bout = Vector(FIL.cadre(L)[0])
    av_bout = Vector(FIL.cadre(L)[1]).normalized()        # la tangente du bout de la queue : la nageoire la prolonge (plus de palette posée sur le dos)
    a.piece("caudale", queue.etire(1.25, 1.35, 1.35), None, mat=O.plan(bout - av_bout * 0.050, Vector((1.0, 0.0, 0.0)), av_bout), poil=False)

    # ----- la nageoire du dos : un croissant dressé, en pointe vers l'arrière ; deux pectorales vers l'avant-bas -----
    dorsale = A.decoupe([(0, 0), (0.04, 0.09), (0.11, 0.17), (0.20, 0.22), (0.20, 0.15), (0.17, 0.08), (0.23, 0.0)], 0.036, 0.011)
    dorsale.teinte = np.tile(NAGEOIRE, (len(dorsale.v), 1))
    s = 0.46 * L
    c0, av0, nq0 = FIL.cadre(s)
    base = Vector(c0) + Vector(nq0) * rayon(0.46) * 0.96
    a.piece("dorsale", couche(dorsale, A.cadre(base - Vector((0.0, 0.04, 0.0)), (1.0, 0.0, 0.0), (0, 0, 1))), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        s = 0.30 * L
        cp, ap, nq = FIL.cadre(s)
        base = Vector(cp) + Vector((c * rayon(0.30) * 0.90, 0.0, -rayon(0.30) * 0.30))
        pec = A.tour(A.profil([(0, 0), (0.026, 0.020), (0.052, 0.080), (0.040, 0.150), (0.014, 0.205), (0, 0.222)], 4), 20)
        pec.etire(0.30, 1.0, 1.0)
        pec.teinte = np.tile(NAGEOIRE, (len(pec.v), 1))
        a.piece("pectorale_" + nom, couche(pec, A.cadre(base, (c * 0.80, 0.34, -0.48), (0, 0, 1))), None, poil=False)

    # ----- les yeux : de petites billes sombres, bas sur la tête, derrière le bec ; le trait rose du sourire -----
    for nom, c in (("G", 1), ("D", -1)):
        s = 0.200 * L
        centre, direction = FIL.vise(s, 1.50, -c * 0.95, 0.45)
        pos, n = a.surface("corps", centre, direction)
        a.oeil("oeil_" + nom, pos + n * 0.003, n, 0.0520)                       # un vrai œil, plus gros
        bouche = []
        for u in np.linspace(0.0, 1.0, 7):
            ss = (0.030 + 0.105 * u) * L                    # la bouche s'arrête bien avant l'œil
            cc, dd = FIL.vise(ss, 0.0, -c * 1.0, -0.30 + 0.10 * u)
            q = a.trace("corps", cc, [dd], 0.002)
            if q:
                bouche.append(q[0])
        a.broderie("sourire_" + nom, A.courbe(bouche, 4), 0.0030, (0.30, 0.34, 0.42))      # un trait de la couleur du corps, plus de rose sur le bec
    a.tete = Vector(FIL.cadre(0.15 * L)[0]) + Vector((0.0, -0.05, 0.05))
    if TOURNE:
        O.tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("dauphin", styles.style_de("dauphin"), sys.modules[__name__]), "Dauphin")
