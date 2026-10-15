"""La chenille en peluche, deuxième dessin : la chenille de sphinx, une diva du potager. Un seul long boudin de velours
turquoise, découpé en anneaux bombés, chaque anneau ceint d'une bande moutarde, le ventre d'un turquoise d'eau pâle ;
au bout, la corne du sphinx, un crochet framboise dressé : son seul éclat. Tout l'arrière est couché dans l'herbe et
ondule, l'avant se dresse haut comme un buste de cobra, puis la tête se penche vers nous, en biais : elle vous toise
d'en haut, les paupières lourdes, la bouche pincée de celle qu'on dérange en plein repas. Ses six petites pattes
vraies sont repliées contre le poitrail, comme des mains jointes.

    python chenille.py        fabrique la fiche art/apercus/animaux/chenille.png
    (le premier dessin, jamais gardé : chenille_ancien.py)
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

TURQUOISE = M.hexa("#3ec4c0")                 # le velours des anneaux (le poil le fonce en turquoise profond)
EAU = M.hexa("#bfeee6")                       # le ventre : un turquoise d'eau pâle
SARCELLE = M.hexa("#16706f")                  # les pattes, les antennes, le fil du dos : le ton sombre de la famille
MOUTARDE = M.hexa("#f0b23c")                  # les bandes des anneaux, la capsule de la tête
FRAMBOISE = M.hexa("#d8336a")                 # l'accent : la corne du sphinx
ANNEAUX = 11                                  # le nombre d'anneaux, de la queue au cou

# la ligne du corps, de la queue (s = 0) au cou : couchée et ondulante derrière, puis dressée en buste, penchée devant
DOS = K.Fil([(0.050, 0.235, 0.040), (0.010, 0.170, 0.047), (-0.024, 0.095, 0.049), (-0.008, 0.020, 0.052),
             (0.010, -0.036, 0.084), (0.014, -0.064, 0.150), (0.012, -0.076, 0.220), (0.016, -0.106, 0.272),
             (0.024, -0.148, 0.282)], flanc=(1, 0, 0))
LONG = DOS.long


def rayon(t):
    """Le rayon du corps à la fraction t de sa longueur (0 la queue, 1 le cou) : une queue qui s'effile, un gros
    ventre, un cou plus mince sous la tête ; chaque anneau bombé, pincé à sa jointure."""
    base = 0.040 * (0.52 + 0.48 * K.lisse(t / 0.32)) * (1 - 0.20 * K.lisse((t - 0.62) / 0.38))
    pli = np.abs(np.sin(math.pi * ANNEAUX * t))
    return base * (0.86 + 0.14 * pli ** 0.5)


def corps():
    """Le boudin tourné d'une pièce, peint anneau par anneau (une bande moutarde au milieu de chacun, le ventre pâle),
    puis couché le long du dos."""
    ts = np.linspace(0, 1, ANNEAUX * 8 + 1)
    profil = [(float(rayon(t)), float(t * LONG)) for t in ts]
    profil[0], profil[-1] = (0.0, 0.0), (0.0, LONG)
    m = A.tour(A.profil(profil, 2), 56).etire(1.08, 1.0, 1.0)
    t = m.v[:, 2] / LONG
    frac = (t * ANNEAUX) % 1.0
    bande = (np.abs(frac - 0.5) < 0.13) & (t > 0.04) & (t < 0.985)
    rho = np.maximum(np.hypot(m.v[:, 0], m.v[:, 1]), 1e-9)
    ventre = m.v[:, 1] / rho < -0.42
    teinte = np.where(bande[:, None], np.asarray(MOUTARDE), np.asarray(TURQUOISE))
    m.teinte = np.where(ventre[:, None], np.asarray(EAU), teinte)
    return m.sculpte(DOS.couche)


def construire():
    a = K.Animal("chenille")
    a.taille = 0.40

    # ----- le corps : un seul boudin, la couture sur l'échine, un rapiéçage d'eau sur le flanc couché -----
    a.piece("corps", corps(), None)
    a.couture("echine", "corps", 14, 0.06, 0.60, "droit", fil=SARCELLE, large=0.008, haut=0.004, pas=0.013)
    centre, sens = DOS.vise(0.27 * LONG, 0, 0.9, 0.35)
    a.rustine("piece", "corps", centre, sens, 0.40, EAU, 0.0025, 14, fil=SARCELLE)

    # ----- la corne du sphinx : un crochet framboise planté sur le dernier anneau, qui part en arrière puis remonte -----
    pied, avant, nuque = DOS.cadre(0.11 * LONG)
    pied = Vector(pied) + Vector(nuque) * 0.026
    corne = A.courbe([pied - Vector(nuque) * 0.006, pied + Vector((0.002, 0.012, 0.020)), pied + Vector((0.004, 0.030, 0.034)),
                      pied + Vector((0.004, 0.048, 0.036))], 6)
    a.piece("corne", A.tube(corne, lambda u: 0.0085 * (1 - 0.75 * u), 12), FRAMBOISE, poil=False)

    # ----- la tête : une capsule moutarde, plus large que le cou, penchée vers nous et tournée de biais -----
    cou, avant, nuque = DOS.cadre(LONG)
    tete = Vector(cou) + Vector(avant) * 0.030 + Vector((0, 0, -0.004))
    port = A.repere(tete, (14, -10, 26))               # elle pique du nez et tourne la tête vers celui qui la regarde

    def vers(x, y, z):
        return port.to_3x3() @ Vector((x, y, z))

    def capsule(v):
        v = K.bosse(K.bosse(v, (0.75, -0.30, 0.45), 0.12, 0.25), (-0.75, -0.30, 0.45), 0.12, 0.25)    # deux lobes au front
        v = K.bosse(v, (0, -0.70, -0.70), 0.10, 0.30)                                               # un menton qui avance
        return K.emousse(v, 0.88) * [0.037, 0.033, 0.034]
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(capsule), MOUTARDE, mat=port)
    a.couture("crane", "tete", 14, 0.55, 0.97, "droit", fil=SARCELLE, large=0.007, haut=0.0035, pas=0.011)
    a.tete = port @ Vector((0, -0.030, 0.0))
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", tete, vers(0.46 * cote, -0.80, 0.30))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0085)
        a.piece("lourde_" + nom, K.paupiere(0.0085, 0.05), SARCELLE, mat=A.cadre(p + n * 0.004, n, vers(0, 0.10, 1)), poil=False)
        # deux antennes minuscules, deux moignons sombres au coin de la bouche
        p, n = a.surface("tete", tete, vers(0.55 * cote, -0.66, -0.42))
        fil = [p - n * 0.003, p + n * 0.004 + vers(0.003 * cote, -0.002, 0.000), p + n * 0.007 + vers(0.007 * cote, -0.002, -0.001)]
        a.piece("antenne_" + nom, A.tube(A.courbe(fil, 4), lambda u: 0.0034 - 0.0010 * u, 12), SARCELLE, poil=False)
    bouche = a.trace("tete", tete, [vers(x, -0.92, z) for x, z in ((0.20, -0.36), (0.07, -0.40), (-0.06, -0.39), (-0.16, -0.33))])
    a.broderie("bouche", A.courbe(bouche, 4), 0.0022, SARCELLE)

    # ----- les pattes vraies : trois paires, petites et pointues, repliées contre le poitrail du buste dressé -----
    for nom, cote in (("G", 1), ("D", -1)):
        mains = None
        for k, f in enumerate((0.80, 0.85, 0.90)):
            c, av, nu = DOS.cadre(f * LONG)
            c, av, nu = Vector(c), Vector(av), Vector(nu)
            r = float(rayon(f)) * 1.08
            depart = c + Vector((cote * 0.62 * r, 0, 0)) - nu * 0.55 * r
            chemin = [depart - Vector((cote * 0.004, 0, 0)) + nu * 0.002, depart + Vector((cote * 0.003, 0, 0)) - nu * 0.006,
                      depart + Vector((cote * 0.001, 0, 0)) - nu * 0.007 - av * 0.006]
            une = K.tube_peint(A.courbe(chemin, 4), lambda u: 0.0058 * (1 - 0.5 * u), [(0.55, TURQUOISE), (9, SARCELLE)])
            mains = une if mains is None else mains + une
        a.piece("mains_" + nom, mains, None, poil=False)

    # ----- les fausses pattes : des plots trapus, la semelle sombre, sous les anneaux couchés ; et la paire du bout -----
    for nom, cote in (("G", 1), ("D", -1)):
        plots = None
        for f in (0.05, 0.27, 0.35, 0.43, 0.51):
            c, av, nu = DOS.cadre(f * LONG)
            c = Vector(c)
            r = float(rayon(f)) * 1.08
            depart = c + Vector((cote * 0.50 * r, 0, -0.62 * r))
            pied = Vector((depart.x + cote * 0.010, depart.y, 0.0085))
            plot = K.tube_peint([depart, (depart + pied) * 0.5, pied], lambda u: 0.0120 + 0.0010 * u, [(0.55, TURQUOISE), (9, SARCELLE)])
            plots = plot if plots is None else plots + plot
        a.piece("plots_" + nom, plots, None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py chenille). Les mesures sont celles du modèle, avant a.taille.
# Le corps est un seul boudin couché le long du dos : une pièce souple que six os se passent le long du fil, et tout ce
# qui y est cousu ou planté (la couture, le rapiéçage, la corne, les plots, les petites mains) suit le même fil. Les os de
# l'arrière s'articulent à leur bout avant (là où ils tiennent au tronçon d'avant), ceux du buste à leur bout arrière.

from poses import Pose, borne, cloche, onde

# chaque os et le début de son tronçon, en fraction du fil depuis la queue
_TRONCONS = (("bout", 0.0), ("arriere", 0.15), ("corps", 0.30), ("buste", 0.48), ("buste2", 0.64), ("cou", 0.80))


def _au_fil(f):
    return tuple(round(float(x), 4) for x in DOS.cadre(f * LONG)[0])


OS = [("racine", None, (0, 0, 0)),
      ("corps", "racine", _au_fil(0.40)),           # le ventre couché : elle s'y appuie
      ("arriere", "corps", _au_fil(0.30)),          # l'arrière couché, en deux os, chacun à son bout avant
      ("bout", "arriere", _au_fil(0.15)),
      ("buste", "corps", _au_fil(0.48)),            # le pied du buste, là où il se dresse
      ("buste2", "buste", _au_fil(0.64)),
      ("cou", "buste2", _au_fil(0.80)),
      ("tete", "cou", _au_fil(1.0))]                # la nuque, au bout du cou


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


def souple(points, cote):
    """Le boudin : chaque os porte son tronçon, et cède au suivant en douceur sur ± 3 cm."""
    # l'usine retourne les pièces de droite en miroir avant de les donner (plots_D, mains_D) : on les remet à leur place
    s = _abscisse(points * ([-1, 1, 1] if cote == "_D" else [1, 1, 1]), DOS.p)
    montees = [np.ones_like(s)] + [K.lisse((s - f * LONG + 0.03) / 0.06) for _o, f in _TRONCONS[1:]] + [np.zeros_like(s)]
    return {o: montees[i] - montees[i + 1] for i, (o, _f) in enumerate(_TRONCONS)}


PORTEURS = [("corps", souple, "corps"), ("echine", souple, "corps"), ("piece", souple, "corps"), ("corne", souple, "corps"),
            ("plots", souple, "corps"), ("mains", souple, "corps"),
            ("tete", "tete"), ("crane", "tete"), ("oeil", "tete"), ("lourde", "tete"), ("antenne", "tete"), ("bouche", "tete"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def repos(t):
    """La diva pose : elle respire, le buste qui se balance comme un cobra, le bout de la queue qui ondule ; puis elle
    lève le menton et détourne la tête, vexée, avant de nous toiser de nouveau, de haut, en battant lentement des
    paupières."""
    p = Pose()
    r = onde(t, 2)
    p.add("corps", ech=(1 + 0.03 * r, 1, 1 + 0.02 * r))
    p.add("buste", rot=(2 * r, 3 * onde(t, 1), 0))
    p.add("buste2", rot=(0, -3 * onde(t, 1, 0.1), 0))
    p.add("bout", rot=(0, 0, 10 * onde(t, 1)))
    vexee = cloche(t, 0.55, 0.14)
    p.add("cou", rot=(-6 * vexee, 0, -10 * vexee))
    p.add("tete", rot=(-14 * vexee, 0, -34 * vexee))
    p.ouvert = borne(1 - cloche(t, 0.25, 0.04) - cloche(t, 0.85, 0.04))
    return p


def avance(t):
    """Elle ondule à la chenille : une bosse naît au bout de la queue et court le long de l'arrière vers le ventre, qui
    reste posé ; le buste reste dressé, il plonge un peu en avant à chaque vague, la tête toujours digne."""
    p = Pose()
    # la bosse : d'abord le bout de la queue se soulève (rx > 0 : ce qui est derrière le pivot monte), puis l'arrière
    # se soulève et le bout se rabat vers l'herbe ; le ventre et le buste, eux, restent posés
    b1 = 0.5 - 0.5 * math.cos(math.tau * t)
    b2 = 0.5 - 0.5 * math.cos(math.tau * (t - 0.33))
    p.add("bout", rot=(16 * b1 - 14 * b2, 0, 0))
    p.add("arriere", rot=(12 * b2, 0, 0))
    p.add("buste", rot=(6 * onde(t, 1, -0.1), 0, 0))
    p.add("cou", rot=(-4 * onde(t, 1, -0.1), 0, 0))
    p.add("tete", rot=(-3 * onde(t, 1, -0.1), 0, 0))
    return p


def mange(t):
    """Elle se penche, toute droite, jusqu'à la feuille par terre, et la grignote à petits coups pressés ; puis elle se
    redresse et mâche, la bouche pincée, en nous regardant de haut."""
    p = Pose()
    bas = cloche(t, 0.42, 0.34)
    croque = max(0.0, onde(t, 10)) ** 2 * cloche(t, 0.42, 0.28)
    p.add("buste", rot=(30 * bas, 0, 0))
    p.add("buste2", rot=(28 * bas, 0, 0))
    p.add("cou", rot=(16 * bas, 0, 0))
    p.add("tete", rot=(-10 * bas + 10 * croque, 0, -14 * bas))
    mache = cloche(t, 0.86, 0.10)
    p.add("tete", rot=(3 * mache * onde(t, 12), 0, 0))
    p.ouvert = borne(1 - 0.5 * bas - cloche(t, 0.92, 0.02))
    return p


def joie(t):
    """Son grand numéro : elle se dresse encore plus haut, tourne sur elle-même d'un tour complet, le buste ondulant,
    la queue qui fouette ; puis une révérence, et elle reprend la pose."""
    p = repos(0.0)
    env = math.sin(math.pi * borne(t / 0.70))
    tourne = borne((t - 0.08) / 0.55)
    tourne = tourne * tourne * (3 - 2 * tourne)
    p.add("buste", rot=(-10 * env, 0, 360 * tourne))
    p.add("buste2", rot=(-8 * env, 10 * env * onde(t, 3), 0))
    p.add("cou", rot=(0, -8 * env * onde(t, 3, 0.2), 0))
    p.add("tete", rot=(-10 * env, 0, 0))
    p.add("bout", rot=(0, 0, 20 * env * onde(t, 4)))
    p.add("arriere", rot=(0, 0, -8 * env * onde(t, 4, 0.2)))
    salut = cloche(t, 0.82, 0.10, False)
    p.add("buste2", rot=(22 * salut, 0, 0))
    p.add("tete", rot=(16 * salut, 0, 0))
    p.ouvert = 1 - 0.7 * salut
    return p


def dort(t):
    """Elle dort lovée dans l'herbe : le buste couché et enroulé sur sa gauche jusqu'à poser la tête près de la queue,
    les yeux fermés ; elle respire lentement, et le bout de la queue frémit une fois."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", ech=(1 + 0.035 * r, 1, 1 + 0.025 * r))
    p.add("buste", rot=(52, 0, 50))
    p.add("buste2", rot=(18, 0, 40))
    p.add("cou", rot=(0, 0, 40))
    p.add("tete", rot=(0, 18, 20))
    p.add("bout", rot=(0, 0, -20 + 10 * cloche(t, 0.6, 0.05)))
    p.add("arriere", rot=(0, 0, -12))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Chenille")
