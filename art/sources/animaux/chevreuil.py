"""Le chevreuil en peluche : une chevrette (sans bois, c'est voulu : ses oreilles lui font une couronne, et sa
silhouette ne se confond pas avec celle du cerf). Toute en nerfs et aux aguets : elle a entendu quelque chose. Un petit
corps de velours sable rosé, la croupe plus haute que le garrot, l'arrière-main ramassé sous elle comme un ressort ;
l'antérieur gauche levé, plié net, le sabot pendu : elle va taper du pied, ou bondir. Le cou dressé, la tête tournée
vers nous, les deux immenses oreilles en cornet braquées sur le bruit, l'une devant, l'autre de côté, la pointe noire.
Le chanfrein plus foncé, le bout du museau et la truffe noirs, une bande blanche sous le nez, le menton et la gorge
blancs ; sur la croupe, le grand miroir blanc, et dessous son pinceau. Des pattes interminables et fines.

    python chevreuil.py        fabrique la fiche art/apercus/animaux/chevreuil.png (style C, velours ras : palier 3)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import matieres as M
import peluche as K

SABLE = M.hexa("#dcbca4")                     # la robe : sable rosé
FONCE = M.hexa("#ad8571")                     # le chanfrein, le bas des jambes
PALE = M.hexa("#f2e6da")                      # le ventre
BLANC = M.hexa("#fbf8f3")                     # le miroir, le menton, la gorge, le dedans des oreilles
NOIR = M.hexa("#2a2223")                      # l'accent : la truffe, le bout du museau, la pointe des oreilles, les sabots
TOURNE = 0                                    # -20 pour la fiche (elle pose de trois quarts) ; 0 pour le jeu
CROUPE = Vector((0.0, 0.240, 0.625))          # le bout arrière du corps (une pièce tournée, couchée vers l'avant)
CABRE = -7.0                                  # la croupe plus haute que le garrot
COL = math.radians(18)                        # le cou part un peu vers sa gauche, du côté où elle regarde
AVANT = Vector((math.sin(COL), -math.cos(COL), 0.0))
FLANC = np.array([math.cos(COL), math.sin(COL), 0.0])
BASE = Vector((0.0, -0.165, 0.600))           # le pied du cou, enfoui dans le poitrail
ARC = [(0.0, 0.0), (0.022, 0.090), (0.048, 0.180), (0.072, 0.250), (0.090, 0.292)]   # (avance, monte) : dressé
LACET, PIQUE, PENCHE = 34.0, 22.0, 8.0        # la tête : tournée vers nous, le nez un peu bas, penchée : elle écoute
GROSSE = 1.45


def gauss(x):
    return np.exp(-x * x)


def jambe(points, rayons, genou=0.58):
    """Une jambe fine : un boudin qui passe par ses articulations, sable en haut, plus foncée sous le genou."""
    rayon = lambda t: float(np.interp(t, np.linspace(0, 1, len(rayons)), rayons))
    return K.tube_peint(A.courbe(points, 6), rayon, [(genou, SABLE), (1, FONCE)], 18)


def sabot(e=1.0):
    """Un petit sabot fendu et pointu : la pince avance, une rainure sépare les deux onglons devant."""
    def fendu(v):
        s = v.copy()
        s[:, 1] -= 0.012 * e * K.lisse((0.032 * e - v[:, 2]) / (0.032 * e))
        devant = K.lisse(-v[:, 1] / (0.016 * e))
        s[:, 1] += 0.006 * e * devant * gauss(v[:, 0] / (0.0038 * e)) * K.lisse((0.034 * e - v[:, 2]) / (0.018 * e))
        return s
    prof = [(0, 0), (0.026, 0.003), (0.028, 0.014), (0.022, 0.036), (0.018, 0.046), (0, 0.050)]
    return A.tour(A.profil([(r * e, z * e) for r, z in prof], 5), 28).sculpte(fendu)


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def construire():
    a = K.Animal("chevreuil")
    a.taille = 1.10

    # ----- le corps : tourné de la croupe au poitrail, puis couché, le nez de la pièce un peu plus bas que la croupe ;
    #       dans la pièce, X est la gauche, Y le dos, Z l'avant. Un petit corps compact, la croupe ronde et pleine. -----
    corps = A.tour(A.profil([(0, 0), (0.088, 0.010), (0.120, 0.055), (0.124, 0.120), (0.110, 0.210), (0.104, 0.290),
                             (0.112, 0.370), (0.104, 0.430), (0.074, 0.468), (0, 0.480)], 6), 48)
    v0 = corps.v
    tour_ = np.abs(np.arctan2(v0[:, 0], v0[:, 1]))
    ventre = (tour_ > 2.25) & (v0[:, 2] > 0.09) & (v0[:, 2] < 0.42)
    miroir = (v0[:, 2] < 0.075) & (tour_ < 2.1)                        # le grand miroir blanc, tout le derrière
    corps.teinte = np.where(miroir[:, None], np.asarray(BLANC), np.where(ventre[:, None], np.asarray(PALE), np.asarray(SABLE)))

    def galbe(v):
        s = v.copy()
        s[:, 0] *= 0.84 * (1 + 0.12 * gauss((v[:, 2] - 0.09) / 0.09))           # la croupe large : les cuisses du sauteur
        bas = v[:, 1] < 0
        s[bas, 1] *= (1 - 0.20 * gauss((v[:, 2] - 0.20) / 0.11) + 0.08 * gauss((v[:, 2] - 0.38) / 0.07))[bas]
        haut = ~bas
        s[haut, 1] *= (1 + 0.10 * gauss((v[:, 2] - 0.09) / 0.08))[haut]
        return s
    a.piece("corps", corps.sculpte(galbe), None, pos=CROUPE, rot=(90 - CABRE, 0, 0))

    # ----- le pinceau : la touffe blanche sous le miroir (c'est une chevrette) -----
    pinceau = A.tour(A.profil([(0, 0), (0.020, 0.008), (0.022, 0.030), (0.012, 0.060), (0, 0.070)], 5), 20).etire(1.0, 0.7, 1.0)
    a.piece("pinceau", pinceau, BLANC, pos=(0, 0.238, 0.590), rot=A.viser((0, 0.30, -0.95)))

    # ----- le cou : long, fin, dressé ; la gorge blanche -----
    enc = K.Fil([tuple(BASE + AVANT * u + Vector((0, 0, z))) for u, z in ARC], FLANC)
    L = enc.long
    parts, rayons = [0.03, 0.15, 0.35, 0.55, 0.75, 0.90, 0.985], [0.086, 0.078, 0.064, 0.055, 0.050, 0.048, 0.045]
    pc = A.profil([(0, 0)] + [(r, p * L) for r, p in zip(rayons, parts)] + [(0, 1.01 * L)], 6)
    a.piece("cou", A.tour(pc, 40).etire(0.84, 1.0, 1.0).sculpte(enc.couche), SABLE)
    c_, av, nq = enc.cadre(0.62 * L)
    a.rustine("gorge", "cou", Vector(c_), Vector(-nq * 0.9 + av * 0.2), lambda th: 0.80 + 0.22 * math.cos(th), BLANC, 0.0025, 0)

    # ----- la tête : courte, large aux yeux, le museau fin ; dans son repère, X la gauche, Y le chanfrein, Z vers le nez -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0, 0, 0), nez) @ Matrix.Rotation(math.radians(PENCHE), 4, Vector((0, 0, 1))) @ A.repere(ech=(GROSSE,) * 3)
    bout = Vector(enc.cadre(L)[0])
    T = A.repere(bout - T.to_3x3() @ Vector((0, -0.020, 0.050))) @ T
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.020, 0.150))

    tete = A.tour(A.profil([(0, 0), (0.045, 0.008), (0.064, 0.034), (0.068, 0.070), (0.056, 0.112), (0.041, 0.155),
                            (0.033, 0.188), (0.031, 0.206), (0.022, 0.224), (0, 0.232)], 6), 56)
    z, x, y = tete.v[:, 2], tete.v[:, 0], tete.v[:, 1]
    chanfrein = (y > 0.010) & (np.abs(x) < 0.030) & (z > 0.050) & (z < 0.200)
    museau = z > 0.210
    moustache = (z > 0.184) & (z <= 0.210) & (y < 0.012)
    menton = (y < -0.020) & (z > 0.150)
    teinte = np.tile(np.asarray(SABLE), (len(z), 1))
    teinte[chanfrein] = FONCE
    teinte[moustache | menton] = BLANC
    teinte[museau] = NOIR
    tete.teinte = teinte

    def fine(v):
        s = v.copy()
        z, haut = v[:, 2], v[:, 1] > 0
        s[:, 0] *= 0.86 + 0.12 * gauss((z - 0.075) / 0.040)
        s[:, 1] *= np.where(haut, 0.94, 1.0 + 0.18 * gauss((z - 0.065) / 0.045))
        return s
    a.piece("tete", tete.sculpte(fine), None, mat=T)
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.019, 0.013, 0.011), NOIR, mat=T @ A.repere((0, 0.008, 0.226)), poil=False)

    # ----- les yeux : petits, noirs, vifs, grands ouverts -----
    centre = T @ Vector((0, 0, 0.085))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.82, 0.46, 0.25)))
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0135)

    # ----- les oreilles : immenses, en cornet, la pointe noire, le dedans blanc. La gauche braquée devant, sur le
    #       bruit ; la droite tournée de côté. -----
    po = A.profil([(0, 0), (0.026, 0.012), (0.050, 0.055), (0.061, 0.110), (0.053, 0.165), (0.031, 0.215), (0.010, 0.242), (0, 0.250)], 6)

    def cornet(v):                                        # les bords se relèvent vers l'avant (+Y) : un creux
        s = v.copy()
        s[:, 1] += 2.6 * v[:, 0] ** 2 * K.lisse(v[:, 2] / 0.04)
        return s
    for nom, c, devant in (("G", 1, Vector((0.10, 0.30, 1.0))), ("D", -1, Vector((-1.0, 0.20, 0.35)))):
        vers = (T3 @ Vector((c * 0.46, 0.88, -0.10))).normalized()
        racine = T @ Vector((c * 0.040, 0.044, 0.030))
        E = A.cadre(racine - vers * 0.012, vers, T3 @ devant)
        oreille = K.bandes(A.tour(po, 36).etire(1.0, 0.34, 1.0), [(0.200, SABLE), (9, NOIR)])
        a.piece("oreille_" + nom, oreille.sculpte(cornet), None, mat=E)
        a.rustine("pavillon_" + nom, "oreille_" + nom, E @ Vector((0, 0, 0.105)), E.to_3x3() @ Vector((0, 1, 0)), 1.15, BLANC, 0.002, 0)

    # ----- les jambes : interminables et fines. L'avant droite plantée, l'avant gauche levée et pliée net, le sabot
    #       pendu ; les deux arrière ramassées sous elle, les jarrets pliés : le ressort est armé. -----
    epaule = [0.044, 0.046, 0.033, 0.023, 0.017, 0.019, 0.016]
    hanche = [0.056, 0.064, 0.032, 0.021, 0.017, 0.019, 0.016]
    plantees = (("avant_D", [(-0.036, -0.165, 0.530), (-0.060, -0.168, 0.450), (-0.062, -0.176, 0.330), (-0.062, -0.186, 0.220),
                             (-0.062, -0.192, 0.120), (-0.062, -0.198, 0.052), (-0.062, -0.202, 0.030)], epaule, 0.58),
                ("arriere_G", [(0.044, 0.185, 0.580), (0.074, 0.120, 0.470), (0.076, 0.150, 0.380), (0.074, 0.262, 0.260),
                               (0.074, 0.214, 0.130), (0.074, 0.186, 0.054), (0.074, 0.180, 0.030)], hanche, 0.55),
                ("arriere_D", [(-0.044, 0.185, 0.580), (-0.074, 0.130, 0.470), (-0.076, 0.165, 0.380), (-0.074, 0.282, 0.262),
                               (-0.074, 0.240, 0.130), (-0.074, 0.214, 0.054), (-0.074, 0.208, 0.030)], hanche, 0.55))
    for nom, points, rayons_, genou in plantees:
        a.piece("patte_" + nom, jambe(points, rayons_, genou), None)
        a.piece("sabot_" + nom, sabot(), NOIR, pos=(points[-1][0], points[-1][1] - 0.005, 0.0), poil=False)
    levee = [(0.036, -0.165, 0.530), (0.058, -0.180, 0.460), (0.062, -0.228, 0.410), (0.064, -0.300, 0.400),
             (0.066, -0.296, 0.310), (0.066, -0.280, 0.240), (0.066, -0.266, 0.214)]
    a.piece("patte_avant_G", jambe(levee, epaule, 0.50), None)
    pend = (Vector(levee[-1]) - Vector(levee[-2])).normalized()
    a.piece("sabot_avant_G", sabot(), NOIR, mat=A.cadre(Vector(levee[-1]) + pend * 0.040, -pend, (0, 1, 0)), poil=False)
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py chevreuil). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Le modèle est saisi l'antérieur gauche levé et plié net : chaque jambe a donc ses deux os à elle, à sa vraie place
# (pas de miroir), et ses pièces passent de l'os du haut à celui du bas au genou (ou au jarret). La jambe levée est
# dessinée plus courte que les autres (pliée) : pour se poser, son bas s'allonge, et son sabot a un troisième os qui
# garde sa forme pendant ce temps.

from poses import Pose, borne, cloche, onde

CORPS_PIVOT = (0.0, 0.000, 0.620)
HANCHES = (0.0, 0.185, 0.600)                 # elle se penche autour d'elles pour brouter
COU = [(0.0, -0.165, 0.600), (0.006, -0.182, 0.674), (0.012, -0.201, 0.748), (0.019, -0.224, 0.821), (0.028, -0.251, 0.892)]
BOULET_G = (0.066, -0.266, 0.214)             # le bas de la jambe levée, où son sabot pend

# chaque jambe : l'os du haut et son épaule (ou sa hanche), l'os du bas et son genou (ou son jarret), et les deux points
# de la jambe qui encadrent le genou
JAMBES = {
    ("avant", "_G"): ("av_g", (0.036, -0.165, 0.530), "av_g2", (0.064, -0.300, 0.400), (0.062, -0.228, 0.410), (0.066, -0.296, 0.310)),
    ("avant", "_D"): ("av_d", (-0.036, -0.165, 0.530), "av_d2", (-0.062, -0.176, 0.330), (-0.060, -0.168, 0.450), (-0.062, -0.186, 0.220)),
    ("arriere", "_G"): ("ar_g", (0.044, 0.185, 0.580), "ar_g2", (0.074, 0.262, 0.260), (0.076, 0.150, 0.380), (0.074, 0.214, 0.130)),
    ("arriere", "_D"): ("ar_d", (-0.044, 0.185, 0.580), "ar_d2", (-0.074, 0.282, 0.262), (-0.076, 0.165, 0.380), (-0.074, 0.240, 0.130)),
}
OS = [("racine", None, (0, 0, 0)),
      ("corps", "racine", CORPS_PIVOT),                  # le milieu du dos
      ("cou", "corps", COU[0]),                          # le pied du cou, dans le poitrail
      ("tete", "cou", COU[-1]),                          # la nuque
      ("oreille_g", "tete", (0.071, -0.234, 0.996)),     # celle qui est braquée devant
      ("oreille_d", "tete", (-0.028, -0.294, 0.981)),    # celle qui est tournée de côté
      ("queue", "corps", (0.0, 0.240, 0.600))]           # le pinceau, sous le miroir
for _h, _ph, _b, _pb, _av, _ap in JAMBES.values():
    OS += [(_h, "corps", _ph), (_b, _h, _pb)]
OS += [("av_g3", "av_g2", BOULET_G)]                     # le sabot de la jambe levée


def _doux(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def _jambe(rang):
    """Une pièce de jambe : l'os du haut au-dessus du genou, celui du bas en dessous, avec un fondu de quelques cm.
    (Les points d'une pièce de droite arrivent en miroir, X retourné : on retourne le genou de même.)"""
    def poids(points, cote):
        h, _ph, b, genou, avant, apres = JAMBES[(rang, cote)]
        m = np.array([-1.0, 1.0, 1.0]) if cote == "_D" else np.ones(3)
        g, u, v = np.array(genou) * m, np.array(avant) * m, np.array(apres) * m
        sens = (g - u) / np.linalg.norm(g - u) + (v - g) / np.linalg.norm(v - g)
        w = _doux((np.asarray(points, float) - g) @ (sens / np.linalg.norm(sens)) / 0.04 + 0.5)
        return {h: 1 - w, b: w}
    return poids


def _sabot(rang):
    """Un sabot : sur l'os du bas de sa jambe (celui de la jambe levée a son os à lui)."""
    return lambda points, cote: {"av_g3" if (rang, cote) == ("avant", "_G") else JAMBES[(rang, cote)][2]: np.ones(len(points))}


def _cou(points, cote):
    """Le cou (et la gorge cousue dessus) : le corps le porte en bas, la tête en haut, il se plie entre les deux."""
    fil = np.asarray(COU, float)
    fins = np.concatenate([np.linspace(fil[i], fil[i + 1], 12, endpoint=False) for i in range(len(fil) - 1)] + [fil[-1:]])
    u = np.argmin(((np.asarray(points, float)[:, None, :] - fins[None]) ** 2).sum(-1), axis=1) / (len(fins) - 1)
    w = _doux((u - 0.55) / 0.45)
    return {"cou": 1 - w, "tete": w}


def _oreille(points, cote):
    return {"oreille_g" if cote == "_G" else "oreille_d": np.ones(len(points))}


PORTEURS = [("corps", "corps"), ("pinceau", "queue"), ("cou", _cou, "cou"), ("gorge", _cou, "cou"),
            ("tete", "tete"), ("truffe", "tete"), ("oeil", "tete"),
            ("oreille", _oreille), ("pavillon", _oreille),
            ("patte_avant", _jambe("avant")), ("patte_arriere", _jambe("arriere")),
            ("sabot_avant", _sabot("avant")), ("sabot_arriere", _sabot("arriere")),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 (l'œil gauche) et paupiere_1
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


# --- un peu de géométrie (les angles d'une Pose : X, puis Y, puis Z, autour des axes du monde)

def _tourne(axe, degres):
    k = np.asarray(axe, float) / np.linalg.norm(axe)
    c = np.array([[0.0, -k[2], k[1]], [k[2], 0.0, -k[0]], [-k[1], k[0], 0.0]])
    a = math.radians(degres)
    return np.eye(3) + math.sin(a) * c + (1 - math.cos(a)) * (c @ c)


def _matrice(rot):
    return _tourne((0, 0, 1), rot[2]) @ _tourne((0, 1, 0), rot[1]) @ _tourne((1, 0, 0), rot[0])


def autour(p, point, rot, pos=(0, 0, 0)):
    """Tourne le corps autour d'un autre point que son pivot (les hanches, pour baisser l'avant)."""
    R = _matrice(rot)
    d = np.subtract(point, CORPS_PIVOT)
    p.add("corps", rot=rot, pos=tuple(d - R @ d + np.asarray(pos, float)))


def deplie(p, x, devant=0.0):
    """La jambe levée : x = 1, pliée haut comme sur le modèle ; x = 0, dépliée sous l'épaule, le sabot à plat par terre
    (son bas s'allonge de 40 %, l'épaule s'enfonce de 4 cm dans le corps). devant > 0 : le pied part vers l'avant."""
    y = 1 - x
    e = 1 + 0.40 * y
    p.add("av_g", rot=(46 * y - devant, 0, 0), pos=(0, 0, -0.040 * y))
    p.add("av_g2", rot=(-56 * y, 0, 0), ech=(1, 1, e))
    p.add("av_g3", rot=(-18 * y, 0, 0), ech=(1, 1, 1 / e))


def plie(p, nom, haut, bas):
    """Une jambe : l'os du haut tourne de « haut » (< 0 : le genou monte devant), celui du bas de « bas »."""
    p.add(nom, rot=(haut, 0, 0))
    p.add(nom + "2", rot=(bas, 0, 0))


# --- les cinq animations

def repos(t):
    """Aux aguets : elle respire vite, les deux grandes oreilles pivotent chacune vers un bruit (c'est son geste), la
    tête suit un instant ; puis elle tape deux fois du pied levé, sèchement, le pinceau qui frétille ; elle cligne."""
    p = Pose()
    r = onde(t, 3)
    tape = cloche(t, 0.56, 0.035) + cloche(t, 0.66, 0.035)
    regard = cloche(t, 0.30, 0.10)
    p.add("corps", ech=(1 + 0.016 * r, 1, 1 + 0.004 * r))   # le souffle gonfle les flancs (en hauteur, il ferait flotter les sabots)
    deplie(p, 1 - tape)
    p.add("cou", rot=(0, 0, 6 * regard))
    p.add("tete", rot=(-4 * regard, -6 * regard, 14 * regard))
    p.add("oreille_g", rot=(0, 0, 40 * cloche(t, 0.12, 0.05) - 30 * cloche(t, 0.84, 0.05)))
    p.add("oreille_d", rot=(0, 0, 35 * cloche(t, 0.24, 0.06) - 25 * cloche(t, 0.44, 0.05)))
    p.add("queue", rot=(-20 * cloche(t, 0.62, 0.08) * abs(onde(t, 10)), 0, 0))
    p.ouvert = borne(1 - cloche(t, 0.40, 0.02) - cloche(t, 0.92, 0.02))
    return p


def avance(t):
    """Son trot léger, les genoux haut comme sur le modèle : les diagonales vont ensemble (antérieur gauche et
    postérieur droit, puis l'autre paire) ; le cou hoche, les oreilles restent braquées, le pinceau balance."""
    p = Pose()
    g = 0.5 + 0.5 * math.cos(math.tau * t)                 # 1 : l'antérieur gauche est en l'air (la pose du modèle)
    d = 1 - g
    deplie(p, g)
    plie(p, "av_d", -40 * d, 80 * d)
    plie(p, "ar_d", -20 * g + 8 * d, -15 * g)              # le jarret se plie, le pied monte et passe sous elle
    plie(p, "ar_g", -20 * d + 8 * g, -15 * d)
    p.add("corps", pos=(0, 0, 0.010 * abs(onde(t, 1))), rot=(0, 2 * onde(t, 1), 0))
    p.add("cou", rot=(4 * onde(t, 2), 0, 0))
    p.add("tete", rot=(-3 * onde(t, 2), 0, 0))
    p.add("queue", rot=(0, 0, 10 * onde(t, 1)))
    return p


def mange(t):
    """Elle broute : le pied levé se pose, les antérieurs s'écartent devant, l'avant s'abaisse, le long cou plonge
    jusqu'à l'herbe ; trois coups de dents, et toutes les deux bouchées elle relève les yeux (méfiante), puis elle se
    redresse en mâchant, oreilles braquées."""
    p = Pose()
    bas = float(_doux(t / 0.16) * (1 - _doux((t - 0.74) / 0.18)))
    pose_pied = float(_doux(t / 0.08) * (1 - _doux((t - 0.84) / 0.12)))
    broute = abs(onde(t, 6)) * bas
    mefie = cloche(t, 0.46, 0.05)
    autour(p, HANCHES, (10 * bas, 0, 0))
    ecart = math.sqrt(bas)                               # l'avant baisse comme bas, l'écart des pieds compense comme sa racine
    deplie(p, 1 - pose_pied, 39 * ecart)
    plie(p, "av_d", -34 * ecart, 0)
    p.add("cou", rot=(130 * bas - 40 * mefie, 0, -10 * bas))
    p.add("tete", rot=(-50 * bas + 4 * broute + 10 * mefie, 0, -10 * bas))
    p.add("oreille_g", rot=(-60 * bas, 0, 20 * mefie))    # la tête retournée vers l'herbe, les oreilles restent dressées
    p.add("oreille_d", rot=(-60 * bas, 0, -20 * mefie))
    p.add("queue", rot=(0, 0, 8 * onde(t, 3)))
    p.ouvert = borne(1 - cloche(t, 0.94, 0.03))
    return p


def joie(t):
    """Le bond du chevreuil : elle se ramasse, s'élance haut, les quatre jambes repliées sous elle, le miroir blanc
    déployé et le pinceau dressé ; un second bond plus petit, puis elle se pose et reprend sa pose d'attente, le pied
    gauche levé."""
    p = Pose()
    ramasse = cloche(t, 0.10, 0.08, False)
    b1 = math.sin(math.pi * borne((t - 0.14) / 0.36))
    b2 = 0.55 * math.sin(math.pi * borne((t - 0.52) / 0.28))
    vol = b1 + b2
    env = math.sin(math.pi * borne(t / 0.86)) if t < 0.86 else 0.0
    p.add("corps", pos=(0, 0, -0.030 * ramasse + 0.22 * vol), rot=(-8 * b1 + 6 * b2, 0, 0))
    deplie(p, 1.0)
    plie(p, "av_d", -50 * vol, 100 * vol)
    plie(p, "ar_g", -20 * vol + 6 * ramasse, 45 * vol)
    plie(p, "ar_d", -20 * vol + 6 * ramasse, 45 * vol)
    p.add("cou", rot=(-10 * env, 0, 0))
    p.add("tete", rot=(-8 * env, 0, 6 * onde(t, 2) * env))
    p.add("oreille_g", rot=(0, 20 * env, 0))
    p.add("oreille_d", rot=(0, -20 * env, 0))
    p.add("queue", rot=(50 * env, 0, 0))
    return p


def dort(t):
    """Couchée dans les herbes hautes, les jambes repliées sous elle, le cou ramené le long du flanc et la tête posée
    sur le dos, les grandes oreilles couchées ; les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.390), ech=(1.02 + 0.012 * r, 1.0, 0.98 + 0.020 * r))
    plie(p, "av_g", 100, 30)
    plie(p, "av_d", 90, -160)
    plie(p, "ar_g", -70, -150)
    plie(p, "ar_d", -70, -150)
    p.add("cou", rot=(-50 + 1.5 * r, 10, 60))             # le cou couché en arrière, le long du flanc gauche
    p.add("tete", rot=(60, 0, 10))                       # la joue posée sur le dos
    p.add("oreille_g", rot=(-60, -15, 0))                 # les oreilles couchées en arrière
    p.add("oreille_d", rot=(-55, 15, 0))
    p.add("queue", rot=(-10, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("chevreuil", styles.style_de("chevreuil"), sys.modules[__name__]), "Chevreuil")
