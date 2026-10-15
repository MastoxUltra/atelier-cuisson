"""Le chien en peluche, deuxième dessin : un teckel, le petit aristocrate du village. Un boudin interminable de velours
chocolat posé sur quatre moignons, le poitrail en proue de navire qui frôle l'herbe, une selle cacao brûlé sur l'échine ;
le museau long, chocolat sur le dessus et feu sur les joues, une truffe de feutrine noire. Deux oreilles immenses, de vrais
pans de velours brûlé doublés de feu, dont l'une s'envole quand il rejette la tête. Il pose en statue : la patte avant
levée et repliée, le menton en l'air, la tête tournée vers vous, et il vous toise sous ses paupières lourdes, deux points
feu en guise de sourcils. Trente centimètres de haut, et la fierté d'un dogue.

    python chien.py        fabrique la fiche art/apercus/animaux/chien.png
    (le premier dessin, jamais gardé : chien_ancien.py)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import garnitures as G
import matieres as M
import peluche as K

CHOCOLAT = M.hexa("#86502c")                  # le velours : un chocolat chaud (le poil le fonce en chocolat au lait)
BRULE = M.hexa("#4e2c1a")                     # la selle, les oreilles, les paupières : le cacao brûlé
FEU = M.hexa("#f2a24a")                       # l'accent : le feu du teckel, joues, sourcils, poitrail, chaussettes
TOURNE = 0                                    # -30 pour la fiche, posé de biais (on lit sa longueur) ; 0 pour le jeu
CORPS = Vector((0.0, 0.060, 0.132))
LARGE, LONG, HAUT = 0.090, 0.355, 0.084       # les demi-mesures du boudin
TETE = Vector((0.010, -0.336, 0.440))
PORT = A.repere(TETE, (-24, 6, 14))           # le menton levé, la tête tournée vers vous, un rien penchée


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du village."""
    return PORT.to_3x3() @ Vector((x, y, z))


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def oreille(c):
    """Un grand pan de velours : étroit à l'attache, large et rond en bas, plat. Dans son repère, l'attache est à
    l'origine, le pan descend le long de -Z ; le dehors est brûlé, la doublure (tournée vers la joue) est feu.
    c : 1 pour l'oreille gauche, -1 pour la droite (la même, en miroir)."""
    def pavillon(v):
        s = v.copy()
        s[:, 1] *= 1 - 0.42 * K.lisse((v[:, 2] + 0.05) / 1.05)
        s[:, 0] *= 1 - 0.30 * K.lisse((-v[:, 2] - 0.2) / 0.8)
        return s
    m = A.boule(1.0, 32, 16).sculpte(pavillon).etire(0.013, 0.060, 0.098).pose((0, 0, -0.090))
    if c < 0:
        m.v[:, 0] *= -1
        m.f = [tuple(reversed(f)) for f in m.f]
    m.teinte = np.where((m.v[:, 0] * c < -0.004)[:, None], np.asarray(FEU), np.asarray(BRULE))
    return m


def patte(chemin, haut):
    """Une patte courte et forte : le velours chocolat, la chaussette feu sur le dernier « haut » mètres, un pied rond au bout."""
    ch = A.courbe(chemin, 5)
    long = float(np.sum(np.linalg.norm(np.diff(ch, axis=0), axis=1)))
    m = K.tube_peint(ch, lambda t: 0.030 - 0.004 * t, [(1 - haut / long, CHOCOLAT), (9, FEU)], 16)
    return m


