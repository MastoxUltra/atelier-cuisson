"""La mouffette en peluche, deuxième dessin : noir charbon, et tout son signe en blanc. Une liste part du bout du
museau, s'ouvre en calotte sur le crâne, coule sur la nuque, se fend en deux bandes le long du dos, se referme sur la
croupe et monte par la face extérieure du panache, énorme, dressé, qui bascule vers l'avant et blanchit jusqu'à la pointe.
Vive et insolente : longue et basse, la croupe haute, elle avance une patte (l'antérieur gauche levé), tourne vers nous
un museau pointu, le menton haut ; un œil plissé sous une paupière lourde, l'autre grand ouvert sous un sourcil levé,
et le coin de la bouche en biais. Pas de rapiéçage, pas de boutons : des yeux vivants.

    python mouffette.py        fabrique la fiche art/apercus/animaux/mouffette.png (dans le style de son palier : voir styles.py)
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

CHARBON = M.hexa("#2b2a31")                   # un noir de charbon, pas un noir pur : le poil doit garder du relief
NEIGE = K.BLANC
FUMEE = M.hexa("#8d8a92")                     # les griffes, le coin de la bouche
SUIE = M.hexa("#46434c")                      # le dedans des oreilles
FIL = M.hexa("#e4e1dc")                       # les sourcils et le coin de la bouche, brodés sur le charbon
TOURNE = 0                                    # -36 la posait de profil sur la fiche ; 0 pour le jeu (l'usine l'exige)

# L'échine, de la croupe au cou : la croupe haute, le dos presque droit, puis le cou qui se redresse.
ECHINE = [(0.0, 0.205, 0.200), (0.0, 0.125, 0.238), (0.0, 0.020, 0.232), (0.0, -0.070, 0.236), (0.0, -0.128, 0.272)]
GALBE = [(0.0, 0.0), (0.03, 0.076), (0.10, 0.118), (0.25, 0.132), (0.45, 0.120), (0.65, 0.100), (0.82, 0.082), (0.93, 0.064), (0.985, 0.038), (1.0, 0.0)]
# Le panache : il sort du haut de la croupe, monte, s'arque et bascule vers l'avant, au-dessus du dos.
PANACHE = [(0.0, 0.150, 0.220), (0.0, 0.222, 0.305), (0.0, 0.262, 0.410), (0.0, 0.255, 0.505), (0.0, 0.205, 0.580),
           (0.0, 0.125, 0.614), (0.0, 0.045, 0.600), (0.0, -0.012, 0.560), (0.0, -0.044, 0.512)]
TOUFFE = [(0.0, 0.0), (0.02, 0.044), (0.12, 0.056), (0.30, 0.088), (0.48, 0.112), (0.62, 0.116), (0.75, 0.098), (0.86, 0.064), (0.94, 0.030), (0.985, 0.008), (1.0, 0.0)]
LACET, PIQUE, PENCHE = 50.0, -12.0, -12.0     # la tête : tournée vers nous, le menton levé, un rien penchée
GROSSE = 1.32                                 # une tête franche : c'est le visage qu'on lit de loin


def fil(chemin, flanc=None):
    """Prépare un chemin lissé : rend sa longueur, et repere(s) -> (centre, avant, dos, côté gauche) à la distance s
    du départ. Sans « flanc », le dos de la pièce cherche le ciel (un corps). Avec, c'est son côté gauche qui cherche
    cette direction : pour une queue qui se dresse puis retombe, dont le fil passe par la verticale."""
    pts = A.courbe(chemin, 16)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    sens = np.gradient(pts, fait, axis=0)

    def repere(s):
        s = np.asarray(s, float)
        centre = np.stack([np.interp(s, fait, pts[:, k]) for k in range(3)], axis=-1)
        avant = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
        if flanc is None:
            dos = np.array([0.0, 0.0, 1.0]) - avant[..., 2:3] * avant
            dos = dos / np.linalg.norm(dos, axis=-1, keepdims=True)
            return centre, avant, dos, np.cross(dos, avant)
        cote = np.asarray(flanc, float) - (avant @ np.asarray(flanc, float))[..., None] * avant
        cote = cote / np.linalg.norm(cote, axis=-1, keepdims=True)
        return centre, avant, np.cross(avant, cote), cote
    return float(fait[-1]), repere


def couche(repere, long):
    """Pour sculpte() : couche le long d'un fil une pièce tournée toute droite (son X : la gauche, son Y : le dos)."""
    def f(v):
        centre, avant, dos, cote = repere(np.clip(v[:, 2], 0.0, long))
        return centre + avant * (v[:, 2] - np.clip(v[:, 2], 0.0, long))[:, None] + v[:, 0:1] * cote + v[:, 1:2] * dos
    return f


