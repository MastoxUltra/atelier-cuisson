"""La tortue d'eau en peluche : une paresseuse qui prend le soleil. La carapace basse et plate, bleu sarcelle sombre, dont
chaque écaille est cernée de moutarde ; la peau crème rayée de sarcelle, une tache corail sur chaque tempe, de grandes
palmes en éventail. Le cou interminable tendu vers le ciel, le menton levé, les paupières lourdes, et une patte arrière
étirée loin derrière elle, les doigts écartés.

    python tortue_eau.py        fabrique la fiche art/apercus/animaux/tortue_eau.png
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

SARCELLE = M.hexa("#0b4a52")                  # les écailles des flancs : une feutrine bleu sarcelle sombre (la photo l'éclaircit et la bleuit)
NUIT = M.hexa("#083840")                      # celles du dos, un ton plus bas
RAYURE = M.hexa("#1b808c")                    # les rayures de la peau, en poil (il les fonce)
RX, RY, RZ, RB = 0.122, 0.148, 0.050, 0.028   # la carapace : demi-largeur, demi-longueur, hauteur du dos, creux du plastron
LACET = A.repere((0, 0, 0), (0, 0, 0))        # sur la fiche, elle était posée de biais (-22°) ; pour le jeu, droit devant (vers -Y)
COQUE = LACET @ A.repere((0, 0.020, 0.048), (-4, 6, 0))      # la carapace : le nez un peu relevé, penchée vers nous
TETE = Vector((0.027, -0.228, 0.212))
PORT = LACET @ A.cadre(TETE, (0.34, -0.82, 0.44), (0.06, 0.42, 0.90))      # la tête : le menton au ciel, tournée vers nous


def raye(maille, regle):
    """Peint une pièce tournée par quartiers, pareil à gauche et à droite : regle(ecart, f) rend la couleur à « ecart »
    degrés du dos (0 : le dessus, 180 : le dessous), à la fraction f de la longueur de la pièce."""
    z0, z1 = maille.v[:, 2].min(), maille.v[:, 2].max()
    maille.teinte = np.zeros((len(maille.v), 3))
    for anneau in maille.anneaux:
        n = len(anneau)
        for j, i in enumerate(anneau):
            ecart = abs((360.0 * j / n + 90.0) % 360.0 - 180.0) if n > 1 else 180.0
            maille.teinte[i] = regle(ecart, (maille.v[i, 2] - z0) / (z1 - z0))
    return maille


def peau(ecart, f):
    """La peau crème et ses rayures sarcelle : une sur le dessus, deux sur chaque flanc, le dessous tout crème."""
    return RAYURE if ecart <= 20 or 56 <= ecart <= 92 or 126 <= ecart <= 150 else K.CREME


def manchon(chemin, rayons, regle=peau, dos=(0, 0, 1), cotes=48):
    """Un boudin tourné, peint par quartiers, puis couché le long d'un chemin lissé : le cou, une patte, la queue.
    rayons : [(fraction de la longueur, rayon), ...] ; dos : vers où regarde le dessus de la pièce."""
    fil = A.courbe(chemin, 10)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(fil, axis=0), axis=1))])
    sens = np.gradient(fil, fait, axis=0)
    long = float(fait[-1])
    ref = np.asarray(dos, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, long)
        centre = np.stack([np.interp(s, fait, fil[:, k]) for k in range(3)], axis=1)
        avant = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=1)
        avant /= np.linalg.norm(avant, axis=1, keepdims=True)
        haut = ref - (avant @ ref)[:, None] * avant
        haut /= np.linalg.norm(haut, axis=1, keepdims=True)
        return centre + v[:, :1] * np.cross(haut, avant) + v[:, 1:2] * haut
    return raye(A.tour(A.profil([(0, 0)] + [(r, f * long) for f, r in rayons] + [(0, long)], 8), cotes), regle).sculpte(couche)


def pans(axe, coins, rond=7):
    """L'ouverture d'une rustine à pans, aux coins arrondis : « coins » sont les directions de ses coins, vues du point
    de visée. (Le repère est celui que prend le kit pour une rustine d'axe « axe ».)"""
    a = Vector(axe).normalized()
    e1 = a.cross(Vector((0, 0, 1)))
    if e1.length < 1e-4:
        e1 = a.cross(Vector((1, 0, 0)))
    e1.normalize()
    e2 = a.cross(e1).normalized()
    pts = []
    for c in coins:
        d = Vector(c).normalized()
        r, th = math.acos(max(-1.0, min(1.0, a.dot(d)))), math.atan2(d.dot(e2), d.dot(e1))
        pts.append(np.array([r * math.cos(th), r * math.sin(th)]))
    bords = []
    for p, q in zip(pts, pts[1:] + pts[:1]):
        n = np.array([q[1] - p[1], p[0] - q[0]])
        n /= np.linalg.norm(n)
        if n @ p < 0:
            n = -n
        bords.append((n, float(n @ p)))
    return lambda th: sum((max(float(n @ (math.cos(th), math.sin(th))), 0.0) / d) ** rond for n, d in bords) ** (-1.0 / rond)


def palme(rayon=0.060, ouvert=56):
    """Une palme de feutrine : un éventail à quatre doigts, la toile un peu creusée entre deux. Elle part de l'origine vers +X."""
    angles = np.radians(np.linspace(ouvert, -ouvert, 4))
    pts = [(-0.010, 0.012)]
    for k, t in enumerate(angles):
        pts.append((rayon * math.cos(t), rayon * math.sin(t)))
        if k < 3:
            m = (t + angles[k + 1]) * 0.5
            pts.append((0.80 * rayon * math.cos(m), 0.80 * rayon * math.sin(m)))
    return A.decoupe(A.courbe(pts + [(-0.010, -0.012)], 5, fermee=True), 0.009, 0.0035)


def construire():
    a = K.Animal("tortue_eau")
    a.taille = 0.40
    a.tete = PORT @ Vector((0, 0.002, 0.045))
    p3, c3 = PORT.to_3x3(), COQUE.to_3x3()

    # ----- la carapace : une lentille basse, un peu plus large à l'arrière, le bord fin ; moutarde dessus, crème dessous -----
    def lentille(v):
        r = np.hypot(v[:, 0], v[:, 1])
        z = np.where(v[:, 2] >= 0, RZ, RB) * (1 - r ** 2.4) * np.sign(v[:, 2]) + 0.007 * v[:, 2]
        return np.stack([v[:, 0] * RX * (1 + 0.10 * v[:, 1]), v[:, 1] * RY, z], axis=1)
    a.piece("carapace", K.bandes(A.boule(1.0, 64, 32), [(-0.30, K.CREME), (9, K.MOUTARDE)]).sculpte(lentille), None, mat=COQUE, poil=False)

    # ----- les écailles : dix coussins de feutrine sarcelle, quatre le long du dos et trois sur chaque flanc ;
    #       la moutarde de la carapace fait le cerne entre elles et le liseré du bord. On les vise de très haut,
    #       comme sur un plan : chaque coin est donné vu de dessus (u : de droite à gauche, w : de l'avant à l'arrière) -----
    dos1 = [(-0.16, -0.93), (0.16, -0.93), (0.20, -0.45), (-0.20, -0.45)]
    dos2 = [(-0.20, -0.45), (0.20, -0.45), (0.34, -0.225), (0.20, 0.0), (-0.20, 0.0), (-0.34, -0.225)]
    flanc1 = [(0.16, -0.93), (0.20, -0.45), (0.34, -0.225), (0.903, -0.294), (0.672, -0.672), (0.386, -0.868)]
    flanc2 = [(0.34, -0.225), (0.20, 0.0), (0.34, 0.225), (0.903, 0.294), (0.95, 0.0), (0.903, -0.294)]
    plan = [dos1, dos2, [(u, w + 0.45) for u, w in dos2], [(u, -w) for u, w in dos1]]
    for cote in (1, -1):
        plan += [[(cote * u, w) for u, w in flanc1], [(cote * u, w) for u, w in flanc2], [(cote * u, -w) for u, w in flanc1]]
    for k, coins in enumerate(plan):
        pts = np.array([(u * RX * (1 + 0.10 * w), w * RY) for u, w in coins])
        milieu = pts.mean(axis=0)
        ecart = pts - milieu
        pts = milieu + ecart * (1 - 0.0052 / np.linalg.norm(ecart, axis=1, keepdims=True))     # le cerne : un centimètre de moutarde
        axe = c3 @ Vector((0, 0, -1))
        a.rustine("ecaille%d" % k, "carapace", COQUE @ Vector((milieu[0], milieu[1], 2.0)), axe,
                  pans(axe, [c3 @ Vector((x - milieu[0], y - milieu[1], -2.0)) for x, y in pts]), NUIT if k < 4 else SARCELLE, 0.0055, 0)

    # ----- le cou : il sort de sous le bord, se redresse et monte droit vers le soleil -----
    cou = manchon([(0, -0.055, 0.030), (0, -0.120, 0.031), (0.003, -0.166, 0.052), (0.010, -0.192, 0.100), (0.017, -0.203, 0.150), (0.022, -0.210, 0.188)],
                  [(0.03, 0.028), (0.30, 0.030), (0.58, 0.024), (0.82, 0.020), (0.97, 0.019)], dos=(0, 0.7, 0.7))
    a.piece("cou", cou, None, mat=LACET)

    # ----- la tête : un coin aplati, large aux tempes, le museau en pointe ; une rayure sur le crâne, une sous la joue -----
    def crane(v):
        v = K.bosse(K.bosse(v, (0.80, 0.30, -0.35), 0.14, 0.25), (-0.80, 0.30, -0.35), 0.14, 0.25)
        fin = K.lisse((v[:, 2] + 0.10) / 1.10)
        return np.stack([v[:, 0] * 0.041 * (1 - 0.52 * fin), v[:, 1] * 0.031 * (1 - 0.40 * fin) - 0.004 * fin, v[:, 2] * 0.064], axis=1)
    tete = raye(A.boule(1.0, 48, 24), lambda ecart, f: RAYURE if ecart <= 20 or (102 <= ecart <= 126 and f < 0.66) else K.CREME)
    a.piece("tete", tete.sculpte(crane), None, mat=PORT)
    centre = PORT @ Vector((0, 0, 0))
    for nom, cote in (("_G", 1), ("_D", -1)):
        # la tache corail de la tempe, allongée vers la nuque
        a.rustine("tempe" + nom, "tete", centre, p3 @ Vector((0.84 * cote, 0.16, -0.36)),
                  lambda th: 0.36 / math.hypot(math.cos(th), 1.75 * math.sin(th)), K.CORAIL, 0.003, 0)
        # l'œil, et sa paupière lourde qui le ferme à moitié
        p, n = a.surface("tete", centre, p3 @ Vector((0.86 * cote, 0.15, 0.50)))
        a.bouton("oeil" + nom, p + n * 0.001, n, 0.0165)
        haut = (p3 @ Vector((0, 1, 0)) - n * n.dot(p3 @ Vector((0, 1, 0)))).normalized()
        a.piece("lourde" + nom, A.boule(1.0, 24, 12).etire(0.0175, 0.0092, 0.0040), K.CREME, mat=A.cadre(p + haut * 0.0080 + n * 0.0034, n, haut), poil=False)
    sourire = [p3 @ Vector((0.80 * math.sin(s), -0.34 + 0.16 * (abs(s) / 1.05) ** 2, math.cos(s))) for s in np.linspace(-1.05, 1.05, 15)]
    a.broderie("bouche", a.trace("tete", centre, sourire, 0.0040), 0.0019)

    # ----- les pattes : devant, la gauche plantée sur le côté et la droite allongée ; derrière, la gauche étirée
    #       loin en arrière, levée du sol, les doigts en éventail, et la droite repliée le long de la carapace -----
    bras = [(0.05, 0.024), (0.35, 0.026), (0.75, 0.021), (0.97, 0.0165)]
    for nom, chemin, cap, leve in (("avant_G", [(0.055, -0.060, 0.030), (0.108, -0.086, 0.027), (0.138, -0.112, 0.023), (0.150, -0.136, 0.021)], -65, 20),
                                   ("avant_D", [(-0.055, -0.070, 0.030), (-0.096, -0.112, 0.027), (-0.112, -0.146, 0.023), (-0.116, -0.170, 0.021)], -95, 20),
                                   ("arriere_G", [(0.055, 0.110, 0.032), (0.084, 0.168, 0.032), (0.098, 0.208, 0.042), (0.104, 0.236, 0.055)], 76, 32),
                                   ("arriere_D", [(-0.055, 0.105, 0.030), (-0.106, 0.128, 0.027), (-0.134, 0.118, 0.023), (-0.146, 0.096, 0.021)], -110, 16)):
        a.piece("patte_" + nom, manchon(chemin, bras), None, mat=LACET)
        bout = Vector(chemin[-1])
        a.piece("palme_" + nom, palme(), K.MOUTARDE, mat=LACET @ A.repere((bout.x, bout.y, bout.z - 0.006), (0, -leve, cap)), poil=False)

    # ----- la queue : courte et pointue, elle traîne du côté droit -----
    a.piece("queue", manchon([(0, 0.150, 0.034), (-0.008, 0.190, 0.024), (-0.028, 0.218, 0.012)], [(0.05, 0.013), (0.5, 0.009), (0.95, 0.004)], cotes=24), None, mat=LACET)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py tortue_eau)

