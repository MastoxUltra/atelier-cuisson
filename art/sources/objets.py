"""Les objets qui traînent dans les prés : tronc couché, souche, champignons, clôture, barrière, meule, panneau,
puits, ruche, épouvantail, petit pont.

    python objets.py              fabrique tout dans art/modeles/decor/objets/ et un aperçu art/apercus/decor/objets.png
    python objets.py puits pont   seulement ceux-là

SANS BLENDER : le maillage, le fichier .glb et l'aperçu sont écrits ici, en Python et numpy (quelques secondes de
processeur, pas de carte graphique). L'aperçu est un dessin de contrôle, pas une belle photo.

Ce que le jeu reçoit : <nom>.glb, sans squelette, l'origine au pied, en vrais mètres, regardant vers +Z comme le reste.
Chaque surface porte le nom de sa texture, rangée dans le même dossier : « bois », « bois_peint », « ecorce »,
« coupe », « paille », « pierre », « toile », « champignon ». Les textures se répètent (sauf coupe et champignon).
La couleur de sommet est la lumière et la teinte peintes, à multiplier à l'albédo (comme le rocher) : pas du vent.
"""
import json
import math
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw

ICI = os.path.dirname(os.path.abspath(__file__))
OBJETS = os.path.normpath(os.path.join(ICI, "..", "modeles", "decor", "objets"))
APERCUS = os.path.normpath(os.path.join(ICI, "..", "apercus", "decor"))
TAU = math.tau
HAUT = np.array([0.0, 0.0, 1.0])
DECOUPEES = ("lierre", "glycine", "filet", "roseaux_secs", "bache")   # les surfaces dont la texture a des trous (transparence à découper),
                                                    # ou vues des deux côtés (la bâche du jardin : sans trous, mais elle pend)


def tourne(rx=0.0, ry=0.0, rz=0.0):
    """La matrice d'une rotation, en degrés, autour de X puis Y puis Z."""
    a, b, c = (math.radians(v) for v in (rx, ry, rz))
    mx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    my = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    mz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return mz @ my @ mx


# ---------------------------------------------------------------- le maillage

