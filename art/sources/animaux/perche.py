"""La perche en peluche : une bagarreuse. Le dos doré olive bossu, cinq selles sombres qui descendent en pointe sur les
flancs, le ventre clair, les nageoires rouge orangé toutes en pointes. Elle charge le nez bas, la mâchoire du bas en
avant, la grande dorsale épineuse hérissée, la queue qui fouette.

    python perche.py        fabrique la fiche art/apercus/animaux/perche.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import garnitures as G
import matieres as M
import peluche as K

DORE = M.hexa("#c9ab35")                      # le doré olive du dos et des flancs
SOMBRE = M.hexa("#3b4026")                    # les cinq selles : un olive presque noir
ROUGE = M.hexa("#f0502a")                     # le rouge orangé des nageoires
CORPS = Vector((0.0, -0.02, 0.092))           # le milieu de l'épaule
AVANT, ARRIERE = 0.165, 0.215                 # de l'épaule au nez, de l'épaule au bout du pédoncule
BIAIS = 0                                     # -12 pour la fiche (posée un peu de biais) ; 0 pour le jeu
POSE = A.repere(CORPS, (6, 0, BIAIS))        # le nez bas comme un taureau qui charge
P3 = POSE.to_3x3()
HAUT = P3 @ Vector((0, 0, 1))


def ploie(y):
    """Le coup de queue : l'arrière du corps part vers la gauche. Rend le décalage en x à la distance y de l'épaule."""
    return 1.3 * np.maximum(y, 0.0) ** 2


def axe(y, z=0.0):
    """Le point du milieu du corps à la distance y de l'épaule (devant si y < 0) : toujours dans la peluche."""
    return POSE @ Vector((float(ploie(y)), y, z))


def quartiers(maille, paliers):
    """Peint une boule par quartiers, comme une orange, pareil à gauche et à droite : paliers = [(angle, couleur), ...]
    donne la couleur jusqu'à chaque angle (en degrés, une fois la boule couchée : -90 sous le ventre, 0 au flanc, 90 au dos)."""
    maille.teinte = np.tile(np.asarray(paliers[-1][1], float), (len(maille.v), 1))
    for anneau in maille.anneaux:
        n = len(anneau)
        for j, i in enumerate(anneau if n > 1 else []):
            c = 360.0 * (j + 0.5) / n                                  # le milieu de la case que ce point colore
            angle = c if c <= 90 else 180 - c if c <= 270 else c - 360
            maille.teinte[i] = next(couleur for seuil, couleur in paliers if angle <= seuil)
    return maille


def debout(depart, vers, penche=0.0):
    """Le repère d'une nageoire découpée, posée de chant sur le corps (on parle dans le repère du corps) : son X part de
    « depart » dans la direction « vers », son Y monte. penche : des degrés pour écarter son bas vers la gauche."""
    u = Vector(vers).normalized()
    n = u.cross(Vector((0, 0, 1))).normalized()
    n = n * math.cos(math.radians(penche)) + n.cross(u) * math.sin(math.radians(penche))
    return POSE @ A.cadre(depart, n, n.cross(u))


