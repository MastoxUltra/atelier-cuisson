"""Le singe en peluche, cousu main (2e dessin, après la relecture de la session Animaux) : un brun noisette, un
chapardeur d'acrobate : le corps penché en avant, presque à quatre pattes, des bras interminables qui touchent le sol
bien devant lui, de longues jambes repliées, une mâchoire qui avance en museau, une face crème en masque autour des
yeux d'ambre, la calotte charbon, de grandes oreilles rondes ; et surtout une très longue queue qui monte en crosse
au-dessus du dos. Il avance à pas de loup vers quelque chose qu'il ne devrait pas prendre, un œil sur nous, l'autre
déjà sur la cible, un sourire en coin.

    python singe.py        fabrique la fiche art/apercus/animaux/singe.png (cousu main, palier 2)
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


def propres(points, eps=2e-4):
    """Les points d'un tracé sans doublons consécutifs (un tube dont deux points se suivent à l'identique se déforme en NaN) ;
    au moins deux points, écartés d'un millimètre au pire."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie

NOISETTE = M.hexa("#f0cf9c")                  # la dominante : brun noisette (le poil la fonce : on la prend très claire)
CHARBON = M.hexa("#4a3a2c")                   # l'accent : la calotte, le bout des mains et des pieds, le bout de la queue
CREME = M.hexa("#fff4e0")                     # le masque, le ventre
ROSE = M.hexa("#e9a5a0")                      # le dedans des oreilles, la bouche
AMBRE = M.hexa("#ffc23a")                     # les yeux
CORPS = Vector((0.0, 0.080, 0.310))
TETE = Vector((0.0, -0.230, 0.390))
LACET = 24.0


def construire():
    a = K.Animal("singe")
    a.taille = 0.85                           # queue comprise

    # ----- le corps : un œuf long, penché vers l'avant (le dos monte en voûte derrière les épaules) ; le ventre crème -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(NOISETTE, float), (len(v), 1))
    t[(v[:, 2] < -0.30) & (v[:, 1] < 0.2)] = CREME
    corps.teinte = t

    def oeuf(v):
        s = v * [0.098, 0.205, 0.112]
        s[:, 2] += 0.045 * K.lisse((v[:, 1] + 0.1) / 1.0)                       # la croupe plus haute que le poitrail
        return s
    G.sillons(corps, [14], 0.005, 1.1)
    a.piece("corps", corps.sculpte(oeuf), None, pos=CORPS, rot=(-6, 0, 0))

    # ----- la tête : un crâne rond, la mâchoire qui avance en museau (le cône crème), l'arcade marquée ; tournée vers nous -----
    H = A.repere(TETE, (14, 0, LACET))
    H3 = H.to_3x3()

    def crane(v):
        v = K.bosse(v, (0, -0.8, 0.45), 0.14, 0.35)                              # l'arcade
        return v * [0.092, 0.092, 0.088]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(crane), NOISETTE, mat=H)
    a.rustine("calotte", "tete", H.to_translation(), H3 @ Vector((0, 0.40, 1.0)), lambda th: 0.66 + 0.08 * math.cos(th), CHARBON, 0.003, 0)
    a.rustine("masque", "tete", H.to_translation() + Vector((0, 0, -0.004)), H3 @ Vector((0, -1.0, -0.06)),
              lambda th: 0.74 - 0.10 * math.cos(2 * th), CREME, 0.003, 0)
    museau = A.tour(A.profil([(0, 0), (0.060, 0.006), (0.058, 0.036), (0.046, 0.066), (0.030, 0.088), (0, 0.098)], 6), 32)
    a.piece("museau", museau.etire(0.95, 0.82, 1.0), CREME, mat=H @ A.repere((0, -0.040, -0.034), (90, 0, 0)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.020, 0.012, 0.012), CHARBON, mat=H @ A.repere((0, -0.140, -0.034)), poil=False)
    a.tete = H @ Vector((0, -0.140, -0.030))
    bouche = [H3 @ Vector(d) for d in ((-0.50, -0.55, -0.55), (-0.20, -0.84, -0.66), (0.20, -0.84, -0.66), (0.60, -0.55, -0.50), (0.74, -0.40, -0.36))]
    a.broderie("sourire", A.courbe(propres(a.trace("museau", H @ Vector((0, -0.040, -0.034)), bouche, 0.004)), 4), 0.0026, CHARBON)

    # ----- les yeux : vivants, d'ambre sous l'arcade ; un sourcil brodé plus haut sur l'œil qui nous guette -----
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.46, -0.84, 0.20))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.22, AMBRE, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0145)
        brow = [H3 @ Vector((c * (0.16 + 0.44 * t), -0.92 + 0.14 * t, 0.36 + (0.26 if c > 0 else 0.10) * t)) for t in np.linspace(0, 1, 5)]
        a.broderie("sourcil_" + nom, propres(a.trace("tete", H.to_translation(), brow, 0.004)), 0.0030, CHARBON)
        po = A.profil([(0, 0), (0.044, 0.010), (0.050, 0.030), (0.040, 0.046), (0.016, 0.054), (0, 0.056)], 5)
        E = A.cadre(H @ Vector((c * 0.092, 0.010, 0.010)), H3 @ Vector((c * 0.95, -0.10, 0.18)), H3 @ Vector((0, 0, 1)))
        a.piece("oreille_" + nom, A.tour(po, 28).etire(1.0, 0.45, 1.0), NOISETTE, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 20).etire(0.66, 0.30, 0.70).pose((0, 0.007, 0.008)), ROSE, mat=E, poil=False)

    # ----- les bras : interminables, plantés loin devant, les mains charbon à plat sur le sol ; le gauche avance d'un pas -----
    for nom, c, avance in (("G", 1, -0.050), ("D", -1, 0.040)):
        chemin = [(c * 0.100, -0.090, 0.370), (c * 0.150, -0.200, 0.300), (c * 0.150, -0.320 + avance, 0.190), (c * 0.140, -0.440 + avance, 0.032)]
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.036 - 0.010 * t, 14), NOISETTE)
        a.piece("main_" + nom, A.boule(1.0, 24, 12).etire(0.032, 0.056, 0.020), CHARBON, pos=(c * 0.140, -0.470 + avance, 0.022), rot=(0, 0, c * 8))

    # ----- les jambes : longues et repliées, les genoux en l'air derrière les coudes, les pieds charbon à plat -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.100, 0.210, 0.340), (c * 0.150, 0.100, 0.230), (c * 0.150, 0.230, 0.090), (c * 0.135, 0.130, 0.030)]
        a.piece("jambe_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.042 - 0.012 * t, 14), NOISETTE)
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.032, 0.070, 0.020), CHARBON, pos=(c * 0.135, 0.090, 0.022), rot=(0, 0, c * 10))

    # ----- la queue : très longue, elle monte du bas du dos et se recourbe en crosse, le bout charbon ; elle fait la moitié du singe -----
    chemin = [(0.0, 0.300, 0.300), (0.0, 0.440, 0.360), (0.0, 0.520, 0.520), (0.0, 0.480, 0.700), (0.0, 0.380, 0.750), (0.0, 0.320, 0.690)]
    queue = K.tube_peint(A.courbe(chemin, 6), lambda t: 0.034 - 0.014 * t, [(0.84, NOISETTE), (1, CHARBON)], 16)
    a.piece("queue", queue, None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("singe", styles.style_de("singe"), sys.modules[__name__]), "Singe")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py singe). Les mesures sont celles du modèle (à quatre pattes, penché en avant), avant a.taille.