def rayer(m, cotes, d1, d2, clair, sombre, n1, n2, eps=0.012):
    """Peint deux bandes claires, symétriques, sur une pièce tournée encore droite (son +Y est le dos) : à la cote z,
    chacune va de d1(z) à d2(z) radians de part et d'autre de la ligne du dos (d1 = 0 : elles n'en font qu'une ;
    d2 = pi : elles font tout le tour). Les méridiens sont tournés pour tomber pile sur les bords : la raie reste nette,
    sur le tissu comme sur le poil. n1 et n2 : le nombre de méridiens donnés, de chaque côté, à l'entre-deux sombre
    du dos et à la bande."""
    quart, demi = cotes // 4, cotes // 2
    m.teinte = np.tile(np.asarray(sombre, float), (len(m.v), 1))
    for anneau in m.anneaux:
        z = m.v[anneau[0], 2]
        a1, a2 = max(0.0, float(d1(z))), float(d2(z))
        bande, plein = a2 - a1 > 4 * eps, a2 > 3.05
        joint = bande and a1 <= eps
        if len(anneau) == 1:
            if joint or (bande and plein):
                m.teinte[anneau[0]] = clair
            continue
        a2 = min(max(a2, a1 + 4 * eps), math.pi - 6 * eps)
        ecart = np.concatenate([np.linspace(0.0, max(a1 - eps, 0.3 * eps), n1 + 1), np.linspace(max(a1 + eps, eps), a2 - eps, n2),
                                np.linspace(a2 + eps, math.pi, demi - n1 - n2)])
        r = np.hypot(m.v[anneau, 0], m.v[anneau, 1])
        for j, i in enumerate(anneau):
            k = (j - quart) % cotes
            signe = 1.0 if k <= demi else -1.0
            k = min(k, cotes - k)
            angle = math.pi / 2 + signe * ecart[k]
            m.v[i, 0], m.v[i, 1] = r[j] * math.cos(angle), r[j] * math.sin(angle)
            if (joint and k <= n1) or (bande and n1 < k <= n1 + n2) or (bande and plein and k > n1 + n2):
                m.teinte[i] = clair
    return m


def table(points, long=1.0):
    """Une fonction de z qui suit une table [(fraction de la longueur, valeur), ...]."""
    f, val = zip(*points)
    return lambda z: float(np.interp(z / long, f, val))


def patte(haut, avance=0.020):
    """Une patte courte et forte, debout sur son pied, dont le bout avance."""
    def pied(v):
        s = v.copy()
        s[:, 1] -= avance * K.lisse((0.045 - v[:, 2]) / 0.045)
        return s
    return A.tour(A.profil([(0, 0), (0.033, 0.005), (0.036, 0.024), (0.026, 0.052), (0.028, 0.10), (0.040, haut - 0.035), (0, haut)], 6), 28).sculpte(pied)


def griffes(pied, cap):
    """Trois longues griffes de fouisseuse au bout d'une patte avant (elles servent à creuser)."""
    tout = None
    for d in (-0.016, 0.0, 0.016):
        c = Vector(pied) + A.tourne((0, 0, 1), cap, Vector((d, -0.050, 0.010)))
        bout = c + A.tourne((0, 0, 1), cap, Vector((d * 0.4, -0.022, -0.009)))
        m = A.tube(A.courbe([tuple(c), tuple((c + bout) * 0.5 + Vector((0, 0, 0.002))), tuple(bout)], 4), lambda t: 0.0058 * (1 - 0.75 * t), 12)
        tout = m if tout is None else tout + m
    return tout


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la fiche seulement)."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