def construire():
    a = K.Animal("perche")
    a.taille = 0.50
    a.tete = axe(-0.135, 0.004)

    # ----- le corps : une boule couchée (son pôle du haut fait le nez), plate sur les flancs, le museau en coin,
    #       une bosse pointue derrière la tête, puis le dos qui redescend tout droit jusqu'à la queue -----
    def coque(v):
        x, t, z = v[:, 0], -v[:, 2], v[:, 1]
        arriere = K.lisse(t)
        museau = 1 - 0.60 * np.clip((-t - 0.44) / 0.56, 0, 1) ** 1.5
        bosse = 1 + 0.34 * np.clip(1 - np.abs(t + 0.30) / 0.30, 0, 1)
        y = t * np.where(t < 0, AVANT, ARRIERE)
        haut = np.where(z > 0, 0.082 * bosse * (1 - 0.52 * arriere), 0.064 * (1 - 0.40 * arriere))
        return np.stack([x * 0.044 * (1 - 0.50 * arriere) * museau + ploie(y), y, z * haut * museau], axis=1)
    corps = quartiers(A.boule(1.0, 64, 32), [(-35, K.CREME), (90, DORE)]).sculpte(coque)
    G.sillons(corps, [16], 0.004, 1.1)                         # la couture du front creuse un peu le tissu
    a.piece("corps", corps, None, mat=POSE)
    a.couture("front", "corps", 16, 0.63, 0.92)

    # ----- la robe : cinq selles de feutrine sombre à cheval sur le dos, en losange, la pointe au milieu du flanc -----
    for k, y in enumerate((-0.062, -0.012, 0.042, 0.094, 0.142)):
        a.rustine("selle%d" % k, "corps", axe(y), HAUT, lambda th: 1.0 / (abs(math.cos(th)) / 1.78 + abs(math.sin(th)) / (0.25 + 0.02 * k)),
                  SOMBRE, 0.0028, 0)

    # ----- la mâchoire du bas, qui avance : un menton clair sous le museau, et la bouche brodée, les coins tombants -----
    menton = POSE @ Vector((0, -0.152, -0.021))
    a.piece("machoire", A.boule(1.0, 32, 16).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.021, 0.036, 0.013), K.CREME, mat=POSE @ A.repere((0, -0.152, -0.021), (-10, 0, 0)))
    moue = [P3 @ Vector((math.sin(s) * 0.9, -math.cos(s), 0.62 - 0.30 * abs(s / 1.9) ** 2)) for s in np.linspace(-1.9, 1.9, 21)]
    a.broderie("bouche", a.trace("machoire", menton, moue, 0.0035), 0.0022)

    # ----- les yeux, haut sur la tête, sous un sourcil froncé ; l'ouïe brodée derrière -----
    for nom, cote in (("_G", 1), ("_D", -1)):
        vers = P3 @ Vector((0.86 * cote, -0.22, 0.46))
        p, n = a.surface("corps", axe(-0.106, 0.012), vers)
        a.bouton("oeil" + nom, p + n * 0.001, n, 0.017)
        sourcil = [p + P3 @ Vector((0, -1, 0)) * (0.022 - 0.036 * u) + HAUT * (0.012 + 0.014 * u) - axe(-0.106, 0.012) for u in np.linspace(0, 1, 6)]
        a.broderie("sourcil" + nom, a.trace("corps", axe(-0.106, 0.012), sourcil, 0.0045), 0.0026)
        ouie = [P3 @ Vector((cote * math.cos(s), 0.20 * math.cos(1.3 * s) - 0.08, math.sin(s))) for s in np.linspace(-0.75, 0.80, 14)]
        a.broderie("ouie" + nom, a.trace("corps", axe(-0.070), ouie, 0.0045), 0.0022, K.CHOCOLAT)

    # ----- la grande dorsale épineuse : un éventail de feutrine planté sur la bosse, une pointe par épine -----
    p0 = a.trace("corps", axe(-0.060), [HAUT], 0.0)[0] - HAUT * 0.007
    p1 = a.trace("corps", axe(0.070), [HAUT], 0.0)[0] - HAUT * 0.007
    pente, long = (p1 - p0).normalized(), (p1 - p0).length
    travers = pente.cross(HAUT).normalized()
    rep = A.cadre(p0, travers, travers.cross(pente))          # son X suit la pente du dos, son Y monte
    epines = [(long * k / 7 + h * math.sin(math.radians(-14 + 9 * k)), h * math.cos(math.radians(-14 + 9 * k)))
              for k, h in enumerate((0.086, 0.116, 0.128, 0.122, 0.106, 0.086, 0.064, 0.042))]
    voile = [(-0.008, -0.012)]
    for k, (u, w) in enumerate(epines):
        voile.append((u, w))
        if k < 7:                                              # entre deux épines, la toile se creuse
            voile.append(((u + epines[k + 1][0]) * 0.5 + 0.004, (w + epines[k + 1][1]) * 0.5 * 0.80))
    voile += [(long + 0.010, -0.012)]
    a.piece("dorsale", A.decoupe(voile, 0.009, 0.003), ROUGE, mat=rep, poil=False)
    for k, (u, w) in enumerate(epines):
        for face in (1, -1):                                   # les épines, brodées des deux côtés
            a.broderie("epine%d" % k, [rep @ Vector((long * k / 7, 0.004, face * 0.0052)), rep @ Vector((u * 0.97 + long * k / 7 * 0.03, w * 0.97, face * 0.0052))], 0.0016, K.BRUN)
    a.piece("tache", A.boule(1.0, 20, 10).etire(0.013, 0.011, 0.0062), SOMBRE, mat=rep @ A.repere((long * 0.93, 0.020, 0)), poil=False)

    # ----- les autres nageoires, du même rouge : la petite dorsale, la queue fourchue, l'anale, les pelviennes
    #       qui la portent comme deux poings, les pectorales écartées -----
    a.piece("dorsale2", A.decoupe([(-0.006, -0.010), (0.004, 0.030), (0.020, 0.052), (0.046, 0.030), (0.064, 0.012), (0.066, -0.010)], 0.008, 0.003), ROUGE,
            mat=debout((float(ploie(0.092)), 0.092, 0.050), (2.6 * 0.12, 1, -0.16)), poil=False)
    a.piece("queue", A.decoupe([(0.0, 0.020), (0.050, 0.046), (0.118, 0.092), (0.112, 0.072), (0.095, 0.061), (0.107, 0.053), (0.072, 0.0), (0.104, -0.044), (0.118, -0.084),
                                (0.050, -0.042), (0.0, -0.020)], 0.010, 0.003), ROUGE,
            mat=debout((float(ploie(0.195)), 0.195, 0.0), (0.95, 1, 0.10), 8), poil=False)
    a.piece("anale", A.decoupe([(-0.004, 0.014), (0.056, 0.014), (0.064, -0.012), (0.044, -0.057), (0.020, -0.020)], 0.008, 0.003), ROUGE,
            mat=debout((float(ploie(0.050)), 0.050, -0.046), (2.6 * 0.07, 1, 0.04)), poil=False)
    for nom, cote in (("_G", 1), ("_D", -1)):
        a.piece("pelvienne" + nom, A.decoupe([(-0.004, 0.016), (0.052, 0.016), (0.058, -0.012), (0.046, -0.043), (0.016, -0.018)], 0.009, 0.003), ROUGE,
                mat=debout((0.016 * cote, -0.070, -0.050), (0.10 * cote, 1, 0), 28 * cote), poil=False)
        a.piece("pectorale" + nom, A.decoupe([(-0.006, -0.012), (0.030, -0.024), (0.070, -0.018), (0.092, 0.014), (0.052, 0.022), (-0.006, 0.012)], 0.008, 0.003), ROUGE,
                mat=debout((0.036 * cote, -0.058, -0.012), (0.62 * cote, 1, -0.10), -20 * cote), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py perche). Les mesures sont celles du modèle de jeu (BIAIS = 0), avant a.taille.