class Maillage:
    """Des triangles rangés par matière : positions, normales, UV (u à droite, v vers le bas de l'image), teinte."""

    def __init__(self, graine=1):
        self.parts = {}
        self.rng = np.random.default_rng(graine)

    def ajoute(self, matiere, pos, nor, uv, tris, teinte=(1.0, 1.0, 1.0)):
        part = self.parts.setdefault(matiere, {"pos": [], "nor": [], "uv": [], "col": [], "tri": []})
        base = len(part["pos"])
        part["pos"] += [np.asarray(q, float) for q in pos]
        part["nor"] += [np.asarray(q, float) / (np.linalg.norm(q) + 1e-12) for q in nor]
        part["uv"] += [tuple(q) for q in uv]
        part["col"] += list(teinte) if isinstance(teinte, list) else [tuple(teinte)] * len(pos)
        for a, b, c in tris:                                    # le sens du triangle suit sa normale : le jeu ne dessine que l'avant
            face = np.cross(part["pos"][base + b] - part["pos"][base + a], part["pos"][base + c] - part["pos"][base + a])
            if np.dot(face, part["nor"][base + a] + part["nor"][base + b] + part["nor"][base + c]) < 0:
                b, c = c, b
            part["tri"].append((a + base, b + base, c + base))

    BISEAU_MAX, BISEAU_MIN_PIECE, BISEAU_PART = 0.03, 0.03, 0.2     # les arêtes arrondies (l'auteur, 15/10 : « trop de formes GameCube »)

    def boite(self, matiere, centre, dims, rot=None, teinte=(1, 1, 1), motif=1.0, biseau=None):
        """Une planche, un poteau, une caisse : le fil du bois suit sa plus grande longueur. Ses arêtes sont biseautées (biseau :
        la largeur du biseau en mètres ; None : un cinquième du plus petit côté, 3 cm au plus, rien sous 3 cm d'épaisseur ; 0 :
        des arêtes vives). Les normales du biseau sont celles des deux faces qu'il joint : l'ombrage passe en douceur, comme sur
        un bord arrondi, pour 32 triangles de plus."""
        rot = np.eye(3) if rot is None else rot
        centre, demi = np.asarray(centre, float), np.asarray(dims, float) * 0.5
        if biseau is None:
            petit = float(min(dims))
            biseau = min(self.BISEAU_PART * petit, self.BISEAU_MAX) if petit >= self.BISEAU_MIN_PIECE else 0.0
        if biseau > 0.0:
            return self._boite_biseautee(matiere, centre, demi, rot, teinte, motif, min(float(biseau), 0.45 * float(min(demi))))
        decal = self.rng.uniform(0, 1, 2)
        for axe in range(3):
            a, b = [k for k in range(3) if k != axe]
            if dims[a] < dims[b]:
                a, b = b, a                                    # u le long du plus grand côté
            for signe in (-1, 1):
                n = np.zeros(3)
                n[axe] = signe
                coins = []
                for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    q = np.zeros(3)
                    q[axe], q[a], q[b] = signe * demi[axe], sa * demi[a], sb * demi[b]
                    coins.append(q)
                if np.dot(np.cross(coins[1] - coins[0], coins[2] - coins[0]), n) < 0:
                    coins = coins[::-1]
                uv = [(q[a] / motif + decal[0], q[b] / motif + decal[1]) for q in coins]
                self.ajoute(matiere, [centre + rot @ q for q in coins], [rot @ n] * 4, uv, [(0, 1, 2), (0, 2, 3)], teinte)

    def _boite_biseautee(self, matiere, centre, demi, rot, teinte, motif, b):
        """La boîte aux arêtes biseautées : six faces rentrées de b sur leurs bords, douze bandes de biseau, huit coins."""
        decal = self.rng.uniform(0, 1, 2)
        axes_uv = {}
        for axe in range(3):
            a_, b_ = [k for k in range(3) if k != axe]
            if demi[a_] < demi[b_]:
                a_, b_ = b_, a_                                # u le long du plus grand côté
            axes_uv[axe] = (a_, b_)
        uv_de = lambda axe, q: (q[axes_uv[axe][0]] / motif + decal[0], q[axes_uv[axe][1]] / motif + decal[1])
        e = np.eye(3)
        coul = tuple(teinte)
        arete = tuple(min(1.0, c * 1.05) for c in teinte)      # les arêtes un peu usées, plus claires

        def poser(points, normales, couleurs, sens):
            q = [np.asarray(x, float) for x in points]
            tris = [(0, 1, 2)] if len(q) == 3 else [(0, 1, 2), (0, 2, 3)]
            if np.dot(np.cross(q[1] - q[0], q[2] - q[0]), sens) < 0:
                tris = [(0, 2, 1)] if len(q) == 3 else [(0, 2, 1), (0, 3, 2)]
            uv = [uv_de(int(np.argmax(np.abs(n))), x) for x, n in zip(q, normales)]
            self.ajoute(matiere, [centre + rot @ x for x in q], [rot @ n for n in normales], uv, tris, list(couleurs))

        r = demi - b                                           # la boîte intérieure
        for axe in range(3):                                   # les six faces
            a_, b_ = axes_uv[axe]
            for signe in (-1, 1):
                n = e[axe] * signe
                coins = []
                for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    q = np.zeros(3)
                    q[axe], q[a_], q[b_] = signe * demi[axe], sa * r[a_], sb * r[b_]
                    coins.append(q)
                poser(coins, [n] * 4, [coul] * 4, n)
        for i, j, k in ((0, 1, 2), (0, 2, 1), (1, 2, 0)):        # les douze bandes, le long de k
            for si in (-1, 1):
                for sj in (-1, 1):
                    ni, nj = e[i] * si, e[j] * sj
                    pts = []
                    for sk, cote in ((-1, "i"), (1, "i"), (1, "j"), (-1, "j")):
                        q = np.zeros(3)
                        q[k] = sk * r[k]
                        if cote == "i":
                            q[i], q[j] = si * demi[i], sj * r[j]
                        else:
                            q[i], q[j] = si * r[i], sj * demi[j]
                        pts.append(q)
                    poser(pts, [ni, ni, nj, nj], [arete] * 4, ni + nj)
        for si in (-1, 1):                                     # les huit coins
            for sj in (-1, 1):
                for sk in (-1, 1):
                    s3 = np.array([si, sj, sk], float)
                    pts, nrm = [], []
                    for axe in range(3):
                        q = r * s3
                        q[axe] = s3[axe] * demi[axe]
                        pts.append(q)
                        nrm.append(e[axe] * s3[axe])
                    poser(pts, nrm, [arete] * 3, s3)

    def poutre(self, matiere, a, b, section=(0.08, 0.08), teinte=(1, 1, 1), motif=1.0):
        """Une pièce de bois droite entre deux points (une lisse, une écharpe, un limon d'escalier)."""
        a, b = np.asarray(a, float), np.asarray(b, float)
        ex = (b - a) / np.linalg.norm(b - a)
        ez = HAUT - ex * np.dot(HAUT, ex)
        ez = ez / np.linalg.norm(ez) if np.linalg.norm(ez) > 1e-6 else np.array([1.0, 0, 0])
        self.boite(matiere, (a + b) / 2, (float(np.linalg.norm(b - a)), section[0], section[1]), np.stack([ex, np.cross(ez, ex), ez], axis=1), teinte, motif)

    def tube(self, matiere, chemin, rayons, cotes=10, bouts=(None, None), teinte=(1, 1, 1), tours=1, motif=1.0, bosses=0.0, vents=None):
        """Un rondin, une branche, une tige, le long d'un chemin. bouts : la matière de chaque bout (None = ouvert).
        bosses : les racines du pied (le premier anneau s'évase en étoile)."""
        ch = np.asarray(chemin, float)
        n = len(ch)
        avant = ch[1] - ch[0]
        avant /= np.linalg.norm(avant)
        cote = np.cross(avant, [1.0, 0, 0] if abs(avant[0]) < 0.9 else [0, 1.0, 0])
        cote /= np.linalg.norm(cote)
        pos, nor, uv, long = [], [], [], 0.0
        reperes = []
        for i in range(n):
            t = ch[min(i + 1, n - 1)] - ch[max(i - 1, 0)]
            t /= np.linalg.norm(t)
            cote = cote - t * np.dot(cote, t)
            cote /= np.linalg.norm(cote)
            bi = np.cross(t, cote)
            reperes.append((t, cote.copy(), bi))
            if i:
                long += float(np.linalg.norm(ch[i] - ch[i - 1]))
            for j in range(cotes + 1):
                a = TAU * j / cotes
                r = rayons[i] * (1 + (bosses * (0.5 + 0.5 * math.cos(5 * a + 0.7)) if i == 0 else 0.0))
                d = cote * math.cos(a) + bi * math.sin(a)
                pos.append(ch[i] + d * r)
                nor.append(d)
                uv.append((long / motif, j / cotes * tours) if matiere.startswith("bois") else (j / cotes * tours, long / motif))
        tris = []
        for i in range(n - 1):
            for j in range(cotes):
                a, b = i * (cotes + 1) + j, (i + 1) * (cotes + 1) + j
                tris += [(a, a + 1, b + 1), (a, b + 1, b)]
        if vents is not None:                                   # un arbre : la prise au vent, dans le rouge, anneau par anneau
            teinte = [(vents[i], 0.0, 0.0) for i in range(n) for _ in range(cotes + 1)]
        self.ajoute(matiere, pos, nor, uv, tris, teinte)
        for bout, i, sens in ((bouts[0], 0, -1), (bouts[1], n - 1, 1)):
            if bout is None:
                continue
            if vents is not None:
                teinte = (vents[i], 0.0, 0.0)
            t, cote, bi = reperes[i]
            pos, uv = [ch[i]], [(0.5, 0.5)]
            for j in range(cotes + 1):
                a = TAU * j / cotes
                r = rayons[i] * (1 + (bosses * (0.5 + 0.5 * math.cos(5 * a + 0.7)) if i == 0 else 0.0))
                pos.append(ch[i] + (cote * math.cos(a) + bi * math.sin(a)) * r)
                uv.append((0.5 + 0.48 * math.cos(a), 0.5 + 0.48 * math.sin(a)))
            tris = [(0, j + 1, j + 2) if sens > 0 else (0, j + 2, j + 1) for j in range(cotes)]
            self.ajoute(bout, pos, [t * sens] * len(pos), uv, tris, teinte)

    def tour(self, matiere, profil, cotes=16, centre=(0, 0, 0), teinte=(1, 1, 1), tours=2, motif=1.0, rayonnant=False):
        """Une forme tournée autour de la verticale : profil = [(rayon, hauteur), ...] du bas vers le haut.
        rayonnant : la texture est vue de dessus, son centre au sommet (un chapeau de champignon)."""
        centre = np.asarray(centre, float)
        pr = np.asarray(profil, float)
        pos, nor, uv, long = [], [], [], 0.0
        total = float(np.linalg.norm(pr[1:] - pr[:-1], axis=1).sum())
        for i in range(len(pr)):
            d = pr[min(i + 1, len(pr) - 1)] - pr[max(i - 1, 0)]
            if i:
                long += float(np.linalg.norm(pr[i] - pr[i - 1]))
            for j in range(cotes + 1):
                a = TAU * j / cotes
                pos.append(centre + [pr[i][0] * math.cos(a), pr[i][0] * math.sin(a), pr[i][1]])
                nor.append([d[1] * math.cos(a), d[1] * math.sin(a), -d[0]])
                if rayonnant:
                    e = 1.0 - long / total
                    uv.append((0.5 + 0.48 * e * math.cos(a), 0.5 + 0.48 * e * math.sin(a)))
                else:
                    uv.append((long / motif, j / cotes * tours) if matiere.startswith("bois") else (j / cotes * tours, -long / motif))
        tris = []
        for i in range(len(pr) - 1):
            for j in range(cotes):
                a, b = i * (cotes + 1) + j, (i + 1) * (cotes + 1) + j
                tris += [(a, a + 1, b + 1), (a, b + 1, b)]
        self.ajoute(matiere, pos, nor, uv, tris, teinte)

    def plaque(self, matiere, coins, teinte=(1, 1, 1), motif=1.0, deux_faces=False):
        """Un quadrilatère (quatre coins dans l'ordre), vu des deux côtés si on le demande."""
        q = [np.asarray(c, float) for c in coins]
        n = np.cross(q[1] - q[0], q[3] - q[0])
        u = (q[1] - q[0]) / (np.linalg.norm(q[1] - q[0]) + 1e-12)
        w = np.cross(n / (np.linalg.norm(n) + 1e-12), u)
        uv = [(float(np.dot(c - q[0], u)) / motif, float(np.dot(c - q[0], w)) / motif) for c in q]
        self.ajoute(matiere, q, [n] * 4, uv, [(0, 1, 2), (0, 2, 3)], teinte)
        if deux_faces:
            self.ajoute(matiere, q, [-n] * 4, uv, [(0, 2, 1), (0, 3, 2)], teinte)

    def peindre_lumiere(self, sombre=0.58):
        """La lumière peinte : le pied dans l'ombre, le haut et les faces tournées vers le ciel plus clairs."""
        haut = max(float(np.max(np.array(p["pos"])[:, 2])) for p in self.parts.values())
        for nom, p in self.parts.items():
            if nom == "lumiere":                                # une vitre allumée n'a pas d'ombre
                continue
            pos, nor = np.array(p["pos"]), np.array(p["nor"])
            lum = sombre + (0.90 - sombre) * np.clip(pos[:, 2] / max(haut, 1e-6), 0, 1) ** 0.6 + 0.10 * np.clip(nor[:, 2], 0, 1)
            p["col"] = [tuple(np.clip(np.array(c) * k, 0, 1)) for c, k in zip(p["col"], lum)]

    def triangles(self):
        return sum(len(p["tri"]) for p in self.parts.values())


