"""La planche de direction artistique : le même lapin, en plusieurs matières.

    python planche_da.py bois | papier | feutre | pate      une photo par matière
    python planche_da.py planche                             les réunit en une seule image
"""
import math
import os
import sys

import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import atelier as A
import garnitures as G
import lapinceau as L
import matieres as M

APERCUS = os.path.normpath(os.path.join(ICI, "..", "apercus"))
CORPS = Vector((0.0, 0.044, 0.212))                     # le milieu du ventre
REGARD_DOUX = Vector((0.31, -0.88, 0.17)).normalized()  # des pupilles qui regardent devant, pas sur le côté
PAIRES = ("oreille", "patte", "peton", "cuisse", "pied")


# ---------------------------------------------------------------- les formes communes

def _galet(v):
    s = v.copy()
    s[:, 0] = np.sign(v[:, 0]) * np.abs(v[:, 0]) ** 0.72
    return s


def _semelle(v):
    s = v.copy()
    s[:, 2] = np.maximum(v[:, 2], -0.55)
    s[:, 0] *= 0.82 + 0.18 * (1 - v[:, 1]) * 0.5
    return s


def _oreille(epaisseur, large=1.0):
    def f(v):
        v = L._emousse(v, 0.8)
        t = (v[:, 2] + 1) * 0.5
        demi = (0.012 + 0.040 * np.sin(np.pi * t ** 0.85) ** 0.75) * large
        x = v[:, 0] * demi
        return np.stack([x, v[:, 1] * epaisseur - 6.0 * x * x, t * 0.31], axis=1)
    return f


def formes(oreille=0.012):
    quille = A.tour(A.profil([(0, 0.02), (0.03, 0.024), (0.036, 0.06), (0.033, 0.15), (0.038, 0.215), (0.03, 0.25), (0, 0.262)], 5), 32)
    return {
        "corps": (A.tour(A.profil([(0, 0), (0.12, 0.025), (0.19, 0.12), (0.205, 0.24), (0.175, 0.38), (0.11, 0.48), (0, 0.52)], 7), 72).etire(1.06, 1, 1),
                  A.repere((0, 0.27, 0.13), (70, 0, 0))),
        "tete": (A.boule(1.0, 72, 36).sculpte(L._joues).etire(*L.R_TETE), A.repere(L.TETE)),
        "museau": (A.boule(1.0, 40, 20).etire(0.07, 0.052, 0.05), A.repere(L.TETE + Vector((0, -0.135, -0.045)))),
        "oreille": (A.boule(1.0, 40, 36).sculpte(_oreille(oreille)), A.repere((0.075, -0.215, 0.648), (-8, 14, 15))),
        "patte": (quille, A.repere((0.105, -0.18, 0.0), (-14, 0, 0))),
        "peton": (A.boule(1.0, 32, 16).etire(0.05, 0.066, 0.036), A.repere((0.105, -0.203, 0.036))),
        "cuisse": (A.boule(1.0, 56, 28).sculpte(_galet).etire(0.058, 0.135, 0.118), A.repere((0.195, 0.085, 0.165), (-12, 0, 0))),
        "pied": (A.boule(1.0, 40, 20).sculpte(_semelle).etire(0.042, 0.128, 0.036), A.repere((0.205, -0.005, 0.022))),
    }


def _monde(m, rep):
    r = np.array(rep)
    return m.v @ r[:3, :3].T + r[:3, 3]


def _arbre(m, rep):
    return G.ecorce(_monde(m, rep), m.f)


def _ligne(m, rep, cote, debut, fin):
    """Les points d'une pièce tournée le long d'un méridien, avec leurs normales, dans le monde."""
    r = np.array(rep)
    anneaux = [a for a in m.anneaux if len(a) > 1]
    i0, i1 = min(int(len(anneaux) * debut), len(anneaux) - 1), int(len(anneaux) * fin)
    pas = 1 if i1 >= i0 else -1
    idx = [anneaux[i][cote] for i in range(i0, i1, pas)]
    return (m.v[idx] @ r[:3, :3].T + r[:3, 3]), (m.normales()[idx] @ r[:3, :3].T)


def _poser(j, nom, m, matiere, rep):
    (j.paire if nom in PAIRES else j.piece)(nom, m, matiere, "x", mat=rep)


def _bosses(amplitude, grain, graine):
    """La main qui a roulé la pâte : la pièce n'est jamais tout à fait ronde."""
    rng = np.random.default_rng(graine)
    ondes = [(rng.normal(size=3) * grain * k, rng.uniform(0, 6.28), a) for k, a in ((0.25, 1.0), (0.25, 1.0), (1.0, 0.45), (1.0, 0.45), (1.0, 0.45), (2.2, 0.2), (2.2, 0.2))]

    def f(v):
        centre = v.mean(axis=0)
        d = v - centre
        d = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
        b = sum(a * np.sin(v @ w + ph) for w, ph, a in ondes)
        return v + d * (b * amplitude)[:, None]
    return f


