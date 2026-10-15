"""Le manchot en peluche (2e dessin, après la relecture de la session Animaux) : un manchot empereur haut et fier, une
seule pièce de velours ras du ventre à la tête (le cou étiré se fond dans le crâne : pas de boule posée dessus), le dos
ardoise qui descend en pointe sur les flancs, le plastron crème qui se dore d'abricot vers la gorge, la tête noire, une
grande tache mandarine derrière l'œil qui coule le long du cou, un long bec fin recourbé à la mandibule mandarine.
Cambré en arrière comme un chanteur d'opéra, le menton haut, le bec de trois quarts, une aile décollée et l'autre
tombante : il se pavane.

    python manchot.py        fabrique la fiche art/apercus/animaux/manchot.png (velours ras, palier 3)
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

DOS = M.hexa("#4b5873")                       # la dominante : bleu nuit ardoise (le rendu la bleuit : on la prend grise)
TETE_C = M.hexa("#2a3250")                    # la tête et la nuque : plus sombre
NUIT = M.hexa("#1f2640")                      # le liseré du plastron, le dessus du bec
CREME = M.hexa("#fffaf0")                     # le plastron
ABRICOT = M.hexa("#ffd08e")                   # le haut du plastron se dore en approchant de la gorge
MANDARINE = M.hexa("#ff922a")                 # l'accent : la tache de l'oreille, la mandibule du bas
ENCRE = M.hexa("#2a2f40")                     # les pieds, en feutrine
# le fil du corps, des pieds à la tête, vu de profil : (recul, hauteur). Cambré : le haut part en arrière, le jabot en avant
FIL = [(0.030, 0.00), (0.050, 0.14), (0.052, 0.34), (0.040, 0.56), (0.016, 0.74), (-0.020, 0.88)]
YAW = 38.0                                    # le bec de trois quarts, tourné vers sa gauche (vers nous)


def peindre(m, L, liser=0.13, eps=0.012):
    """Peint le corps (une pièce tournée encore droite, de 0 en bas à L en haut) : le dos et la tête sombres, le plastron
    crème qui se resserre vers la gorge et se dore d'abricot, cerné d'un liseré. Les méridiens de chaque anneau sont
    tournés pour tomber pile sur les bords : la limite reste nette sur le tissu comme sur le poil."""
    cotes = 56
    demi, devant = cotes // 2, 3 * cotes // 4                      # le méridien 42 sur 56 regarde droit devant (-Y)
    n1, n2 = 9, 2
    m.teinte = np.tile(np.asarray(DOS, float), (len(m.v), 1))
    for anneau in m.anneaux:
        if len(anneau) < 2:
            continue
        h = m.v[anneau[0], 2] / L
        w = float(np.interp(h, [0.0, 0.10, 0.22, 0.40, 0.58, 0.74, 0.86, 1.0], [1.95, 1.70, 1.42, 1.02, 0.64, 0.42, 0.30, 0.30]))
        ecart = np.concatenate([np.linspace(0.0, w - eps, n1 + 1), np.linspace(w + eps, w + liser - eps, n2),
                                np.linspace(w + liser + eps, math.pi, demi - n1 - n2)])
        r = np.hypot(m.v[anneau, 0], m.v[anneau, 1])
        for j, i in enumerate(anneau):
            k = (j - devant) % cotes
            signe = 1.0 if k <= demi else -1.0
            k = min(k, cotes - k)
            m.v[i, 0], m.v[i, 1] = r[j] * math.sin(signe * ecart[k]), -r[j] * math.cos(ecart[k])
            if h > 0.82:
                m.teinte[i] = ABRICOT if (h < 0.875 and k <= 1) else TETE_C   # la tête noire, la gorge abricot au milieu
            elif k <= n1:
                d = float(K.lisse((h - 0.35) / 0.45))
                m.teinte[i] = np.asarray(CREME) * (1 - d) + np.asarray(ABRICOT) * d
            elif k <= n1 + n2:
                m.teinte[i] = NUIT
    return m


def construire():
    a = K.Animal("manchot")
    a.taille = 0.95

    # ----- le corps, la nuque et la tête : une seule chaussette couchée le long d'un fil cambré ; le cou s'étire, le crâne
    #       s'y fond -----
    fil = K.Fil([(0.0, y, z) for y, z in FIL], (1, 0, 0))
    L = fil.long
    pc = A.profil([(0, 0), (0.060, 0.012 * L), (0.150, 0.06 * L), (0.172, 0.20 * L), (0.168, 0.36 * L), (0.134, 0.52 * L),
                   (0.098, 0.64 * L), (0.080, 0.72 * L), (0.076, 0.79 * L), (0.086, 0.855 * L), (0.090, 0.915 * L),
                   (0.066, 0.968 * L), (0, L)], 6)
    corps = A.tour(pc, 56)
    peindre(corps, L)
    a.piece("corps", corps.sculpte(fil.couche), None)
    centre, avant, nuque = fil.cadre(0.90 * L)
    C = Vector(centre)
    a.tete = C + Vector((math.sin(math.radians(YAW)) * -0.08, -math.cos(math.radians(YAW)) * 0.08, 0.0))

    # ----- la tache mandarine derrière l'œil, qui coule le long du cou ; l'œil, petit, sous une paupière lourde -----
    vers = lambda c: Vector((c * 0.88, -0.30, 0.0))
    for nom, c in (("G", 1), ("D", -1)):
        a.rustine("oreille_" + nom, "corps", C + Vector((0, 0, -0.010)), vers(c),
                  lambda th: 0.30 + 0.38 * max(0.0, math.sin(th)) ** 1.4, MANDARINE, 0.003, 0)
        p, n = a.surface("corps", C + Vector((0, 0, 0.012)), Vector((c * 0.78, -0.62, 0.12)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0150)
        # (paupière retirée : yeux ouverts, bouton net, sans air fatigué ni fâché)

    # ----- le bec : long, fin, recourbé vers le bas à la pointe ; le dessus noir, la mandibule mandarine dessous -----
    y = math.radians(YAW)
    avant_bec = Vector((math.sin(y), -math.cos(y), 0.30)).normalized()
    B = A.cadre(C + Vector((math.sin(y), -math.cos(y), 0.0)) * 0.072 + Vector((0, 0, 0.004)), avant_bec, Vector((0, 0, 1)))

    def courbe_(v):
        s = v.copy()
        s[:, 1] -= 0.030 * np.clip(v[:, 2] / 0.230, 0, 1) ** 2.2             # la pointe se recourbe
        return s
    dessus = A.tour(A.profil([(0, 0), (0.024, 0.006), (0.021, 0.060), (0.014, 0.130), (0.008, 0.190), (0.003, 0.226), (0, 0.236)], 6), 28)
    a.piece("bec", dessus.etire(0.72, 1.0, 1.0).sculpte(courbe_), NUIT, mat=B, poil=False)
    dessous = A.tour(A.profil([(0, 0), (0.019, 0.006), (0.016, 0.060), (0.010, 0.120), (0.004, 0.170), (0, 0.186)], 6), 24)
    a.piece("mandibule", dessous.etire(0.66, 0.70, 1.0).pose((0, -0.017, 0.0)).sculpte(courbe_), MANDARINE, mat=B, poil=False)

    # ----- les ailerons : de longues lames fines, bleu nuit dessus et crème dessous, la gauche décollée du corps comme
    #       pour se pavaner, la droite qui tombe le long du flanc -----
    for nom, c, epaule, sens in (("G", 1, (0.150, 0.050, 0.520), (0.78, 0.18, -0.35)),
                                 ("D", -1, (-0.150, 0.060, 0.515), (-0.34, 0.12, -0.93))):
        aile = A.boule(1.0, 40, 20)
        t = np.tile(np.asarray(CREME, float), (len(aile.v), 1))
        t[c * aile.v[:, 0] > 0.30] = DOS
        aile.teinte = t

        def lame(v, c=c):
            z = v[:, 2]
            s = v.copy()
            s[:, 1] *= (0.70 + 0.30 * K.lisse((z + 1) / 0.7)) * (1 - 0.62 * K.lisse((z + 0.1) / 1.1))
            s[:, 1] += 0.22 * K.lisse(z) ** 2                                      # la pointe s'affine et se recourbe
            s = s * [0.018, 0.062, 0.205]
            s[:, 0] += c * 0.014 * (1 - z ** 2)
            return s
        W = A.cadre(Vector(epaule), Vector(sens), A.tourne(sens, c * 30, Vector((0, -1, 0))))
        a.piece("aile_" + nom, aile.sculpte(lame).pose((0, 0, 0.180)), None, mat=W)

    # ----- les pieds : de grandes palmes de feutrine à trois doigts, plantées en canard sous le ventre -----
    for nom, pos, cap in (("G", (0.092, -0.115, 0.0), 20.0), ("D", (-0.092, -0.095, 0.0), -16.0)):
        pied = A.boule(1.0, 24, 12).etire(0.048, 0.060, 0.022).pose((0, -0.010, 0.022))
        for ang in (-28, 0, 28):
            pied = pied + A.boule(1.0, 20, 10).etire(0.021, 0.054, 0.017).pose((0, -0.048, 0.017)).pose((0, 0, 0), (0, 0, ang))
        pied = pied + A.tube(A.courbe([(0, 0.020, 0.020), (0, 0.040, 0.100), (0, 0.050, 0.150)], 6), lambda t: 0.036 - 0.006 * t, 14)
        a.piece("pied_" + nom, pied.pose(pos, (0, 0, cap)), ENCRE, poil=False)

    # ----- la queue : un petit coin raide qui touche le sol derrière (il s'y appuie) -----
    a.piece("queue", A.boule(1.0, 24, 12).etire(0.050, 0.120, 0.024), DOS, pos=(0, 0.240, 0.042), rot=(-16, 0, 0))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("manchot", styles.style_de("manchot"), sys.modules[__name__]), "Manchot")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py manchot). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.141                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.119, 0.130)),
    ('tete', 'corps', (0.050, -0.060, 0.790)),
    ('oreille_G', 'tete', (0.077, -0.045, 0.793)),
    ('patte_av_G', 'corps', (0.077, -0.073, 0.141)),
    ('aile_G', 'corps', (0.148, 0.057, 0.534)),
    ('queue', 'corps', (-0.000, 0.134, 0.077)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('mandibule', 'corps'), ('oreille', 'oreille', True), ('lourde', 'tete'),
    ('corps', 'corps'), ('queue', 'queue'), ('aile', 'aile', True), ('oeil', 'tete'), ('pied', 'patte_av', True),
    ('bec', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'),
    ('cil_1', 'paupiere_1'),
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
    p.paire('aile', rot=(0, -3 * cloche(t, 0.55, 0.06), 0))
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
    p.paire('aile', rot=(0, -2 + 2 * onde(t, 2), 0))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.042 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    p.paire('aile', rot=(0, -48 * vol, 0))
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
