"""Le pic-vert en peluche : le dos et les ailes vert anis, très jaune et très vif (c'est la seule bête verte du jardin :
il ne faut pas qu'il se fonde dans l'herbe), une calotte rouge vif de la nuque au front qui finit en huppe, un masque
noir autour de l'œil, une moustache noire, la gorge et le ventre crème, le croupion jaune d'or, le bout des ailes barré
de noir et de crème. Un bûcheron entêté : dressé à la verticale, calé sur sa queue raide comme sur un trépied, le poitrail
en avant, la tête rejetée en arrière, son long bec gris levé comme une cognée, prêt à frapper.

    python pic_vert.py        fabrique la fiche art/apercus/animaux/pic_vert.png
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

ANIS = M.hexa("#dfea34")                      # le vert anis du dos et des ailes : presque jaune, loin du vert de l'herbe (le poil le verdit)
ROUGE = M.hexa("#e62a1e")                     # la calotte
SUIE = M.hexa("#1c1a1f")                      # le masque, la moustache, les barres des ailes, la queue (la feutrine sort plus claire)
ACIER = M.hexa("#8a909e")                     # le bec
PLOMB = M.hexa("#666b78")                     # les pattes

# Sur la fiche, il était posé de biais (TOURNE = -38), presque de profil : son bec en poignard et son aplomb s'y lisaient
# mieux. Pour le jeu, il regarde droit devant (vers -Y) : TOURNE = 0.
TOURNE = 0
LOC = A.repere((0, 0, 0), (0, 0, TOURNE))

# Le fil du corps, du croupion au cou : il monte droit, le poitrail en avant, puis le cou part en arrière.
DOS = [(0.0, 0.070, 0.045), (0.0, 0.030, 0.13), (0.0, 0.0, 0.21), (0.0, 0.012, 0.285), (0.0, 0.050, 0.345), (0.0, 0.095, 0.385)]
GALBE = [(0.0, 0.0), (0.04, 0.032), (0.15, 0.054), (0.35, 0.072), (0.58, 0.088), (0.76, 0.080), (0.89, 0.060), (0.96, 0.046), (1.0, 0.0)]
TETE = Vector((0.0, 0.115, 0.440))
PORT = LOC @ A.repere(TETE, (-30, 5, 14))     # la tête : rejetée en arrière, le bec levé, un rien tournée vers nous
CENTRE = PORT @ Vector((0, 0, 0))


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def fil(chemin, flanc=None):
    """Prépare un chemin lissé : rend sa longueur, et repere(s) -> (centre, avant, dos, côté gauche) à la distance s
    du départ. Sans « flanc », le dos de la pièce cherche le ciel. Avec, c'est son côté gauche qui cherche cette
    direction : pour un corps debout, dont le fil passe par la verticale."""
    pts = A.courbe(chemin, 16)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    sens = np.gradient(pts, fait, axis=0)

    def repere(s):
        s = np.asarray(s, float)
        centre = np.stack([np.interp(s, fait, pts[:, k]) for k in range(3)], axis=-1)
        avant = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
        if flanc is None:
            dos = np.array([0.0, 0.0, 1.0]) - avant[..., 2:3] * avant
            dos = dos / np.linalg.norm(dos, axis=-1, keepdims=True)
            return centre, avant, dos, np.cross(dos, avant)
        cote = np.asarray(flanc, float) - (avant @ np.asarray(flanc, float))[..., None] * avant
        cote = cote / np.linalg.norm(cote, axis=-1, keepdims=True)
        return centre, avant, np.cross(avant, cote), cote
    return float(fait[-1]), repere


def couche(repere, long):
    """Pour sculpte() : couche le long d'un fil une pièce tournée toute droite (son X : la gauche, son Y : le dos)."""
    def f(v):
        centre, _avant, dos, cote = repere(np.clip(v[:, 2], 0.0, long))
        return centre + v[:, 0:1] * cote + v[:, 1:2] * dos
    return f