# ---------------------------------------------------------------- le fichier .glb

def ecrire_glb(chemin, m, nom, teintes=True):
    """Écrit le maillage au format glTF binaire. Z vers le haut ici devient Y vers le haut là-bas, l'avant (-Y) devient +Z."""
    binaire, vues, accesseurs, primitives, matieres = bytearray(), [], [], [], []

    def bloc(tableau, cible, genre, composante, bornes=False):
        while len(binaire) % 4:
            binaire.append(0)
        donnees = tableau.tobytes()
        vues.append({"buffer": 0, "byteOffset": len(binaire), "byteLength": len(donnees), "target": cible})
        binaire.extend(donnees)
        acc = {"bufferView": len(vues) - 1, "componentType": composante, "count": int(len(tableau)), "type": genre}
        if bornes:
            acc["min"], acc["max"] = [float(v) for v in tableau.min(axis=0)], [float(v) for v in tableau.max(axis=0)]
        accesseurs.append(acc)
        return len(accesseurs) - 1

    for matiere, p in m.parts.items():
        pos, nor = np.array(p["pos"], np.float32), np.array(p["nor"], np.float32)
        vers = lambda t: np.stack([t[:, 0], t[:, 2], -t[:, 1]], axis=1).astype(np.float32)
        couleurs = np.clip(np.array(p["col"], np.float32), 0, 1)
        if teintes:                                            # une teinte peinte : le fichier la veut en linéaire. Du vent : tel quel
            couleurs = couleurs ** 2.2
        col = np.concatenate([couleurs, np.ones((len(pos), 1), np.float32)], axis=1)
        attributs = {"POSITION": bloc(vers(pos), 34962, "VEC3", 5126, True), "NORMAL": bloc(vers(nor), 34962, "VEC3", 5126),
                     "TEXCOORD_0": bloc(np.array(p["uv"], np.float32), 34962, "VEC2", 5126), "COLOR_0": bloc(col, 34962, "VEC4", 5126)}
        indices = bloc(np.array(p["tri"], np.uint32).reshape(-1), 34963, "SCALAR", 5125)
        fiche = {"name": matiere, "pbrMetallicRoughness": {"metallicFactor": 0.0, "roughnessFactor": 0.9}}
        if matiere in DECOUPEES:                               # une image à trous : le jeu la découpe et la montre des deux côtés
            fiche.update(alphaMode="MASK", alphaCutoff=0.5, doubleSided=True)
        matieres.append(fiche)
        primitives.append({"attributes": attributs, "indices": indices, "material": len(matieres) - 1})
    doc = {"asset": {"version": "2.0", "generator": "bibelots objets.py"}, "scene": 0, "scenes": [{"nodes": [0]}],
           "nodes": [{"name": nom, "mesh": 0}], "meshes": [{"name": nom, "primitives": primitives}], "materials": matieres,
           "accessors": accesseurs, "bufferViews": vues, "buffers": [{"byteLength": len(binaire)}]}
    texte = json.dumps(doc, separators=(",", ":")).encode("utf-8")
    texte += b" " * (-len(texte) % 4)
    binaire.extend(b"\x00" * (-len(binaire) % 4))
    with open(chemin, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(texte) + 8 + len(binaire)))
        f.write(struct.pack("<II", len(texte), 0x4E4F534A) + texte)
        f.write(struct.pack("<II", len(binaire), 0x004E4942) + bytes(binaire))
    print("[export]", os.path.basename(chemin), m.triangles(), "triangles,", " + ".join(m.parts), flush=True)


# ---------------------------------------------------------------- les textures, peintes par le code

def _bruit(taille, grain_x, grain_y, rng):
    """Un bruit doux qui se raccorde sur ses quatre bords."""
    petit = rng.uniform(0, 1, (grain_y, grain_x)).astype(np.float32)
    grand = Image.fromarray(np.tile(petit, (3, 3)), "F").resize((taille * 3, taille * 3), Image.BICUBIC)
    return np.clip(np.asarray(grand.crop((taille, taille, taille * 2, taille * 2)), float), 0, 1)


def _degrade(h, sombre, clair):
    return np.array(sombre, float) * (1 - h[..., None]) + np.array(clair, float) * h[..., None]


def _ecrire(chemin, couleur, haut=None, force=4.0):
    """Enregistre la texture et, si on donne sa hauteur, la carte de relief à côté (<nom>_relief.png)."""
    Image.fromarray(np.clip(couleur, 0, 255).astype(np.uint8), "RGB").save(chemin, optimize=True)
    if haut is not None:
        gx = (np.roll(haut, -1, 1) - np.roll(haut, 1, 1)) * force
        gy = (np.roll(haut, -1, 0) - np.roll(haut, 1, 0)) * force
        nn = np.stack([-gx, gy, np.ones_like(haut)], axis=2)
        nn /= np.linalg.norm(nn, axis=2, keepdims=True)
        Image.fromarray(((nn * 0.5 + 0.5) * 255).astype(np.uint8), "RGB").save(chemin[:-4] + "_relief.png", optimize=True)


