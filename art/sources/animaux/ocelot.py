"""L'ocelot en peluche de magasin : un sable clair, presque crème, le ventre blanc, et sur les flancs de longues
rayures-chaînes chocolat, qui s'enchaînent en ovales cernés ; la tête ronde et petite, de grands yeux d'ambre, les
oreilles rondes à tache blanche, les pattes à taches, la queue annelée. Un petit félin tout en élégance, peluche
d'étagère : assis bien droit, le dos tendu, les pattes de devant serrées, la queue enroulée autour des pieds, la tête
penchée de côté, qui nous observe de très haut, sans un bruit.

    python ocelot.py        fabrique la fiche art/apercus/animaux/ocelot.png (peluche de magasin, palier 4)

Les 5 traits de l'espèce (relus sur 12 photos de Commons le 15/10) : 1. un félin mince et long, la tête ronde aux petites
oreilles rondes tachées de blanc derrière ; 2. le pelage sable chargé de chaînes d'ovales bruns cernés ; 3. le visage :
deux barres noires sur chaque joue, deux traits sur le front, le museau blanc, la truffe rose ; 4. la queue annelée de brun ;
5. les pattes tachetées, les grands pieds.
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

GONFLAGE = True       # la base aux volumes gonflés de l'Artiste (fusion.py) : jointures fondues, bouts arrondis


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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
SABLE = M.hexa("#fff0c8")                     # la dominante : sable clair, presque crème
CHOCOLAT = M.hexa("#7a4a30")                  # l'accent : les chaînes de rayures
BLANC = M.hexa("#fffaf0")                     # le ventre, le dedans des pattes
OEIL = M.hexa("#e8b84a")                      # les yeux
CORPS = Vector((0.0, 0.040, 0.300))
TETE = Vector((0.0, -0.080, 0.610))
LACET, PENCHE = 28.0, 12.0


def chaines(m, graine=0.0, freq=10.0, ventre=None):
    """Peint une pièce encore droite en sable et lui pose des chaînes d'ovales chocolat cernés de sable (un produit de
    sinus dans une bande étroite, étiré dans le sens du flanc) ; le ventre, blanc."""
    v = m.v
    t = np.tile(np.asarray(SABLE, float), (len(v), 1))
    bande = np.sin(freq * v[:, 2] + graine + 0.9 * np.sin(2.4 * v[:, 1]))             # des bandes ondulées le long du flanc
    chaine = np.sin(0.55 * freq * v[:, 1] + 0.6 * graine)                              # coupées en chaînons
    t[(bande > 0.34) & (chaine > -0.55)] = CHOCOLAT
    if ventre is not None:
        t[ventre(v)] = BLANC
    m.teinte = t
    return m


def construire():
    a = K.Animal("ocelot")
    a.taille = 1.00

    # ----- le corps : un œuf dressé (assis), le poitrail rond, les hanches larges ; chaînes de rayures chocolat -----
    def oeuf(v):
        v = K.bosse(v, (0, -0.9, 0.3), 0.12, 0.45)
        s = v * [0.150, 0.175, 0.230]
        s[:, 0] *= 1 + 0.18 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s
    corps = chaines(A.boule(1.0, 56, 28), 0.0, ventre=lambda v: (v[:, 1] < -0.55) & (v[:, 2] < 0.7))
    a.piece("corps", corps.sculpte(oeuf), None, pos=CORPS, rot=(-8, 0, 0))

    # ----- la tête : ronde et petite, les joues rondes, les moustaches ; penchée de côté, tournée vers nous -----
    T = A.repere(TETE, (0, PENCHE, LACET))
    T3 = T.to_3x3()

    def tete_f(v):
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.90, -0.25, -0.35), 0.22, 0.30)
        return v * [0.115, 0.105, 0.100]
    tete = chaines(A.boule(1.0, 48, 24), 3.0, 14.0, ventre=None)
    tete.teinte[(tete.v[:, 1] < -0.45) & (tete.v[:, 2] < 0.0)] = BLANC
    # les marques du visage (photos de Commons), peintes à plat sur le poil, plus de tiges : deux barres sur chaque joue,
    # deux traits sur le front
    ax, ay, az = np.abs(tete.v[:, 0]), tete.v[:, 1], tete.v[:, 2]
    barre_haute = (ax > 0.62) & (az > -0.02) & (az < 0.15) & (ay < 0.30)
    barre_basse = (ax > 0.58) & (az > -0.40) & (az < -0.25) & (ay < 0.20)
    front = (ay < -0.12) & (az > 0.50) & (((ax > 0.10) & (ax < 0.19)) | ((ax > 0.30) & (ax < 0.39)))
    tete.teinte[barre_haute | barre_basse | front] = CHOCOLAT
    a.piece("tete", tete.sculpte(tete_f), None, mat=T)
    a.piece("museau", A.boule(1.0, 32, 16).etire(0.052, 0.046, 0.042), BLANC, mat=T @ A.repere((0, -0.096, -0.034)))
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.018, 0.012, 0.012), M.hexa("#d98a8a"), mat=T @ A.repere((0, -0.138, -0.016)), poil=False)
    a.tete = T @ Vector((0, -0.100, -0.004))
    for c in (1, -1):
        bouche = [T3 @ Vector(d) for d in ((c * 0.02, -0.55, -0.78), (c * 0.20, -0.64, -0.72), (c * 0.40, -0.58, -0.62))]
        a.broderie("bouche_" + ("G" if c > 0 else "D"),
                   A.courbe(propres(a.trace("museau", T @ Vector((0, -0.096, -0.034)), bouche, 0.004)), 4), 0.0026, CHOCOLAT)

    # ----- les yeux : grands, ronds, d'ambre, au regard doux (plus de traits froncés) -----
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.50, -0.82, 0.18))
        a.rustine("iris_" + nom, "tete", T.to_translation(), regard, 0.24, OEIL, 0.003, 0)       # un fin cercle d'ambre : plus de lunettes
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0215)
        E = A.cadre(T @ Vector((c * 0.080, 0.040, 0.070)), T3 @ Vector((c * 0.30, 0.22, 0.93)), T3 @ Vector((c * 0.4, -0.9, 0.0)))
        po = A.profil([(0, 0), (0.034, 0.008), (0.042, 0.030), (0.034, 0.052), (0.015, 0.066), (0, 0.072)], 5)
        a.piece("oreille_" + nom, A.tour(po, 28).etire(1.0, 0.42, 1.0), CHOCOLAT, mat=E)
        a.piece("tache_" + nom, A.tour(po, 20).etire(0.55, 0.30, 0.62).pose((0, 0.008, 0.006)), BLANC, mat=E, poil=False)

    # ----- les pattes de devant : deux piliers serrés, les pieds blancs, les griffes rentrées ; les hanches : deux jambons -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.070, -0.100, 0.350), (c * 0.075, -0.140, 0.190), (c * 0.075, -0.150, 0.045)]
        patte = K.tube_peint(A.courbe(chemin, 6), lambda t: 0.052 - 0.010 * t, [(0.76, SABLE), (1, BLANC)], 16)
        a.piece("patte_" + nom, patte, None)
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.050, 0.075, 0.032), BLANC, pos=(c * 0.075, -0.165, 0.032))
        h = chaines(A.boule(1.0, 32, 16), 5.0 + c, 12.0)
        a.piece("hanche_" + nom, h.etire(0.085, 0.130, 0.105), None, pos=(c * 0.125, 0.090, 0.130))

    # ----- la queue : annelée de chocolat, enroulée autour des pieds ; le bout noir -----
    chemin = [(0.0, 0.200, 0.110), (0.120, 0.250, 0.060), (0.230, 0.130, 0.050), (0.210, -0.040, 0.050), (0.120, -0.150, 0.050),
              (0.020, -0.130, 0.050)]
    bagues, f, c = [], 0.0, SABLE
    while f < 0.90:
        f += 0.11
        bagues.append((min(f, 0.90), c))
        c = CHOCOLAT if c is SABLE else SABLE
    bagues[-1] = (0.90, bagues[-1][1])
    bagues.append((1.0, M.hexa("#3a2a22")))
    queue = K.tube_peint(A.courbe(chemin, 6), lambda t: 0.052 - 0.014 * t, bagues, 14)
    a.piece("queue", queue, None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("ocelot", styles.style_de("ocelot"), sys.modules[__name__]), "Ocelot")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py ocelot). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.344                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.111, 0.133)),
    ('tete', 'corps', (0.008, -0.041, 0.517)),
    ('oreille_G', 'tete', (0.055, -0.012, 0.675)),
    ('patte_av_G', 'corps', (0.072, -0.118, 0.344)),
    ('queue', 'corps', (0.037, 0.184, 0.103)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('oreille', 'oreille', True), ('hanche', 'corps'), ('museau', 'tete'),
    ('truffe', 'corps'), ('bouche', 'tete'), ('corps', 'corps'), ('patte', 'patte_av', True), ('queue', 'queue'),
    ('tache', 'corps'), ('tete', 'tete'), ('pied', 'patte_av', True), ('iris', 'tete'), ('oeil', 'tete'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add('oreille_G', rot=(0, 0, 20 * cloche(t, 0.50, 0.05) - 8 * g))
    p.add('oreille_D', rot=(0, 0, -20 * cloche(t, 0.88, 0.05) + 6 * d))
    p.add('queue', rot=(0, 0, 10 * onde(t, 1)))
    p.ouvert = borne(1 - 0.3 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.62, 0.02))
    return p


def avance(t):
    """Sa marche : les pattes alternent, le corps oscille, la tête dodeline."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 18.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_av_D', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.paire('oreille', rot=(-8 + 3 * onde(t, 2, -0.25), 0, 0))
    p.add('queue', rot=(-6, 0, -10 * s))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(34 * bas + 3 * coups, 0, 0))
    p.paire('patte_av', rot=(-30 * bas, 0, 0))
    p.add('tete', rot=(16 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.paire('oreille', rot=(-6 * bas + 5 * leve, 0, 0))
    p.add('queue', rot=(0, 0, -7 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.103 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.02), rot=(36, 0, 6), ech=(1 + 0.010 * r, 1, 1 + 0.020 * r))
    p.paire('patte_av', rot=(-30, 0, 0))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
