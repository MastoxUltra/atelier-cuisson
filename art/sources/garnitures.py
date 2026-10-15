"""Ce qu'on pose sur une forme : des franges de papier, des rustines de feutrine,
des coutures, et l'herbe du studio de photo."""
import math

import bpy  # avant mathutils
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from atelier import TAU, Maille, tube


# ---------------------------------------------------------------- le papier frangé

def franges(m, longueur=0.03, largeur=0.010, pas=0.015, souleve=0.007, couleur=None, graine=1, sens=-1, debut=0.0, fin=1.0):
    """Des rangs de languettes de papier sur une pièce tournée.
    Les languettes pendent vers le premier anneau (sens = -1) ou vers le dernier (sens = 1).
    couleur(rang, t) rend (r, v, b) ; t va de 0 à 1 le long de la pièce."""
    rng = np.random.default_rng(graine)
    nor = m.normales()
    anneaux = [a for a in m.anneaux if len(a) > 1]
    if sens > 0:
        anneaux = anneaux[::-1]
    pts = np.array([m.v[a] for a in anneaux])
    nrm = np.array([nor[a] for a in anneaux])
    cotes = pts.shape[1]
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(pts[1:] - pts[:-1], axis=2).mean(axis=1))])
    total = s[-1]

    def en(sv, u):
        sv = np.clip(sv, 0.0, total)
        i = np.clip(np.searchsorted(s, sv) - 1, 0, len(s) - 2)
        f = ((sv - s[i]) / np.maximum(s[i + 1] - s[i], 1e-9))[:, None]
        j = (u % 1.0) * cotes
        j0 = np.floor(j).astype(int) % cotes
        j1 = (j0 + 1) % cotes
        g = (j - np.floor(j))[:, None]

        def mele(t):
            return (t[i, j0] * (1 - g) + t[i, j1] * g) * (1 - f) + (t[i + 1, j0] * (1 - g) + t[i + 1, j1] * g) * f

        n = mele(nrm)
        return mele(pts), n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)

    points, faces, teintes = [], [], []
    rang, fait = 0, 0
    sr = total * fin
    while sr > total * debut + 1e-6:
        cercle_, _ = en(np.full(49, sr), np.linspace(0.0, 1.0, 49))
        perimetre = np.linalg.norm(cercle_[1:] - cercle_[:-1], axis=1).sum()
        n = max(5, int(perimetre / largeur))
        k = np.arange(n)
        decale = 0.5 * (rang % 2) + rng.uniform(-0.15, 0.15)
        u0 = (k + decale + 0.04) / n
        u1 = (k + decale + 0.96) / n
        uc = (u0 + u1) * 0.5
        lf = longueur * rng.uniform(0.78, 1.18, n)
        vrille = rng.uniform(-0.18, 0.18, n) / n
        base = np.asarray(couleur(rang, sr / total) if couleur else (1, 1, 1), float)
        eclat = rng.uniform(0.88, 1.07, n)[:, None]
        bloc, tb = [], []
        # trois étages : la racine collée, le milieu qui décolle, le bout qui rebique
        for etage, (recul, lever, serre, ombre) in enumerate(((0.0, 0.0, 1.0, 0.60), (0.5, 0.5, 0.92, 0.88), (1.0, 1.0, 0.78, 1.04))):
            hauteur = np.full(n, 0.0012) if etage == 0 else souleve * lever * rng.uniform(0.6, 1.5, n)
            for u in (u0, u1):
                p, nn = en(sr - lf * recul, uc + (u - uc) * serre + vrille * recul)
                bloc.append(p + nn * hauteur[:, None])
                tb.append(np.broadcast_to(base, (n, 3)) * eclat * ombre)
        points.append(np.stack(bloc, axis=1).reshape(-1, 3))
        teintes.append(np.stack(tb, axis=1).reshape(-1, 3))
        for q in range(n):
            o = fait + q * 6
            faces.append((o, o + 1, o + 3, o + 2))
            faces.append((o + 2, o + 3, o + 5, o + 4))
        fait += n * 6
        rang += 1
        sr -= pas
    sortie = Maille(np.vstack(points), faces)
    sortie.teinte = np.clip(np.vstack(teintes), 0.0, 1.0)
    return sortie