def manteau(m, cotes, large, dessus, dessous, n, eps=0.012):
    """Peint une pièce tournée encore droite (son +Y est le dos) en deux tissus : le manteau « dessus » couvre le dos
    sur large(z) radians de part et d'autre de sa ligne, le « dessous » fait le reste (le plastron). Les méridiens
    sont tournés pour que la limite tombe pile entre deux méridiens serrés : elle reste nette, sur le tissu comme sur
    le poil. n : le nombre de méridiens donnés, de chaque côté, au manteau."""
    quart, demi = cotes // 4, cotes // 2
    m.teinte = np.tile(np.asarray(dessous, float), (len(m.v), 1))
    for anneau in m.anneaux:
        if len(anneau) == 1:
            m.teinte[anneau[0]] = dessus
            continue
        bord = min(max(float(large(m.v[anneau[0], 2])), 4 * eps), math.pi - 6 * eps)
        ecart = np.concatenate([np.linspace(0.0, bord - eps, n + 1), np.linspace(bord + eps, math.pi, demi - n)])
        r = np.hypot(m.v[anneau, 0], m.v[anneau, 1])
        for j, i in enumerate(anneau):
            k = (j - quart) % cotes
            signe = 1.0 if k <= demi else -1.0
            k = min(k, cotes - k)
            angle = math.pi / 2 + signe * ecart[k]
            m.v[i, 0], m.v[i, 1] = r[j] * math.cos(angle), r[j] * math.sin(angle)
            if k <= n:
                m.teinte[i] = dessus
    return m


def table(points, long=1.0):
    """Une fonction de z qui suit une table [(fraction de la longueur, valeur), ...]."""
    f, val = zip(*points)
    return lambda z: float(np.interp(z / long, f, val))


def penne(long, large, epais, bandes, pointe=0.0):
    """Une plume ou une aile debout sur son pied (son axe Z), peinte par bandes nettes : « bandes » donne (jusqu'où,
    de 0 à 1 ; la couleur). pointe = 0 : un galet au bout rond ; pointe = 0,5 : la moitié du bout s'effile en pointe.
    Deux tours serrés de part et d'autre de chaque limite : les barres restent nettes."""
    u = np.linspace(0.0, 1.0, 37)
    cotes = sorted(set(((1 - np.cos(math.pi * u)) / 2).round(5).tolist() + [f + e for f, _c in bandes[:-1] for e in (-0.004, 0.004)]))

    def demi(t):
        if t <= 0.0 or t >= 1.0:
            return 0.0
        if pointe:
            return math.sqrt(min(1.0, t / 0.12)) * min(1.0, (1 - t) / pointe) ** 0.9
        return (4 * t * (1 - t)) ** 0.45 * (1 - 0.30 * t)
    m = A.tour([(large * demi(t), long * t) for t in cotes], 24).etire(1.0, epais / large, 1.0)
    return K.bandes(m, [(long * f, c) for f, c in bandes])


def ovale(grand, petit, penche):
    """La forme d'une rustine en ovale : son grand axe penché de « penche » radians (0 : à l'horizontale)."""
    return lambda th: grand * petit / math.hypot(petit * math.cos(th - penche), grand * math.sin(th - penche))


def patte():
    """Une patte de grimpeur en feutrine : un canon court, deux doigts devant, deux derrière."""
    def doigt(degres, long):
        t = math.radians(degres)
        return A.boule(1.0, 16, 8).etire(0.0095, long, 0.0085).pose((long * 0.8 * math.sin(t), -long * 0.8 * math.cos(t), 0.0085), (0, 0, degres))
    return doigt(-24, 0.030) + doigt(22, 0.033) + doigt(150, 0.023) + doigt(-155, 0.025) + A.tube([(0, 0.058, 0.090), (0, 0.005, 0.010)], 0.013, 12)