def _cellules(taille, germes, large, haut):
    """Pour chaque point, la distance au germe le plus proche, au suivant, et le numéro du plus proche : des pierres,
    des pavés. Les distances se comptent en cases (large x haut cases dans l'image) et se raccordent d'un bord à l'autre."""
    y, x = (np.mgrid[0:taille, 0:taille] + 0.5) / taille
    f1, f2 = np.full((taille, taille), 9.0), np.full((taille, taille), 9.0)
    qui = np.zeros((taille, taille), int)
    for k, (gx, gy) in enumerate(germes):
        dx, dy = np.abs(x - gx % 1.0), np.abs(y - gy % 1.0)
        d = np.hypot(np.minimum(dx, 1 - dx) * large, np.minimum(dy, 1 - dy) * haut)
        proche = d < f1
        f2 = np.where(proche, f1, np.minimum(f2, d))
        qui = np.where(proche, k, qui)
        f1 = np.where(proche, d, f1)
    return f1, f2, qui


def peindre_bois(chemin, taille=1024, graine=1, sombre=(92, 64, 44), clair=(198, 160, 116), peint=False, planches=6):
    """Des planches jointives : le fil court de gauche à droite, un joint sombre entre deux planches, des nœuds.
    peint : un bois blanchi qui s'écaille, à teinter par la couleur de sommet."""
    rng = np.random.default_rng(graine)
    fil = 0.50 * _bruit(taille, 5, 90, rng) + 0.30 * _bruit(taille, 14, 220, rng) + 0.20 * rng.uniform(0, 1, (taille, taille))
    y = (np.arange(taille) + 0.5) / taille * planches
    rang = np.floor(y).astype(int) % planches
    dans = y - np.floor(y)
    joint = np.clip(1 - np.minimum(dans, 1 - dans) / 0.045, 0, 1)[:, None]            # 1 au milieu du joint
    ton = rng.uniform(-0.14, 0.14, planches)[rang][:, None]
    h = np.clip(0.30 + 0.60 * fil + ton + 0.20 * (_bruit(taille, 3, 5, rng) - 0.5), 0, 1)
    noeud = np.clip((_bruit(taille, 9, 26, rng) - 0.88) * 14, 0, 1)                     # des nœuds petits, allongés dans le fil
    if peint:
        c = _degrade(h, (214, 210, 202), (253, 251, 247))
        ecaille = np.clip((_bruit(taille, 16, 70, rng) - 0.88) * 12, 0, 1)[..., None]
        c = c * (1 - ecaille) + _degrade(h, (140, 112, 86), (190, 162, 128)) * ecaille
        c = c * (1 - 0.45 * joint[..., None])
    else:
        c = _degrade(h, sombre, clair) * (1 - 0.5 * noeud[..., None]) * (1 - 0.62 * joint[..., None])
    _ecrire(chemin, c, 0.35 * h + 0.65 * (1 - joint) - 0.3 * noeud, 3.0 if not peint else 2.2)


def peindre_ecorce(chemin, taille=512, graine=2):
    """Une écorce en plaques allongées (le haut de l'image vers le haut du tronc), avec un peu de mousse."""
    rng = np.random.default_rng(graine)
    f1, f2, _qui = _cellules(taille, rng.uniform(0, 1, (110, 2)), 30.0, 10.0)
    h = np.clip((f2 - f1) * 1.3, 0, 1) ** 0.6
    h = np.clip(h * (0.85 + 0.3 * _bruit(taille, 60, 12, rng)), 0, 1)
    c = _degrade(h, (70, 50, 38), (172, 136, 102))
    mousse = (np.clip((_bruit(taille, 4, 4, rng) - 0.62) * 5, 0, 1) * (0.5 + 0.5 * h))[..., None]
    _ecrire(chemin, c * (1 - mousse) + np.array((110, 140, 62), float) * mousse, h, 5.0)


def peindre_coupe(chemin, taille=256, graine=3):
    """Le bout d'un rondin scié : des cernes, quelques fentes, un liseré d'écorce."""
    rng = np.random.default_rng(graine)
    y, x = (np.mgrid[0:taille, 0:taille] + 0.5) / taille - 0.5
    r = np.hypot(x + 0.03, y - 0.02) * 2.08
    a = np.arctan2(y, x)
    cernes = 0.5 + 0.5 * np.sin(r * 58 + 2.5 * np.sin(a * 3 + 1.0))
    h = np.clip(0.55 + 0.30 * cernes - 0.25 * r + 0.08 * rng.uniform(0, 1, (taille, taille)), 0, 1)
    c = _degrade(h, (150, 110, 70), (232, 200, 150))
    fente = np.clip(1 - np.abs(np.sin(a * 2.5 + 0.4)) * 30, 0, 1) * np.clip(r * 1.6 - 0.3, 0, 1)
    c = c * (1 - 0.5 * fente[..., None])
    c[r > 0.90] = (86, 62, 46)
    _ecrire(chemin, c)


def peindre_paille(chemin, taille=1024, graine=4, couches=5):
    """Du chaume posé en couches : des brins serrés qui descendent, et l'ombre de chaque couche sur la suivante."""
    rng = np.random.default_rng(graine)
    brins = 0.55 * _bruit(taille, 260, 10, rng) + 0.30 * _bruit(taille, 520, 26, rng) + 0.15 * rng.uniform(0, 1, (taille, taille))
    bord = (_bruit(taille, 40, 2, rng)[0] - 0.5) * 0.16                                   # le bas de chaque couche est irrégulier
    y = (np.arange(taille) + 0.5)[:, None] / taille * couches + bord[None, :]
    dans = y - np.floor(y)                                                               # 0 en haut de la couche, 1 à son bord
    ombre = np.clip(dans / 0.16, 0, 1)                                                   # sous le bord de la couche du dessus
    h = np.clip(0.18 + 0.50 * brins + 0.32 * dans, 0, 1)
    c = _degrade(h, (150, 112, 46), (246, 218, 132))
    gris = np.clip((_bruit(taille, 5, 4, rng) - 0.55) * 3, 0, 1)[..., None] * 0.45       # des plages grisées par le temps
    c = c * (1 - gris) + _degrade(h, (124, 112, 84), (196, 184, 150)) * gris
    _ecrire(chemin, c * (0.58 + 0.42 * ombre)[..., None], 0.55 * dans + 0.45 * brins, 4.0)


