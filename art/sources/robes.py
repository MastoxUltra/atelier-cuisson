"""Les robes gagnées des peluches : une seule texture par animal, et le jeu recolore ses zones (poil, pièces rapportées,
feutrine rase) dans la teinte de la robe, en gardant le clair et le foncé du dessin. Demande de la session principale,
le 14 octobre 2026 : « colorer les peluches, c'est le but du jeu, et aujourd'hui on ne voit pas la couleur changer ».

    python robes.py escargot mouffette       écrit « robes » dans art/modeles/<animal>/<animal>.json
    python robes.py tous                     tous les animaux fabriqués
    python robes.py planche escargot mouffette   le dessin de contrôle : sauvage, d'origine, robe 1, robe 2

Ce qui va dans <animal>.json, clé « robes » :
    moyennes     la couleur moyenne de chaque zone dans la texture d'origine (le shader divise par sa clarté)
    <couleur>    facultatif : la teinte d'une zone pour cette espèce, si celle de la palette commune ne lui va pas
Le jeu : art/shaders/robes.gd (Robes.porter(noeud, animal, couleur)) ; les shaders : peluche.gdshader et poil.gdshader.
La même formule est reprise ici, en numpy, pour le dessin de contrôle (sans le poil en couches).

SANS BLENDER (numpy), quelques secondes par animal.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

import objets as O

MODELES = os.path.normpath(os.path.join(O.ICI, "..", "modeles"))
APERCUS = os.path.normpath(os.path.join(O.ICI, "..", "apercus"))
REGLES = os.path.normpath(os.path.join(O.ICI, "..", "..", "regles", "robes.json"))
ZONES = ("poil", "pieces", "accents")
# la palette commune, la même que dans robes.gd : pour chaque teinture, le poil, les pièces rapportées (plus claires), la
# feutrine rase (plus profonde). Des couleurs franches : une robe gagnée doit se voir de loin.
PALETTE = {
    "rouge": ("#c8322a", "#f2c6b2", "#6e1c18"),
    "orange": ("#e8761e", "#f8d4a4", "#7c3610"),
    "jaune": ("#e8b828", "#f8e8aa", "#8a5c12"),
    "verte": ("#4a9c3c", "#d2e8ac", "#24481c"),
    "bleue": ("#2f64bc", "#bcd2f0", "#1a2e60"),
    "violette": ("#7c3c9c", "#e0c4ec", "#3c1a50"),
    "brune": ("#7c4a2a", "#dcb88e", "#3e2616"),
}
NOMS = {"origine": "d'origine", "sauvage": "sauvage"}


def lineaire(c):
    c = np.asarray(c, np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb(c):
    c = np.clip(np.asarray(c, np.float32), 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def hexa(c):
    return "#%02x%02x%02x" % tuple(int(round(v * 255)) for v in np.clip(c, 0, 1))


def de_hexa(h):
    return np.array([int(h[k:k + 2], 16) / 255 for k in (1, 3, 5)], np.float32)


def lire(animal):
    d = os.path.join(MODELES, animal)
    couleur = np.asarray(Image.open(os.path.join(d, animal + "_couleur.png")).convert("RGB"), np.float32) / 255
    taille = couleur.shape[0]
    zones = np.asarray(Image.open(os.path.join(d, animal + "_zones.png")).convert("RGB").resize((taille, taille)), np.float32) / 255
    return couleur, zones


def masques(zones):
    return {"poil": (zones[..., 0] >= 0.25).astype(np.float32), "pieces": zones[..., 1], "accents": zones[..., 2]}


def moyennes(animal):
    """La couleur moyenne de chaque zone (pondérée par la zone), en sRGB. Une zone presque absente n'en a pas."""
    couleur, zones = lire(animal)
    lin = lineaire(couleur)
    faites = {}
    for nom, w in masques(zones).items():
        if w.sum() < 400:
            continue
        faites[nom] = hexa(srgb((lin * w[..., None]).sum(axis=(0, 1)) / w.sum()))
    return faites


def ecrire(animal):
    chemin = os.path.join(MODELES, animal, animal + ".json")
    d = json.load(open(chemin, encoding="utf-8")) if os.path.exists(chemin) else {}
    robes = d.get("robes", {})
    robes["moyennes"] = moyennes(animal)
    d["robes"] = robes
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print("[robes]", animal, robes["moyennes"], flush=True)