# Le chapardeur : tout est dans les bras, la tête et la queue ; la queue en crosse est souple, trois os se la partagent.

from poses import Pose, borne, cloche, onde

JAMBE = 0.34                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.18, 0.31)),         # les hanches : il se penche, se cabre, se roule autour
    ("tete", "corps", (0.0, -0.19, 0.37)),          # la nuque
    ("oreille_G", "tete", (0.110, -0.21, 0.44)),
    ("bras_G", "corps", (0.100, -0.09, 0.37)),      # l'épaule : le bras et la main
    ("jambe_G", "corps", (0.100, 0.21, 0.34)),      # la hanche : la jambe et le pied
    ("queue1", "corps", (0.0, 0.30, 0.30)),         # la queue en crosse : le pied, le milieu, le bout
    ("queue2", "queue1", (0.0, 0.52, 0.52)),
    ("queue3", "queue2", (0.0, 0.40, 0.75)),
]


def queue_souple(points, cote):
    """La queue se plie en trois : la base (bas du dos), le milieu (le sommet de la crosse), le bout (la pointe charbon).
    On les partage selon la hauteur du point : 0,3 à 0,36 pour la base, vers 0,5 à 0,6 le milieu, au-dessus de 0,68 le bout."""
    z = points[:, 2]

    def doux(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3 - 2 * x)
    milieu, bout = doux((z - 0.36) / 0.16), doux((z - 0.64) / 0.08)
    return {"queue1": 1 - milieu, "queue2": milieu * (1 - bout), "queue3": milieu * bout}


