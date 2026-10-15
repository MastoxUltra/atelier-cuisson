"""L'épinoche en peluche, deuxième dessin : le petit videur de la mare. Un fuseau de velours en trois tons : le dos bleu
de minuit, les flancs acier, et la gorge rouge cerise de la noce, qui lui prend tout le devant. Sur le dos, trois épines
de feutrine minuit, fines comme des lames, chacune tenue par sa petite voile acier ; deux autres sous le ventre, sorties
comme des coudes. Un pédoncule tout fin et une queue en éventail qui fouette de côté. Il se cambre sur le ventre, la
tête relevée et tournée vers nous, la bouche qui boude, l'œil cerclé de turquoise sous une paupière qui
descend vers le nez : il défend sa mare, et il est prêt à charger plus gros que lui.

    python epinoche.py        fabrique la fiche art/apercus/animaux/epinoche.png
    (le premier dessin, refusé le 14/10 : epinoche_ancien.py)
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

MINUIT = M.hexa("#2c3a5c")                    # le dos, les épines
ACIER = M.hexa("#a9bfd2")                     # les flancs, les voiles, les nageoires
CERISE = M.hexa("#d8402c")                    # la gorge et le ventre de la noce (le poil la fonce en cerise)
TOURNE = 0                                    # -45 pour la fiche, posée de biais (on lit son profil) ; 0 pour le jeu
ROT = A.repere((0, 0, 0), (0, 0, TOURNE))
# l'échine, de la queue au nez : couchée sur le ventre, cambrée, le nez relevé vers nous, la queue partie de côté
DOS = K.Fil([ROT @ Vector(p) for p in ((-0.022, 0.128, 0.058), (-0.006, 0.070, 0.034), (0.0, 0.000, 0.036), (0.010, -0.060, 0.052),
                                       (0.024, -0.094, 0.072))], flanc=tuple(ROT.to_3x3() @ Vector((1, 0, 0))))
LONG = 0.240                                  # la longueur du corps le long de l'échine


def robe(m):
    """Peint le fuseau (tourné tout droit, le +Y de la pièce est le dos) en trois tons : la gorge cerise qui monte haut
    sur le devant et redescend vers la queue, les flancs acier, le dos minuit."""
    z, y = m.v[:, 2], m.v[:, 1]
    gorge = -0.034 + 0.040 * K.lisse((z - 0.070) / 0.120)
    dos = 0.010 + 0.006 * K.lisse((z - 0.120) / 0.080)
    m.teinte = np.where((y < gorge)[:, None], np.asarray(CERISE), np.where((y > dos)[:, None], np.asarray(MINUIT), np.asarray(ACIER)))
    return m


def sur_le_dos(s, haut, vers_queue=0.0):
    """Le point du dos à la distance s de la queue, et le repère d'une pièce plate plantée là : son Y monte, son X part
    vers la queue (penché de « vers_queue »), sa face regarde le flanc gauche."""
    centre, avant, nuque = (Vector(x) for x in DOS.cadre(s))
    pied = centre + nuque * haut
    monte = (nuque - avant * vers_queue).normalized()
    return pied, monte, A.cadre(pied, Vector(DOS.flanc), monte)


def poser(maille, rep):
    """Déplace une maille dans un repère (une matrice de A.cadre)."""
    r = np.array(rep)
    return maille.sculpte(lambda v: v @ r[:3, :3].T + r[:3, 3])


def epine(hauteur, rayon):
    """Une épine de feutrine : une lame tournée, fine et droite, au bout pointu."""
    return A.tour(A.profil([(0, 0), (rayon, 0.002), (rayon * 0.78, hauteur * 0.45), (rayon * 0.30, hauteur * 0.90), (0, hauteur)], 5), 16)


def voile(hauteur, large):
    """La petite voile tendue derrière une épine : un triangle de feutrine dont le bord arrière se creuse."""
    return A.courbe([(0.0, 0.0), (0.0, hauteur), (large * 0.35, hauteur * 0.55), (large, 0.0)], 4, fermee=True)


def construire():
    a = K.Animal("epinoche")
    a.taille = 0.32

    # ----- le corps : un fuseau tourné de la queue au nez, plat sur les côtés, la gorge bombée, couché le long de l'échine -----
    profil = A.profil([(0, 0), (0.006, 0.004), (0.0075, 0.030), (0.012, 0.060), (0.025, 0.100), (0.035, 0.140), (0.038, 0.172),
                       (0.034, 0.202), (0.024, 0.226), (0, LONG)], 9)

    def fuseau(v):
        s = v * [0.62, 1.0, 1.0]
        s[:, 1] *= np.where(v[:, 1] < 0, 1.0 + 0.18 * K.lisse((v[:, 2] - 0.110) / 0.08), 1.0)   # la gorge bombée
        return s
    corps = robe(A.tour(profil, 64).sculpte(fuseau)).sculpte(DOS.couche)
    a.piece("corps", corps, None)
    nez, _avant, _nuque = DOS.cadre(LONG - 0.012)
    a.tete = Vector(nez)

    # ----- les yeux : sur les flancs du devant, cerclés de turquoise, sous une paupière qui descend vers le nez -----
    for nom, cote in (("G", 1), ("D", -1)):
        centre, d = DOS.vise(0.205, 0.30, 0.86 * cote, 0.40)
        p, n = a.surface("corps", centre, d)
        a.rustine("cerne_" + nom, "corps", centre, n, 0.62, K.TURQUOISE, 0.0025, 0)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0095)
        _c, avant, nuque = (Vector(x) for x in DOS.cadre(0.205))
        a.piece("lourde_" + nom, K.paupiere(0.0095, 0.12), MINUIT, mat=A.cadre(p + n * 0.004, n, nuque + avant * 0.55), poil=False)

    # ----- la bouche : un trait brodé qui boude, tombé aux deux coins -----
    centre, avant, nuque = (Vector(x) for x in DOS.cadre(LONG - 0.020))
    bouche = a.trace("corps", centre, [avant * 0.9 + nuque * h + Vector(DOS.flanc) * x
                                       for x, h in ((0.55, -0.30), (0.25, -0.24), (0.0, -0.22), (-0.25, -0.24), (-0.55, -0.30))], 0.003)
    a.broderie("bouche", A.courbe(bouche, 4), 0.0020, MINUIT)

    # ----- les trois épines du dos, chacune avec sa voile, et la petite dorsale molle derrière -----
    epines, voiles = None, None
    for s, haut, long, large in ((0.170, 0.050, 0.044, 0.024), (0.128, 0.034, 0.038, 0.020), (0.092, 0.030, 0.018, 0.010)):
        pied, monte, rep = sur_le_dos(s, haut * 0.55, 0.32)
        une = poser(epine(long, 0.0042), A.cadre(pied, monte, Vector(DOS.flanc)))
        epines = une if epines is None else epines + une
        v = poser(A.decoupe(voile(long * 0.85, large), 0.0030, 0.0010), rep)
        voiles = v if voiles is None else voiles + v
    a.piece("epines", epines, MINUIT, poil=False)
    a.piece("voiles", voiles, ACIER, poil=False)
    pied, _monte, rep = sur_le_dos(0.062, 0.012, 0.0)
    a.piece("dorsale", A.decoupe(A.courbe([(0.0, 0.0), (-0.004, 0.016), (0.012, 0.020), (0.030, 0.008), (0.034, 0.0)], 4, fermee=True),
                                 0.0032, 0.0010), ACIER, mat=rep, poil=False)

    # ----- la queue : un éventail fendu au bout du pédoncule, qui fouette vers sa droite ; trois rayons brodés -----
    bout, avant, nuque = (Vector(x) for x in DOS.cadre(0.004))
    rep = A.cadre(bout, (Vector(DOS.flanc) - avant * 0.40).normalized(), nuque)      # son X part vers l'arrière, et de côté
    eventail = A.courbe([(0.0, -0.006), (0.040, -0.034), (0.050, -0.030), (0.034, 0.0), (0.050, 0.030), (0.040, 0.034), (0.0, 0.006)], 5, fermee=True)
    a.piece("caudale", A.decoupe(eventail, 0.0035, 0.0012), ACIER, mat=rep, poil=False)

    # ----- les nageoires du côté : deux petites palettes acier, la gauche levée -----
    for nom, cote, leve in (("G", 1, 35), ("D", -1, 10)):
        centre, d = DOS.vise(0.168, -0.30, 0.90 * cote, -0.30)
        p, n = a.surface("corps", centre, d)
        _c, avant, nuque = (Vector(x) for x in DOS.cadre(0.168))
        rep = A.cadre(p + n * 0.002, (n * 0.35 + nuque * 0.94).normalized(), (-avant * 0.9 + n * math.sin(math.radians(leve))).normalized())
        a.piece("pectorale_" + nom, A.decoupe(A.courbe([(-0.007, 0.0), (0.007, 0.0), (0.011, 0.020), (0.0, 0.028), (-0.010, 0.018)], 4, fermee=True),
                                               0.0030, 0.0010), ACIER, mat=rep, poil=False)
    # les deux épines du ventre, sorties sur les côtés comme des coudes
    ventrales = None
    for cote in (1, -1):
        centre, d = DOS.vise(0.150, -0.10, 0.55 * cote, -0.85)
        p, n = a.surface("corps", centre, d)
        _c, avant, nuque = (Vector(x) for x in DOS.cadre(0.150))
        pointe = p + Vector(DOS.flanc) * (0.020 * cote) - avant * 0.016 - nuque * 0.004
        une = A.tube(A.courbe([p - n * 0.003, p + (pointe - p) * 0.5 + n * 0.002, pointe], 4), lambda t: 0.0040 * (1 - 0.85 * t), 12)
        ventrales = une if ventrales is None else ventrales + une
    a.piece("ventrales", ventrales, MINUIT, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py epinoche). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.004, -0.010, 0.040)),               # le milieu du corps, derrière les ouïes
    ("queue", "corps", (-0.004, 0.040, 0.036)),               # le début du pédoncule
    ("queue2", "queue", (-0.016, 0.100, 0.046)),              # le bout du pédoncule, là où s'attache l'éventail
    ("nageoire_G", "corps", (0.024, -0.050, 0.040)),          # la pectorale (la droite est son miroir)
]


def souple(points, cote):
    """Le corps : la tête et le ventre suivent le corps, le pédoncule la queue, l'éventail le bout de la queue."""
    y = points[:, 1]
    w1 = K.lisse((y - 0.015) / 0.050)
    w2 = K.lisse((y - 0.080) / 0.040)
    return {"corps": 1 - w1, "queue": w1 - w2, "queue2": w2}


