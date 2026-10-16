"""Le zèbre en peluche de velours ras (3e dessin) : un blanc franc zébré de rayures charbon nettes qui suivent le corps
(elles partent de l'échine, descendent en s'infléchissant vers l'arrière et s'effilent en pointe sous le ventre ; sur
la croupe elles tournent en arcs ; sur le cou elles sont obliques ; sur le museau elles sont fines et serrées), une
longue tête de cheval, le museau gris sombre, de petits yeux, une crinière en brosse droite noire et blanche, des
jambes à bracelets, la queue à houppe noire. Tête haute, il renâcle : le cou arqué, les naseaux dilatés, une jambe
avant levée qui racle le sol, la queue qui fouette.

    python zebre.py        fabrique la fiche art/apercus/animaux/zebre.png (velours ras, palier 3)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K

BLANC = np.array(M.hexa("#fffdf6"))           # la dominante : blanc franc
CHARBON = np.array(M.hexa("#26222a"))         # l'accent : les rayures
GRIS = np.array(M.hexa("#6a6064"))            # le museau
SABOT = M.hexa("#3a3436")
PAS = 0.007                                   # l'écart entre deux anneaux : assez fin pour que les rayures soient nettes


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    """Une pièce tournée très finement échantillonnée : points = [(fraction de la longueur, rayon), ...]."""
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def rayer(m, phase, seuil, ventre=0.80):
    """Peint une pièce tournée droite : blanc, et charbon là où frac(phase(z, u)) est sous seuil(z, u) ; u = l'écart au
    dos (0 sur l'échine, 1 sous le ventre). Les rayures s'effilent : le seuil baisse vers le ventre."""
    x, y, z = m.v[:, 0], m.v[:, 1], m.v[:, 2]
    u = np.abs(np.arctan2(x, y)) / math.pi
    f = phase(z, u) % 1.0
    noir = f < np.maximum(seuil(z, u), 0.0)
    t = np.tile(BLANC, (len(z), 1))
    t[noir & (u < ventre)] = CHARBON
    m.teinte = t
    return m


def construire():
    a = K.Animal("zebre_p98")
    a.taille = 2.40

    # ----- le corps : un tonneau élancé couché le long d'un fil (la croupe ronde, le garrot haut) ; rayures qui partent de
    #       l'échine, s'infléchissent vers l'arrière et s'effilent sous le ventre ; sur la croupe elles tournent en arcs -----
    chemin = [(0.0, y, z) for y, z in ((0.560, 0.640), (0.440, 0.690), (0.200, 0.700), (-0.050, 0.700), (-0.290, 0.720), (-0.450, 0.720))]
    fil = K.Fil(chemin, (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.03, 0.078), (0.12, 0.130), (0.30, 0.140), (0.55, 0.138), (0.80, 0.146), (0.94, 0.118), (1.0, 0.0)], L)   # un corps plus mince (l'auteur : « trop gros »)

    def phase(z, u):
        sw = 0.075 * u ** 1.6 + 0.020 * np.exp(-((z - 0.20 * L) / 0.15) ** 2) * u        # vers l'arrière en descendant ; arcs sur la croupe
        return (z + sw) / 0.115

    def seuil(z, u):
        large = 0.50 + 0.08 * np.sin(z * 17.0)                                              # des rayures de largeur variable
        return large * (1.0 - 0.80 * u ** 1.4)
    rayer(corps, phase, seuil)
    a.piece("corps", corps.sculpte(lambda v: v * [1.04, 1.0, 1.0]).sculpte(fil.couche), None)

    # ----- le cou : arqué, haut ; les rayures y sont obliques ; la crinière en brosse droite, noire et blanche -----
    BASE = Vector((0.0, -0.310, 0.750))
    enc = K.Fil([tuple(BASE + Vector((0, -u, z))) for u, z in ((0.0, 0.0), (0.030, 0.140), (0.080, 0.290), (0.140, 0.400), (0.200, 0.470))], (1, 0, 0))
    Lc = enc.long
    cou = fuseau([(0.0, 0.10), (0.10, 0.125), (0.25, 0.112), (0.5, 0.092), (0.8, 0.078), (1.0, 0.070)], Lc, 56)
    rayer(cou, lambda z, u: (z + 0.060 * u) / 0.085, lambda z, u: 0.52 * (1.0 - 0.55 * u ** 1.5), ventre=0.86)
    a.piece("cou", cou.sculpte(lambda v: v * [0.82, 1.0, 1.0]).sculpte(enc.couche), None)
    for i, f in enumerate(np.linspace(0.05, 0.97, 18)):
        c_, av, nq = enc.cadre(f * Lc)
        r = float(np.interp(f, [0.0, 0.10, 0.25, 0.5, 0.8, 1.0], [0.10, 0.150, 0.138, 0.108, 0.088, 0.078]))
        pied = c_ + nq * r * 0.96
        brin = A.boule(1.0, 12, 6).etire(0.012, 0.022, 0.078).pose(tuple(pied + nq * 0.050))
        a.piece("crin_%02d" % i, brin, tuple(CHARBON if i % 2 == 0 else BLANC), poil=False)

    # ----- la tête : longue, de cheval, tenue haute, le museau gris ; les rayures fines et serrées ; petits yeux -----
    centre, avant, nuque = enc.cadre(Lc)
    l, p = math.radians(30.0), math.radians(-42.0)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), math.sin(p)))
    T = A.cadre(Vector(centre) + Vector((0, 0.030, 0.040)), nez, Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.05, 0.070), (0.20, 0.090), (0.45, 0.074), (0.68, 0.062), (0.84, 0.066), (0.96, 0.056), (1.0, 0.0)], 0.360, 48)
    rayer(tete, lambda z, u: (z + 0.030 * u) / 0.050, lambda z, u: 0.50 * (1.0 - 0.5 * u), ventre=0.84)
    tete.teinte[tete.v[:, 2] > 0.280] = GRIS
    a.piece("tete", tete.sculpte(lambda v: v * [0.86, 1.0, 1.0]), None, mat=T @ A.repere((0, 0.060, -0.050), (0, 0, 0)))
    a.tete = T @ Vector((0, 0.060, 0.100))                          # on vise le milieu de la tête : la caméra de la vue de tête recule
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", T @ Vector((0, 0.050, 0.110)), T3 @ Vector((c * 0.46, 0.58, 0.68)))
        # (le cerne noir est retiré : il se lisait comme d'énormes yeux autour du museau)
        a.oeil("oeil_" + nom, pos + n * 0.008, n, 0.0300)
        po = A.profil([(0, 0), (0.026, 0.012), (0.036, 0.050), (0.028, 0.092), (0.010, 0.120), (0, 0.130)], 6)
        vers = Vector((c * 0.22, 0.22, 0.95)).normalized()
        E = A.cadre(T @ Vector((c * 0.052, 0.098, -0.026)) - vers * 0.012, vers, Vector((c * 0.5, -0.9, 0.0)))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 28).etire(1.0, 0.45, 1.0), [(0.060, tuple(CHARBON)), (9, tuple(BLANC))]), None, mat=E)
    for nom, c in (("G", 1), ("D", -1)):                  # les naseaux dilatés : deux ovales sombres cousues sur le bout du museau
        a.rustine("naseau_" + nom, "tete", T @ Vector((0, 0.060, 0.200)), T3 @ Vector((c * 0.34, 0.10, 0.94)), 0.17, tuple(CHARBON), 0.0025, 0)
    a.piece("toupet", A.boule(1.0, 12, 6).etire(0.010, 0.016, 0.040), tuple(CHARBON), mat=T @ A.repere((0, 0.138, 0.068), (-20, 0, 0)), poil=False)

    # ----- les jambes : fines, en bracelets noirs et blancs, le genou et le boulet marqués, les sabots noirs ;
    #       l'antérieur gauche levé : il racle le sol -----
    def jambe(points, r0):
        ch = A.courbe(points, 8)
        fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(ch, axis=0), axis=1))])
        n = max(int(fait[-1] / 0.040), 2)
        bandes = [((k + 1) / n, tuple(CHARBON) if k % 2 else tuple(BLANC)) for k in range(n)]
        return K.tube_peint(ch, lambda t: r0 * (1 - 0.40 * t) + 0.012 * math.exp(-((t - 0.50) / 0.08) ** 2) + 0.010 * math.exp(-((t - 0.88) / 0.05) ** 2),
                            bandes, 18)
    plantees = (("av_D", [(-0.110, -0.320, 0.640), (-0.118, -0.330, 0.480), (-0.118, -0.322, 0.300), (-0.116, -0.330, 0.050)], 0.062),
                ("ar_G", [(0.120, 0.420, 0.620), (0.135, 0.380, 0.470), (0.132, 0.440, 0.300), (0.130, 0.420, 0.050)], 0.074),
                ("ar_D", [(-0.120, 0.420, 0.620), (-0.135, 0.380, 0.470), (-0.132, 0.440, 0.300), (-0.130, 0.420, 0.050)], 0.074))
    for nom, pts, r0 in plantees:
        a.piece("patte_" + nom, jambe(pts, r0), None)
        a.piece("sabot_" + nom, A.boule(1.0, 24, 12).etire(0.048, 0.060, 0.034), SABOT, pos=(pts[-1][0], pts[-1][1] - 0.010, 0.032), poil=False)
    levee = [(0.110, -0.320, 0.640), (0.118, -0.350, 0.500), (0.120, -0.450, 0.440), (0.120, -0.500, 0.300)]
    a.piece("patte_av_G", jambe(levee, 0.062), None)
    a.piece("sabot_av_G", A.boule(1.0, 24, 12).etire(0.048, 0.060, 0.034), SABOT, pos=(0.120, -0.520, 0.270), rot=(-48, 0, 0), poil=False)

    # ----- la queue : un fouet fin, rayé, à houppe noire, qui balaie un côté -----
    chemin = [(0.0, 0.540, 0.640), (0.070, 0.620, 0.520), (0.120, 0.640, 0.360)]
    a.piece("queue", A.tube(A.courbe(chemin, 5), 0.016, 12), tuple(BLANC))
    a.piece("houppe", A.boule(1.0, 24, 12).etire(0.032, 0.040, 0.100), tuple(CHARBON), pos=(0.130, 0.640, 0.270), rot=(0, -10, 0))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("zebre_p98", styles.style_de("zebre"), sys.modules[__name__]), "Zèbre (planche 98)")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py zebre). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.620                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.351, 0.772)),
    ('cou', 'corps', (-0.000, -0.201, 0.841)),
    ('tete', 'cou', (0.034, -0.520, 1.192)),
    ('oreille_G', 'tete', (0.066, -0.499, 1.341)),
    ('patte_av_D', 'corps', (-0.114, -0.325, 0.623)),
    ('patte_ar_G', 'corps', (0.130, 0.390, 0.609)),
    ('patte_av_G', 'corps', (0.115, -0.329, 0.629)),
    ('queue', 'corps', (0.006, 0.531, 0.639)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True),
    ('sabot_av', 'patte_av', True), ('sabot_ar', 'patte_ar', True), ('oreille', 'oreille', True),
    ('crin_00', 'corps'), ('crin_02', 'corps'), ('crin_04', 'corps'), ('crin_06', 'corps'), ('crin_08', 'corps'),
    ('crin_10', 'corps'), ('crin_12', 'corps'), ('crin_14', 'corps'), ('crin_16', 'corps'), ('crin_01', 'corps'),
    ('crin_03', 'corps'), ('crin_05', 'corps'), ('crin_07', 'corps'), ('crin_09', 'corps'), ('crin_11', 'corps'),
    ('crin_13', 'corps'), ('crin_15', 'corps'), ('crin_17', 'corps'), ('naseau', 'tete'), ('toupet', 'corps'),
    ('houppe', 'corps'), ('corps', 'corps'), ('cerne', 'tete'), ('queue', 'queue'), ('tete', 'tete'),
    ('oeil', 'tete'), ('cou', 'cou'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
    ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('cou', rot=(2 * r, 0, 8 * g - 6 * d))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add('oreille_G', rot=(0, 0, 20 * cloche(t, 0.50, 0.05) - 8 * g))
    p.add('oreille_D', rot=(0, 0, -20 * cloche(t, 0.88, 0.05) + 6 * d))
    p.add('queue', rot=(0, 0, 10 * onde(t, 1)))
    p.ouvert = borne(1 - 0.3 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.62, 0.02))
    return p


def avance(t):
    """Sa marche : les pattes alternent, le corps oscille, la tête dodeline."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 26.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('cou', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('tete', rot=(3 - 2 * onde(t, 2, -0.2), -2 * c, -2 * s))
    p.paire('oreille', rot=(-8 + 3 * onde(t, 2, -0.25), 0, 0))
    p.add('queue', rot=(-6, 0, -10 * s))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('cou', rot=(34 * bas + 4 * coups, 0, 5 * leve))
    p.add('tete', rot=(18 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.paire('oreille', rot=(-6 * bas + 5 * leve, 0, 0))
    p.add('queue', rot=(0, 0, -7 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.186 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.341), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