from poses import Pose, borne, cloche, onde

# Le corps est un seul boudin qui ondule : quatre os se le partagent d'avant en arrière (corps, dos, croupe, queue), et
# tout ce qui est cousu ou planté sur lui le suit (les selles, l'ouïe, le sourcil, la grande dorsale, la petite, l'anale).
# La mâchoire du bas a son os, pour s'ouvrir ; les nageoires paires (pectorales, pelviennes) aussi, en miroir.
OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, -0.040, 0.090)),          # en avant de l'épaule : la tête et l'avant du corps
    ("dos", "corps", (0.001, 0.010, 0.095)),            # le milieu du corps
    ("croupe", "dos", (0.013, 0.080, 0.1025)),          # l'arrière, qui s'effile (déjà parti vers sa gauche)
    ("queue", "croupe", (0.038, 0.149, 0.110)),         # le pédoncule et la queue fourchue
    ("machoire", "corps", (0.0, -0.140, 0.067)),        # la charnière, au fond de la mâchoire du bas
    ("pectorale_G", "corps", (0.036, -0.076, 0.074)),   # la racine des nageoires (celles de droite sont leur miroir)
    ("pelvienne_G", "corps", (0.016, -0.084, 0.035)),
]


def souple(points, cote):
    """Le boudin : chaque point suit le tronçon où il tombe le long du corps, en douceur d'un tronçon à l'autre."""
    y = ((points - np.asarray(CORPS)) @ np.array(P3))[:, 1]     # la distance à l'épaule, le long du corps
    dos = K.lisse((y - 0.000) / 0.060)
    croupe = K.lisse((y - 0.070) / 0.060)
    queue = K.lisse((y - 0.140) / 0.060)
    return {"corps": 1 - dos, "dos": dos - croupe, "croupe": croupe - queue, "queue": queue}


