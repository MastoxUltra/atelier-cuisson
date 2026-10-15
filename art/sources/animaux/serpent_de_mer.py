"""Le serpent de mer en peluche : un long boudin bagué de larges anneaux noirs et bleu glacier, très contrastés, avec une
queue plate en pagaie. Lové en S sur le sable, le cou se dresse en point d'interrogation et la tête, toute petite
au bout, penche vers nous un œil rond sous une paupière : il goûte l'air de la langue, deux fois, et n'a rien décidé.

    python serpent_de_mer.py        fabrique la fiche art/apercus/animaux/serpent_de_mer.png (style du palier : C, velours ras)
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

NOIR = np.array(M.hexa("#1d1d26"))
GLACIER = np.array(M.hexa("#8fb6c9"))         # la dominante (registre : bagué noir et bleu glacier)
VENTRE = np.array(M.hexa("#d8e6ec"))
LANGUE = M.hexa("#e2778a")
FIL = M.hexa("#10101a")

# le fil du corps, de la pagaie au bout du nez : un S couché sur le sable, puis le cou qui se dresse et la tête qui revient
CHEMIN = [(0.30, 0.46, 0.030), (0.17, 0.50, 0.040), (0.04, 0.42, 0.048), (-0.06, 0.28, 0.050), (-0.04, 0.12, 0.050),
          (0.10, 0.02, 0.050), (0.22, -0.10, 0.050), (0.16, -0.24, 0.050), (0.00, -0.28, 0.056), (-0.12, -0.20, 0.080),
          (-0.14, -0.08, 0.150), (-0.08, -0.06, 0.260), (-0.02, -0.12, 0.350), (0.01, -0.20, 0.390), (0.0, -0.27, 0.368)]
FIL_ = K.Fil(CHEMIN, flanc=(1.0, 0.0, 0.0), pas=10)
L = FIL_.long
TETE_F = 1.0 - 0.050 / L                      # la fraction où commence la tête


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def rayon(f):
    """La pagaie fine (aplatie ensuite), le corps épais, le cou un peu plus fin, la petite tête ronde au bout."""
    s = f * L
    base = 0.048 * np.interp(f, [0.0, 0.08, 0.30, 0.70, 0.90, 0.955, 0.985, 1.0], [0.40, 0.75, 1.0, 1.0, 0.72, 0.78, 0.92, 0.0])
    return float(base)


def construire():
    a = K.Animal("serpent_de_mer")
    a.taille = 1.40

    # ----- le boudin : tourné tout droit, peint en larges anneaux noirs et bleu glacier, ventre pâle ; couché le long du fil -----
    fs = np.linspace(0.0, 1.0, 260)
    prof = [(0.0, 0.0)] + [(rayon(f), f * L) for f in fs[1:-1]] + [(0.0, L)]
    corps = A.tour(prof, 40)
    z = corps.v[:, 2]
    anneau = (np.floor(z / 0.105).astype(int)) % 2
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))          # 0 : le dos ; pi : le ventre
    t = np.where(anneau[:, None] == 0, NOIR, GLACIER)
    t[(ang > 2.45) & (anneau == 1)] = VENTRE
    tete = z > L - 0.060
    t[tete] = NOIR * 0.9 + GLACIER * 0.1
    corps.teinte = t

    def pagaie(v):                                   # le bout de queue s'aplatit en pagaie (sur X) et s'élargit un peu
        s = v.copy()
        f = np.clip(1.0 - v[:, 2] / (0.16 * L), 0.0, 1.0)
        s[:, 0] *= 1 + 0.9 * f
        s[:, 1] *= 1 - 0.55 * f
        return s
    a.piece("corps", corps.sculpte(pagaie).sculpte(FIL_.couche), None)

    # ----- le visage : un œil rond sous une paupière, de chaque côté de la tête ; la langue fourchue qui goûte -----
    centre, avant, nuque = (Vector(q) for q in FIL_.cadre((TETE_F - 0.006) * L))
    for nom, c in (("G", 1), ("D", -1)):
        cc, dd = FIL_.vise((TETE_F + 0.010) * L, 0.28, c * 0.92, 0.32)
        pos, n = a.surface("corps", cc, dd)
        a.bouton("oeil_" + nom, pos + n * 0.002, n, 0.0155)
        haut_oeil = (nuque - n * n.dot(nuque)).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.0155, 0.10), tuple(NOIR), mat=A.cadre(pos + n * 0.002, n, haut_oeil), poil=False)
    c_, a_ = Vector(FIL_.cadre(L)[0]), Vector(FIL_.cadre(L)[1])
    fourche = [(0.0, -0.0026), (0.040, -0.0028), (0.060, -0.0120), (0.064, -0.0092), (0.046, 0.0), (0.064, 0.0092), (0.060, 0.0120),
               (0.040, 0.0028), (0.0, 0.0026)]
    langue = A.decoupe(fourche, 0.0030, 0.0010)
    haut = (Vector((0, 0, 1)) - a_ * a_.z).normalized()
    a.piece("langue", langue, LANGUE, mat=A.cadre(c_ - haut * 0.004, (a_ * 0.9 - haut * 0.1).normalized(), haut), poil=False)
    a.tete = c_ + a_ * 0.03
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules[__name__], "serpent")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("serpent_de_mer", styles.style_de("serpent_de_mer"), sys.modules[__name__]), "Serpent de mer")
