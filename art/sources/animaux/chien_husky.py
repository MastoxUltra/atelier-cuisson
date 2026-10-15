"""Le chien en peluche, la race husky (le teckel, chien.py, reste la robe de base du chien). Un loup de velours gris,
la selle et la calotte ardoise, tout le dessous blanc ; le masque blanc dessiné comme au pochoir, la pointe grise qui
descend entre les yeux, deux taches blanches en guise de sourcils, des lunettes grises autour de deux yeux bleu
glacier. Les oreilles en triangles épais, dressées haut et serrées ; la queue en panache roulée sur le dos, le bout
blanc posé sur l'échine. Il est en pleine tirade : campé sur ses quatre pattes, le poitrail bombé, il lève le museau,
ouvre la gueule et rouspète, la tête penchée, un œil bleu planté dans le vôtre. Le grand bavard du village.

    python chien_husky.py        fabrique la fiche art/apercus/animaux/chien_husky.png
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

GRIS = M.hexa("#aab0b8")                      # le manteau : un gris loup (le poil le fonce)
ARDOISE = M.hexa("#6c727b")                   # la selle, la calotte, les lunettes, le dos des oreilles, la queue
BLANC = M.hexa("#f8f8f4")                     # le masque, le ventre, les pattes, le bout de la queue
GLACIER = M.hexa("#8ed4f6")                   # l'accent : les yeux bleu glacier (et le fil du rapiéçage)
GORGE = M.hexa("#5a2f3a")                     # le fond de la gueule
TOURNE = 0                                    # -30 pour la fiche, posé de biais (on lit sa longueur) ; 0 pour le jeu
CORPS = Vector((0.0, 0.040, 0.300))
LARGE, LONG, HAUT = 0.090, 0.250, 0.094       # les demi-mesures du corps
TETE = Vector((0.010, -0.290, 0.535))
PORT = A.repere(TETE, (-26, 12, 20))          # le museau levé, la tête penchée, tournée vers vous : il rouspète
OEIL = (0.48, -0.76, 0.30)                    # la direction de l'œil gauche, dans le repère de la tête


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du village."""
    return PORT.to_3x3() @ Vector((x, y, z))


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def unite(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def epouse(v):
    """Pour sculpte() : le bas d'une oreille s'incurve pour épouser le crâne."""
    s = v.copy()
    s[:, 2] -= v[:, 0] ** 2 / 0.17 * (1 - K.lisse(v[:, 2] / 0.05))
    return s


def patte(chemin, blanc_depuis):
    """Une patte de coureur : le velours gris en haut, blanche à partir de la fraction « blanc_depuis » du chemin."""
    return K.tube_peint(A.courbe(chemin, 5), lambda t: 0.031 - 0.006 * t, [(blanc_depuis, GRIS), (9, BLANC)], 16)


def construire():
    a = K.Animal("chien_husky")
    a.taille = 1.05
    a.tete = PORT @ Vector((0.0, -0.110, -0.016))

    # ----- le corps : un coureur de traîneau, le poitrail bombé, la croupe ferme ; selle ardoise, flancs gris, dessous
    #       blanc qui monte sur le poitrail -----
    def coque(v):
        y = v[:, 1]
        rond = np.sqrt(np.maximum(1 - y * y, 1e-9))
        boudin = np.maximum(1 - np.abs(y) ** 2.4, 0.0) ** (1 / 2.4)
        k = boudin / rond
        s = np.stack([v[:, 0] * k, y, v[:, 2] * k], axis=1)
        s = K.bosse(s, (0, -0.70, -0.55), 0.26, 0.22)                 # le poitrail bombé
        s = K.bosse(s, (0, 0.80, 0.35), 0.08, 0.22)                   # la croupe
        s = K.bosse(K.bosse(s, (0.85, -0.50, -0.10), 0.05, 0.10), (-0.85, -0.50, -0.10), 0.05, 0.10)   # les épaules
        avant = K.lisse((-s[:, 1] - 0.1) / 0.8)
        arriere = K.lisse((s[:, 1] + 0.1) / 0.9)
        s = s * [LARGE, LONG, HAUT]
        s[:, 0] *= 1 + 0.08 * avant - 0.06 * arriere
        s[:, 2] *= np.where(s[:, 2] < 0, 1 + 0.10 * avant - 0.30 * arriere, 1.0)
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    cv = corps.v
    dessous = cv[:, 2] < -0.032 + 0.100 * K.lisse((-cv[:, 1] - 0.12) / 0.13)
    selle = cv[:, 2] > 0.052
    corps.teinte = np.where(dessous[:, None], np.asarray(BLANC), np.where(selle[:, None], np.asarray(ARDOISE), np.asarray(GRIS)))
    G.sillons(corps, [14, 42], 0.005, 1.1)
    a.piece("corps", corps, None, pos=CORPS, rot=(-3, 0, 0))
    a.couture("dos", "corps", 14, 0.60, 0.99, fil=BLANC)
    a.couture("echine", "corps", 42, 0.80, 0.99, fil=BLANC)
    a.rustine("rapiecage", "corps", CORPS + Vector((0, -0.08, 0.0)), (1.0, -0.10, 0.20),
              lambda th: 0.24 + 0.04 * math.cos(3 * th) + 0.03 * math.sin(2 * th), ARDOISE, feston=16, fil=GLACIER)

    # ----- le cou : épais comme une collerette, ardoise sur la nuque, blanc devant -----
    fil_cou = K.Fil([(0.0, -0.140, 0.335), (0.003, -0.215, 0.425), (0.008, -0.265, 0.495)], flanc=(1, 0, 0))
    cou = A.tour(A.profil([(0, -0.02), (0.084, 0.0), (0.082, 0.07), (0.072, 0.14), (0.064, 0.19), (0, 0.225)], 5), 32)
    cou.teinte = np.where((cou.v[:, 1] < -0.015)[:, None], np.asarray(BLANC), np.asarray(ARDOISE))
    a.piece("cou", cou.sculpte(fil_cou.couche), None)

    # ----- la tête : un crâne de loup, les joues pleines ; le masque blanc, la calotte ardoise et sa pointe entre les
    #       yeux, les lunettes ardoise autour des yeux, les deux taches blanches au-dessus -----
    def crane(v):
        v = K.bosse(v, (0, -0.50, 0.85), 0.08, 0.25)                 # le front
        v = K.bosse(K.bosse(v, (0.80, -0.40, -0.30), 0.10, 0.22), (-0.80, -0.40, -0.30), 0.10, 0.22)   # les joues
        return v * [0.086, 0.090, 0.080]
    tete = A.boule(1.0, 56, 28).sculpte(crane)
    u = tete.v / np.array([0.086, 0.090, 0.080])
    u /= np.maximum(np.linalg.norm(u, axis=1, keepdims=True), 1e-9)
    calotte = u[:, 2] > 0.30 - 0.30 * np.maximum(u[:, 1], 0.0)
    pointe = (np.abs(u[:, 0]) < 0.09 + 0.35 * np.maximum(u[:, 2], 0.0)) & (u[:, 1] < 0) & (u[:, 2] > -0.12)
    sombre = calotte | pointe | (u[:, 1] > 0.10)
    for c in (1, -1):
        oeil = unite((OEIL[0] * c, OEIL[1], OEIL[2]))
        tache = unite((0.30 * c, -0.66, 0.68))
        sombre |= np.linalg.norm(u - oeil, axis=1) < 0.30
        sombre &= np.linalg.norm(u - tache, axis=1) > 0.15
    tete.teinte = np.where(sombre[:, None], np.asarray(ARDOISE), np.asarray(BLANC))
    a.piece("tete", tete, None, mat=PORT)
    a.couture("crane", "tete", 14, 0.55, 0.97, fil=BLANC)

    # ----- le museau : blanc, l'arête ardoise ; la gueule ouverte sur la tirade : la mâchoire tombe, le fond sombre ;
    #       la truffe noire -----
    MU = PORT @ A.repere((0, -0.050, -0.030), (98, 0, 0))     # dans ce repère : X la gauche, Y le haut, Z vers la truffe
    museau = A.tour(A.profil([(0, -0.015), (0.058, 0.0), (0.054, 0.04), (0.044, 0.085), (0.035, 0.115), (0.028, 0.135),
                              (0, 0.148)], 6), 40)
    museau.etire(1.0, 0.80, 1.0)
    angle = np.degrees(np.arctan2(museau.v[:, 1], museau.v[:, 0]))
    arete = (np.abs(angle - 90) < 20) & (museau.v[:, 2] < 0.075)
    palais = (np.abs(angle + 90) < 40) & (museau.v[:, 2] > 0.075)
    museau.teinte = np.where(arete[:, None], np.asarray(ARDOISE), np.where(palais[:, None], np.asarray(GORGE), np.asarray(BLANC)))
    a.piece("museau", museau, None, mat=MU)
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.024, 0.017, 0.016), K.NOIR, mat=MU @ A.repere((0, 0.005, 0.142)), poil=False)
    machoire = A.tour(A.profil([(0, -0.012), (0.042, 0.0), (0.040, 0.035), (0.033, 0.075), (0.025, 0.100), (0, 0.112)], 6), 32)
    machoire.etire(1.0, 0.58, 1.0)
    ang = np.degrees(np.arctan2(machoire.v[:, 1], machoire.v[:, 0]))
    machoire.teinte = np.where(((np.abs(ang - 90) < 50) & (machoire.v[:, 2] > 0.050))[:, None], np.asarray(GORGE), np.asarray(BLANC))
    a.piece("machoire", machoire, None, mat=MU @ A.repere((0, -0.030, 0.010), (20, 0, 0)))
    a.piece("gorge", A.boule(1.0, 24, 12).etire(0.026, 0.014, 0.036), GORGE, mat=MU @ A.repere((0, -0.034, 0.088)), poil=False)

    # ----- les yeux : un iris de feutrine bleu glacier, la pupille vivante par-dessus -----
    for nom, c in (("G", 1), ("D", -1)):
        d = vers(OEIL[0] * c, OEIL[1], OEIL[2])
        a.rustine("iris_" + nom, "tete", TETE, d, 0.16, GLACIER, 0.0025, 0)
        p, n = a.surface("tete", TETE, d)
        a.oeil("oeil_" + nom, p + n * 0.0035, n, 0.0085)

    # ----- les oreilles : deux triangles épais, dressés haut et serrés, le dos ardoise, le creux blanc -----
    po = A.profil([(0, 0), (0.040, 0.010), (0.043, 0.028), (0.032, 0.062), (0.015, 0.092), (0, 0.104)], 6)
    for nom, c in (("G", 1), ("D", -1)):
        m = A.tour(po, 32).etire(1.0, 0.40, 1.0)
        creux = (m.v[:, 1] > 0.004) & (np.abs(m.v[:, 0]) < 0.028 - 0.22 * m.v[:, 2]) & (m.v[:, 2] > 0.008)
        m.teinte = np.where(creux[:, None], np.asarray(BLANC), np.asarray(ARDOISE))
        m.sculpte(epouse)
        p, n = a.surface("tete", TETE, vers(0.42 * c, 0.04, 0.90))
        dresse = vers(0.30 * c, -0.08, 0.95).normalized()
        a.piece("oreille_" + nom, m, None, mat=A.cadre(p - dresse * 0.018, dresse, vers(0, -1, 0.12)))

    # ----- les pattes : campé, les pattes avant un peu écartées, la droite avancée ; gris en haut, blanc en bas -----
    a.piece("patte_avant_G", patte([(0.052, -0.150, 0.275), (0.062, -0.165, 0.150), (0.070, -0.172, 0.060), (0.074, -0.176, 0.020)], 0.35), None)
    a.piece("pied_avant_G", A.boule(1.0, 24, 12).etire(0.034, 0.043, 0.017).pose((0.076, -0.190, 0.0168), (0, 0, 10)), BLANC)
    a.piece("patte_avant_D", patte([(-0.052, -0.150, 0.275), (-0.060, -0.180, 0.150), (-0.066, -0.200, 0.060), (-0.068, -0.208, 0.020)], 0.35), None)
    a.piece("pied_avant_D", A.boule(1.0, 24, 12).etire(0.034, 0.043, 0.017).pose((-0.069, -0.222, 0.0168), (0, 0, -10)), BLANC)
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.boule(1.0, 32, 16).etire(0.046, 0.072, 0.076), GRIS, pos=(0.064 * c, 0.200, 0.248), rot=(-22, 0, 0))
        a.piece("patte_arriere_" + nom, patte([(0.060 * c, 0.210, 0.300), (0.070 * c, 0.170, 0.180), (0.072 * c, 0.262, 0.090),
                                               (0.072 * c, 0.248, 0.020)], 0.45), None)
        a.piece("pied_arriere_" + nom, A.boule(1.0, 24, 12).etire(0.033, 0.042, 0.017).pose((0.073 * c, 0.234, 0.0168), (0, 0, 6 * c)), BLANC)

    # ----- la queue : un gros panache qui monte de la croupe, roule par-dessus le dos et vient poser son bout blanc
    #       sur l'échine, du côté qu'il nous tend -----
    queue = K.tube_peint(A.courbe([(0.0, 0.250, 0.340), (0.0, 0.300, 0.400), (0.006, 0.292, 0.462), (0.022, 0.240, 0.490),
                                   (0.038, 0.185, 0.455), (0.044, 0.150, 0.388)], 6),
                         lambda t: 0.024 + 0.020 * math.sin(math.pi * t) - 0.008 * t, [(0.72, ARDOISE), (9, BLANC)], 18)
    a.piece("queue", queue, None)
    if TOURNE:
        tourner(a, TOURNE)
    return a


if __name__ == "__main__":
    K.planche(construire, "Husky")