from poses import Pose, borne, cloche, onde

# Le cou est une seule pièce souple, partagée entre trois os : sa racine sous la carapace, le coude où il se redresse,
# et le haut, sous la tête. Les pattes sont posées chacune à sa façon ; leurs os de droite sont les miroirs de ceux de
# gauche (les hanches tombent à quelques millimètres près au même endroit).
OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.020, 0.048)),          # le milieu de la carapace
    ("cou", "corps", (0, -0.100, 0.031)),            # la racine du cou, sous le bord de la carapace
    ("nuque", "cou", (0.003, -0.166, 0.052)),        # le coude du cou, là où il se redresse vers le ciel
    ("tete", "nuque", (0.019, -0.205, 0.165)),       # le haut du cou, sous la tête
    ("avant_G", "corps", (0.058, -0.066, 0.030)),    # les épaules et les hanches, sous le bord
    ("arriere_G", "corps", (0.057, 0.108, 0.031)),
    ("queue", "corps", (0, 0.150, 0.034)),
]

FIL_DU_COU = np.array([(0, -0.055, 0.030), (0, -0.120, 0.031), (0.003, -0.166, 0.052), (0.010, -0.192, 0.100),
                       (0.017, -0.203, 0.150), (0.022, -0.210, 0.188)])


def cou_souple(points, cote):
    """Chaque point du cou trouve sa place le long du fil du cou (en mètres depuis sa racine), et se partage entre les
    trois os : la racine jusqu'à 9 cm, le coude de 14 à 21 cm, la tête au-delà de 25 cm ; en douceur entre deux."""
    meilleur, place = np.full(len(points), 9.0), np.zeros(len(points))
    fait = 0.0
    for a_, b_ in zip(FIL_DU_COU[:-1], FIL_DU_COU[1:]):
        long = float(np.linalg.norm(b_ - a_))
        u = np.clip((points - a_) @ (b_ - a_) / long ** 2, 0.0, 1.0)
        d = np.linalg.norm(points - a_ - u[:, None] * (b_ - a_), axis=1)
        plus = d < meilleur
        meilleur, place = np.where(plus, d, meilleur), np.where(plus, fait + u * long, place)
        fait += long
    coude, haut = K.lisse((place - 0.090) / 0.050), K.lisse((place - 0.212) / 0.040)
    return {"cou": 1 - coude, "nuque": coude * (1 - haut), "tete": coude * haut}


