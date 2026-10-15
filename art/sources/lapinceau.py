"""Le Lapinceau : un lapin à remonter, avec un pinceau pour queue.

    python lapinceau.py argile     les formes seules, photographiées
    python lapinceau.py            tout : textures, squelette, animations, export
"""
import math
import os
import sys

import bpy  # avant mathutils : c'est lui qui l'apporte
import numpy as np
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atelier as A

ICI = os.path.dirname(os.path.abspath(__file__))
APERCUS = os.path.normpath(os.path.join(ICI, "..", "apercus"))
MODELES = os.path.normpath(os.path.join(ICI, "..", "modeles"))

# --- les repères du jouet (mètres ; il regarde vers -Y) ---
TETE = Vector((0.0, -0.25, 0.53))
R_TETE = Vector((0.17, 0.155, 0.15))
REGARD = Vector((0.52, -0.80, 0.28)).normalized()            # là où pointe l'œil gauche
OEIL = TETE + Vector((R_TETE.x * REGARD.x, R_TETE.y * REGARD.y, R_TETE.z * REGARD.z)) * 0.93
CHARNIERE = Vector((REGARD.y, -REGARD.x, 0.0)).normalized()   # l'axe autour duquel la paupière bascule
PAUPIERE_OUVERTE = 142.0
DOS = Vector((0.0, 0.342, 0.940))                             # « vers le haut » pour le corps incliné
FLANC = Vector((0.643, 0.262, 0.720)).normalized()            # la normale du haut du flanc gauche
QUEUE = Vector((0.0, 0.643, 0.766))


def _emousse(v, e):
    """Rend une boule plus carrée (e < 1) : des bouts francs, des flancs droits."""
    rho = np.hypot(v[:, 0], v[:, 1])
    k = np.where(rho > 1e-9, rho ** e / np.maximum(rho, 1e-9), 0.0)
    s = v.copy()
    s[:, 0] *= k
    s[:, 1] *= k
    s[:, 2] = np.sign(v[:, 2]) * np.abs(v[:, 2]) ** e
    return s