def construire():
    a = K.Animal("mouffette")
    a.taille = 0.60

    # ----- le corps : une poire couchée le long de l'échine, la croupe large et haute ; une seule bande blanche sur la
    #       nuque, qui se fend sur les épaules en deux bandes, lesquelles se rejoignent sur la croupe -----
    long, echine = fil(ECHINE)
    corps = A.tour(A.profil([(r, f * long) for f, r in GALBE], 8), 64)
    rayer(corps, 64, table([(0.0, 0.0), (0.06, 0.0), (0.16, 0.24), (0.35, 0.38), (0.55, 0.34), (0.72, 0.12), (0.80, 0.0), (1.0, 0.0)], long),
          table([(0.0, 0.0), (0.06, 0.62), (0.16, 1.00), (0.35, 1.12), (0.60, 1.05), (0.80, 1.10), (0.92, 1.30), (1.0, 1.30)], long), NEIGE, CHARBON, 3, 6)

    def pansue(v):                                        # des hanches larges, le ventre un peu plat
        s = v.copy()
        s[:, 0] *= 1 + 0.10 * np.exp(-((v[:, 2] / long - 0.22) / 0.16) ** 2)
        s[:, 1] *= np.where(v[:, 1] < 0, 0.86, 0.96)
        return s
    a.piece("corps", corps.sculpte(pansue).sculpte(couche(echine, long)), None)

    # ----- le panache : plus haut que le corps, élargi vers le haut, aplati de côté pour qu'on le voie large de profil.
    #       La bande blanche du dos monte par sa face extérieure, s'élargit, et finit par le blanchir tout entier ; le dedans,
    #       tourné vers le dos, reste noir. La pointe s'effile au-dessus des épaules -----
    haut, panache = fil(PANACHE, flanc=(1, 0, 0))
    queue = A.tour(A.profil([(r, f * haut) for f, r in TOUFFE], 10), 64)
    rayer(queue, 64, lambda z: 0.0, table([(0.0, 0.55), (0.15, 0.85), (0.40, 1.20), (0.62, 1.50), (0.80, 2.20), (0.90, 3.15), (1.0, 3.15)], haut),
          NEIGE, CHARBON, 1, 18)
    queue.sculpte(lambda v: v * [0.84, 1.18, 1.0])
    a.piece("queue", queue.sculpte(couche(panache, haut)), None)

    # ----- la tête : un museau pointu, le crâne plat, des joues fournies ; dans son repère, X la gauche, Y le dessus,
    #       Z vers la truffe. La liste blanche s'ouvre en calotte et coule sur la nuque, le bout du museau est noir -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0, 0, 0), nez) @ Matrix.Rotation(math.radians(PENCHE), 4, Vector((0, 0, 1))) @ A.repere(ech=(GROSSE,) * 3)
    cou = Vector(echine(long)[0])
    T = A.repere(cou - T.to_3x3() @ Vector((0, -0.006, 0.040))) @ T
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.010, 0.120))

    def fute(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 1] *= np.where(v[:, 1] > 0, 0.80 + 0.08 * np.exp(-((z - 0.05) / 0.03) ** 2), 0.92)
        s[:, 0] *= 1 + 0.16 * np.exp(-((z - 0.070) / 0.030) ** 2) * (v[:, 1] < 0.015)
        return s
    tete = A.tour(A.profil([(0, 0), (0.042, 0.008), (0.064, 0.030), (0.071, 0.058), (0.066, 0.084), (0.050, 0.110), (0.034, 0.134),
                            (0.023, 0.154), (0.016, 0.166), (0, 0.176)], 6), 64)
    tour_ = np.abs(np.arctan2(tete.v[:, 0], tete.v[:, 1]))
    z = tete.v[:, 2]
    large = 0.26 + 0.75 * K.lisse((0.064 - z) / 0.030) + 1.15 * K.lisse((0.032 - z) / 0.030)      # la liste, la calotte, puis le capuchon de la nuque
    tete.teinte = np.where(((tour_ < large) & (z < 0.156))[:, None], NEIGE, CHARBON)
    a.piece("tete", tete.sculpte(fute), None, mat=T)
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.017, 0.012, 0.012), CHARBON, mat=T @ A.repere((0, 0.004, 0.170)), poil=False)

    # ----- les yeux : vivants, sur une amande blanche (sur le charbon, on ne les verrait pas), la pupille tournée vers nous ;
    #       un sourcil blanc levé haut, l'autre bas : elle nous jauge -----
    centre = T @ Vector((0, 0, 0.085))
    for nom, c, lorgne in (("G", 1, 0.16), ("D", -1, -0.06)):
        vers = T3 @ Vector((c * 0.70, 0.42, 0.56))
        a.rustine("amande_" + nom, "tete", centre, vers, lambda th: 0.30 + 0.06 * math.cos(2 * th), NEIGE, 0.003, 0)
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.70 + lorgne, 0.44, 0.56)))
        a.oeil("oeil_" + nom, pos + n * 0.004, n, 0.0170)
    # l'œil gauche, celui qu'elle nous tend, est plissé sous une paupière lourde : l'air narquois
    pos, n = a.surface("tete", centre, T3 @ Vector((0.70, 0.42, 0.56)))
    monte = T3 @ Vector((0, 1, 0))
    monte = A.tourne(n, -12, (monte - n * monte.dot(n)).normalized())
    a.piece("lourde_G", K.paupiere(0.025, 0.30), CHARBON, mat=A.cadre(pos + n * 0.002, n, monte))
    # sur l'autre œil, grand ouvert, un sourcil blanc levé haut
    leve = [T3 @ Vector((-0.44 + 0.10 * u, 0.90 + 0.18 * math.sin(math.pi * u), 0.08 + 0.55 * u)) for u in np.linspace(0, 1, 6)]
    a.broderie("sourcil_d", A.courbe(a.trace("tete", centre, leve, 0.004), 4), 0.0030, FIL)
    bouche = a.trace("tete", T @ Vector((0, 0, 0.128)), [T3 @ Vector(d) for d in ((0.30, -0.90, 0.10), (0.62, -0.72, -0.08), (0.80, -0.40, -0.22))], 0.004)
    a.broderie("bouche", A.courbe(bouche, 4), 0.0024, FUMEE)

    # ----- les oreilles : petites, rondes et couchées en arrière, au bord de la calotte ; leur dedans gris fumée -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", T @ Vector((0, 0, 0.046)), T3 @ Vector((c * 0.66, 0.70, -0.30)))
        face, dresse = T3 @ Vector((c * 0.55, 0.45, 0.70)), n + T3 @ Vector((0, 0.2, -0.9))      # couchées en arrière
        E = A.cadre(pos + n * 0.008, face, dresse)
        a.piece("oreille_" + nom, A.boule(1.0, 28, 14).etire(0.026, 0.032, 0.011), CHARBON, mat=E)
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).etire(0.015, 0.020, 0.006), SUIE, mat=E @ A.repere((0, -0.002, 0.007)), poil=False)

    # ----- les pattes : courtes et fortes ; les postérieures plantées large ; l'antérieure droite tient le sol, griffes
    #       dehors, la gauche est levée pour taper du pied -----
    for nom, f, ecart, h in (("arriere", 0.20, 0.085, 0.215),):
        centre_, avant_, _dos, gauche = echine(f * long)
        cap = math.degrees(math.atan2(avant_[0], -avant_[1]))
        for suffixe, c in (("_G", 1), ("_D", -1)):
            pied = centre_ + gauche * (ecart * c)
            a.piece("patte_" + nom + suffixe, patte(h), CHARBON, mat=A.repere((pied[0], pied[1], 0.0), (0, 0, cap + 10 * c)))
    centre_, avant_, _dos, gauche = echine(0.80 * long)
    pied = centre_ - gauche * 0.058
    a.piece("patte_avant_D", patte(0.215, 0.024), CHARBON, mat=A.repere((pied[0], pied[1], 0.0), (0, 0, -6)))
    a.piece("griffes_D", griffes((pied[0], pied[1], 0.0), -6), FUMEE, poil=False)
    epaule = centre_ + gauche * 0.058
    levee = [epaule + np.array(d) for d in ((0, 0, 0), (0.004, -0.032, -0.058), (0.006, -0.074, -0.066), (0.006, -0.090, -0.088))]
    a.piece("patte_avant_G", A.tube(A.courbe(levee, 6), lambda t: float(np.interp(t, [0, 0.4, 0.75, 1], [0.040, 0.031, 0.031, 0.034])), 24), CHARBON)
    a.couleur_paupiere = CHARBON                   # les paupières de l'usine : du charbon, pas le gris moyen de la tête
    a.large_paupiere = 1.45                        # plus larges que l'œil : la pupille glisse sur son amande (jusqu'à 7 mm)
    if TOURNE:
        tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py mouffette). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.