def teintes(animal, couleur):
    propres = {}
    chemin = os.path.join(MODELES, animal, animal + ".json")
    if os.path.exists(chemin):
        propres = json.load(open(chemin, encoding="utf-8")).get("robes", {}).get(couleur, {})
    return [de_hexa(propres.get(z, PALETTE[couleur][i])) for i, z in enumerate(ZONES)]


def peindre(animal, couleur):
    """La texture que le shader montre pour cette robe (la même formule, en numpy, dans l'espace linéaire)."""
    c, zones = lire(animal)
    if couleur == "origine":
        return c
    moy = json.load(open(os.path.join(MODELES, animal, animal + ".json"), encoding="utf-8"))["robes"]["moyennes"]
    lin = lineaire(c)
    lum = lin @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    for (nom, w), robe in zip(masques(zones).items(), teintes(animal, couleur)):
        if nom not in moy:
            continue
        k = np.clip(lum / max(float(lineaire(de_hexa(moy[nom])) @ np.array([0.2126, 0.7152, 0.0722])), 0.02), 0, 3)[..., None]
        r = lineaire(robe)
        neuf = np.where(k <= 1, r * (0.45 + 0.55 * k), r + (1 - r) * np.minimum((k - 1) * 0.5, 0.85))   # comme le shader
        lin = lin * (1 - w[..., None]) + neuf * w[..., None]
    return srgb(lin)


def planche(animaux):
    """Chaque animal quatre fois : sauvage, d'origine, sa robe 1, sa robe 2 (les couleurs de regles/robes.json)."""
    import brut as B
    from PIL import ImageDraw, ImageFont
    regles = json.load(open(REGLES, encoding="utf-8"))["robes"]
    rangs = []
    for animal in animaux:
        robes = [r["couleur"] for r in regles.get(animal, [])][:2] or ["brune", "bleue"]
        etats = ["sauvage", "origine"] + robes
        textures = {}
        for etat in etats:
            chemin = os.path.join(MODELES, animal, animal + "_brut.png") if etat == "sauvage" else os.path.join(O.ICI, "essais", "robes", "%s_%s.png" % (animal, etat))
            if etat != "sauvage":
                os.makedirs(os.path.dirname(chemin), exist_ok=True)
                Image.fromarray(np.clip(peindre(animal, etat) * 255, 0, 255).astype(np.uint8), "RGB").save(chemin)
            textures[etat] = chemin
        glb = os.path.join(MODELES, animal, animal + ".glb")
        scenes, haut = [], 0.0
        for i, etat in enumerate(etats):
            m = B.lire_glb(glb, etat)
            pts = np.array(m.parts[etat]["pos"])
            haut = max(float((pts.max(axis=0) - pts.min(axis=0)).max()), haut)
            scenes.append((m, ((i - 1.5) * haut * 1.35, 0.0), -25))
        chemin = os.path.join(APERCUS, "robes-%s.png" % animal)
        O.dessiner(chemin, scenes, (0.0, -haut * 8.0, haut * 1.7), (0.0, 0.0, haut * 0.45), (3200, 1100), 37.3, dossiers=[], en_plus=textures)
        img = Image.open(chemin)
        dessin = ImageDraw.Draw(img)
        police = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 30)
        for i, etat in enumerate(etats):
            texte = "%s : %s" % (animal, NOMS.get(etat, "robe " + etat)) if i == 0 else NOMS.get(etat, "robe " + etat)
            x = img.width * (0.125 + 0.25 * i)
            dessin.text((x - dessin.textlength(texte, font=police) / 2, img.height - 48), texte, font=police, fill=(255, 250, 232))
        img.save(chemin)
        rangs.append(chemin)
    vues = [Image.open(c).convert("RGB").resize((1600, 550)) for c in rangs]
    p = Image.new("RGB", (1600, 550 * len(vues)))
    for i, v in enumerate(vues):
        p.paste(v, (0, 550 * i))
    sortie = os.path.join(APERCUS, "robes.png")
    p.save(sortie)
    print("[planche]", sortie, flush=True)


if __name__ == "__main__":
    import machine
    animaux = [a for a in sys.argv[1:] if a not in ("planche", "tous")]
    if "tous" in sys.argv:
        animaux = sorted(n for n in os.listdir(MODELES) if os.path.exists(os.path.join(MODELES, n, n + "_zones.png")))
    with machine.tour("les robes (sans Blender)", 300):
        for animal in animaux:
            ecrire(animal)
        if "planche" in sys.argv:
            planche(animaux)
