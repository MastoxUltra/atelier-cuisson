"""La robe sauvage : un animal qui a PERDU ses couleurs. On la tire des textures déjà cuites de l'animal.

    python brut.py lapin canard escargot        écrit art/modeles/<animal>/<animal>_brut.png (la robe choisie)
    python brut.py essais lapin                 écrit les trois essais _brut_a.png, _b.png, _c.png et un dessin de contrôle

ARTHUR A CHOISI LA ROBE C, « cendre », le 13 octobre 2026 (sur les photos prises dans le jeu, avec le poil).
L'usine écrit cette robe toute seule à la fin de chaque fabrication.

SANS BLENDER : de la peinture en deux dimensions (numpy), quelques secondes par animal.

Les trois propositions qu'il a vues :
    a  « délavée »     une toile de lin écrue, passée au soleil ; l'ancienne couleur n'a survécu qu'au creux des plis
    b  « toile de sac » un jute brun et rêche, rapiécé de bouts de sac gris, sali dans les creux, plus rien de la couleur
    c  « cendre »       un gris pâle et froid, comme vidé ; on devine l'ancien motif, mais sans aucune teinte

Ce que le jeu en fait : peluche.gdshader et poil.gdshader prennent cette image dans « brut » (avec a_brut = 1) à la place
de leur toile unie, partout où la teinture n'est pas montée.
"""
import json
import math
import os
import struct
import sys

import numpy as np
from PIL import Image

import objets as O

MODELES = os.path.normpath(os.path.join(O.ICI, "..", "modeles"))
APERCUS = os.path.normpath(os.path.join(O.ICI, "..", "apercus"))
ROBES = {  # la toile, le rapiéçage, le fil, la part d'ancienne couleur (à plat, dans les plis), la salissure des plis, la trame (force, pas en pixels)
    "a": dict(toile=(232, 216, 184), piece=(214, 196, 164), fil=(150, 118, 86), reste=(0.10, 0.42), sale=0.16, trame=(0.05, 11), froid=0.0),
    "b": dict(toile=(190, 162, 120), piece=(160, 152, 138), fil=(88, 66, 48), reste=(0.03, 0.06), sale=0.36, trame=(0.13, 16), froid=0.0),
    "c": dict(toile=(210, 208, 204), piece=(184, 184, 190), fil=(82, 82, 90), reste=(0.0, 0.0), sale=0.26, trame=(0.05, 11), froid=1.0),
}


CHOISIE = "c"


