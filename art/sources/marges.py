"""Remplir les marges des textures cuites d'un animal : autour de chaque îlot du dépliage, la couleur de l'îlot s'étend
dans le fond, sur une bonne largeur, puis tout le reste du fond prend la couleur moyenne.

Pourquoi : entre deux îlots, le fond était crème (couleur), noir (zones : pas de poil). Vu de loin, le jeu lit une
image plus petite (mipmap) où ce fond se mélange au bord des îlots : le long de chaque couture du dépliage apparaissait
une ligne claire en pointillé, et le poil s'y arrêtait. Signalé par la session principale le 14 octobre 2026 sur le
renard teint (le flanc et la queue). Sans Blender : on lit les UV du .glb, on peint un masque des îlots, on étend.

    python marges.py renard             corrige les textures de art/modeles/renard/
    python marges.py tous               tous les animaux fabriqués
L'usine le fait d'elle-même après chaque fabrication.
"""
import json
import os
import struct
import sys

import numpy as np
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
MODELES = os.path.normpath(os.path.join(ICI, "..", "modeles"))
TEXTURES = ("couleur", "orm", "zones", "relief", "brut")
LARGE = 24                                                           # la marge, en pixels, peinte par extension pas à pas


def uv_du_glb(chemin):
    """Les triangles du dépliage (en UV du .glb : u vers la droite, v vers le bas de l'image), tous maillages confondus."""
    with open(chemin, "rb") as f:
        donnees = f.read()
    long_json = struct.unpack_from("<I", donnees, 12)[0]
    doc = json.loads(donnees[20:20 + long_json])
    binaire = donnees[20 + long_json + 8:]

    def tableau(i):
        acc = doc["accessors"][i]
        vue = doc["bufferViews"][acc["bufferView"]]
        genre = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}[acc["componentType"]]
        large = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[acc["type"]]
        debut = vue.get("byteOffset", 0) + acc.get("byteOffset", 0)
        pas = vue.get("byteStride", 0)
        taille = np.dtype(genre).itemsize * large
        if pas and pas != taille:
            brut = np.frombuffer(binaire, np.uint8, pas * acc["count"], debut).reshape(acc["count"], pas)[:, :taille]
            return np.frombuffer(brut.tobytes(), genre).reshape(acc["count"], large)
        return np.frombuffer(binaire, genre, acc["count"] * large, debut).reshape(acc["count"], large)

    triangles = []
    for mesh in doc["meshes"]:
        for prim in mesh["primitives"]:
            if "TEXCOORD_0" not in prim["attributes"] or "indices" not in prim:
                continue
            uv = tableau(prim["attributes"]["TEXCOORD_0"]).astype(np.float64)
            idx = tableau(prim["indices"]).reshape(-1, 3).astype(np.int64)
            triangles.append(uv[idx])
    return np.concatenate(triangles) if triangles else np.zeros((0, 3, 2))


def masque(triangles, taille):
    """Les pixels couverts par les îlots du dépliage."""
    m = np.zeros((taille, taille), bool)
    for tri in triangles * taille:
        x0, x1 = int(max(0, np.floor(tri[:, 0].min()) - 1)), int(min(taille - 1, np.ceil(tri[:, 0].max()) + 1))
        y0, y1 = int(max(0, np.floor(tri[:, 1].min()) - 1)), int(min(taille - 1, np.ceil(tri[:, 1].max()) + 1))
        if x1 < x0 or y1 < y0:
            continue
        gy, gx = np.mgrid[y0:y1 + 1, x0:x1 + 1] + 0.5
        (ax, ay), (bx, by), (cx, cy) = tri
        aire = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
        if abs(aire) < 1e-12:
            continue
        w0 = ((bx - gx) * (cy - gy) - (cx - gx) * (by - gy)) / aire
        w1 = ((cx - gx) * (ay - gy) - (ax - gx) * (cy - gy)) / aire
        w2 = 1 - w0 - w1
        m[y0:y1 + 1, x0:x1 + 1] |= (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
    return m


def etendre(image, dedans, large=LARGE):
    """Étend les couleurs des îlots dans le fond, pixel par pixel, sur « large » pixels ; le reste prend la moyenne."""
    valeurs = image.astype(np.float32)
    connu = dedans.copy()
    for _ in range(large):
        somme = np.zeros_like(valeurs)
        poids = np.zeros(connu.shape, np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            c = np.roll(np.roll(connu, dy, 0), dx, 1)
            somme += np.roll(np.roll(valeurs * connu[..., None], dy, 0), dx, 1)
            poids += c
        neuf = (~connu) & (poids > 0)
        if not neuf.any():
            break
        valeurs[neuf] = somme[neuf] / poids[neuf][:, None]
        connu |= neuf
    if (~connu).any():
        valeurs[~connu] = valeurs[dedans].mean(axis=0)
    return np.clip(valeurs + 0.5, 0, 255).astype(np.uint8)


def corriger(animal):
    dossier = os.path.join(MODELES, animal)
    glb = os.path.join(dossier, animal + ".glb")
    if not os.path.exists(glb):
        print("[marges] pas de modèle :", animal)
        return
    triangles = uv_du_glb(glb)
    faits, masques = [], {}
    for nom in TEXTURES:
        chemin = os.path.join(dossier, "%s_%s.png" % (animal, nom))
        if not os.path.exists(chemin):
            continue
        img = Image.open(chemin)
        mode = img.mode
        tab = np.asarray(img.convert("RGB"))
        taille = tab.shape[0]
        if taille not in masques:
            masques[taille] = masque(triangles, taille)
        Image.fromarray(etendre(tab, masques[taille]), "RGB").convert(mode if mode in ("RGB", "RGBA") else "RGB").save(chemin, optimize=True)
        faits.append(nom)
    print("[marges]", animal, ":", ", ".join(faits), "(%d triangles)" % len(triangles), flush=True)


if __name__ == "__main__":
    import machine
    noms = sys.argv[1:]
    if noms == ["tous"]:
        noms = sorted(n for n in os.listdir(MODELES) if os.path.exists(os.path.join(MODELES, n, n + ".glb")))
    for nom in noms:
        with machine.tour("les marges de « %s »" % nom, 300):
            corriger(nom)
