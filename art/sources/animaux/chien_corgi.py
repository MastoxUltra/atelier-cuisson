"""Le chien en peluche, la race corgi (le teckel, chien.py, reste la robe de base du chien). Un tonneau de velours roux
posé sur quatre moignons blancs plus courts encore que ceux du teckel, le jabot blanc bombé, la croupe ronde comme une
miche où pointe un plumeau de rien du tout. Sa signature : deux oreilles immenses, dressées en antennes et doublées de
feutrine blanche. Il refuse d'avancer : les pattes avant arc-boutées devant lui, le poids sur l'arrière, la tête
penchée sur le côté, un seul sourcil froncé, et il sourit jusqu'aux oreilles, la langue framboise pendue de travers.
Jovial, et têtu comme une mule.

    python chien_corgi.py        fabrique la fiche art/apercus/animaux/chien_corgi.png
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

ROUX = M.hexa("#efa25c")                      # le velours : un roux de renard (le poil le fonce en roux cuivré)
BRAISE = M.hexa("#c9733a")                    # la selle et le dos des oreilles : le roux plus sombre
BLANC = M.hexa("#fcf7ee")                     # le liseré du front, le museau, le jabot, le dessous, les chaussettes
LANGUE = M.hexa("#ec5f78")                    # l'accent : la langue framboise, pendue de travers
FIL = M.hexa("#4a2a1c")                       # le fil des broderies : le sourire, le sourcil
TOURNE = 0                                    # -30 pour la fiche, posé de biais (on lit sa longueur) ; 0 pour le jeu
CORPS = Vector((0.0, 0.030, 0.150))
LARGE, LONG, HAUT = 0.106, 0.270, 0.098       # les demi-mesures du tonneau
TETE = Vector((0.006, -0.282, 0.392))
PORT = A.repere(TETE, (-8, 16, 22))           # la tête penchée sur le côté, tournée vers vous, le menton à peine levé


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


def oreille():
    """Une grande oreille dressée : un triangle épais aux coins ronds, aplati d'avant en arrière, et son creux de
    feutrine. Dans son repère, l'attache est à l'origine, la pointe monte le long de +Z, le creux regarde vers +Y.
    Le bas s'incurve pour épouser le crâne (sans quoi les coins de l'attache resteraient en l'air)."""
    po = A.profil([(0, 0), (0.052, 0.012), (0.058, 0.040), (0.046, 0.082), (0.026, 0.118), (0.009, 0.138), (0, 0.145)], 6)

    def epouse(v):
        s = v.copy()
        s[:, 2] -= v[:, 0] ** 2 / 0.18 * (1 - K.lisse(v[:, 2] / 0.06))
        return s
    dehors = A.tour(po, 32).etire(1.0, 0.32, 1.0).sculpte(epouse)
    creux = A.tour(po, 24).etire(0.62, 0.30, 0.80).pose((0, 0.008, 0.014)).sculpte(epouse)
    return dehors, creux


def patte(chemin, blanc):
    """Une patte courte et forte : le velours roux en haut, la chaussette blanche sur les derniers « blanc » mètres."""
    ch = A.courbe(chemin, 5)
    long = float(np.sum(np.linalg.norm(np.diff(ch, axis=0), axis=1)))
    return K.tube_peint(ch, lambda t: 0.033 - 0.005 * t, [(1 - blanc / long, ROUX), (9, BLANC)], 16)


