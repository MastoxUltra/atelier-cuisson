"""La girafe en peluche de magasin (2e dessin) : un jaune miel couvert de vraies plaques châtain à bords nets, cousues en
pavés polygonaux sur le fond clair (le corps, le cou et le haut des jambes) ; un long cou en courbe douce, la croupe
plus basse que le garrot, les genoux noueux, de longs cils, de petits yeux, deux ossicônes à houppette sombre, des
oreilles en feuille, une crinière en brosse brune, une queue à pinceau noir. Une dame qui n'a pas de hâte : le cou
infléchi en S, la tête penchée vers nous d'en haut, un œil par-dessus l'épaule, les antérieurs un peu écartés.

    python girafe.py        fabrique la fiche art/apercus/animaux/girafe.png (peluche de magasin, palier 4)
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

GONFLAGE = True       # la base aux volumes gonflés de l'Artiste (fusion.py) : jointures fondues, bouts arrondis

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
MIEL = np.array(M.hexa("#ffd070"))            # la dominante : jaune miel
CHATAIGNE = np.array(M.hexa("#b86a30"))       # l'accent : les plaques
CREME = np.array(M.hexa("#fff2d6"))           # le museau, le ventre, le bas des jambes
BRUN = M.hexa("#5a3a28")                      # la crinière, les houppes, le pinceau
CORNE = M.hexa("#3a2e2c")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=80, pas=PAS):
    """Une pièce tournée très finement échantillonnée : points = [(fraction de la longueur, rayon), ...]."""
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def paver(m, graine, taille, joint=0.020, clair=None):
    """Peint une pièce encore droite en pavés châtain à joints miel (un pavage de Voronoï : le plus proche de quelques
    graines tirées dans la boîte de la pièce ; le joint, là où deux graines sont presque à égale distance). clair(v) vrai :
    la crème des bas de jambes et du ventre, sans plaques."""
    rng = np.random.default_rng(graine)
    v = m.v
    lo, hi = v.min(axis=0), v.max(axis=0)
    n = int(np.clip(np.prod(np.maximum((hi - lo) / taille, 1.0)) * 1.6, 8, 160))
    graines = lo + rng.random((n, 3)) * (hi - lo)
    d = np.sort(np.linalg.norm(v[:, None, :] - graines[None, :, :], axis=2), axis=1)[:, :2]
    t = np.tile(CHATAIGNE, (len(v), 1))
    t[(d[:, 1] - d[:, 0]) < joint] = MIEL
    if clair is not None:
        t[clair(v)] = CREME
    m.teinte = t
    return m


def construire():
    a = K.Animal("girafe")
    a.taille = 5.00

    # ----- le corps : un tonneau élancé en pente (le garrot haut, la croupe basse), couché le long d'un fil -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.480, 1.000), (0.320, 1.040), (0.080, 1.090), (-0.140, 1.150), (-0.300, 1.190), (-0.380, 1.200))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.130), (0.15, 0.212), (0.40, 0.245), (0.70, 0.255), (0.90, 0.228), (1.0, 0.0)], L)
    paver(corps, 3, 0.22, 0.020, clair=lambda v: (np.abs(np.arctan2(v[:, 0], v[:, 1])) > 2.7))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou : long, en courbe douce, d'une seule pièce ; des pavés plus petits ; la crinière en brosse -----
    BASE = Vector((0.0, -0.250, 1.160))
    # 16/10 (l'auteur : « celle qui me perturbait le plus » ; d'après les vues d'une vraie girafe, CC-BY, rien d'importé) : le cou
    # presque droit, penché d'une vingtaine de degrés vers l'avant, au lieu du S bosselé ; plus mince à la base
    pts = ((0.0, 0.0), (0.095, 0.290), (0.190, 0.580), (0.280, 0.870), (0.355, 1.150))                       # (avance, monte)
    enc = K.Fil([tuple(BASE + Vector((0, -u, z))) for u, z in pts], (1, 0, 0))
    Lc = enc.long
    tab = [(0.0, 0.140), (0.10, 0.148), (0.30, 0.120), (0.60, 0.094), (0.85, 0.074), (1.0, 0.064)]     # le haut plus fin que la tête
    cou = fuseau(tab, Lc, 64)
    paver(cou, 5, 0.17, 0.016)
    a.piece("cou", cou.sculpte(lambda v: v * [0.86, 1.0, 1.0]).sculpte(enc.couche), None)
    for i, f in enumerate(np.linspace(0.04, 0.97, 24)):
        c_, av, nq = enc.cadre(f * Lc)
        r = float(np.interp(f, [q[0] for q in tab], [q[1] for q in tab]))
        e = A.boule(1.0, 10, 6).etire(0.012, 0.022, 0.034).pose(tuple(c_ + nq * r * 0.98 + np.array([0.0, 0.0, 0.0])))
        a.piece("crin_%02d" % i, e, BRUN, poil=False)

    # ----- la tête : petite, étroite, le museau crème ; penchée vers nous d'en haut ; deux ossicônes à houppe, les oreilles -----
    centre, avant, nuque = enc.cadre(Lc)
    # 16/10, 3e essai de la TÊTE (« pas encore à la hauteur ») : 20 % plus grande ; le museau en coin, large au front, qui
    # s'affine, le bout un peu élargi et aplati, deux narines en fente, une couture de bouche ; de gros yeux sous une paupière
    # (bord à 0,62 : l'œil ouvert) et quelques longs cils sombres ; tournée moins vers nous et les yeux plus en avant : de
    # trois quarts, le museau ne cache plus le second œil
    G_ = 1.20
    l, p = math.radians(10.0), math.radians(-10.0)                   # à peine tournée : de trois quarts, ses deux yeux se voient
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), math.sin(p)))
    T = A.cadre(Vector(centre) + Vector((0.0, -0.020, 0.040)), nez, Vector((0, 0, 1)))
    T3 = T.to_3x3()
    LT = 0.420 * G_
    tete = fuseau([(0.0, 0.0), (0.05, 0.064 * G_), (0.18, 0.086 * G_), (0.42, 0.072 * G_), (0.68, 0.060 * G_), (0.88, 0.056 * G_),
                   (0.96, 0.048 * G_), (1.0, 0.0)], LT, 56, 0.006)
    tete.teinte = np.where((np.arctan2(tete.v[:, 0], tete.v[:, 1]) > 2.5)[:, None], CREME, MIEL)
    tete.teinte[tete.v[:, 2] > 0.86 * LT] = MIEL * 0.82                             # le bout du museau, un ton plus sombre

    def coin(v):                                       # le coin : large au front, qui s'affine, le bout élargi et aplati
        s = v.copy()
        f = np.clip(v[:, 2] / LT, 0.0, 1.0)
        s[:, 0] = v[:, 0] * np.interp(f, [0.0, 0.25, 0.70, 0.90, 1.0], [0.98, 0.92, 0.74, 0.86, 0.84])
        s[:, 1] = v[:, 1] * np.interp(f, [0.0, 0.30, 0.70, 0.90, 1.0], [1.00, 1.00, 0.94, 0.74, 0.70])
        s[:, 1] -= np.where(v[:, 1] > 0, 0.10 * v[:, 1] * np.clip((f - 0.3) / 0.7, 0.0, 1.0), 0.0)     # le chanfrein droit
        return s
    RT = T @ A.repere((0, 0.040 * G_, -0.060 * G_))                                  # le repère de la tête : z vers le bout du museau
    RT3 = RT.to_3x3()
    a.piece("tete", tete.sculpte(coin), None, mat=RT)
    a.tete = RT @ Vector((0, 0.0, 0.50 * LT))
    a.paupieres_lourdes = "fines"                      # la base gonflée garde les paupières, fines, le bord à 0,60 au moins
    R_OEIL = 0.028
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", RT @ Vector((0.0, 0.010, 0.20 * LT)), RT3 @ Vector((c * 0.55, 0.40, 0.72)))   # plus en avant : vus de face et de trois quarts
        a.oeil("oeil_" + nom, pos + n * 0.004, n, R_OEIL)
        h = (Vector((0, 0, 1)) - n * n.z).normalized()
        a.piece("lourde_" + nom, K.paupiere(R_OEIL * 1.15, 0.62), tuple(MIEL), mat=A.cadre(pos + n * 0.005, n, h), poil=False)
        cote_ = h.cross(n).normalized()
        for k, ang in enumerate((50.0, 75.0, 100.0, 125.0)):                       # quatre longs cils sombres sur le haut
            r_ = math.radians(ang if c > 0 else 180.0 - ang)
            bord = pos + n * 0.010 + (cote_ * math.cos(r_) + h * math.sin(r_)) * R_OEIL * 1.05
            sort = (cote_ * math.cos(r_) + h * math.sin(r_)).normalized()
            pts = [bord, bord + sort * 0.014 + n * 0.006, bord + sort * 0.028 + n * 0.004 + h * 0.008]
            cil = A.tube(A.courbe([tuple(q) for q in pts], 4), lambda t_: 0.0026 * (1.0 - 0.6 * t_), 8)
            a.piece("cils_%s%d" % (nom, k), cil, (0.10, 0.07, 0.05), poil=False)
        # les narines en fente, sur le dessus du bout du museau, un peu de biais
        pn, nn = a.surface("tete", RT @ Vector((0.0, 0.0, 0.88 * LT)), RT3 @ Vector((c * 0.45, 0.80, 0.30)))
        fente = A.boule(1.0, 12, 6).etire(0.0045, 0.0130, 0.0030)
        a.piece("narine_" + nom, fente, tuple(np.array(BRUN) * 0.8), mat=A.cadre(pn + nn * 0.001, nn, RT3 @ Vector((c * 0.35, 0.0, 1.0))), poil=False)
        oss = A.tour(A.profil([(0, 0), (0.024, 0.006), (0.020, 0.050), (0.015, 0.088), (0, 0.102)], 5), 18)      # courts, comme une vraie
        a.piece("ossicone_" + nom, oss, tuple(MIEL), mat=A.cadre(T @ Vector((c * 0.030 * G_, 0.092 * G_, -0.040 * G_)), Vector((c * 0.10, 0.20, 0.97)), (0, 1, 0)))
        a.piece("houppe_" + nom, A.boule(1.0, 16, 8).etire(0.022, 0.022, 0.022), BRUN,
                pos=tuple(T @ Vector((c * 0.034 * G_, 0.108 * G_, -0.040 * G_)) + Vector((c * 0.008, 0.016, 0.080))))
        po = A.profil([(0, 0), (0.030, 0.008), (0.040, 0.032), (0.030, 0.060), (0.010, 0.078), (0, 0.084)], 5)
        E = A.cadre(T @ Vector((c * 0.064 * G_, 0.056 * G_, -0.034 * G_)), Vector((c * 0.95, 0.10, 0.28)), (0, 0, 1))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 24).etire(1.10, 0.36, 1.15), [(0.060, tuple(MIEL)), (9, BRUN)]), None, mat=E)   # plus petites
    # la couture de la bouche, qui fait le tour du bout du museau, en bas
    bouche = a.trace("tete", RT @ Vector((0.0, -0.012 * G_, 0.80 * LT)),
                     [RT3 @ Vector((math.sin(th), -0.55, math.cos(th))) for th in np.linspace(-1.35, 1.35, 9)], 0.002)
    if len(bouche) > 1:
        a.broderie("bouche", A.courbe(bouche, 4), 0.0030, M.hexa("#3a2618"))

    # ----- les jambes : quatre longues, fines, les genoux noueux ; pavés en haut, crème en bas ; les sabots sombres -----
    def jambe(depart, plan, graine):
        x, y, z = depart
        pts = [(x, y + dy, z - dz) for dy, dz in plan]
        f = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, 0.092), (0.20, 0.072), (0.42, 0.046), (0.50, 0.060), (0.57, 0.044), (0.90, 0.040), (0.96, 0.048), (1.0, 0.0)], f.long, 36, 0.010)   # genoux moins noueux
        paver(m, graine, 0.13, 0.016, clair=lambda v: v[:, 2] > 0.80 * f.long)
        return m.sculpte(f.couche), pts[-1], pts[len(pts) // 2 + 0]
    pieds = []
    for nom, dep, plan, g in (("av_G", (0.130, -0.150, 1.040), [(0.0, 0.0), (0.0, 0.33), (-0.01, 0.62), (0.0, 0.86), (-0.01, 1.04)], 11),
                              ("av_D", (-0.130, -0.150, 1.040), [(0.0, 0.0), (-0.01, 0.33), (-0.03, 0.62), (-0.04, 0.86), (-0.04, 1.04)], 12),
                              ("ar_G", (0.140, 0.420, 0.980), [(0.0, 0.0), (-0.03, 0.30), (-0.07, 0.56), (0.03, 0.80), (0.02, 0.98)], 13),
                              ("ar_D", (-0.140, 0.420, 0.980), [(0.0, 0.0), (-0.03, 0.30), (-0.07, 0.56), (0.03, 0.80), (0.02, 0.98)], 14)):
        m, bout, genou = jambe(dep, plan, g)
        a.piece("jambe_" + nom, m, None)
        a.piece("sabot_" + nom, A.boule(1.0, 24, 12).etire(0.048, 0.060, 0.034), CORNE, pos=(bout[0], bout[1] - 0.010, 0.032), poil=False)
    queue = A.tube(A.courbe([(0.0, 0.520, 1.010), (0.0, 0.580, 0.850), (0.0, 0.590, 0.600)], 5), 0.018, 12)
    a.piece("queue", queue, tuple(MIEL))
    a.piece("pinceau", A.boule(1.0, 20, 10).etire(0.040, 0.040, 0.110), BRUN, pos=(0, 0.592, 0.520))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("girafe", styles.style_de("girafe"), sys.modules[__name__]), "Girafe")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py girafe). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.973                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.239, 1.114)),
    ('cou', 'corps', (0.000, -0.098, 1.280)),
    ('tete', 'cou', (0.010, -0.630, 2.340)),                     # 16/10 : le cou droit, la tête plus en avant, un peu plus bas
    ('oreille_G', 'tete', (0.075, -0.612, 2.424)),
    ('patte_av_G', 'corps', (0.130, -0.146, 1.002)),
    ('patte_ar_G', 'corps', (0.140, 0.411, 0.944)),
    ('queue', 'corps', (-0.001, 0.514, 1.002)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('jambe_av', 'patte_av', True), ('jambe_ar', 'patte_ar', True), ('ossicone', 'corps'),
    ('sabot_av', 'patte_av', True), ('sabot_ar', 'patte_ar', True), ('oreille', 'oreille', True),
    ('crin_00', 'corps'), ('crin_01', 'corps'), ('crin_02', 'corps'), ('crin_03', 'corps'), ('crin_04', 'corps'),
    ('crin_05', 'corps'), ('crin_06', 'corps'), ('crin_07', 'corps'), ('crin_08', 'corps'), ('crin_09', 'corps'),
    ('crin_10', 'corps'), ('crin_11', 'corps'), ('crin_12', 'corps'), ('crin_13', 'corps'), ('crin_14', 'corps'),
    ('crin_15', 'corps'), ('crin_16', 'corps'), ('crin_17', 'corps'), ('crin_18', 'corps'), ('crin_19', 'corps'),
    ('crin_20', 'corps'), ('crin_21', 'corps'), ('crin_22', 'corps'), ('crin_23', 'corps'), ('pinceau', 'queue'),
    ('houppe', 'corps'), ('corps', 'corps'), ('queue', 'queue'), ('tete', 'tete'), ('oeil', 'tete'), ('cou', 'cou'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
    ('lourde', 'tete'), ('cils', 'tete'), ('narine', 'tete'), ('bouche', 'tete'),            # 16/10 : la tête refaite
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
    pas = 18.0
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
    p.add('corps', rot=(34 * bas + 3 * coups, 0, 0))
    p.paire('patte_av', rot=(-30 * bas, 0, 0))
    p.add('tete', rot=(16 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.292 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.02), rot=(36, 0, 6), ech=(1 + 0.010 * r, 1, 1 + 0.020 * r))
    p.paire('patte_av', rot=(-30, 0, 0))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
