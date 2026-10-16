"""(Troisième dessin, 15/10 au soir, d'après le contrôleur et des photos du cerf élaphe au brame : la ramure courbe et
pointue, la crinière en mèches plates couchées, le corps lourd et les jambes fortes, les yeux ouverts, et le gonflage.
Cinq traits : la ramure en lyre courbe à andouillers pointus ; l'encolure épaisse à crinière ; le corps profond aux
épaules fortes ; la tête longue au museau effilé ; le miroir crème sous une queue courte.)
Le cerf en peluche, deuxième dessin (l'auteur, 15/10 : « il manque de prestance, c'est un animal imposant ») : le seigneur du bois, majestueux et un brin vaniteux. Un grand corps de velours châtaigne, haut
sur pattes, le poitrail bombé et le ventre levretté ; l'encolure épaisse, plus sombre, qui porte sous la gorge une
lourde crinière de rut en mèches brun noir. La tête haute, le menton levé, tournée vers nous juste assez pour qu'on
voie sa ramure : immense, ivoire, deux merrains qui montent en lyre et s'ouvrent au sommet en couronne de trois
andouillers, presque aussi haute que lui. Deux yeux vifs, grands ouverts : il nous regarde de haut. Il a
fait un pas en avant de l'antérieur gauche, comme on pose pour un portrait. Le ventre, le dedans des oreilles et le
miroir autour de sa courte queue sont crème ; le bas des jambes et les sabots, brun noir.

    python cerf.py        fabrique la fiche art/apercus/animaux/cerf.png (style C, velours ras : palier 3)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import matieres as M
import peluche as K

GONFLAGE = True                                # la base aux volumes de l'Artiste (fusion.py) : des volumes rembourrés, pas des tubes

CHATAIGNE = M.hexa("#8a5a3c")                 # la robe
SOMBRE = M.hexa("#573626")                    # l'encolure, le bas des jambes
CRIN = M.hexa("#3e2a22")                      # la crinière de la gorge, la queue
CREME = M.hexa("#ecd8b4")                     # le ventre, le miroir, le menton, le dedans des oreilles
IVOIRE = M.hexa("#f2ead8")                    # l'accent : les pointes des bois, en feutrine
MERRAIN_BRUN = M.hexa("#9b7652")               # le bois lui-même, brun noisette, qui blanchit vers les pointes
CORNE = M.hexa("#2f2725")                     # les sabots, le bout du nez
TOURNE = -20                                  # -20 sur la fiche (il pose de trois quarts) ; 0 pour le jeu
CROUPE = Vector((0.0, 0.29, 0.660))           # le bout arrière du corps (une pièce tournée, couchée vers l'avant)
CABRE = 5.0                                   # le poitrail plus haut que la croupe : il bombe le torse
COL = math.radians(14)                        # l'encolure part un peu vers sa gauche, du côté où il regarde
AVANT = Vector((math.sin(COL), -math.cos(COL), 0.0))
FLANC = np.array([math.cos(COL), math.sin(COL), 0.0])
BASE = Vector((0.0, -0.200, 0.730))           # le pied de l'encolure, enfoui dans le poitrail
ARC = [(0.0, 0.0), (0.024, 0.110), (0.046, 0.215), (0.068, 0.300), (0.088, 0.360), (0.100, 0.392)]   # l'encolure monte plus droite : port de tête haut   # (avance, monte)
LACET, PIQUE, PENCHE = 46.0, -2.0, -6.0       # la tête : tournée vers nous, le nez presque à l'horizontale (le menton levé)
GROSSE = 1.50                                 # une grosse tête de peluche
RAMURE = 1.05                                 # la ramure, à l'échelle de la tête
ALLONGE = 1.60                                # les andouillers, longs et pointus (courts, ils faisaient chevilles)


def gauss(x):
    return np.exp(-x * x)


def meche(chemin, large, face, plat=0.45, cotes=16):
    """Une mèche plate : un fuseau tourné, aplati, couché le long d'un chemin (comme la crinière du cheval).
    « face » : la direction de son épaisseur ; sa largeur se met d'équerre avec le chemin, en chaque point."""
    p = A.courbe(chemin, 8)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    n0 = np.asarray(face, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.linalg.norm(t, axis=1, keepdims=True)
        x = np.cross(n0, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.60 * large, 0.05 * L), (0.95 * large, 0.22 * L), (large, 0.42 * L), (0.72 * large, 0.70 * L),
                     (0.30 * large, 0.92 * L), (0.06 * large, 0.985 * L), (0, L)], 5)
    return A.tour(prof, cotes).etire(1.0, plat, 1.0).sculpte(couche)


