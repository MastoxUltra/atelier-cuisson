"""Le perce-oreille en peluche : un petit dur qui bluffe. Un corps bordeaux en trois pièces, la tête, le corselet en
écusson et deux élytres courts en feutrine lie-de-vin (l'un rapiécé de vieux rose au point de feston) ; derrière, le
long abdomen bagué, fait d'anneaux qui se chevauchent, relevé en scorpion par-dessus le dos ; et au bout, son arme et
son accent, deux pinces ambre grandes ouvertes, pointées vers nous. Il se campe : les six pattes écartées, l'avant
dressé, la tête tournée vers celui qui approche, le sourcil froncé, une antenne pointée en avant, l'autre rejetée en
arrière. Il ne ferait pas de mal à une mouche, mais il ne faut pas le lui dire.

    python perce_oreille.py        fabrique la fiche art/apercus/animaux/perce_oreille.png
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

BORDEAUX = M.hexa("#a33246")                  # l'abdomen et la tête, en velours (le poil le fonce vers le bordeaux)
LIE = M.hexa("#5c1a28")                       # les élytres, en feutrine, et le bord des anneaux
VIEUX_ROSE = M.hexa("#c56b78")                # les pattes, les antennes, le rapiéçage
AMBRE = M.hexa("#f2a53a")                     # l'accent : les pinces, le fil des coutures
TOURNE = 0                                    # inutile ici : il se lit bien de trois quarts
LEVE = 0.010                                  # tout le corps monte d'un cran sur ses pattes : l'herbe ne l'avale pas
PORT = A.repere((0.0, -0.104, 0.056 + LEVE), (-14, 0, 22))      # la tête, relevée, tournée vers nous
CENTRE_TETE = PORT @ Vector((0, 0, 0))
# L'abdomen : il part sous les élytres, file en arrière, puis se relève en scorpion par-dessus le dos.
QUEUE = K.Fil([(0, 0.000, 0.040 + LEVE), (0, 0.052, 0.040 + LEVE), (0, 0.096, 0.056 + LEVE), (0, 0.122, 0.094 + LEVE),
               (0, 0.120, 0.134 + LEVE), (0, 0.100, 0.160 + LEVE)], flanc=(1, 0, 0), pas=16)


# les six pattes : où part la hanche (y0), où se pose le pied (y1), et leur écart
PATTES = ((-0.066, -0.100, 0.062), (-0.040, -0.036, 0.070), (-0.014, 0.030, 0.064))


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête, rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def construire():
    a = K.Animal("perce_oreille")
    a.taille = 0.30
    a.tete = PORT @ Vector((0, -0.020, 0.004))

    # ----- l'abdomen : huit anneaux de velours bordeaux qui se chevauchent, chacun bordé de lie-de-vin, de plus en plus
    #       fins vers le bout -----
    long = QUEUE.long
    def anneaux(z):
        f = np.clip(z / long, 0.0, 1.0)
        rayon = 0.027 - 0.010 * f
        bourrelet = 1 + 0.10 * (1 - ((f * 8) % 1.0)) ** 2           # chaque anneau gonfle à sa racine
        return rayon * bourrelet
    z = np.linspace(0.0, long, 90)
    profil = [(0, 0)] + [(float(anneaux(q)), float(q)) for q in z[1:-1]] + [(0, long)]
    ventre = A.tour(profil, 40)
    paliers = []
    for k in range(8):
        fin = long * (k + 1) / 8
        paliers += [(fin - long / 8 * 0.22, BORDEAUX), (fin, LIE)]
    K.bandes(ventre, paliers + [(9, BORDEAUX)])
    G.sillons(ventre, [10], 0.0015, 1.0)
    a.piece("abdomen", ventre.sculpte(lambda v: v * [1.10, 0.86, 1.0]).sculpte(QUEUE.couche), None)
    a.couture("dos", "abdomen", 10, 0.06, 0.88, "droit", fil=AMBRE, large=0.006, haut=0.0015, pas=0.010)

    # ----- les pinces : deux cornes ambre, épaisses à la racine, grandes ouvertes, qui se referment en crochet -----
    bout, sens, nuque = QUEUE.cadre(long * 0.97)
    bout, sens, nuque = Vector(bout), Vector(sens), Vector(nuque)
    for nom, c in (("G", 1), ("D", -1)):
        cote = Vector((c, 0, 0))
        chemin = [bout - sens * 0.006 + cote * 0.007, bout + sens * 0.020 + cote * 0.024, bout + sens * 0.046 + cote * 0.033 + nuque * 0.004,
                  bout + sens * 0.068 + cote * 0.026 + nuque * 0.006, bout + sens * 0.080 + cote * 0.012 + nuque * 0.004]
        a.piece("pince_" + nom, A.tube(A.courbe(chemin, 8), lambda t: 0.0075 * (1 - 0.72 * t) + 0.0012, 14), AMBRE, poil=False)

    # ----- les élytres : un court écusson de feutrine lie-de-vin, fendu au milieu par une couture ambre ; un rapiéçage
    #       vieux rose sur l'élytre gauche -----
    def ecusson(v):
        s = K.emousse(v, 0.82) * [0.040, 0.037, 0.018]
        s[:, 0] *= 1 + 0.10 * K.lisse((v[:, 1] + 0.3) / 1.3)       # un peu plus large derrière
        return s
    elytres = A.boule(1.0, 56, 28).sculpte(ecusson)
    G.sillons(elytres, [14, 42], 0.0025, 1.2)
    centre_e = Vector((0, -0.010, 0.058 + LEVE))
    a.piece("elytres", elytres, LIE, mat=A.repere(centre_e, (-6, 0, 0)), poil=False)
    a.couture("suture", "elytres", 14, 0.52, 0.99, "droit", fil=AMBRE, large=0.007, haut=0.0012, pas=0.010)
    a.couture("suture2", "elytres", 42, 0.62, 0.99, "droit", fil=AMBRE, large=0.007, haut=0.0012, pas=0.010)
    a.rustine("piece", "elytres", centre_e, (0.62, -0.20, 0.76), 0.62, VIEUX_ROSE, 0.002, 16, fil=AMBRE)

    # ----- le corselet : un écusson de velours plus petit, entre la tête et les élytres -----
    corselet = A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.032, 0.028, 0.020)
    a.piece("corselet", corselet, BORDEAUX, mat=A.repere((0, -0.062, 0.056 + LEVE), (-10, 0, 8)))

    # ----- la tête : un coin large et plat ; deux petits yeux sous un sourcil froncé, une bouche en accent -----
    def caboche(v):
        v = K.bosse(v, (0, -1, -0.3), 0.12, 0.30)                       # les mandibules
        return K.emousse(v, 0.88) * [0.031, 0.033, 0.022]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(caboche), BORDEAUX, mat=PORT)
    a.couture("crane", "tete", 12, 0.55, 0.97, "droit", fil=AMBRE, large=0.006, haut=0.0012, pas=0.009)
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", CENTRE_TETE, vers(0.70 * cote, -0.55, 0.42))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0085)
        sourcil = a.trace("tete", CENTRE_TETE, [vers(x * cote, -0.62, h) for x, h in ((0.92, 0.62), (0.62, 0.72), (0.30, 0.60))], 0.002)
        a.broderie("sourcil_" + nom, A.courbe(sourcil, 4), 0.0016, LIE)
    bouche = a.trace("tete", CENTRE_TETE, [vers(x, -0.96, h) for x, h in ((0.30, -0.18), (0.08, -0.26), (-0.16, -0.22))], 0.002)
    a.broderie("bouche", A.courbe(bouche, 4), 0.0015, LIE)

    # ----- les antennes : longues et fines, l'une pointée en avant, l'autre rejetée en arrière -----
    for nom, cote, chemin in (("G", 1, ((0.004, -0.004, 0.003), (0.020, -0.030, 0.020), (0.030, -0.060, 0.030), (0.036, -0.086, 0.024))),
                              ("D", -1, ((-0.004, -0.004, 0.003), (-0.024, -0.014, 0.030), (-0.040, 0.004, 0.056), (-0.046, 0.030, 0.070)))):
        p, n = a.surface("tete", CENTRE_TETE, vers(0.62 * cote, -0.50, 0.60))
        fil = A.courbe([p - n * 0.003] + [p + vers(*q) for q in chemin], 6)
        a.piece("antenne_" + nom, K.tube_peint(fil, lambda t: 0.0030 - 0.0012 * t, [(0.82, VIEUX_ROSE), (9, LIE)]), None, poil=False)

    # ----- les six pattes : courtes, écartées, campées ; un genou relevé, le pied à plat. Une pièce par patte (pour le
    #       jeu : chacune marche à son tour) -----
    for nom, cote in (("G", 1), ("D", -1)):
        for rang, (y0, y1, ecart) in zip(("avant", "milieu", "arriere"), PATTES):
            hanche = Vector((0.018 * cote, y0, 0.046 + LEVE))
            genou = Vector((ecart * 0.70 * cote, (y0 + y1) * 0.5, 0.050 + LEVE))
            pied = Vector((ecart * cote, y1, 0.0040))
            une = A.tube(A.conges([hanche, genou, pied, pied + Vector((0.004 * cote, (y1 - y0) * 0.15, 0))], 0.006, 5), lambda t: 0.0058 * (1 - 0.25 * t), 12)
            a.piece("patte_" + rang + "_" + nom, une, VIEUX_ROSE, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py perce_oreille). Les mesures sont celles du modèle, avant a.taille.
# Les six pattes pendent à la racine, pas au corps : un pied posé ne bouge pas quand le corps se cabre au-dessus de
# lui. L'abdomen est une pièce souple que trois os se passent le long de son fil ; les pinces ont chacune le leur.
# La tête est tournée de 22° : ses antennes ne sont pas en miroir, chacune a son os à elle (antenne_g, antenne_d).

from poses import Pose, borne, cloche, onde

_JALONS = (("abdomen", 0.0), ("abdomen2", 0.45), ("abdomen3", 0.75))      # en fraction du fil de l'abdomen
_BOUT, _SENS, _NUQUE = (np.asarray(x, float) for x in QUEUE.cadre(QUEUE.long * 0.97))     # le bout, d'où partent les pinces


def _au_fil(f):
    return tuple(round(float(x), 4) for x in QUEUE.cadre(f * QUEUE.long)[0])


OS = ([("racine", None, (0, 0, 0)),
       ("corps", "racine", (0.0, -0.030, 0.062)),            # sous les élytres : il se cabre et se couche autour
       ("tete", "corps", (0.003, -0.084, 0.066)),            # la nuque, sous le corselet
       ("antenne_g", "tete", (0.0184, -0.1067, 0.083)),      # la racine de chaque antenne, sur le front
       ("antenne_d", "tete", (-0.0114, -0.1187, 0.083))]
      + [(o, parent, _au_fil(f)) for (o, f), parent in zip(_JALONS, ("corps", "abdomen", "abdomen2"))]
      + [("pince_G", "abdomen3", (0.007, 0.1087, 0.1609))]  # la racine de la pince gauche (la droite est son miroir)
      + [("patte_%s_G" % rang, "racine", (0.018, y0, 0.046 + LEVE)) for rang, (y0, _y1, _e) in zip(("avant", "milieu", "arriere"), PATTES)])


def _abscisse(points, chemin):
    """Pour chaque point : sa place le long d'un chemin (en mètres), au pied de la perpendiculaire sur le tronçon le plus proche."""
    c = np.asarray(chemin, float)
    a, ab = c[:-1], np.diff(c, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    ap = points[:, None, :] - a[None, :, :]
    u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
    j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
    fait = np.concatenate([[0.0], np.cumsum(np.sqrt(l2))])
    return fait[j] + u[np.arange(len(points)), j] * np.sqrt(l2[j])


def _abdomen(points, cote):
    """Les anneaux : chaque os porte le tronçon qui suit son pivot, et cède au suivant en douceur sur un centimètre et demi."""
    s = _abscisse(points, QUEUE.p)
    montees = [np.ones_like(s)] + [K.lisse((s - f * QUEUE.long + 0.015) / 0.030) for _o, f in _JALONS[1:]] + [np.zeros_like(s)]
    return {o: montees[i] - montees[i + 1] for i, (o, _f) in enumerate(_JALONS)}


def _antenne(points, cote):
    return {"antenne" + cote.lower(): np.ones(len(points))}


PORTEURS = [("abdomen", _abdomen, "abdomen"), ("dos", _abdomen, "abdomen"), ("pince", "pince", True),
            ("elytres", "corps"), ("suture", "corps"), ("piece", "corps"), ("corselet", "corps"),
            ("tete", "tete"), ("crane", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("bouche", "tete"),
            ("antenne", _antenne), ("patte_avant", "patte_avant", True), ("patte_milieu", "patte_milieu", True),
            ("patte_arriere", "patte_arriere", True),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _tour(axe, degres):
    """La rotation de « degres » autour d'un axe, en matrice 3 × 3."""
    x, y, z = np.asarray(axe, float) / np.linalg.norm(axe)
    a = math.radians(degres)
    c, s, u = math.cos(a), math.sin(a), 1 - math.cos(a)
    return np.array([[c + x * x * u, x * y * u - z * s, x * z * u + y * s],
                     [y * x * u + z * s, c + y * y * u, y * z * u - x * s],
                     [z * x * u - y * s, z * y * u + x * s, c + z * z * u]])


def _angles(R):
    """Les angles qu'attend Pose (degrés, autour des axes du monde : X, puis Y, puis Z) pour la rotation R."""
    return (math.degrees(math.atan2(R[2, 1], R[2, 2])), math.degrees(math.asin(-max(-1.0, min(1.0, R[2, 0])))),
            math.degrees(math.atan2(R[1, 0], R[0, 0])))


def _pinces(p, ouvre):
    """Les pinces s'écartent (ouvre > 0, en degrés) ou se referment l'une sur l'autre (ouvre < 0), dans leur plan."""
    p.paire("pince", rot=_angles(_tour(_NUQUE, ouvre)))


def _pas(p, rang, cote, phase, force=1.0):
    """Une patte qui marche : levée et portée en avant pendant la première moitié de son tour, puis posée, elle
    repousse le sol vers l'arrière (rz > 0 : le pied part en arrière)."""
    phi = math.tau * phase
    leve, recule = 16 * force * max(0.0, math.sin(phi)), 14 * force * math.cos(phi)
    if cote == "_G":
        p.add("patte_" + rang + "_G", rot=(0, -leve, recule))
    else:
        p.add("patte_" + rang + "_D", rot=(0, leve, -recule))


def repos(t):
    """Il monte la garde, campé : il respire, l'abdomen se balance au-dessus du dos ; deux fois il fait claquer ses
    pinces en avançant la queue d'un coup sec (il bluffe), puis détourne la tête comme si de rien n'était ; ses
    antennes tâtent l'air chacune à son rythme ; il cligne."""
    p = Pose()
    r = onde(t, 2)
    p.add("abdomen", ech=(1 + 0.03 * r, 1, 1 + 0.03 * r))
    p.add("abdomen2", rot=(0, 0, 6 * onde(t, 1)))
    menace = cloche(t, 0.38, 0.10)
    clac = cloche(t, 0.34, 0.03) + cloche(t, 0.43, 0.03)
    p.add("abdomen3", rot=(14 * menace, 0, 0))
    _pinces(p, 12 * menace - 20 * clac)
    p.add("corps", rot=(-4 * menace, 0, 0))
    p.add("tete", rot=(-6 * menace, 0, -24 * cloche(t, 0.72, 0.10)))
    p.add("antenne_g", rot=(10 * onde(t, 3), 0, 6 * onde(t, 2)))
    p.add("antenne_d", rot=(-8 * onde(t, 2, 0.3), 0, 10 * onde(t, 3, 0.2)))
    p.ouvert = borne(1 - cloche(t, 0.15, 0.02) - cloche(t, 0.60, 0.02))
    return p


def avance(t):
    """Il trotte en tripode, à petits pas pressés : trois pattes en l'air (l'avant et l'arrière d'un côté, le milieu
    de l'autre) pendant que les trois autres poussent ; le corps roule un peu, l'abdomen ondule, les antennes
    balaient devant lui."""
    p = Pose()
    for rang, cote, decale in (("avant", "_G", 0.0), ("milieu", "_D", 0.0), ("arriere", "_G", 0.0),
                               ("avant", "_D", 0.5), ("milieu", "_G", 0.5), ("arriere", "_D", 0.5)):
        _pas(p, rang, cote, 2 * t + decale)
    p.add("corps", rot=(0, 3 * onde(t, 2), 2 * onde(t, 2, 0.25)), pos=(0, 0, 0.002 * abs(onde(t, 2))))
    p.add("abdomen2", rot=(0, 0, 8 * onde(t, 1)))
    p.add("abdomen3", rot=(0, 0, -8 * onde(t, 1, -0.2)))
    p.add("tete", rot=(0, 0, 4 * onde(t, 2)))
    p.add("antenne_g", rot=(6 * onde(t, 2), 0, 10 * onde(t, 2)))
    p.add("antenne_d", rot=(6 * onde(t, 2, 0.5), 0, 10 * onde(t, 2, 0.5)))
    return p


def mange(t):
    """Il plonge la tête dans l'herbe et grignote à petits coups, les antennes baissées vers le festin, l'abdomen qui
    se relâche ; puis il se redresse, mâche, et rouvre ses pinces : ce n'est pas parce qu'on mange qu'on baisse la garde."""
    p = Pose()
    bas = cloche(t, 0.42, 0.34)
    croque = max(0.0, onde(t, 8)) ** 2 * cloche(t, 0.42, 0.28)
    p.add("corps", rot=(8 * bas, 0, 0), pos=(0, 0, -0.003 * bas))
    p.add("tete", rot=(18 * bas + 8 * croque, 0, 0))
    p.add("antenne_g", rot=(18 * bas, 0, 0))
    p.add("antenne_d", rot=(18 * bas, 0, 0))
    p.add("abdomen2", rot=(-10 * bas, 0, 0))
    mache = cloche(t, 0.88, 0.08)
    p.add("tete", rot=(3 * mache * onde(t, 10), 0, 0))
    _pinces(p, 12 * mache)
    p.ouvert = borne(1 - 0.3 * croque - cloche(t, 0.80, 0.02))
    return p


def joie(t):
    """Sa danse de victoire : il se cabre sur ses pattes arrière, l'abdomen dressé tout droit, et fait claquer ses
    pinces au-dessus de lui, quatre fois, en sautillant ; puis il se recampe, l'air de dire : vous avez vu ?"""
    p = repos(0.0)
    env = math.sin(math.pi * borne(t / 0.80))
    hop = abs(math.sin(math.pi * 3 * borne(t / 0.80))) * env
    p.add("corps", rot=(-16 * env, 0, 0), pos=(0, 0, 0.010 * env + 0.012 * hop))
    for rang in ("avant", "milieu", "arriere"):
        p.paire("patte_" + rang, rot=(0, -8 * env if rang == "avant" else 0, 0), pos=(0, 0, 0.012 * hop))
    p.add("abdomen2", rot=(12 * env, 0, 0))
    p.add("abdomen3", rot=(10 * env, 0, 0))
    _pinces(p, 24 * env * (0.5 + 0.5 * onde(borne(t / 0.80), 4)))
    p.add("tete", rot=(-10 * env, 0, 0))
    p.add("antenne_g", rot=(-16 * env, 0, 8 * env * onde(t, 4)))
    p.add("antenne_d", rot=(-16 * env, 0, -8 * env * onde(t, 4)))
    return p


def dort(t):
    """Il dort à plat ventre, la garde enfin baissée : l'abdomen redescendu et couché derrière lui, les pinces
    refermées, la tête basse, les antennes rabattues sur le dos ; les yeux fermés, il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.008), rot=(3, 0, 0))
    p.add("abdomen", rot=(-6, 0, 0), ech=(1 + 0.03 * r, 1, 1 + 0.03 * r))
    p.add("abdomen2", rot=(-46, 0, 0))
    p.add("abdomen3", rot=(-34, 0, 0))
    _pinces(p, -8)
    p.add("tete", rot=(10, 0, -8))
    p.add("antenne_g", rot=(-34, 0, 0))
    p.add("antenne_d", rot=(-26, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Perce-oreille")