from poses import Pose, borne, cloche, onde

HANCHES = (0.0, 0.143, 0.233)
EPAULE = (0.058, -0.068, 0.236)                   # l'épaule gauche, celle de la patte levée (la droite est son miroir)
COUDE = (0.062, -0.100, 0.178)                    # là où la patte levée se plie
PAUME = (0.064, -0.158, 0.148)                    # le bout de la patte levée, au repos
LEVEE = ((0, 0, 0), (0.004, -0.032, -0.058), (0.006, -0.074, -0.066), (0.006, -0.090, -0.088))   # son chemin depuis l'épaule (construire)
SOL = 0.022                                       # la hauteur de PAUME quand le bout de la patte touche terre
JAMBE = 0.218                                     # de l'épaule droite (ou d'une hanche) au sol
HAUT_TETE = (-0.022, 0.290, 0.957)                # l'axe « dessus » de la tête au repos (tournée vers nous, un peu penchée)
GAUCHE_TETE = (0.662, 0.722, -0.203)              # son axe « gauche »
RELEVE = (0.021, -0.894, 0.449)                   # l'axe autour duquel la paupière lourde remonte le long du front

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", HANCHES),                 # les hanches : elle respire, se dandine, se couche autour
    ("tete", "corps", (0.0, -0.128, 0.272)),      # la nuque
    # Les yeux : chacun sur son os, le pivot au centre du globe, c'est-à-dire au centre de courbure de la tête sous l'œil
    # (56 mm derrière la pupille) : en tournant, la pupille glisse sur son amande blanche sans quitter le tissu. Nommés à la
    # main : les deux yeux ne sont pas symétriques (la tête est tournée), le miroir des « _G » les poserait de travers.
    ("oeil_g", "tete", (0.061, -0.155, 0.289)),   # l'œil plissé
    ("oeil_d", "tete", (0.040, -0.182, 0.296)),   # l'œil grand ouvert
    ("lourde", "tete", (0.060, -0.160, 0.287)),   # la paupière lourde tourne autour du même centre : elle remonte le long du front
    ("oreille_g", "tete", (0.021, -0.063, 0.318)),
    ("oreille_d", "tete", (-0.047, -0.137, 0.339)),
    ("patte_avant_G", "corps", EPAULE),           # l'épaule ; son miroir porte la patte droite, celle d'appui
    ("patte_levee", "patte_avant_G", COUDE),      # le bas de la patte levée : il s'allonge jusqu'au sol pour taper, marcher, se dresser
    ("patte_arriere_G", "corps", (0.085, 0.143, 0.218)),   # la hanche
    ("queue1", "corps", (0.0, 0.150, 0.220)),     # le panache : trois os, de la croupe à la pointe
    ("queue2", "queue1", (0.0, 0.260, 0.399)),
    ("queue3", "queue2", (0.0, 0.194, 0.588)),
]