def jambe(points, rayons, genou=0.55):
    """Une jambe : un boudin qui passe par ses articulations, châtaigne en haut, brun sombre sous le genou (ou le jarret)."""
    rayon = lambda t: float(np.interp(t, np.linspace(0, 1, len(rayons)), rayons))
    return K.tube_peint(A.courbe(points, 6), rayon, [(genou, CHATAIGNE), (1, SOMBRE)], 20)


def sabot():
    """Un petit sabot fendu : la pince avance, et une rainure sépare les deux onglons devant."""
    def fendu(v):
        s = v.copy()
        s[:, 1] -= 0.010 * K.lisse((0.036 - v[:, 2]) / 0.036)
        devant = K.lisse(-v[:, 1] / 0.020)
        s[:, 1] += 0.007 * devant * gauss(v[:, 0] / 0.0045) * K.lisse((0.040 - v[:, 2]) / 0.020)
        return s
    return A.tour(A.profil([(0, 0), (0.036, 0.003), (0.039, 0.018), (0.032, 0.044), (0.028, 0.054), (0, 0.058)], 5), 28).sculpte(fendu)


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


# la ramure, dans le repère de la tête (avant l'échelle GROSSE) : X la gauche, Y le dessus du crâne, Z vers le nez.
# Le merrain s'ouvre large, part en arrière puis remonte : une lyre. Chaque andouiller : son chemin, et son rayon au départ.
MERRAIN = [(0.034, 0.056, 0.040), (0.075, 0.100, 0.010), (0.140, 0.160, -0.060), (0.205, 0.240, -0.110),
           (0.250, 0.330, -0.105), (0.270, 0.410, -0.055), (0.268, 0.470, 0.015)]      # courbe : en arrière, puis il remonte vers l'avant
ANDOUILLERS = [
    ([(0.064, 0.098, 0.025), (0.085, 0.112, 0.090), (0.095, 0.145, 0.150)], 0.012),     # l'andouiller d'œil, sur le front
    ([(0.115, 0.160, -0.020), (0.145, 0.190, 0.050), (0.160, 0.235, 0.095)], 0.011),    # le second
    ([(0.215, 0.285, -0.080), (0.250, 0.320, -0.010), (0.270, 0.370, 0.035)], 0.011),   # la chevillure
    ([(0.268, 0.400, -0.050), (0.285, 0.470, -0.110), (0.280, 0.530, -0.140)], 0.010),  # la couronne : en arrière,
    ([(0.272, 0.465, 0.005), (0.268, 0.530, 0.030), (0.262, 0.575, 0.040)], 0.010),     #   au milieu,
    ([(0.270, 0.440, -0.020), (0.320, 0.490, 0.010), (0.350, 0.545, 0.020)], 0.009),    #   et vers le dehors,
    ([(0.271, 0.455, -0.008), (0.300, 0.520, -0.060), (0.312, 0.575, -0.080)], 0.009),  #   et une quatrième pointe : une couronne de roi
    ([(0.090, 0.130, 0.008), (0.120, 0.150, 0.075), (0.135, 0.185, 0.125)], 0.010),     # le surandouiller, juste au-dessus du premier
]