def construire():
    a = K.Animal("pic_vert")
    a.taille = 0.40
    a.tete = PORT @ Vector((0, -0.090, 0.0))

    # ----- le corps : une longue poire dressée le long de son fil, le poitrail bombé. Le manteau anis couvre le dos,
    #       le plastron crème monte du bas-ventre à la gorge, et le croupion est jaune d'or -----
    long, dos = fil(DOS, flanc=(1, 0, 0))
    croupion = (0.07 * long, 0.47 * long)
    prof = A.profil([(r, f * long) for f, r in GALBE], 8)
    cotes = sorted(set(np.linspace(0.0, long, 64).tolist() + [z + e for z in croupion for e in (-0.0015, 0.0015)]))
    corps = A.tour([(0.0, 0.0)] + [(float(np.interp(z, prof[:, 1], prof[:, 0])), z) for z in cotes[1:-1]] + [(0.0, long)], 64)
    manteau(corps, 64, table([(0.0, 2.45), (0.15, 2.28), (0.45, 2.16), (0.75, 2.16), (1.0, 2.22)], long), ANIS, K.CREME, 19)
    jaune = (corps.v[:, 2] > croupion[0]) & (corps.v[:, 2] < croupion[1]) & (np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1])) < 1.30)
    corps.teinte[jaune] = K.JAUNE

    def bombe(v):                                         # le poitrail en avant, comme un torse de bûcheron
        s = v.copy()
        s[:, 1] *= np.where(v[:, 1] < 0, 1 + 0.22 * np.exp(-((v[:, 2] / long - 0.64) / 0.20) ** 2), 1.0)
        return s
    corps.sculpte(bombe)
    a.piece("corps", corps.sculpte(couche(dos, long)), None, mat=LOC)
    # les deux coutures d'assemblage : là où le manteau anis rejoint le plastron crème (19 méridiens de part et d'autre du dos)
    a.couture("lisiere_G", "corps", 16 - 19, 0.16, 0.88)
    a.couture("lisiere_D", "corps", 16 + 19, 0.16, 0.88)

    # ----- la tête : une boule peinte par tranches (la gorge crème, les joues anis, la calotte rouge), posée penchée
    #       pour que le rouge descende sur la nuque ; la calotte finit en huppe : avec le bec, la tête fait un marteau.
    #       Dans la pièce : X la gauche, Y l'arrière, Z le dessus -----
    seuils = (-0.42, 0.15)
    tranches = sorted(set((-np.cos(np.linspace(0.0, math.pi, 29))).round(5).tolist() + [s + e for s in seuils for e in (-0.012, 0.012)]))
    tete = K.bandes(A.tour([(math.sqrt(max(0.0, 1 - z * z)), z) for z in tranches], 48), [(seuils[0], K.CREME), (seuils[1], ANIS), (9, ROUGE)])

    def crane(v):
        v = K.bosse(v, (0, 0.80, 0.60), 0.85, 0.075)
        return v * [0.070, 0.078, 0.068]
    a.piece("tete", tete.sculpte(crane), None, mat=PORT @ A.repere((0, 0, 0), (-18, 0, 0)))

    # ----- le masque noir, l'œil cerclé de crème au milieu (sur le noir, le bouton ne se verrait pas), la moustache -----
    for nom, cote in (("_G", 1), ("_D", -1)):
        penche = (lambda t: t) if cote > 0 else (lambda t: math.pi - t)
        regard = vers(0.80 * cote, -0.52, 0.12)
        a.rustine("masque" + nom, "tete", CENTRE, vers(0.72 * cote, -0.64, 0.08), ovale(0.64, 0.34, penche(0.30)), SUIE, 0.003, 0)
        a.rustine("cerne" + nom, "tete", CENTRE, regard, 0.39, K.CREME, 0.005, 0)
        p, n = a.surface("tete", CENTRE, regard)
        a.bouton("oeil" + nom, p + n * 0.005, n, 0.021)
        a.rustine("moustache" + nom, "tete", CENTRE, vers(0.56 * cote, -0.62, -0.62), ovale(0.46, 0.14, penche(-0.52)), SUIE, 0.003, 0)

    # ----- le bec : un long poignard de feutrine grise, plus haut que large -----
    pointe = vers(0, -1, -0.04)
    p, n = a.surface("tete", CENTRE, vers(0, -1, -0.10))
    bec = A.tour(A.profil([(0, 0), (0.031, 0.007), (0.029, 0.040), (0.019, 0.100), (0.008, 0.150), (0.002, 0.165), (0, 0.167)], 6), 28).etire(0.80, 1.0, 1.0)
    a.piece("bec", K.bandes(bec, [(0.108, ACIER), (9, PLOMB)]), None, mat=A.cadre(p - pointe * 0.018, pointe, vers(0, 0, 1)), poil=False)

    # ----- les ailes : deux longs galets anis couchés sur les flancs, le bout barré de noir et de crème -----
    barres = [(0.56, ANIS), (0.65, SUIE), (0.72, K.CREME), (0.81, SUIE), (0.88, K.CREME), (1.0, SUIE)]
    for nom, cote in (("_G", 1), ("_D", -1)):
        c0, _a, d0, g0 = dos(0.76 * long)
        c1, _a, d1, g1 = dos(0.08 * long)
        epaule = Vector(c0 + (g0 * (0.92 * cote) + d0 * 0.25) * 0.080)
        bout = Vector(c1 + (g1 * (0.86 * cote) + d1 * 0.52) * 0.058)
        flanc = Vector((0.94 * cote, 0.34, 0.0))
        a.piece("aile" + nom, penne((bout - epaule).length, 0.062, 0.025, barres), None,
                mat=LOC @ A.cadre(epaule, bout - epaule, flanc))
        a.couture("aile" + nom, "aile" + nom, 0 if cote > 0 else 12, 0.10, 0.55, "droit")

    # ----- la queue : quatre plumes raides et pointues en feutrine noire, plantées dans l'herbe : il s'y adosse -----
    racine, _a, d, _g = dos(0.07 * long)
    racine = Vector(racine + d * 0.020)
    queue = None
    for degres, portee in ((-24, 0.140), (-8, 0.165), (8, 0.165), (24, 0.140)):
        t = math.radians(degres)
        pied = racine + Vector((0.016 * math.sin(t) / 0.36, 0, 0))
        cible = Vector((racine.x + portee * math.sin(t), racine.y + portee * math.cos(t), 0.005))
        plume = penne((cible - pied).length, 0.030, 0.0055, [(0.22, ANIS), (1.0, SUIE)], pointe=0.55)
        z = (cible - pied).normalized()
        y = (Vector((0, 0.6, 0.8)) - z * Vector((0, 0.6, 0.8)).dot(z)).normalized()
        plume.v = np.outer(plume.v[:, 0], np.array(y.cross(z))) + np.outer(plume.v[:, 1], np.array(y)) + np.outer(plume.v[:, 2], np.array(z)) + np.array(pied)
        queue = plume if queue is None else queue + plume
    a.piece("queue", queue, None, mat=LOC, poil=False)

    # ----- les pattes : courtes, en feutrine gris plomb, plantées devant lui, deux doigts devant et deux derrière -----
    a.piece("patte_G", patte(), PLOMB, mat=LOC @ A.repere((0.048, -0.020, 0.0), (0, 0, 12)), poil=False)
    a.piece("patte_D", patte(), PLOMB, mat=LOC @ A.repere((-0.048, -0.020, 0.0), (0, 0, -12)), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py pic_vert)

