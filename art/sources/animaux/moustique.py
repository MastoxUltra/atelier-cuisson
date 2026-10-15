"""Le moustique en peluche : sournois, l'air de rien. Un thorax bossu gris fumée barré d'un galon perle, la petite tête
qui pend dessous, un long abdomen rouge rubis rayé de fines bandes sombres et dressé en l'air, deux ailes étroites gris
perle, deux antennes plumeuses, des pattes interminables zébrées noir et blanc. Il est penché sur sa longue trompe
framboise comme sur une canne, les deux pattes arrière relevées au-dessus du dos, une paupière plus basse que l'autre.

    python moustique.py        fabrique la fiche art/apercus/animaux/moustique.png
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

FUMEE = M.hexa("#8f8a96")                     # le gris fumée du thorax
PALE = M.hexa("#c6c3cf")                      # la tête, plus claire : on doit lire le regard sous la bosse
RUBIS = M.hexa("#d0143e")                     # l'abdomen (le poil le fonce)
SOMBRE = M.hexa("#3a0e20")                    # ses fines bandes
PERLE = M.hexa("#dfe3ee")                     # la feutrine des ailes, le galon du dos
NOIR, BLANC = M.hexa("#1d1b21"), M.hexa("#fffaf0")      # les zébrures des pattes
TOURNE = 0                                    # -26 sur la fiche (posé de biais, vu de trois quarts) ; 0 pour le jeu : il regarde droit devant
POSE = A.repere((0, 0, 0), (0, 0, TOURNE))
BUSTE = POSE @ A.repere((0.0, 0.0, 0.150), (32, 5, 0))      # le thorax : le nez vers le sol, l'abdomen en l'air
PORT = BUSTE @ A.repere((0.0, -0.074, -0.020), (-16, 14, 24))      # la tête : penchée sur l'épaule, tournée vers nous
P3 = PORT.to_3x3()
LONG = 0.165                                  # la longueur de l'abdomen
ARC = LONG / math.radians(34)                 # le rayon de l'arc qui le relève
BANDES = (0.024, 0.047, 0.070, 0.092, 0.113, 0.132, 0.148)      # ses bandes sombres


def rayon(z):
    """Le rayon de l'abdomen à la distance z du thorax : dodu au départ, effilé au bout, un peu serré à chaque bande."""
    r = np.interp(z, [0, 0.012, 0.05, 0.11, 0.150, LONG], [0.012, 0.021, 0.0235, 0.019, 0.012, 0.0])
    return float(r) * (1 - 0.09 * sum(math.exp(-((z - b) / 0.004) ** 2) for b in BANDES))


def cambre(v):
    """Relève l'abdomen le long d'un arc (vers le -Y de la pièce, son dos)."""
    angle = v[:, 2] / ARC
    s = v.copy()
    s[:, 1] = (ARC + v[:, 1]) * np.cos(angle) - ARC
    s[:, 2] = (ARC + v[:, 1]) * np.sin(angle)
    return s


