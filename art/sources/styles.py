"""Les trois façons de faire une peluche. l'auteur les a choisies le 13 octobre 2026, sur la planche de la poule :
« A, B et la C », les trois dans le jeu, chaque espèce a la sienne.

    A  cousu main          yeux en boutons à croix, coutures et points de feston visibles (le style d'origine)
    B  peluche de magasin  billes de verre, aucune couture apparente, un poil long et doux (plus court sur la tête),
                           des couleurs adoucies, plus proches du vrai animal
    C  velours ras         yeux de feutrine mate avec leur reflet blanc, aucune couture, un velours court et net,
                           des couleurs franches

Le fichier d'un animal ne change pas : on rejoue son construire() en remplaçant, le temps de le bâtir, quelques gestes
du kit (les yeux, les coutures, les couleurs, le poil). Les formes, le squelette et les animations sont les mêmes.

    python styles.py poule B         rend la fiche art/apercus/styles/poule_B.png (attend son tour, comme toute fiche)
    python styles.py planche poule   assemble art/apercus/styles/banc-poule.png avec les fiches qui existent

L'usine s'en sert aussi : python usine.py lapin style=B (voir usine.py), et écrit les réglages du jeu dans <animal>.json.
"""
import importlib
import os
import sys
from contextlib import contextmanager

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
sys.path.insert(0, os.path.join(ICI, "animaux"))
FICHES = os.path.normpath(os.path.join(ICI, "..", "apercus", "styles"))
STYLES = {  # le titre, les yeux, des coutures ?, la longueur du poil, la vivacité des couleurs, le poil de la tête
    "A": dict(titre="A. cousu main", yeux=None, coutures=True, poil=1.0, vif=1.0, tete=1.0),
    "B": dict(titre="B. peluche de magasin", yeux="verre", coutures=False, poil=1.8, vif=0.60, tete=0.6),
    "C": dict(titre="C. velours ras", yeux="feutre", coutures=False, poil=0.45, vif=1.0, tete=1.0),
}
# LA RÈGLE, choisie par l'auteur le 13 octobre 2026 : par rareté. « Plus l'animal est dur à obtenir, plus la peluche est belle. »
#     paliers 1 et 2 (familiers, courants)  ->  A, cousu main
#     palier 3 (farouches)                  ->  C, velours ras
#     paliers 4 et 5 (rares, vedettes)      ->  B, peluche de magasin
# Le palier de chaque animal est dans docs/animaux.md (tenu par la session du jeu ; l'auteur peut en faire monter ou descendre un).
STYLE_DU_PALIER = {1: "A", 2: "A", 3: "C", 4: "B", 5: "B"}
STYLE_DE = {}        # une exception voulue pour une espèce : {"renard": "C"}
LISTE = os.path.normpath(os.path.join(ICI, "..", "..", "docs", "animaux.md"))
AUTRES_NOMS = {"mante": "mante_religieuse", "tortue_eau": "tortue_d_eau", "poisson_rouge": "poisson_rouge", "boeuf_musque": "bœuf_musque",
               "chien_corgi": "chien", "chien_husky": "chien", "chien_berger": "chien", "chien_caniche": "chien", "chien_carlin": "chien"}   # les races : le palier du chien     # fichier -> nom dans la liste


def _cle(nom):
    """« Carpe koï ★ » -> « carpe_koi » : sans accents, sans étoile, les blancs et les traits en soulignés."""
    import unicodedata
    nom = unicodedata.normalize("NFD", nom.replace("★", "").strip().lower())
    nom = "".join(c for c in nom if unicodedata.category(c) != "Mn")
    return "_".join("".join(c if c.isalnum() else " " for c in nom).split())


def paliers():
    """Le palier de chaque animal de la liste : {« carpe_koi » : 2, ...}."""
    trouves = {}
    try:
        for ligne in open(LISTE, encoding="utf-8"):
            cases = [c.strip() for c in ligne.split("|")]
            if len(cases) > 5 and cases[4][:1].isdigit():
                trouves.setdefault(_cle(cases[1]), int(cases[4][0]))
    except OSError:
        pass
    return trouves


def palier_de(animal):
    animal = animal[:-3] if animal.endswith("_v2") else animal
    return paliers().get(AUTRES_NOMS.get(animal, animal))