PORTEURS = [("corps", souple, "corps"), ("front", souple, "corps"), ("selle", souple, "corps"), ("ouie", souple, "corps"),
            ("sourcil", souple, "corps"), ("dorsale", souple, "corps"), ("epine", souple, "corps"), ("tache", souple, "corps"),
            ("anale", souple, "corps"), ("oeil", "corps"), ("machoire", "machoire"), ("bouche", "machoire"), ("queue", "queue"),
            ("pectorale", "pectorale", True), ("pelvienne", "pelvienne", True),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def ondule(p, t, force, tours=1):
    """La nage : une vague qui part de la tête et grossit jusqu'à la queue."""
    p.add("corps", rot=(0, 0, 0.25 * force * onde(t, tours)))
    p.add("dos", rot=(0, 0, -0.50 * force * onde(t, tours, -0.12)))
    p.add("croupe", rot=(0, 0, -0.80 * force * onde(t, tours, -0.25)))
    p.add("queue", rot=(0, 0, -1.20 * force * onde(t, tours, -0.38)))


def rames(p, t, force, tours):
    """Les pectorales godillent, les pelviennes suivent à contretemps."""
    p.paire("pectorale", rot=(0, 0, force * onde(t, tours)))
    p.paire("pelvienne", rot=(0, 0, 0.5 * force * onde(t, tours, 0.25)))


def repos(t):
    """Elle se tient sur place, le nez bas, les pectorales qui godillent ; elle roule de la mâchoire (elle respire),
    puis fait sa charge à vide : un coup de queue en avant, un coup de tête de taureau, et elle recule ; elle cligne."""
    p = Pose()
    ondule(p, t, 6, 2)
    rames(p, t, 16, 6)
    charge = cloche(t, 0.55, 0.07)
    secoue = charge * onde(t, 16)
    p.add("corps", pos=(0, -0.022 * charge, 0.003 * (1 + onde(t, 1)) + 0.004 * charge), rot=(5 * charge, 0, 8 * secoue))
    p.add("queue", rot=(0, 0, 22 * charge * onde(t, 8)))
    p.add("machoire", rot=(5 * (0.5 + 0.5 * onde(t, 4)) * (1 - charge) + 12 * charge, 0, 0))
    p.ouvert = borne(1 - cloche(t, 0.25, 0.025) - cloche(t, 0.85, 0.025))
    return p


def avance(t):
    """Elle nage en force : tout le corps ondule, la queue fouette large, les nageoires se plaquent le long du corps,
    et le nez reste bas, comme si elle chargeait."""
    p = Pose()
    ondule(p, t, 18)
    p.paire("pectorale", rot=(0, 0, -22 + 6 * onde(t, 2)))
    p.paire("pelvienne", rot=(0, 0, -12))
    p.add("corps", rot=(3, 0, 0))
    return p


def mange(t):
    """Elle fond sur sa proie, la gueule grande ouverte, l'avale d'un coup et la secoue ; puis elle mâche en reculant."""
    p = Pose()
    fond = cloche(t, 0.25, 0.12)
    gueule = cloche(t, 0.27, 0.06)
    secoue = cloche(t, 0.42, 0.08) * onde(t, 12)
    mache = cloche(t, 0.70, 0.18) * max(0.0, onde(t, 8))
    ondule(p, t, 6 + 14 * fond, 2)
    rames(p, t, 12, 4)
    p.add("corps", pos=(0, -0.030 * fond, 0), rot=(6 * fond, 0, 10 * secoue))
    p.add("machoire", rot=(32 * gueule + 10 * mache, 0, 0))
    p.ouvert = borne(1 - 0.4 * gueule - cloche(t, 0.90, 0.025))
    return p


def joie(t):
    """Elle bondit hors de l'eau en se cambrant, la queue qui fouette et toutes nageoires dehors, la gueule ouverte
    comme pour mordre le ciel ; elle retombe à plat, et reprend sa pose."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    s = borne((t - 0.20) / 0.50)
    saut = 4 * s * (1 - s)
    ondule(p, t, 22 * env, 4)
    p.add("corps", pos=(0, 0, 0.13 * saut), rot=(-20 * saut + 14 * cloche(t, 0.72, 0.10, False), 0, 0))
    p.add("dos", rot=(10 * saut, 0, 0))
    p.add("croupe", rot=(12 * saut, 0, 0))
    p.paire("pectorale", rot=(0, 34 * saut, 0))
    p.paire("pelvienne", rot=(0, 20 * saut, 0))
    p.add("machoire", rot=(24 * saut, 0, 0))
    return p


def dort(t):
    """Immobile au ras du fond, les nageoires posées, les yeux fermés ; la mâchoire s'entrouvre lentement à chaque
    respiration, et la queue balance à peine."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    ondule(p, t, 2)
    p.add("corps", pos=(0, 0, 0.002 * (1 + r)), ech=(1.0 + 0.01 * r, 1.0, 1.0 + 0.01 * r))
    p.add("machoire", rot=(3 + 3 * r, 0, 0))
    p.paire("pectorale", rot=(0, -10, 6 * cloche(t, 0.6, 0.06) * onde(t, 8)))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Perche")