def construire():
    a = K.Animal("chien")
    a.taille = 0.92
    a.tete = PORT @ Vector((0.0, -0.110, -0.010))

    # ----- le corps : un boudin interminable aux flancs droits ; le poitrail en proue qui descend frôler l'herbe, le
    #       ventre qui remonte vers les cuisses ; une selle brûlée posée sur l'échine -----
    def coque(v):
        y = v[:, 1]
        rond = np.sqrt(np.maximum(1 - y * y, 1e-9))
        boudin = np.maximum(1 - np.abs(y) ** 2.8, 0.0) ** (1 / 2.8)
        k = boudin / rond
        s = np.stack([v[:, 0] * k, y, v[:, 2] * k], axis=1)
        s = K.bosse(s, (0, -0.70, -0.72), 0.34, 0.20)                 # la proue du poitrail
        s = K.bosse(s, (0, 0.80, 0.30), 0.06, 0.20)                   # la croupe
        s = K.bosse(K.bosse(s, (0.85, -0.50, -0.15), 0.05, 0.10), (-0.85, -0.50, -0.15), 0.05, 0.10)   # les épaules
        avant = K.lisse((-s[:, 1] - 0.1) / 0.8)
        arriere = K.lisse((s[:, 1] + 0.1) / 0.9)
        s = s * [LARGE, LONG, HAUT]
        s[:, 0] *= 1 + 0.10 * avant - 0.08 * arriere
        s[:, 2] *= np.where(s[:, 2] < 0, 1 + 0.10 * avant - 0.36 * arriere, 1.0)
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    corps.teinte = np.where(((corps.v[:, 2] > 0.056) & (corps.v[:, 1] > -0.22) & (corps.v[:, 1] < 0.30))[:, None],
                            np.asarray(BRULE), np.asarray(CHOCOLAT))
    G.sillons(corps, [14, 42], 0.005, 1.1)
    a.piece("corps", corps, None, pos=CORPS, rot=(-5, 0, 0))
    a.couture("dos", "corps", 14, 0.60, 0.99, fil=FEU)
    a.couture("echine", "corps", 42, 0.80, 0.99, fil=FEU)
    a.rustine("poitrail", "corps", CORPS + Vector((0, -0.24, 0.0)), (0, -0.82, -0.58),
              lambda th: 0.50 - 0.12 * math.cos(2 * th), FEU, feston=22, fil=BRULE)
    a.rustine("rapiecage", "corps", CORPS + Vector((0, 0.12, 0.0)), (1.0, 0.0, 0.05),
              lambda th: 0.30 + 0.05 * math.cos(3 * th) + 0.03 * math.sin(2 * th), BRULE, feston=16, fil=FEU)

    # ----- le cou : dressé et épais, le jabot en avant -----
    fil_cou = K.Fil([(0.0, -0.200, 0.140), (0.002, -0.268, 0.250), (0.008, -0.312, 0.380)], flanc=(1, 0, 0))
    cou = A.tour(A.profil([(0, -0.02), (0.078, 0.0), (0.074, 0.07), (0.064, 0.15), (0.058, 0.22), (0, 0.255)], 5), 32)
    a.piece("cou", cou.sculpte(fil_cou.couche), CHOCOLAT)

    # ----- la tête : un crâne bombé au front, les joues pleines, levé et tourné vers nous -----
    def crane(v):
        v = K.bosse(v, (0, -0.55, 0.80), 0.10, 0.25)                 # le front
        v = K.bosse(K.bosse(v, (0.80, -0.45, -0.30), 0.08, 0.22), (-0.80, -0.45, -0.30), 0.08, 0.22)   # les joues
        return v * [0.084, 0.094, 0.080]
    tete = A.boule(1.0, 56, 28).sculpte(crane)
    a.piece("tete", tete, CHOCOLAT, mat=PORT)
    a.couture("crane", "tete", 14, 0.55, 0.97, fil=FEU)

    # ----- le museau : long, chocolat sur l'arête, feu sur les joues et le menton ; la truffe de feutrine noire -----
    MU = PORT @ A.repere((0, -0.040, -0.026), (96, 0, 0))     # dans ce repère : X la gauche, Y le haut, Z vers la truffe
    MU3 = MU.to_3x3()
    museau = A.tour(A.profil([(0.066, 0.0), (0.060, 0.04), (0.048, 0.10), (0.037, 0.15), (0.029, 0.184), (0, 0.200)], 6), 40)
    museau.etire(1.0, 0.84, 1.0)
    angle = np.degrees(np.arctan2(museau.v[:, 1], museau.v[:, 0]))
    arete = np.abs(angle - 90) < 66 - 34 * K.lisse(museau.v[:, 2] / 0.18)
    museau.teinte = np.where((arete & (museau.v[:, 2] < 0.180))[:, None], np.asarray(CHOCOLAT), np.asarray(FEU))
    a.piece("museau", museau, None, mat=MU)
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.023, 0.017, 0.016), K.NOIR, mat=MU @ A.repere((0, 0.004, 0.194)), poil=False)
    for nom, c in (("g", 1), ("d", -1)):                       # la bouche pincée, qui retombe au coin
        pts = [a.trace("museau", MU @ Vector((0, 0, z)), [MU3 @ Vector((c * math.cos(math.radians(d)), math.sin(math.radians(d)), 0))])[0]
               for z, d in zip(np.linspace(0.172, 0.062, 7), (-82, -74, -64, -54, -46, -44, -52))]
        a.broderie("bouche_" + nom, A.courbe(pts, 4), 0.0022, BRULE)

    # ----- les yeux : petits et vifs, à moitié voilés par une paupière lourde brûlée ; au-dessus, les deux points feu -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, vers(0.52 * c, -0.72, 0.36))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0150)
        a.piece("lourde_" + nom, K.paupiere(0.0150, 0.10), BRULE, mat=A.cadre(p + n * 0.003, n, vers(-0.10 * c, 0.15, 1)), poil=False)
        a.rustine("sourcil_" + nom, "tete", TETE, vers(0.36 * c, -0.52, 0.80), 0.15, FEU, 0.0025, 0)

    # ----- les oreilles : deux grands pans qui tombent droit, plaqués sur les joues ; la gauche s'envole en arrière et
    #       montre sa doublure feu -----
    for nom, c, ouvre, recule in (("G", 1, 34, 26), ("D", -1, 6, 4)):
        p, n = a.surface("tete", TETE, vers(0.78 * c, 0.22, 0.52))
        rep = A.repere(p - n * 0.010) @ Matrix.Rotation(math.radians(-ouvre * c), 4, "Y") @ Matrix.Rotation(math.radians(recule), 4, "X")
        a.piece("oreille_" + nom, oreille(c), None, mat=rep @ Matrix.Rotation(math.radians(8 * c), 4, "Z"))

    # ----- les pattes : courtes comme des pieds de buffet ; l'avant droite tient le sol, l'avant gauche est levée et
    #       repliée, le pied pendant ; les deux arrière, sous de fortes cuisses -----
    a.piece("patte_avant_D", patte([(-0.060, -0.180, 0.090), (-0.068, -0.196, 0.040), (-0.074, -0.206, 0.016)], 0.040), None)
    a.piece("pied_avant_D", A.boule(1.0, 24, 12).etire(0.032, 0.040, 0.016).pose((-0.078, -0.218, 0.0158), (0, 0, 18)), FEU)
    a.piece("patte_avant_G", patte([(0.058, -0.182, 0.096), (0.068, -0.250, 0.112), (0.074, -0.270, 0.074)], 0.034), None)
    a.piece("pied_avant_G", A.boule(1.0, 24, 12).etire(0.030, 0.036, 0.017).pose((0.075, -0.274, 0.058), (-72, 0, -10)), FEU)
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.boule(1.0, 32, 16).etire(0.042, 0.072, 0.064), CHOCOLAT, pos=(0.058 * c, 0.318, 0.112), rot=(-18, 0, 0))
        a.piece("patte_arriere_" + nom, patte([(0.066 * c, 0.320, 0.080), (0.070 * c, 0.322, 0.040), (0.072 * c, 0.316, 0.016)], 0.036), None)
        a.piece("pied_arriere_" + nom, A.boule(1.0, 24, 12).etire(0.030, 0.038, 0.015).pose((0.074 * c, 0.304, 0.0152), (0, 0, 8 * c)), FEU)

    # ----- la queue : un sabre dressé, porté haut comme un étendard -----
    queue = A.tube(A.courbe([(0, 0.400, 0.170), (0, 0.452, 0.222), (0, 0.482, 0.300), (0, 0.478, 0.372)], 6),
                   lambda t: 0.024 - 0.017 * t, 16)
    a.piece("queue", queue, CHOCOLAT)
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py chien). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Le modèle pose en statue, la patte avant gauche levée : c'est sa pose de repos. Pour marcher, manger, faire la fête
# ou dormir, elle redescend d'abord (_quatre). Les pattes sont assez symétriques pour leurs miroirs ; les oreilles ne le
# sont pas (la tête est tournée, la gauche s'envole) : chacune a son os nommé à la main.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.060, 0.132)),          # le milieu du boudin
    ("cou", "corps", (0.0, -0.205, 0.150)),            # le pied du cou, dans le poitrail
    ("tete", "cou", (0.008, -0.305, 0.370)),           # la nuque, en haut du cou
    ("oreille_g", "tete", (0.063, -0.291, 0.462)),     # l'attache de chaque oreille sur le crâne
    ("oreille_d", "tete", (-0.052, -0.319, 0.475)),
    ("avant_G", "corps", (0.058, -0.182, 0.096)),      # l'épaule (la droite est son miroir)
    ("arriere_G", "corps", (0.062, 0.318, 0.100)),     # la hanche, au cœur de la cuisse
    ("queue", "corps", (0.0, 0.400, 0.170)),           # la naissance de la queue
]