def _doux(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def yeux(points, cote):
    """Chaque œil (sa pastille et son reflet) sur son os à lui."""
    return {"oeil_g" if cote == "_G" else "oeil_d": np.ones(len(points))}


def oreilles(points, cote):
    return {"oreille_g" if cote == "_G" else "oreille_d": np.ones(len(points))}


def patte_avant(points, cote):
    """La patte droite, d'appui, suit son épaule. La gauche, levée, est souple : le haut suit l'épaule, le bas suit
    « patte_levee », et le milieu s'étire entre les deux quand le pied descend toucher terre."""
    if cote == "_D":
        return {"patte_avant_D": np.ones(len(points))}
    chemin = A.courbe([np.add(EPAULE, d) for d in LEVEE], 12)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(chemin, axis=0), axis=1))])
    u = fait[np.argmin(((points[:, None, :] - chemin[None, :, :]) ** 2).sum(-1), axis=1)] / fait[-1]
    bas = _doux((u - 0.30) / 0.40)
    return {"patte_avant_G": 1 - bas, "patte_levee": bas}


def queue_souple(points, cote):
    """Le panache est souple : trois os se le partagent le long de son fil (0 à la croupe, 1 à la pointe). La place de
    chaque point sur le fil, c'est sa hauteur dans la pièce encore droite : on la refait (mêmes points, même ordre)."""
    haut, repere = fil(PANACHE, flanc=(1, 0, 0))
    droite = A.tour(A.profil([(r, f * haut) for f, r in TOUFFE], 10), 64).v
    if len(droite) == len(points):
        u = np.clip(droite[:, 2] / haut, 0.0, 1.0)
    else:                                         # si la pièce a changé : le point du fil le plus proche
        s = np.linspace(0.0, haut, 120)
        u = s[np.argmin(((points[:, None, :] - repere(s)[0][None]) ** 2).sum(-1), axis=1)] / haut
    milieu, bout = _doux((u - 0.18) / 0.30), _doux((u - 0.50) / 0.30)
    return {"queue1": 1 - milieu, "queue2": milieu * (1 - bout), "queue3": milieu * bout}


