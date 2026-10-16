"""Le lagopède en peluche, cinquième dessin (16/10, Art : d'après les vues d'un vrai gallinacé de la même famille, CC-BY,
regardé pour les proportions seulement, rien d'importé ; ses couleurs ne sont pas celles du lagopède). Plus d'œuf debout :
un gallinacé dodu POSÉ À L'HORIZONTALE, la poitrine ronde en avant et un peu relevée, le dos qui descend vers une
queue courte en éventail ; une petite tête ronde sur un cou court, le bec court, noir et crochu ; la caroncule vermillon
en croissant au-dessus de l'œil ; le dos, le cou et la tête grège mouchetés de brun, les ailes repliées, le ventre et
le dessous de la queue blancs, la queue noire bordée de blanc dessus ; des pattes emplumées de blanc jusqu'aux doigts.

    les 5 traits : le corps de perdrix dodu, horizontal ; la petite tête ronde au bec court et noir ; la caroncule rouge
    au-dessus de l'œil ; les pattes emplumées en chaussons blancs ; les ailes et le ventre blancs sous un manteau grège
    moucheté, la queue noire.

    python lagopede.py        fabrique la fiche art/apercus/animaux/lagopede.png (style du palier : C, velours ras)
    (refusés : trois « boules » le 15/10, puis « un œuf aux chaussons détachés et à la queue en palette » le 16/10)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

GREGE = np.array(M.hexa("#c4ad8e"))           # la dominante (registre : grège moucheté #cbb79a ; le velours la fonce un peu)
MOUCHE = np.array(M.hexa("#7f6a55"))          # les mouchetures
BLANC = np.array(M.hexa("#fbf9f4"))           # les ailes, le ventre, les chaussons
NOIR = np.array(M.hexa("#26211f"))            # la queue
VERMILLON = np.array(M.hexa("#ee3b22"))       # l'accent : la caroncule
CREME = np.array(M.hexa("#fffaf0"))           # le fin tour de l'œil
BEC = M.hexa("#241e1c")
TETE = Vector((0.0, -0.190, 0.392))


def mouchetures(v, cote, rayon, graine=0, proba=0.6):
    """Vrai là où un point tombe dans une petite tache (des sphères au hasard dans un quadrillage 3D, coupées par la peau)."""
    v = np.asarray(v, float)
    base = np.floor(v / cote).astype(np.int64)
    dedans = np.zeros(len(v), bool)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                c = base + np.array([dx, dy, dz], dtype=np.int64)
                h = ((c[:, 0] * 73856093) ^ (c[:, 1] * 19349663) ^ (c[:, 2] * 83492791) ^ (graine * 40503)) & 0x7FFFFFFF

                def alea(m):
                    return ((((h * m) + 12345) >> 9) & 0xFFFF) / 65535.0
                present = alea(1103515245) < proba
                centre = (c + np.stack([alea(214013), alea(1664525), alea(22695477)], axis=1)) * cote
                r = rayon * (0.65 + 0.70 * alea(134775813))
                dedans |= present & (np.linalg.norm(v - centre, axis=1) < r)
    return dedans


def construire():
    a = K.Animal("lagopede")
    a.taille = 0.50
    a.gonflage_reglages = {"fins": 0.0, "pointes": 0.0}    # la queue reste une queue plate (gonflée, elle faisait une palette ronde)

    # ----- le corps : un fuseau dodu couché, la poitrine devant (-Y) relevée de 18°, la queue derrière -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))              # 0 : le dos ; pi : le ventre
        fr = m.v[:, 2] / L                                          # 0 : la croupe ; 1 : la poitrine
        t_ = np.tile(GREGE, (len(ang), 1))
        blanc = (ang > 1.95 + 0.55 * np.clip((fr - 0.55) / 0.40, 0.0, 1.0)) | ((fr < 0.22) & (ang > 1.35))
        t_[blanc] = BLANC                                           # le ventre blanc ; la poitrine reste grège
        taches = mouchetures(m.v, 0.030, 0.0085, 5) & ~blanc
        t_[taches] = MOUCHE
        return t_
    rayon = O.interp([(0.0, 0.0), (0.06, 0.062), (0.25, 0.102), (0.55, 0.126), (0.80, 0.122), (0.94, 0.090), (1.0, 0.040)])
    O.corps_h(a, "corps", (0.0, 0.130, 0.170), 0.300, rayon, peint, None, cotes=56, pitch=18.0,
              deforme=O.gabarit(poitrail=0.06, ventre=0.0, croupe=0.0))

    # ----- le cou, court et épais ; la tête ronde, un peu tournée vers nous -----
    cou = O.tube_r([(0.0, -0.110, 0.300), (0.0, -0.145, 0.340), (0.0, -0.172, 0.368)], [0.072, 0.066, 0.060], 22)
    tc = np.tile(GREGE, (len(cou.v), 1))
    tc[mouchetures(cou.v, 0.030, 0.0085, 9)] = MOUCHE
    cou.teinte = tc
    a.piece("cou", cou, None)
    RT = A.repere(TETE, (0, 0, 20))
    tete = A.boule(1.0, 56, 28)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(GREGE, (len(u), 1))
    t[mouchetures(tete.v * 0.075, 0.022, 0.0060, 13)] = MOUCHE
    OEIL_DIR = np.array([0.55, -0.78, 0.26])
    for c in (1, -1):
        e = OEIL_DIR * [c, 1, 1]
        e /= np.linalg.norm(e)
        t[(u @ e) > 0.910] = GREGE                                  # pas de moucheture autour de l'œil (pas d'œil en plus)
        t[(u @ e) > 0.9636] = CREME                                 # le fin tour clair de l'œil (l'œil couvre ~12,6°)
        cr = e * 0.80 + np.array([0.0, 0.0, 0.32])
        cr /= np.linalg.norm(cr)
        croissant = ((u @ cr) > math.cos(math.radians(14))) & ((u @ e) < math.cos(math.radians(15.5))) & (u[:, 2] > e[2] + 0.04)
        t[croissant] = VERMILLON                                    # la caroncule, en croissant au-dessus de l'œil
    tete.teinte = t
    a.piece("tete", tete.etire(0.076, 0.080, 0.072), None, mat=RT)
    O.paire_yeux(a, "tete", TETE, tuple(OEIL_DIR), 0.0150, couleur_lourde=tuple(GREGE), coupe=0.62, decolle=0.002, R=RT)
    a.tete = RT @ Vector((0.0, -0.085, -0.005))

    # ----- le bec : court, fort, noir, un peu crochu, planté dans la face -----
    bec = O.pointe(0.040, 0.020, 14).sculpte(lambda v: np.stack([v[:, 0], v[:, 1] - 0.30 * 0.040 * (v[:, 2] / 0.040) ** 2, v[:, 2]], axis=1))
    a.piece("bec", O.couche(bec.etire(1.0, 0.85, 1.0), RT @ A.cadre(Vector((0.0, -0.066, -0.010)), Vector((0.0, -1.0, -0.22)), Vector((0, 0, 1)))),
            BEC, poil=False)

    # ----- les ailes repliées, blanches, plaquées sur les flancs, le bout vers la queue -----
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 36, 18).sculpte(lambda v: K.emousse(v, 0.85))
        aile.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] * (1.0 - 0.35 * np.clip(v[:, 2], 0.0, 1.0) ** 1.5), v[:, 2]], axis=1))   # effilée vers l'arrière
        a.piece("aile_" + nom, O.teinte(aile.etire(0.030, 0.070, 0.115), BLANC), None,
                mat=A.cadre(Vector((c * 0.098, 0.040, 0.235)), Vector((c * 0.10, 1.0, -0.30)), Vector((0, 0, 1))))

    # ----- la queue : courte, en éventail, noire, le dessus bordé de blanc ; le dessous blanc -----
    q = A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.8))
    q.sculpte(lambda v: np.stack([v[:, 0] * (0.70 + 0.30 * np.clip(v[:, 1], -1, 1) ** 2 + 0.30 * (v[:, 1] + 1) * 0.5), v[:, 1], v[:, 2]], axis=1))
    tq = np.tile(NOIR, (len(q.v), 1))
    tq[(q.v[:, 2] > 0.35) & (q.v[:, 1] < 0.35)] = BLANC             # les couvertures blanches sur le dessus
    tq[q.v[:, 2] < -0.40] = BLANC                                   # le dessous
    q.teinte = tq
    a.piece("queue", q.etire(0.060, 0.075, 0.024), None, mat=A.repere((0.0, 0.180, 0.212), (-10, 0, 0)))          # plantée dans la croupe, un peu tombante

    # ----- les pattes : courtes, emplumées de blanc jusqu'aux doigts, plantées sous le ventre -----
    for nom, c in (("G", 1), ("D", -1)):
        jambe = O.tube_r([(c * 0.044, 0.010, 0.135), (c * 0.048, -0.002, 0.075), (c * 0.050, -0.012, 0.035)], [0.034, 0.030, 0.028], 18)
        a.piece("patte_" + nom, O.teinte(jambe, BLANC), None)
        pied = A.boule(1.0, 24, 12).sculpte(lambda v: K.emousse(v, 0.8))
        pied.sculpte(lambda v: K.bosse(v, (0.0, -1.0, 0.0), 0.35, 0.25))                     # les doigts emplumés devant
        a.piece("pied_" + nom, O.teinte(pied.etire(0.036, 0.054, 0.020), BLANC), None, pos=(c * 0.052, -0.034, 0.020))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lagopede", styles.style_de("lagopede"), sys.modules[__name__]), "Lagopède")