PORTEURS = [("corps", souple, "corps"), ("cerne", souple, "corps"), ("bouche", souple, "corps"),
            ("epines", souple, "corps"), ("voiles", souple, "corps"), ("dorsale", souple, "corps"), ("ventrales", souple, "corps"),
            ("caudale", "queue2"), ("oeil", "corps"), ("lourde", "corps"), ("pectorale", "nageoire", True),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def ondule(p, force, t, tours=1.0):
    """La nage : une vague qui court de la tête vers la queue, de plus en plus large."""
    p.add("corps", rot=(0, 0, 3 * force * onde(t, tours)))
    p.add("queue", rot=(0, 0, -10 * force * onde(t, tours, -0.15)))
    p.add("queue2", rot=(0, 0, -18 * force * onde(t, tours, -0.30)))


def repos(t):
    """Il monte la garde : les pectorales battent sans arrêt, la queue balance à peine, il se tourne d'un coup vers ce
    qui approche puis revient, et cligne sous sa paupière en colère."""
    p = Pose()
    ondule(p, 0.4, t, 2)
    p.paire("nageoire", rot=(0, 0, 18 * onde(t, 8)))
    p.add("corps", rot=(0, 0, 12 * cloche(t, 0.45, 0.10)), pos=(0, 0, 0.002 * onde(t, 2)))
    p.ouvert = 1 - cloche(t, 0.70, 0.02)
    return p


def avance(t):
    """Il nage : deux grands coups de queue par cycle, le corps qui ondule, les pectorales collées."""
    p = Pose()
    ondule(p, 1.0, t, 2)
    p.paire("nageoire", rot=(0, 0, -20))
    return p


def mange(t):
    """Il fond sur la miette d'un coup de queue, la happe, recule et recommence ; puis il mâche."""
    p = Pose()
    for c in (0.20, 0.55):
        coup = cloche(t, c, 0.08)
        p.add("corps", pos=(0, -0.014 * coup, -0.004 * coup), rot=(8 * coup, 0, 0))
        p.add("queue2", rot=(0, 0, 26 * coup * onde(t, 6)))
    p.paire("nageoire", rot=(0, 0, 14 * onde(t, 6)))
    p.ouvert = 1 - cloche(t, 0.85, 0.02)
    return p


def joie(t):
    """Un saut hors de l'eau, cambré, la queue qui fouette, toutes épines dehors ; il retombe à plat."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.8)) if t < 0.8 else 0.0
    p.add("corps", pos=(0, 0, 0.060 * env), rot=(-18 * env * (1 - 2 * borne(t / 0.8)), 0, 0))
    p.add("queue", rot=(10 * env, 0, 14 * onde(t, 5) * env))
    p.add("queue2", rot=(12 * env, 0, 22 * onde(t, 5, -0.2) * env))
    p.paire("nageoire", rot=(0, -20 * env, 0))
    return p


def dort(t):
    """Posé au fond, immobile, les pectorales qui battent tout doucement, les yeux fermés."""
    p = Pose()
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.004), ech=(1.0, 1.0, 1.0 + 0.015 * onde(t, 1)))
    p.paire("nageoire", rot=(0, 0, 6 * onde(t, 2)))
    p.add("queue2", rot=(0, 0, 6))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Épinoche")