def peindre_pierre(chemin, taille=1024, graine=5, rangs=7, par_rang=4):
    """Un mur de moellons : des pierres inégales en assises, bombées, des joints de mortier en creux."""
    rng = np.random.default_rng(graine)
    germes = [((j + 0.5 + rng.uniform(-0.28, 0.28) + (0.5 if i % 2 else 0.0)) / par_rang, (i + 0.5 + rng.uniform(-0.12, 0.12)) / rangs)
              for i in range(rangs) for j in range(par_rang)]
    f1, f2, qui = _cellules(taille, germes, par_rang, rangs)
    bombe = np.clip((f2 - f1) * 2.6, 0, 1) ** 0.5
    ton, chaud, froid = (rng.uniform(0, 1, len(germes))[qui] for _ in range(3))
    grain = 0.6 * _bruit(taille, 110, 110, rng) + 0.4 * rng.uniform(0, 1, (taille, taille))
    pierre = _degrade(np.clip(0.15 + 0.75 * ton, 0, 1), (128, 124, 118), (216, 210, 198))
    for teinte, part in (((204, 176, 138), np.clip(chaud - 0.55, 0, 1) * 1.2), ((150, 162, 178), np.clip(froid - 0.70, 0, 1) * 1.6)):
        pierre = pierre * (1 - part[..., None]) + np.array(teinte, float) * part[..., None]
    pierre *= (0.70 + 0.36 * bombe + 0.14 * (grain - 0.5))[..., None]
    mortier = np.array((104, 94, 80), float) * (0.85 + 0.3 * grain[..., None])
    k = np.clip(bombe * 4.5, 0, 1)[..., None]
    _ecrire(chemin, mortier * (1 - k) + pierre * k, bombe + 0.08 * grain, 5.0)


def peindre_toile(chemin, taille=256, graine=6):
    """Une toile de sac : une trame claire, à teinter par la couleur de sommet."""
    rng = np.random.default_rng(graine)
    y, x = np.mgrid[0:taille, 0:taille]
    trame = 0.5 + 0.25 * np.sin(x * TAU / 8) + 0.25 * np.sin(y * TAU / 8)
    h = np.clip(0.35 + 0.5 * trame + 0.3 * (_bruit(taille, 10, 10, rng) - 0.5), 0, 1)
    _ecrire(chemin, _degrade(h, (176, 160, 130), (244, 234, 208)), trame, 2.0)


def peindre_champignon(chemin, taille=256, graine=7):
    """Le chapeau vu de dessus (rouge à pois blancs), le pied et les lames (crème) dans le coin."""
    rng = np.random.default_rng(graine)
    img = Image.new("RGB", (taille, taille), (238, 228, 204))
    d = ImageDraw.Draw(img)
    c = taille / 2
    for k in range(40, 0, -1):
        r = c * 0.97 * k / 40
        d.ellipse((c - r, c - r, c + r, c + r), fill=tuple(int(a + (b - a) * (k / 40) ** 2) for a, b in zip((236, 70, 50), (190, 28, 30))))
    for _ in range(26):
        a, e = rng.uniform(0, TAU), math.sqrt(rng.uniform(0.02, 0.8)) * c * 0.9
        r = rng.uniform(0.025, 0.06) * taille
        d.ellipse((c + math.cos(a) * e - r, c + math.sin(a) * e - r, c + math.cos(a) * e + r, c + math.sin(a) * e + r), fill=(255, 250, 240))
    d.rectangle((0, 0, taille * 0.12, taille * 0.12), fill=(238, 228, 204))
    img.save(chemin, optimize=True)


TEXTURES = {"bois": peindre_bois, "bois_peint": lambda chemin: peindre_bois(chemin, graine=11, peint=True), "ecorce": peindre_ecorce,
            "coupe": peindre_coupe, "paille": peindre_paille, "pierre": peindre_pierre, "toile": peindre_toile, "champignon": peindre_champignon}
CREME = (0.02, 0.02)          # dans champignon.png, le coin crème : le pied et les lames y prennent leur couleur


# ---------------------------------------------------------------- les objets

def tronc_couche(graine=1):
    m = Maillage(graine)
    chemin = [(-1.6 + 3.2 * t, 0.10 * math.sin(2.4 * t), 0.27 + 0.03 * math.sin(3 * t)) for t in np.linspace(0, 1, 7)]
    m.tube("ecorce", chemin, [0.33 - 0.07 * t for t in np.linspace(0, 1, 7)], 12, ("coupe", "coupe"), tours=2, motif=1.2)
    m.tube("ecorce", [(0.5, 0.0, 0.50), (0.62, 0.10, 0.78), (0.70, 0.16, 0.92)], [0.085, 0.07, 0.06], 7, (None, "coupe"), motif=1.2)      # un chicot
    m.tube("ecorce", [(-0.7, -0.05, 0.50), (-0.80, -0.30, 0.66)], [0.07, 0.055], 7, (None, "coupe"), motif=1.2)
    return m


def souche(graine=2):
    m = Maillage(graine)
    chemin = [(0, 0, -0.12), (0, 0, 0.10), (0.01, 0, 0.32), (0.02, 0.01, 0.56)]
    m.tube("ecorce", chemin, [0.50, 0.44, 0.40, 0.39], 16, (None, "coupe"), tours=3, motif=1.0, bosses=0.42)
    for cap in (0.6, 2.4, 4.3):                                                    # trois racines qui courent au sol
        d = np.array([math.cos(cap), math.sin(cap), 0.0])
        m.tube("ecorce", [d * 0.38 + [0, 0, 0.16], d * 0.72 + [0, 0, 0.05], d * 1.02 + [0, 0, -0.06]], [0.14, 0.09, 0.04], 7, motif=1.0)
    return m


def champignons(graine=3):
    m = Maillage(graine)
    for x, y, haut, r in ((0.0, 0.0, 0.34, 0.20), (0.26, 0.10, 0.20, 0.12), (-0.20, 0.16, 0.24, 0.14), (0.08, -0.24, 0.14, 0.09)):
        part = m.parts.setdefault("champignon", {"pos": [], "nor": [], "uv": [], "col": [], "tri": []})
        debut = len(part["uv"])
        m.tube("champignon", [(x, y, -0.02), (x + 0.01, y, haut * 0.6), (x + 0.015, y, haut)], [r * 0.34, r * 0.24, r * 0.22], 9)
        m.tour("champignon", [(r * 0.25, haut - 0.005), (r * 0.98, haut + r * 0.02)], 14, (x + 0.015, y, 0))                     # les lames
        part["uv"][debut:] = [CREME] * (len(part["uv"]) - debut)
        profil = [(r * math.cos(a), haut + r * 0.02 + r * 0.72 * math.sin(a)) for a in np.linspace(0, math.pi / 2, 6)]
        m.tour("champignon", profil, 14, (x + 0.015, y, 0), rayonnant=True)
    return m