PORTEURS = [("corps", "corps"), ("tete", "tete"), ("museau", "tete"), ("nez", "tete"), ("sourire", "tete"), ("oeil", "tete"),
            ("calotte", "tete"), ("iris", "tete"), ("masque", "tete"),
            ("sourcil", "tete"), ("oreille", "oreille", True), ("pavillon", "oreille", True), ("bras", "bras", True),
            ("main", "bras", True), ("jambe", "jambe", True), ("pied", "jambe", True), ("queue", queue_souple, "queue1"),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def repos(t):
    """Accroupi, il guette : la tête pivote vite d'un côté puis de l'autre, les oreilles captent, la queue en crosse se déroule
    et se renroule, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.26, 0.12), cloche(t, 0.62, 0.12)
    p.add("corps", ech=(1 + 0.010 * r, 1, 1 + 0.016 * r))
    p.add("tete", rot=(2 * r + 4 * g, -6 * g + 5 * d, 26 * g - 22 * d))
    p.add("oreille_G", rot=(0, 0, 20 * cloche(t, 0.40, 0.05) - 8 * g))
    p.add("oreille_D", rot=(0, 0, -20 * cloche(t, 0.82, 0.05) + 8 * d))
    p.add("queue1", rot=(0, 0, 8 * onde(t, 1)))
    p.add("queue2", rot=(10 * onde(t, 1, -0.10), 0, 0))
    p.add("queue3", rot=(14 * onde(t, 1, -0.20), 0, 0))
    p.ouvert = borne(1 - 0.3 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.70, 0.02))
    return p


def avance(t):
    """À pas de loup : les bras longs et les jambes repliées alternent, le corps roule et pique, la tête reste tournée vers
    la cible, la queue en crosse oscille d'un côté à l'autre."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 26.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.45
    p.add("corps", pos=(0, 0, -creux), rot=(2 * onde(t, 2, 0.1), 4 * c, 3 * s))
    for nom, sens in (("bras_G", 1), ("jambe_D", 1), ("bras_D", -1), ("jambe_G", -1)):
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.030 * max(0.0, -sens * c)))
    p.add("tete", rot=(-6 + 2 * onde(t, 2, -0.2), -3 * c, 10 - 2 * s))
    p.paire("oreille", rot=(-8 + 3 * onde(t, 2, -0.25), 0, 0))
    p.add("queue1", rot=(-6, 0, -10 * s))
    p.add("queue2", rot=(-8 * onde(t, 2, -0.15), 0, -12 * onde(t, 1, -0.12)))
    p.add("queue3", rot=(-10 * onde(t, 2, -0.30), 0, -14 * onde(t, 1, -0.24)))
    return p


def mange(t):
    """Il se redresse sur les hanches, porte une main à sa bouche, mâchouille en regardant autour de lui, puis rabaisse la main."""
    p = Pose()
    haut = cloche(t, 0.5, 0.36)
    mache = onde(t, 6) * haut
    p.add("corps", rot=(-14 * haut, 0, 0))
    p.add("bras_G", rot=(-84 * haut, 0, 14 * haut))
    p.add("tete", rot=(12 * haut + 4 * mache, 0, 18 * cloche(t, 0.78, 0.12)))
    p.paire("oreille", rot=(-5 * mache, 0, 0))
    p.add("queue1", rot=(10 * haut, 0, 0))
    p.add("queue2", rot=(0, 0, 10 * onde(t, 2) * haut))
    p.ouvert = borne(1 - cloche(t, 0.12, 0.03) - cloche(t, 0.88, 0.03))
    return p


def joie(t):
    """Un bond d'acrobate : il se tasse, saute en se retournant à moitié, les bras en l'air, la queue qui fouette, et se
    réceptionne sur les mains."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 4) * cloche(t, 0.50, 0.30, False)
    p.add("corps", pos=(0, 0, -0.04 * tasse + 0.26 * vol), rot=(10 * tasse - 16 * vol + 8 * salut, 0, 0))
    p.paire("bras", rot=(-110 * vol + 20 * tasse, 0, 24 * vol))
    p.paire("jambe", rot=(-30 * vol, 0, 0))
    p.add("tete", rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire("oreille", rot=(-20 * vol, 0, 0))
    p.add("queue1", rot=(-18 * vol, 0, 20 * fouet))
    p.add("queue2", rot=(-12 * vol, 0, 26 * fouet))
    p.add("queue3", rot=(-10 * vol, 0, 30 * fouet))
    return p


def dort(t):
    """Roulé en boule, la tête entre les genoux, les bras serrés autour des jambes, la queue enroulée par-dessus ; il respire."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.10), rot=(26, 0, 0), ech=(1 + 0.012 * r, 1, 1 + 0.026 * r))
    p.paire("bras", rot=(-30, 0, -18))
    p.paire("jambe", rot=(-60, 0, 12))
    p.add("tete", rot=(36, 0, 22))
    p.paire("oreille", rot=(-18, 0, 0))
    p.add("queue1", rot=(-30, 0, 60))
    p.add("queue2", rot=(-50 + 2 * r, 0, 30))
    p.add("queue3", rot=(-40 + 3 * r, 0, 20))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