def construire():
    a = K.Animal("cerf")
    a.taille = 2.10

    # ----- le corps : tourné de la croupe au poitrail, puis couché ; dans la pièce, X est la gauche, Y le dos, Z l'avant.
    #       Le poitrail profond, le ventre qui remonte vers les flancs (levretté), une croupe ronde. -----
    corps = A.tour(A.profil([(0, 0), (0.122, 0.010), (0.174, 0.060), (0.190, 0.130), (0.184, 0.220), (0.186, 0.300),
                             (0.208, 0.400), (0.218, 0.470), (0.176, 0.550), (0, 0.605)], 6), 48)       # lourd : un corps de biche ne fait pas un cerf       # le poitrail large et profond
    v0 = corps.v
    dessous = np.abs(np.arctan2(v0[:, 0], v0[:, 1])) > 2.30
    ventre = dessous & (v0[:, 2] > 0.10) & (v0[:, 2] < 0.46)
    miroir = (v0[:, 2] < 0.045) & (v0[:, 1] > -0.05)
    corps.teinte = np.where((ventre | miroir)[:, None], np.asarray(CREME), np.asarray(CHATAIGNE))

    def galbe(v):
        s = v.copy()
        s[:, 0] *= 0.84 * (1 + 0.10 * gauss((v[:, 2] - 0.10) / 0.10) + 0.10 * gauss((v[:, 2] - 0.47) / 0.08))
        bas = v[:, 1] < 0
        s[bas, 1] *= (1 - 0.18 * gauss((v[:, 2] - 0.20) / 0.12) + 0.16 * gauss((v[:, 2] - 0.46) / 0.08))[bas]
        haut = ~bas
        s[haut, 1] *= (1 + 0.06 * gauss((v[:, 2] - 0.10) / 0.08) + 0.08 * gauss((v[:, 2] - 0.48) / 0.07))[haut]
        return s
    a.piece("corps", corps.sculpte(galbe), None, pos=CROUPE, rot=(90 - CABRE, 0, 0))

    # ----- l'encolure : une pièce couchée le long de son arc, épaisse (c'est la saison du brame), plus sombre -----
    enc = K.Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in ARC], FLANC)
    L = enc.long
    parts, rayons = [0.03, 0.15, 0.35, 0.55, 0.75, 0.90, 0.985], [0.182, 0.170, 0.148, 0.126, 0.106, 0.094, 0.080]
    pc = A.profil([(0, 0)] + [(r, p * L) for r, p in zip(rayons, parts)] + [(0, 1.01 * L)], 6)
    a.piece("cou", A.tour(pc, 48).etire(0.80, 1.0, 1.0).sculpte(enc.couche), SOMBRE)

    # ----- la crinière de rut : des mèches brun noir nées sous la gorge et sur le bas des flancs du cou, qui pendent -----
    criniere = None
    touffes = [(f, 0, 0.21 - 0.08 * abs(f - 0.38) / 0.45) for f in (0.12, 0.22, 0.32, 0.42, 0.52, 0.62, 0.72, 0.82)]
    touffes += [(f, c * a_, 0.16 - 0.02 * k) for k, f in enumerate((0.18, 0.34, 0.50, 0.66)) for c in (1, -1) for a_ in (0.75, 1.30)]
    for i, (f, ang, long) in enumerate(touffes):
        c_, av, nq = enc.cadre(f * L)
        r = float(np.interp(f, parts, rayons))
        cote = FLANC * math.sin(ang) * 0.80
        gorge = -nq * math.cos(ang) + cote
        depart = c_ + gorge * r * 0.80
        bas = np.array([0.0, 0.0, -1.0])
        chemin = [depart - gorge * 0.012, depart + gorge * 0.024 + bas * 0.016 - av * 0.012, depart + gorge * 0.030 + bas * long * 0.45 - av * 0.040,
                  depart + gorge * 0.022 + bas * long * 0.75 - av * 0.075]      # couchées vers le poitrail
        m = meche(chemin, 0.044 if i % 2 else 0.052, FLANC if ang == 0 else gorge, 0.38, 12)     # plates et larges : épaisses, elles pendaient en boudins
        criniere = m if criniere is None else criniere + m
    a.piece("criniere", criniere, CRIN)

    # ----- la tête : longue et fine, le front large, le chanfrein droit, le bout du nez noir, le menton crème ;
    #       dans son repère, X la gauche, Y le chanfrein, Z vers le nez -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0, 0, 0), nez) @ Matrix.Rotation(math.radians(PENCHE), 4, Vector((0, 0, 1))) @ A.repere(ech=(GROSSE,) * 3)
    bout = Vector(enc.cadre(L)[0])
    T = A.repere(bout - T.to_3x3() @ Vector((0, -0.024, 0.064))) @ T            # le bout de l'encolure entre dans la ganache
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.030, 0.190))

    tete = A.tour(A.profil([(0, 0), (0.046, 0.008), (0.068, 0.040), (0.072, 0.085), (0.060, 0.140), (0.046, 0.195),
                            (0.040, 0.240), (0.039, 0.268), (0.028, 0.292), (0, 0.302)], 6), 56)
    z, y = tete.v[:, 2], tete.v[:, 1]
    menton = (y < -0.018) & (z > 0.160)
    tete.teinte = np.where((z > 0.291)[:, None], np.asarray(CORNE), np.where(menton[:, None], np.asarray(CREME), np.asarray(CHATAIGNE)))

    def fine(v):
        s = v.copy()
        z, haut = v[:, 2], v[:, 1] > 0
        s[:, 0] *= 0.82 + 0.10 * gauss((z - 0.085) / 0.045)
        s[:, 1] *= np.where(haut, 0.92 + 0.06 * gauss((z - 0.070) / 0.040), 1.0 + 0.24 * gauss((z - 0.070) / 0.050))
        return s
    a.piece("tete", tete.sculpte(fine), None, mat=T)

    # ----- les yeux : vivants, haut sur les côtés, grands ouverts (mi-clos, l'auteur y lit de la tristesse) -----
    centre = T @ Vector((0, 0, 0.090))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.66, 0.46, 0.45)))     # plus en avant : de côté, un seul œil se voyait sur la fiche
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0215)       # visibles de profil et de face
        a.piece("lourde_" + nom, K.paupiere(0.0215, 0.60), SOMBRE, mat=A.cadre(pos + n * 0.003, n, T3 @ Vector((0, 1, -0.25))), poil=False)

    # ----- les oreilles : moyennes, en cornet, portées de côté sous la ramure ; le dedans crème -----
    po = A.profil([(0, 0), (0.022, 0.010), (0.032, 0.040), (0.029, 0.075), (0.013, 0.104), (0, 0.114)], 6)
    for nom, c in (("G", 1), ("D", -1)):
        vers = (T3 @ Vector((c * 0.86, 0.36, -0.30))).normalized()
        racine = T @ Vector((c * 0.052, 0.040, 0.030))
        E = A.cadre(racine - vers * 0.010, vers, T3 @ Vector((0, 0.15, 1)))
        a.piece("oreille_" + nom, A.tour(po, 32).etire(1.0, 0.42, 1.0), CHATAIGNE, mat=E)
        a.rustine("pavillon_" + nom, "oreille_" + nom, E @ Vector((0, 0, 0.050)), E.to_3x3() @ Vector((0, 1, 0)), 1.15, CREME, 0.002, 0)

    # ----- la ramure : deux merrains ivoire, leurs andouillers, une couronne au sommet -----
    for nom, c in (("G", 1), ("D", -1)):
        monde = lambda q: tuple(T @ (Vector((c * q[0], q[1], q[2])) * RAMURE + Vector((0, 0.008, 0.006))))
        # le merrain épais, brun noisette, perlé à la base (la meule), qui blanchit vers le haut ; des andouillers forts
        bois = K.tube_peint(A.courbe([monde(q) for q in MERRAIN], 8), lambda t: 0.060 - 0.030 * t + 0.014 * gauss(t / 0.05),
                            [(9, MERRAIN_BRUN)], 18)          # brun d'un bout à l'autre (son bout ivoire faisait une bague sous la couronne)
        for chemin, r0 in ANDOUILLERS:
            q0 = np.array(chemin[0])
            chemin = [tuple(q0 + (np.array(q) - q0) * ALLONGE * np.array([1.0, 1.45, 0.70])) for q in chemin]   # plus vers le ciel que vers nous : de face, ils faisaient des cônes
            bois = bois + K.tube_peint(A.courbe([monde(q) for q in chemin], 8), lambda t, r0=r0: 2.4 * r0 * (1 - 0.82 * t),
                                       [(0.78, MERRAIN_BRUN), (9, IVOIRE)], 14)    # pointus, la pointe ivoire
        a.piece("ramure_" + nom, bois, None, poil=False)       # « ramure » et pas « bois » : la vue de près ne vise que la tête

    # ----- la queue : courte, brun noir, plaquée sur le miroir crème -----
    queue = A.tour(A.profil([(0, 0), (0.030, 0.010), (0.034, 0.045), (0.022, 0.085), (0, 0.100)], 5), 24).etire(1.0, 0.55, 1.0)
    a.piece("queue", queue, CRIN, pos=(0, 0.300, 0.715), rot=A.viser((0, 0.40, -0.92)))

    # ----- les jambes : longues, fines au canon, la cuisse pleine. Il a fait un pas de l'antérieur gauche ;
    #       le postérieur gauche est resté en arrière. Les quatre sont posées. -----
    epaule = [0.098, 0.084, 0.064, 0.046, 0.035, 0.037, 0.032]     # fortes : fines, elles faisaient biche
    hanche = [0.120, 0.104, 0.062, 0.042, 0.035, 0.037, 0.032]
    pattes = (("avant_G", [(0.052, -0.210, 0.650), (0.082, -0.225, 0.530), (0.086, -0.250, 0.390), (0.088, -0.278, 0.270),
                           (0.088, -0.296, 0.150), (0.088, -0.310, 0.062), (0.088, -0.318, 0.034)], epaule, 0.55),
              ("avant_D", [(-0.052, -0.200, 0.650), (-0.082, -0.200, 0.530), (-0.086, -0.196, 0.390), (-0.088, -0.192, 0.270),
                           (-0.088, -0.190, 0.150), (-0.088, -0.188, 0.062), (-0.088, -0.188, 0.034)], epaule, 0.55),
              ("arriere_G", [(0.060, 0.215, 0.640), (0.090, 0.190, 0.500), (0.092, 0.250, 0.390), (0.090, 0.355, 0.270),
                             (0.090, 0.350, 0.150), (0.090, 0.344, 0.062), (0.090, 0.342, 0.034)], hanche, 0.50),
              ("arriere_D", [(-0.060, 0.205, 0.640), (-0.090, 0.170, 0.500), (-0.092, 0.200, 0.390), (-0.090, 0.280, 0.270),
                             (-0.090, 0.272, 0.150), (-0.090, 0.264, 0.062), (-0.090, 0.260, 0.034)], hanche, 0.50))
    for nom, points, rayons_, genou in pattes:
        a.piece("patte_" + nom, jambe(points, rayons_, genou), None)
        a.piece("sabot_" + nom, sabot(), CORNE, pos=(points[-1][0], points[-1][1] - 0.006, 0.0), poil=False)
    if TOURNE:
        tourner(a, TOURNE)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("cerf", styles.style_de("cerf"), sys.modules[__name__]), "Cerf")