from poses import Pose, borne, cloche, onde

# Le corps est une seule pièce, du croupion au cou : il plie à la taille. Le bas suit « corps » (les hanches, la queue),
# le haut suit « buste » (le poitrail, les ailes, la tête). Les pattes pendent à la racine : posées, elles ne bougent pas.
OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.040, 0.100)),          # les hanches, au-dessus des pattes
    ("buste", "corps", (0, 0.008, 0.200)),           # la taille : il s'y plie pour frapper, s'y renverse pour rire
    ("tete", "buste", (0, 0.100, 0.400)),            # la nuque, sous la tête
    ("aile_G", "buste", (0.064, 0.050, 0.298)),      # l'épaule
    ("queue", "corps", (0, 0.078, 0.075)),           # la racine des quatre plumes de la queue
    ("patte_G", "racine", (0.048, 0.040, 0.090)),    # le haut de la patte
]


def taille(points, cote):
    """Le corps plie à la taille : sous 15 cm il suit les hanches, au-dessus de 27 cm le buste, entre les deux il se partage.
    Les coutures des flancs prennent les mêmes poids que le tissu qui les porte."""
    w = K.lisse((points[:, 2] - 0.15) / 0.12)
    return {"corps": 1 - w, "buste": w}


PORTEURS = [("corps", taille, "corps"), ("lisiere", taille, "corps"), ("tete", "tete"), ("masque", "tete"), ("cerne", "tete"),
            ("oeil", "tete"), ("moustache", "tete"), ("bec", "tete"), ("aile", "aile", True), ("queue", "queue"),
            ("patte", "patte", True),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _plateau(t, debut, fin, pente=0.02):
    """1 entre « debut » et « fin », 0 ailleurs, avec des bords raides de « pente » : un geste d'oiseau, net, par saccade."""
    x = borne(min(t - debut + pente, fin + pente - t) / pente)
    return x * x * (3 - 2 * x)


def _rafale(t, debut, fin, coups):
    """Une rafale de coups de bec entre « debut » et « fin » : 1 quand le bec frappe, 0 quand il se relève."""
    if t <= debut or t >= fin:
        return 0.0
    return abs(math.sin(math.pi * coups * (t - debut) / (fin - debut))) ** 0.7


def _bond(p, haut, penche=0.0):
    """Tout l'oiseau monte de « haut » (les pattes avec lui) ; il se penche en avant de « penche » degrés en l'air,
    ce qui lève la queue au-dessus de l'herbe. Un « haut » négatif : il se ramasse sur ses pattes, qui restent au sol."""
    p.add("corps", pos=(0, 0, haut), rot=(penche, 0, 0))
    p.paire("patte", pos=(0, 0, max(0.0, haut)))


def _ailes(p, ouvre, bat=0.0):
    """Les ailes s'écartent du corps de « ouvre » degrés, autour de l'épaule (le bout part en dehors et en arrière)."""
    p.paire("aile", rot=(0.35 * ouvre, -0.9 * ouvre - bat, -0.30 * ouvre))


def repos(t):
    """Il guette : il respire, tourne la tête par saccades (à droite, puis à gauche), la penche pour écouter sous l'herbe
    (les fourmis), sautille une fois sur place, frétille de la queue, cligne des yeux."""
    p = Pose()
    r = onde(t, 2)
    droite = _plateau(t, 0.10, 0.27)
    ecoute = _plateau(t, 0.33, 0.47, 0.03)
    gauche = _plateau(t, 0.52, 0.63)
    saut = math.sin(math.pi * borne((t - 0.76) / 0.10))
    ramasse = cloche(t, 0.745, 0.025) + cloche(t, 0.875, 0.025)
    p.add("buste", ech=(1 + 0.018 * r, 1 + 0.018 * r, 1))
    _bond(p, 0.030 * saut - 0.010 * ramasse, 6 * saut)
    p.add("tete", rot=(9 * ecoute - 5 * saut, 16 * ecoute, -34 * droite + 22 * gauche - 6 * ecoute))
    p.add("queue", rot=(10 * cloche(t, 0.93, 0.03), 0, 7 * cloche(t, 0.93, 0.05) * onde(t, 16)))
    _ailes(p, 8 * saut)
    p.ouvert = 1 - cloche(t, 0.05, 0.02) - cloche(t, 0.69, 0.02)
    return p


def avance(t):
    """Il sautille : deux bonds par boucle. Il se ramasse, s'envole penché en avant (la queue décolle de l'herbe, les pattes
    se replient sous lui), retombe sur ses pattes et se ramasse encore. Posées, les pattes glissent vers l'arrière : il avance."""
    p = Pose()
    u = (2 * t) % 1.0
    air = math.sin(math.pi * u / 0.55) if u < 0.55 else 0.0
    sol = math.sin(math.pi * (u - 0.55) / 0.45) if u >= 0.55 else 0.0
    glisse = (-0.5 + (u - 0.55) / 0.45) if u >= 0.55 else 0.5 * math.cos(math.pi * u / 0.55)
    _bond(p, 0.042 * air - 0.010 * sol, 10 * air + 4)
    p.paire("patte", rot=(26 * air, 0, 0), pos=(0, 0.022 * glisse, 0))
    p.add("buste", rot=(4 * air, 0, 0))
    p.add("tete", rot=(-10 * air - 4 + 3 * sol, 0, 0))
    p.add("queue", rot=(4 * air, 0, 0))
    _ailes(p, 12 * air)
    return p


def mange(t):
    """Au sol, sur une fourmilière : il se plie en avant et frappe du bec par rafales (cinq coups, une pause la tête penchée
    pour écouter, six coups), puis il se redresse, le bec au ciel, et avale."""
    p = Pose()
    leve = cloche(t, 0.86, 0.13)
    bas = 1 - leve
    coups = (_rafale(t, 0.06, 0.32, 5) + _rafale(t, 0.46, 0.72, 6)) * bas
    ecoute = _plateau(t, 0.35, 0.43, 0.03) * bas
    p.add("corps", pos=(0, 0, -0.020 * bas), rot=(30 * bas, 0, 0))
    p.add("buste", rot=(44 * bas + 7 * coups, 0, 0))
    p.add("tete", pos=(0, -0.006 * bas, 0.012 * bas + 0.020 * coups),
          rot=(22 * bas + 13 * coups - 22 * leve + 6 * onde(t, 8) * leve, 14 * ecoute, -8 * ecoute))
    p.add("queue", rot=(-10 * bas, 0, 0))
    _ailes(p, 4 * coups)
    p.ouvert = 1 - cloche(t, 0.40, 0.02) - 0.5 * leve
    return p


def joie(t):
    """Il rit, comme rit un pic-vert : un bond, la tête renversée en arrière, le bec au ciel, secouée par saccades,
    les ailes entrouvertes, la queue qui bat ; puis il retombe et reprend sa garde."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    saut = math.sin(math.pi * borne((t - 0.08) / 0.30))
    rire = abs(onde(t, 8)) * env
    _bond(p, 0.045 * saut, 8 * saut)
    p.paire("patte", rot=(20 * saut, 0, 0))
    p.add("buste", rot=(-12 * env - 3 * rire, 0, 0))
    p.add("tete", rot=(-38 * env - 10 * rire, 0, 6 * onde(t, 2) * env))
    p.add("queue", rot=(12 * env, 0, 10 * onde(t, 6) * env))
    _ailes(p, 30 * env, 8 * onde(t, 8) * env)
    p.ouvert = 1 - 0.5 * env
    return p


def dort(t):
    """Il dort debout, calé sur sa queue : il se tasse sur ses pattes, se met en boule (le plumage gonflé), la tête rentrée
    dans les épaules, le bec posé sur le poitrail, les yeux fermés ; il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.022), rot=(2, 0, 0))
    p.add("buste", rot=(6, 0, 0), ech=(1.06 + 0.015 * r, 1.06 + 0.015 * r, 0.97))
    p.add("tete", pos=(0, -0.006, -0.005), rot=(26 + 1.5 * r, 0, -10))
    p.add("queue", rot=(12, 0, 0))
    _ailes(p, 2 + 1.5 * r)
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Pic-vert")
