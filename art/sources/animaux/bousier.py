"""Le bousier en peluche : une boule de muscles. Deux élytres de feutrine violet améthyste, bombés et côtelés, des
épaules de velours violet plus larges que le reste, la tête et les pattes noir charbon, le chaperon en pelle crénelée
au ras du sol, et une petite corne dont la pointe est dorée. Un travailleur têtu : arc-bouté sur ses pattes arrière,
le derrière en l'air, la tête basse, le regard par en dessous sous deux gros sourcils, il pousse de toutes ses forces.

    python bousier.py        fabrique la fiche art/apercus/animaux/bousier.png
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

AMETHYSTE = M.hexa("#8a45d8")                 # la feutrine des élytres : un violet améthyste vif
EPAULES = M.hexa("#9457dc")                   # le velours du corselet (le poil fonce et sature : il sort plus profond)
CHARBON = M.hexa("#26262c")                   # la tête, le chaperon, les pattes
OR = K.JAUNE                                  # l'accent : la pointe de la corne, le fil de la suture
BASCULE = A.repere((0, 0.035, 0.118), (18, -5, 6))                 # le corps pique du nez : le derrière en l'air, une épaule en avant
PORT = BASCULE @ A.repere((0, -0.150, 0.004), (-10, 0, 12))        # la tête, basse, juste au-dessus de l'herbe, tournée vers nous
TETE = PORT @ Vector((0, 0, 0))


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
    """Une patte courte et très épaisse en feutrine charbon : la hanche sous le corps, le genou dehors, le pied à plat
    qui prolonge le tibia. La cuisse est renflée, comme un mollet de pilier de mêlée."""
    loin = Vector((pied[0] - genou[0], pied[1] - genou[1], 0)).normalized() * (gros * 1.7)
    points = [hanche, genou, (pied[0], pied[1], gros * 1.0), (pied[0] + loin.x, pied[1] + loin.y, gros * 0.55)]
    return A.tube(A.conges(points, 0.014, 5), lambda u: gros * (1 + 0.30 * math.exp(-((u - 0.22) / 0.16) ** 2) - 0.42 * u), 14)


def construire():
    a = K.Animal("bousier")
    a.taille = 0.30
    a.tete = PORT @ Vector((0, -0.030, 0.020))

    # ----- les élytres : un dôme de feutrine, court et rond, tourné de la pointe arrière aux épaules ; un sillon profond
    #       le fend en deux élytres, tenu par une suture dorée, et deux côtes creusent chaque élytre -----
    profil = A.profil([(0, 0), (0.044, 0.007), (0.080, 0.036), (0.094, 0.076), (0.095, 0.110), (0.086, 0.136), (0.066, 0.150), (0, 0.155)], 6)

    def dome(v):
        s = v.copy()
        s[:, 1] *= np.where(v[:, 1] > 0, 1.04, 0.34)
        return s
    elytres = A.tour(profil, 56).sculpte(dome)
    G.sillons(elytres, [14], 0.007, 1.4)
    G.sillons(elytres, [4, 9, 19, 24], 0.0055, 1.0)
    a.piece("elytres", elytres, AMETHYSTE, mat=BASCULE @ A.repere((0, 0.085, 0), (90, 0, 0)), poil=False)
    a.couture("suture", "elytres", 14, 0.05, 0.96, "croix", fil=OR, large=0.010, haut=0.0020, pas=0.0150)
    a.ourlet("col", "elytres", 0.86, fil=OR, haut=0.0020, pas=0.014)

    # ----- le corselet : les épaules. Un bloc de velours plus large que les élytres, avec deux bosses de déménageur -----
    def carrure(v):
        v = K.bosse(K.bosse(v, (0.80, -0.10, 0.60), 0.16, 0.22), (-0.80, -0.10, 0.60), 0.16, 0.22)
        s = np.sign(v) * np.abs(v) ** 0.78 * [0.112, 0.058, 0.074]
        s[:, 2] *= np.where(v[:, 2] > 0, 1.0, 0.62)
        return s
    corselet = A.boule(1.0, 56, 28).sculpte(carrure)
    G.sillons(corselet, [14, 42], 0.004, 1.2)
    a.piece("corselet", corselet, EPAULES, mat=BASCULE @ A.repere((0, -0.085, -0.010)))

    # ----- la tête : un crâne bas en velours charbon, et devant lui le chaperon : une pelle de feutrine épaisse, plus
    #       large devant, dont le bord est taillé en quatre créneaux carrés ; elle passe juste au-dessus de l'herbe -----
    def crane(v):
        s = K.emousse(v, 0.85) * [0.052, 0.042, 0.036]
        s[:, 2] *= np.where(v[:, 2] > 0, 1.0, 0.70)
        return s
    a.piece("crane", A.boule(1.0, 56, 28).sculpte(crane), CHARBON, mat=PORT)
    moitie = [(0.0, 0.0), (0.056, 0.0), (0.082, 0.060), (0.082, 0.086), (0.046, 0.086), (0.046, 0.062), (0.036, 0.062),
              (0.036, 0.090), (0.005, 0.090), (0.005, 0.066)]
    tour = moitie + [(-x, y) for x, y in reversed(moitie)]                     # la moitié gauche, puis son miroir

    def releve(y):
        return 0.012 * (y / 0.090) ** 2                                       # la lame se relève vers son bord
    lame = A.decoupe(A.conges([(x, -y) for x, y in tour], 0.005, 3)[:-1], 0.018, 0.003)
    lame.sculpte(lambda v: v + np.stack([0 * v[:, 0], 0 * v[:, 0], releve(v[:, 1])], axis=1))
    pose = PORT @ A.repere((0, -0.014, -0.016), (8, 0, 0))
    a.piece("chaperon", lame, CHARBON, mat=pose, poil=False)
    # un point avant doré court le long du bord, à un demi-centimètre : même de loin, noir sur l'herbe, on lit les créneaux
    demi = [(0.060, 0.026), (0.074, 0.060), (0.074, 0.079), (0.053, 0.079), (0.053, 0.055), (0.029, 0.055), (0.029, 0.083),
            (0.012, 0.083), (0.012, 0.059)]
    piste = [(x, -y, 0.0102 + releve(y)) for x, y in demi + [(-x, y) for x, y in reversed(demi)]]
    a.piece("chaperon_points", G.couture(piste, [(0, 0, 1)] * len(piste), 0.0125, 0.0080, 0.0017, 0.0012), OR, mat=pose, poil=False)

    # ----- le regard : deux gros boutons sur deux ronds de feutrine lilas (sur le noir ils se perdraient), et par-dessus
    #       deux sourcils de feutrine charbon, épais, qui plongent vers le milieu : il serre les dents -----
    for nom, cote in (("G", 1), ("D", -1)):
        regard = vers(0.54 * cote, -0.50, 0.68)
        a.rustine("cerne_" + nom, "crane", TETE, regard, 0.50, K.LILAS, 0.003, 0)
        p, n = a.surface("crane", TETE, regard)
        a.bouton("oeil_" + nom, p + n * 0.003, n, 0.0155)
        bouts = a.trace("crane", TETE, [vers(0.92 * cote, -0.04, 0.50), vers(0.10 * cote, -0.62, 0.78)], 0.0065)
        milieu = a.trace("crane", TETE, [vers(0.50 * cote, -0.30, 0.80)], 0.0115)
        a.piece("sourcil_" + nom, A.tube(A.courbe([bouts[0], milieu[0], bouts[1]], 6), 0.0062, 12), CHARBON, poil=False)

    # ----- la petite corne : plantée sur le crâne, recourbée vers l'arrière, la pointe dorée -----
    p, n = a.surface("crane", TETE, vers(0, -0.30, 0.95))
    fil = A.courbe([p - n * 0.006, p + vers(0, -0.006, 0.019), p + vers(0, 0.004, 0.038), p + vers(0, 0.020, 0.050)], 6)
    a.piece("corne", tube_peint(fil, lambda t: 0.0115 - 0.0078 * t, [(0.42, CHARBON), (9, OR)], 14), None, poil=False)

    # ----- les six pattes, épaisses : celles de devant plantées de part et d'autre de la tête, celles de derrière
    #       tendues loin en arrière, qui poussent ; aucun pied n'est posé comme son vis-à-vis -----
    hanches = ((0.080, -0.078, 0.074), (0.088, 0.000, 0.084), (0.060, 0.092, 0.118))
    genoux = ((0.124, -0.096, 0.076), (0.134, 0.028, 0.088), (0.094, 0.140, 0.122))
    pieds = {1: ((0.118, -0.146), (0.138, 0.080), (0.100, 0.190)), -1: ((0.110, -0.128), (0.132, 0.094), (0.088, 0.172))}
    for cote, nom in ((1, "pattes_G"), (-1, "pattes_D")):
        pattes = None
        for i in range(3):
            (hx, hy, hz), (gx, gy, gz), (px, py) = hanches[i], genoux[i], pieds[cote][i]
            une = patte((cote * hx, hy, hz), (cote * gx, gy, gz), (cote * px, py), (0.0220, 0.0185, 0.0205)[i])
            pattes = une if pattes is None else pattes + une
        a.piece(nom, pattes, CHARBON, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py bousier). Les mesures sont celles du modèle, avant a.taille.

from poses import Pose, borne, cloche, onde

# Les hanches sont symétriques : les os des pattes finissent en _G et l'usine les recopie en _D. Les trois pattes d'un
# côté sont une seule pièce (pattes_G, pattes_D) : chaque point suit la patte dont le fil passe le plus près. Les pattes
# pendent à la racine : un pied posé ne bouge pas quand le corps roule au-dessus de lui. La tête est tournée de 12° :
# on la fait tourner autour de ses axes à elle.
T3 = np.array(PORT.to_3x3())                   # les axes de la tête, en colonnes : sa gauche, son arrière, son dessus
_HANCHES = ((0.080, -0.078, 0.074), (0.088, 0.000, 0.084), (0.060, 0.092, 0.118))           # les mêmes que dans construire
_GENOUX = ((0.124, -0.096, 0.076), (0.134, 0.028, 0.088), (0.094, 0.140, 0.122))
_PIEDS = {1: ((0.118, -0.146), (0.138, 0.080), (0.100, 0.190)), -1: ((0.110, -0.128), (0.132, 0.094), (0.088, 0.172))}
RANGS = ("avant", "milieu", "arriere")
FILS = {"%s_%s" % (r, l): [np.array((c * _HANCHES[i][0], _HANCHES[i][1], _HANCHES[i][2])),
                           np.array((c * _GENOUX[i][0], _GENOUX[i][1], _GENOUX[i][2])),
                           np.array((c * _PIEDS[c][i][0], _PIEDS[c][i][1], (0.0220, 0.0185, 0.0205)[i]))]
        for l, c in (("G", 1), ("D", -1)) for i, r in enumerate(RANGS)}
CORPS = np.array((0.0, 0.0, 0.085))            # le pivot du corps : entre les hanches du milieu, il roule autour

OS = ([("racine", None, (0, 0, 0)),
       ("corps", "racine", tuple(CORPS)),                         # le cœur de la boule de muscles
       ("corselet", "corps", (0.004, 0.000, 0.100)),             # l'attache des épaules sur les élytres
       ("tete", "corselet", (0.009, -0.078, 0.080))]             # la nuque, sous le bord des épaules
      + [("patte_%s_G" % r, "racine", _HANCHES[i]) for i, r in enumerate(RANGS)])      # les hanches (la droite en miroir)


def _pattes(points, cote):
    """Les trois pattes d'un côté, une seule pièce : chaque point suit la patte dont le fil passe le plus près.
    L'usine retourne les pièces de droite en miroir avant de les donner : on les remet à leur place."""
    q = points * ([1, 1, 1] if cote == "_G" else [-1, 1, 1])
    ecarts = []
    for r in RANGS:
        f = FILS[r + cote]
        e = np.full(len(q), 9.0)
        for a, b in zip(f[:-1], f[1:]):
            u = np.clip((q - a) @ (b - a) / ((b - a) @ (b - a)), 0.0, 1.0)
            e = np.minimum(e, np.linalg.norm(q - a - u[:, None] * (b - a), axis=1))
        ecarts.append(e)
    proche = np.argmin(ecarts, axis=0)
    return {"patte_%s%s" % (r, cote): (proche == k).astype(float) for k, r in enumerate(RANGS)}