PORTEURS = [("corps", "corps"), ("queue", queue_souple, "queue1"),
            ("tete", "tete"), ("truffe", "tete"), ("amande", "tete"), ("sourcil", "tete"), ("bouche", "tete"),
            ("lourde", "lourde"), ("oeil", yeux), ("oreille", oreilles), ("dedans", oreilles),
            ("patte_avant", patte_avant), ("griffes", "patte_avant", True), ("patte_arriere", "patte_arriere", True),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 (l'œil gauche) et paupiere_1
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


# --- un peu de géométrie, pour viser juste (les angles d'une Pose : X, puis Y, puis Z, autour des axes du monde)

def _tourne(axe, degres):
    k = np.asarray(axe, float) / np.linalg.norm(axe)
    c = np.array([[0.0, -k[2], k[1]], [k[2], 0.0, -k[0]], [-k[1], k[0], 0.0]])
    a = math.radians(degres)
    return np.eye(3) + math.sin(a) * c + (1 - math.cos(a)) * (c @ c)


def _matrice(rot):
    return _tourne((0, 0, 1), rot[2]) @ _tourne((0, 1, 0), rot[1]) @ _tourne((1, 0, 0), rot[0])


def _angles(R):
    """Les angles d'une Pose pour une rotation quelconque."""
    return (math.degrees(math.atan2(R[2, 1], R[2, 2])), math.degrees(math.asin(-max(-1.0, min(1.0, R[2, 0])))),
            math.degrees(math.atan2(R[1, 0], R[0, 0])))


def _geste(pivot, rot=(0, 0, 0), pos=(0, 0, 0), ech=(1, 1, 1)):
    """Ce qu'un os fait à ses points : x -> pivot + pos + R E (x - pivot), en 4 × 4."""
    m = np.eye(4)
    m[:3, :3] = _matrice(rot) @ np.diag(ech)
    m[:3, 3] = np.add(pivot, pos) - m[:3, :3] @ np.asarray(pivot, float)
    return m


def _du_corps(p):
    o = p.os.get("corps", {"rot": (0, 0, 0), "pos": (0, 0, 0), "ech": (1, 1, 1)})
    return _geste(HANCHES, o["rot"], o["pos"], o["ech"])


def autour(p, point, rot, pos=(0, 0, 0)):
    """Tourne le corps autour d'un autre point que les hanches (les épaules, pour se dresser sur les pattes avant)."""
    R = _matrice(rot)
    d = np.subtract(point, HANCHES)
    p.add("corps", rot=rot, pos=tuple(d - R @ d + np.asarray(pos, float)))


def regard(p, lacet, tangage=0.0):
    """Les deux yeux ensemble, comme de vrais yeux dans leur orbite : lacet > 0, les pupilles filent vers sa gauche ;
    tangage > 0, elles montent. Un degré déplace la pupille d'un millimètre sur son amande."""
    e = _angles(_tourne(HAUT_TETE, lacet) @ _tourne(GAUCHE_TETE, -tangage))
    p.add("oeil_g", rot=e)
    p.add("oeil_d", rot=e)


def releve(p, degres):
    """La paupière lourde remonte le long du front (degres > 0) : vers 12°, l'œil plissé est grand ouvert."""
    p.add("lourde", rot=_angles(_tourne(RELEVE, degres)))


def pose_patte(p, cible, bras=(0, 0, 0), main=(0, 0, 0), enfonce=0.0, part=1.0):
    """Pose le bout de la patte levée en « cible » (un point du jardin) : l'épaule tourne de « bras » et descend de
    « enfonce » dans le corps (le haut de la patte y reste caché), le bas tourne de « main » autour du coude et s'allonge
    jusqu'à la cible. À appeler une fois l'os du corps posé : le pied reste où on le met, quoi que fasse le corps.
    part < 1 : seulement en chemin, depuis la patte levée du modèle."""
    bouge = _du_corps(p) @ _geste(EPAULE, bras, (0, 0, -enfonce))
    ici = np.linalg.solve(bouge, np.append(np.asarray(cible, float), 1.0))[:3]
    pos = ici - (np.asarray(COUDE) + _matrice(main) @ np.subtract(PAUME, COUDE))
    p.add("patte_avant_G", rot=tuple(part * np.asarray(bras, float)), pos=(0, 0, -enfonce * part))
    p.add("patte_levee", rot=tuple(part * np.asarray(main, float)), pos=tuple(part * pos))


def jambe(p, nom, angle=0.0, leve=0.0):
    """Une patte raide (la droite d'avant, les arrière) : elle fait « angle » degrés avec la verticale (> 0 : le pied
    part en arrière), monte de « leve », et se tasse juste assez pour ne pas entrer dans le sol quand le corps descend."""
    pivot = next(np.multiply(t, (-1 if n != nom else 1, 1, 1)) for n, _p, t in OS if nom in (n, n.replace("_G", "_D")))
    haut = (_du_corps(p) @ np.append(pivot, 1.0))[2]
    o = p.os.get("corps", {"rot": (0, 0, 0), "ech": (1, 1, 1)})
    rx = o["rot"][0]
    a = math.radians(angle)                       # le pied parti en arrière, c'est la pointe (et les griffes) qui descend
    long = pivot[2] * o["ech"][2] * math.cos(a) + (0.080 if a > 0 else 0.012) * abs(math.sin(a))
    e = max(0.45, min(1.0, (haut - leve) / long))
    p.add(nom, rot=(angle - rx, 0, 0), pos=(0, 0, leve), ech=(1 + 0.4 * (1 - e), 1 + 0.4 * (1 - e), e))


def _suivi(t, depart, etapes):
    """Un regard qui va de cible en cible : (début, durée, lacet, tangage). Le dernier revient au départ."""
    lacet, tangage = depart
    for debut, duree, l2, t2 in etapes:
        x = float(_doux((t - debut) / duree))
        lacet, tangage = lacet + (l2 - lacet) * x, tangage + (t2 - tangage) * x
    return lacet, tangage


# --- les cinq animations

REGARD_REPOS = [(0.06, 0.20, -7.0, 1.5),          # il glisse vers nous, lentement
                (0.47, 0.03, 10.0, 3.0),          # file de côté : une saccade de quatre images
                (0.70, 0.04, -4.0, 0.0),          # revient sur nous
                (0.84, 0.14, 0.0, 0.0)]           # et se repose où le dessin l'a mis


def repos(t):
    """Elle respire et nous lorgne ; elle s'impatiente : deux coups de la patte levée par terre. Quelque chose passe de
    côté : le regard y file, la paupière lourde se relève d'étonnement, la tête suit ; puis tout revient à l'air narquois.
    Le panache se balance."""
    p = Pose()
    r, b = onde(t, 2), onde(t, 2, -0.08)
    tape = cloche(t, 0.255, 0.035) + cloche(t, 0.333, 0.035)
    nous, cote = cloche(t, 0.24, 0.14), cloche(t, 0.60, 0.12)
    p.add("corps", pos=(0, 0, -0.003 * tape), rot=(1.0 * tape, 0, 0), ech=(1 + 0.012 * r, 1, 1 + 0.020 * r))
    p.add("tete", rot=(2.0 * r + 3.0 * tape, 5 * nous - 3 * cote, -4 * nous + 9 * cote))
    regard(p, *_suivi(t, (0.0, 0.0), REGARD_REPOS))
    releve(p, 13 * float(_doux((t - 0.47) / 0.03) * (1 - _doux((t - 0.60) / 0.10))))
    pose_patte(p, (0.062, -0.122, SOL), bras=(12, 0, 0), enfonce=0.03, part=tape)
    for nom in ("patte_avant_D", "patte_arriere_G", "patte_arriere_D"):
        jambe(p, nom)
    p.add("oreille_d", rot=(0, 0, -16 * cloche(t, 0.76, 0.03)))
    p.add("oreille_g", rot=(0, 0, 12 * cloche(t, 0.52, 0.04)))
    p.add("queue1", rot=(1.5 * r, 4 * b, 0))
    p.add("queue2", rot=(0, 7 * onde(t, 2, -0.16), 0))
    p.add("queue3", rot=(2 * r, 11 * onde(t, 2, -0.24), 0))
    p.ouvert = borne(1 - cloche(t, 0.475, 0.02) - cloche(t, 0.90, 0.02))
    return p


def avance(t):
    """Sa marche : un pas court et chaloupé, la croupe qui roule, le panache dressé qui balance en retard. La patte levée du
    modèle, c'est la gauche en plein pas : elle se pose devant, glisse sous l'épaule et repart haut, comme sur le dessin.
    Les yeux regardent où elle va, la paupière lourde sautille à chaque pas."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 13.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s)))
    p.add("corps", pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3.0 * c, 2.5 * s))
    jambe(p, "patte_avant_D", pas * s, 0.025 * max(0.0, -c))
    jambe(p, "patte_arriere_G", pas * s, 0.025 * max(0.0, -c))
    jambe(p, "patte_arriere_D", -pas * s, 0.025 * max(0.0, c))
    pose_patte(p, (0.062, EPAULE[1] - JAMBE * math.sin(math.radians(pas * s)), SOL), bras=(14, 0, 0), enfonce=0.03,
               part=1 - max(0.0, c) ** 1.5)
    p.add("tete", rot=(-2 * onde(t, 2, -0.15), -2 * c, -12 - 2 * s))
    regard(p, -6 + 2.5 * onde(t, 1, 0.1), -2 + 1.0 * onde(t, 2))
    releve(p, 2.5 * abs(onde(t, 2, -0.1)))
    p.add("queue1", rot=(-3 + 2 * onde(t, 2, -0.15), 3 * onde(t, 1, -0.10), 0))
    p.add("queue2", rot=(2 * onde(t, 2, -0.25), 6 * onde(t, 1, -0.20), 0))
    p.add("queue3", rot=(3 * onde(t, 2, -0.35), 9 * onde(t, 1, -0.30), 0))
    return p


def mange(t):
    """Elle gratte la terre : l'avant baissé, deux coups de griffes de la patte levée, le museau dans le trou pour deux
    bouchées, puis elle relève la tête en mâchant et nous jette un regard (la paupière lourde se soulève : « quoi ? »)."""
    p = Pose()
    bas = float(_doux(t / 0.14) * (1 - _doux((t - 0.78) / 0.18)))
    leve = cloche(t, 0.88, 0.10)
    bouchee = cloche(t, 0.55, 0.05) + cloche(t, 0.68, 0.05)
    p.add("corps", rot=(13 * bas, 0, 0))
    for nom in ("patte_avant_D", "patte_arriere_G", "patte_arriere_D"):
        jambe(p, nom)
    for centre in (0.22, 0.38):                    # deux coups de griffes : posée devant, tirée en arrière, relevée
        f = borne((t - centre + 0.08) / 0.16)
        touche = float(_doux(f / 0.30) * (1 - _doux((f - 0.75) / 0.25)))
        if touche > 0:
            y = -0.165 + 0.075 * float(_doux((f - 0.30) / 0.45))
            pose_patte(p, (0.062, y, SOL), bras=(6, 0, 0), enfonce=0.02, part=touche)
    p.add("tete", rot=(50 * bas + 10 * bouchee - 8 * leve, -4 * bas, -18 * bas + 4 * leve * onde(t, 8)),
          pos=(0, -0.010 * bas, -0.012 * bas))
    lacet, tangage = _suivi(t, (0.0, 0.0), [(0.04, 0.10, -2.0, -6.0), (0.80, 0.05, -8.0, 2.0), (0.93, 0.07, 0.0, 0.0)])
    regard(p, lacet, tangage)
    releve(p, 7 * cloche(t, 0.87, 0.06))
    p.add("queue1", rot=(-6 * bas, 0, 0))
    p.add("queue2", rot=(0, 4 * onde(t, 2, -0.2), 0))
    p.add("queue3", rot=(0, 6 * onde(t, 2, -0.3), 0))
    p.ouvert = borne(1 - cloche(t, 0.80, 0.02))
    return p


def joie(t):
    """La pose célèbre des mouffettes, pour rire : elle se ramasse, lance la croupe en l'air et se dresse sur les pattes
    avant, le panache déployé au-dessus d'elle ; deux sautillements sur les mains, les deux yeux grands ouverts vers nous
    (la paupière lourde est remontée). Puis elle redescend et retrouve la première pose de repos."""
    p = repos(0.0)
    tasse = cloche(t, 0.10, 0.10, False)
    dresse = float(_doux((t - 0.12) / 0.20) * (1 - _doux((t - 0.64) / 0.24)))
    hop = abs(math.sin(math.tau * borne((t - 0.34) / 0.30))) * dresse
    angle = 60 * dresse
    autour(p, EPAULE, (angle - 4 * tasse, 0, 0), (0, 0, -0.012 * tasse + 0.030 * hop))
    jambe(p, "patte_avant_D")
    pose_patte(p, (0.062, EPAULE[1] - 0.010, SOL + 0.030 * hop), bras=(0, 0, 0), enfonce=0.03, part=max(dresse, tasse))
    for nom in ("patte_arriere_G", "patte_arriere_D"):         # en l'air, les pattes arrière se replient un peu et s'écartent
        jambe(p, nom, 0.6 * angle + 12 * hop)
    p.paire("patte_arriere", rot=(0, 0, 8 * dresse))
    p.add("tete", rot=(-48 * dresse + 6 * tasse, 5 * dresse * onde(t, 2), 4 * dresse))
    regard(p, -7 * dresse, 2 * dresse)
    releve(p, 13 * dresse)
    p.add("oreille_g", rot=(0, 0, 14 * dresse))
    p.add("oreille_d", rot=(0, 0, -14 * dresse))
    fouet = onde(t, 3) * dresse
    p.add("queue1", rot=(-40 * dresse - 8 * tasse, 6 * fouet, 0))
    p.add("queue2", rot=(-10 * dresse, 10 * fouet, 0))
    p.add("queue3", rot=(-8 * dresse, 14 * fouet, 0))
    p.ouvert = min(p.ouvert, borne(1 - cloche(t, 0.86, 0.04, False)))
    return p


def dort(t):
    """Roulée en boule, à demi sur le flanc gauche, la tête ramenée contre ce flanc, les pattes repliées dessous ; le
    grand panache rabattu par-dessus son dos et son flanc droit comme une couverture (de notre côté, on voit son visage
    endormi au bord). Les yeux fermés, la paupière lourde tombée ; une respiration lente, la pointe du panache frémit une fois."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.100), rot=(0, 10, 12), ech=(1 + 0.012 * r, 1, 1 + 0.030 * r))
    p.add("patte_avant_D", rot=(70, 0, 0), pos=(0, 0, 0.010))
    pose_patte(p, (0.062, 0.02, 0.06), bras=(60, 0, 0), enfonce=0.0)
    p.paire("patte_arriere", rot=(-72, 0, 0))
    p.add("tete", rot=(18, 6, 70))
    releve(p, -3)
    p.add("queue1", rot=(45 + 1.5 * r, -25, 0))
    p.add("queue2", rot=(26, 0, 0))
    p.add("queue3", rot=(30 + 6 * cloche(t, 0.62, 0.05), 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("mouffette", styles.style_de("mouffette"), sys.modules[__name__]), "Mouffette")
