"""La taupe en peluche, deuxième dessin : la myope du jardin, qui sort de terre pour savoir qui marche sur son toit.
Un gros haricot de velours ardoise sans cou, assis sur sa croupe ronde et dressé à moitié, la gorge pâle cousue en
plastron ; tout l'avant file en pointe vers un long groin rose qui se relève et flaire de travers. Ses deux mains sont
démesurées, aussi grandes que sa tête : deux paumes roses toutes rondes, tournées vers le dehors comme une brasse,
cinq doigts boudinés et cinq griffes d'ivoire ; la gauche levée haut qui tâte l'air, la droite plantée dans l'herbe.
Des yeux si petits qu'on les cherche dans le velours, et deux sourcils brodés qui se lèvent : elle ne vous voit pas,
mais elle vous sent.

    python taupe.py        fabrique la fiche art/apercus/animaux/taupe.png
    (le premier dessin, jamais gardé : taupe_ancien.py)
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

ARDOISE = M.hexa("#5e6683")                   # le velours : un ardoise bleuté (le poil le fonce en ardoise profond)
SUIE = M.hexa("#3b4054")                      # les bras, la pièce du dos, le fil des sourcils
BRUME = M.hexa("#aab3cc")                     # le plastron de la gorge
ROSE = M.hexa("#f2899e")                      # l'accent : le groin, les mains, les pieds, la queue
IVOIRE = M.hexa("#f3ead6")                    # les griffes
TOURNE = 0                                    # -38 pour la fiche, posée de biais (on lit son groin) ; 0 pour le jeu
# l'échine, de la croupe au nez : assise sur la croupe, l'avant dressé, la tête qui part vers sa gauche (vers vous)
DOS = K.Fil([(0.0, 0.150, 0.074), (0.0, 0.080, 0.079), (0.0, 0.010, 0.090), (0.008, -0.056, 0.108), (0.028, -0.112, 0.126)],
            flanc=(1, 0, 0))
GALBE = [(0, 0), (0.050, 0.008), (0.072, 0.034), (0.079, 0.074), (0.077, 0.120), (0.068, 0.166), (0.054, 0.206), (0.039, 0.240),
         (0.026, 0.262), (0, 0.278)]


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def main(centre, paume, doigts, ecarte=1.0, echelle=1.0):
    """Une main de taupe : une large paume ronde et creusée, dont le haut se fend en cinq doigts boudinés, et au bout de
    chacun un ongle d'ivoire large et plat, comme une petite pelle. paume : là où regarde le creux de la main ; doigts :
    là où pointe le doigt du milieu ; echelle : sa taille."""
    angles = [math.radians(90 + (k - 2) * 25 * ecarte) for k in range(5)]
    m = A.boule(1.0, 48, 16)

    def paleron(v):
        th = np.arctan2(v[:, 1], v[:, 0])
        lobes = sum(np.exp(-((np.angle(np.exp(1j * (th - t)))) / math.radians(8.5)) ** 2) for t in angles)
        lobes *= K.lisse(v[:, 1] * 3.0 + 0.4) * (v[:, 0] ** 2 + v[:, 1] ** 2) ** 1.5
        r = 1 + 0.26 * lobes
        s = v * np.stack([0.046 * r, 0.043 * r, 0.0135 * (1 - 0.30 * lobes)], axis=1)
        s[:, 2] -= 0.007 * (1 - (s[:, 0] ** 2 + s[:, 1] ** 2) / 0.046 ** 2)          # le creux de la paume
        return s
    m.sculpte(paleron).peint(ROSE)
    for k, t in enumerate(angles):
        d = np.array([math.cos(t), math.sin(t), 0.0])
        r = 0.043 * 1.26 + 0.003 * math.cos(t)
        ongle = A.tour(A.profil([(0.0085, 0.0), (0.0080, 0.006), (0.0055, 0.012), (0, 0.017)], 4), 16).etire(1.0, 0.42, 1.0)
        ongle.sculpte(lambda v: v + np.outer(v[:, 2] ** 2, [0, -10.0, 0]))                 # recourbé vers le creux
        ongle.v = ongle.v @ np.array(A.cadre((0, 0, 0), tuple(d), (0, 0, -1)))[:3, :3].T + d * (r - 0.006)
        m = m + ongle.peint(IVOIRE)
    m.v = m.v * echelle
    rep = np.array(A.cadre(centre, paume, doigts))
    m.v = m.v @ rep[:3, :3].T + rep[:3, 3]
    return m


def construire():
    a = K.Animal("taupe")
    a.taille = 0.42

    # ----- le corps : un haricot couché le long de l'échine, gros de croupe, sans cou, qui file en pointe vers le nez -----
    corps = A.tour(A.profil(GALBE, 8), 56)
    corps.sculpte(lambda v: v * [1.06, 0.96, 1.0])
    G.sillons(corps, [14], 0.005, 1.1)
    corps.sculpte(DOS.couche)
    a.piece("corps", corps, ARDOISE)
    a.couture("dos", "corps", 14, 0.12, 0.78, fil=SUIE)
    a.couture("flanc", "corps", 0, 0.08, 0.46, "droit", fil=SUIE, large=0.007, haut=0.003)
    centre, d = DOS.vise(0.190, 0.30, 0.0, -1.0)
    a.rustine("plastron", "corps", centre, d, lambda th: 0.62 - 0.14 * math.cos(2 * th), BRUME, feston=22, fil=SUIE)
    centre, d = DOS.vise(0.090, 0.0, 0.70, 0.72)
    a.rustine("piece", "corps", centre, d, lambda th: 0.30 + 0.05 * math.cos(3 * th) + 0.03 * math.sin(2 * th), SUIE, feston=14, fil=BRUME)

    # ----- le groin : un long cône rose qui se relève au bout, comme un doigt qui flaire ; un ourlet à sa racine -----
    nez, avant, nuque = (Vector(x) for x in DOS.cadre(DOS.long))
    flair = (avant + nuque * 0.05 + Vector((0.10, 0, 0))).normalized()
    groin = A.tour(A.profil([(0.024, 0.0), (0.020, 0.022), (0.0145, 0.048), (0.0098, 0.074), (0.0078, 0.092), (0.0070, 0.101), (0, 0.107)], 6), 32)
    groin.sculpte(lambda v: v + np.outer((v[:, 2] / 0.107) ** 2, [0, 0.016, 0]))
    racine = nez - avant * 0.022
    a.piece("groin", groin, ROSE, mat=A.cadre(racine, flair, nuque), poil=False)
    a.tete = racine + flair * 0.010

    # ----- les yeux : deux têtes d'épingle dans le velours, et deux sourcils brodés qui se lèvent -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, d = DOS.vise(0.236, 0.30, 0.80 * c, 0.52)
        p, n = a.surface("corps", centre, d)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0058)
        _c, av, nu = (Vector(x) for x in DOS.cadre(0.236))
        fl = Vector(DOS.flanc) * c
        cil = a.trace("corps", centre, [d.normalized() + nu * (0.30 + 0.10 * math.sin(math.pi * u)) + av * (0.14 - 0.30 * u) + fl * 0.0
                                        for u in np.linspace(0, 1, 5)], 0.004)
        a.broderie("sourcil_" + nom, A.courbe(cil, 4), 0.0022, SUIE)

    # ----- les mains : énormes, la paume tournée vers le dehors ; la gauche levée à hauteur de joue qui tâte l'air,
    #       la droite plantée dans l'herbe, les griffes devant -----
    epaule, av, nu = (Vector(x) for x in DOS.cadre(0.196))
    fl = Vector(DOS.flanc)
    for nom, c, centre, paume, doigts, ecarte, echelle in (
            ("G", 1, epaule + fl * 0.090 + nu * 0.012 + av * 0.004, fl * 0.80 + av * 0.56 - nu * 0.05, nu * 0.62 + av * 0.72, 1.10, 0.60),
            ("D", -1, epaule - fl * 0.086 - nu * 0.040 + av * 0.030, -fl * 0.62 + av * 0.55 + nu * 0.50, av * 0.75 - nu * 0.55 - fl * 0.20, 0.95, 0.80)):
        dos_main = centre - paume.normalized() * (0.012 * echelle)
        coude = epaule + fl * ((0.042 if c > 0 else 0.070) * c) + nu * (-0.002 if c > 0 else -0.020)
        m = main(centre, paume, doigts, ecarte, echelle)
        if c < 0:                                         # la main plantée : posée juste sur l'herbe
            bas = Vector((0, 0, 0.004 - float(m.v[:, 2].min())))
            centre, dos_main = centre + bas, dos_main + bas
            m = main(centre, paume, doigts, ecarte, echelle)
        a.piece("bras_" + nom, A.tube(A.courbe([tuple(epaule + fl * (0.030 * c)), tuple(coude), tuple(dos_main)], 5),
                                      lambda t, g=(0.022 if c > 0 else 0.030): g - 0.25 * g * t, 16), ARDOISE)
        a.piece("main_" + nom, m, None, poil=False)

    # ----- les pieds de derrière : deux semelles roses étalées de chaque côté de la croupe, et le bout de queue dressé -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.022, 0.038, 0.011), ROSE, pos=(0.066 * c, 0.096, 0.011), rot=(0, 0, 46 * c), poil=False)
    queue = A.tube(A.courbe([(0, 0.140, 0.082), (0.004, 0.170, 0.096), (0.010, 0.180, 0.114)], 5), lambda t: 0.0085 - 0.0040 * t, 12)
    a.piece("queue", queue, ROSE, poil=False)
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py taupe). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Le haricot est une seule pièce : on le rend souple le long de l'échine, l'avant (le museau, les yeux) suit « tete ».
# Les deux bras ne sont pas symétriques (la gauche levée qui tâte l'air, la droite plantée) : chacun a son os nommé à la
# main, à l'épaule ; ils pendent au corps et non à la tête, pour que la main plantée ne glisse pas quand la tête cherche.

from poses import Pose, borne, cloche, onde


def _ou(v):
    return tuple(round(float(x), 4) for x in v)


_EPAULE = Vector(DOS.cadre(0.196)[0])
OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.100, 0.020)),                       # le bas de la croupe, où elle est assise
    ("tete", "corps", _ou(DOS.cadre(0.150)[0])),                     # sur l'échine, au-dessus des épaules
    ("groin", "tete", _ou(Vector(DOS.cadre(DOS.long)[0]) - Vector(DOS.cadre(DOS.long)[1]) * 0.022)),   # la racine du groin
    ("bras_g", "corps", _ou(_EPAULE + Vector(DOS.flanc) * 0.030)),   # chaque épaule
    ("bras_d", "corps", _ou(_EPAULE - Vector(DOS.flanc) * 0.030)),
    ("pied_G", "racine", (0.066, 0.096, 0.011)),                     # le milieu de la semelle (la droite est son miroir)
    ("queue", "corps", (0.0, 0.140, 0.082)),
]


def _abscisse(points):
    """Pour chaque point : sa place le long de l'échine, au pied de la perpendiculaire sur le tronçon le plus proche."""
    a, ab = DOS.p[:-1], np.diff(DOS.p, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    ap = points[:, None, :] - a[None, :, :]
    u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
    j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
    return DOS.fait[j] + u[np.arange(len(points)), j] * np.sqrt(l2[j])


def souple(points, cote):
    """Le haricot et ce qui y est cousu : l'arrière suit le corps, l'avant passé les épaules suit la tête."""
    # l'usine retourne en miroir les pièces de droite (sourcil_D) avant de les donner : on les remet à leur place
    s = _abscisse(points * ([-1, 1, 1] if cote == "_D" else [1, 1, 1]))
    w = K.lisse((s - 0.120) / 0.090)
    return {"corps": 1 - w, "tete": w}


def _bras(points, cote):
    """Un bras et sa main : tout entier sur l'os de son côté (nommé à la main, sans miroir)."""
    return {"bras_g" if cote == "_G" else "bras_d": np.ones(len(points))}


PORTEURS = [("corps", souple, "corps"), ("dos", souple, "corps"), ("flanc", souple, "corps"), ("plastron", souple, "corps"),
            ("piece", souple, "corps"), ("sourcil", souple, "corps"),
            ("groin", "groin"), ("oeil", "tete"), ("bras", _bras), ("main", _bras), ("pied", "pied", True), ("queue", "queue"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]

FOUILLE = (6.0, 38.0)                         # mange : le corps se penche, l'avant plonge vers la terre
BOULE = (6.0, 18.0, 20.0)                     # dort : le corps, la tête et le groin se replient
RAME_G = 56.0                                 # de combien le bras gauche, levé sur le modèle, descend ramer près du sol


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _penche(p, degres):
    """Le corps se penche en avant autour de sa croupe ; le bras droit, planté, se redresse d'autant et remonte de ce
    que son épaule descend : la main reste posée dans l'herbe."""
    p.add("corps", rot=(degres, 0, 0))
    p.add("bras_d", rot=(-degres, 0, 0), pos=(0, 0, 0.143 * math.sin(math.radians(degres))))


def _flaire(p, t, force, vite=20):
    """Le groin flaire : il frétille en petits coups de côté et de haut en bas (vite : combien de coups dans l'animation)."""
    p.add("groin", rot=(5 * force * onde(t, vite, 0.25), 0, 7 * force * onde(t, vite)))


def repos(t):
    """La myope cherche ce qui marche sur son toit : elle respire, balaie lentement l'air de la tête d'un côté puis de
    l'autre (elle ne voit rien), le groin qui frétille sans arrêt, et sa grande main levée tâte l'air, la paume en
    avant ; un clignement de ses yeux minuscules."""
    p = Pose()
    r = onde(t, 2)
    p.add("corps", ech=(1 + 0.015 * r, 1, 1 + 0.020 * r))
    cherche = cloche(t, 0.25, 0.16) - cloche(t, 0.65, 0.16)
    p.add("tete", rot=(-4 * cloche(t, 0.45, 0.08), 0, 18 * cherche))
    _flaire(p, t, 0.6 + 0.4 * cloche(t, 0.45, 0.10), 30)
    tate = cloche(t, 0.45, 0.14)
    p.add("bras_g", rot=(-14 * tate + 4 * onde(t, 3) * tate, 0, 10 * tate))
    p.add("queue", rot=(0, 0, 10 * onde(t, 1)))
    p.ouvert = 1 - cloche(t, 0.10, 0.02) - cloche(t, 0.80, 0.02)
    return p


def avance(t):
    """Elle avance à la brasse, en se dandinant : les grandes mains rament l'une après l'autre (la gauche descend ramer
    près du sol), le haricot roule d'un côté à l'autre, les semelles traînent à petits pas, le groin flaire devant."""
    p = Pose()
    s, c = math.sin(math.tau * t), math.cos(math.tau * t)
    _penche(p, 4)
    p.add("corps", rot=(0, 4 * s, 3 * s), pos=(0, 0, 0.003 * abs(c)))
    p.add("tete", rot=(0, -3 * s, -4 * s))
    p.add("bras_g", rot=(10 * c, RAME_G + 8 * c, -18 * s))
    p.add("bras_d", rot=(-7 * (1 - s), 0, 10 * c), pos=(0, 0, 0.010 * max(0.0, -c) + 0.008 * max(0.0, -s)))   # jamais sous l'herbe
    p.add("pied_G", pos=(0, 0.010 * s, 0.006 * max(0.0, c)))
    p.add("pied_D", pos=(0, -0.010 * s, 0.006 * max(0.0, -c)))
    _flaire(p, t, 0.8, 4)
    p.add("queue", rot=(0, 0, 12 * s))
    return p



def mange(t):
    """Elle a senti un ver : elle se penche, plonge le groin dans la terre et fouille en le tortillant, gratte de ses
    deux grandes mains ; puis elle se redresse, mâche, le groin en l'air, ravie."""
    p = Pose()
    bas = _plateau(t, 0.40, 0.26, 0.12)
    gratte = onde(t, 8) * _plateau(t, 0.40, 0.22, 0.06)
    _penche(p, FOUILLE[0] * bas)
    p.add("tete", rot=(FOUILLE[1] * bas, 0, 4 * gratte))
    _flaire(p, t, 0.5 + 0.8 * bas, 20)
    p.add("bras_g", rot=(6 * gratte, RAME_G * bas, 0))
    p.add("bras_d", rot=(-8 * gratte, 0, 0), pos=(0, 0, 0.006 * max(0.0, gratte)))
    mache = cloche(t, 0.84, 0.10)
    p.add("groin", rot=(-14 * mache, 0, 0))
    p.ouvert = 1 - cloche(t, 0.90, 0.03)
    return p


def joie(t):
    """Sa fête : elle se dresse tout droit comme sortie de sa taupinière, lève ses deux grandes mains et les agite
    au-dessus d'elle, le groin pointé au ciel qui frétille ; puis elle se rassoit, la main gauche reprend l'air."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85)) if t < 0.85 else 0.0
    agite = onde(t, 4) * env
    p.add("corps", rot=(-12 * env, 0, 0), pos=(0, 0, 0.018 * env))
    p.add("tete", rot=(-16 * env, 0, 0))
    p.add("bras_g", rot=(-16 * env, -10 * env + 12 * agite, 0))
    p.add("bras_d", rot=(-40 * env, 70 * env - 12 * agite, 0))
    _flaire(p, t, 1.4 * env, 12)
    p.add("groin", rot=(-12 * env, 0, 0))
    p.add("queue", rot=(0, 0, 20 * onde(t, 6) * env))
    return p


def dort(t):
    """Roulée en boule sur le flanc de sa croupe, le groin rentré sous la grande main gauche ramenée devant le museau,
    les yeux fermés ; elle respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    _penche(p, BOULE[0])
    p.add("corps", ech=(1.03 + 0.015 * r, 1.0, 0.97 + 0.025 * r))
    p.add("tete", rot=(BOULE[1], 0, 8))
    p.add("groin", rot=(BOULE[2], 0, 0))
    p.add("bras_g", rot=(10, RAME_G * 0.8, -20))
    p.add("bras_d", rot=(0, 0, 10))
    p.add("queue", rot=(0, 0, 30))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Taupe")