def construire():
    a = K.Animal("chien_corgi")
    a.taille = 0.70
    a.tete = PORT @ Vector((0.0, -0.104, -0.012))

    # ----- le corps : un tonneau, le jabot bombé en avant, la croupe ronde et haute comme une miche ; roux dessus,
    #       blanc dessous, une selle braise sur l'échine -----
    def coque(v):
        y = v[:, 1]
        rond = np.sqrt(np.maximum(1 - y * y, 1e-9))
        boudin = np.maximum(1 - np.abs(y) ** 2.4, 0.0) ** (1 / 2.4)
        k = boudin / rond
        s = np.stack([v[:, 0] * k, y, v[:, 2] * k], axis=1)
        s = K.bosse(s, (0, -0.70, -0.60), 0.24, 0.22)                 # le jabot
        s = K.bosse(s, (0, 0.80, 0.25), 0.16, 0.30)                   # la croupe en miche
        s = K.bosse(K.bosse(s, (0.85, -0.50, -0.10), 0.05, 0.10), (-0.85, -0.50, -0.10), 0.05, 0.10)   # les épaules
        avant = K.lisse((-s[:, 1] - 0.1) / 0.8)
        arriere = K.lisse((s[:, 1] + 0.1) / 0.9)
        s = s * [LARGE, LONG, HAUT]
        s[:, 0] *= 1 + 0.06 * avant + 0.04 * arriere                  # large partout, la croupe aussi
        s[:, 2] *= np.where(s[:, 2] < 0, 1 + 0.08 * avant - 0.18 * arriere, 1.0)
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    cv = corps.v
    dessous = cv[:, 2] < -0.030 + 0.105 * K.lisse((-cv[:, 1] - 0.13) / 0.12)      # le blanc monte sur le jabot
    selle = (cv[:, 2] > 0.062) & (cv[:, 1] > -0.17) & (cv[:, 1] < 0.21)
    corps.teinte = np.where(dessous[:, None], np.asarray(BLANC), np.where(selle[:, None], np.asarray(BRAISE), np.asarray(ROUX)))
    G.sillons(corps, [14, 42], 0.005, 1.1)
    a.piece("corps", corps, None, pos=CORPS, rot=(-6, 0, 0))
    a.couture("dos", "corps", 14, 0.60, 0.99, fil=BLANC)
    a.couture("echine", "corps", 42, 0.80, 0.99, fil=BLANC)
    a.rustine("rapiecage", "corps", CORPS + Vector((0, 0.10, 0.01)), (1.0, 0.05, 0.30),
              lambda th: 0.26 + 0.05 * math.cos(3 * th) + 0.03 * math.sin(2 * th), BLANC, feston=16, fil=BRAISE)

    # ----- le cou : court et épais, le jabot blanc devant -----
    fil_cou = K.Fil([(0.0, -0.150, 0.185), (0.002, -0.212, 0.282), (0.005, -0.262, 0.352)], flanc=(1, 0, 0))
    cou = A.tour(A.profil([(0, -0.02), (0.084, 0.0), (0.080, 0.06), (0.070, 0.12), (0.062, 0.17), (0, 0.205)], 5), 32)
    cou.teinte = np.where((cou.v[:, 1] < -0.020)[:, None], np.asarray(BLANC), np.asarray(ROUX))
    a.piece("cou", cou.sculpte(fil_cou.couche), None)

    # ----- la tête : large, les joues rieuses ; un liseré blanc descend du front et s'ouvre sur le menton -----
    def crane(v):
        v = K.bosse(v, (0, -0.55, 0.80), 0.08, 0.25)                 # le front
        v = K.bosse(K.bosse(v, (0.80, -0.50, -0.35), 0.12, 0.22), (-0.80, -0.50, -0.35), 0.12, 0.22)   # les joues
        return v * [0.088, 0.088, 0.078]
    tete = A.boule(1.0, 56, 28).sculpte(crane)
    tv = tete.v
    liste = (tv[:, 1] < -0.020) & (np.abs(tv[:, 0]) < 0.010 + 0.50 * np.maximum(0.025 - tv[:, 2], 0.0))
    menton = (tv[:, 2] < -0.032) & (tv[:, 1] < 0.020)
    tete.teinte = np.where((liste | menton)[:, None], np.asarray(BLANC), np.asarray(ROUX))
    a.piece("tete", tete, None, mat=PORT)
    a.couture("crane", "tete", 14, 0.55, 0.97, fil=BLANC)

    # ----- le museau : un museau de renard, blanc, deux touches rousses en haut des joues ; la truffe noire -----
    MU = PORT @ A.repere((0, -0.050, -0.024), (96, 0, 0))     # dans ce repère : X la gauche, Y le haut, Z vers la truffe
    MU3 = MU.to_3x3()
    museau = A.tour(A.profil([(0, -0.015), (0.064, 0.0), (0.060, 0.035), (0.049, 0.075), (0.038, 0.108), (0.029, 0.128),
                              (0, 0.140)], 6), 40)
    museau.etire(1.0, 0.84, 1.0)
    angle = np.degrees(np.arctan2(museau.v[:, 1], museau.v[:, 0]))
    joue = (np.abs(angle - 90) > 24) & (np.abs(angle - 90) < 78) & (museau.v[:, 2] < 0.052)
    museau.teinte = np.where(joue[:, None], np.asarray(ROUX), np.asarray(BLANC))
    a.piece("museau", museau, None, mat=MU)
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.022, 0.016, 0.015), K.NOIR, mat=MU @ A.repere((0, 0.006, 0.134)), poil=False)
    for nom, c in (("g", 1), ("d", -1)):                       # le grand sourire, qui remonte aux coins
        pts = [a.trace("museau", MU @ Vector((0, 0, z)), [MU3 @ Vector((c * math.cos(math.radians(d)), math.sin(math.radians(d)), 0))])[0]
               for z, d in zip(np.linspace(0.124, 0.050, 7), (-86, -80, -72, -62, -52, -42, -36))]
        a.broderie("bouche_" + nom, A.courbe(pts, 4), 0.0022, FIL)
    # la langue : un pan de feutrine framboise qui sort sous le museau et pend de travers, du côté qu'il nous tend
    a.piece("langue", A.boule(1.0, 24, 12).etire(0.017, 0.032, 0.0065), LANGUE,
            mat=MU @ A.repere((0.010, -0.042, 0.092), (-20, 0, 15)), poil=False)

    # ----- les yeux : petits et vifs ; au-dessus du gauche, un seul sourcil brodé, froncé : il ne bougera pas -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, vers(0.50 * c, -0.74, 0.30))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0145)
    sourcil = a.trace("tete", TETE, [vers(0.24, -0.82, 0.46), vers(0.40, -0.74, 0.58), vers(0.58, -0.62, 0.58), vers(0.70, -0.52, 0.48)])
    a.broderie("sourcil_g", A.courbe(sourcil, 4), 0.0024, FIL)

    # ----- les oreilles : immenses, dressées et écartées en antennes, le dos braise, le creux de feutrine blanche ;
    #       la tête penchée en couche une un peu plus que l'autre -----
    dehors, creux = oreille()
    for nom, c, ecart in (("G", 1, 0.44), ("D", -1, 0.36)):
        p, n = a.surface("tete", TETE, vers(0.48 * c, 0.04, 0.88))
        dresse = vers(ecart * c, -0.04, 0.92).normalized()
        E = A.cadre(p - dresse * 0.020, dresse, vers(0, -1, 0.10))
        a.piece("oreille_" + nom, dehors.copie(), BRAISE, mat=E)
        a.piece("pavillon_" + nom, creux.copie(), BLANC, mat=E, poil=False)

    # ----- les pattes : des moignons ; les deux de devant arc-boutées loin en avant (il refuse d'avancer), celles de
    #       derrière plantées sous de grosses cuisses ; des chaussettes blanches, les pieds tournés en dehors -----
    for nom, c, devant in (("G", 1, 0.0), ("D", -1, 0.012)):
        a.piece("patte_avant_" + nom, patte([(0.060 * c, -0.150, 0.115), (0.066 * c, -0.200 - devant, 0.062),
                                             (0.070 * c, -0.236 - devant, 0.020)], 0.080), None)
        a.piece("pied_avant_" + nom, A.boule(1.0, 24, 12).etire(0.034, 0.044, 0.017).pose((0.072 * c, -0.252 - devant, 0.0168), (0, 0, 10 * c)), BLANC)
        a.piece("cuisse_" + nom, A.boule(1.0, 32, 16).etire(0.046, 0.068, 0.064), ROUX, pos=(0.066 * c, 0.212, 0.120), rot=(-14, 0, 0))
        a.piece("patte_arriere_" + nom, patte([(0.068 * c, 0.200, 0.110), (0.072 * c, 0.212, 0.058), (0.074 * c, 0.204, 0.020)], 0.060), None)
        a.piece("pied_arriere_" + nom, A.boule(1.0, 24, 12).etire(0.033, 0.042, 0.017).pose((0.076 * c, 0.192, 0.0168), (0, 0, 6 * c)), BLANC)

    # ----- la queue : un plumeau de rien du tout, roux au pied, blanc au bout, planté en haut de la miche -----
    plumeau = A.boule(1.0, 24, 12).etire(0.022, 0.020, 0.030)
    plumeau.teinte = np.where((plumeau.v[:, 2] > 0.012)[:, None], np.asarray(BLANC), np.asarray(ROUX))
    a.piece("queue", plumeau, None, pos=(0.0, 0.318, 0.184), rot=(-35, 0, 0))
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py chien_corgi). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Le modèle est arc-bouté, les pattes avant loin devant lui (il refuse d'avancer) : c'est sa pose de repos. Les pattes
# sont assez symétriques pour leurs miroirs ; les oreilles ne le sont pas (la tête est penchée et tournée) : chacune a
# son os nommé à la main. La langue a le sien : elle pend, elle halète, elle bat au trot.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.030, 0.150)),          # le milieu du tonneau
    ("cou", "corps", (0.0, -0.155, 0.190)),            # le pied du cou, dans le jabot
    ("tete", "cou", (0.005, -0.255, 0.345)),           # la nuque, en haut du cou
    ("oreille_g", "tete", (0.053, -0.249, 0.448)),     # l'attache de chaque antenne sur le crâne
    ("oreille_d", "tete", (-0.015, -0.277, 0.470)),
    ("langue", "tete", (0.051, -0.409, 0.366)),        # la racine de la langue, sous le museau
    ("avant_G", "corps", (0.060, -0.150, 0.115)),      # l'épaule (la droite est son miroir)
    ("arriere_G", "corps", (0.066, 0.210, 0.108)),     # la hanche, au cœur de la cuisse
    ("queue", "corps", (0.0, 0.302, 0.160)),           # le pied du plumeau
]