# ---------------------------------------------------------------- coudre sur une surface

def ecorce(points, faces):
    """De quoi viser une pièce déjà posée : on lance un rayon, on sait où il touche."""
    return BVHTree.FromPolygons([Vector(p) for p in points], [tuple(f) for f in faces])


def _repere_de(axe):
    a = Vector(axe).normalized()
    e1 = a.cross(Vector((0, 0, 1)))
    if e1.length < 1e-4:
        e1 = a.cross(Vector((1, 0, 0)))
    e1.normalize()
    return a, e1, a.cross(e1).normalized()


def _vise(arbre, centre, a, e1, e2, angle, tour_):
    d = a * math.cos(angle) + (e1 * math.cos(tour_) + e2 * math.sin(tour_)) * math.sin(angle)
    p, n, _i, _d = arbre.ray_cast(Vector(centre), d)
    if p is None:
        return Vector(centre) + d * 0.1, d
    return p, n


def rustine(arbre, centre, axe, forme, epaisseur=0.003, rangs=9, cotes=56):
    """Un morceau de feutrine posé sur une pièce. Depuis le centre de la pièce, on regarde le long
    de l'axe ; forme(tour) donne l'ouverture du morceau (en radians) dans chaque direction."""
    a, e1, e2 = _repere_de(axe)
    p0, n0 = _vise(arbre, centre, a, e1, e2, 0.0, 0.0)
    points, faces = [p0 + n0 * epaisseur], []
    for r in range(1, rangs + 1):
        t = r / rangs
        bombe = 1.0 if t < 0.8 else 1.0 - 0.9 * ((t - 0.8) / 0.2) ** 2
        for j in range(cotes):
            th = TAU * j / cotes
            p, n = _vise(arbre, centre, a, e1, e2, forme(th) * t, th)
            points.append(p + n * epaisseur * bombe)
    for j in range(cotes):
        faces.append((0, 1 + j, 1 + (j + 1) % cotes))
    for r in range(rangs - 1):
        for j in range(cotes):
            k = (j + 1) % cotes
            faces.append((1 + r * cotes + j, 1 + (r + 1) * cotes + j, 1 + (r + 1) * cotes + k, 1 + r * cotes + k))
    return Maille(points, faces)


def surjet(arbre, centre, axe, forme, nombre=40, epaisseur=0.003, fil=0.0011, long=0.012):
    """Le point de feston qui tient une rustine : un fil le long du bord, des points en travers.
    long : la longueur d'un point, en mètres (au plus un cinquième du rayon de la pièce)."""
    a, e1, e2 = _repere_de(axe)
    coeur, _n = _vise(arbre, centre, a, e1, e2, 0.0, 0.0)
    bord = []
    for j in range(nombre * 3 + 1):
        th = TAU * j / (nombre * 3)
        p, n = _vise(arbre, centre, a, e1, e2, forme(th), th)
        bord.append(p + n * (epaisseur * 0.35 + fil))
    tout = tube(bord, fil, 5)
    for j in range(nombre):
        th = TAU * (j + 0.5) / nombre
        p1, n1 = _vise(arbre, centre, a, e1, e2, forme(th), th)
        rentre = max(0.5, 1.0 - min(0.22, long / max((p1 - coeur).length, 1e-6)))
        p2, n2 = _vise(arbre, centre, a, e1, e2, forme(th) * rentre, th)
        tout = tout + tube([p1 + n1 * (epaisseur * 0.3 + fil), (p1 + p2) * 0.5 + n1 * (epaisseur + fil * 1.6),
                            p2 + n2 * (epaisseur * 0.6)], fil, 5)
    return tout