def style_de(animal):
    if animal in STYLE_DE:
        return STYLE_DE[animal]
    palier = palier_de(animal)
    if palier is None:
        print("[styles] « %s » n'est pas dans la liste des animaux : style A" % animal, flush=True)
    return STYLE_DU_PALIER.get(palier, "A")


def reglages(lettre, taille):
    """Les réglages de poil.gdshader et peluche.gdshader pour un animal de cette taille (en mètres) dans ce style.
    Le jeu les pose tels quels sur les matières de l'animal ; un réglage absent garde sa valeur par défaut."""
    base = min(0.05, max(0.010, 0.018 * ((taille or 0.7) / 0.7) ** 0.5))       # un petit animal a le poil plus court ; un géant plus long (5 cm au plus)
    if lettre == "B":
        return {"longueur": round(base * 1.7, 4), "touffes": 0.7, "densite": 440.0, "racine": 0.62, "velours": 0.6}
    if lettre == "C":
        return {"longueur": round(base * 0.45, 4), "touffes": 0.15, "densite": 820.0, "racine": 0.86, "nuance": 0.06, "velours": 0.8}
    return {"longueur": round(base, 4)}


@contextmanager
def habiller(lettre):
    """Le temps du bloc, les gestes du kit sont ceux du style : yeux, coutures, couleurs."""
    import numpy as np
    from mathutils import Vector

    import atelier as A
    import peluche as K

    s = STYLES[lettre]
    d_origine = {nom: getattr(K.Animal, nom) for nom in ("bouton", "couture", "ourlet", "rustine", "piece")}

    def adoucie(c):
        """Une couleur moins vive, plus proche du vrai animal : on la ramène vers son gris."""
        c = np.asarray(c, float)
        gris = np.expand_dims(c @ np.array([0.30, 0.59, 0.11]), -1)
        return (gris + (c - gris) * s["vif"]) * 0.97

    def piece(self, nom, maille, couleur, *args, **kw):
        if s["vif"] != 1.0:
            if couleur is not None:
                couleur = tuple(adoucie(couleur))
            elif getattr(maille, "teinte", None) is not None:
                maille.teinte = adoucie(maille.teinte)
        return d_origine["piece"](self, nom, maille, couleur, *args, **kw)

    def bouton(self, nom, pos, vers, rayon=0.03, couleur=K.NOIR, fil=K.JAUNE, paire=False):
        if not nom.startswith("oeil"):
            return d_origine["bouton"](self, nom, pos, vers, rayon, couleur, fil, paire)
        if s["yeux"] == "feutre":                            # un œil de feutrine à reflet : celui du kit
            return K.Animal.oeil(self, nom, pos, vers, rayon, paire)
        self._boutons.append((nom, Vector(pos), Vector(vers).normalized(), rayon, paire))     # l'usine y pose les paupières
        self._bombe = 0.72                                   # de combien l'œil dépasse, en rayons : la paupière doit le couvrir
        bille = A.boule(1.0, 28, 14).etire(rayon * 0.95, rayon * 0.95, rayon * 0.72)       # une bille noire, à demi enfoncée
        self._poser(self._jouet(self._durs, K.NOIR, "d"), nom, bille, "bouton", A.cadre(Vector(pos), Vector(vers)), paire, "volume", "dur")

    def rustine(self, *args, **kw):
        args = list(args)
        if len(args) > 7:                                    # (nom, sur, centre, axe, ouverture, couleur, epaisseur, feston, ...)
            args[7] = 0
        else:
            kw["feston"] = 0
        if s["vif"] != 1.0:
            if len(args) > 5 and args[5] is not None:
                args[5] = tuple(adoucie(args[5]))
            elif kw.get("couleur") is not None:
                kw["couleur"] = tuple(adoucie(kw["couleur"]))
        return d_origine["rustine"](self, *args, **kw)

    try:
        if lettre != "A":
            K.Animal.piece, K.Animal.bouton = piece, bouton
            if not s["coutures"]:
                K.Animal.couture = lambda self, *args, **kw: None
                K.Animal.ourlet = lambda self, *args, **kw: None
                K.Animal.rustine = rustine
        yield
    finally:
        for nom, geste in d_origine.items():
            setattr(K.Animal, nom, geste)