def cloture(graine=4):
    """Un tronçon de 2 m : un poteau à l'origine, trois lisses qui partent vers +X. Les tronçons se mettent bout à bout."""
    m = Maillage(graine)
    m.tube("bois", [(0, 0, -0.15), (0.01, 0, 0.6), (0, 0.005, 1.18)], [0.075, 0.07, 0.062], 7, (None, "coupe"), motif=0.8)
    for z, penche in ((0.34, 1.0), (0.66, -1.2), (0.98, 0.6)):
        m.boite("bois", (1.0, 0.075, z), (2.06, 0.035, 0.105), tourne(penche * 2, penche * 0.5, 0), motif=0.9)
    return m


def barriere(graine=5):
    """Une barrière de pré de 2 m entre ses deux poteaux, peinte en blanc."""
    m = Maillage(graine)
    blanc = (0.96, 0.95, 0.90)
    for x in (0.0, 2.0):
        m.tube("bois", [(x, 0, -0.15), (x, 0, 1.38)], [0.09, 0.08], 8, (None, "coupe"), motif=0.8)
    for z in (0.30, 0.62, 0.94, 1.20):
        m.boite("bois_peint", (1.0, 0.0, z), (1.78, 0.04, 0.10), teinte=blanc)
    for x in (0.14, 1.86):
        m.boite("bois_peint", (x, 0.0, 0.75), (0.10, 0.045, 1.02), teinte=blanc)
    m.boite("bois_peint", (1.0, 0.02, 0.75), (1.95, 0.035, 0.09), tourne(0, -27.5, 0), blanc)       # l'écharpe en travers
    return m


def meule(graine=6):
    m = Maillage(graine)
    profil = [(1.20, -0.05), (1.38, 0.45), (1.36, 1.0), (1.10, 1.6), (0.62, 2.15), (0.18, 2.48), (0.0, 2.55)]
    m.tour("paille", profil, 20, tours=5, motif=1.2)
    m.tube("bois", [(0, 0, 2.3), (0.03, 0.02, 3.0)], [0.045, 0.035], 6, (None, "coupe"))
    return m


def panneau(graine=7):
    """Un poteau de carrefour et trois flèches de bois peint, sans texte : chacune montre un chemin."""
    m = Maillage(graine)
    m.tube("bois", [(0, 0, -0.2), (0.01, 0, 1.2), (0, 0, 2.45)], [0.075, 0.068, 0.058], 8, (None, "coupe"), motif=0.8)
    for z, cap, teinte in ((2.12, 20, (0.96, 0.92, 0.80)), (1.82, 150, (0.72, 0.84, 0.92)), (1.52, -95, (0.96, 0.80, 0.62))):
        rot = tourne(0, 0, cap)
        m.boite("bois_peint", rot @ np.array([0.42, 0.075, 0]) + [0, 0, z], (0.72, 0.03, 0.19), rot, teinte)
        pointe = [rot @ np.array(q) + [0, 0, z] for q in ((0.78, 0.06, -0.095), (0.96, 0.06, 0.0), (0.78, 0.06, 0.095), (0.78, 0.06, 0.0))]
        m.plaque("bois_peint", [pointe[0], pointe[1], pointe[2], pointe[3]], teinte, deux_faces=True)
    return m


def puits(graine=8):
    m = Maillage(graine)
    m.tour("pierre", [(0.82, -0.1), (0.80, 0.85)], 18, tours=5, motif=1.0)                                  # la margelle, dehors
    m.tour("pierre", [(0.80, 0.85), (0.58, 0.85)], 18, tours=5, motif=1.0)                                  # son dessus
    m.tour("pierre", [(0.58, 0.85), (0.58, 0.15), (0.0, 0.15)], 18, tours=4, motif=1.0, teinte=(0.25, 0.30, 0.36))      # le fond, dans le noir
    for x in (-0.72, 0.72):
        m.boite("bois", (x, 0, 1.45), (0.11, 0.11, 1.5))
    m.tube("bois", [(-0.80, 0, 1.62), (0.80, 0, 1.62)], [0.07, 0.07], 8, ("coupe", "coupe"))               # le treuil
    m.tube("bois", [(0.80, 0, 1.62), (0.98, 0, 1.62), (0.98, 0.0, 1.40)], [0.025, 0.025, 0.025], 6)        # sa manivelle
    m.tube("toile", [(0.1, 0, 1.56), (0.1, 0, 1.12)], [0.012, 0.012], 5)                                   # la corde
    m.tour("bois", [(0.12, 0.90), (0.15, 1.12)], 10, (0.1, 0, 0), tours=2)                                 # le seau
    for cote in (-1, 1):                                                                                    # le petit toit de bardeaux
        rot = tourne(-cote * 38, 0, 0)                                                                     # le bord extérieur descend : un chapeau, pas un V
        m.boite("bois", (0, cote * 0.38, 2.30), (1.95, 1.02, 0.045), rot, (0.80, 0.70, 0.62), 0.5)
    m.boite("bois", (0, 0, 2.62), (2.0, 0.07, 0.07))
    return m


def ruche(graine=9):
    m = Maillage(graine)
    for x in (-0.22, 0.22):
        for y in (-0.18, 0.18):
            m.boite("bois", (x, y, 0.15), (0.07, 0.07, 0.34))
    m.boite("bois", (0, 0, 0.33), (0.60, 0.50, 0.04))
    for i, teinte in enumerate(((0.98, 0.88, 0.52), (0.62, 0.82, 0.92), (0.98, 0.96, 0.90))):               # trois hausses peintes
        m.boite("bois_peint", (0, 0, 0.35 + 0.13 + i * 0.26), (0.52, 0.44, 0.255), teinte=teinte)
    m.boite("bois", (0, -0.225, 0.375), (0.26, 0.012, 0.025), teinte=(0.12, 0.10, 0.08))                    # le trou de vol
    m.boite("bois", (0, -0.27, 0.355), (0.40, 0.10, 0.015))                                                  # la planche d'envol
    m.boite("bois_peint", (0, 0, 1.17), (0.60, 0.52, 0.09), teinte=(0.80, 0.82, 0.84))                       # le toit plat
    return m


