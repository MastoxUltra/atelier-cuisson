"""Le scarabée en peluche : un lucane cerf-volant. Une carapace de feutrine bleu pétrole fendue d'une couture claire,
la tête et le corselet presque noirs, et deux mandibules énormes, en bois de cerf, acajou. Un petit char d'assaut :
trapu, dressé sur ses pattes avant, les bois levés comme des poings, la tête tournée vers celui qui approche.

    python scarabee.py        fabrique la fiche art/apercus/animaux/scarabee.png
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

PETROLE = M.hexa("#134f66")                   # le bleu nuit pétrole des élytres
NUIT = M.hexa("#181b26")                      # la tête et le corselet : presque noirs, mais le poil s'y lit encore
ACAJOU = M.hexa("#9a3b22")                    # les bois, les cernes, la pièce du dos, le bout des pattes
OSSEUX = M.hexa("#f0dfbd")                    # la pointe des bois
# le corps se cabre en trois temps : les élytres à peine relevés (on doit voir leur dôme), le corselet davantage,
# la tête encore plus, et tournée vers nous
CABRE = A.repere((0, 0, 0.055), (-11, 0, 0))
CORSELET = CABRE @ A.repere((0, -0.068, 0.020), (-12, 0, 8))
PORT = CORSELET @ A.repere((0, -0.058, 0.004), (-8, 0, 14))


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête, rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def tube_peint(chemin, rayon, paliers, cotes=12):
    """Un tube peint par tronçons le long de son fil : paliers = [(fraction du chemin, couleur), ...], la dernière
    fraction à 1 ou plus. Le chemin est recoupé tous les 4 mm pour que la limite des couleurs reste nette."""
    ch = np.asarray(chemin, float)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(ch, axis=0), axis=1))])
    t = np.linspace(0.0, 1.0, max(6, int(fait[-1] / 0.004)))
    ch = np.stack([np.interp(t * fait[-1], fait, ch[:, k]) for k in range(3)], axis=1)
    m = A.tube(ch, rayon, cotes)
    t = np.concatenate([np.repeat(t, cotes), [0.0, 1.0]])           # les anneaux du tube, puis ses deux bouchons
    m.teinte = np.zeros((len(t), 3))
    for seuil, couleur in reversed(paliers):
        m.teinte[t <= seuil] = couleur
    return m


def patte(hanche, genou, pied, gros):
    """Une patte courte et épaisse en feutrine : la hanche sous le corps, le genou dehors, le pied à plat qui pointe
    vers l'extérieur. Elle s'affine, et son dernier quart est acajou."""
    loin = Vector((pied[0] - hanche[0], pied[1] - hanche[1], 0)).normalized() * (gros * 1.9)
    points = [hanche, genou, (pied[0], pied[1], gros * 1.05), (pied[0] + loin.x, pied[1] + loin.y, gros * 0.58)]
    return tube_peint(A.conges(points, 0.012, 5), lambda u: gros * (1 - 0.45 * u), [(0.74, NUIT), (9, ACAJOU)])


def bois(cote):
    """Une mandibule en bois de cerf, dans le repère de la tête (cote : 1 à gauche, -1 à droite) : le merrain part
    du coin de la mâchoire, s'écarte, monte et se referme ; une dent au milieu, tournée vers l'intérieur ;
    une fourche au bout. Les trois pointes s'effilent et sont couleur d'os, comme polies à force de servir."""
    def branche(points, gros, fin, pointe):
        fil = A.courbe([(cote * x, y, z) for x, y, z in points], 6)
        debut = pointe - 0.6 * (1 - pointe)             # la branche commence à s'effiler un peu avant sa pointe claire
        return tube_peint(fil, lambda t: (gros - (gros - fin) * t) * (1 - 0.72 * float(K.lisse((t - debut) / (1 - debut)))),
                          [(pointe, ACAJOU), (9, OSSEUX)], 14)
    merrain = branche([(0.036, -0.014, -0.012), (0.076, -0.040, -0.006), (0.106, -0.078, 0.010),
                       (0.112, -0.122, 0.032), (0.092, -0.160, 0.052), (0.056, -0.180, 0.066)], 0.0190, 0.0100, 0.89)
    dent = branche([(0.103, -0.070, 0.007), (0.088, -0.090, 0.022), (0.070, -0.099, 0.042)], 0.0125, 0.0075, 0.56)
    fourche = branche([(0.098, -0.150, 0.047), (0.108, -0.172, 0.064), (0.112, -0.188, 0.090)], 0.0115, 0.0070, 0.54)
    return merrain + dent + fourche


def construire():
    a = K.Animal("scarabee")
    a.taille = 0.34
    a.tete = PORT @ Vector((0, -0.040, 0.006))

    # ----- les élytres : une coque de feutrine tournée de la pointe arrière aux épaules, le dos en dôme, le ventre plat ;
    #       un sillon profond la fend en deux, tenu par une couture claire, et deux côtes légères rident chaque élytre -----
    profil = A.profil([(0, 0), (0.032, 0.010), (0.062, 0.052), (0.078, 0.104), (0.082, 0.148), (0.079, 0.178), (0.064, 0.197), (0, 0.202)], 6)

    def dome(v):
        s = v.copy()
        s[:, 1] *= np.where(v[:, 1] > 0, 0.98, 0.28)
        return s
    elytres = A.tour(profil, 56).sculpte(dome)
    G.sillons(elytres, [14], 0.006, 1.3)
    G.sillons(elytres, [6, 22], 0.002, 0.9)
    a.piece("elytres", elytres, PETROLE, mat=CABRE @ A.repere((0, 0.155, 0), (90, 0, 0)), poil=False)
    a.couture("suture", "elytres", 14, 0.06, 0.95, "croix", fil=K.CREME, large=0.008, haut=0.0018, pas=0.0125)
    # la pièce d'un bagarreur : un carré d'acajou recousu de travers sur l'élytre gauche
    a.rustine("piece", "elytres", CABRE @ Vector((0, 0.064, 0.004)), CABRE.to_3x3() @ Vector((0.60, 0.22, 0.77)),
              lambda th: 0.27 * (1 - 0.11 * math.cos(4 * (th - 0.3))), ACAJOU, 0.003, 14, fil=K.CREME)

    # ----- le corselet : une plaque de blindage en peluche noire, carrée d'épaules -----
    def plaque(v):
        s = np.sign(v) * np.abs(v) ** 0.72 * [0.066, 0.042, 0.046]
        s[:, 0] *= 1 + 0.08 * v[:, 1]                   # plus large derrière, contre les élytres
        return s
    corselet = A.boule(1.0, 48, 24).sculpte(plaque)
    G.sillons(corselet, [12, 36], 0.004, 1.2)
    a.piece("corselet", corselet, NUIT, mat=CORSELET)

    # ----- la tête : un pavé large et bas, deux crêtes au-dessus des yeux -----
    def caboche(v):
        v = K.bosse(K.bosse(v, (0.72, -0.30, 0.62), 0.10, 0.2), (-0.72, -0.30, 0.62), 0.10, 0.2)
        s = np.sign(v) * np.abs(v) ** 0.72 * [0.052, 0.034, 0.032]
        s[:, 0] *= 1 - 0.08 * v[:, 1]                   # plus large devant
        return s
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(caboche), NUIT, mat=PORT)

    # ----- le regard : deux petits boutons rapprochés, cernés d'acajou (sur le noir ils se perdraient), et deux gros
    #       sourcils de fil clair qui plongent vers le milieu en mordant sur le haut des boutons -----
    centre = PORT @ Vector((0, 0, 0))
    for nom, cote in (("G", 1), ("D", -1)):
        regard = vers(0.55 * cote, -0.76, 0.34)
        a.rustine("cerne_" + nom, "tete", centre, regard, 0.37, ACAJOU, 0.0025, 0)
        p, n = a.surface("tete", centre, regard)
        a.bouton("oeil_" + nom, p + n * 0.0028, n, 0.0125)
        sourcil = a.trace("tete", centre, [vers(0.14 * cote, -0.80, 0.36), vers(0.51 * cote, -0.60, 0.62), vers(0.79 * cote, -0.29, 0.54)], 0.0050)
        a.broderie("sourcil_" + nom, A.courbe(sourcil, 5), 0.0032, K.CREME)

    # ----- les bois : deux mandibules énormes, levées et ouvertes -----
    a.piece("mandibule_G", bois(1), None, mat=PORT, poil=False)
    a.piece("mandibule_D", bois(-1), None, mat=PORT, poil=False)

    # ----- les six pattes, courtes et épaisses : celles de devant, plantées loin devant, tiennent le poitrail en l'air ;
    #       aucun pied n'est posé comme son vis-à-vis : il piétine, prêt à charger -----
    genoux = ((0.098, -0.110, 0.090), (0.112, -0.012, 0.070), (0.100, 0.084, 0.056))
    pieds = {1: ((0.106, -0.156), (0.132, 0.012), (0.108, 0.114)), -1: ((0.122, -0.130), (0.128, -0.008), (0.104, 0.128))}
    for cote, nom in ((1, "pattes_g"), (-1, "pattes_d")):
        hanches = (CORSELET @ Vector((0.046 * cote, -0.010, -0.036)), CABRE @ Vector((0.058 * cote, -0.012, -0.018)),
                   CABRE @ Vector((0.056 * cote, 0.050, -0.018)))
        pattes = None
        for i in range(3):
            (gx, gy, gz), (px, py) = genoux[i], pieds[cote][i]
            une = patte(tuple(hanches[i]), (cote * gx, gy, gz), (cote * px, py), 0.0165 if i == 0 else 0.0135)
            pattes = une if pattes is None else pattes + une
        a.piece(nom, pattes, None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py scarabee). Les mesures sont celles du modèle, avant a.taille.

from poses import Pose, borne, cloche, onde

# Il n'est pas symétrique : le corselet tourne de 8°, la tête de 14° de plus, aucun pied n'est posé comme son vis-à-vis.
# Les bois et les pattes ont donc chacun leur os à sa vraie place, nommés _g et _d, sans miroir. Les trois pattes d'un
# côté sont une seule pièce (pattes_g, pattes_d) : chaque point suit la patte dont le fil passe le plus près. Les pattes
# pendent à la racine : un pied posé ne bouge pas quand le corps roule au-dessus de lui.
T3 = np.array(PORT.to_3x3())                   # les axes de la tête, en colonnes : sa gauche, son arrière, son dessus
_GENOUX = ((0.098, -0.110, 0.090), (0.112, -0.012, 0.070), (0.100, 0.084, 0.056))           # les mêmes que dans construire
_PIEDS = {1: ((0.106, -0.156), (0.132, 0.012), (0.108, 0.114)), -1: ((0.122, -0.130), (0.128, -0.008), (0.104, 0.128))}


def _fil(cote, i):
    """Le fil d'une patte telle que construire() la dessine : la hanche, le genou, le pied."""
    hanche = (CORSELET @ Vector((0.046 * cote, -0.010, -0.036)), CABRE @ Vector((0.058 * cote, -0.012, -0.018)),
              CABRE @ Vector((0.056 * cote, 0.050, -0.018)))[i]
    gx, gy, gz = _GENOUX[i]
    px, py = _PIEDS[cote][i]
    return [np.array(hanche, float), np.array((cote * gx, gy, gz)), np.array((cote * px, py, (0.0165 if i == 0 else 0.0135) * 1.05))]