def _oreille_os(points, cote):
    """Une oreille tout entière (le dos et son creux) sur l'os de son côté (nommé à la main, sans miroir)."""
    return {"oreille_g" if cote == "_G" else "oreille_d": np.ones(len(points))}


PORTEURS = [("corps", "corps"), ("dos", "corps"), ("echine", "corps"), ("rapiecage", "corps"),
            ("cou", "cou"),
            ("tete", "tete"), ("crane", "tete"), ("museau", "tete"), ("truffe", "tete"), ("bouche", "tete"),
            ("oeil", "tete"), ("sourcil", "tete"), ("langue", "langue"),
            ("oreille", _oreille_os), ("pavillon", _oreille_os),
            ("patte_avant", "avant", True), ("pied_avant", "avant", True),
            ("cuisse", "arriere", True), ("patte_arriere", "arriere", True), ("pied_arriere", "arriere", True),
            ("queue", "queue"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]

RAMENE = 12.0                                  # avance : les pattes avant, arc-boutées sur le modèle, reviennent sous lui
PLONGE = (48.0, 25.0)                          # mange : le cou et la tête plongent vers la gamelle
REVERENCE = 12.0                               # joie : l'avant s'incline au ras de l'herbe, la croupe en l'air
COUCHE = (-0.044, 80.0, 66.0, -44.0)           # dort : le corps descend, les pattes arrière s'étalent derrière lui
                                               # (en grenouille), le cou plonge et la tête se pose à plat sur les pattes

# chaque patte, posée : l'angle sous l'horizontale, vers l'avant, de l'épaule ou de la hanche jusqu'au milieu du pied,
# et cette longueur (les pattes avant, arc-boutées, partent loin devant)
_JAMBES = {"avant_G": (43.9, 0.1416), "avant_D": (40.7, 0.1505), "arriere_G": (78.8, 0.0930), "arriere_D": (78.8, 0.0930)}
_PIEDS = {"avant": (0.044, 0.017), "arriere": (0.042, 0.017)}     # les demi-mesures d'un pied : sa longueur, son épaisseur
_PIVOT = {n: t for n, _p, t in OS}


def _hauteur(pivot, tangage, descente):
    """La hauteur d'un pivot porté par le corps quand le corps penche de « tangage » degrés (> 0 : l'avant plonge) et
    descend de « descente »."""
    th = math.radians(tangage)
    c = _PIVOT["corps"]
    return c[2] + descente + (pivot[1] - c[1]) * math.sin(th) + (pivot[2] - c[2]) * math.cos(th)


def _pied(p, os_, degres, tangage=0.0, descente=0.0, leve=0.0, libre=False):
    """Une patte tourne de « degrés » par rapport au corps (> 0 : le pied part vers l'arrière) ; elle monte ou descend
    juste ce qu'il faut pour que son pied reste posé dans l'herbe, le corps penché de « tangage » et descendu de
    « descente » ; plus « leve » (le pied qui revient en l'air). libre : le pied peut quitter le sol, jamais s'y enfoncer."""
    a, long = _JAMBES[os_]
    pivot = _PIVOT[os_.replace("_D", "_G")]
    sol = pivot[2] - long * math.sin(math.radians(a))
    h = sol - _hauteur(pivot, tangage, descente) + long * math.sin(math.radians(a + tangage + degres))
    lg, ep = _PIEDS[os_[:-2]]
    b = math.radians(tangage + degres)                                  # le pied penché enfonce son talon ou ses doigts
    h += math.hypot(lg * math.sin(b), ep * math.cos(b)) - ep
    p.add(os_, rot=(degres, 0, 0), pos=(0, 0, (max(0.0, h) if libre else h) + leve))


def _tendu(os_, tangage=0.0, descente=0.0):
    """De combien tourner une patte pour que, tendue vers l'avant, son pied touche juste l'herbe (sans bouger son pivot)."""
    a, long = _JAMBES[os_]
    pivot = _PIVOT[os_.replace("_D", "_G")]
    x = (_hauteur(pivot, tangage, descente) - pivot[2] + long * math.sin(math.radians(a))) / long
    return math.degrees(math.asin(max(-1.0, min(1.0, x)))) - a - tangage


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _oreilles(p, avant, dehors=0.0):
    """Les deux antennes ensemble : elles basculent vers l'avant (degrés > 0, vers l'arrière < 0) et s'écartent (dehors)."""
    p.add("oreille_g", rot=(avant, dehors, 0))
    p.add("oreille_d", rot=(avant, -dehors, 0))


def repos(t):
    """Arc-bouté, ravi de ne pas bouger : il halète, la langue pendue qui ballotte ; il penche la tête de l'autre côté
    (« hein ? »), la remet, puis secoue la tête, têtu : non, il n'avancera pas ; les antennes tressaillent, le plumeau
    frétille ; il cligne."""
    p = Pose()
    r = onde(t, 2)
    halete = onde(t, 16)
    p.add("corps", ech=(1 + 0.012 * r + 0.004 * halete, 1, 1 + 0.016 * r + 0.006 * halete))
    hein = cloche(t, 0.36, 0.12)
    non = cloche(t, 0.76, 0.07) * onde(t, 14)
    p.add("cou", rot=(0, -4 * hein, 3 * non))
    p.add("tete", rot=(-4 * hein, -30 * hein, 14 * non))
    p.add("langue", rot=(6 * halete, 0, 5 * onde(t, 4) + 10 * non))
    _oreilles(p, -8 * cloche(t, 0.20, 0.04) + 6 * hein, 4 * cloche(t, 0.56, 0.04))
    p.add("queue", rot=(0, 0, 28 * onde(t, 12) * cloche(t, 0.55, 0.09)))
    p.ouvert = 1 - cloche(t, 0.10, 0.04) - cloche(t, 0.60, 0.04)
    return p


def avance(t):
    """Son petit trot de tonneau : les pattes avant reviennent sous lui et ses moignons moulinent, les diagonales
    ensemble ; la croupe en miche se dandine, les grandes antennes ballottent, la langue bat au vent, le plumeau balance."""
    p = Pose()
    for os_, phase in (("avant_G", 0.0), ("arriere_D", 0.0), ("avant_D", 0.5), ("arriere_G", 0.5)):
        a = math.tau * (t + phase)
        base = RAMENE if os_.startswith("avant") else 0.0
        _pied(p, os_, base + 20 * math.sin(a), leve=0.010 * max(0.0, -math.cos(a)), libre=True)
    p.add("corps", pos=(0, 0, 0.005 * (0.5 - 0.5 * math.cos(2 * math.tau * t))), rot=(0, 4 * onde(t, 1), 3 * onde(t, 1, 0.25)))
    p.add("cou", rot=(0, -2 * onde(t, 1), -3 * onde(t, 1, 0.25)))
    p.add("tete", rot=(3 * onde(t, 2), 0, 0))
    _oreilles(p, 7 * onde(t, 2, -0.1), 3 * onde(t, 2))
    p.add("langue", rot=(14 * onde(t, 2, -0.15), 0, 8 * onde(t, 1)))
    p.add("queue", rot=(0, 0, 18 * onde(t, 2)))
    return p


def mange(t):
    """Les pattes déjà plantées devant lui, il plonge le nez dans la gamelle et lape à grands coups de langue, le
    plumeau en folie ; puis il relève la tête, se pourlèche les babines et retrouve son sourire de travers."""
    p = Pose()
    bas = _plateau(t, 0.42, 0.26, 0.12)
    lape = onde(t, 10) * _plateau(t, 0.42, 0.20, 0.06)
    leche = cloche(t, 0.86, 0.05)
    p.add("cou", rot=(PLONGE[0] * bas, 0, 0))
    p.add("tete", rot=(PLONGE[1] * bas + 3 * lape - 8 * leche, 0, -10 * bas))
    p.add("langue", rot=(16 * lape - 34 * leche, 0, 0))
    _oreilles(p, 8 * bas, 6 * bas)
    p.add("queue", rot=(0, 0, 24 * onde(t, 8) * bas))
    p.ouvert = 1 - cloche(t, 0.94, 0.03)
    return p


def joie(t):
    """Sa fête : la révérence du jeu, l'avant au ras de l'herbe, la croupe en l'air qui se tortille ; puis deux bonds sur
    place, les antennes rabattues, la langue au vent, le plumeau fou ; il retombe arc-bouté, content de lui."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85)) if t < 0.85 else 0.0
    salut = cloche(t, 0.22, 0.20, False)
    u = borne((t - 0.42) / 0.40)
    saut = abs(math.sin(2 * math.pi * u))
    tangage, descente = REVERENCE * salut, -0.012 * salut
    p.add("corps", pos=(0, 0, descente + 0.045 * saut), rot=(tangage - 3 * saut, 0, 5 * onde(t, 4) * salut))
    for os_ in ("avant_G", "avant_D", "arriere_G", "arriere_D"):
        _pied(p, os_, _tendu(os_, tangage, descente), tangage, descente)
        p.add(os_, rot=(-14 * saut if os_.startswith("avant") else 14 * saut, 0, 0))   # en l'air, les pattes se replient
    p.add("cou", rot=(-0.8 * tangage - 4 * saut, 0, 0))
    p.add("tete", rot=(-6 * salut - 10 * saut, 0, 8 * onde(t, 3) * env))
    _oreilles(p, -18 * saut - 6 * salut, 10 * saut)
    p.add("langue", rot=(16 * onde(t, 6) * env, 0, 6 * onde(t, 3) * env))
    p.add("queue", rot=(0, 0, 34 * onde(t, 12) * env))
    return p


def dort(t):
    """Il s'étale en grenouille, la sieste du corgi : à plat ventre, les pattes de devant tendues, celles de derrière
    allongées loin derrière lui, la tête posée à plat sur les pattes, les antennes tombées de côté, le bout de la langue
    qui dépasse ; les yeux fermés, le tonneau respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    d = COUCHE[0]
    p.add("corps", pos=(0, 0, d), ech=(1 + 0.015 * r, 1, 1 + 0.025 * r))
    for os_ in ("avant_G", "avant_D"):
        _pied(p, os_, _tendu(os_, 0.0, d), 0.0, d)
    for os_ in ("arriere_G", "arriere_D"):
        _pied(p, os_, COUCHE[1], 0.0, d, libre=True)
    p.add("cou", rot=(COUCHE[2], 0, 0))
    p.add("tete", rot=(COUCHE[3], 0, 0))
    _oreilles(p, -14, 18)
    p.add("langue", rot=(-12 + 3 * r, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Corgi")
