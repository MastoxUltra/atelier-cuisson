"""Le canard en peluche, deuxième dessin : un colvert adulte, effronté, saisi en plein dandinement.
Un corps long et bas, gris perle au dessous crème ; la poitrine marron prune, bombée en avant ; un vrai cou en S, bleu
canard comme la tête, cerclé d'un collier blanc ; un long bec moutarde en spatule, entrouvert ; le croupion noir qui
remonte en pointe avec ses deux plumes en crosse ; sur chaque aile ardoise, un miroir bleu vif entre deux filets blancs.
La tête penchée et tournée vers nous, un sourcil levé, l'autre froncé, une grande palme orange en l'air.

    python canard.py           fabrique la fiche art/apercus/animaux/canard.png
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

PETROLE = M.hexa("#157e90")                   # la tête et le haut du cou : un bleu canard, bleu-vert profond (pas un vert d'herbe)
PRUNE = M.hexa("#9c505c")                     # la poitrine : un marron prune (le poil le fonce beaucoup)
PERLE = M.hexa("#cdd0d9")                     # le corps
ARDOISE = M.hexa("#8a91a2")                   # les ailes, un gris plus soutenu que le corps
NUIT = M.hexa("#1c1d23")                      # le croupion, ses crosses et le bout des rémiges
BLEU = M.hexa("#2a6be0")                      # le miroir de l'aile
MOUTARDE = M.hexa("#ecb42c")                  # le bec
ORANGE = M.hexa("#ff6d1f")                    # les pattes et les palmes

CORPS = Vector((0.0, 0.02, 0.212))
DANDINE = A.repere(CORPS, (-4, -8, -6))       # le corps : presque à l'horizontale, il roule sur sa patte droite et pivote avec le pas
C3 = DANDINE.to_3x3()
LONG = 0.56                                   # le corps, de la pointe du croupion au bout de la poitrine
CRANE = DANDINE @ A.repere((0.0, -0.198, 0.298), (-4, 12, 21))     # la tête : penchée sur l'épaule gauche, tournée vers nous
TETE = CRANE @ Vector((0, 0, 0))

# le cou : un S dessiné dans le plan du corps, de la poitrine (où il est enfoui) jusque dans la tête
FIL = A.courbe([tuple(DANDINE @ Vector(q)) for q in ((0, -0.150, 0.020), (0, -0.192, 0.100), (0, -0.216, 0.170), (0, -0.204, 0.235), (0, -0.196, 0.285))], 8)
FAIT = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(FIL, axis=0), axis=1))])
SENS = np.gradient(FIL, FAIT, axis=0)
HAUT = float(FAIT[-1])
FLANC = np.array(C3 @ Vector((1, 0, 0)))


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du jardin."""
    return CRANE.to_3x3() @ Vector((x, y, z))


def lorgne(azimut, hauteur, cote):
    """Une direction autour de la tête : tant de degrés depuis le bec vers le côté, tant de degrés au-dessus de l'horizon."""
    a, h = math.radians(azimut), math.radians(hauteur)
    return vers(cote * math.sin(a) * math.cos(h), -math.cos(a) * math.cos(h), math.sin(h))


def serre(profil, limites, e=0.0015):
    """Ajoute à un profil de tour deux tours serrés de part et d'autre de chaque hauteur de « limites » :
    une couleur peinte par K.bandes y garde un bord net."""
    p = np.asarray(profil, float)
    plus = [(float(np.interp(h + d, p[:, 1], p[:, 0])), h + d) for h in limites for d in (-e, e)]
    tout = sorted([tuple(q) for q in p] + plus, key=lambda q: q[1])
    return [q for i, q in enumerate(tout) if i == 0 or q[1] - tout[i - 1][1] > 1e-6]