def epouvantail(graine=10):
    m = Maillage(graine)
    m.tube("bois", [(0, 0, -0.2), (0.02, 0, 1.0), (0, 0, 2.02)], [0.05, 0.045, 0.04], 7)
    m.tube("bois", [(-0.82, 0, 1.52), (0, 0.01, 1.56), (0.82, 0, 1.50)], [0.035, 0.04, 0.035], 6)
    chemise = (0.82, 0.36, 0.30)
    m.tour("toile", [(0.30, 0.82), (0.26, 1.20), (0.20, 1.56), (0.10, 1.64)], 10, teinte=chemise, tours=3, motif=0.4)       # la chemise
    for cote in (-1, 1):
        m.tube("toile", [(cote * 0.16, 0, 1.56), (cote * 0.50, 0, 1.53), (cote * 0.74, 0, 1.47)], [0.10, 0.09, 0.085], 8, teinte=chemise, motif=0.4)
        m.tour("paille", [(0.0, 0.0), (0.09, 0.02), (0.05, 0.20)], 7, (cote * 0.84, 0, 1.36), tours=1, motif=0.3)                   # la paille des mains
    m.tour("paille", [(0.34, 0.60), (0.30, 0.84)], 10, tours=2, motif=0.4)                                                           # la paille sous la chemise
    profil = [(0.19 * math.sin(a), 1.84 - 0.19 * math.cos(a)) for a in np.linspace(0.15, math.pi, 7)]
    m.tour("toile", profil, 12, tours=2, motif=0.4)                                                                                  # la tête en sac
    m.tour("paille", [(0.36, 1.97), (0.20, 1.99), (0.17, 2.10), (0.0, 2.24)], 12, tours=3, motif=0.3)                                # le chapeau
    m.tour("paille", [(0.20, 1.985), (0.36, 1.965)], 12, tours=3, motif=0.3)
    for cote in (-1, 1):                                                                                                             # les yeux : deux boutons
        m.tour("bois", [(0.0, 0.0), (0.035, 0.0)], 8, (cote * 0.07, -0.185, 1.86), teinte=(0.10, 0.08, 0.08))
    return m


def pont(graine=11):
    """Un petit pont de bois en dos d'âne : 4 m de long (le long de X), 1,6 m de large."""
    m = Maillage(graine)

    def dos(x):
        return 0.38 * (1 - (x / 2.0) ** 2) + 0.12

    for cote in (-0.62, 0.62):                                                    # les deux longerons
        m.tube("bois", [(x, cote, dos(x) - 0.12) for x in np.linspace(-2.05, 2.05, 7)], [0.085] * 7, 6, ("coupe", "coupe"), motif=0.9)
    for i in range(11):                                                           # le tablier
        x = -1.82 + i * 0.364
        pente = math.degrees(math.atan(-0.38 * 2 * x / 4.0))
        m.boite("bois", (x, 0, dos(x) + 0.015), (0.34, 1.62, 0.05), tourne(0, -pente, 0), (0.95, 0.92, 0.88), 0.9)
    for cote in (-0.76, 0.76):                                                    # les garde-corps
        for x in (-1.7, -0.57, 0.57, 1.7):
            m.boite("bois", (x, cote, dos(x) + 0.42), (0.085, 0.085, 0.95))
        m.tube("bois", [(x, cote, dos(x) + 0.92) for x in np.linspace(-1.9, 1.9, 7)], [0.05] * 7, 6, ("coupe", "coupe"), motif=0.9)
        m.tube("bois", [(x, cote, dos(x) + 0.50) for x in np.linspace(-1.8, 1.8, 7)], [0.035] * 7, 5, motif=0.9)
    return m


def banc(graine=12):
    m = Maillage(graine)
    for x in (-0.62, 0.62):
        m.boite("bois", (x, 0.14, 0.22), (0.09, 0.09, 0.46))
        m.boite("bois", (x, -0.14, 0.45), (0.09, 0.09, 0.92), tourne(-8, 0, 0))
        m.boite("bois", (x, 0.0, 0.40), (0.07, 0.42, 0.07))
    for y in (0.16, 0.04, -0.08):
        m.boite("bois", (0, y, 0.46), (1.50, 0.105, 0.035), teinte=(0.96, 0.92, 0.86))
    for z in (0.66, 0.82):
        m.boite("bois", (0, -0.20, z), (1.50, 0.03, 0.12), tourne(-8, 0, 0), (0.96, 0.92, 0.86))
    return m


def charrette(graine=13):
    """Une charrette à bras, à l'arrêt : sa caisse, ses deux roues, ses brancards posés au sol vers -Y."""
    m = Maillage(graine)
    vert = (0.46, 0.66, 0.50)
    penche = tourne(-9, 0, 0)

    def pose(q):
        return penche @ np.asarray(q, float) + [0, 0, 0.62]

    for i in range(5):                                                            # le plancher
        m.boite("bois", pose((-0.44 + i * 0.22, 0.0, 0.0)), (0.21, 1.9, 0.04), penche)
    for x in (-0.57, 0.57):                                                       # les ridelles peintes
        for z in (0.16, 0.36):
            m.boite("bois_peint", pose((x, 0.0, z)), (0.035, 1.9, 0.14), penche, vert)
        for y in (-0.85, 0.0, 0.85):
            m.boite("bois", pose((x, y, 0.22)), (0.06, 0.06, 0.50), penche)
    m.boite("bois_peint", pose((0, 0.95, 0.25)), (1.14, 0.035, 0.46), penche, vert)
    for x in (-0.50, 0.50):                                                       # les brancards
        m.tube("bois", [pose((x, 0.9, -0.05)), pose((x, -1.0, -0.05)), pose((x * 0.9, -2.3, -0.05))], [0.04, 0.04, 0.03], 6, ("coupe", "coupe"))
    m.boite("bois", (0, 0.72, 0.32), (0.07, 0.07, 0.66))                          # la béquille
    m.tube("bois", [(-0.78, 0.12, 0.52), (0.78, 0.12, 0.52)], [0.045, 0.045], 8, ("coupe", "coupe"))                       # l'essieu
    for x in (-0.72, 0.72):                                                       # les roues
        jante = [(x, 0.12 + 0.50 * math.cos(a), 0.52 + 0.50 * math.sin(a)) for a in np.linspace(0, TAU, 19)]
        m.tube("bois", jante, [0.045] * 19, 6, motif=0.6)
        m.tube("bois", [(x - 0.07, 0.12, 0.52), (x + 0.07, 0.12, 0.52)], [0.09, 0.09], 10, ("coupe", "coupe"))
        for k in range(8):
            a = TAU * k / 8
            m.boite("bois", (x, 0.12 + 0.27 * math.cos(a), 0.52 + 0.27 * math.sin(a)), (0.035, 0.42, 0.045), tourne(math.degrees(a), 0, 0))
    return m


FABRIQUES = {"banc": banc, "charrette": charrette, "tronc_couche": tronc_couche, "souche": souche, "champignons": champignons, "cloture": cloture, "barriere": barriere,
             "meule": meule, "panneau": panneau, "puits": puits, "ruche": ruche, "epouvantail": epouvantail, "pont": pont}


# ---------------------------------------------------------------- l'aperçu de contrôle (un dessin, pas une photo)