def couture(points, normales, pas=0.014, long=0.008, fil=0.0011, haut=0.0012):
    """Un point avant le long d'une ligne : un tiret de fil, un vide, un tiret."""
    pts = [Vector(p) for p in points]
    nrm = [Vector(n) for n in normales]
    cumul = [0.0]
    for i in range(1, len(pts)):
        cumul.append(cumul[-1] + (pts[i] - pts[i - 1]).length)

    def en(sv):
        sv = min(max(sv, 0.0), cumul[-1])
        i = max(0, min(len(pts) - 2, int(np.searchsorted(cumul, sv)) - 1))
        f = (sv - cumul[i]) / max(cumul[i + 1] - cumul[i], 1e-9)
        return pts[i].lerp(pts[i + 1], f), nrm[i].lerp(nrm[i + 1], f).normalized()

    tout = None
    sv = pas * 0.5
    while sv + long < cumul[-1]:
        (p1, n1), (p2, n2), (p3, n3) = en(sv), en(sv + long * 0.5), en(sv + long)
        t = tube([p1 + n1 * haut * 0.3, p2 + n2 * (haut + fil), p3 + n3 * haut * 0.3], fil, 5)
        tout = t if tout is None else tout + t
        sv += pas
    return tout


# ---------------------------------------------------------------- l'herbe du studio

def herbe(rayon=2.2, nombre=60000, graine=3, clairiere=None):
    """Des brins d'herbe en vrac autour du sujet.
    clairiere(x, y) rend la hauteur relative (0 à 1) de l'herbe à cet endroit."""
    rng = np.random.default_rng(graine)
    r = rayon * np.sqrt(rng.uniform(0, 1, nombre))
    a = rng.uniform(0, TAU, nombre)
    x, y = r * np.cos(a), r * np.sin(a)
    h = rng.uniform(0.035, 0.085, nombre) * (1.0 + 0.5 * np.sin(x * 3.1) * np.cos(y * 2.3))
    if clairiere is not None:
        h = h * clairiere(x, y)
    large = rng.uniform(0.0035, 0.006, nombre)
    cap = rng.uniform(0, TAU, nombre)
    penche = rng.uniform(0.2, 0.9, nombre)
    dx, dy = np.cos(cap), np.sin(cap)
    px, py = -dy, dx
    vert = np.stack([rng.uniform(0.10, 0.20, nombre), rng.uniform(0.42, 0.62, nombre), rng.uniform(0.05, 0.12, nombre)], axis=1)
    points, teintes = [], []
    for t, serre, clair in ((0.0, 1.0, 0.45), (0.4, 0.85, 0.8), (0.75, 0.55, 1.05)):
        for cote_ in (-1, 1):
            cx = x + dx * penche * h * t * t + px * large * serre * cote_
            cy = y + dy * penche * h * t * t + py * large * serre * cote_
            points.append(np.stack([cx, cy, h * t], axis=1))
            teintes.append(vert * clair)
    points.append(np.stack([x + dx * penche * h, y + dy * penche * h, h], axis=1))
    teintes.append(vert * 1.25 + [0.06, 0.05, 0.0])
    pts = np.stack(points, axis=1).reshape(-1, 3)
    tes = np.clip(np.stack(teintes, axis=1).reshape(-1, 3), 0, 1)
    faces = []
    for i in range(nombre):
        o = i * 7
        faces += [(o, o + 1, o + 3, o + 2), (o + 2, o + 3, o + 5, o + 4), (o + 4, o + 5, o + 6)]
    m = Maille(pts, faces)
    m.teinte = tes
    return m


# ---------------------------------------------------------------- la peluche

