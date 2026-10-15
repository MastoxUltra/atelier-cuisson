"""L'élan en peluche, quatrième dessin, bâti comme le chevreuil gardé par l'auteur : le géant des sapins, brun presque noir,
les jambes pâles, le garrot en bosse. Les cinq traits de l'élan (trois photos, 15/10) : très haut sur pattes, le garrot en
bosse et la croupe courte ; une tête LONGUE au chanfrein doux et au mufle énorme dont la lèvre pend ; de grandes oreilles
étalées ; une cloche de peau sous la gorge ; des bois en larges palmes à doigts, sur une perche courte (moins de la moitié
du corps pour chaque palme). La tête de trois quarts, le nez un peu bas : il hésite à traverser la clairière.

    python elan.py        fabrique la fiche art/apercus/animaux/elan.png (style du palier : B, peluche de magasin)
    (1er dessin : museau-boule et palmes démesurées ; 3e : jambes en chaussettes et palmes à plat qui flottent ;
    4e : corps en pièce tournée, jambes à genou et boulet, sabots fendus, comme le chevreuil)
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
PALE = np.array(M.hexa("#bfa98c"))            # le bas des jambes, le ventre
FONCE = np.array(M.hexa("#3b2a20"))           # le chanfrein
BOIS = np.array(M.hexa("#b3803c"))            # l'accent : les bois, ocre
MUFLE = np.array(M.hexa("#5e4838"))           # le mufle
NEZ_T = M.hexa("#1a1411")
NEZ = np.array(NEZ_T)
CROUPE = Vector((0.0, 0.520, 0.980))          # le bout arrière du corps (une pièce tournée, couchée vers l'avant)
CABRE = 6.0                                   # le devant plus haut que la croupe
COL = math.radians(14)                        # le cou part un peu sur sa gauche, du côté où il regarde
AVANT = Vector((math.sin(COL), -math.cos(COL), 0.0))
FLANC = np.array([math.cos(COL), math.sin(COL), 0.0])
BASE = Vector((0.0, -0.300, 1.060))           # le pied du cou, enfoui dans le poitrail
ARC = [(0.0, 0.0), (0.030, 0.090), (0.080, 0.170), (0.140, 0.230), (0.200, 0.265)]       # (avance, monte)
LACET, PIQUE, PENCHE = 30.0, 16.0, 6.0        # la tête : de trois quarts, le nez un peu bas
GROSSE = 1.35


def gauss(x):
    return np.exp(-np.asarray(x) ** 2)


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


def jambe(points, rayons, genou):
    """Une jambe : un boudin qui passe par ses articulations (le genou, le boulet gonflés), sombre en haut, pâle sous le genou."""
    rayon = lambda t: float(np.interp(t, np.linspace(0, 1, len(rayons)), rayons))
    return K.tube_peint(A.courbe(points, 6), rayon, [(genou, SOMBRE), (1, PALE)], 18)


def sabot(e=1.0):
    """Un sabot fendu : la pince avance, une rainure sépare les deux onglons devant."""
    def fendu(v):
        s = v.copy()
        s[:, 1] -= 0.012 * e * K.lisse((0.032 * e - v[:, 2]) / (0.032 * e))
        devant = K.lisse(-v[:, 1] / (0.016 * e))
        s[:, 1] += 0.006 * e * devant * gauss(v[:, 0] / (0.0038 * e)) * K.lisse((0.034 * e - v[:, 2]) / (0.018 * e))
        return s
    prof = [(0, 0), (0.026, 0.003), (0.028, 0.014), (0.022, 0.036), (0.018, 0.046), (0, 0.050)]
    return A.tour(A.profil([(r * e, z * e) for r, z in prof], 5), 28).sculpte(fendu)


def construire():
    a = K.Animal("elan")
    a.taille = 2.30

    # ----- le corps : tourné de la croupe au poitrail, puis couché ; dans la pièce, X la gauche, Y le dos, Z l'avant ;
    #       le poitrail profond, le garrot en bosse, la croupe courte et basse ; le ventre plus pâle -----
    corps = A.tour(A.profil([(0, 0), (0.100, 0.010), (0.150, 0.060), (0.170, 0.150), (0.165, 0.260), (0.170, 0.380), (0.200, 0.500),
                             (0.225, 0.620), (0.230, 0.720), (0.190, 0.800), (0.110, 0.850), (0, 0.870)], 6), 52)
    v0 = corps.v
    tour_ = np.abs(np.arctan2(v0[:, 0], v0[:, 1]))
    corps.teinte = np.where(((tour_ > 2.30) & (v0[:, 2] < 0.70))[:, None], PALE * 0.55 + SOMBRE * 0.45, SOMBRE)

    def galbe(v):
        s = v.copy()
        s[:, 0] *= 0.88
        haut = v[:, 1] > 0
        s[haut, 1] += (0.100 * gauss((v[:, 2] - 0.66) / 0.14))[haut]              # le garrot en bosse
        bas = ~haut
        s[bas, 1] *= (1 - 0.14 * gauss((v[:, 2] - 0.30) / 0.16))[bas]             # le ventre remonte
        return s
    a.piece("corps", corps.sculpte(galbe), None, pos=CROUPE, rot=(90 - CABRE, 0, 0))

    # ----- le cou : court, énorme, porté en avant, qui s'amincit sous la tête -----
    enc = K.Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in ARC], FLANC)
    L = enc.long
    parts, rayons = [0.03, 0.15, 0.35, 0.55, 0.75, 0.90, 0.985], [0.200, 0.190, 0.170, 0.150, 0.135, 0.125, 0.118]
    pc = A.profil([(0, 0)] + [(r, p * L) for r, p in zip(rayons, parts)] + [(0, 1.01 * L)], 6)
    cou = A.tour(pc, 40).etire(0.88, 1.0, 1.0)
    cou.teinte = np.tile(SOMBRE, (len(cou.v), 1))
    a.piece("cou", cou.sculpte(enc.couche), None)

    # ----- la tête : LONGUE, le chanfrein à l'arc doux, le mufle bulbeux dont la lèvre pend ; dans son repère, X la gauche,
    #       Y le chanfrein, Z vers le nez -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0, 0, 0), nez) @ Matrix.Rotation(math.radians(PENCHE), 4, Vector((0, 0, 1))) @ A.repere(ech=(GROSSE,) * 3)
    bout = Vector(enc.cadre(L)[0])
    T = A.repere(bout - T.to_3x3() @ Vector((0, -0.020, 0.040))) @ T
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.0, 0.200))

    tete = A.tour(A.profil([(0, 0), (0.060, 0.008), (0.080, 0.040), (0.084, 0.080), (0.076, 0.125), (0.066, 0.165), (0.062, 0.195),
                            (0.070, 0.225), (0.072, 0.250), (0.066, 0.272), (0.044, 0.290), (0, 0.300)], 6), 56)
    z, x, y = tete.v[:, 2], tete.v[:, 0], tete.v[:, 1]
    teinte = np.tile(SOMBRE * 1.05, (len(z), 1))
    teinte[(y > 0.012) & (np.abs(x) < 0.040) & (z > 0.050) & (z < 0.230)] = FONCE          # le chanfrein
    teinte[z > 0.215] = MUFLE                                                              # le mufle
    teinte[z > 0.282] = NEZ                                                                # le bout du nez
    tete.teinte = teinte

    def chanfrein(v):
        s = v.copy()
        zz = v[:, 2]
        s[:, 1] += 0.014 * gauss((zz - 0.16) / 0.07) * (v[:, 1] > 0)                       # l'arc du nez
        s[:, 1] -= 0.024 * K.lisse((zz - 0.22) / 0.05) * (v[:, 1] < 0)                     # la lèvre qui pend
        return s
    a.piece("tete", tete.sculpte(chanfrein), None, mat=T)
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("narine_" + nom, A.boule(1.0, 14, 8).etire(0.013, 0.007, 0.020), NEZ_T, mat=T @ A.repere((c * 0.028, 0.052, 0.262), (-18, 0, 0)), poil=False)

    # la cloche : la goutte de peau velue qui pend sous la gorge
    cl = A.tour(A.profil([(0, 0), (0.026, 0.010), (0.060, 0.060), (0.068, 0.140), (0.052, 0.225), (0.026, 0.290), (0, 0.320)], 5), 24).etire(0.72, 1.0, 1.0)
    cl.teinte = np.tile(SOMBRE * 1.05, (len(cl.v), 1))
    a.piece("cloche", cl, None, mat=A.cadre(T @ Vector((0.0, -0.062, 0.060)), (0.0, -0.10, -1.0), (0, 0, 1)))

    # ----- les yeux : petits, noirs, ouverts, sur les côtés du chanfrein -----
    centre = T @ Vector((0, 0, 0.100))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.84, 0.40, 0.20)))
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0175)

    # ----- les oreilles : grandes, en cornet, étalées de côté et un peu en arrière -----
    po = A.profil([(0, 0), (0.020, 0.010), (0.038, 0.041), (0.046, 0.083), (0.040, 0.124), (0.023, 0.161), (0.008, 0.181), (0, 0.188)], 6)

    def cornet(v):
        s = v.copy()
        s[:, 1] += 2.6 * v[:, 0] ** 2 * K.lisse(v[:, 2] / 0.04)
        return s
    for nom, c in (("G", 1), ("D", -1)):
        vers = (T3 @ Vector((c * 0.85, 0.50, -0.25))).normalized()
        racine = T @ Vector((c * 0.058, 0.044, 0.030))
        E = A.cadre(racine - vers * 0.012, vers, T3 @ Vector((c * 0.10, 0.30, 1.0)))
        oreille = A.tour(po, 36).etire(1.0, 0.36, 1.0)
        oreille.teinte = np.tile(SOMBRE, (len(oreille.v), 1))
        a.piece("oreille_" + nom, oreille.sculpte(cornet), None, mat=E)

    # ----- les bois : une perche courte et forte, puis la palme à cinq doigts, inclinée vers le haut et l'avant -----
    for nom, c in (("G", 1), ("D", -1)):
        pts = [tuple(T @ Vector((c * 0.034, 0.062, 0.046))), tuple(T @ Vector((c * 0.080, 0.100, 0.060))), tuple(T @ Vector((c * 0.126, 0.122, 0.074)))]
        perche = O.tube_r(pts, [0.036, 0.032, 0.029], 14)
        a.piece("perche_" + nom, O.teinte(perche, BOIS * 0.92), None, poil=False)
        pal = palme(0.34, 0.115, 5)
        pal.teinte = np.where((np.hypot(pal.v[:, 0] / 0.34 - 0.5, pal.v[:, 1] / 0.20) > 0.40)[:, None], BOIS * 1.10, BOIS * 0.92)
        ex = T3 @ Vector((c * 0.90, 0.35, 0.25))
        ey = T3 @ Vector((c * 0.10, 0.50, 1.0))
        a.piece("bois_" + nom, O.couche(pal, O.plan(Vector(pts[-1]), ex, ey)), None, poil=False)

    # ----- les jambes : longues, le haut sombre, le bas pâle ; l'épaule ou la hanche, le genou, le canon, le boulet gonflé ;
    #       un sabot fendu au bout -----
    epaule = [0.092, 0.084, 0.064, 0.048, 0.040, 0.046, 0.040]
    hanche = [0.108, 0.094, 0.066, 0.048, 0.040, 0.046, 0.040]
    avant = lambda c: [(c * 0.100, -0.280, 1.000), (c * 0.120, -0.300, 0.820), (c * 0.120, -0.310, 0.620), (c * 0.120, -0.320, 0.420),
                       (c * 0.120, -0.330, 0.230), (c * 0.120, -0.335, 0.085), (c * 0.120, -0.338, 0.050)]
    arriere = lambda c: [(c * 0.115, 0.480, 1.000), (c * 0.150, 0.420, 0.810), (c * 0.140, 0.520, 0.610), (c * 0.130, 0.600, 0.420),
                         (c * 0.130, 0.565, 0.230), (c * 0.130, 0.545, 0.085), (c * 0.130, 0.540, 0.050)]
    for nom, c in (("G", 1), ("D", -1)):
        for quoi, pts, ray, genou in (("avant", avant(c), epaule, 0.58), ("arriere", arriere(c), hanche, 0.56)):
            a.piece("patte_%s_%s" % (quoi, nom), jambe(pts, ray, genou), None)
            a.piece("sabot_%s_%s" % (quoi, nom), O.teinte(sabot(2.0), np.asarray(NEZ, float)), None,
                    pos=(pts[-1][0], pts[-1][1] - 0.008, 0.0), poil=False)
    queue = A.boule(1.0, 16, 8).etire(0.040, 0.040, 0.060)
    queue.teinte = np.tile(SOMBRE, (len(queue.v), 1))
    a.piece("queue", queue, None, pos=(0.0, 0.540, 0.900))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("elan", styles.style_de("elan"), sys.modules[__name__]), "Élan")