def _pompon(rayon, nombre, long, large, couleur, graine=5):
    """Une boule de brins de laine : des rubans qui partent du cœur."""
    rng = np.random.default_rng(graine)
    d = rng.normal(size=(nombre, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    cote = np.cross(d, rng.normal(size=(nombre, 3)))
    cote /= np.linalg.norm(cote, axis=1, keepdims=True)
    vrac = np.cross(d, cote) * rng.uniform(-0.5, 0.5, (nombre, 1))
    lg = long * rng.uniform(0.7, 1.15, (nombre, 1))
    points, teintes = [], []
    for t, serre, clair in ((0.0, 1.0, 0.55), (0.55, 1.0, 0.9), (1.0, 0.55, 1.05)):
        for s in (-1, 1):
            points.append(d * (rayon + lg * t) + vrac * lg * t * t + cote * large * serre * s)
            teintes.append(np.tile(np.asarray(couleur) * clair, (nombre, 1)) * rng.uniform(0.9, 1.05, (nombre, 1)))
    m = A.Maille(np.stack(points, axis=1).reshape(-1, 3),
                 [f for i in range(nombre) for f in ((i * 6, i * 6 + 1, i * 6 + 3, i * 6 + 2), (i * 6 + 2, i * 6 + 3, i * 6 + 5, i * 6 + 4))])
    m.teinte = np.clip(np.stack(teintes, axis=1).reshape(-1, 3), 0, 1)
    return m


def _bouche(arbre, centre, rayon_fil):
    """Le petit « Y » sous la truffe, suivi sur le museau."""
    a, e1, e2 = G._repere_de((0, -1, 0.42))
    bas = math.pi / 2
    trait = [G._vise(arbre, centre, a, e1, e2, 0.42 + 0.05 * k, bas) for k in range(8)]
    tout = A.tube([p + n * rayon_fil * 0.6 for p, n in trait], rayon_fil, 6)
    for s in (-1, 1):
        arc = [G._vise(arbre, centre, a, e1, e2, 0.77 + 0.10 * math.sin(k / 7 * math.pi) * 0.6 - 0.02 * k, bas + s * 0.115 * k) for k in range(8)]
        tout = tout + A.tube([p + n * rayon_fil * 0.6 for p, n in arc], rayon_fil, 6)
    return tout


def _moustaches(rayon):
    depart = L.TETE + Vector((0.05, -0.171, -0.05))
    fils = None
    for k in (-1, 0, 1):
        chemin = A.courbe([depart + Vector((0, 0, 0.011 * k)), depart + Vector((0.06, -0.006, 0.026 * k + 0.008)),
                           depart + Vector((0.135, 0.012, 0.05 * k - 0.004))], 7)
        f = A.tube(chemin, lambda t: rayon * (1.0 - 0.45 * t), 6)
        fils = f if fils is None else fils + f
    return fils


# ---------------------------------------------------------------- 1. le bois peint

def lapin_bois():
    def corps(g, p):
        x, y, z = g.xyz(p)
        r = g.racine(x * x + y * y)
        tour_ = g.abs(g.angle(x, y))                                  # 0 sur le dos, pi sous le ventre
        feston = 2.0 + 0.07 * g.sin(z * 95.0)
        ventre = g.lisse(tour_, feston, feston + 0.04) * g.lisse(z, 0.05, 0.08)
        lisere = g.lisse(tour_, feston - 0.13, feston - 0.10) * (1.0 - g.lisse(tour_, feston - 0.02, feston + 0.01)) * g.lisse(z, 0.05, 0.08)
        dz = (g.frac(z / 0.072) - 0.5) * 0.072
        da = (tour_ - 0.62) * r
        pois = 1.0 - g.lisse(g.racine(dz * dz + da * da), 0.017, 0.020)
        db = (tour_ - 1.25) * r
        dz2 = (g.frac(z / 0.072 + 0.5) - 0.5) * 0.072
        petits = 1.0 - g.lisse(g.racine(dz2 * dz2 + db * db), 0.008, 0.010)
        c = g.mele(g.couleur(M.CREME), g.couleur(M.ROSE), ventre)
        c = g.mele(c, g.couleur(M.JAUNE), lisere)
        c = g.mele(c, g.couleur(M.TURQUOISE), pois)
        return g.mele(c, g.couleur(M.CORAIL), petits)

    def tete(g, p):
        x, y, z = g.xyz(p)
        ax = g.abs(x)
        devant = g.lisse(y, 0.0, -0.03)
        a, b = x / 0.032, (z - 0.085) / 0.062
        flamme = (1.0 - g.lisse(g.racine(a * a + b * b), 0.92, 1.05)) * devant
        joue = (1.0 - g.lisse(g.longueur(g.vec(ax, y, z) - (0.112, -0.105, -0.052)), 0.026, 0.044)) * 0.9
        o = L.OEIL - L.TETE
        cerne = g.longueur(g.vec(ax, y, z) - (o.x, o.y, o.z))
        tour_oeil = g.lisse(cerne, 0.060, 0.057) * g.lisse(cerne, 0.046, 0.049)
        c = g.mele(g.couleur(M.CREME), g.couleur(M.JAUNE), flamme)
        c = g.mele(c, g.couleur(M.ROSE), joue)
        return g.mele(c, g.couleur(M.TURQUOISE), tour_oeil)

    def oreille(g, p):
        x, y, z = g.xyz(p)
        _nx, ny, _nz = g.xyz(g.normale())
        dedans = g.lisse(ny, -0.25, -0.5) * (1.0 - g.lisse(g.abs(x), 0.020, 0.026)) * g.lisse(z, 0.012, 0.03)
        return g.mele(g.couleur(M.CREME), g.couleur(M.ROSE), dedans)

    def cuisse(g, p):
        x, y, z = g.xyz(p)
        r = g.racine(y * y + z * z)
        petale = g.abs(g.cos(g.angle(z, y) * 3.0))
        fleur = (1.0 - g.lisse(r, 0.030 + 0.034 * petale, 0.034 + 0.034 * petale)) * g.lisse(g.abs(x), 0.02, 0.03)
        coeur = 1.0 - g.lisse(r, 0.018, 0.021)
        c = g.mele(g.couleur(M.CREME), g.couleur(M.TURQUOISE), fleur)
        return g.mele(c, g.couleur(M.JAUNE), coeur * g.lisse(g.abs(x), 0.02, 0.03))

    def doigts(fond):
        def f(g, p):
            x, y, z = g.xyz(p)
            trait = (1.0 - g.lisse(g.abs(g.abs(x) - 0.014), 0.0016, 0.0030)) * g.lisse(y, -0.02, -0.035) * g.lisse(z, -0.012, 0.0)
            return g.mele(g.couleur(fond), g.couleur(M.BRUN), trait)
        return f

    def museau(g, p):
        x, y, z = g.xyz(p)
        ax = g.abs(x)
        devant = g.lisse(y, -0.01, -0.025)
        droit = (1.0 - g.lisse(ax, 0.0014, 0.0026)) * g.lisse(z, -0.021, -0.017) * g.lisse(z, 0.018, 0.012)
        sourire = (1.0 - g.lisse(g.abs(z + 0.019 + 0.010 * g.sin(ax * 105.0)), 0.0014, 0.0026)) * g.lisse(ax, 0.031, 0.027)
        return g.mele(g.couleur(M.BLANC), g.couleur(M.BRUN), g.borne(droit + sourire) * devant)

    def collier(g, p):
        x, y, z = g.xyz(p)
        tour_ = g.angle(y, x) / 6.2832 * 14.0
        d = (g.frac(tour_) - 0.5) * 0.045
        pois = (1.0 - g.lisse(g.racine(d * d + z * z), 0.008, 0.010)) * g.lisse(g.racine(x * x + y * y), 0.098, 0.104)
        return g.mele(g.couleur(M.TURQUOISE), g.couleur(M.JAUNE), pois)

    def meche(g, p):
        x, y, z = g.xyz(p)
        poil = g.bruit(g.vec(g.angle(y, x) * 14.0, z * 2.0, 0.0), 6.0, 3.0)
        trempe = g.lisse(z + poil * 0.035, 0.235, 0.262)
        crin = g.mele(g.couleur(M.hexa("#5b3a22")), g.couleur(M.hexa("#e2c08a")), g.lisse(z, 0.13, 0.25)) * (0.75 + 0.5 * poil)
        return g.mele(crin, g.couleur(M.CORAIL), trempe)

    def uni(c):
        return lambda g, p: g.couleur(c)

    def manche(g, p):
        _x, _y, z = g.xyz(p)
        return g.mele(g.couleur(M.JAUNE), g.couleur(M.TURQUOISE), g.lisse(z, 0.030, 0.032) * g.lisse(z, 0.050, 0.048))

    j = A.Jouet("bois")
    L.pieces(j)
    j.monter()
    j.habiller({
        "corps": M.bois_peint("corps", corps), "tete": M.bois_peint("tete", tete), "oreille": M.bois_peint("oreille", oreille),
        "cuisse": M.bois_peint("cuisse", cuisse), "patte": M.bois_peint("patte", uni(M.CREME)),
        "peton": M.bois_peint("peton", doigts(M.TURQUOISE)), "pied": M.bois_peint("pied", doigts(M.CREME)),
        "paupiere": M.bois_peint("paupiere", uni(M.ROSE)), "museau": M.bois_peint("museau", museau),
        "truffe": M.bois_peint("truffe", uni(M.CORAIL)), "collier": M.bois_peint("collier", collier),
        "manche": M.bois_peint("manche", manche, usure_max=0.6), "meche": M.bois_peint("meche", meche, usure_max=0.0, brillant=0.1),
        "oeil": M.oeil_de_verre("oeil"), "laiton": M.metal("laiton", M.hexa("#e9b44c")), "acier": M.metal("acier", M.hexa("#c9ced3"), 0.2),
    })


# ---------------------------------------------------------------- 2. le papier frangé

def lapin_papier():
    creme, rose, corail, turquoise, jaune, blanc = (np.array(c) for c in (M.CREME, M.ROSE, M.CORAIL, M.TURQUOISE, M.JAUNE, M.BLANC))

    def bandes(*paliers):
        """bandes((0.3, turquoise), (0.4, jaune), (1.0, creme)) : la couleur change à chaque palier."""
        def f(_rang, t):
            for seuil, c in paliers:
                if t <= seuil:
                    return c
            return paliers[-1][1]
        return f

    reglages = {
        "corps": dict(longueur=0.034, largeur=0.0085, pas=0.014, souleve=0.010,
                      couleur=bandes((0.20, corail), (0.27, jaune), (0.56, creme), (0.66, turquoise), (0.71, jaune), (0.80, corail), (1.0, creme))),
        "tete": dict(longueur=0.030, largeur=0.0080, pas=0.013, souleve=0.008, couleur=bandes((0.10, turquoise), (0.16, jaune), (0.90, creme), (1.0, corail))),
        "museau": dict(longueur=0.014, largeur=0.006, pas=0.007, souleve=0.003, couleur=bandes((1.0, blanc))),
        "oreille": dict(longueur=0.026, largeur=0.009, pas=0.012, souleve=0.006, couleur=bandes((0.50, creme), (0.74, rose), (1.0, corail))),
        "patte": dict(longueur=0.026, largeur=0.009, pas=0.012, souleve=0.006, couleur=bandes((0.34, turquoise), (0.42, jaune), (1.0, creme))),
        "peton": dict(longueur=0.018, largeur=0.008, pas=0.009, souleve=0.004, couleur=bandes((1.0, turquoise))),
        "cuisse": dict(longueur=0.032, largeur=0.010, pas=0.014, souleve=0.008, couleur=bandes((0.30, creme), (0.46, corail), (0.52, jaune), (1.0, creme))),
        "pied": dict(longueur=0.020, largeur=0.008, pas=0.010, souleve=0.005, couleur=bandes((1.0, corail))),
    }
    def couche(v):
        x, y, z = v[:, 0], v[:, 1], v[:, 2]
        gros = 1.0 + 0.16 * y
        haut = z * 0.198 * gros + 0.085 * L._lisse((0.1 - y) / 1.1) - 0.02 * L._lisse((y - 0.2) / 0.8)
        return np.stack([x * 0.217 * gros, y * 0.262, haut], axis=1)

    f = formes(0.012)
    f["corps"] = (A.boule(1.0, 80, 44).sculpte(couche), A.repere((0, 0.03, 0.215)))
    j = A.Jouet("papier")
    for i, (nom, (m, rep)) in enumerate(f.items()):
        dessous = m.copie().peint(reglages[nom]["couleur"](0, 0.5) * 0.42)
        _poser(j, nom, dessous + G.franges(m, graine=10 + i, **reglages[nom]), "papier", rep)
    queue = A.boule(0.06, 40, 20)
    j.piece("queue", queue.copie().peint(blanc * 0.5) + G.franges(queue, 0.05, 0.010, 0.010, 0.034, lambda r, t: blanc, 77), "papier", "x", (0, 0.275, 0.30))
    j.paire("oeil", A.boule(0.052, 40, 20), "oeil", "x", L.OEIL - L.REGARD * 0.004, A.viser(REGARD_DOUX))
    j.piece("truffe", A.boule(1.0, 24, 12).etire(0.024, 0.017, 0.017), "truffe", "x", L.TETE + Vector((0, -0.186, -0.027)))
    j.monter()
    j.habiller({"papier": M.papier("papier"), "oeil": M.oeil_dessine("oeil"), "truffe": M.papier_uni("truffe", M.CORAIL)})


# ---------------------------------------------------------------- 3. la feutrine cousue

def lapin_feutre():
    f = formes(0.015)
    arbres = {nom: _arbre(m, rep) for nom, (m, rep) in f.items()}
    creme, rose, turquoise, jaune, fils, durs = (A.Jouet(n) for n in ("f_creme", "f_rose", "f_turquoise", "f_jaune", "f_fils", "f_durs"))
    for nom, (m, rep) in f.items():
        _poser(creme, nom, m, "feutre", rep)

    # le ventre, les joues, le dedans des oreilles : des morceaux roses tenus au point de feston
    def ventre(th):
        return 0.60 - 0.16 * math.cos(2 * th)
    rose.piece("ventre", G.rustine(arbres["corps"], CORPS, (0, -0.80, -0.22), ventre), "feutre", "x")
    fils.piece("ventre", G.surjet(arbres["corps"], CORPS, (0, -0.80, -0.22), ventre, 46), "fil", "x")
    joue = (0.62, -0.55, -0.45)
    rose.paire("joue", G.rustine(arbres["tete"], L.TETE, joue, lambda th: 0.27, 0.0028, 6, 40), "feutre", "x")
    fils.paire("joue", G.surjet(arbres["tete"], L.TETE, joue, lambda th: 0.27, 18, 0.0028), "fil", "x")
    dedans = A.boule(1.0, 40, 36).sculpte(_oreille(0.006, 0.62))
    rep_o = f["oreille"][1] @ A.repere((0, -0.0125, 0.012), ech=(1, 1, 0.92))
    rose.paire("oreille", dedans, "feutre", "x", mat=rep_o)
    bord = [a for a in dedans.anneaux if len(a) > 1]
    tour_ = [dedans.v[a[0]] * [0.86, 1, 1] + [0, -0.0045, 0] for a in bord[3:-3]] + [dedans.v[a[20]] * [0.86, 1, 1] + [0, -0.0045, 0] for a in bord[-4:2:-1]]
    r = np.array(rep_o)
    fils.paire("oreille", G.couture([p @ r[:3, :3].T + r[:3, 3] for p in tour_], [r[:3, :3] @ np.array([0, -1.0, 0])] * len(tour_), 0.013, 0.007), "fil", "x")

    # la truffe et la bouche brodée
    c_museau = L.TETE + Vector((0, -0.135, -0.045))
    rose.piece("truffe", G.rustine(arbres["museau"], c_museau, (0, -1, 0.42), lambda th: 0.40 * (1 + 0.25 * math.cos(3 * (th - math.pi / 2))), 0.004, 6, 36), "feutre_corail", "x")
    durs.piece("bouche", _bouche(arbres["museau"], c_museau, 0.0016), "fil_brun", "x")
    durs.paire("moustache", _moustaches(0.0016), "fil_blanc", "x")

    # un collier rembourré, une fleur cousue sur la cuisse
    turquoise.piece("collier", A.tore(0.098, 0.024, 64, 18), "feutre", "x", (0, -0.165, 0.40), A.viser((0, -0.546, 0.838)))
    c_cuisse = Vector((0.195, 0.085, 0.165))

    def fleur(th):
        return 0.58 * (0.68 + 0.32 * abs(math.cos(2.5 * th)))
    turquoise.paire("fleur", G.rustine(arbres["cuisse"], c_cuisse, (1, 0, 0.08), fleur, 0.003, 7, 60), "feutre", "x")
    fils.paire("fleur", G.surjet(arbres["cuisse"], c_cuisse, (1, 0, 0.08), fleur, 30), "fil", "x")
    jaune.paire("coeur", G.rustine(arbres["cuisse"], c_cuisse, (1, 0, 0.08), lambda th: 0.21, 0.006, 5, 28), "feutre", "x")

    # les coutures d'assemblage : le long du dos, par-dessus le crâne
    pts, nrm = _ligne(f["corps"][0], f["corps"][1], 18, 0.12, 0.80)
    fils.piece("dos", G.couture(pts, nrm, 0.015, 0.009), "fil", "x")
    p1, n1 = _ligne(f["tete"][0], f["tete"][1], 18, 0.42, 1.0)
    p2, n2 = _ligne(f["tete"][0], f["tete"][1], 54, 1.0, 0.72)
    fils.piece("crane", G.couture(np.vstack([p1, p2]), np.vstack([n1, n2]), 0.015, 0.009), "fil", "x")

    # deux boutons pour les yeux, un pompon pour la queue
    bouton = A.tour(A.conges([(0, 0.004), (0.022, 0.004), (0.026, 0.0), (0.036, 0.0), (0.036, 0.010), (0.027, 0.010), (0.023, 0.006), (0, 0.006)], 0.0015, 3), 40)
    rep_b = A.repere(L.OEIL + L.REGARD * 0.008, A.viser(L.REGARD))
    durs.paire("oeil", bouton, "bouton", "x", mat=rep_b)
    croix = A.tube([(-0.011, -0.011, 0.0065), (0, 0, 0.0085), (0.011, 0.011, 0.0065)], 0.0016, 6) + A.tube([(-0.011, 0.011, 0.0065), (0, 0, 0.0095), (0.011, -0.011, 0.0065)], 0.0016, 6)
    fils.paire("croix", croix, "fil", "x", mat=rep_b)
    blancs = A.Jouet("f_pompon")
    blancs.piece("queue", A.boule(0.03, 24, 12).peint(np.array(M.BLANC) * 0.5) + _pompon(0.025, 5200, 0.052, 0.0022, M.BLANC), "laine", "x", (0, 0.285, 0.30))

    mats = {"feutre_creme": M.feutre("feutre_creme", M.CREME), "feutre_rose": M.feutre("feutre_rose", M.ROSE),
            "feutre_corail": M.feutre("feutre_corail", M.CORAIL), "feutre_turquoise": M.feutre("feutre_turquoise", M.TURQUOISE),
            "feutre_jaune": M.feutre("feutre_jaune", M.JAUNE), "fil": M.fil("fil", M.JAUNE), "fil_brun": M.fil("fil_brun", M.BRUN),
            "fil_blanc": M.fil("fil_blanc", M.BLANC), "bouton": M.bouton("bouton"), "laine": M.papier("laine")}
    for jouet, feutre in ((creme, "feutre_creme"), (rose, "feutre_rose"), (turquoise, "feutre_turquoise"), (jaune, "feutre_jaune"), (fils, None), (durs, None), (blancs, None)):
        jouet.monter()
        jouet.habiller({**mats, "feutre": mats[feutre]} if feutre else mats)


# ---------------------------------------------------------------- 4. la pâte à modeler

def lapin_pate():
    f = formes(0.018)
    for i, (nom, (m, _rep)) in enumerate(f.items()):
        m.sculpte(_bosses(0.0035 if nom in ("corps", "tete", "cuisse") else 0.0018, 70.0, 40 + i))
    arbres = {nom: _arbre(m, rep) for nom, (m, rep) in f.items()}
    creme, rose, corail, turquoise, jaune, blanc, noir, brun, raye = (A.Jouet("p_" + n) for n in
                                                                      ("creme", "rose", "corail", "turquoise", "jaune", "blanc", "noir", "brun", "raye"))
    for nom, (m, rep) in f.items():
        _poser(turquoise if nom == "peton" else creme, nom, m, "pate", rep)

    rose.piece("ventre", G.rustine(arbres["corps"], CORPS, (0, -0.80, -0.22), lambda th: 0.60 - 0.16 * math.cos(2 * th), 0.005, 10), "pate", "x")
    rose.paire("joue", G.rustine(arbres["tete"], L.TETE, (0.62, -0.55, -0.45), lambda th: 0.25, 0.0045, 6, 40), "pate", "x")
    rose.paire("oreille", A.boule(1.0, 40, 36).sculpte(_oreille(0.008, 0.6)), "pate", "x", mat=f["oreille"][1] @ A.repere((0, -0.016, 0.014), ech=(1, 1, 0.9)))
    c_museau = L.TETE + Vector((0, -0.135, -0.045))
    corail.piece("truffe", A.boule(1.0, 24, 12).etire(0.026, 0.018, 0.019).sculpte(_bosses(0.001, 200.0, 3)), "pate", "x", L.TETE + Vector((0, -0.186, -0.027)))
    brun.piece("bouche", _bouche(arbres["museau"], c_museau, 0.0024), "pate", "x")

    # les yeux : une boule blanche, une pastille noire écrasée dessus, un grain de lumière
    blanc.paire("oeil", A.boule(0.048, 40, 20).sculpte(_bosses(0.0008, 120.0, 8)), "pate", "x", L.OEIL - L.REGARD * 0.003)
    noir.paire("pupille", A.boule(1.0, 32, 16).etire(0.027, 0.027, 0.008), "pate", "x", L.OEIL - L.REGARD * 0.003 + REGARD_DOUX * 0.045, A.viser(REGARD_DOUX))
    reflet = L.OEIL - L.REGARD * 0.003 + (REGARD_DOUX + Vector((0.12, 0.0, 0.22))).normalized() * 0.051
    blanc.paire("reflet", A.boule(0.0075, 16, 8), "pate", "x", reflet)

    # un collier torsadé de deux couleurs, une queue en chou-fleur, une fleur pressée sur la cuisse
    tore = A.tore(0.098, 0.026, 96, 20)
    i = np.arange(len(tore.v))
    torsade = np.sin((i // 20) * (A.TAU * 11 / 96) + (i % 20) * (A.TAU / 20)) > 0
    tore.teinte = np.where(torsade[:, None], np.array(M.TURQUOISE), np.array(M.JAUNE))
    raye.piece("collier", tore, "pate_teinte", "x", (0, -0.165, 0.40), A.viser((0, -0.546, 0.838)))
    blanc.piece("queue", A.boule(0.068, 64, 32).sculpte(_bosses(0.010, 150.0, 21)), "pate", "x", (0, 0.275, 0.30))
    c_cuisse = Vector((0.195, 0.085, 0.165))
    for k in range(5):
        a = A.TAU * k / 5 + 0.3
        jaune.paire("petale%d" % k, G.rustine(arbres["cuisse"], c_cuisse, (1, 0.50 * math.cos(a), 0.50 * math.sin(a) + 0.05), lambda th: 0.26, 0.005, 5, 24), "pate", "x")
    turquoise.paire("coeur", G.rustine(arbres["cuisse"], c_cuisse, (1, 0, 0.05), lambda th: 0.22, 0.008, 5, 24), "pate", "x")
    brun.paire("moustache", _moustaches(0.0022), "pate", "x")

    couleurs = {creme: M.CREME, rose: M.ROSE, corail: M.CORAIL, turquoise: M.TURQUOISE, jaune: M.JAUNE, blanc: M.BLANC, noir: M.NOIR, brun: M.BRUN}
    for jouet in (creme, rose, corail, turquoise, jaune, blanc, noir, brun, raye):
        jouet.monter()
        jouet.habiller({"pate": M.pate(jouet.nom, couleurs.get(jouet)), "pate_teinte": M.pate("pate_teinte")})


# ---------------------------------------------------------------- 3 bis. la peluche, poussée

def _plie(z0, degres, zone=0.06):
    """Une oreille qui retombe : au-dessus de z0, elle bascule vers l'avant."""
    def f(v):
        s = v.copy()
        h = v[:, 2] - z0
        t = np.clip(h / zone, 0.0, 1.0)
        a = np.radians(degres) * t * t * (3 - 2 * t)
        dessus = h > 0
        s[dessus, 1] = (v[:, 1] * np.cos(a) - h * np.sin(a))[dessus]
        s[dessus, 2] = z0 + (v[:, 1] * np.sin(a) + h * np.cos(a))[dessus]
        return s
    return f


def _vers_monde(points, rep, vecteurs=False):
    r = np.array(rep)
    p = np.asarray(points, float) @ r[:3, :3].T
    return p if vecteurs else p + r[:3, 3]


def _tour(m, rep, fraction):
    """Les points d'un anneau d'une pièce tournée, refermé, avec ses normales, dans le monde."""
    anneaux = [a for a in m.anneaux if len(a) > 1]
    a = anneaux[int(len(anneaux) * fraction)]
    idx = list(a) + [a[0]]
    return _vers_monde(m.v[idx], rep), _vers_monde(m.normales()[idx], rep, True)


def lapin_peluche(sobre=False, droit=False, avant=None, brins=None, par_os=False):
    """sobre : la version entre-deux, avec moins de coutures et de rapiéçages.
    droit : les deux oreilles dressées (c'est le squelette qui en fera retomber une).
    avant(jouets) : appelé avant le montage, pour dire quel os porte chaque pièce.
    brins : le nombre de brins de poil, si on veut l'alléger.
    par_os : la source de cuisson du jeu. Un objet par os et par tissu (« pl_rose@tete »), pas de poil,
    une queue lisse (dans le jeu, le poil et le pompon viennent du shader)."""
    f = formes(0.015)
    G.sillons(f["corps"][0], [0, 18, 36, 54], 0.008, 1.1)
    G.sillons(f["tete"][0], [0, 18, 36, 54], 0.006, 1.1)
    G.sillons(f["cuisse"][0], [14, 42], 0.004, 1.0)
    G.sillons(f["patte"][0], [0], 0.003, 0.8)
    arbres = {nom: _arbre(m, rep) for nom, (m, rep) in f.items()}
    noms = ("creme", "rose", "corail", "turquoise", "jaune", "pois", "raye", "blanc", "fil_corail", "fil_jaune", "fil_brun", "durs")
    creme, rose, corail, turquoise, jaune, pois, raye, blanc, fil_c, fil_j, fil_b, durs = (A.Jouet("pl_" + n) for n in noms)

    def ligne(nom, cote, debut, fin):
        return _ligne(f[nom][0], f[nom][1], cote, debut, fin)

    # ----- les pièces de peluche, et leurs coutures d'assemblage en gros fil corail -----
    for nom, (m, rep) in f.items():
        if nom != "oreille":
            _poser(creme, nom, m, "tissu", rep)
    point = dict(pas=0.014, large=0.009, fil=0.0014, haut=0.0045) if sobre else {}
    for cote, style in (((18, "biais"),) if sobre else ((18, "croix"), (0, "biais"), (36, "biais"))):
        fil_c.piece("corps%d" % cote, G.piqure(*ligne("corps", cote, 0.10, 0.90), style=style, **point), "fil", "x")
    p1, n1 = ligne("tete", 18, 0.30, 1.0)
    p2, n2 = ligne("tete", 54, 1.0, 0.63)
    fil_c.piece("crane", G.piqure(np.vstack([p1, p2]), np.vstack([n1, n2]), style="biais" if sobre else "croix", **point), "fil", "x")
    if not sobre:
        for cote in (0, 36):
            fil_c.piece("tempe%d" % cote, G.piqure(*ligne("tete", cote, 0.22, 0.80), style="biais"), "fil", "x")
        fil_c.paire("patte", G.piqure(*ligne("patte", 0, 0.28, 0.95), pas=0.012, large=0.009, haut=0.004, style="droit"), "fil", "x")
    for cote in (14, 42):
        fil_c.paire("cuisse%d" % cote, G.piqure(*ligne("cuisse", cote, 0.10, 0.90), **{**dict(pas=0.012, large=0.010, style="biais"), **point}), "fil", "x")
    fil_c.paire("pied", G.couture(*_tour(f["pied"][0], f["pied"][1], 0.42), 0.012, 0.007, 0.0015, 0.004), "fil", "x")
    fil_c.paire("peton", G.couture(*_tour(f["peton"][0], f["peton"][1], 0.45), 0.012, 0.007, 0.0015, 0.004), "fil", "x")

    # ----- les oreilles : la gauche dressée, la droite qui retombe -----
    rep_o = f["oreille"][1]
    for miroir, pli in ((False, None), (True, None if droit else (_plie(0.20, 68.0) if sobre else _plie(0.15, 112.0)))):
        cote_ = "_D" if miroir else "_G"
        oreille = A.boule(1.0, 40, 36).sculpte(_oreille(0.015))
        dedans = A.boule(1.0, 40, 36).sculpte(_oreille(0.006, 0.62)).etire(1, 1, 0.92).pose((0, -0.0125, 0.012))
        ourlet = A.boule(1.0, 40, 36).sculpte(_oreille(0.006, 0.62)).etire(0.86, 1, 0.92).pose((0, -0.017, 0.012))
        if pli:
            oreille.sculpte(pli)
            dedans.sculpte(pli)
            ourlet.sculpte(pli)
        creme.piece("oreille" + cote_, oreille, "tissu", "x", mat=rep_o, _miroir=miroir)
        rose.piece("oreille" + cote_, dedans, "tissu", "x", mat=rep_o, _miroir=miroir)
        bord = [a for a in oreille.anneaux if len(a) > 1][2:-2]
        contour = [a[0] for a in bord] + [a[20] for a in reversed(bord)]
        if not sobre:
            fil_c.piece("oreille" + cote_, G.piqure(_vers_monde(oreille.v[contour], rep_o), _vers_monde(oreille.normales()[contour], rep_o, True),
                                                     pas=0.014, large=0.012, haut=0.002, style="droit"), "fil", "x", _miroir=miroir)
        bord = [a for a in ourlet.anneaux if len(a) > 1][3:-3]
        contour = [a[0] for a in bord] + [a[20] for a in reversed(bord)]
        face = [a[30] for a in bord] + [a[30] for a in reversed(bord)]       # la normale du milieu de la face avant, au même niveau
        devant = _vers_monde(ourlet.normales()[face], rep_o, True)
        fil_j.piece("ourlet" + cote_, G.couture(_vers_monde(ourlet.v[contour], rep_o), devant, 0.012, 0.007, 0.0013, 0.0015), "fil", "x", _miroir=miroir)

    # ----- les rapiéçages : ventre, joues, un carré à pois sur le flanc, une fleur sur la cuisse -----
    def ventre(th):
        return 0.60 - 0.16 * math.cos(2 * th)
    rose.piece("ventre", G.rustine(arbres["corps"], CORPS, (0, -0.80, -0.22), ventre), "tissu", "x")
    fil_j.piece("ventre", G.surjet(arbres["corps"], CORPS, (0, -0.80, -0.22), ventre, 50, fil=0.0015), "fil", "x")
    joue = (0.62, -0.55, -0.45)
    rose.paire("joue", G.rustine(arbres["tete"], L.TETE, joue, lambda th: 0.27, 0.0028, 6, 40), "tissu", "x")
    fil_j.paire("joue", G.surjet(arbres["tete"], L.TETE, joue, lambda th: 0.27, 20, 0.0028, 0.0014), "fil", "x")

    def carre(th):
        return 0.30 / (abs(math.cos(th)) ** 4 + abs(math.sin(th)) ** 4) ** 0.25
    flanc = (0.78, -0.30, 0.55)
    if not sobre:
        pois.piece("piece", G.rustine(arbres["corps"], CORPS, flanc, carre, 0.003, 8, 64), "tissu", "x")
        fil_j.piece("piece", G.surjet(arbres["corps"], CORPS, flanc, carre, 30, fil=0.0015), "fil", "x")
    c_cuisse = Vector((0.195, 0.085, 0.165))

    def fleur(th):
        return 0.58 * (0.68 + 0.32 * abs(math.cos(2.5 * th)))
    turquoise.paire("fleur", G.rustine(arbres["cuisse"], c_cuisse, (1, 0, 0.08), fleur, 0.003, 7, 60), "tissu", "x")
    fil_j.paire("fleur", G.surjet(arbres["cuisse"], c_cuisse, (1, 0, 0.08), fleur, 30, fil=0.0014), "fil", "x")
    jaune.paire("coeur", G.rustine(arbres["cuisse"], c_cuisse, (1, 0, 0.08), lambda th: 0.21, 0.006, 5, 28), "tissu", "x")

    # ----- le visage : truffe en feutrine, bouche et moustaches brodées, deux boutons dépareillés -----
    c_museau = L.TETE + Vector((0, -0.135, -0.045))
    corail.piece("truffe", G.rustine(arbres["museau"], c_museau, (0, -1, 0.42), lambda th: 0.40 * (1 + 0.25 * math.cos(3 * (th - math.pi / 2))), 0.004, 6, 36), "tissu", "x")
    fil_b.piece("bouche", _bouche(arbres["museau"], c_museau, 0.0018), "fil", "x")
    blanc.paire("moustache", _moustaches(0.0016), "fil_blanc", "x")
    rep_b = A.repere(L.OEIL + L.REGARD * 0.008, A.viser(L.REGARD))

    def bouton(rayon):
        return A.tour(A.conges([(0, rayon * 0.11), (rayon * 0.61, rayon * 0.11), (rayon * 0.72, 0.0), (rayon, 0.0), (rayon, rayon * 0.28),
                                (rayon * 0.75, rayon * 0.28), (rayon * 0.64, rayon * 0.17), (0, rayon * 0.17)], 0.0015, 3), 40)

    def croix(rayon, double=False):
        e, h = rayon * 0.30, rayon * 0.19
        if double:
            return A.tube([(-e, -e * 0.5, h), (0, -e * 0.5, h + 0.002), (e, -e * 0.5, h)], 0.0016, 6) + A.tube([(-e, e * 0.5, h), (0, e * 0.5, h + 0.002), (e, e * 0.5, h)], 0.0016, 6)
        return A.tube([(-e, -e, h), (0, 0, h + 0.002), (e, e, h)], 0.0016, 6) + A.tube([(-e, e, h), (0, 0, h + 0.003), (e, -e, h)], 0.0016, 6)
    durs.piece("oeil_G", bouton(0.037), "bouton_noir", "x", mat=rep_b)
    fil_j.piece("oeil_G", croix(0.037), "fil", "x", mat=rep_b)
    if sobre:
        durs.piece("oeil_D", bouton(0.037), "bouton_noir", "x", mat=rep_b, _miroir=True)
        fil_j.piece("oeil_D", croix(0.037), "fil", "x", mat=rep_b, _miroir=True)
    else:
        durs.piece("oeil_D", bouton(0.031), "bouton_turquoise", "x", mat=rep_b, _miroir=True)
        fil_c.piece("oeil_D", croix(0.031, True), "fil", "x", mat=rep_b, _miroir=True)
    # les membres tiennent par un bouton, comme sur un ours articulé
    for nom, pos, rayon in (() if sobre else (("hanche", (0.259, 0.085, 0.170), 0.022), ("epaule", (0.141, -0.128, 0.205), 0.015))):
        rep_j = A.repere(pos, A.viser((1, 0, 0)))
        durs.paire(nom, bouton(rayon), "bouton_bois", "x", mat=rep_j)
        fil_c.paire(nom, croix(rayon), "fil", "x", mat=rep_j)

    # ----- le col à pois et son nœud rayé, l'étiquette, le pompon, la bourre qui sort d'une couture -----
    (turquoise if sobre else pois).piece("collier", A.tore(0.098, 0.024, 64, 18), "tissu", "x", (0, -0.165, 0.40), A.viser((0, -0.546, 0.838)))
    rep_n = A.cadre((0.080, -0.246, 0.347), (0.643, -0.642, -0.2))
    noeud = A.boule(0.017, 24, 12)
    for s in (-1, 1):
        noeud = noeud + A.boule(1.0, 32, 16).etire(0.040, 0.024, 0.012).pose((s * 0.046, 0.006, 0.0), (0, 0, s * 18.0))
        noeud = noeud + A.boule(1.0, 24, 12).etire(0.013, 0.040, 0.006).pose((s * 0.020, -0.046, 0.0), (0, 0, s * 20.0))
    raye.piece("noeud", noeud, "tissu", "x", mat=rep_n)
    rep_e = A.cadre((0.212, 0.0, 0.305), (0.1, -0.95, 0.25), (0.25, 0, 1))
    if not sobre:
      blanc.piece("etiquette", A.decoupe([(-0.026, -0.014), (0.026, -0.014), (0.026, 0.014), (-0.026, 0.014)], 0.002, 0.0008, 2), "feutre_blanc", "x", mat=rep_e)
      fil_c.piece("etiquette", A.tube([(0.004, -0.008, 0.002), (0.004, 0.0, 0.003), (0.004, 0.008, 0.002)], 0.0013, 6), "fil", "x", mat=rep_e)
    if par_os:
        blanc.piece("queue", A.boule(0.06, 32, 16), "feutre_blanc", "x", (0, 0.285, 0.30))
    else:
        blanc.piece("queue", A.boule(0.03, 24, 12).peint(np.array(M.BLANC) * 0.5) + _pompon(0.025, 5200, 0.052, 0.0022, M.BLANC), "laine", "x", (0, 0.285, 0.30))
    pf, nf = ligne("corps", 0, 0.60, 0.66)
    fuite = Vector(pf[0]) + Vector(nf[0]) * 0.003
    if not sobre:
      blanc.piece("bourre", _pompon(0.004, 260, 0.016, 0.0016, M.BLANC, 9), "laine", "x", fuite)
      fil_c.piece("fil_perdu", A.tube(A.courbe([fuite, fuite + Vector((0.02, -0.004, 0.012)), fuite + Vector((0.034, -0.002, -0.004)), fuite + Vector((0.040, 0.006, -0.03))], 6), 0.0013, 6), "fil", "x")

    mats = {"feutre_blanc": M.feutre("feutre_blanc", M.BLANC), "fil_blanc": M.fil("fil_blanc", M.BLANC), "laine": M.papier("laine"),
            "bouton_noir": M.bouton("bouton_noir"), "bouton_turquoise": M.bouton("bouton_turquoise", M.TURQUOISE),
            "bouton_bois": M.bouton("bouton_bois", M.hexa("#8a5a2b"))}
    tissus = {creme: M.feutre("t_creme", M.CREME), rose: M.feutre("t_rose", M.ROSE), corail: M.feutre("t_corail", M.CORAIL),
              turquoise: M.feutre("t_turquoise", M.TURQUOISE), jaune: M.feutre("t_jaune", M.JAUNE),
              pois: M.tissu("t_pois", M.TURQUOISE, M.CREME, "pois"), raye: M.tissu("t_raye", M.CORAIL, M.CREME, "rayures")}
    fils = {fil_c: M.fil("f_corail", M.hexa("#c7854a") if sobre else M.CORAIL), fil_j: M.fil("f_jaune", M.JAUNE), fil_b: M.fil("f_brun", M.BRUN)}
    tous = (creme, rose, corail, turquoise, jaune, pois, raye, blanc, fil_c, fil_j, fil_b, durs)
    if avant:
        avant(tous)
    if par_os:
        objets = []
        for jouet in [j for j in tous if j.pieces]:
            for groupe in sorted({p["groupe"] for p in jouet.pieces}):
                morceau = A.Jouet("%s@%s" % (jouet.nom, groupe))
                morceau.pieces = [p for p in jouet.pieces if p["groupe"] == groupe]
                morceau.monter()
                morceau.habiller({**mats, "tissu": tissus.get(jouet), "fil": fils.get(jouet)})
                objets.append(morceau.objet)
        return {"pieces": objets, "duvet": None}
    couvrants = [p for j in tous if j is not creme and j is not blanc for p in j.pieces]
    poil = G.duvet(creme.pieces, couvrants, brins or 460000, 0.0055, 0.00036, M.CREME) if sobre else G.duvet(creme.pieces, couvrants, brins or 320000, 0.0065, 0.0005, M.CREME)
    duvet = A.Jouet("pl_duvet")
    duvet.monter_brins(poil, M.duvet())
    for jouet in [j for j in tous if j.pieces]:
        jouet.monter()
        jouet.habiller({**mats, "tissu": tissus.get(jouet), "fil": fils.get(jouet)})
    return {"pieces": [j.objet for j in tous if j.pieces], "duvet": duvet.objet}


# ---------------------------------------------------------------- le studio et la planche

MATIERES = {"bois": ("Bois peint", lapin_bois), "papier": ("Papier frangé", lapin_papier),
            "feutre": ("Feutrine cousue", lapin_feutre), "pate": ("Pâte à modeler", lapin_pate)}
SUITE = {"peluche": ("Peluche poussée", lapin_peluche), "milieu": ("Entre-deux", lambda: lapin_peluche(True))}


def jardin():
    A.studio()
    bpy.data.objects["sol"].data.materials.clear()
    bpy.data.objects["sol"].data.materials.append(M.terre())
    bpy.data.objects["soleil"].rotation_euler = [math.radians(a) for a in (50, 0, 76)]

    def clairiere(x, y):
        return 0.25 + 0.75 * np.clip((np.hypot(x / 0.34, (y - 0.02) / 0.50) - 0.75) / 0.5, 0, 1)
    h = A.Jouet("herbe")
    h.piece("herbe", G.herbe(2.6, 90000, 3, clairiere), "gazon", "x")
    h.monter()
    h.habiller({"gazon": M.gazon()})


def photographier(nom):
    A.neuf()
    {**MATIERES, **SUITE}[nom][1]()
    jardin()
    net = L.TETE + Vector((0.05, -0.15, 0.0))
    A.photo(os.path.join(APERCUS, "da-%s.png" % nom), (1.25, -1.85, 1.12), (0.0, 0.02, 0.43), 46, grains=128, net=net, ouverture=2.6)
    A.photo(os.path.join(APERCUS, "da-%s-pres.png" % nom), (0.52, -1.02, 0.78), (0.03, -0.20, 0.50), 55, grains=128, net=net, ouverture=4.0)


def planche():
    from PIL import Image, ImageDraw, ImageFont
    noms = [n for n in MATIERES if os.path.exists(os.path.join(APERCUS, "da-%s.png" % n))]
    police = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 44)
    large, haut = 1280, 720
    img = Image.new("RGB", (large * 2, haut * 2), (20, 20, 20))
    dessin = ImageDraw.Draw(img)
    for i, n in enumerate(noms):
        x, y = (i % 2) * large, (i // 2) * haut
        img.paste(Image.open(os.path.join(APERCUS, "da-%s.png" % n)).convert("RGB"), (x, y))
        texte = "%d. %s" % (i + 1, MATIERES[n][0])
        l = dessin.textlength(texte, font=police)
        dessin.rounded_rectangle((x + 28, y + 26, x + 28 + l + 44, y + 26 + 72), 22, fill=(255, 246, 224))
        dessin.text((x + 50, y + 34), texte, font=police, fill=(70, 44, 24))
    img.save(os.path.join(APERCUS, "planche-da.png"))
    print("[planche]", len(noms), "matières")


def bande(noms, sortie, suffixe="", titres_=None):
    """Des photos côte à côte, avec leur titre."""
    from PIL import Image, ImageDraw, ImageFont
    police = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 40)
    titres = {**MATIERES, **SUITE, **(titres_ or {})}
    img = Image.new("RGB", (1280 * len(noms), 720), (20, 20, 20))
    dessin = ImageDraw.Draw(img)
    for i, n in enumerate(noms):
        img.paste(Image.open(os.path.join(APERCUS, "da-%s%s.png" % (n, suffixe))).convert("RGB"), (i * 1280, 0))
        texte = titres[n][0]
        l = dessin.textlength(texte, font=police)
        dessin.rounded_rectangle((i * 1280 + 28, 26, i * 1280 + 28 + l + 44, 26 + 68), 22, fill=(255, 246, 224))
        dessin.text((i * 1280 + 50, 34), texte, font=police, fill=(70, 44, 24))
    img.save(os.path.join(APERCUS, sortie))
    print("[bande]", sortie)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if arg == "planche":
            planche()
        elif arg == "trio":
            simple = {"feutre": ("Simple", None)}
            bande(("feutre", "milieu", "peluche"), "trio-peluche.png", "", simple)
            bande(("feutre", "milieu", "peluche"), "trio-peluche-pres.png", "-pres", simple)
        elif arg in MATIERES or arg in SUITE:
            photographier(arg)