def _oreille_os(points, cote):
    """Une oreille tout entière sur l'os de son côté (nommé à la main, sans miroir)."""
    return {"oreille_g" if cote == "_G" else "oreille_d": np.ones(len(points))}


PORTEURS = [("corps", "corps"), ("dos", "corps"), ("echine", "corps"), ("poitrail", "corps"), ("rapiecage", "corps"),
            ("cou", "cou"),
            ("tete", "tete"), ("crane", "tete"), ("museau", "tete"), ("truffe", "tete"), ("bouche", "tete"),
            ("oeil", "tete"), ("lourde", "tete"), ("sourcil", "tete"), ("oreille", _oreille_os),
            ("patte_avant", "avant", True), ("pied_avant", "avant", True),
            ("cuisse", "arriere", True), ("patte_arriere", "arriere", True), ("pied_arriere", "arriere", True),
            ("queue", "queue"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]

POSE_PATTE = 20.0                              # de combien la patte levée tourne pour reposer le pied dans l'herbe
PLONGE = (47.0, 22.0)                          # mange : le cou et la tête plongent vers la gamelle
COUCHE = (-0.045, -70.0, 90.0, 64.0, -22.0)    # dort : le corps descend, les pattes avant s'allongent devant,
                                               # celles de derrière derrière, le cou et la tête se posent sur les pattes


# chaque patte, posée (la gauche une fois redescendue) : l'angle sous l'horizontale, vers l'avant, de l'épaule ou de la
# hanche jusqu'au milieu du pied, et cette longueur
_JAMBES = {"avant_G": (42.4, 0.0995), "avant_D": (65.8, 0.088), "arriere_G": (80.6, 0.086), "arriere_D": (80.6, 0.086)}


def _pas(p, os_, degres, leve=0.0):
    """Une patte tourne de « degrés » (> 0 : le pied part vers l'arrière) ; elle remonte d'autant qu'il le faut pour que
    le pied ne s'enfonce pas dans l'herbe, plus « leve » (le pied qui revient en l'air)."""
    a, long = _JAMBES[os_]
    creuse = long * (math.sin(math.radians(a + degres)) - math.sin(math.radians(a)))
    p.add(os_, rot=(degres, 0, 0), pos=(0, 0, max(0.0, creuse) + leve))


def _quatre(p, k=1.0):
    """La patte avant gauche, levée sur le modèle, redescend se poser (k = 1) ; k = 0 la laisse levée."""
    p.add("avant_G", rot=(POSE_PATTE * k, 0, 0))


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _oreilles(p, arriere, dehors=0.0):
    """Les deux oreilles ensemble : elles balancent vers l'arrière (degrés > 0) et s'écartent de la tête (dehors)."""
    p.add("oreille_g", rot=(arriere, -dehors, 0))
    p.add("oreille_d", rot=(arriere, dehors, 0))


def repos(t):
    """L'aristocrate pose en statue, la patte levée : il respire, hume l'air du bout de la truffe, relève encore le
    menton et détourne la tête, dédaigneux, puis daigne revenir vers nous ; la patte levée frémit, les oreilles
    tressaillent, la queue-étendard balance à peine ; il cligne lourdement."""
    p = Pose()
    r = onde(t, 2)
    p.add("corps", ech=(1 + 0.012 * r, 1, 1 + 0.016 * r))
    hume = cloche(t, 0.16, 0.07) * onde(t, 24)
    dedain = cloche(t, 0.50, 0.15)
    p.add("cou", rot=(-3 * dedain, 0, -4 * dedain))
    p.add("tete", rot=(-8 * dedain + 2 * hume, 0, -26 * dedain))
    p.add("avant_G", rot=(-6 * cloche(t, 0.78, 0.04) - 4 * cloche(t, 0.86, 0.04), 0, 0))
    _oreilles(p, 6 * cloche(t, 0.30, 0.04) + 4 * dedain, 3 * dedain)
    p.add("queue", rot=(0, 0, 6 * onde(t, 2)))
    p.ouvert = 1 - cloche(t, 0.06, 0.04) - cloche(t, 0.68, 0.04)
    return p


def avance(t):
    """Il trotte, le nez haut, sur ses petites pattes qui moulinent : les diagonales vont ensemble, le long boudin
    roule à peine et tressaute, les grandes oreilles battent à chaque pas, la queue-étendard se balance."""
    p = Pose()
    _quatre(p)
    for os_, phase in (("avant_G", 0.0), ("arriere_D", 0.0), ("avant_D", 0.5), ("arriere_G", 0.5)):
        a = math.tau * (t + phase)
        _pas(p, os_, 22 * math.sin(a), 0.012 * max(0.0, -math.cos(a)))
    p.add("corps", pos=(0, 0, 0.004 * (0.5 - 0.5 * math.cos(2 * math.tau * t))), rot=(0, 2 * onde(t, 1), 2 * onde(t, 1, 0.25)))
    p.add("tete", rot=(2 * onde(t, 2), 0, -2 * onde(t, 1, 0.25)))
    _oreilles(p, 10 * onde(t, 2, -0.1), 4 + 4 * onde(t, 2))
    p.add("queue", rot=(0, 0, 12 * onde(t, 1)))
    return p


def mange(t):
    """Il pose la patte, plonge le long museau dans la gamelle et bâfre à petits coups pressés, la queue qui bat de
    contentement ; puis il relève la tête, se pourlèche d'un coup de menton, et reprend un air digne."""
    p = Pose()
    _quatre(p)
    bas = _plateau(t, 0.42, 0.26, 0.12)
    mache = onde(t, 10) * _plateau(t, 0.42, 0.20, 0.06)
    p.add("cou", rot=(PLONGE[0] * bas, 0, 0))
    p.add("tete", rot=(PLONGE[1] * bas + 3 * mache - 8 * cloche(t, 0.88, 0.04), 0, 4 * mache))
    _oreilles(p, -6 * bas, 4 * bas)
    p.add("queue", rot=(0, 0, 16 * onde(t, 6) * bas))
    p.ouvert = 1 - cloche(t, 0.92, 0.03)
    return p


def joie(t):
    """Sa fête, toute dignité oubliée : la patte redescend, il bondit deux fois sur place en aboyant le nez au ciel,
    les oreilles qui s'envolent, la queue folle ; puis il se reprend, relève la patte et retrouve sa pose de statue."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85)) if t < 0.85 else 0.0
    saut = abs(onde(borne(t / 0.85), 2)) * env
    aboie = max(0.0, onde(t, 6)) * env
    _quatre(p, env)
    p.add("corps", pos=(0, 0, 0.045 * saut), rot=(-6 * saut, 0, 0))
    for os_ in ("avant_G", "avant_D"):
        p.add(os_, rot=(-16 * saut, 0, 0))
    for os_ in ("arriere_G", "arriere_D"):
        p.add(os_, rot=(14 * saut, 0, 0))
    p.add("cou", rot=(-8 * env, 0, 0))
    p.add("tete", rot=(-12 * env - 8 * aboie, 0, 10 * onde(t, 3) * env))
    _oreilles(p, 20 * saut, 26 * saut + 6 * env)
    p.add("queue", rot=(0, 0, 32 * onde(t, 10) * env))
    return p


def dort(t):
    """Couché à plat ventre de tout son long, les pattes de devant allongées, le menton posé dessus, les grandes
    oreilles étalées dans l'herbe ; la queue rabattue sur le côté, les yeux fermés ; le boudin respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, COUCHE[0]), ech=(1 + 0.015 * r, 1, 1 + 0.025 * r))
    p.add("avant_D", rot=(COUCHE[1], 0, 0))
    p.add("avant_G", rot=(COUCHE[1] + 50, 0, 0))                   # levée et repliée sur le modèle : elle est déjà devant
    for os_ in ("arriere_G", "arriere_D"):
        p.add(os_, rot=(COUCHE[2], 0, 0), pos=(0, 0, 0.014))         # la cuisse se pose à côté du ventre, sans s'enfoncer
    p.add("cou", rot=(COUCHE[3], 0, 0))
    p.add("tete", rot=(COUCHE[4], 0, 0))
    _oreilles(p, -10, 22)
    p.add("queue", rot=(-70, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Chien")
