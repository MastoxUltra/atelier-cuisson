"""Le bœuf musqué en peluche de magasin : un brun encre, presque noir, qui disparaît sous sa propre laine : une grande
jupe de poils qui lui tombe jusqu'aux chaussettes crème, la bosse des épaules, une selle crème sur le dos, la tête
basse sous un casque de cornes ivoire (le bouclier du front, puis les cornes qui descendent le long des joues et
remontent à la pointe). Un mur de laine, têtu, qui n'a rien à prouver : il vous regarde par en dessous, sans bouger.

    python boeuf_musque.py        fabrique la fiche art/apercus/animaux/boeuf_musque.png (peluche de magasin, palier 4)
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
ENCRE = M.hexa("#5d463c")                     # la dominante : brun encre (le poil le fonce presque jusqu'au noir : on le prend plus clair)
SOUS = M.hexa("#3a2b26")                      # le dessous de la jupe, les mèches du bas
CREME = M.hexa("#fff0d2")                     # les chaussettes
SELLE = M.hexa("#d6bd96")                     # la selle : un beige pâle, comme la référence (crème, elle faisait une tache)
IVOIRE = M.hexa("#efe2c4")                    # l'accent : les cornes, un ivoire chaud (la référence : corne claire)
CORNE = M.hexa("#cdb78c")                     # le bout des cornes, les sabots
NEZ = M.hexa("#a08a78")                       # le museau : pâle, comme le vrai (le visage se lit enfin)
# (16/10, planche 27 : l'auteur veut les proportions d'un vrai modèle) : relevées sur la référence (references_3d/boeuf_musque,
# CC-BY, la (3) importée en pose de repos : mesurée, rien d'importé) : un long corps, la bosse haute sur les épaules, la
# croupe à peine plus basse, la jupe jusqu'à mi-jambe, la tête basse devant les épaules
CORPS = Vector((0.0, 0.060, 0.370))
TETE = Vector((0.0, -0.400, 0.340))
LACET, PIQUE = 24.0, -6.0                    # la tête tournée vers nous, le nez baissé


def meche(chemin, large, face, plat=0.36, long_pointe=0.93, cotes=18):
    """Une mèche plate (le geste du cheval et du renne) : un fuseau tourné, aplati, couché le long d'un chemin ;
    « face » : la direction de son épaisseur (on la voit de plat depuis là)."""
    p = A.courbe(chemin, 8)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    n0 = np.asarray(face, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.linalg.norm(t, axis=1, keepdims=True)
        x = np.cross(n0, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.60 * large, 0.05 * L), (0.95 * large, 0.22 * L), (large, 0.42 * L), (0.72 * large, 0.70 * L),
                     (0.30 * large, long_pointe * L), (0.06 * large, 0.985 * L), (0, L)], 5)
    return A.tour(prof, cotes).etire(1.0, plat, 1.0).sculpte(couche)


def construire():
    a = K.Animal("boeuf_musque")
    a.taille = 2.40

    # ----- le corps : une masse ronde, la bosse haute sur les épaules, la croupe basse -----
    def masse(v):
        v = K.bosse(v, (0, -0.50, 0.80), 0.40, 0.42)                  # la grosse bosse des épaules
        s = v * [0.205, 0.420, 0.200]
        s[:, 2] *= 1 - 0.16 * K.lisse((v[:, 1] - 0.0) / 1.0)           # la croupe un peu plus basse (le modèle : 0,55 contre 0,65)
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(masse), ENCRE, pos=CORPS)
    # la selle crème : un large pan sur le dos, derrière la bosse
    a.rustine("selle", "corps", CORPS + Vector((0, 0.00, 0.0)), (0, 0.25, 1.0), lambda th: 0.46 - 0.10 * math.cos(2 * th), SELLE, 0.004, 0)

    # ----- la jupe de poils : une trentaine de longues mèches plates, nées du flanc, qui tombent en s'évasant jusqu'à
    #       mi-jambe, une sur deux plus sombre (le geste des fanons du cheval) -----
    rng = np.random.default_rng(7)
    claires, sombres = None, None
    for i in range(36):
        t = 2 * math.pi * (i + rng.uniform(-0.25, 0.25)) / 36
        base = np.array([0.197 * math.cos(t), CORPS.y + 0.403 * math.sin(t)])
        radial = np.array([math.cos(t) * 1.0, math.sin(t) * 0.62])
        radial /= np.linalg.norm(radial)
        k = 0.85 + 0.40 * rng.random() + 0.18 * max(0.0, -math.sin(t))                # plus longues devant, là où il est plus laineux
        z0 = CORPS.z - 0.03
        chemin = [(base[0] * 0.94, base[1] * 0.94 + CORPS.y * 0.06, z0 + 0.04),
                  (base[0] + radial[0] * 0.010, base[1] + radial[1] * 0.010, z0 - 0.07),
                  (base[0] + radial[0] * 0.040, base[1] + radial[1] * 0.040, z0 - 0.135 * k),
                  (base[0] + radial[0] * 0.062, base[1] + radial[1] * 0.062, z0 - 0.200 * k)]
        m = meche(chemin, 0.054 + 0.010 * rng.random(), (radial[0], radial[1], 0.0), 0.40)
        if i % 2:
            sombres = m if sombres is None else sombres + m
        else:
            claires = m if claires is None else claires + m
    a.piece("meches_a", claires, ENCRE)
    a.piece("meches_b", sombres, SOUS)

    # ----- les chaussettes crème : quatre jambes courtes qui dépassent de la jupe, les sabots corne -----
    for nom, x, y in (("av_G", 0.110, -0.170), ("av_D", -0.110, -0.170), ("ar_G", 0.115, 0.300), ("ar_D", -0.115, 0.300)):
        a.piece("jambe_" + nom, A.tube(A.courbe([(x, y, 0.300), (x, y - 0.004, 0.150), (x, y - 0.010, 0.040)], 5), 0.058, 16), CREME)
        a.piece("sabot_" + nom, A.boule(1.0, 24, 12).etire(0.056, 0.066, 0.036), CORNE, pos=(x, y - 0.014, 0.026), poil=False)

    # ----- la tête : longue, lourde, penchée ; le museau pâle bien en vue, des poils longs sur les joues -----
    H = A.repere(TETE, (PIQUE, 0, LACET))
    H3 = H.to_3x3()

    def tete_f(v):
        s = v.copy()
        s[:, 0] *= 0.66 + 0.10 * K.lisse((-v[:, 1] + 0.1) / 0.9)
        s = K.bosse(s, (0, -1, -0.2), 0.12, 0.35)
        return s * [0.172, 0.200, 0.150]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(tete_f), SOUS, mat=H)
    a.piece("museau", A.boule(1.0, 36, 18).etire(0.068, 0.084, 0.060), NEZ, mat=H @ A.repere((0, -0.165, -0.050)))
    a.piece("nez", A.boule(1.0, 24, 12).etire(0.040, 0.026, 0.030), CORNE, mat=H @ A.repere((0, -0.245, -0.050)), poil=False)
    a.tete = H @ Vector((0, -0.200, -0.040))

    # ----- les yeux : ronds et vivants, au regard calme, sous la corne (plus de paupière lourde) -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.42, -0.88, 0.06)))     # devant, sous le casque : de côté, la corne les cachait
        a.oeil("oeil_" + nom, p + n * 0.012, n, 0.0360)

    # ----- le casque de cornes : le bouclier ivoire sur le front, puis la corne qui descend le long de la joue et
    #       remonte, la pointe corne tournée vers l'avant -----
    a.piece("bouclier", A.boule(1.0, 36, 16).etire(0.125, 0.085, 0.034), IVOIRE, mat=H @ A.repere((0, -0.040, 0.118), (-10, 0, 0)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [H @ Vector(q) for q in ((c * 0.100, -0.030, 0.110), (c * 0.170, -0.020, 0.085), (c * 0.205, -0.030, 0.000),
                                         (c * 0.205, -0.085, -0.075), (c * 0.180, -0.140, -0.060), (c * 0.165, -0.175, 0.010))]
        corne = K.tube_peint(A.courbe(chemin, 6), lambda t: 0.002 + 0.029 * (1 - t) ** 0.8, [(0.62, IVOIRE), (1, CORNE)], 18)   # la pointe fine (coupée net, elle faisait tube : 16/10)
        a.piece("corne_" + nom, corne, None, poil=False)

    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("boeuf_musque", styles.style_de("boeuf_musque"), sys.modules[__name__]), "Bœuf musqué")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py boeuf_musque). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.294                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.235, 0.335)),
    ('tete', 'corps', (-0.042, -0.268, 0.321)),
    ('patte_av_G', 'corps', (0.120, -0.261, 0.294)),
    ('patte_ar_G', 'corps', (0.130, 0.309, 0.294)),
]

PORTEURS = [
    ('meches_a', 'corps'), ('jambe_av', 'patte_av', True), ('jambe_ar', 'patte_ar', True), ('meches_b', 'corps'),
    ('sabot_av', 'patte_av', True), ('sabot_ar', 'patte_ar', True), ('bouclier', 'corps'), ('lourde', 'tete'),
    ('museau', 'tete'), ('corps', 'corps'), ('selle', 'corps'), ('corne', 'tete'), ('tete', 'tete'), ('oeil', 'tete'),
    ('nez', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'),
    ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
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
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.088 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.162), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