def zebre(points, rayon_, pas=0.019, angle=0.012):
    """Une patte de feutrine : un tube qui passe par les points (les angles arrondis), zébré noir et blanc tous les « pas »
    mètres. rayon_ : une fonction de 0 à 1."""
    fil = A.conges([np.asarray(p, float) for p in points], angle, 5)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(fil, axis=0), axis=1))])
    s = np.linspace(0.0, fait[-1], int(fait[-1] / 0.0035) + 2)
    m = A.tube(np.stack([np.interp(s, fait, fil[:, k]) for k in range(3)], axis=1), rayon_, 12)
    noir = np.repeat((s // pas).astype(int) % 2 == 0, 12)
    m.teinte = np.zeros((len(m.v), 3))
    m.teinte[:len(noir)] = np.where(noir[:, None], NOIR, BLANC)
    m.teinte[len(noir):] = [NOIR if noir[0] else BLANC, NOIR if noir[-1] else BLANC]
    return m


def construire():
    a = K.Animal("moustique")
    a.taille = 0.26
    a.tete = PORT @ Vector((0, -0.036, -0.002))

    # ----- le thorax : une boule couchée (son pôle du haut regarde l'avant), une grosse bosse sur les épaules,
    #       et un galon perle peint tout le long du dos -----
    def bossu(v):
        v = K.bosse(v, (0, 0.80, 0.42), 0.46, 0.55)
        return np.stack([v[:, 0] * 0.040, -v[:, 2] * 0.050, v[:, 1] * 0.043], axis=1)
    thorax = A.boule(1.0, 48, 24)
    thorax.teinte = np.zeros((len(thorax.v), 3))
    for anneau in thorax.anneaux:
        for j, i in enumerate(anneau):
            thorax.teinte[i] = PERLE if len(anneau) > 1 and abs(j - len(anneau) / 4) <= 2.5 else FUMEE
    a.piece("thorax", thorax.sculpte(bossu), None, mat=BUSTE)

    # ----- l'abdomen : un long fuseau rubis, bagué de fines bandes sombres, relevé en arc vers le ciel -----
    profil = [(rayon(z), z) for z in np.linspace(0, LONG, 90)]
    profil[-1] = (0.0, LONG)
    bagues = [palier for b in BANDES for palier in ((b - 0.0032, RUBIS), (b + 0.0032, SOMBRE))] + [(9, RUBIS)]
    a.piece("abdomen", K.bandes(A.tour(profil, 40), bagues).sculpte(cambre), None, mat=BUSTE @ A.repere((0, 0.030, -0.004), (-94, 0, 0)))

    # ----- la tête : une petite boule sous la bosse, deux gros boutons rapprochés, des paupières en coin -----
    a.piece("tete", A.boule(1.0, 40, 20).etire(0.039, 0.035, 0.035), PALE, mat=PORT)
    centre = PORT @ Vector((0, 0, 0))
    for nom, cote, ferme in (("_G", 1, 0.0138), ("_D", -1, 0.0096)):
        p, n = a.surface("tete", centre, P3 @ Vector((0.46 * cote, -0.76, 0.34)))
        a.bouton("oeil" + nom, p + n * 0.001, n, 0.0185)
        haut = (P3 @ Vector((0.30 * cote, 0, 1)) - n * n.dot(P3 @ Vector((0.30 * cote, 0, 1)))).normalized()
        a.piece("lourde" + nom, A.boule(1.0, 20, 10).etire(0.0200, 0.0098, 0.0040), FUMEE, mat=A.cadre(p + haut * ferme + n * 0.0066, n, haut), poil=False)
        # l'antenne plumeuse : un boudin de peluche gris perle, renflé au milieu, dressé en V au-dessus de la tête
        pied = PORT @ Vector((0.016 * cote, -0.012, 0.031))
        a.piece("antenne" + nom, A.tube(A.courbe([pied, pied + P3 @ Vector((0.016 * cote, -0.014, 0.030)), pied + P3 @ Vector((0.044 * cote, -0.022, 0.056))], 6),
                                        lambda t: 0.0028 + 0.0048 * math.sin(math.pi * min(1.0, t * 1.1)) ** 0.8, 12), PERLE)

    # ----- la trompe : une longue paille de feutrine framboise, plantée dans le sol ; il s'appuie dessus -----
    depart = PORT @ Vector((0.0, -0.028, -0.016))
    pointe = POSE @ Vector((0.012, -0.150, 0.0))
    pointe.z = 0.004
    a.piece("trompe", A.tube(A.courbe([depart, depart.lerp(pointe, 0.5) + Vector((0, 0, 0.006)), pointe], 8), lambda t: 0.0066 - 0.0032 * t, 12), K.FRAMBOISE, poil=False)

    # ----- les deux ailes : étroites, en feutrine gris perle, dressées en V au-dessus du dos (l'abdomen rubis reste
    #       à découvert) ; une nervure brodée -----
    contour = A.courbe([(0.0, -0.006), (0.050, -0.014), (0.120, -0.018), (0.160, -0.012), (0.174, 0.0), (0.160, 0.014), (0.110, 0.020), (0.050, 0.016), (0.0, 0.006)], 5, fermee=True)
    for nom, cote, vrille in (("_G", 1, 22), ("_D", -1, 6)):
        d = Vector((0.34 * cote, 0.66, 0.68)).normalized()
        f = Vector((cote, 0, 0))
        f = A.tourne(d, vrille, (f - d * d.dot(f)).normalized())
        rep = BUSTE @ A.cadre(Vector((0.012 * cote, 0.006, 0.034)), d.cross(f), f)
        a.piece("aile" + nom, A.decoupe(contour, 0.0045, 0.0018), PERLE, mat=rep, poil=False)
        for face in (1, -1):
            a.broderie("nervure" + nom, [rep @ Vector((x, y, face * 0.0030)) for x, y in ((0.012, 0.0), (0.070, 0.002), (0.125, 0.0), (0.160, -0.004))], 0.0014, K.ARDOISE)

    # ----- les six pattes, interminables : quatre plantées loin du corps, le genou plus haut que le dos, aucune posée
    #       comme sa voisine ; les deux de derrière relevées en l'air, recourbées au-dessus de l'abdomen -----
    def fine(t):
        return 0.0076 - 0.0034 * t
    for nom, hanche, suite in (("avant_G", (0.016, -0.022, -0.030), [(0.100, -0.050, 0.182), (0.140, -0.092, 0.006), (0.150, -0.104, 0.004)]),
                               ("avant_D", (-0.016, -0.022, -0.030), [(-0.070, -0.072, 0.172), (-0.098, -0.124, 0.006), (-0.106, -0.140, 0.004)]),
                               ("milieu_G", (0.020, 0.0, -0.034), [(0.112, 0.022, 0.207), (0.150, 0.060, 0.006), (0.162, 0.068, 0.004)]),
                               ("milieu_D", (-0.020, 0.0, -0.034), [(-0.108, -0.004, 0.200), (-0.146, 0.024, 0.006), (-0.158, 0.028, 0.004)]),
                               ("arriere_G", (0.018, 0.020, -0.030), [(0.090, 0.070, 0.165), (0.112, 0.140, 0.230), (0.094, 0.176, 0.270)]),
                               ("arriere_D", (-0.018, 0.020, -0.030), [(-0.088, 0.082, 0.175), (-0.104, 0.154, 0.243), (-0.080, 0.180, 0.284)])):
        a.piece("patte_" + nom, zebre([BUSTE @ Vector(hanche)] + [POSE @ Vector(p) for p in suite], fine, angle=0.030 if "arriere" in nom else 0.012), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py moustique)

from poses import Pose, borne, cloche, onde

# Il n'est pas symétrique (le thorax roule de 5°, la tête est penchée, aucune patte n'est posée comme sa voisine) :
# chaque côté a ses os à lui, nommés _g et _d, sans miroir. Chaque patte a deux os, la cuisse (de la hanche au genou,
# plus haut que le dos) et la jambe (du genou au pied) : les pieds posés restent cloués au sol quand le corps bouge.
B3 = np.array(BUSTE.to_3x3())                  # les axes du thorax, en colonnes : sa gauche, son arrière, son dessus
T3 = np.array(P3)                              # ceux de la tête, de même


def ici(m, v):
    """Un point donné dans un repère (BUSTE, PORT, POSE), rendu en numpy dans celui du jardin."""
    return np.array(m @ Vector(v))


CORPS = ici(BUSTE, (0, 0, 0))
COU = ici(BUSTE, (0, -0.046, -0.018))          # entre la bosse et la petite tête
BASE = ici(PORT, (0.0, -0.028, -0.016))        # le départ de la trompe
POINTE = ici(POSE, (0.012, -0.150, 0.0)) * [1, 1, 0] + [0, 0, 0.004]      # son bout, planté dans le sol
# les six pattes (les mêmes mesures que dans construire) : la hanche dans le thorax, puis le genou, le pied, l'orteil
PATTES = {"avant_g": ((0.016, -0.022, -0.030), [(0.100, -0.050, 0.182), (0.140, -0.092, 0.006), (0.150, -0.104, 0.004)]),
          "avant_d": ((-0.016, -0.022, -0.030), [(-0.070, -0.072, 0.172), (-0.098, -0.124, 0.006), (-0.106, -0.140, 0.004)]),
          "milieu_g": ((0.020, 0.0, -0.034), [(0.112, 0.022, 0.207), (0.150, 0.060, 0.006), (0.162, 0.068, 0.004)]),
          "milieu_d": ((-0.020, 0.0, -0.034), [(-0.108, -0.004, 0.200), (-0.146, 0.024, 0.006), (-0.158, 0.028, 0.004)]),
          "arriere_g": ((0.018, 0.020, -0.030), [(0.090, 0.070, 0.165), (0.112, 0.140, 0.230), (0.094, 0.176, 0.270)]),
          "arriere_d": ((-0.018, 0.020, -0.030), [(-0.088, 0.082, 0.175), (-0.104, 0.154, 0.243), (-0.080, 0.180, 0.284)])}
FIL = {n: [ici(BUSTE, h)] + [ici(POSE, q) for q in suite] for n, (h, suite) in PATTES.items()}
POSEES = ("avant_g", "avant_d", "milieu_g", "milieu_d")

OS = ([("racine", None, (0, 0, 0)),
       ("corps", "racine", tuple(CORPS)),                                  # le cœur du thorax
       ("abdomen", "corps", tuple(ici(BUSTE, (0, 0.030, -0.004)))),       # l'attache de l'abdomen
       ("tete", "corps", tuple(COU)),
       ("trompe", "tete", tuple(BASE))]
      + [("antenne_" + l, "tete", tuple(ici(PORT, (0.016 * c, -0.012, 0.031)))) for l, c in (("g", 1), ("d", -1))]
      + [("aile_" + l, "corps", tuple(ici(BUSTE, (0.012 * c, 0.006, 0.034)))) for l, c in (("g", 1), ("d", -1))]
      + [os_ for n, f in FIL.items() for os_ in (("cuisse_" + n, "corps", tuple(f[0])), ("jambe_" + n, "cuisse_" + n, tuple(f[1])))])


def _cote(nom):
    """Une pièce d'un côté (antenne_G, aile_D) suit l'os de son côté (antenne_g, aile_d)."""
    return lambda points, cote: {nom + cote.lower(): np.ones(len(points))}


def _patte(nom):
    """Une patte zébrée : jusqu'au genou elle suit la cuisse, après lui la jambe (le passage se fait dans le coude).
    L'usine retourne les pièces de droite en miroir avant de les donner : on les remet à leur place."""
    def poids(points, cote):
        n = nom + cote.lower()
        q = points * ([1, 1, 1] if cote == "_G" else [-1, 1, 1])
        f = FIL[n]
        fait, meilleur, u = 0.0, np.full(len(q), 9.0), np.zeros(len(q))
        for a, b in zip(f[:-1], f[1:]):
            long_ = float(np.linalg.norm(b - a))
            x = np.clip((q - a) @ (b - a) / long_ ** 2, 0.0, 1.0)
            e = np.linalg.norm(q - a - x[:, None] * (b - a), axis=1)
            u = np.where(e < meilleur, fait + x * long_, u)
            meilleur = np.minimum(e, meilleur)
            fait += long_
        w = K.lisse((u - float(np.linalg.norm(f[1] - f[0])) + 0.014) / 0.028)
        return {"cuisse_" + n: 1.0 - w, "jambe_" + n: w}
    return poids


PORTEURS = [("thorax", "corps"), ("abdomen", "abdomen"), ("tete", "tete"), ("oeil", "tete"), ("lourde", "tete"),
            ("antenne", _cote("antenne")), ("trompe", "trompe"), ("aile", _cote("aile")), ("nervure", _cote("aile")),
            ("patte_avant", _patte("avant")), ("patte_milieu", _patte("milieu")), ("patte_arriere", _patte("arriere")),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def doux(x):
    """De 0 à 1 en douceur, pour un geste qui part et s'arrête sans à-coup."""
    x = borne(x)
    return x * x * (3 - 2 * x)


def tour(axe, degres):
    """La rotation de « degres » autour d'un axe, en matrice 3 × 3."""
    x, y, z = np.asarray(axe, float) / np.linalg.norm(axe)
    a = math.radians(degres)
    c, s, u = math.cos(a), math.sin(a), 1 - math.cos(a)
    return np.array([[c + x * x * u, x * y * u - z * s, x * z * u + y * s],
                     [y * x * u + z * s, c + y * y * u, y * z * u - x * s],
                     [z * x * u - y * s, z * y * u + x * s, c + z * z * u]])


def angles(R):
    """Les angles qu'attend Pose (degrés, autour des axes du monde : X, puis Y, puis Z) pour la rotation R."""
    return (math.degrees(math.atan2(R[2, 1], R[2, 2])), math.degrees(math.asin(-max(-1.0, min(1.0, R[2, 0])))),
            math.degrees(math.atan2(R[1, 0], R[0, 0])))


def vers_(a, b):
    """La plus petite rotation qui couche la direction a sur la direction b."""
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    axe = np.cross(a, b)
    if np.linalg.norm(axe) < 1e-9:
        return np.eye(3)
    return tour(axe, math.degrees(math.atan2(np.linalg.norm(axe), a @ b)))


def _cadre(a, n):
    """Un repère en colonnes : la direction a, la normale n du plan où plie la patte, et la troisième."""
    a = a / np.linalg.norm(a)
    n = n / np.linalg.norm(n)
    return np.column_stack([a, n, np.cross(a, n)])


def cloue(nom, R, monte):
    """Les rotations de la cuisse et de la jambe qui gardent le pied d'une patte posée là où il est cousu quand le
    thorax tourne de R et monte de « monte » : le genou se replie dans le plan où il plie déjà."""
    H, Kn, F = FIL[nom][0], FIL[nom][1], FIL[nom][2]
    H2 = R @ (H - CORPS) + CORPS + monte
    la, lb = float(np.linalg.norm(Kn - H)), float(np.linalg.norm(F - Kn))
    d = F - H2
    D = min(max(float(np.linalg.norm(d)), abs(la - lb) + 1e-4), la + lb - 1e-4)
    d = d / np.linalg.norm(d)
    x = (la * la - lb * lb + D * D) / (2 * D)
    guide = R @ (Kn - H)
    m = guide - (guide @ d) * d
    K2 = H2 + d * x + m / np.linalg.norm(m) * math.sqrt(max(la * la - x * x, 0.0))
    n0, n2 = np.cross(Kn - H, F - Kn), np.cross(K2 - H2, F - K2)
    cuisse = _cadre(K2 - H2, n2) @ _cadre(Kn - H, n0).T
    jambe = _cadre(F - K2, n2) @ _cadre(F - Kn, n0).T
    return R.T @ cuisse, cuisse.T @ jambe


def tete(hoche=0.0, tourne=0.0, penche=0.0):
    """La rotation de la tête autour de ses axes à elle : hoche > 0, le nez plonge ; tourne > 0, elle regarde vers
    sa gauche ; penche > 0, elle se couche sur son épaule gauche."""
    return tour(T3[:, 2], tourne) @ tour(T3[:, 0], hoche) @ tour(T3[:, 1], penche)


def campe(p, R=np.eye(3), monte=(0.0, 0.0, 0.0), Rt=np.eye(3), pointe=None, posees=POSEES):
    """Pose le thorax (tourné de R, monté de « monte ») et la tête (Rt), en gardant les pieds des pattes posées au
    sol et, si on la donne, la pointe de la trompe sur ce point : il s'y appuie comme sur une canne."""
    monte = np.asarray(monte, float)
    p.add("corps", rot=angles(R), pos=tuple(monte))
    p.add("tete", rot=angles(Rt))
    if pointe is not None:
        Rm = R @ Rt                                              # la tête, dans le monde
        base = R @ (Rt @ (BASE - COU) + COU - CORPS) + CORPS + monte
        # la trompe est raide : on vise, dans la direction du point voulu, l'endroit à sa hauteur qu'elle touche juste
        long_, haut = float(np.linalg.norm(POINTE - BASE)), base[2] - pointe[2]
        plat = (np.asarray(pointe, float) - base) * [1, 1, 0]
        vise = base + plat / np.linalg.norm(plat) * math.sqrt(max(long_ * long_ - haut * haut, 0.0)) - [0, 0, haut]
        p.add("trompe", rot=angles(Rm.T @ vers_(Rm @ (POINTE - BASE), vise - base) @ Rm))
    for nom in posees:
        cuisse, jambe = cloue(nom, R, monte)
        p.add("cuisse_" + nom, rot=angles(cuisse))
        p.add("jambe_" + nom, rot=angles(jambe))


def ailes(p, ouvre, bat, rabat=0.0):
    """Les ailes : « ouvre » les écarte du dos vers l'horizontale (degrés, autour de l'axe du thorax) et les ramène
    en travers ; « bat » s'y ajoute (le battement) ; « rabat » les couche en arrière sur l'abdomen."""
    for l, c in (("g", 1), ("d", -1)):
        R = tour(B3[:, 1], c * (ouvre + bat)) @ tour(B3[:, 2], -c * 0.45 * ouvre) @ tour(B3[:, 0], -rabat) @ tour(B3[:, 1], -c * 0.3 * rabat)
        p.add("aile_" + l, rot=angles(R))


def pend(p, air):
    """En vol, les six pattes pendent sous lui et traînent en arrière, les genoux dépliés : air de 0 (posé) à 1."""
    for nom in PATTES:
        c = 1 if nom.endswith("g") else -1
        devant = {"avant": 0, "milieu": 1, "arriere": 2}[nom[:-2]]
        p.add("cuisse_" + nom, rot=angles(tour(B3[:, 0], -(25 + 30 * devant) * air) @ tour(B3[:, 1], c * 35 * air)))
        p.add("jambe_" + nom, rot=angles(tour(B3[:, 0], (55 - 10 * devant) * air)))


def repos(t):
    """L'air de rien : il se balance sur ses longues pattes, appuyé sur sa trompe comme sur une canne, la tête qui
    se tourne vers nous puis se détourne ; il lève l'une après l'autre ses pattes arrière au-dessus du dos et les
    agite (il mijote quelque chose), fait frémir ses ailes ; l'abdomen respire, les antennes tâtent l'air, il cligne."""
    p = Pose()
    r = onde(t, 2)
    berce = onde(t, 1)
    regard = cloche(t, 0.20, 0.12) - cloche(t, 0.70, 0.10)
    campe(p, tour(B3[:, 1], 2.5 * berce) @ tour(B3[:, 0], 1.5 * r), (0.0, 0.0, 0.003 * r), tete(-4 * cloche(t, 0.20, 0.12), 14 * regard, -5 * regard), POINTE)
    for l, c, quand in (("g", 1, 0.42), ("d", -1, 0.56)):
        leve = cloche(t, quand, 0.09)
        p.add("cuisse_arriere_" + l, rot=angles(tour(B3[:, 1], c * 28 * leve) @ tour(B3[:, 0], -22 * leve)))
        p.add("jambe_arriere_" + l, rot=angles(tour(B3[:, 0], 22 * leve * onde(t, 9)) @ tour(B3[:, 1], c * 14 * leve)))
    p.add("abdomen", rot=angles(tour(B3[:, 0], 2 * r)), ech=(1 + 0.03 * r, 1, 1 + 0.03 * r))
    ailes(p, 0.0, 4 * cloche(t, 0.90, 0.05) * onde(t, 30, 0.25))
    p.add("antenne_g", rot=(7 * onde(t, 3), 0, 5 * onde(t, 2)))
    p.add("antenne_d", rot=(-7 * onde(t, 4), 0, 5 * onde(t, 2)))
    p.ouvert = 1 - cloche(t, 0.30, 0.02) - cloche(t, 0.84, 0.02)
    return p


def avance(t):
    """Il vole sur place : le corps flotte en l'air et tangue à peine, les ailes vibrent (dix battements par boucle),
    les longues pattes pendent et traînent, la trompe pointe devant lui, les antennes frémissent."""
    p = Pose()
    h = onde(t, 1)
    campe(p, tour(B3[:, 0], -14 + 2 * onde(t, 1, 0.25)) @ tour(B3[:, 1], 3 * onde(t, 2)), (0.0, 0.0, 0.16 + 0.010 * h),
          tete(-10 - 2 * onde(t, 1, 0.25)), posees=())
    p.add("trompe", rot=angles(tour(T3[:, 0], -12)))
    ailes(p, 58, 34 * onde(t, 10))
    pend(p, 1.0)
    p.add("abdomen", rot=angles(tour(B3[:, 0], -10 + 3 * onde(t, 1, 0.5))))
    p.add("antenne_g", rot=(4 * onde(t, 5), 0, 0))
    p.add("antenne_d", rot=(4 * onde(t, 5, 0.3), 0, 0))
    return p


def mange(t):
    """Il pique : penché sur sa trompe, il la relève et la plante d'un coup, cinq fois ; à chaque gorgée l'abdomen
    gonfle et les pattes arrière se dressent d'aise ; puis il se redresse, repu, et l'abdomen dégonfle."""
    p = Pose()
    leve = cloche(t, 0.88, 0.10)
    bas = 1 - leve
    pique = max(0.0, onde(t, 5, 0.25)) ** 3 * bas            # la trompe en l'air entre deux coups
    plein = doux(t / 0.8) * (1 - doux((t - 0.84) / 0.14))
    campe(p, tour(B3[:, 0], 9 * bas - 3 * leve), (0.0, 0.0, -0.006 * bas), tete(14 * bas - 8 * pique - 6 * leve, 8 * leve * onde(t, 3)),
          POINTE + [0.0, 0.010 * pique, 0.030 * pique])
    p.add("abdomen", rot=angles(tour(B3[:, 0], 6 * plein)), ech=(1 + 0.22 * plein, 1 + 0.08 * plein, 1 + 0.22 * plein))
    for l, c in (("g", 1), ("d", -1)):
        p.add("cuisse_arriere_" + l, rot=angles(tour(B3[:, 0], 10 * plein + 6 * pique)))
    ailes(p, 0.0, 5 * pique * onde(t, 30, 0.25))
    p.add("antenne_g", rot=(10 * bas + 6 * pique, 0, 0))
    p.add("antenne_d", rot=(10 * bas + 6 * pique, 0, 0))
    p.ouvert = 1 - 0.4 * plein * bas                              # l'œil mi-clos de plaisir
    return p


def joie(t):
    """Il décolle d'un bond en vrombissant, fait une pirouette en l'air les pattes au vent, et se repose d'aplomb,
    l'air de rien."""
    p = Pose()
    air = doux(t / 0.16) * (1 - doux((t - 0.70) / 0.20))
    pirouette = doux((t - 0.16) / 0.52)
    campe(p, tour(B3[:, 0], -10 * air), (0.0, 0.0, 0.12 * air), tete(-12 * air), posees=())
    p.add("corps", rot=(0, 0, 360 * pirouette))                  # le tour sur lui-même, ajouté à part : l'angle reste continu
    pend(p, air)
    for l, c in (("g", 1), ("d", -1)):
        p.add("cuisse_arriere_" + l, rot=angles(tour(B3[:, 1], c * 30 * air * onde(t, 4))))
    p.add("trompe", rot=angles(tour(T3[:, 0], -20 * air)))
    ailes(p, 58 * air, 34 * air * onde(t, 10))
    p.add("abdomen", rot=angles(tour(B3[:, 0], 12 * air * onde(t, 3))))
    p.add("antenne_g", rot=(-14 * air, 0, 0))
    p.add("antenne_d", rot=(-14 * air, 0, 0))
    return p


def dort(t):
    """Il dort debout, posé sur ses longues pattes : le corps descendu entre les genoux, la tête qui pique du nez,
    la trompe posée au sol, les ailes couchées sur l'abdomen, les pattes arrière retombées ; les yeux fermés,
    l'abdomen respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    campe(p, tour(B3[:, 0], 4), (0.0, 0.0, -0.035 - 0.002 * r), tete(16 + 2 * r, 0.0, 8), POINTE + [0.0, -0.010, 0.0])
    p.add("abdomen", rot=angles(tour(B3[:, 0], -26)), ech=(1 + 0.03 * r, 1, 1 + 0.03 * r))
    ailes(p, 0.0, 0.0, 40)
    for l, c in (("g", 1), ("d", -1)):
        p.add("cuisse_arriere_" + l, rot=angles(tour(B3[:, 0], -40)))
        p.add("jambe_arriere_" + l, rot=angles(tour(B3[:, 0], -30)))
    p.add("antenne_g", rot=(30 + 2 * r, 0, 0))
    p.add("antenne_d", rot=(30 + 2 * r, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Moustique")
