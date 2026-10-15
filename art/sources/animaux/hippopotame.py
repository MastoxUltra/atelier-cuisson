"""L'hippopotame en peluche de magasin : un prune rosé saturé, un baril énorme qui traîne presque au sol, une tête
gigantesque tout en museau (deux grosses bosses de narines, la gueule large comme une valise, de petites oreilles rondes
et des yeux placés tout en haut qui dépassent comme des périscopes), quatre courtes colonnes à quatre sabots, une queue
en moignon. Le bâilleur : la gueule grande ouverte, rose vif dedans, deux grandes dents d'ivoire en bas, le corps posé
dans l'herbe, les yeux mi-clos de contentement.

    python hippopotame.py        fabrique la fiche art/apercus/animaux/hippopotame.png (peluche de magasin, palier 4)
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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
PRUNE = M.hexa("#b87898")                     # la dominante : prune rosé saturé
CLAIR = M.hexa("#e8b8c8")                     # le ventre, le tour du museau
ROSE = M.hexa("#ff8aa0")                      # l'intérieur de la gueule
IVOIRE = M.hexa("#fff4dc")                    # l'accent : les défenses
CHARBON = M.hexa("#4a3a40")
CORPS = Vector((0.0, 0.250, 0.380))
TETE = Vector((0.0, -0.560, 0.560))
LACET = 22.0


def construire():
    a = K.Animal("hippopotame")
    a.taille = 3.50

    # ----- le corps : un énorme baril bas, plus large que haut, qui frôle le sol ; plissé en travers -----
    def baril(v):
        s = v * [0.440, 0.700, 0.380]
        s[:, 2] = np.where(s[:, 2] < 0, s[:, 2] * 0.88, s[:, 2])
        return s
    corps = A.boule(1.0, 64, 32)
    t = np.tile(np.asarray(PRUNE, float), (len(corps.v), 1))
    t[corps.v[:, 2] < -0.55] = CLAIR
    t[(np.sin(13 * corps.v[:, 1]) > 0.88) & (corps.v[:, 2] < 0.5)] = M.hexa("#9a5a78")
    corps.teinte = t
    a.piece("corps", corps.sculpte(baril), None, pos=CORPS)

    # ----- la tête : un bloc énorme, le front plat ; les yeux en périscopes tout en haut ; le museau carré -----
    H = A.repere(TETE, (4, 0, LACET))
    H3 = H.to_3x3()

    def bloc(v):
        s = K.emousse(v, 0.74)
        return s * [0.420, 0.440, 0.300]
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(bloc), PRUNE, mat=H @ A.repere((0, -0.050, 0.0)))
    for c in (1, -1):
        n = "G" if c > 0 else "D"
        a.piece("narine_bosse_" + n, A.boule(1.0, 20, 10).etire(0.088, 0.070, 0.062), PRUNE, mat=H @ A.repere((c * 0.180, -0.470, 0.130)))
        a.piece("narine_" + n, A.boule(1.0, 14, 8).etire(0.032, 0.030, 0.020), CHARBON, mat=H @ A.repere((c * 0.180, -0.530, 0.150)), poil=False)
        # les yeux en périscopes : une bosse sur le dessus du crâne, l'œil dessus
        a.piece("globe_" + n, A.boule(1.0, 24, 12).etire(0.080, 0.080, 0.068), PRUNE, mat=H @ A.repere((c * 0.230, -0.150, 0.280)))
        p, nn = a.surface("globe_" + n, H @ Vector((c * 0.230, -0.150, 0.280)), H3 @ Vector((c * 0.50, -0.70, 0.50)))
        a.oeil("oeil_" + n, p + nn * 0.004, nn, 0.0340)
        # (paupière retirée : yeux ouverts, bouton net, sans air fatigué ni fâché)
        # les petites oreilles rondes derrière
        po = A.profil([(0, 0), (0.044, 0.010), (0.050, 0.032), (0.038, 0.054), (0.014, 0.064), (0, 0.068)], 5)
        a.piece("oreille_" + n, A.tour(po, 24).etire(1.0, 0.45, 1.0), PRUNE,
                mat=A.cadre(H @ Vector((c * 0.300, 0.150, 0.190)), H3 @ Vector((c * 0.45, 0.10, 0.88)), H3 @ Vector((c * 0.3, -0.9, 0.0))))
    a.tete = H @ Vector((0, -0.380, 0.0))

    # ----- la gueule : la mâchoire du bas, abaissée très loin ; l'intérieur rose ; deux grandes défenses d'ivoire en bas -----
    bas = A.boule(1.0, 48, 24).sculpte(lambda v: K.emousse(v, 0.78) * [0.380, 0.330, 0.110])
    a.piece("machoire", bas, PRUNE, mat=H @ A.repere((0, -0.230, -0.250), (18, 0, 0)))
    a.piece("gueule", A.boule(1.0, 36, 18).etire(0.330, 0.300, 0.060), ROSE, mat=H @ A.repere((0, -0.230, -0.130), (10, 0, 0)), poil=False)
    for c in (1, -1):
        n = "G" if c > 0 else "D"
        a.piece("defense_b_" + n, A.tour(A.profil([(0, 0), (0.034, 0.006), (0.028, 0.070), (0.014, 0.130), (0, 0.160)], 5), 18),
                IVOIRE, mat=H @ A.repere((c * 0.250, -0.350, -0.190), (-10, 0, 0)), poil=False)
        a.piece("defense_h_" + n, A.tour(A.profil([(0, 0), (0.030, 0.006), (0.024, 0.060), (0.012, 0.110), (0, 0.140)], 5), 18),
                IVOIRE, mat=H @ A.repere((c * 0.230, -0.360, -0.050), (170, 0, 0)), poil=False)

    # ----- les pattes : quatre colonnes courtes et larges, quatre sabots chacune ; la queue : un moignon -----
    for nom, x, y in (("av_G", 0.300, -0.300), ("av_D", -0.300, -0.300), ("ar_G", 0.310, 0.620), ("ar_D", -0.310, 0.620)):
        a.piece("patte_" + nom, A.tube(A.courbe([(x, y, 0.340), (x * 1.04, y - 0.010, 0.200), (x * 1.06, y - 0.020, 0.060)], 5), 0.150, 20), PRUNE)
        a.piece("pied_" + nom, A.boule(1.0, 28, 14).etire(0.168, 0.176, 0.056), CLAIR, pos=(x * 1.06, y - 0.040, 0.054))
        for k in (-1.5, -0.5, 0.5, 1.5):
            a.piece("sabot_%s_%s" % (nom, str(k)), A.boule(1.0, 10, 6).etire(0.034, 0.040, 0.038), CHARBON,
                    pos=(x * 1.06 + k * 0.070, y - 0.180, 0.040), poil=False)
    a.piece("queue", A.boule(1.0, 20, 10).etire(0.040, 0.100, 0.040), PRUNE, pos=(0, 0.940, 0.360), rot=(-12, 0, 0))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("hippopotame", styles.style_de("hippopotame"), sys.modules[__name__]), "Hippopotame")



# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py hippopotame). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.330                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.443, 0.471)),
    ('tete', 'corps', (0.042, -0.252, 0.382)),
    ('oreille_G', 'tete', (0.212, -0.341, 0.782)),
    ('patte_av_G', 'corps', (0.318, -0.313, 0.330)),
    ('patte_ar_G', 'corps', (0.328, 0.607, 0.330)),
    ('queue', 'corps', (-0.000, 0.848, 0.383)),
]

PORTEURS = [
    ('sabot_av_G_-1.5', 'patte_av_G'), ('sabot_av_G_-0.5', 'patte_av_G'), ('sabot_av_D_-1.5', 'patte_av_D'),
    ('sabot_av_D_-0.5', 'patte_av_D'), ('sabot_ar_G_-1.5', 'patte_ar_G'), ('sabot_ar_G_-0.5', 'patte_ar_G'),
    ('sabot_ar_D_-1.5', 'patte_ar_D'), ('sabot_ar_D_-0.5', 'patte_ar_D'), ('sabot_av_G_0.5', 'patte_av_G'),
    ('sabot_av_G_1.5', 'patte_av_G'), ('sabot_av_D_0.5', 'patte_av_D'), ('sabot_av_D_1.5', 'patte_av_D'),
    ('sabot_ar_G_0.5', 'patte_ar_G'), ('sabot_ar_G_1.5', 'patte_ar_G'), ('sabot_ar_D_0.5', 'patte_ar_D'),
    ('sabot_ar_D_1.5', 'patte_ar_D'), ('narine_bosse', 'tete'), ('oeil_reflet', 'tete'), ('defense_b', 'tete'),
    ('defense_h', 'tete'), ('machoire', 'corps'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True),
    ('oreille', 'oreille', True), ('pied_av', 'patte_av', True), ('pied_ar', 'patte_ar', True), ('lourde', 'tete'),
    ('narine', 'tete'), ('gueule', 'corps'), ('corps', 'corps'), ('globe', 'corps'), ('queue', 'queue'),
    ('tete', 'tete'), ('oeil', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
    ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    pas = 26.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
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
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.099 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.181), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