def _lisse(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _joues(v):
    u = v / np.linalg.norm(v, axis=1, keepdims=True)
    g = np.zeros(len(v))
    for c in ((0.62, -0.55, -0.45), (-0.62, -0.55, -0.45)):
        c = np.array(c) / np.linalg.norm(c)
        g += np.exp(-np.sum((u - c) ** 2, axis=1) / 0.16)
    return v * (1 + 0.13 * g)[:, None]


def _oreille(bas):
    def f(v):
        v = _emousse(v, 0.62)
        t = (v[:, 2] + 1) * 0.5
        if bas:
            demi = 0.024 + 0.019 * _lisse(t)
        else:
            demi = 0.0435 * (1.0 - 0.55 * t ** 2.4)
        x = v[:, 0] * demi
        y = v[:, 1] * 0.0145 - 9.0 * x * x
        return np.stack([x, y, t * 0.165], axis=1)
    return f


def _coquille(dehors, dedans, ouverture, n=14):
    """Une calotte creuse autour de +Z : la paupière d'une poupée qui dort."""
    p = [(0.0, dedans)]
    for i in range(1, n + 1):
        a = math.radians(ouverture) * i / n
        p.append((dedans * math.sin(a), dedans * math.cos(a)))
    for i in range(n, 0, -1):
        a = math.radians(ouverture) * i / n
        p.append((dehors * math.sin(a), dehors * math.cos(a)))
    p.append((0.0, dehors))
    return A.tour(p, 40)


def _poils(v):
    a = np.arctan2(v[:, 1], v[:, 0])
    t = np.clip((v[:, 2] - 0.13) / 0.24, 0.0, 1.0)
    k = 1 + (0.045 * np.cos(34 * a) + 0.03 * np.cos(13 * a + 1.3) + 0.02 * np.cos(57 * a + 0.4)) * (0.35 + 0.65 * t)
    s = v.copy()
    s[:, 0] *= k
    s[:, 1] *= k
    s[:, 1] += 0.55 * np.maximum(v[:, 2] - 0.22, 0.0) ** 2 * 4.0       # la mèche se recourbe
    return s


def pieces(j):
    # ----- le corps : un œuf tourné, couché, la poitrine relevée -----
    oeuf = A.tour(A.profil([(0, 0), (0.12, 0.025), (0.19, 0.12), (0.205, 0.24), (0.175, 0.38), (0.11, 0.48), (0, 0.52)], 7), 72)
    j.piece("corps", oeuf.etire(1.06, 1.0, 1.0), "corps", "corps", (0, 0.27, 0.13), (70, 0, 0))
    j.piece("collier", A.tore(0.098, 0.024, 64, 18), "collier", "corps", (0, -0.165, 0.40), A.viser((0, -0.546, 0.838)))

    # ----- la tête -----
    j.piece("tete", A.boule(1.0, 72, 36).sculpte(_joues).etire(*R_TETE), "tete", "tete", TETE)
    j.piece("museau", A.boule(1.0, 40, 20).etire(0.07, 0.052, 0.05), "museau", "tete", TETE + Vector((0, -0.135, -0.045)))
    j.piece("truffe", A.boule(1.0, 24, 12).etire(0.024, 0.016, 0.017), "truffe", "tete", TETE + Vector((0, -0.184, -0.027)))
    j.paire("oeil", A.boule(0.044, 40, 20), "oeil", "tete", OEIL, A.viser(REGARD))
    ouverte = A.tourne(CHARNIERE, PAUPIERE_OUVERTE, REGARD)
    j.paire("paupiere", _coquille(0.0505, 0.0455, 80.0), "paupiere", "paupiere_G", OEIL, A.viser(ouverte))

    # les moustaches : trois fils de laiton de chaque côté
    depart = TETE + Vector((0.05, -0.171, -0.05))
    fils = None
    for k in (-1, 0, 1):
        chemin = A.courbe([depart + Vector((0, 0, 0.011 * k)), depart + Vector((0.06, -0.006, 0.026 * k + 0.008)),
                           depart + Vector((0.135, 0.012, 0.05 * k - 0.004))], 7)
        fil = A.tube(chemin, lambda t: 0.0030 - 0.0014 * t, 6)
        fils = fil if fils is None else fils + fil
    j.paire("moustache", fils, "laiton", "tete")

    # ----- les oreilles : deux planchettes articulées, sur leur goupille -----
    o1 = A.repere((0.075, -0.215, 0.648), (-8, 14, 15))
    o2 = o1 @ A.repere((0, 0, 0.150), (-7, 0, 0))
    j.paire("oreille", A.boule(1.0, 40, 28).sculpte(_oreille(True)), "oreille", "oreille_G", mat=o1)
    j.paire("oreille2", A.boule(1.0, 40, 28).sculpte(_oreille(False)), "oreille", "oreille2_G", mat=o2)
    j.paire("goupille", A.cylindre(0.0075, 0.046, 0.002, 16), "laiton", "oreille_G", mat=o1 @ A.repere((0, -0.027, 0.157), (-90, 0, 0)))

    # ----- les pattes avant : deux quilles et leurs petons -----
    quille = A.tour(A.profil([(0, 0.02), (0.03, 0.024), (0.034, 0.06), (0.03, 0.15), (0.036, 0.215), (0.03, 0.25), (0, 0.262)], 5), 32)
    j.paire("patte", quille, "patte", "patte_G", (0.105, -0.18, 0.0), (-14, 0, 0))
    j.paire("peton", A.boule(1.0, 32, 16).etire(0.05, 0.066, 0.036), "peton", "patte_G", (0.105, -0.203, 0.036))

    # ----- les pattes arrière : une cuisse en galet, un long pied -----
    def galet(v):
        s = v.copy()
        s[:, 0] = np.sign(v[:, 0]) * np.abs(v[:, 0]) ** 0.72
        return s

    def semelle(v):
        s = v.copy()
        s[:, 2] = np.maximum(v[:, 2], -0.55)
        s[:, 0] *= 0.82 + 0.18 * (1 - v[:, 1]) * 0.5
        return s

    j.paire("cuisse", A.boule(1.0, 56, 28).sculpte(galet).etire(0.058, 0.135, 0.118), "cuisse", "cuisse_G", (0.195, 0.085, 0.165), (-12, 0, 0))
    j.paire("rivet", A.boule(1.0, 24, 12).etire(0.011, 0.021, 0.021), "laiton", "cuisse_G", (0.253, 0.085, 0.19))
    j.paire("pied", A.boule(1.0, 40, 20).sculpte(semelle).etire(0.042, 0.128, 0.036), "pied", "pied_G", (0.205, -0.005, 0.022))

    # ----- la queue : un pinceau, manche, virole et poils -----
    q = A.repere((0, 0.205, 0.29), A.viser(QUEUE))
    j.piece("manche", A.cylindre(0.026, 0.075, 0.004, 28), "manche", "queue", mat=q)
    virole = A.tour(A.conges([(0, 0.06), (0.031, 0.06), (0.034, 0.066), (0.034, 0.084), (0.038, 0.088), (0.038, 0.094),
                              (0.034, 0.098), (0.035, 0.122), (0.039, 0.127), (0.039, 0.138), (0, 0.138)], 0.0015, 3), 40)
    j.piece("virole", virole, "acier", "queue", mat=q)
    meche = A.tour(A.profil([(0, 0.13), (0.03, 0.132), (0.037, 0.16), (0.05, 0.215), (0.046, 0.27), (0.028, 0.325), (0.008, 0.36), (0, 0.368)], 8), 136)
    j.piece("meche", meche.sculpte(_poils), "meche", "queue", mat=q)

    # ----- la mécanique : la clé dans le dos, deux engrenages sur le flanc -----
    c = A.repere((0, 0.107, 0.385), A.viser(DOS))
    j.piece("embase", A.cylindre(0.031, 0.03, 0.006, 32), "laiton", "corps", mat=c)
    cle = A.cylindre(0.0115, 0.135, 0.003, 20).pose((0, 0, 0.02)) + A.boule(0.019, 24, 12).pose((0, 0, 0.158))
    for s in (-1, 1):
        cle = cle + A.tore(0.04, 0.0115, 40, 12).pose((s * 0.051, 0, 0.176), (90, 0, 0))
    j.piece("cle", cle, "laiton", "cle", mat=c)

    for nom, centre, rayon, dents, tour_de in (("roue1", Vector((0.139, 0.117, 0.352)), 0.068, 10, 0.0),
                                                ("roue2", Vector((0.131, 0.020, 0.378)), 0.042, 6, 30.0)):
        r = A.repere(centre + FLANC * 0.013, A.viser(FLANC)) @ A.repere(rot=(0, 0, tour_de))
        j.piece(nom, A.decoupe(A.contour_engrenage(rayon, dents), 0.02, 0.003, 2, rayon * 0.3), "laiton", nom, mat=r)
        j.piece(nom + "_axe", A.cylindre(rayon * 0.2, 0.05, 0.002, 16).pose((0, 0, -0.03)) + A.boule(rayon * 0.23, 16, 8).pose((0, 0, 0.02)), "acier", nom, mat=r)

    # ----- le squelette -----
    j.articulation("racine", None, (0, 0, 0))
    j.articulation("corps", "racine", (0, 0.05, 0.22))
    j.articulation("tete", "corps", (0, -0.17, 0.42))
    j.articulation("oreille_G", "tete", o1 @ Vector((0, 0, 0)), True)
    j.articulation("oreille2_G", "oreille_G", o1 @ Vector((0, 0, 0.157)), True)
    j.articulation("paupiere_G", "tete", OEIL, True)
    j.articulation("patte_G", "corps", (0.105, -0.117, 0.25), True)
    j.articulation("cuisse_G", "corps", (0.195, 0.095, 0.20), True)
    j.articulation("pied_G", "cuisse_G", (0.205, 0.10, 0.045), True)
    j.articulation("queue", "corps", q @ Vector((0, 0, 0)))
    j.articulation("cle", "corps", c @ Vector((0, 0, 0)))
    j.articulation("roue1", "corps", (0.139, 0.117, 0.352))
    j.articulation("roue2", "corps", (0.131, 0.020, 0.378))


ARGILE = {
    "corps": ((0.95, 0.90, 0.78), 0.4, 0), "tete": ((0.95, 0.90, 0.78), 0.4, 0), "oreille": ((0.95, 0.90, 0.78), 0.4, 0),
    "patte": ((0.95, 0.90, 0.78), 0.4, 0), "cuisse": ((0.95, 0.90, 0.78), 0.4, 0), "pied": ((0.95, 0.90, 0.78), 0.4, 0),
    "paupiere": ((0.95, 0.90, 0.78), 0.4, 0), "peton": ((0.93, 0.62, 0.68), 0.4, 0), "museau": ((0.93, 0.62, 0.68), 0.4, 0),
    "truffe": ((0.85, 0.30, 0.38), 0.3, 0), "collier": ((0.70, 0.07, 0.04), 0.3, 0), "oeil": ((0.01, 0.01, 0.01), 0.05, 0),
    "laiton": ((0.85, 0.52, 0.12), 0.28, 1), "acier": ((0.55, 0.57, 0.60), 0.3, 1), "manche": ((0.62, 0.40, 0.18), 0.6, 0),
    "meche": ((0.70, 0.07, 0.04), 0.6, 0),
}


def argile():
    A.neuf()
    j = A.Jouet("lapinceau")
    pieces(j)
    ob = j.monter()
    for nom in j.matieres:
        couleur, rugosite, metal = ARGILE[nom]
        ob.data.materials.append(A._principled(nom, couleur, rugosite, metal))
    print("[argile] points :", len(ob.data.vertices), " faces :", len(ob.data.polygons))
    A.studio()
    A.photo(os.path.join(APERCUS, "argile-1-trois-quarts.png"), (1.35, -1.9, 1.0), (0, 0.0, 0.43), 42)
    A.photo(os.path.join(APERCUS, "argile-2-face.png"), (0.3, -2.4, 0.6), (0, 0.0, 0.45), 42)
    A.photo(os.path.join(APERCUS, "argile-3-dos.png"), (1.2, 1.9, 1.35), (0, 0.0, 0.40), 42)
    A.photo(os.path.join(APERCUS, "argile-4-profil.png"), (2.5, 0.0, 0.5), (0, 0.0, 0.43), 42)


if __name__ == "__main__":
    if "argile" in sys.argv:
        argile()