PORTEURS = [("carapace", "corps"), ("ecaille", "corps"), ("cou", cou_souple, "cou"), ("tete", "tete"), ("tempe", "tete"),
            ("oeil", "tete"), ("lourde", "tete"), ("bouche", "tete"), ("patte_avant", "avant", True), ("palme_avant", "avant", True),
            ("patte_arriere", "arriere", True), ("palme_arriere", "arriere", True), ("queue", "queue"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]

# où va chaque patte, vue de dessus, depuis sa hanche (pour la lever ou la poser, il faut tourner en travers d'elle)
VERS = {"avant_G": (0.70, -0.71), "avant_D": (-0.52, -0.85), "arriere_G": (0.36, 0.93), "arriere_D": (-0.99, 0.12)}


def _leve(p, os_, angle):
    """Lève le bout d'une patte de « angle » degrés (négatif : l'appuie au sol), en tournant en travers de sa direction."""
    dx, dy = VERS[os_]
    p.add(os_, rot=(angle * dy, -angle * dx, 0))


def _ramene(p, combien):
    """Ramène la patte arrière gauche, étirée au soleil, sous le bord de la carapace, en position de marche."""
    p.add("arriere_G", rot=(-8 * combien, 0, -38 * combien))


def repos(t):
    """Elle lézarde : le menton au soleil, le cou qui ondule lentement d'un côté à l'autre, la gorge qui palpite ; elle
    étire sa patte arrière en éventail, la repose, cligne de ses lourdes paupières, et la queue frétille un peu."""
    p = Pose()
    r = onde(t, 2)
    etire = cloche(t, 0.46, 0.13)
    p.add("corps", ech=(1 + 0.006 * r, 1, 1 + 0.012 * r))
    p.add("cou", ech=(1 + 0.03 * cloche(t, 0.70, 0.03) + 0.03 * cloche(t, 0.76, 0.03), 1, 1))
    p.add("nuque", rot=(-3 * onde(t, 1), 0, 7 * onde(t, 1)))
    p.add("tete", rot=(-3 * (1 - math.cos(math.tau * t)) - 6 * etire, 0, -5 * onde(t, 1)))
    _leve(p, "arriere_G", 10 * etire)
    p.add("arriere_G", rot=(0, 0, 6 * etire * onde(t, 6)))
    p.add("queue", rot=(0, 0, 12 * cloche(t, 0.88, 0.06) * onde(t, 10)))
    p.ouvert = 1 - cloche(t, 0.18, 0.04) - cloche(t, 0.80, 0.05)
    return p


def avance(t):
    """Elle marche à pas comptés, les pattes en diagonale (l'avant gauche avec l'arrière droite) : chaque patte balaie
    vers l'arrière au sol, se lève à peine et revient. La carapace roule et tangue un peu, le cou se penche en avant
    et la tête dodeline à contretemps."""
    p = Pose()
    _ramene(p, 1.0)
    p.add("avant_D", rot=(0, 0, -22))                     # la patte avant droite, allongée devant, s'écarte du cou pour marcher
    for os_, phase in (("avant_G", 0.0), ("arriere_D", 0.0), ("avant_D", 0.5), ("arriere_G", 0.5)):
        a_ = math.tau * (t + phase)
        signe = 1 if os_.endswith("_G") else -1
        p.add(os_, rot=(0, 0, -signe * 16 * math.cos(a_)))
        _leve(p, os_, 12 * max(0.0, -math.sin(a_)))
    s, d = math.sin(math.tau * t), math.sin(2 * math.tau * t)
    p.add("corps", rot=(1.2 * d, 1.5 * s, 2 * s), pos=(0, 0, 0.004 * abs(s)))
    p.add("nuque", rot=(22, 0, -5 * s))
    p.add("tete", rot=(18 - 4 * d, 0, -3 * s))
    p.add("queue", rot=(0, 0, -10 * s))
    return p


def mange(t):
    """Le cou plonge jusqu'à l'herbe : elle happe trois fois d'un coup sec, la tête en avant, puis relève le menton
    et avale, la gorge qui palpite."""
    p = Pose()
    leve = cloche(t, 0.84, 0.14)
    bas = 1 - leve
    happe = max(0.0, onde(t, 3)) ** 3 * bas
    p.add("corps", rot=(2 * bas, 0, 0), pos=(0, 0, 0.003 * bas))
    p.add("avant_D", rot=(0, 0, -26 * bas))               # la patte avant droite, allongée devant, laisse passer le cou
    p.add("cou", pos=(0, -0.008 * happe, 0.002 * bas))
    p.add("nuque", rot=(44 * bas + 6 * happe, 0, 0))
    p.add("tete", rot=(18 * bas + 5 * happe - 10 * leve, 0, 0), pos=(0, -0.010 * happe, 0))
    p.add("cou", ech=(1 + 0.05 * leve * abs(onde(t, 6)), 1, 1))
    p.add("queue", rot=(0, 0, 6 * onde(t, 2)))
    p.ouvert = 1 - 0.5 * happe - 0.5 * leve
    return p


def joie(t):
    """Une joie de lézarde : elle se hisse sur ses pattes avant, tend le cou vers le soleil, dodeline de la tête de
    gauche à droite, les yeux mi-clos de bonheur, bat l'air de sa patte arrière étirée et frétille de la queue."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    p.add("corps", rot=(-7 * env, 0, 0), pos=(0, 0, 0.008 * env))
    p.add("avant_D", rot=(0, 0, -24 * env))                # la patte avant droite s'écarte du cou qui danse
    _leve(p, "avant_G", -9 * env)
    _leve(p, "avant_D", -9 * env)
    p.add("nuque", rot=(-12 * env, 0, 8 * onde(t, 2) * env))
    p.add("tete", rot=(-8 * env, 10 * onde(t, 3) * env, 16 * onde(t, 3) * env))
    _leve(p, "arriere_G", 14 * env * (0.5 + 0.5 * onde(t, 4)))
    p.add("queue", rot=(9 * env, 0, 18 * onde(t, 6) * env))
    p.ouvert = 1 - 0.6 * env
    return p


def dort(t):
    """Elle rentre la tête : le cou glisse sous la carapace et se tasse, le menton se pose près du bord ; les pattes
    se ramassent sous la carapace, les yeux fermés ; elle respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    _ramene(p, 1.0)
    p.add("corps", ech=(1 + 0.006 * r, 1, 1 + 0.014 * r))
    p.add("cou", pos=(0, 0.040, 0.005))
    p.add("nuque", rot=(24, 0, -6), ech=(1, 1, 0.55))
    p.add("tete", ech=(1, 1, 1 / 0.55), rot=(1.5 * r, 0, 0))
    p.add("avant_D", rot=(0, 0, -34))                     # la patte avant droite, allongée devant, se range sur le côté
    for os_ in ("avant_G", "avant_D", "arriere_G", "arriere_D"):
        p.add(os_, ech=(0.80, 0.80, 1))
    p.add("queue", rot=(0, 0, 12), ech=(0.8, 0.8, 1))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Tortue d'eau")