def sillons(m, lignes, profondeur=0.006, largeur=1.1):
    """Creuse une pièce tournée le long de méridiens (des numéros de côté) :
    la couture tire le tissu, les panneaux gonflent entre deux coutures."""
    for a in m.anneaux:
        n = len(a)
        if n < 2:
            continue
        idx = np.array(a)
        centre = m.v[idx].mean(axis=0)
        j = np.arange(n)
        creux = np.zeros(n)
        for c in lignes:
            d = np.abs(j - c)
            creux += np.exp(-(np.minimum(d, n - d) / largeur) ** 2)
        r = m.v[idx] - centre
        long = np.maximum(np.linalg.norm(r, axis=1, keepdims=True), 1e-6)
        m.v[idx] = centre + r * (1 - np.minimum(creux, 1.0)[:, None] * np.minimum(profondeur, 0.3 * long) / long)
    return m


def piqure(points, normales, pas=0.013, large=0.011, fil=0.0017, haut=0.005, style="croix"):
    """De gros points qui enjambent une couture. style : « croix », « biais » ou « droit »."""
    pts = [Vector(p) for p in points]
    nrm = [Vector(n) for n in normales]
    cumul = [0.0]
    for i in range(1, len(pts)):
        cumul.append(cumul[-1] + (pts[i] - pts[i - 1]).length)
    total = cumul[-1]

    def en(sv):
        sv = min(max(sv, 0.0), total)
        i = max(0, min(len(pts) - 2, int(np.searchsorted(cumul, sv)) - 1))
        f = (sv - cumul[i]) / max(cumul[i + 1] - cumul[i], 1e-9)
        return pts[i].lerp(pts[i + 1], f), nrm[i].lerp(nrm[i + 1], f).normalized()

    tout = None
    w = large * 0.5
    sv = pas * 0.5
    while sv < total - pas * 0.3:
        p, n = en(sv)
        t = (en(sv + 0.002)[0] - en(sv - 0.002)[0])
        if t.length < 1e-9:
            sv += pas
            continue
        t.normalize()
        b = n.cross(t).normalized()
        if style == "croix":
            brins = [((-b - t) * w, (b + t) * w, 0.0), ((-b + t) * w, (b - t) * w, fil * 1.2)]
        elif style == "biais":
            brins = [((-b - t * 0.55) * w, (b + t * 0.55) * w, 0.0)]
        else:
            brins = [(-b * w, b * w, 0.0)]
        for depart, arrivee, plus in brins:
            brin = tube([p + depart + n * haut * 0.35, p + (depart + arrivee) * 0.5 + n * (haut + fil + plus), p + arrivee + n * haut * 0.35], fil, 6)
            tout = brin if tout is None else tout + brin
        sv += pas
    return tout


