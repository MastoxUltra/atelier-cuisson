"""La sauterelle en peluche : rose vif (elles existent), le ventre crème, deux cuisses immenses repliées en Z dont les
genoux jaunes pointent bien au-dessus du dos, une selle mûre derrière la tête, des ailes en étui et deux antennes
interminables. Nerveuse : ramassée sur l'avant, une patte en l'air, la tête tournée d'un coup vers nous, prête à bondir.

    python sauterelle.py        fabrique la fiche art/apercus/animaux/sauterelle.png
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

ROSE = M.hexa("#ff8ac6")                      # le rose vif du poil (il fonce et se sature une fois en peluche)
BONBON = M.hexa("#ff9ccb")                    # la feutrine des ailes, un ton plus clair
MURE = M.hexa("#8f1c58")                      # les tibias, les antennes, la selle, les nervures
CROUPE = Vector((0.0, 0.105, 0.096))          # le bout arrière de l'abdomen ; le corps file de là vers l'avant, en piquant du nez
PIQUE = math.radians(11)
AXE = Vector((0.0, -math.cos(PIQUE), -math.sin(PIQUE)))
DOS = Vector((0.0, -math.sin(PIQUE), math.cos(PIQUE)))             # le dessus du corps
TETE = Vector((0.0, -0.110, 0.088))
PORT = A.repere(TETE, (16, 9, 30))            # la tête : le front en avant, penchée, tournée d'un coup vers nous


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête, rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def tube_peint(chemin, rayon, paliers, cotes=12):
    """Un tube peint par tronçons le long de son fil : paliers = [(fraction du chemin, couleur), ...], la dernière
    fraction à 1 ou plus. Le chemin est recoupé tous les 4 mm pour que la limite des couleurs reste nette."""
    ch = np.asarray(chemin, float)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(ch, axis=0), axis=1))])
    t = np.linspace(0.0, 1.0, max(6, int(fait[-1] / 0.004)))
    ch = np.stack([np.interp(t * fait[-1], fait, ch[:, k]) for k in range(3)], axis=1)
    m = A.tube(ch, rayon, cotes)
    t = np.concatenate([np.repeat(t, cotes), [0.0, 1.0]])           # les anneaux du tube, puis ses deux bouchons
    m.teinte = np.zeros((len(t), 3))
    for seuil, couleur in reversed(paliers):
        m.teinte[t <= seuil] = couleur
    return m


def construire():
    a = K.Animal("sauterelle")
    a.taille = 0.36
    a.tete = PORT @ Vector((0, -0.036, 0.0))

    # ----- le corps : un fuseau tourné de la croupe au cou, le thorax plus haut que large ; rose dessus, crème dessous -----
    corps = A.tour(A.profil([(0, 0), (0.011, 0.006), (0.021, 0.040), (0.029, 0.085), (0.035, 0.130), (0.038, 0.165), (0.033, 0.190), (0, 0.200)], 6), 48)

    def thorax(v):
        s = v.copy()
        s[:, 1] *= 1 + 0.18 * K.lisse((v[:, 2] - 0.095) / 0.06)
        return s
    corps = K.bandes(corps.sculpte(thorax), [(-0.012, K.CREME), (9, ROSE)], axe=1)
    a.piece("corps", corps, None, pos=CROUPE, rot=(90 + math.degrees(PIQUE), 0, 0))
    # la selle : le corselet des sauterelles, un morceau de feutrine mûre à cheval sur le thorax
    a.rustine("selle", "corps", CROUPE + AXE * 0.150, DOS, lambda th: 0.50 + 0.80 * math.cos(th) ** 2, MURE, 0.003, 22)

    # ----- la tête : une longue tête de cheval, deux bosses en haut pour les yeux, le menton étroit, le museau crème -----
    def crane(v):
        v = K.bosse(K.bosse(v, (0.70, -0.40, 0.58), 0.12, 0.18), (-0.70, -0.40, 0.58), 0.12, 0.18)
        s = v * [0.036, 0.034, 0.058]
        s[:, 0] *= 1 - 0.34 * K.lisse(-1.2 * v[:, 2])
        return s
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(crane), ROSE, mat=PORT)
    a.rustine("museau", "tete", TETE, vers(0, -0.84, -0.54), lambda th: 0.80 + 0.10 * math.cos(2 * th), K.CREME, 0.003, 18)
    # les yeux, haut perchés, et sur le front deux sourcils courts qui remontent vers le milieu : elle s'inquiète de tout
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, vers(0.62 * cote, -0.46, 0.70))
        a.bouton("oeil_" + nom, p + n * 0.003, n, 0.0150)
        sourcil = a.trace("tete", TETE, [vers(0.033 * cote, -0.008, 0.043), vers(0.020 * cote, -0.013, 0.050), vers(0.008 * cote, -0.017, 0.055)], 0.0048)
        a.broderie("sourcil_" + nom, sourcil, 0.0027, MURE)
    # la bouche : un petit trait qui tremble, de travers sur le museau
    tremble = [vers(-0.32 + 0.16 * i, -0.80, -0.66 + (0.05 if i % 2 else 0.0) + 0.015 * i) for i in range(5)]
    a.broderie("bouche", a.trace("tete", TETE, tremble, 0.0048), 0.0022, MURE)

    # ----- les antennes : deux fouets interminables, jamais d'accord ; celle de gauche tâte l'air, basse et loin sur le côté,
    #       celle de droite monte haut et part en arrière -----
    for nom, cote, fouet in (("G", 1, ((0.016, 0.006, 0.050), (0.046, 0.022, 0.092), (0.082, 0.046, 0.118), (0.116, 0.074, 0.126))),
                             ("D", -1, ((-0.016, 0.004, 0.054), (-0.042, 0.018, 0.104), (-0.074, 0.044, 0.142), (-0.104, 0.078, 0.160)))):
        pied = PORT @ Vector((0.014 * cote, 0.004, 0.054))
        fil = A.courbe([pied] + [pied + Vector(q) for q in fouet], 8)
        a.piece("antenne_" + nom, A.tube(fil, lambda t: 0.0046 - 0.0024 * t, 12), MURE, poil=False)

    # ----- les ailes : deux lames de feutrine posées en toit sur le dos, qui dépassent loin derrière ; leurs nervures brodées -----
    lame = A.courbe([(0.0, -0.004), (0.06, 0.003), (0.14, 0.004), (0.205, 0.0), (0.224, -0.007), (0.20, -0.019),
                     (0.14, -0.033), (0.07, -0.037), (0.02, -0.027)], 5, fermee=True)
    toit = A.repere((0.003, -0.038, 0.116), (4, 0, 0)) @ A.cadre((0, 0, 0), (0.82, 0, 0.57), (-0.57, 0, 0.82))
    a.piece("aile", A.decoupe(lame, 0.005, 0.002), BONBON, mat=toit, poil=False, paire=True)
    for i, nervure in enumerate((((0.015, -0.016), (0.11, -0.016), (0.212, -0.007)), ((0.055, -0.016), (0.085, -0.031)),
                                 ((0.105, -0.016), (0.138, -0.029)), ((0.155, -0.013), (0.185, -0.022)))):
        a.broderie("nervure%d" % i, [toit @ Vector((u, w, 0.0036)) for u, w in nervure], 0.0015, MURE, paire=True)

    # ----- les pattes sauteuses : une cuisse en massue qui monte loin derrière, cousue sur sa tranche, un genou jaune tout
    #       en haut, puis un tibia mûre replié contre elle jusqu'au sol. Celle de droite est moins serrée : elle piétine -----
    cuisse = A.tour(A.profil([(0, 0), (0.020, 0.008), (0.027, 0.038), (0.023, 0.076), (0.014, 0.126), (0.0085, 0.172), (0, 0.180)], 6), 40)
    for nom, hanche, genou, cheville, orteil in (("G", (0.028, -0.013, 0.070), (0.060, 0.105, 0.212), (0.070, 0.040, 0.016), (0.074, -0.004, 0.0075)),
                                                 ("D", (-0.028, -0.013, 0.070), (-0.062, 0.122, 0.190), (-0.074, 0.064, 0.016), (-0.078, 0.020, 0.0075))):
        elan = Vector(genou) - Vector(hanche)
        long, elan = elan.length + 0.008, elan.normalized()
        m = cuisse.copie().etire(1.0, 0.72, long / 0.180)
        a.piece("cuisse_" + nom, m, ROSE, mat=A.cadre(Vector(hanche) - elan * 0.008, elan, (1, 0, 0)))
        a.couture("cuisse_" + nom, "cuisse_" + nom, 0, 0.12, 0.86, large=0.007, haut=0.003, pas=0.011)
        tibia = A.conges([tuple(Vector(genou) - elan * 0.004), cheville, orteil], 0.010, 5)
        a.piece("tibia_" + nom, tube_peint(tibia, lambda t: 0.0066 + 0.0062 * math.exp(-(t / 0.05) ** 2) - 0.0014 * t,
                                           [(0.085, K.JAUNE), (9, MURE)]), None, poil=False)

    # ----- les quatre pattes de devant, fines et pliées : le corps est ramassé dessus. L'avant gauche est levée, hésitante -----
    marche = None
    for points in (((0.022, -0.078, 0.038), (0.058, -0.100, 0.092), (0.068, -0.142, 0.080), (0.066, -0.160, 0.062)),
                   ((-0.022, -0.078, 0.038), (-0.062, -0.092, 0.074), (-0.072, -0.128, 0.013), (-0.076, -0.152, 0.0068)),
                   ((0.026, -0.046, 0.036), (0.074, -0.040, 0.078), (0.094, -0.036, 0.013), (0.112, -0.044, 0.0068)),
                   ((-0.026, -0.046, 0.036), (-0.072, -0.034, 0.076), (-0.090, -0.020, 0.013), (-0.108, -0.024, 0.0068))):
        une = A.tube(A.conges(points, 0.009, 4), lambda t: 0.0074 - 0.0024 * t, 12)
        marche = une if marche is None else marche + une
    a.piece("pattes", marche, MURE, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py sauterelle). Les mesures sont celles du modèle, avant a.taille.

from poses import Pose, borne, cloche, onde

# Les pattes sauteuses ont deux os chacune, la cuisse (de la hanche au genou jaune) et le tibia (du genou au pied) :
# le pied reste planté pendant que le corps s'accroupit puis se détend, et la jambe se déplie pour le bond. Les deux
# genoux ne sont pas à la même place (celle de droite piétine) et la tête est tournée de 30° : cuisses, tibias et
# antennes ont chacun leur os à sa vraie place, nommés _g et _d, sans miroir. Les quatre pattes de devant sont une seule
# pièce (pattes) : chaque point suit la patte dont le fil passe le plus près ; leurs hanches sont symétriques (os en _G,
# recopiés en _D) et elles pendent à la racine : un pied posé ne bouge pas quand le corps bouge au-dessus de lui.
BASSIN = np.array((0.0, -0.010, 0.075))       # le pivot du corps : entre les hanches des pattes sauteuses
# les pattes sauteuses telles que construire() les dessine, vues de côté (y, z) : la hanche, le genou, la cheville
JARRETS = {"g": (np.array((-0.013, 0.070)), np.array((0.105, 0.212)), np.array((0.040, 0.016))),
           "d": (np.array((-0.013, 0.070)), np.array((0.122, 0.190)), np.array((0.064, 0.016)))}
# les quatre pattes de devant (les mêmes points que dans construire) : la hanche, le genou, le pied, l'orteil
FILS = {"avant_G": [(0.022, -0.078, 0.038), (0.058, -0.100, 0.092), (0.068, -0.142, 0.080), (0.066, -0.160, 0.062)],
        "avant_D": [(-0.022, -0.078, 0.038), (-0.062, -0.092, 0.074), (-0.072, -0.128, 0.013), (-0.076, -0.152, 0.0068)],
        "milieu_G": [(0.026, -0.046, 0.036), (0.074, -0.040, 0.078), (0.094, -0.036, 0.013), (0.112, -0.044, 0.0068)],
        "milieu_D": [(-0.026, -0.046, 0.036), (-0.072, -0.034, 0.076), (-0.090, -0.020, 0.013), (-0.108, -0.024, 0.0068)]}
FILS = {n: [np.array(q, float) for q in f] for n, f in FILS.items()}

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", tuple(BASSIN)),                        # le milieu du fuseau, au-dessus des hanches
    ("tete", "corps", (-0.010, -0.088, 0.094)),                # la nuque, sous la selle
    ("antenne_g", "tete", (0.025, -0.109, 0.138)),             # le pied des antennes (la tête est tournée : pas de miroir)
    ("antenne_d", "tete", (0.001, -0.122, 0.143)),
    ("ailes_G", "corps", (0.006, -0.036, 0.112)),              # la racine des ailes, devant, sur le dos
    ("cuisse_g", "corps", (0.028, -0.013, 0.070)),             # la hanche d'une patte sauteuse
    ("cuisse_d", "corps", (-0.028, -0.013, 0.070)),
    ("tibia_g", "cuisse_g", (0.060, 0.105, 0.212)),            # le genou jaune, tout en haut
    ("tibia_d", "cuisse_d", (-0.062, 0.122, 0.190)),
    ("patte_avant_G", "racine", tuple(FILS["avant_G"][0])),    # les hanches des pattes de devant
    ("patte_milieu_G", "racine", tuple(FILS["milieu_G"][0])),
]


def _cote(nom):
    """Une pièce d'un côté (cuisse_G, tibia_D) suit l'os de son côté (cuisse_g, tibia_d)."""
    return lambda points, cote: {nom + cote.lower(): np.ones(len(points))}


def _pattes(points, cote):
    """Les quatre pattes de devant, une seule pièce : chaque point suit la patte dont le fil passe le plus près."""
    ecarts = []
    for n in FILS:
        e = np.full(len(points), 9.0)
        for a, b in zip(FILS[n][:-1], FILS[n][1:]):
            u = np.clip((points - a) @ (b - a) / ((b - a) @ (b - a)), 0.0, 1.0)
            e = np.minimum(e, np.linalg.norm(points - a - u[:, None] * (b - a), axis=1))
        ecarts.append(e)
    proche = np.argmin(ecarts, axis=0)
    return {"patte_" + n: (proche == k).astype(float) for k, n in enumerate(FILS)}


PORTEURS = [("corps", "corps"), ("selle", "corps"),
            ("tete", "tete"), ("museau", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("bouche", "tete"),
            ("antenne", _cote("antenne")), ("aile", "ailes", True), ("nervure", "ailes", True),
            ("cuisse", _cote("cuisse")), ("tibia", _cote("tibia")), ("pattes", _pattes),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


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


def _angle(v):
    return math.atan2(v[1], v[0])


def jarret(p, l, pique, monte, leve=0.0, sol=1.0):
    """Une patte sauteuse, son pied planté : le corps a piqué de « pique » degrés (> 0, le nez descend) et s'est
    déplacé de « monte » (y, z) ; on plie la cuisse et le tibia pour que la cheville reste où elle est cousue, ou
    monte de « leve ». Tout se passe de profil (des rotations autour de X ne changent pas x), le genou reste plié du
    même côté. sol : 1 le pied est planté, 0 la jambe reste repliée contre le corps (en l'air), entre les deux en douceur."""
    H, K, F = JARRETS[l]
    th = math.radians(pique)
    r = H - BASSIN[1:]
    H2 = BASSIN[1:] + (r[0] * math.cos(th) - r[1] * math.sin(th), r[0] * math.sin(th) + r[1] * math.cos(th)) + np.asarray(monte, float)
    cible = F + (0.0, leve)
    a, b = float(np.linalg.norm(K - H)), float(np.linalg.norm(F - K))
    d = cible - H2
    D = min(max(float(np.linalg.norm(d)), abs(a - b) + 1e-4), a + b - 1e-4)
    u = d / np.linalg.norm(d)
    x = (a * a - b * b + D * D) / (2 * D)
    sens = math.copysign(1.0, (F - H)[0] * (K - H)[1] - (F - H)[1] * (K - H)[0])
    K2 = H2 + u * x + np.array((-u[1], u[0])) * math.sqrt(max(a * a - x * x, 0.0)) * sens
    cuisse = math.degrees(_angle(K2 - H2) - _angle(K - H))
    tibia = math.degrees(_angle(H2 + u * D - K2) - _angle(F - K))
    p.add("cuisse_" + l, rot=(sol * (cuisse - pique), 0, 0))
    p.add("tibia_" + l, rot=(sol * (tibia - cuisse), 0, 0))


def corps(p, pique=0.0, monte=(0.0, 0.0), ech=(1, 1, 1), leve=(0.0, 0.0), sol=1.0):
    """Pose le corps (« pique » > 0, le nez descend ; monte = (y, z)) et plante les deux pattes sauteuses sous lui ;
    leve = de combien chaque cheville (gauche, droite) quitte le sol."""
    p.add("corps", rot=(pique, 0, 0), pos=(0, monte[0], monte[1]), ech=ech)
    jarret(p, "g", pique, monte, leve[0], sol)
    jarret(p, "d", pique, monte, leve[1], sol)


def devant(p, nom, arriere=0.0, leve=0.0, suit=0.0, pique=0.0, monte=(0.0, 0.0)):
    """Une patte de devant sur sa hanche : « arriere » degrés vers l'arrière (autour de la verticale), « leve » degrés
    vers le haut (le pied monte en s'écartant). suit (0 à 1) : la part du mouvement du corps qu'elle suit (en l'air)."""
    H, F = FILS[nom][0], FILS[nom][2]
    c = 1 if nom.endswith("G") else -1
    R = tour((0, 0, 1), c * arriere) @ tour(np.cross((F - H) * [1, 1, 0], (0, 0, 1)), leve)
    Rc = tour((1, 0, 0), pique)
    pos = Rc @ (H - BASSIN) + BASSIN + (0, monte[0], monte[1]) - H
    sol, air = np.array(angles(R)), np.array(angles(Rc @ R))
    p.add("patte_" + nom, rot=tuple(sol + (air - sol) * suit), pos=tuple(pos * suit))


def antennes(p, g, d, fouet=(0.0, 0.0)):
    """Les antennes : de combien chacune se couche en arrière (degrés) et de combien elle fouette de côté."""
    p.add("antenne_g", rot=(-g, 0, fouet[0]))
    p.add("antenne_d", rot=(-d, 0, fouet[1]))


def repos(t):
    """Nerveuse : elle respire vite, tourne la tête d'un coup vers un bruit, puis vers nous, puis ailleurs ; elle chante
    en frottant sa cuisse gauche (le pied qui scie l'air), tâte le sol de sa patte avant levée, et sursaute pour rien,
    prête à bondir. Les antennes ne tiennent pas en place ; elle cligne vite."""
    p = Pose()
    r = onde(t, 4)
    chante = cloche(t, 0.52, 0.10)
    sursaut = cloche(t, 0.84, 0.03)
    corps(p, 1.5 * sursaut, (0, -0.004 * sursaut), ech=(1 + 0.010 * r, 1, 1 + 0.016 * r),
          leve=(0.008 * chante * (1 + onde(t, 24)), 0.0))
    p.add("tete", rot=(0, 0, -22 * cloche(t, 0.16, 0.05) + 14 * cloche(t, 0.34, 0.05) - 10 * cloche(t, 0.72, 0.04)))
    tape = cloche(t, 0.64, 0.025) + cloche(t, 0.70, 0.025)
    devant(p, "avant_G", -6 * tape, -30 * tape)
    antennes(p, 8 * onde(t, 3) + 10 * sursaut, -6 * onde(t, 2, 0.3), (6 * onde(t, 5), 5 * onde(t, 3, 0.2)))
    p.paire("ailes", rot=(3 * chante * onde(t, 24, 0.25), 0, 0))
    p.ouvert = 1 - cloche(t, 0.08, 0.015) - cloche(t, 0.44, 0.015) - cloche(t, 0.90, 0.015)
    return p


def avance(t):
    """Elle avance par bonds : elle s'accroupit, les cuisses se détendent d'un coup, les tibias se déplient et la
    lancent en l'air, le nez levé ; en vol les ailes frémissent et les jambes se replient ; elle se reçoit sur les
    pattes de devant, le nez baissé, tasse, et repart."""
    p = Pose()
    accroupi = cloche(t, 0.14, 0.12) + 0.6 * cloche(t, 0.90, 0.08)
    vol = math.sin(math.pi * borne((t - 0.20) / 0.62)) if 0.20 < t < 0.82 else 0.0
    sol = 1 - K.lisse(np.array((t - 0.30) / 0.10)).item() + K.lisse(np.array((t - 0.70) / 0.10)).item()
    suit = K.lisse(np.array((t - 0.24) / 0.10)).item() - K.lisse(np.array((t - 0.74) / 0.08)).item()
    pique = 3 * accroupi - 9 * cloche(t, 0.36, 0.14) + 7 * cloche(t, 0.70, 0.10)
    monte = (0.0, -0.008 * accroupi + 0.070 * vol)
    corps(p, pique, monte, sol=sol)
    for l in ("g", "d"):                                     # en l'air : la jambe se détend derrière, puis se replie
        p.add("tibia_" + l, rot=(26 * cloche(t, 0.40, 0.10) * (1 - sol), 0, 0))
    for nom in FILS:
        devant(p, nom, -14 * vol, 14 * vol, suit, pique, monte)
    p.add("tete", rot=(-pique * 0.6, 0, 0))
    antennes(p, 18 * vol, 18 * vol)
    p.paire("ailes", rot=(10 * vol + 5 * vol * onde(t, 12), 0, -6 * vol))
    return p


def mange(t):
    """Elle baisse le nez sur un brin d'herbe et le grignote à toute vitesse, la tête qui hache menu, les pattes de
    devant qui le tiennent ; un coup d'œil inquiet de côté, puis elle relève la tête."""
    p = Pose()
    bas = 1 - cloche(t, 0.88, 0.12)
    hache = abs(onde(t, 10)) * bas
    corps(p, 7 * bas)
    p.add("tete", rot=(18 * bas + 6 * hache, 0, 14 * cloche(t, 0.50, 0.05)))
    for nom in ("avant_G", "avant_D"):
        devant(p, nom, -10 * bas, 6 * bas + 3 * hache)
    antennes(p, -6 * bas, -4 * bas, (4 * hache, -4 * hache))
    p.ouvert = 1 - cloche(t, 0.30, 0.015) - cloche(t, 0.93, 0.02)
    return p


def joie(t):
    """Un saut de joie : accroupie, elle s'envole bien plus haut qu'à l'ordinaire, les ailes roses grandes ouvertes qui
    vrombissent, donne en l'air deux ruades de ses grandes jambes, et retombe en tassant."""
    p = Pose()
    accroupi = cloche(t, 0.10, 0.09, False) + 0.8 * cloche(t, 0.84, 0.08, False)
    vol = math.sin(math.pi * borne((t - 0.16) / 0.62)) if 0.16 < t < 0.78 else 0.0
    sol = 1 - K.lisse(np.array((t - 0.22) / 0.08)).item() + K.lisse(np.array((t - 0.68) / 0.08)).item()
    suit = K.lisse(np.array((t - 0.18) / 0.08)).item() - K.lisse(np.array((t - 0.70) / 0.08)).item()
    pique = 3 * accroupi - 14 * vol
    monte = (0.0, -0.010 * accroupi + 0.140 * vol)
    corps(p, pique, monte, sol=sol)
    ruade = cloche(t, 0.40, 0.06, False) + cloche(t, 0.54, 0.06, False)
    for l in ("g", "d"):
        p.add("cuisse_" + l, rot=(-10 * ruade, 0, 0))
        p.add("tibia_" + l, rot=(40 * ruade, 0, 0))
    for nom in FILS:
        devant(p, nom, -16 * vol, 18 * vol, suit, pique, monte)
    p.add("tete", rot=(-0.5 * pique, 0, 0))
    antennes(p, 24 * vol, 24 * vol)
    p.paire("ailes", rot=(34 * vol + 8 * vol * onde(t, 16), 0, -30 * vol))
    return p


def dort(t):
    """Tassée au ras de l'herbe, les grandes cuisses repliées haut, la tête basse, les antennes retombées en arrière
    le long du dos ; les yeux fermés, elle respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    corps(p, 3, (0.0, -0.008 - 0.001 * r), ech=(1 + 0.012 * r, 1, 1 + 0.018 * r))
    p.add("tete", rot=(12 + 1.0 * r, 0, -10))
    antennes(p, 30, 22)
    devant(p, "avant_G", 0, -24)
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Sauterelle")
