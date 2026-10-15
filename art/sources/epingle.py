"""L'Épinglé : le mal-aimé de chaque biome, tel qu'on le croise d'abord. On l'a piqué d'épingles de couturière à
grosses têtes de verre (la seule couleur qui lui reste), une couture lâche sur son flanc et la bourre en sort.
Quand le joueur le soigne, les épingles tombent, la couture se referme, et il redevient l'animal ordinaire pour toujours.
Validé par l'auteur le 13 octobre 2026, sur le renard (« oui, c'est ça »).

Dans le fichier d'un animal qui est un Épinglé :

    EPINGLE = dict(epingles=[(pièce piquée, un point dedans, la direction où l'on vise sa surface, de combien elle penche), ...],
                   couture=(pièce, un point dedans, la direction visée, la direction de la fente))

L'usine ajoute alors les épingles et la couture au modèle, chacune sur son os :
    epingle_1, epingle_2, ...   une épingle (sa tige et sa tête), enfant de l'os de la pièce piquée
    couture                     la fente, la bourre et les points qui ont sauté
Les animations ne touchent jamais ces os : c'est le jeu qui les met à l'échelle 1 (Épinglé) ou 0 (guéri), une par une.
"""
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K

ACIER = M.hexa("#9aa0aa")
TETES = (K.FRAMBOISE, K.MOUTARDE, K.TURQUOISE)
FENTE = M.hexa("#26242a")
OS_LIBRES = ("epingle", "couture")           # les os que les animations ne touchent pas


def epingler(a, epingles=(), couture=None, long=0.075, tete=0.0125):
    """Plante les épingles et ouvre la couture. À appeler avant a.a_taille() : tout est dans les mesures du modèle.
    Rend les os à créer : (nom de l'os, la pièce piquée, la position de l'os)."""
    os_ = []
    for i, (sur, centre, direction, penche) in enumerate(epingles, 1):
        p, n = a.surface(sur, centre, direction)
        axe = (Vector(n) + Vector((penche[0], penche[1], 0.0))).normalized()
        rep = A.repere(Vector(p), A.viser(axe))
        tige = A.tube([(0, 0, -0.012), (0, 0, long)], 0.0026, 8)
        a._poser(a._jouet(a._durs, ACIER, "d"), "epingle_%d_tige" % i, tige, "bouton", rep, False, "volume", "dur")
        a._poser(a._jouet(a._durs, TETES[(i - 1) % len(TETES)], "d"), "epingle_%d_tete" % i, A.boule(tete, 14, 7).pose((0, 0, long)), "bouton", rep, False,
                 "volume", "dur")
        os_.append(("epingle_%d" % i, sur, tuple(p)))
    if couture:
        sur, centre, direction, sens = couture
        p, n = a.surface(sur, centre, direction)
        rep = A.cadre(Vector(p) + Vector(n) * 0.002, Vector(n), Vector(sens))
        a.piece("couture_fente", A.boule(1.0, 20, 10).etire(0.013, 0.052, 0.004), FENTE, mat=rep, poil=False)
        bourre = A.boule(0.017, 14, 7).pose((0.0, 0.012, 0.011)) + A.boule(0.014, 14, 7).pose((0.004, -0.016, 0.010)) + A.boule(0.012, 12, 6).pose((-0.003, -0.002, 0.020))
        a.piece("couture_bourre", bourre, K.BLANC, mat=rep)
        for k, points in enumerate((((-0.024, 0.036, 0.004), (0.0, 0.038, 0.011), (0.024, 0.040, 0.004)),              # un point qui tient encore
                                    ((-0.024, -0.030, 0.004), (-0.012, -0.036, 0.014), (-0.020, -0.050, 0.022)),       # deux qui ont sauté
                                    ((0.024, 0.004, 0.004), (0.030, 0.000, 0.016), (0.040, -0.012, 0.010)))):
            a.broderie("couture_point%d" % k, [rep @ Vector(q) for q in points], 0.0030, K.NOIR)
        os_.append(("couture", sur, tuple(p)))
    return os_


def porteurs(os_):
    """Les lignes à mettre EN TÊTE de PORTEURS (la première qui correspond gagne ; « cou » attraperait « couture »)."""
    return [(nom + "_", nom) for nom, _piece, _pos in os_]


def nettoyer_glb(chemin, prefixes=OS_LIBRES):
    """Retire d'un .glb les pistes d'animation des os que le jeu commande lui-même : l'export de Blender écrit une piste
    pour chaque os, et une piste « échelle 1 » remettrait les épingles à chaque image. Rend le nombre de pistes retirées."""
    import json
    import struct
    with open(chemin, "rb") as f:
        donnees = f.read()
    long_json = struct.unpack_from("<I", donnees, 12)[0]
    doc = json.loads(donnees[20:20 + long_json])
    reste = donnees[20 + long_json:]
    libres = {i for i, noeud in enumerate(doc.get("nodes", [])) if noeud.get("name", "").startswith(tuple(prefixes))}
    retirees = 0
    for anim in doc.get("animations", []):
        gardees = [c for c in anim["channels"] if c["target"].get("node") not in libres]
        retirees += len(anim["channels"]) - len(gardees)
        anim["channels"] = gardees
    if retirees:
        texte = json.dumps(doc, separators=(",", ":")).encode("utf-8")
        texte += b" " * (-len(texte) % 4)
        with open(chemin, "wb") as f:
            f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(texte) + len(reste)))
            f.write(struct.pack("<II", len(texte), 0x4E4F534A) + texte + reste)
    return retirees