def robe(animal, lettre=None):
    """Fabrique la robe sauvage d'un animal à partir de sa couleur, de ses zones et de son ombre de contact.
    Sans lettre : la robe choisie, dans <animal>_brut.png. Avec une lettre : un essai, dans <animal>_brut_<lettre>.png."""
    r = ROBES[lettre or CHOISIE]
    dossier = os.path.join(MODELES, animal)
    couleur = np.asarray(Image.open(os.path.join(dossier, animal + "_couleur.png")).convert("RGB"), np.float32) / 255
    taille = couleur.shape[0]
    zones = np.asarray(Image.open(os.path.join(dossier, animal + "_zones.png")).convert("RGB").resize((taille, taille)), np.float32) / 255
    orm = np.asarray(Image.open(os.path.join(dossier, animal + "_orm.png")).convert("RGB").resize((taille, taille)), np.float32) / 255
    ombre, rugueux = orm[..., 0], orm[..., 1]
    rng = np.random.default_rng(7)
    clair = couleur @ np.array([0.299, 0.587, 0.114], np.float32)
    pli = np.clip((0.86 - ombre) / 0.5, 0, 1)                                  # 1 au creux d'un pli, d'une couture
    cousu = zones.max(axis=2) < 0.12                                           # les fils et les boutons (ni poil, ni pièce, ni feutrine)
    bouton = cousu & (clair < 0.22)                                            # un bouton, une bille de verre, un œil de feutrine
    fil = cousu & ~bouton
    piece = zones[..., 1] > 0.5
    # la toile : elle garde le clair et le foncé de l'ancien dessin, pas sa couleur
    toile = np.where(piece[..., None], np.array(r["piece"], np.float32), np.array(r["toile"], np.float32)) / 255 * (0.80 + 0.24 * clair)[..., None]
    reste = (r["reste"][0] + (r["reste"][1] - r["reste"][0]) * pli)[..., None]  # la couleur n'a survécu qu'au creux des plis
    c = toile * (1 - reste) + couleur * reste
    taches = np.clip(O._bruit(taille, 7, 7, rng) - 0.45, 0, 1) * 0.5           # des auréoles, larges et douces
    c *= (1 - r["sale"] * pli - 0.5 * r["sale"] * taches)[..., None]
    if r["froid"]:
        c *= (1 - 0.10 * pli[..., None] * np.array([1.0, 0.6, 0.0], np.float32))            # l'ombre tire sur le bleu
    force, pas = r["trame"]
    y, x = np.mgrid[0:taille, 0:taille].astype(np.float32)
    trame = 0.5 * np.sin(x * math.tau / pas) * np.sin(y * math.tau / pas) + 0.5 * (rng.uniform(0, 1, (taille, taille)).astype(np.float32) - 0.5)
    c *= (1 + force * trame)[..., None]
    c = np.where(fil[..., None], np.array(r["fil"], np.float32) / 255 * (0.75 + 0.5 * clair)[..., None], c)                 # le fil, brut lui aussi
    c = np.where(bouton[..., None], couleur * 0.35 + np.array((62, 60, 56), np.float32) / 255 * 0.65 * (0.6 + 1.6 * clair)[..., None], c)   # les boutons ternis
    # la tête de verre d'une épingle (lisse et de couleur vive) : la seule couleur qui reste à un Épinglé
    perle = cousu & (rugueux < 0.35) & ((couleur.max(axis=2) - couleur.min(axis=2)) > 0.35)
    c = np.where(perle[..., None], couleur, c)
    chemin = os.path.join(dossier, "%s_brut%s.png" % (animal, "_" + lettre if lettre else ""))
    Image.fromarray(np.clip(c * 255, 0, 255).astype(np.uint8), "RGB").save(chemin, optimize=True)
    print("[robe]", os.path.basename(chemin), round(os.path.getsize(chemin) / 1e6, 1), "Mo", flush=True)
    return chemin


# ---------------------------------------------------------------- lire un modèle du jeu, pour le dessin de contrôle

def lire_glb(chemin, matiere):
    """Le maillage d'un .glb du jeu, tel qu'il est au repos, les paupières retirées (elles sont fermées au repos)."""
    with open(chemin, "rb") as f:
        donnees = f.read()
    long_json = struct.unpack_from("<I", donnees, 12)[0]
    doc = json.loads(donnees[20:20 + long_json])
    binaire = donnees[20 + long_json + 8:]

    def tableau(i):
        acc = doc["accessors"][i]
        vue = doc["bufferViews"][acc["bufferView"]]
        genre = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}[acc["componentType"]]
        large = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[acc["type"]]
        debut = vue.get("byteOffset", 0) + acc.get("byteOffset", 0)
        pas = vue.get("byteStride", 0)
        if pas and pas != np.dtype(genre).itemsize * large:
            brut = np.frombuffer(binaire, np.uint8, pas * acc["count"], debut).reshape(acc["count"], pas)[:, :np.dtype(genre).itemsize * large]
            t = np.frombuffer(brut.tobytes(), genre).reshape(acc["count"], large)
        else:
            t = np.frombuffer(binaire, genre, acc["count"] * large, debut).reshape(acc["count"], large)
        if acc.get("normalized"):
            t = t.astype(np.float32) / np.iinfo(genre).max
        return t

    m = O.Maillage()
    part = m.parts.setdefault(matiere, {"pos": [], "nor": [], "uv": [], "col": [], "tri": []})
    os_ = [doc["nodes"][j].get("name", "") for j in doc["skins"][0]["joints"]] if doc.get("skins") else []
    for maille in doc["meshes"]:
        for prim in maille["primitives"]:
            a = prim["attributes"]
            pos, nor, uv = tableau(a["POSITION"]).astype(float), tableau(a["NORMAL"]).astype(float), tableau(a["TEXCOORD_0"]).astype(float)
            tris = tableau(prim["indices"]).reshape(-1, 3).astype(int)
            if "JOINTS_0" in a and os_:
                plus_fort = tableau(a["JOINTS_0"])[np.arange(len(pos)), np.argmax(tableau(a["WEIGHTS_0"]), axis=1)]
                paupiere = np.array([os_[j].startswith("paupiere") for j in plus_fort])
                tris = tris[~paupiere[tris].all(axis=1)]
            base = len(part["pos"])
            part["pos"] += [np.array([q[0], -q[2], q[1]]) for q in pos]          # du repère du jeu (Y en haut) au nôtre (Z en haut)
            part["nor"] += [np.array([q[0], -q[2], q[1]]) for q in nor]
            part["uv"] += [tuple(q) for q in uv]
            part["col"] += [(1.0, 1.0, 1.0)] * len(pos)
            part["tri"] += [(int(t[0]) + base, int(t[1]) + base, int(t[2]) + base) for t in tris]
    return m