FILS = {"%s_%s" % (r, l): _fil(c, i) for l, c in (("g", 1), ("d", -1)) for i, r in enumerate(("avant", "milieu", "arriere"))}
CORPS = np.array((0.0, 0.048, 0.046))          # le pivot du corps : au-dessus des hanches de derrière, il se cabre autour

OS = ([("racine", None, (0, 0, 0)),
       ("corps", "racine", tuple(CORPS)),                         # le milieu des élytres, côté arrière
       ("corselet", "corps", (0.0, -0.038, 0.072)),              # l'attache du corselet sur les élytres
       ("tete", "corselet", (0.0, -0.096, 0.098)),               # la nuque, à l'arrière de la tête
       ("mandibule_g", "tete", (0.047, -0.119, 0.106)),          # le coin de la mâchoire, à gauche
       ("mandibule_d", "tete", (-0.020, -0.144, 0.115))]         # et à droite (la tête est tournée : pas de miroir)
      + [("patte_" + n, "racine", tuple(np.round(f[0], 3))) for n, f in FILS.items()])     # les six hanches


def _cote(nom):
    """Une pièce d'un côté (mandibule_G, mandibule_D) suit l'os de son côté (mandibule_g, mandibule_d)."""
    return lambda points, cote: {nom + cote.lower(): np.ones(len(points))}