def duvet(pieces, couvrants, nombre=300000, long=0.0065, large=0.0005, couleur=(1, 1, 1), graine=11):
    """Le poil court d'une peluche : des brins semés sur les pièces données (celles d'un Jouet, avant montage).
    Il ne pousse pas sous ce qui le couvre (les pièces « couvrantes » : rustines, boutons, col).
    couleur : une couleur pour tout le poil, ou None pour que chaque pièce donne la sienne (sa clé « poil »)."""
    rng = np.random.default_rng(graine)
    pts, nrm, tris, decal = [], [], [], 0
    os_ = sorted({o for p in pieces for o in (p.get("poids") or {p["os"]: None})})
    charge, robes, facteurs = [], [], []
    for p in pieces:
        facteurs.append(np.full(len(p["monde"]), float(p.get("poil_k", 1.0))))
        if couleur is None and isinstance(p.get("poil"), str):
            robes.append(np.asarray(p["teinte"], float))
        else:
            robes.append(np.tile(np.asarray(couleur if couleur is not None else (p.get("poil") or (1, 1, 1)), float), (len(p["monde"]), 1)))
        c = np.zeros((len(p["monde"]), len(os_)), np.float32)
        for o, w in (p.get("poids") or {p["os"]: None}).items():
            c[:, os_.index(o)] = 1.0 if w is None else w
        charge.append(c)
        m = Maille(p["monde"], p["faces"])
        pts.append(m.v)
        nrm.append(m.normales())
        for f in m.f:
            for k in range(1, len(f) - 1):
                tris.append((f[0] + decal, f[k] + decal, f[k + 1] + decal))
        decal += len(m.v)
    pts, nrm, tris = np.vstack(pts), np.vstack(nrm), np.array(tris)
    a, b, c = pts[tris[:, 0]], pts[tris[:, 1]], pts[tris[:, 2]]
    aire = np.nan_to_num(np.linalg.norm(np.cross(b - a, c - a), axis=1), nan=0.0, posinf=0.0)   # une pièce dégénérée (sommets NaN,
    if aire.sum() <= 0:                                                                          # triangles plats) ne casse plus le semis
        aire = np.ones(len(tris))
    choix = rng.choice(len(tris), nombre, p=aire / aire.sum())
    u, v = rng.uniform(0, 1, nombre), rng.uniform(0, 1, nombre)
    hors = u + v > 1
    u[hors], v[hors] = 1 - u[hors], 1 - v[hors]
    w = (1 - u - v)[:, None]
    t = tris[choix]
    pied = pts[t[:, 0]] * w + pts[t[:, 1]] * u[:, None] + pts[t[:, 2]] * v[:, None]
    n = nrm[t[:, 0]] * w + nrm[t[:, 1]] * u[:, None] + nrm[t[:, 2]] * v[:, None]
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
    charge = np.vstack(charge)
    suit = charge[t[:, 0]] * w + charge[t[:, 1]] * u[:, None] + charge[t[:, 2]] * v[:, None]
    robe = np.vstack(robes)[t[:, 0]]
    facteur = np.concatenate(facteurs)[t[:, 0]]
    if couvrants:
        cp, cf, d = [], [], 0
        for p in couvrants:
            cp.append(p["monde"])
            cf += [tuple(i + d for i in f) for f in p["faces"]]
            d += len(p["monde"])
        arbre = BVHTree.FromPolygons([Vector(q) for q in np.vstack(cp)], cf)
        libre = np.array([arbre.ray_cast(Vector(pied[i] + n[i] * 0.0003), Vector(n[i]), long * 2.2)[0] is None for i in range(nombre)])
        pied, n, suit, robe, facteur = pied[libre], n[libre], suit[libre], robe[libre], facteur[libre]
    k = len(pied)
    sens = n + rng.normal(size=(k, 3)) * 0.42 + [0.0, 0.0, -0.22]      # ébouriffé, et un peu couché par son poids
    sens /= np.linalg.norm(sens, axis=1, keepdims=True)
    cote = np.cross(sens, rng.normal(size=(k, 3)))
    cote /= np.maximum(np.linalg.norm(cote, axis=1, keepdims=True), 1e-9)
    lg = long * facteur[:, None] * rng.uniform(0.6, 1.25, (k, 1))
    ton = robe * rng.uniform(0.86, 1.08, (k, 1))
    points = np.stack([pied - cote * large, pied + cote * large,
                       pied + sens * lg * 0.55 - cote * large * 0.8, pied + sens * lg * 0.55 + cote * large * 0.8,
                       pied + (sens * 0.9 + n * 0.1) * lg], axis=1).reshape(-1, 3)
    teintes = np.stack([ton * 0.78, ton * 0.78, ton * 1.0, ton * 1.0, ton * 1.14], axis=1).reshape(-1, 3)
    o = np.arange(k) * 5
    sortie = Maille(points, [])
    sortie.quads = np.stack([o, o + 1, o + 3, o + 2], axis=1)
    sortie.tris = np.stack([o + 2, o + 3, o + 4], axis=1)
    sortie.teinte = np.clip(teintes, 0, 1)
    sortie.poids = {o: np.repeat(suit[:, i], 5) for i, o in enumerate(os_) if suit[:, i].max() > 0}
    print("[duvet]", k, "brins")
    return sortie