def dessiner(chemin, scenes, depuis, vers, taille=(3200, 1800), ouverture=38.0, dossiers=None, en_plus=None, vent=()):
    """Trace les objets vus d'un point, avec leurs textures, leur lumière peinte et un soleil : assez pour juger
    les formes, les tailles et les raccords de texture. scenes : [(maillage, (x, y), cap en degrés), ...]."""
    large, haut = taille
    depuis, vers = np.asarray(depuis, float), np.asarray(vers, float)
    avant = (vers - depuis) / np.linalg.norm(vers - depuis)
    droite = np.cross(avant, HAUT)
    droite /= np.linalg.norm(droite)
    dessus = np.cross(droite, avant)
    focale = 0.5 * large / math.tan(math.radians(ouverture) / 2)
    soleil = np.array([0.45, -0.55, 0.70])
    soleil /= np.linalg.norm(soleil)
    ciel = np.linspace(0, 1, haut)[:, None, None]
    image = np.repeat((np.array((150, 196, 236), float) * (1 - ciel) + np.array((214, 232, 244), float) * ciel), large, axis=1)
    fond = np.full((haut, large), np.inf)
    textures = {}
    for dossier in ([OBJETS] if dossiers is None else dossiers):
        for fichier in os.listdir(dossier):
            if fichier.endswith(".png"):
                textures[fichier[:-4]] = np.asarray(Image.open(os.path.join(dossier, fichier)).convert("RGBA"), float)
    sol = Maillage()
    for gx in range(-30, 30, 4):
        for gy in range(-16, 44, 4):
            sol.plaque("sol", [(gx, gy, 0), (gx + 4, gy, 0), (gx + 4, gy + 4, 0), (gx, gy + 4, 0)], (0.36, 0.60, 0.26))
    textures["sol"] = np.full((2, 2, 4), 255.0)
    for nom_, fichier in (en_plus or {}).items():
        textures[nom_] = np.asarray(Image.open(fichier).convert("RGBA"), float)
    for m, place, cap in [(sol, (0, 0), 0)] + list(scenes):
        rot = tourne(0, 0, cap)
        for matiere, p in m.parts.items():
            pos = np.array(p["pos"]) @ rot.T + [place[0], place[1], 0.0]
            nor = np.array(p["nor"]) @ rot.T
            uv, col = np.array(p["uv"]), np.array(p["col"])
            if any(m is a for a in vent):                           # un arbre : sa couleur de sommet est du vent, pas une teinte
                col = np.ones_like(col)
            rel = pos - depuis
            cam = np.stack([rel @ droite, rel @ dessus, rel @ avant], axis=1)
            tex = textures[matiere]
            th, tw = tex.shape[:2]
            eclat = 0.42 + 0.62 * np.clip(nor @ soleil, 0, 1)
            for a, b, c in p["tri"]:
                z = cam[[a, b, c], 2]
                if z.min() < 0.2:
                    continue
                sx = large / 2 + focale * cam[[a, b, c], 0] / z
                sy = haut / 2 - focale * cam[[a, b, c], 1] / z
                x0, x1 = max(int(sx.min()), 0), min(int(sx.max()) + 1, large - 1)
                y0, y1 = max(int(sy.min()), 0), min(int(sy.max()) + 1, haut - 1)
                if x0 > x1 or y0 > y1:
                    continue
                aire = (sx[1] - sx[0]) * (sy[2] - sy[0]) - (sx[2] - sx[0]) * (sy[1] - sy[0])
                if abs(aire) < 1e-9:
                    continue
                gy, gx = np.mgrid[y0:y1 + 1, x0:x1 + 1] + 0.5
                w0 = ((sx[1] - gx) * (sy[2] - gy) - (sx[2] - gx) * (sy[1] - gy)) / aire
                w1 = ((sx[2] - gx) * (sy[0] - gy) - (sx[0] - gx) * (sy[2] - gy)) / aire
                w2 = 1 - w0 - w1
                dedans = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
                if not dedans.any():
                    continue
                iz = w0 / z[0] + w1 / z[1] + w2 / z[2]                    # l'inverse de la profondeur : tout se mélange avec lui
                prof = 1.0 / np.maximum(iz, 1e-9)
                devant = dedans & (prof < fond[y0:y1 + 1, x0:x1 + 1])
                if not devant.any():
                    continue
                poids = [w0 / z[0] * prof, w1 / z[1] * prof, w2 / z[2] * prof]
                u = sum(k * uv[i][0] for k, i in zip(poids, (a, b, c)))
                v = sum(k * uv[i][1] for k, i in zip(poids, (a, b, c)))
                teinte = sum(k[..., None] * col[i] for k, i in zip(poids, (a, b, c)))
                lum = sum(k * eclat[i] for k, i in zip(poids, (a, b, c)))
                u, v = np.nan_to_num(u), np.nan_to_num(v)
                texel = tex[(np.floor(v * th).astype(int)) % th, (np.floor(u * tw).astype(int)) % tw]
                devant &= texel[..., 3] > 127                       # une feuille découpée : on voit à travers ses trous
                zone = image[y0:y1 + 1, x0:x1 + 1]
                zone[devant] = (texel[..., :3] * teinte * lum[..., None])[devant]
                fond[y0:y1 + 1, x0:x1 + 1][devant] = prof[devant]
    os.makedirs(APERCUS, exist_ok=True)
    Image.fromarray(np.clip(image, 0, 255).astype(np.uint8), "RGB").resize((large // 2, haut // 2), Image.LANCZOS).save(chemin)
    print("[dessin]", chemin, flush=True)


def jalon():
    """Un piquet rouge et blanc d'un mètre, pour l'échelle."""
    m = Maillage()
    for i in range(5):
        m.tube("bois_peint", [(0, 0, 0.2 * i), (0, 0, 0.2 * (i + 1))], [0.025, 0.025], 6, teinte=(0.9, 0.15, 0.12) if i % 2 == 0 else (1, 1, 1))
    return m


if __name__ == "__main__":
    os.makedirs(OBJETS, exist_ok=True)
    for nom, peindre in TEXTURES.items():
        peindre(os.path.join(OBJETS, nom + ".png"))
    choisis = [n for n in sys.argv[1:] if n in FABRIQUES] or list(FABRIQUES)
    faits = {}
    for nom in choisis:
        faits[nom] = FABRIQUES[nom]()
        faits[nom].peindre_lumiere()
        ecrire_glb(os.path.join(OBJETS, nom + ".glb"), faits[nom], nom)
    places = {"epouvantail": ((-6.6, 6.0), 12), "meule": ((-3.0, 6.6), 0), "puits": ((1.2, 6.0), 25), "charrette": ((5.2, 6.4), -35),
              "cloture": ((-7.2, 2.6), 0), "barriere": ((-5.2, 2.6), 0), "panneau": ((-1.6, 2.2), 0), "banc": ((0.8, 2.4), 10),
              "ruche": ((3.2, 2.4), -20), "pont": ((6.2, 1.0), 12), "tronc_couche": ((-4.6, -1.4), 14), "souche": ((-1.2, -1.6), 0),
              "champignons": ((0.6, -2.0), 0)}
    scenes = [(faits[n], places[n][0], places[n][1]) for n in choisis] + [(jalon(), (2.0, -1.8), 0)]
    dessiner(os.path.join(APERCUS, "objets.png"), scenes, (0.0, -15.0, 6.0), (0.0, 2.6, 0.7), ouverture=50.0)
    dessiner(os.path.join(APERCUS, "objets-pres.png"), scenes, (1.6, -3.4, 3.4), (1.4, 5.2, 1.0), ouverture=58.0)