def _pattes(lettre):
    """Les trois pattes d'un côté, une seule pièce : chaque point suit la patte dont le fil passe le plus près."""
    def poids(points, cote):
        miennes = [n for n in FILS if n.endswith(lettre)]
        ecarts = []
        for n in miennes:
            e = np.full(len(points), 9.0)
            for a, b in zip(FILS[n][:-1], FILS[n][1:]):
                u = np.clip((points - a) @ (b - a) / ((b - a) @ (b - a)), 0.0, 1.0)
                e = np.minimum(e, np.linalg.norm(points - a - u[:, None] * (b - a), axis=1))
            ecarts.append(e)
        proche = np.argmin(ecarts, axis=0)
        return {"patte_" + n: (proche == k).astype(float) for k, n in enumerate(miennes)}
    return poids


PORTEURS = [("elytres", "corps"), ("suture", "corps"), ("piece", "corps"), ("corselet", "corselet"),
            ("tete", "tete"), ("cerne", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("mandibule", _cote("mandibule")),
            ("pattes_g", _pattes("_g")), ("pattes_d", _pattes("_d")),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def tour(axe, degres):
    """La rotation de « degres » autour d'un axe, en matrice 3 × 3."""
    x, y, z = np.asarray(axe, float) / np.linalg.norm(axe)
    a = math.radians(degres)
    c, s, u = math.cos(a), math.sin(a), 1 - math.cos(a)
    return np.array([[c + x * x * u, x * y * u - z * s, x * z * u + y * s],
                     [y * x * u + z * s, c + y * y * u, y * z * u - x * s],
                     [z * x * u - y * s, z * y * u + x * s, c + z * z * u]])


def angles(R):
    """Les angles qu'attend Pose (degrés, autour des axes du monde : X, puis Y, puis Z) pour la rotation R."""
    return (math.degrees(math.atan2(R[2, 1], R[2, 2])), math.degrees(math.asin(-max(-1.0, min(1.0, R[2, 0])))),
            math.degrees(math.atan2(R[1, 0], R[0, 0])))


def campe(p, cabre=0.0, monte=(0.0, 0.0, 0.0), roule=0.0, lacet=0.0, ech=(1, 1, 1)):
    """Pose le corps : « cabre » > 0 lève l'avant (degrés), « roule » > 0 le couche sur sa gauche, « lacet » > 0 le tourne
    vers sa gauche ; « monte » le déplace. Rend sa rotation et son déplacement, pour les pattes qui doivent le suivre."""
    R = tour((0, 0, 1), lacet) @ tour((0, 1, 0), roule) @ tour((1, 0, 0), -cabre)
    p.add("corps", rot=angles(R), pos=tuple(monte), ech=ech)
    return R, np.asarray(monte, float)


def jambe(p, nom, arriere=0.0, leve=0.0, suit=None):
    """Tourne une patte sur sa hanche : « arriere » degrés vers l'arrière (autour de la verticale), « leve » degrés vers le
    haut (le pied monte en s'écartant). suit = ce que rend campe : la patte suit alors le corps (elle quitte le sol)."""
    H, F = FILS[nom][0], FILS[nom][2]
    c = 1 if nom.endswith("g") else -1
    R = tour((0, 0, 1), c * arriere) @ tour(np.cross((F - H) * [1, 1, 0], (0, 0, 1)), leve)
    pos = np.zeros(3)
    if suit is not None:
        Rc, monte = suit
        R, pos = Rc @ R, Rc @ (H - CORPS) + CORPS + monte - H
    p.add("patte_" + nom, rot=angles(R), pos=tuple(pos))


def pince(p, ouvre=0.0, leve=0.0):
    """Les bois : « ouvre » > 0 les écarte (degrés, autour du dessus de la tête), « leve » > 0 les dresse vers le ciel."""
    for l, c in (("g", 1), ("d", -1)):
        p.add("mandibule_" + l, rot=angles(tour(T3[:, 2], c * ouvre) @ tour(T3[:, 0], -leve)))


def tete(p, hoche=0.0, tourne=0.0, penche=0.0):
    """La tête autour de ses axes à elle : hoche > 0, le nez plonge ; tourne > 0, elle regarde vers sa gauche ;
    penche > 0, elle se couche sur son épaule gauche."""
    p.add("tete", rot=angles(tour(T3[:, 2], tourne) @ tour(T3[:, 0], hoche) @ tour(T3[:, 1], penche)))


def repos(t):
    """Le petit char attend : il respire, la tête suit celui qui approche puis revient sur lui ; il gonfle le poitrail
    et brandit ses bois en les claquant deux fois (qu'on se le dise), puis piétine de la patte avant droite, prêt à
    charger. Il cligne deux fois."""
    p = Pose()
    r = onde(t, 2)
    menace = cloche(t, 0.46, 0.13)
    clac = cloche(t, 0.42, 0.035) + cloche(t, 0.52, 0.035)
    pietine = cloche(t, 0.74, 0.035) + cloche(t, 0.84, 0.035)
    campe(p, 1.5 * menace, ech=(1 + 0.012 * r, 1, 1 + 0.018 * r))
    p.add("corselet", rot=(-4 * menace - 1.0 * r, 0, 0))
    tete(p, -6 * menace, 16 * cloche(t, 0.20, 0.11) - 6 * cloche(t, 0.66, 0.08))
    pince(p, 14 * menace - 16 * clac, 10 * menace)
    jambe(p, "avant_d", -6 * pietine, 16 * pietine)
    p.ouvert = 1 - cloche(t, 0.10, 0.02) - cloche(t, 0.62, 0.02)
    return p


def avance(t):
    """Il charge au pas, lourd comme un char : deux trépieds de pattes à contretemps (l'avant et l'arrière d'un côté,
    le milieu de l'autre), chaque patte se lève en revenant devant et pousse au sol en reculant. Le corps roule d'un
    trépied sur l'autre, la tête dodeline à chaque pas, les bois tanguent."""
    p = Pose()
    s = onde(t, 1)
    campe(p, 0.8 * onde(t, 2, 0.25), (0, 0, 0.0015 * abs(onde(t, 1, 0.25))), roule=-2.5 * s, lacet=-2.0 * s)
    for nom in FILS:
        ph = math.tau * t + (0.0 if nom in ("avant_g", "milieu_d", "arriere_g") else math.pi)
        jambe(p, nom, 15 * math.sin(ph), 17 * max(0.0, -math.cos(ph)))
    p.add("corselet", rot=(1.5 * onde(t, 2), 0, 2 * s))
    tete(p, 3 * onde(t, 2, 0.15), -4 * s)
    pince(p, 2 * onde(t, 2, 0.3), 2 * onde(t, 2))
    return p


def mange(t):
    """Il plonge le poitrail vers la sève, les bois à ras de l'herbe, lèche à petits coups de tête en ouvrant et
    refermant les bois, puis se redresse."""
    p = Pose()
    bas = 1 - cloche(t, 0.88, 0.12)
    coups = abs(onde(t, 5)) * bas
    campe(p, -7 * bas)
    p.add("corselet", rot=(9 * bas, 0, 0))
    tete(p, 14 * bas + 7 * coups, -8 * bas)
    pince(p, 10 * bas * onde(t, 5, 0.25), -6 * bas)
    p.ouvert = 1 - cloche(t, 0.93, 0.02)
    return p


def joie(t):
    """Un saut de victoire : il s'arrache du sol, les six pattes pendantes, le poitrail dressé et les bois grands
    ouverts levés vers le ciel comme deux poings ; il retombe, claque deux fois des bois et se campe."""
    p = Pose()
    air = math.sin(math.pi * borne((t - 0.08) / 0.46)) if 0.08 < t < 0.54 else 0.0
    fier = math.sin(math.pi * borne(t / 0.86)) if t < 0.86 else 0.0
    clac = cloche(t, 0.64, 0.05, False) + cloche(t, 0.76, 0.05, False)
    suit = campe(p, 9 * air, (0, 0, 0.034 * air))
    for nom in FILS:
        jambe(p, nom, (-14 if nom.startswith("avant") else 6) * air, 10 * air, suit)
    p.add("corselet", rot=(-10 * fier, 0, 0))
    tete(p, -12 * fier)
    pince(p, 22 * fier - 20 * clac, 16 * fier)
    return p


def dort(t):
    """Il s'est tassé sur le ventre, le poitrail posé, la tête basse, les bois couchés dans l'herbe ; les yeux fermés,
    il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    campe(p, -3.5, (0, 0, -0.004), ech=(1 + 0.010 * r, 1, 1 + 0.016 * r))
    p.add("corselet", rot=(10, 0, 0))
    tete(p, 12 + 1.5 * r, -6)
    pince(p, -4, -12)
    for nom in FILS:
        jambe(p, nom, 8 if nom.startswith("arriere") else -4, 0.0)
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Scarabée")