def construire(animal, lettre, module=None):
    """L'animal bâti dans ce style. Le poil de la tête est plus court là où le style le demande (le visage reste lisible)."""
    import numpy as np

    s = STYLES[lettre]
    module = module or importlib.import_module(animal)
    with habiller(lettre):
        a = module.construire()
    a.style = lettre
    if s["poil"] != 1.0:
        bas, haut = a.boite()
        a.poil_long = (a.poil_long or __import__("peluche").poil_par_taille(float(max(haut - bas)))) * s["poil"]
    if s["tete"] != 1.0 and a.tete is not None:
        bas, haut = a.boite()
        pres = 0.20 * float(max(haut - bas))
        for p in a._toutes():
            if p.get("poil") is not None and float(np.linalg.norm(p["monde"].mean(axis=0) - np.array(a.tete))) < pres:
                p["poil_k"] = s["tete"]
    return a


def rendre(animal, lettre):
    import bpy  # avant mathutils

    import peluche as K

    def bati():
        a = construire(animal, lettre)
        a.nom = "%s_%s" % (animal, lettre)
        return a

    os.makedirs(FICHES, exist_ok=True)
    K.FICHES = FICHES
    K.planche(bati, STYLES[lettre]["titre"])


def planche(animal, lettres="ABC"):
    """Les styles côte à côte : la grande vue de chaque fiche qui existe, avec la lettre et le nom du style."""
    from PIL import Image, ImageDraw, ImageFont
    police = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 34)
    vues = []
    for lettre in lettres:
        chemin = os.path.join(FICHES, "%s_%s.png" % (animal, lettre)) if lettre != "A" else os.path.join(FICHES, "..", "animaux", animal + ".png")
        if os.path.exists(chemin):
            vues.append((lettre, Image.open(chemin).convert("RGB").crop((0, 0, 1280, 720)).resize((960, 540), Image.LANCZOS)))
    colonnes = 2 if len(vues) > 3 else len(vues)
    img = Image.new("RGB", (960 * colonnes, 540 * ((len(vues) + colonnes - 1) // colonnes)), (20, 20, 20))
    dessin = ImageDraw.Draw(img)
    for i, (lettre, vue) in enumerate(vues):
        x, y = (i % colonnes) * 960, (i // colonnes) * 540
        img.paste(vue, (x, y))
        texte = STYLES[lettre]["titre"]
        large = max(dessin.textlength(texte, font=police), 300)             # assez grande pour couvrir l'étiquette de la fiche
        dessin.rounded_rectangle((x + 12, y + 8, x + 12 + large + 44, y + 78), 18, fill=(255, 246, 224))
        dessin.text((x + 32, y + 20), texte, font=police, fill=(70, 44, 24))
    sortie = os.path.join(FICHES, "banc-%s.png" % animal)
    img.save(sortie)
    print("[banc]", sortie, flush=True)


def fiches_du_jeu():
    """Écrit <animal>.json à côté de chaque modèle déjà fabriqué en style A et qui n'en a pas : son style, les réglages
    de son poil. Sans Blender. Les modèles fabriqués depuis reçoivent le leur de l'usine."""
    import json
    import re
    modeles = os.path.normpath(os.path.join(ICI, "..", "modeles"))
    for animal in sorted(os.listdir(modeles)):
        source = os.path.join(ICI, "animaux", animal + ".py")
        sortie = os.path.join(modeles, animal, animal + ".json")
        if not os.path.exists(os.path.join(modeles, animal, animal + ".glb")) or not os.path.exists(source) or os.path.exists(sortie):
            continue
        trouve = re.search(r"a\.taille\s*=\s*([0-9.]+)", open(source, encoding="utf-8").read())
        taille = float(trouve.group(1)) if trouve else None
        with open(sortie, "w", encoding="utf-8") as f:
            json.dump({"style": "A", "taille": taille, "poil": reglages("A", taille)}, f, ensure_ascii=False, indent=1)
        print("[json]", animal, "A", taille, "(sa règle :", style_de(animal) + ")", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "json":
        fiches_du_jeu()
    elif sys.argv[1] == "planche":
        for nom in sys.argv[2:]:
            planche(nom)
    else:
        rendre(sys.argv[1], sys.argv[2])