PORTEURS = [("elytres", "corps"), ("suture", "corps"), ("col", "corps"), ("corselet", "corselet"),
            ("crane", "tete"), ("chaperon", "tete"), ("cerne", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("corne", "tete"),
            ("pattes", _pattes),
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


def campe(p, pique=0.0, monte=(0.0, 0.0, 0.0), roule=0.0, lacet=0.0, ech=(1, 1, 1), virevolte=0.0):
    """Pose le corps : « pique » > 0 baisse l'avant (degrés), « roule » > 0 le couche sur sa gauche, « lacet » > 0 le
    tourne vers sa gauche, « virevolte » aussi mais d'autant de tours qu'on veut (ajouté à part : l'angle reste continu) ;
    « monte » le déplace. Rend de quoi faire suivre une patte (voir jambe)."""
    R = tour((0, 0, 1), lacet) @ tour((0, 1, 0), roule) @ tour((1, 0, 0), pique)
    p.add("corps", rot=angles(R), pos=tuple(monte), ech=ech)
    p.add("corps", rot=(0, 0, virevolte))
    return R, np.asarray(monte, float), virevolte


def jambe(p, nom, arriere=0.0, leve=0.0, suit=None):
    """Tourne une patte sur sa hanche : « arriere » degrés vers l'arrière (autour de la verticale), « leve » degrés vers le
    haut (le pied monte en s'écartant). suit = ce que rend campe : la patte suit alors le corps (elle quitte le sol)."""
    H, F = FILS[nom][0], FILS[nom][2]
    c = 1 if nom.endswith("G") else -1
    R = tour((0, 0, 1), c * arriere) @ tour(np.cross((F - H) * [1, 1, 0], (0, 0, 1)), leve)
    pos, virevolte = np.zeros(3), 0.0
    if suit is not None:
        Rc, monte, virevolte = suit
        R = Rc @ R
        pos = tour((0, 0, 1), virevolte) @ Rc @ (H - CORPS) + CORPS + monte - H
    p.add("patte_" + nom, rot=angles(R), pos=tuple(pos))
    p.add("patte_" + nom, rot=(0, 0, virevolte))


def tete(p, hoche=0.0, tourne=0.0, penche=0.0):
    """La tête autour de ses axes à elle : hoche > 0, le nez plonge ; tourne > 0, elle regarde vers sa gauche ;
    penche > 0, elle se couche sur son épaule gauche."""
    p.add("tete", rot=angles(tour(T3[:, 2], tourne) @ tour(T3[:, 0], hoche) @ tour(T3[:, 1], penche)))


def repos(t):
    """Il souffle entre deux poussées : le dos se gonfle, il regarde par en dessous à gauche puis revient sur nous ;
    il gratte deux fois le sol de la patte arrière, comme un taureau, roule des épaules, puis s'essuie le chaperon
    d'un revers de patte avant. Il cligne lentement, l'air buté."""
    p = Pose()
    r = onde(t, 2)
    gratte = cloche(t, 0.30, 0.04) + cloche(t, 0.40, 0.04)
    epaules = cloche(t, 0.52, 0.06)
    essuie = cloche(t, 0.75, 0.08)
    campe(p, 1.5 * epaules, roule=2 * epaules * onde(t, 8), ech=(1 + 0.014 * r, 1, 1 + 0.022 * r))
    p.add("corselet", rot=(2 * epaules - 1.0 * r, 0, 3 * epaules * onde(t, 8)))
    tete(p, -4 * essuie + 4 * epaules, 14 * cloche(t, 0.15, 0.09) - 8 * essuie)
    jambe(p, "arriere_G", 22 * gratte, 14 * gratte)
    jambe(p, "avant_D", -16 * essuie + 10 * essuie * onde(t, 12), 26 * essuie)
    p.ouvert = 1 - cloche(t, 0.08, 0.03) - cloche(t, 0.60, 0.03)
    return p


def avance(t):
    """Il pousse : la tête basse, il avance à petits pas lourds sur deux trépieds à contretemps, les pattes de derrière
    poussent loin en arrière ; à chaque pas les épaules donnent un coup en avant (« han ! »), le corps roule et
    se tord d'un trépied sur l'autre."""
    p = Pose()
    s = onde(t, 1)
    han = abs(onde(t, 1))
    campe(p, 1.5 * han, (0, -0.004 * han, -0.002 * han), roule=-3.5 * s, lacet=-2.5 * s)
    for nom in FILS:
        ph = math.tau * t + (0.0 if nom in ("avant_G", "milieu_D", "arriere_G") else math.pi)
        ample = 18 if nom.startswith("arriere") else 12
        jambe(p, nom, ample * math.sin(ph), 14 * max(0.0, -math.cos(ph)))
    p.add("corselet", rot=(3 * han, 0, 3 * s))
    tete(p, 3 * han, -3 * s)
    return p


def mange(t):
    """Il plonge le chaperon dans l'herbe et pellette : trois coups de pelle, la tête qui racle et remonte, le derrière
    qui se soulève à chaque coup ; puis il relève la tête et mâche."""
    p = Pose()
    bas = 1 - cloche(t, 0.88, 0.12)
    pelle = max(0.0, onde(t, 3, 0.75)) * bas                 # 0 → 1 → 0 trois fois : le chaperon racle vers l'avant
    campe(p, 3 * bas + 2 * pelle)
    p.add("corselet", rot=(2 * bas, 0, 0))
    tete(p, 2.5 * bas - 8 * pelle + 4 * cloche(t, 0.90, 0.04) * onde(t, 12))
    p.ouvert = 1 - cloche(t, 0.93, 0.02)
    return p


def joie(t):
    """La danse du bousier : il bondit comme sur le haut de sa boule, y fait un tour complet sur lui-même pour
    s'orienter, les pattes avant levées comme des bras de lutteur ; il retombe et roule des épaules, content de lui."""
    p = Pose()
    air = math.sin(math.pi * borne((t - 0.06) / 0.56)) if 0.06 < t < 0.62 else 0.0
    tourne = K.lisse(np.array((t - 0.10) / 0.46)).item()
    fier = cloche(t, 0.78, 0.12, False)
    suit = campe(p, -6 * air, (0, 0, 0.030 * air), virevolte=360 * tourne)
    p.add("corps", rot=(0, 3 * fier * onde(t, 6), 0))         # le roulis du fier-à-bras, une fois retombé : les pattes n'en suivent rien
    for nom in FILS:
        if nom.startswith("avant"):
            jambe(p, nom, -26 * air, 40 * air, suit)
        else:
            jambe(p, nom, 8 * air, 8 * air, suit)
    p.add("corselet", rot=(-6 * air, 0, 4 * fier * onde(t, 6)))
    tete(p, -10 * air)
    return p


def dort(t):
    """Il s'est affalé : le derrière redescendu, le ventre dans l'herbe, les pattes écartées, la tête posée sur son
    chaperon ; les yeux fermés, il ronfle d'un dos qui se soulève lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    campe(p, -7, (0, 0, -0.016), ech=(1 + 0.012 * r, 1, 1 + 0.022 * r))
    p.add("corselet", rot=(5, 0, 0))
    tete(p, 3 + 1.0 * r, -4)
    for nom in FILS:
        jambe(p, nom, 6 if nom.startswith("arriere") else -4, 0.0)
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Bousier")