def couche(v):
    """Couche une pièce tournée toute droite (son axe Z) le long du fil du cou : son +Y devient la nuque."""
    s = np.clip(v[:, 2], 0.0, HAUT)
    centre = np.stack([np.interp(s, FAIT, FIL[:, k]) for k in range(3)], axis=-1)
    avant = np.stack([np.interp(s, FAIT, SENS[:, k]) for k in range(3)], axis=-1)
    avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
    return centre + avant * (v[:, 2] - s)[:, None] + v[:, 0:1] * FLANC + v[:, 1:2] * np.cross(avant, FLANC)


def plume(long, large, bandes, epais=0.18):
    """Une plume plate debout sur son pied (son axe Z), en fer de lance : étroite au pied, large passé le milieu,
    le bout bien rond. « bandes » la peint : (jusqu'où, de 0 à 1 ; la couleur). Deux tours serrés à chaque limite :
    le bord des couleurs reste net."""
    cotes = sorted(set(np.linspace(0.0, 1.0, 31).tolist() + [0.975, 0.99, 0.997] + [f + e for f, _c in bandes[:-1] for e in (-0.004, 0.004)]))

    def demi(t):
        return 0.0 if t <= 0.0 or t >= 1.0 else 1.93 * t ** 0.6 * (1 - t) ** 0.38
    m = A.tour([(large * demi(t), long * t) for t in cotes], 20).etire(1.0, epais, 1.0)
    return K.bandes(m, [(long * f, c) for f, c in bandes])


def plaque(m, pied, pointe, plat):
    """Couche une plume (son axe Z) : le pied posé en « pied », la pointe vers « pointe », le plat tourné vers « plat »."""
    z = Vector(pointe).normalized()
    y = (Vector(plat) - z * Vector(plat).dot(z)).normalized()
    x = y.cross(z)
    m.v = np.outer(m.v[:, 0], np.array(x)) + np.outer(m.v[:, 1], np.array(y)) + np.outer(m.v[:, 2], np.array(z)) + np.array(pied)
    return m


def palme():
    """Une grande palme à plat, le talon à l'origine, les trois doigts vers -Y : étroite au talon, large et festonnée devant."""
    def forme(v):
        s = v.copy()
        devant = K.lisse((0.3 - v[:, 1]) / 1.3)
        feston = 1 + 0.14 * np.cos(7.2 * np.arctan2(v[:, 0], -v[:, 1])) * devant
        s[:, 0] *= (0.40 + 0.82 * devant) * feston
        s[:, 1] *= feston
        return s
    return A.boule(1.0, 48, 12).sculpte(forme).etire(0.060, 0.068, 0.013).pose((0, -0.048, 0))