def controle(animal, chemins):
    """L'animal quatre fois de suite : teint, puis ses trois robes sauvages. Sans le poil : c'est le jeu qui le pose."""
    glb = os.path.join(MODELES, animal, animal + ".glb")
    textures = {"teint": os.path.join(MODELES, animal, animal + "_couleur.png"), **{"robe_" + k: v for k, v in chemins.items()}}
    scenes, haut = [], 0.0
    for i, nom in enumerate(textures):
        m = lire_glb(glb, nom)
        pts = np.array(m.parts[nom]["pos"])
        haut = max(float((pts.max(axis=0) - pts.min(axis=0)).max()), haut)      # sa plus grande mesure : la place qu'il lui faut
        scenes.append((m, ((i - 1.5) * haut * 1.35, 0.0), -25))
    chemin = os.path.join(APERCUS, "brut-%s.png" % animal)
    O.dessiner(chemin, scenes, (0.0, -haut * 8.0, haut * 1.7), (0.0, 0.0, haut * 0.45), (3200, 1100), 37.3, dossiers=[], en_plus=textures)
    from PIL import ImageDraw, ImageFont                       # le nom de chaque robe sous l'animal
    img = Image.open(chemin)
    dessin = ImageDraw.Draw(img)
    police = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
    for i, texte in enumerate(("teint (aujourd'hui)", "A. délavée", "B. toile de sac", "C. cendre")):
        x = img.width * (0.125 + 0.25 * i)
        dessin.text((x - dessin.textlength(texte, font=police) / 2, img.height - 44), texte, font=police, fill=(255, 250, 232))
    img.save(chemin)


if __name__ == "__main__":
    import machine
    animaux = [a for a in sys.argv[1:] if a not in ("essais", "dessins")]
    with machine.tour("les robes sauvages", 600):
        if "essais" not in sys.argv and "dessins" not in sys.argv:
            for animal in animaux:
                robe(animal)
                for lettre in ROBES:                           # les essais refusés s'en vont
                    essai = os.path.join(MODELES, animal, "%s_brut_%s.png" % (animal, lettre))
                    for fichier in (essai, essai + ".import"):
                        if os.path.exists(fichier):
                            os.remove(fichier)
        else:
            for animal in animaux:
                chemins = {lettre: os.path.join(MODELES, animal, "%s_brut_%s.png" % (animal, lettre)) for lettre in ROBES}
                if "dessins" not in sys.argv:
                    chemins = {lettre: robe(animal, lettre) for lettre in ROBES}
                controle(animal, chemins)
            planche = Image.new("RGB", (1600, 550 * len(animaux)))
            for i, animal in enumerate(animaux):
                planche.paste(Image.open(os.path.join(APERCUS, "brut-%s.png" % animal)), (0, 550 * i))
            planche.save(os.path.join(APERCUS, "brut-propositions.png"))
