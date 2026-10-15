"""Le bœuf musqué en peluche de magasin : un brun encre, presque noir, qui disparaît sous sa propre laine : une grande
jupe de poils qui lui tombe jusqu'aux chaussettes crème, la bosse des épaules, une selle crème sur le dos, la tête
basse sous un casque de cornes ivoire (le bouclier du front, puis les cornes qui descendent le long des joues et
remontent à la pointe). Un mur de laine, têtu, qui n'a rien à prouver : il vous regarde par en dessous, sans bouger.

    python boeuf_musque.py        fabrique la fiche art/apercus/animaux/boeuf_musque.png (peluche de magasin, palier 4)
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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
ENCRE = M.hexa("#5d463c")                     # la dominante : brun encre (le poil le fonce presque jusqu'au noir : on le prend plus clair)
SOUS = M.hexa("#3a2b26")                      # le dessous de la jupe, les mèches du bas
CREME = M.hexa("#fff0d2")                     # la selle, les chaussettes
IVOIRE = M.hexa("#fff6e0")                    # l'accent : les cornes
CORNE = M.hexa("#cdb78c")                     # le bout des cornes, les sabots
NEZ = M.hexa("#a08a78")                       # le museau : pâle, comme le vrai (le visage se lit enfin)
CORPS = Vector((0.0, 0.050, 0.400))
TETE = Vector((0.0, -0.440, 0.350))
LACET, PIQUE = 24.0, -6.0                    # la tête tournée vers nous, le nez baissé


def meche(chemin, large, face, plat=0.36, long_pointe=0.93, cotes=18):
    """Une mèche plate (le geste du cheval et du renne) : un fuseau tourné, aplati, couché le long d'un chemin ;
    « face » : la direction de son épaisseur (on la voit de plat depuis là)."""
    p = A.courbe(chemin, 8)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    n0 = np.asarray(face, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.linalg.norm(t, axis=1, keepdims=True)
        x = np.cross(n0, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.60 * large, 0.05 * L), (0.95 * large, 0.22 * L), (large, 0.42 * L), (0.72 * large, 0.70 * L),
                     (0.30 * large, long_pointe * L), (0.06 * large, 0.985 * L), (0, L)], 5)
    return A.tour(prof, cotes).etire(1.0, plat, 1.0).sculpte(couche)


def construire():
    a = K.Animal("boeuf_musque")
    a.taille = 2.40

    # ----- le corps : une masse ronde, la bosse haute sur les épaules, la croupe basse -----
    def masse(v):
        v = K.bosse(v, (0, -0.50, 0.80), 0.30, 0.45)                  # la grosse bosse des épaules
        s = v * [0.255, 0.400, 0.178]
        s[:, 2] *= 1 - 0.34 * K.lisse((v[:, 1] - 0.0) / 1.0)           # la croupe bien plus basse
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(masse), ENCRE, pos=CORPS)
    # la selle crème : un large pan sur le dos, derrière la bosse
    a.rustine("selle", "corps", CORPS + Vector((0, 0.00, 0.0)), (0, 0.25, 1.0), lambda th: 0.46 - 0.10 * math.cos(2 * th), CREME, 0.004, 0)

    # ----- la jupe de poils : une trentaine de longues mèches plates, nées du flanc, qui tombent en s'évasant jusqu'à
    #       mi-jambe, une sur deux plus sombre (le geste des fanons du cheval) -----
    rng = np.random.default_rng(7)
    claires, sombres = None, None
    for i in range(36):
        t = 2 * math.pi * (i + rng.uniform(-0.25, 0.25)) / 36
        base = np.array([0.246 * math.cos(t), CORPS.y + 0.384 * math.sin(t)])
        radial = np.array([math.cos(t) * 1.0, math.sin(t) * 0.62])
        radial /= np.linalg.norm(radial)
        k = 0.85 + 0.40 * rng.random() + 0.18 * max(0.0, -math.sin(t))                # plus longues devant, là où il est plus laineux
        z0 = CORPS.z - 0.03
        chemin = [(base[0] * 0.94, base[1] * 0.94 + CORPS.y * 0.06, z0 + 0.04),
                  (base[0] + radial[0] * 0.010, base[1] + radial[1] * 0.010, z0 - 0.07),
                  (base[0] + radial[0] * 0.040, base[1] + radial[1] * 0.040, z0 - 0.145 * k),
                  (base[0] + radial[0] * 0.062, base[1] + radial[1] * 0.062, z0 - 0.225 * k)]
        m = meche(chemin, 0.054 + 0.010 * rng.random(), (radial[0], radial[1], 0.0), 0.40)
        if i % 2:
            sombres = m if sombres is None else sombres + m
        else:
            claires = m if claires is None else claires + m
    a.piece("meches_a", claires, ENCRE)
    a.piece("meches_b", sombres, SOUS)

    # ----- les chaussettes crème : quatre jambes courtes qui dépassent de la jupe, les sabots corne -----
    for nom, x, y in (("av_G", 0.120, -0.250), ("av_D", -0.120, -0.250), ("ar_G", 0.130, 0.320), ("ar_D", -0.130, 0.320)):
        a.piece("jambe_" + nom, A.tube(A.courbe([(x, y, 0.300), (x, y - 0.004, 0.150), (x, y - 0.010, 0.040)], 5), 0.058, 16), CREME)
        a.piece("sabot_" + nom, A.boule(1.0, 24, 12).etire(0.056, 0.066, 0.036), CORNE, pos=(x, y - 0.014, 0.026), poil=False)

    # ----- la tête : longue, lourde, penchée ; le museau pâle bien en vue, des poils longs sur les joues -----
    H = A.repere(TETE, (PIQUE, 0, LACET))
    H3 = H.to_3x3()

    def tete_f(v):
        s = v.copy()
        s[:, 0] *= 0.66 + 0.10 * K.lisse((-v[:, 1] + 0.1) / 0.9)
        s = K.bosse(s, (0, -1, -0.2), 0.12, 0.35)
        return s * [0.172, 0.200, 0.150]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(tete_f), SOUS, mat=H)
    a.piece("museau", A.boule(1.0, 36, 18).etire(0.078, 0.092, 0.068), NEZ, mat=H @ A.repere((0, -0.165, -0.050)))
    a.piece("nez", A.boule(1.0, 24, 12).etire(0.040, 0.026, 0.030), CORNE, mat=H @ A.repere((0, -0.245, -0.050)), poil=False)
    a.tete = H @ Vector((0, -0.200, -0.040))

    # ----- les yeux : de petites billes sous la corne, sous une paupière lourde : il vous toise par en dessous -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.78, -0.52, 0.14)))
        a.bouton("oeil_" + nom, p + n * 0.003, n, 0.028)
        a.piece("lourde_" + nom, K.paupiere(0.032, 0.10), SOUS, mat=A.cadre(p + n * 0.006, n, H3 @ Vector((0, 0, 1))))

    # ----- le casque de cornes : le bouclier ivoire sur le front, puis la corne qui descend le long de la joue et
    #       remonte, la pointe corne tournée vers l'avant -----
    a.piece("bouclier", A.boule(1.0, 36, 16).etire(0.125, 0.085, 0.034), IVOIRE, mat=H @ A.repere((0, -0.040, 0.118), (-10, 0, 0)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [H @ Vector(q) for q in ((c * 0.100, -0.030, 0.110), (c * 0.170, -0.020, 0.085), (c * 0.205, -0.030, 0.000),
                                         (c * 0.205, -0.085, -0.075), (c * 0.180, -0.140, -0.060), (c * 0.165, -0.175, 0.010))]
        corne = K.tube_peint(A.courbe(chemin, 6), lambda t: 0.034 - 0.025 * t, [(0.70, IVOIRE), (1, CORNE)], 18)
        a.piece("corne_" + nom, corne, None, poil=False)

    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("boeuf_musque", styles.style_de("boeuf_musque"), sys.modules[__name__]), "Bœuf musqué")