def construire():
    a = K.Animal("canard")
    a.taille = 0.55
    a.tete = CRANE @ Vector((0.02, -0.095, 0.0))

    # ----- le corps : une longue barque tournée du croupion à la poitrine, puis couchée (dans la pièce : X la gauche,
    #       Y le dos, Z l'avant). Elle est peinte par tranches nettes : le croupion noir, le corps perle, la poitrine prune ;
    #       et sous le corps seulement, bien en arrière de la poitrine, le dessous crème. -----
    profil = A.profil([(0, 0), (0.022, 0.04 * LONG), (0.056, 0.14 * LONG), (0.096, 0.30 * LONG), (0.120, 0.50 * LONG), (0.126, 0.68 * LONG),
                       (0.116, 0.84 * LONG), (0.080, 0.95 * LONG), (0, LONG)], 7)
    corps = A.tour(serre(profil, [0.13 * LONG, 0.72 * LONG]), 56)
    ou = corps.v[:, 2] / LONG
    dessous = np.abs(np.arctan2(corps.v[:, 0], -corps.v[:, 1])) < math.radians(66)
    corps.teinte = np.where((ou < 0.13)[:, None], NUIT, np.where((ou > 0.72)[:, None], PRUNE, np.where(dessous[:, None], K.CREME, PERLE)))

    def barque(v):
        s = v.copy()
        u = v[:, 2] / LONG
        s[:, 0] *= 1.10
        s[:, 1] += 0.150 * K.lisse((0.36 - u) / 0.36) ** 1.6      # le croupion remonte en pointe
        s[:, 1] -= 0.016 * K.lisse((u - 0.58) / 0.25)             # la poitrine est profonde
        return s
    G.sillons(corps, [14], 0.004, 1.1)                  # la couture du dos creuse un peu le tissu
    a.piece("corps", corps.sculpte(barque), None, mat=DANDINE @ A.repere((0, 0.30, 0), (90, 0, 0)))
    a.couture("dos", "corps", 14, 0.20, 0.66, fil=ARDOISE, large=0.007, haut=0.004, pas=0.016)

    # ----- le croupion : deux plumes de feutrine noire en crosse, qui montent et s'enroulent vers l'avant -----
    crosse = ((0, 0.0, 0.0), (0, 0.030, 0.040), (0, 0.035, 0.085), (0, 0.010, 0.115), (0, -0.025, 0.108), (0, -0.038, 0.080), (0, -0.026, 0.060))
    crosses = None
    for pos, rot, grande in (((0.008, 0.262, 0.128), (0, 6, 8), 1.0), ((-0.014, 0.270, 0.122), (14, -16, -22), 0.72)):
        pousse = DANDINE @ A.repere(pos, rot, (grande, grande, grande))
        m = A.tube(A.courbe([tuple(pousse @ Vector(q)) for q in crosse], 7), lambda t, g=grande: (0.017 - 0.009 * t) * g, 14)
        crosses = m if crosses is None else crosses + m
    a.piece("crosses", crosses, NUIT, poil=False)

    # ----- le cou : une chaussette couchée le long du S ; prune à la base, un collier blanc, puis bleu canard jusqu'à la tête -----
    pc = A.profil([(0, 0), (0.086, 0.015), (0.078, 0.070), (0.060, 0.120), (0.047, 0.165), (0.042, 0.210), (0.042, HAUT - 0.02), (0, HAUT)], 6)
    cou = K.bandes(A.tour(serre(pc, [0.138, 0.164]), 32), [(0.138, PRUNE), (0.164, K.BLANC), (9, PETROLE)])       # il s'évase en entrant dans la poitrine
    a.piece("cou", cou.sculpte(couche), None)

    # ----- la tête : petite, allongée vers le bec, les joues un peu pleines -----
    def crane(v):
        v = K.bosse(v, (0, -0.90, -0.25), 0.14, 0.30)
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.85, -0.20, -0.35), 0.08, 0.25)
        return v * [0.066, 0.078, 0.064]
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(crane), PETROLE, mat=CRANE)

    # ----- les yeux : une pastille noire et son reflet sur un rond de feutrine blanche (sans lui, le noir se perd dans le bleu) ;
    #       au-dessus, deux sourcils de fil crème : levé à gauche, froncé à droite -----
    for nom, cote in (("G", 1), ("D", -1)):
        a.rustine("cerne_" + nom, "tete", TETE, vers(0.80 * cote, -0.48, 0.30), 0.40, K.BLANC, 0.003, 0)
        p, n = a.surface("tete", TETE, vers(0.78 * cote, -0.54, 0.27))     # la pupille un peu en avant et en bas dans son rond : il nous toise
        a.oeil("oeil_" + nom, p + n * 0.0045, n, 0.019)
    leve = a.trace("tete", TETE, [lorgne(28, 46, 1), lorgne(57, 60, 1), lorgne(88, 50, 1)], 0.005)
    a.broderie("sourcil_g", A.courbe(leve, 5), 0.0048, K.CREME)
    fronce = a.trace("tete", TETE, [lorgne(24, 28, -1), lorgne(55, 49, -1), lorgne(86, 52, -1)], 0.005)
    a.broderie("sourcil_d", A.courbe(fronce, 5), 0.0048, K.CREME)

    # ----- le bec : une longue spatule de feutrine moutarde, étroite à la racine, large et retroussée au bout ; le dessous bâille -----
    def spatule(v):
        s = K.emousse(v, 0.8)
        devant = K.lisse((0.35 - v[:, 1]) / 1.2)
        s[:, 0] *= 0.68 + 0.36 * devant
        s = s * [0.043, 0.086, 0.014]
        s[:, 2] += 0.016 * np.clip(-v[:, 1], 0, 1) ** 2.2
        return s
    a.piece("bec", A.boule(1.0, 40, 20).sculpte(spatule), MOUTARDE, mat=CRANE @ A.repere((0, -0.142, -0.018), (5, 0, 0)), poil=False)

    def menton(v):
        s = K.emousse(v, 0.8)
        s[:, 0] *= 0.72 + 0.26 * K.lisse((0.35 - v[:, 1]) / 1.2)
        return s * [0.035, 0.066, 0.010]
    a.piece("bec_bas", A.boule(1.0, 32, 16).sculpte(menton), MOUTARDE, mat=CRANE @ A.repere((0, -0.122, -0.040), (16, 0, 0)), poil=False)

    # ----- les ailes : une épaule de peluche ardoise, puis trois rémiges de feutrine couchées vers l'arrière, peintes aux mêmes
    #       hauteurs : filet blanc, miroir bleu, filet blanc, bout noir. Elles se décollent un peu, la gauche plus que la droite. -----
    def galet(v):
        s = K.emousse(v, 0.85)
        pointe = K.lisse((v[:, 1] + 0.2) / 1.2)
        s[:, 2] = s[:, 2] * (1 - 0.35 * pointe) + 0.12 * pointe
        return s
    for nom, cote, rot in (("g", 1, (7, -4, -10)), ("d", -1, (5, 6, 5))):
        AILE = DANDINE @ A.repere((0.128 * cote, 0.000, 0.030), rot)
        a.piece("aile_" + nom, A.boule(1.0, 40, 20).sculpte(galet).etire(0.026, 0.105, 0.074), ARDOISE, mat=AILE)
        remiges = None
        for z, degres, long in ((-0.036, -3, 0.215), (-0.006, 5, 0.205), (0.024, 13, 0.180)):
            t = math.radians(degres)
            p = plume(long, 0.035, [(0.44, ARDOISE), (0.50, K.BLANC), (0.70, BLEU), (0.76, K.BLANC), (1.0, NUIT)])
            p = plaque(p, (0.004 * cote, 0.010, z), (0, math.cos(t), math.sin(t)), (1, 0, 0))
            remiges = p if remiges is None else remiges + p
        a.piece("remiges_" + nom, remiges, None, mat=AILE, poil=False)

    # ----- les pattes en feutrine orange, courtes, aux grandes palmes : la droite porte tout le poids, tournée en canard ;
    #       la gauche est levée en plein pas, la palme en l'air -----
    appui = A.tube([(0, 0.012, 0.170), (0, 0.0, 0.015)], 0.020, 14) + palme().pose((0, 0, 0.013))
    a.piece("patte_d", appui, ORANGE, pos=(-0.050, 0.030, 0.0), rot=(0, 0, -10), poil=False)
    levee = A.tube(A.courbe([(0.066, 0.000, 0.155), (0.086, -0.085, 0.138), (0.094, -0.125, 0.130)], 5), 0.020, 14)
    a.piece("patte_g", levee + palme().pose((0.094, -0.125, 0.128), (18, 12, 22)), ORANGE, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py canard)

from poses import Pose, borne, cloche, onde

# Le modèle est saisi en plein pas : le corps roulé de 8° sur sa patte droite, la palme gauche levée, la tête penchée et
# tournée. Chaque côté a donc son os à lui, à sa vraie place (aile_g, aile_d, patte_g, patte_d : pas de miroir), et les
# pattes pendent à la racine, pas au corps : une palme posée ne bouge pas quand le corps roule au-dessus d'elle.
OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.035, 0.150)),            # le bassin : il se dandine autour
    ("cou", "corps", (-0.022, -0.132, 0.252)),           # le pied du cou, enfoui dans la poitrine : en plongeant, le cou sort par-devant
    ("tete", "cou", (-0.060, -0.150, 0.476)),            # la nuque
    ("bec_bas", "tete", (-0.046, -0.224, 0.504)),        # la charnière du bec
    ("aile_g", "corps", (0.112, -0.058, 0.284)),         # l'épaule gauche
    ("aile_d", "corps", (-0.141, -0.032, 0.248)),        # l'épaule droite
    ("crosses", "corps", (0.014, 0.280, 0.305)),         # le bout du croupion
    ("patte_g", "racine", (0.066, 0.000, 0.155)),        # la hanche de la patte levée
    ("patte_d", "racine", (-0.050, 0.040, 0.170)),       # la hanche de la patte d'appui
]
PORTEURS = [("corps", "corps"), ("dos", "corps"), ("crosses", "crosses"), ("cou", "cou"),
            ("tete", "tete"), ("cerne", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("bec_bas", "bec_bas"), ("bec", "tete"),
            ("aile_g", "aile_g"), ("remiges_g", "aile_g"), ("aile_d", "aile_d"), ("remiges_d", "aile_d"),
            ("patte_g", "patte_g"), ("patte_d", "patte_d"),
            # les yeux sont posés un par un : l'usine appelle alors leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _campe(p):
    """La pose d'attente, d'où partent repos, mange et joie : la palme gauche redescend se poser sur la pointe
    (il se tient hanché sur sa patte droite) et le bec se referme à demi."""
    p.add("patte_g", rot=(22, 0, 0))
    p.add("bec_bas", rot=(-9, 0, 0))
    return p


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _ailes(p, leve):
    """Les deux ailes se lèvent de « leve » degrés, chacune autour de son épaule : le bout monte et s'écarte du corps
    (l'aile part de l'épaule vers l'arrière ; la tourner seulement autour de l'axe du corps ne la ferait presque pas bouger)."""
    p.add("aile_g", rot=(0.55 * leve, -0.4 * leve, -0.6 * leve))
    p.add("aile_d", rot=(0.55 * leve, 0.4 * leve, 0.6 * leve))


def repos(t):
    """Hanché sur sa patte droite, il respire, toise à droite puis revient vers nous, tape deux fois de la palme
    (il s'impatiente), lâche un coin-coin, frétille des crosses, cligne des yeux."""
    p = _campe(Pose())
    r = onde(t, 2)
    droite = cloche(t, 0.26, 0.16)
    tape = cloche(t, 0.50, 0.035) + cloche(t, 0.58, 0.035)
    coin = cloche(t, 0.74, 0.05)
    p.add("corps", ech=(1 + 0.012 * r, 1 + 0.008 * r, 1 + 0.020 * r))
    p.add("cou", rot=(-3 * coin, 0, -10 * droite))
    p.add("tete", rot=(2 * r - 6 * coin, -8 * droite, -30 * droite))
    p.add("bec_bas", rot=(17 * coin, 0, 0))
    p.add("patte_g", rot=(-15 * tape, 0, 0))
    _ailes(p, 6 * cloche(t, 0.40, 0.06))
    p.add("crosses", rot=(0, 0, 16 * cloche(t, 0.88, 0.07) * onde(t, 10)))
    p.ouvert = 1 - cloche(t, 0.13, 0.02) - cloche(t, 0.62, 0.02)
    return p


def avance(t):
    """Il se dandine. À t = 0 c'est la pose du modèle : le corps roulé à droite, la palme gauche levée devant ; à mi-cycle
    c'est l'inverse : la gauche a pris appui, le corps a roulé à gauche, la droite se lève et passe devant.
    La tête penche à contre-sens et garde son cap ; elle avance et recule à chaque pas. Il y a toujours une palme au sol,
    et la palme posée glisse vers l'arrière pendant qu'elle porte : il avance."""
    p = Pose()
    s = math.sin(math.tau * t)
    g = (1 - math.cos(math.tau * t)) / 2                  # le roulis : 0 en appui à droite, 1 en appui à gauche
    pose_g = _plateau(t, 0.50, 0.20, 0.10)                # la palme gauche est posée (sur la pointe) de 0,3 à 0,7
    leve_d = _plateau(t, 0.50, 0.10, 0.10)                # la droite ne quitte le sol qu'une fois la gauche posée
    p.add("corps", rot=(0, 16 * g, 12 * g), pos=(0.016 * g, 0, 0.010 * abs(s)))
    p.add("patte_g", rot=(22 * pose_g, 0, 0), pos=(0, 0.045 * pose_g - 0.030 * s, 0))
    p.add("patte_d", rot=(-26 * leve_d, 0, 0), pos=(0, 0.030 * s, 0.030 * leve_d))
    p.add("cou", rot=(0, -10 * g, -5 * g))
    p.add("tete", rot=(0, -12 * g, -7 * g), pos=(0, -0.010 * math.cos(2 * math.tau * t), 0))
    p.add("bec_bas", rot=(-6, 0, 0))
    _ailes(p, 5 + 5 * abs(s))
    p.add("crosses", rot=(0, 0, 10 * s))
    return p


def mange(t):
    """Le croupion en l'air, le cou plongé : quatre coups de bec au sol (le bec s'ouvre entre deux coups et claque
    en touchant), puis il relève la tête pour avaler."""
    p = _campe(Pose())
    leve = cloche(t, 0.85, 0.13)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add("corps", rot=(13 * bas, 0, 0))
    p.add("cou", rot=(65 * bas + 5 * coups, 0, -8 * bas))
    p.add("tete", rot=(30 * bas + 8 * coups - 8 * leve, -8 * bas, -10 * bas))
    p.add("bec_bas", rot=(16 * max(0.0, -onde(t, 4)) * bas + 10 * leve * abs(onde(t, 6)), 0, 0))
    _ailes(p, 5 * bas)
    p.add("crosses", rot=(0, 0, 10 * onde(t, 4) * bas))
    p.ouvert = 1 - cloche(t, 0.90, 0.03)
    return p


def joie(t):
    """Sa fête à lui : il se hausse, sautille, bat des ailes à grands coups, le bec grand ouvert vers le ciel (il cancane),
    et les deux crosses du croupion frétillent. Puis il retombe dans sa pose d'attente."""
    p = _campe(Pose())
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    bat = onde(t, 7) * env
    saut = abs(onde(t, 3.5)) * env
    p.add("corps", pos=(0, 0, 0.050 * saut + 0.012 * env), rot=(-11 * env, 5 * onde(t, 3.5) * env, 0))
    p.add("patte_g", pos=(0, 0, 0.050 * saut), rot=(-14 * saut, 0, 0))
    p.add("patte_d", pos=(0, 0, 0.050 * saut))
    p.add("cou", rot=(-12 * env, 0, -6 * env))
    p.add("tete", rot=(-16 * env, 6 * onde(t, 3.5) * env, -8 * env))
    p.add("bec_bas", rot=(26 * env * (0.55 + 0.45 * abs(onde(t, 7))), 0, 0))
    _ailes(p, 48 * env + 30 * bat)
    p.add("crosses", rot=(8 * env, 0, 24 * onde(t, 9) * env))
    return p


def dort(t):
    """Posé sur le ventre, les palmes dessous, le cou retourné et la tête couchée sur le dos, le bec entre les ailes,
    les yeux fermés ; il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.076), rot=(4, 8, 0), ech=(1.03 + 0.012 * r, 1.0, 0.97 + 0.025 * r))
    p.add("patte_g", rot=(22, 0, 0), pos=(-0.040, 0.085, 0.0))
    p.add("cou", rot=(60, 0, 170))
    p.add("tete", rot=(-48, 0, -12))
    p.add("bec_bas", rot=(-14, 0, 0))
    _ailes(p, 2 + 1.5 * r)
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Canard")
