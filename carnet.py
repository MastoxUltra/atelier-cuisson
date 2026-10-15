"""Le carnet de Atelier : un lot de travaux Blender sur une machine louée (Kaggle tout seul, ou Colab lancé à la main).

Il trouve le lot (travaux.json, et à côté l'arbre « atelier » : art/sources, docs, regles, les entrées), installe le
même Blender que chez nous (Python 3.11.9 + bpy 4.5.14 + numpy 1.26.4 + pillow 12.3.0), règle Cycles sur la carte
(OptiX si elle répond, sinon CUDA), lance les travaux un par un depuis art/sources, et range dans la sortie SEULEMENT
les fichiers créés ou modifiés sous art/modeles et art/apercus (chemins relatifs gardés), avec un journal.

    python carnet.py                                    sur Kaggle : tout est trouvé seul (sortie : /kaggle/working/sortie)
    python carnet.py --entree /content/envoi --sortie /content/sortie        sur Colab (voir colab.ipynb)
    python carnet.py --sec --entree D --travail D --sortie D [--python PY] [--simuler]
            à blanc, sur n'importe quelle machine : vérifie le lot, déballe l'arbre, prépare la sortie, AUCUN calcul

Ce fichier n'utilise que la bibliothèque standard (Python 3.8 et plus) : c'est le Python 3.11 qu'il installe qui
fait tourner Blender. Les travaux voient BIBELOTS_DISTANT=1 (machine.py ne ménage rien), BIBELOTS_GPU=OPTIX ou CUDA
(atelier.neuf), et BIBELOTS_APERCUS=CYCLES si EEVEE ne marche pas sans écran (usine.py).
"""
import argparse
import ast
import glob
import hashlib
import json
import os
import re
import shutil
import concurrent.futures
import queue
import subprocess
import sys
import tarfile
import threading
import time
import urllib.request
import zipfile

LOT_ATTENDU = None          # envoyer.py écrit ici le nom du lot : si le jeu de données n'est pas encore à jour, on s'arrête tout de suite
VERSIONS = {"python": "3.11.9", "bpy": "4.5.14", "numpy": "1.26.4", "pillow": "12.3.0"}
BLENDER_SECOURS = "https://download.blender.org/release/Blender4.5/blender-4.5.14-linux-x64.tar.xz"
LIMITE_TRAVAIL = 3 * 3600   # un travail qui dépasse est arrêté (le lot peut la changer : "limite_travail")
LIMITE_TOTALE = 11 * 3600   # Kaggle coupe à 12 h : on ne lance plus rien après 11 h (installation comprise)
MAX_FICHIERS = 400          # Kaggle limite le nombre de fichiers de sortie : au-delà, tout part dans sortie/art.zip
RECOLTE = ("art/modeles", "art/apercus")
MARQUE = ".atelier-carnet"  # un dossier de travail ou de sortie qu'on peut vider : il porte cette marque
# ce qu'un script peut importer sans que ce soit un fichier de art/sources : Blender, numpy, pillow
CONNUS = {"bpy", "bmesh", "mathutils", "gpu", "gpu_extras", "bpy_extras", "bl_math", "idprop", "aud", "freestyle",
          "imbuf", "bgl", "blf", "bpy_types", "addon_utils", "rna_prop_ui", "bl_operators", "bl_ui", "cycles", "numpy", "PIL"}
LIBS_SYSTEME = ["libx11-6", "libxext6", "libxrender1", "libxi6", "libxkbcommon0", "libsm6", "libice6", "libxxf86vm1",
                "libxfixes3", "libgl1", "libegl1"]
ICI = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()   # Kaggle peut l'exécuter dans IPython

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


# ---------------------------------------------------------------- le journal

def _duree(s):
    s = int(s)
    return "%dh%02d" % (s // 3600, s % 3600 // 60) if s >= 3600 else "%dm%02d" % (s // 60, s % 60)


class Journal:
    """Chaque ligne va à l'écran (le journal de Kaggle) et dans sortie/journal.txt."""

    def __init__(self):
        self.debut = time.time()
        self.f = None
        self.attente = []

    def ouvrir(self, chemin):
        self.f = open(chemin, "a", encoding="utf-8")
        for ligne in self.attente:
            self.f.write(ligne + "\n")
        self.f.flush()

    def __call__(self, *morceaux):
        ligne = "[carnet %s +%s] %s" % (time.strftime("%H:%M:%S"), _duree(time.time() - self.debut), " ".join(str(m) for m in morceaux))
        print(ligne, flush=True)
        if self.f:
            self.f.write(ligne + "\n")
            self.f.flush()
        else:
            self.attente.append(ligne)


J = Journal()


def sh(cmd, timeout=1800, env=None, cwd=None, montrer=True):
    """Lance une commande, rend (code, sortie). Rien n'est caché : en cas d'échec, la fin de la sortie va au journal."""
    if montrer:
        J("$", " ".join(str(c) for c in cmd))
    try:
        r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, env=env, cwd=cwd)
        sortie = (r.stdout or "") + (r.stderr or "")
        code = r.returncode
    except subprocess.TimeoutExpired:
        sortie, code = "(temps dépassé : %d s)" % timeout, -9
    except OSError as e:
        sortie, code = str(e), -1
    if code != 0 and montrer:
        for ligne in sortie.strip().splitlines()[-15:]:
            J("   |", ligne)
    return code, sortie


# ---------------------------------------------------------------- trouver et déballer le lot

def trouver_entree(candidats):
    """Le dossier qui contient travaux.json (sur Kaggle : quelque part sous /kaggle/input)."""
    for racine in candidats:
        if not racine or not os.path.isdir(racine):
            continue
        for dossier, sous, fichiers in os.walk(racine):
            if "travaux.json" in fichiers:
                return dossier
            if dossier[len(racine):].count(os.sep) >= 4:
                sous[:] = []
            sous[:] = [s for s in sous if s not in ("atelier", "art", "proc", "sys")]
    return None


def _vider(dossier):
    """Vide un dossier de travail ou de sortie, seulement s'il est à nous (il porte la marque) ou vide."""
    if os.path.isdir(dossier) and os.listdir(dossier):
        if not os.path.exists(os.path.join(dossier, MARQUE)):
            raise SystemExit("[carnet] je refuse de vider %s : ce dossier n'est pas à moi (pas de %s)" % (dossier, MARQUE))
        shutil.rmtree(dossier)
    os.makedirs(dossier, exist_ok=True)
    open(os.path.join(dossier, MARQUE), "w").close()


def extraire_zip(archive, cible):
    with zipfile.ZipFile(archive) as z:
        for m in z.infolist():
            parties = m.filename.replace("\\", "/").split("/")
            if m.filename.startswith(("/", "\\")) or ".." in parties or ":" in parties[0]:
                raise SystemExit("[carnet] chemin refusé dans %s : %s" % (archive, m.filename))
        z.extractall(cible)


def deballer(entree, arbre):
    """Recopie l'arbre du lot dans le dossier de travail. Kaggle a pu garder atelier.zip tel quel, ou l'avoir déplié."""
    if os.path.isdir(os.path.join(entree, "atelier", "art", "sources")):
        source = os.path.join(entree, "atelier")
        shutil.copytree(source, arbre, dirs_exist_ok=True)
        J("arbre recopié depuis", source)
    elif os.path.isfile(os.path.join(entree, "atelier.zip")):
        extraire_zip(os.path.join(entree, "atelier.zip"), arbre)
        J("arbre déplié depuis", os.path.join(entree, "atelier.zip"))
    elif os.path.isdir(os.path.join(entree, "art", "sources")):
        for nom in os.listdir(entree):
            chemin = os.path.join(entree, nom)
            if os.path.isdir(chemin):
                shutil.copytree(chemin, os.path.join(arbre, nom), dirs_exist_ok=True)
        J("arbre recopié depuis", entree, "(déplié à la racine du jeu de données)")
    else:
        raise SystemExit("[carnet] ni atelier/, ni atelier.zip, ni art/sources dans " + entree)
    sources = os.path.join(arbre, "art", "sources")
    if not os.path.isfile(os.path.join(sources, "machine.py")):
        raise SystemExit("[carnet] art/sources/machine.py manque dans le lot")
    n = sum(len(f) for _d, _s, f in os.walk(arbre))
    J("arbre de travail :", arbre, "(%d fichiers)" % n)
    return sources


# ---------------------------------------------------------------- vérifier les travaux sans rien lancer

def _stdlib():
    """Les modules de la bibliothèque standard (Python 3.10 et plus) ; None avant : on ne juge pas les imports."""
    if not hasattr(sys, "stdlib_module_names"):
        return None
    return set(sys.stdlib_module_names) | set(sys.builtin_module_names)


def _local(nom, recherche):
    for d in recherche:
        for c in (os.path.join(d, nom + ".py"), os.path.join(d, nom, "__init__.py")):
            if os.path.isfile(c):
                return c
    return None


def verifier_travail(sources, commande):
    """(fatals, avertissements) pour une commande : le script existe, se compile, et ses imports se trouvent."""
    fatals, avis = [], []
    script = commande[0] if commande else ""
    chemin = os.path.normpath(os.path.join(sources, script))
    if not script.endswith(".py") or os.path.isabs(script) or not chemin.startswith(os.path.normpath(sources) + os.sep):
        return ["« %s » n'est pas un script .py sous art/sources" % script], avis
    if not os.path.isfile(chemin):
        return ["script introuvable : art/sources/" + script], avis
    stdlib = _stdlib()
    racines = [sources, os.path.join(sources, "animaux")]
    file_ = [chemin]
    # un argument qui nomme un fichier du kit (usine.py belette -> animaux/belette.py) est vérifié lui aussi
    for arg in commande[1:]:
        trouve = _local(arg, racines) if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", arg) else None
        if trouve:
            file_.append(trouve)
    vus = set()
    while file_:
        f = file_.pop()
        if f in vus:
            continue
        vus.add(f)
        try:
            arbre = ast.parse(open(f, encoding="utf-8-sig").read(), f)
            compile(arbre, f, "exec")
        except SyntaxError as e:
            fatals.append("erreur de syntaxe : %s ligne %s" % (os.path.relpath(f, sources), e.lineno))
            continue
        recherche = [os.path.dirname(f)] + racines
        for noeud in ast.walk(arbre):
            if isinstance(noeud, ast.Import):
                noms = [a.name.split(".")[0] for a in noeud.names]
            elif isinstance(noeud, ast.ImportFrom) and noeud.level == 0 and noeud.module:
                noms = [noeud.module.split(".")[0]]
            else:
                continue
            for nom in noms:
                local = _local(nom, recherche)
                if local:
                    file_.append(local)
                elif nom not in CONNUS and stdlib is not None and nom not in stdlib:
                    avis.append("import « %s » (dans %s) : ni dans art/sources, ni Blender, ni numpy/pillow" % (nom, os.path.relpath(f, sources)))
    return fatals, sorted(set(avis))


# ---------------------------------------------------------------- la police des titres de fiche

def trouver_police():
    """Une police grasse libre pour les titres des fiches (les scripts demandent C:/Windows/Fonts/segoeuib.ttf)."""
    candidats = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]
    for motif in ("/usr/share/fonts/**/DejaVuSans-Bold.ttf", "/usr/share/fonts/**/*Sans*Bold.ttf",
                  "/usr/local/lib/python3*/*-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans-Bold.ttf",
                  "/usr/lib/python3*/*-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans-Bold.ttf",
                  "/opt/conda/lib/python3*/site-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans-Bold.ttf"):
        candidats += sorted(glob.glob(motif, recursive=True))
    return next((c for c in candidats if os.path.isfile(c)), None)


def poser_police(sources):
    """Sous Linux, « C:/Windows/Fonts/segoeuib.ttf » est un chemin RELATIF : lancés depuis art/sources, les scripts
    le cherchent dans art/sources/C:/Windows/Fonts/. On y pose une police libre (DejaVu Sans Bold), sans toucher au code."""
    police = trouver_police()
    if os.name == "nt":
        J("police : rien à faire sous Windows (segoeuib.ttf est là) ; sous Linux ce serait :", police or "AUCUNE")
        return police
    if police is None:
        J("ATTENTION : aucune police grasse trouvée : les fiches échoueront au moment d'écrire leur titre")
        return None
    cible = os.path.join(sources, "C:", "Windows", "Fonts")
    os.makedirs(cible, exist_ok=True)
    shutil.copyfile(police, os.path.join(cible, "segoeuib.ttf"))
    J("police des titres :", police, "-> art/sources/C:/Windows/Fonts/segoeuib.ttf")
    return police


# ---------------------------------------------------------------- installer Blender (Python 3.11.9 + bpy)

CODE_VERSIONS = ("import sys, json, bpy, numpy, PIL; print('VERSIONS ' + json.dumps({'python': sys.version.split()[0], "
                 "'bpy': bpy.app.version_string, 'numpy': numpy.__version__, 'pillow': PIL.__version__}))")
CODE_VERSIONS_SEC = ("import sys, json, importlib.util as u, importlib.metadata as m; r = {'python': sys.version.split()[0]}\n"
                     "for p, mod in (('bpy', 'bpy'), ('numpy', 'numpy'), ('pillow', 'PIL')):\n"
                     "    r[p] = m.version(p) if u.find_spec(mod) else None\n"
                     "print('VERSIONS ' + json.dumps(r))")
LANCEUR = '''import os, runpy, sys
args = sys.argv[sys.argv.index("--") + 1:]
sys.argv = list(args)
sys.path.insert(0, os.path.dirname(os.path.abspath(args[0])))
runpy.run_path(args[0], run_name="__main__")
'''


def env_propre(**plus):
    """L'environnement du Python 3.11 : sans PYTHONPATH ni réglages pip/uv de la machine. Colab pose PYTHONPATH vers
    ses propres paquets (faits pour 3.12) : ils passeraient devant numpy 1.26.4 et casseraient bpy."""
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONUSERBASE", "VIRTUAL_ENV") and not k.startswith(("UV_", "PIP_"))}
    env.update(plus)
    return env


def _versions(sortie):
    for ligne in sortie.splitlines():
        if ligne.startswith("VERSIONS "):
            return json.loads(ligne[9:])
    return None


def _uv(outils):
    """La commande uv : installée par pip dans un dossier à part (rien ne change dans le Python de la machine)."""
    cible = os.path.join(outils, "uv-paquet")
    sh([sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--target", cible, "uv"], 600)
    for c in [os.path.join(cible, "bin", "uv"), shutil.which("uv")]:
        if c and os.path.isfile(c):
            return c
    script = os.path.join(outils, "installer-uv.sh")                         # second essai : l'installeur officiel d'astral
    urllib.request.urlretrieve("https://astral.sh/uv/install.sh", script)
    code, _ = sh(["sh", script], 600, env=dict(os.environ, UV_INSTALL_DIR=os.path.join(outils, "uv-bin"), UV_NO_MODIFY_PATH="1"))
    c = os.path.join(outils, "uv-bin", "uv")
    if code == 0 and os.path.isfile(c):
        return c
    raise RuntimeError("uv introuvable")


def installer_module(outils):
    """Le chemin choisi : un Python 3.11.9 portable (python-build-standalone, par uv), puis bpy en module comme chez nous.
    Kaggle et Colab n'ont pas Python 3.11 (Colab 3.12, Kaggle 3.13 en septembre 2026) et bpy 4.5 ne va qu'avec 3.11."""
    uv = _uv(outils)
    env = env_propre(UV_PYTHON_INSTALL_DIR=os.path.join(outils, "pythons"), UV_CACHE_DIR=os.path.join(outils, "cache-uv"))
    version = VERSIONS["python"]
    if sh([uv, "python", "install", version], 900, env)[0] != 0:
        J("Python %s introuvable chez uv : je prends le dernier 3.11 (bpy ne demande que 3.11.*)" % version)
        version = "3.11"
        if sh([uv, "python", "install", version], 900, env)[0] != 0:
            raise RuntimeError("uv n'a pas pu installer Python 3.11")
    venv = os.path.join(outils, "venv")
    if sh([uv, "venv", "--python", version, venv], 600, env)[0] != 0:
        raise RuntimeError("uv venv a échoué")
    py = os.path.join(venv, "bin", "python")
    paquets = ["bpy==%s" % VERSIONS["bpy"], "numpy==%s" % VERSIONS["numpy"], "pillow==%s" % VERSIONS["pillow"]]
    if sh([uv, "pip", "install", "--python", py] + paquets, 2400, env)[0] != 0:
        raise RuntimeError("l'installation de bpy a échoué")
    return py


def _bibliotheques_systeme():
    """bpy a besoin de quelques bibliothèques X11/GL que l'image peut ne pas avoir (on est root sur Kaggle et Colab)."""
    J("bibliothèques système manquantes : apt-get install", " ".join(LIBS_SYSTEME))
    sh(["apt-get", "update", "-qq"], 900)
    sh(["apt-get", "install", "-y", "-qq", "--no-install-recommends"] + LIBS_SYSTEME, 1200,
       env=dict(os.environ, DEBIAN_FRONTEND="noninteractive"))


def verifier_import(commande):
    """Importe vraiment bpy, numpy et PIL (commande : de quoi lancer CODE_VERSIONS), et rend leurs versions.
    Une bibliothèque système manquante est installée, puis on réessaie une fois."""
    for essai in (1, 2):
        code, sortie = sh(commande, 600, env=env_propre())
        versions = _versions(sortie)
        if code == 0 and versions:
            return versions
        if essai == 1 and "cannot open shared object file" in sortie:
            _bibliotheques_systeme()
            continue
        break
    raise RuntimeError("import de bpy impossible")


def installer_blender(outils):
    """Le dernier recours : le Blender 4.5.14 Linux officiel (378 Mo), les scripts lancés par un petit lanceur.
    Rend (base, préfixe) : base + ["--python-expr", code] exécute du code, préfixe + [script, args] lance un script."""
    archive = os.path.join(outils, os.path.basename(BLENDER_SECOURS))
    J("téléchargement de", BLENDER_SECOURS)
    urllib.request.urlretrieve(BLENDER_SECOURS, archive)
    try:
        sommes = urllib.request.urlopen(BLENDER_SECOURS.rsplit("/", 1)[0] + "/blender-%s.sha256" % VERSIONS["bpy"], timeout=60).read().decode()
        attendue = next((l.split()[0] for l in sommes.splitlines() if l.strip().endswith(os.path.basename(archive))), None)
    except Exception:
        attendue = None
    if attendue:
        h = hashlib.sha256()
        with open(archive, "rb") as f:
            for bloc in iter(lambda: f.read(1 << 20), b""):
                h.update(bloc)
        if h.hexdigest() != attendue:
            raise SystemExit("[carnet] somme de contrôle fausse pour " + archive)
        J("somme de contrôle sha256 : bonne")
    else:
        J("somme de contrôle : introuvable, je continue")
    with tarfile.open(archive) as t:
        if hasattr(tarfile, "data_filter"):
            t.extractall(outils, filter="data")
        else:
            t.extractall(outils)
    racine = os.path.join(outils, os.path.basename(archive).replace(".tar.xz", ""))
    blender = os.path.join(racine, "blender")
    pyb = sorted(glob.glob(os.path.join(racine, "4.5", "python", "bin", "python3*")))[0]
    sh([pyb, "-m", "ensurepip"], 600, env=env_propre())
    sh([pyb, "-m", "pip", "install", "--quiet", "pillow==%s" % VERSIONS["pillow"]], 900, env=env_propre())
    lanceur = os.path.join(outils, "lanceur.py")
    with open(lanceur, "w", encoding="utf-8") as f:
        f.write(LANCEUR)
    base = [blender, "-b", "--factory-startup", "--python-exit-code", "1"]
    return base, base + ["--python", lanceur, "--"]


def installer(outils):
    """Rend (mode, préfixe de commande, versions). Le préfixe suivi de « script.py args » lance un script Blender."""
    os.makedirs(outils, exist_ok=True)
    try:
        py = installer_module(outils)
        return "module (Python 3.11 portable + bpy)", [py, "-u", "-B"], verifier_import([py, "-c", CODE_VERSIONS])
    except Exception as e:
        J("ÉCHEC du chemin principal (%s) -> secours : le Blender %s Linux officiel" % (e, VERSIONS["bpy"]))
    base, prefixe = installer_blender(outils)
    try:
        versions = verifier_import(base + ["--python-expr", CODE_VERSIONS])
    except RuntimeError:
        raise SystemExit("[carnet] ni bpy ni le Blender officiel ne démarrent : voir le journal")
    return "blender officiel (secours)", prefixe, versions


# ---------------------------------------------------------------- les sondes : quelle carte, et EEVEE sans écran ?

SONDE_CYCLES = r'''
import json, sys
import bpy
genre, chemin = sys.argv[1], sys.argv[2]
bpy.ops.wm.read_factory_settings(use_empty=False)
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = genre
prefs.get_devices()
cartes = [d.name for d in prefs.devices if d.type == genre]
for d in prefs.devices:
    d.use = d.type == genre
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "GPU"
sc.cycles.samples = 8
sc.render.resolution_x = sc.render.resolution_y = 64
sc.render.filepath = chemin
bpy.ops.render.render(write_still=True)
px = list(bpy.data.images.load(chemin).pixels)
moyenne = sum(v for i, v in enumerate(px) if i % 4 != 3) / max(1, len(px) * 3 // 4)
print("SONDE " + json.dumps({"genre": genre, "cartes": cartes, "moyenne": round(moyenne, 4)}))
'''

SONDE_EEVEE = r'''
import json, sys, time
import bpy
t = time.time()
bpy.ops.wm.read_factory_settings(use_empty=False)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT"
sc.eevee.taa_render_samples = 4
sc.render.resolution_x = sc.render.resolution_y = 64
sc.render.filepath = sys.argv[1]
bpy.ops.render.render(write_still=True)
info = {"secondes": round(time.time() - t, 1)}
try:
    import gpu
    info.update(renderer=gpu.platform.renderer_get(), vendor=gpu.platform.vendor_get(), backend=gpu.platform.backend_type_get())
except Exception as e:
    info["gpu"] = str(e)[:120]
print("SONDE " + json.dumps(info))
'''


def _sonde(prefixe, dossier, nom, code_sonde, args, env, timeout):
    os.makedirs(dossier, exist_ok=True)
    script = os.path.join(dossier, nom + ".py")
    with open(script, "w", encoding="utf-8") as f:
        f.write(code_sonde)
    code, sortie = sh(prefixe + [script] + list(args), timeout, env=env, montrer=False)
    info = next((json.loads(l[6:]) for l in sortie.splitlines() if l.startswith("SONDE ")), None)
    return code, sortie, info


def choisir_gpu(prefixe, dossier, demande, env):
    """OptiX d'abord (plus rapide, et c'est ce qu'on a chez nous), CUDA sinon ; chacun vérifié par un rendu de 64 points."""
    code, sortie = sh(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"], 60, montrer=False)
    cartes_smi = [l.strip() for l in sortie.strip().splitlines()] if code == 0 else []
    J("cartes vues par nvidia-smi :", cartes_smi or "AUCUNE")
    ordre = [demande] if demande in ("OPTIX", "CUDA") else ["OPTIX", "CUDA"]
    for genre in ordre:
        chemin = os.path.join(dossier, "sonde_%s.png" % genre.lower())
        code, sortie, info = _sonde(prefixe, dossier, "sonde_cycles", SONDE_CYCLES, [genre, chemin], env, 1200)
        ok = code == 0 and info and info["cartes"] and info["moyenne"] > 0.005 and os.path.isfile(chemin)
        J("sonde Cycles %s :" % genre, "BONNE" if ok else "refusée", info or "(pas de réponse)", "" if ok else "code %s" % code)
        if not ok:
            for ligne in [l for l in sortie.splitlines() if re.search(r"(?i)error|fail|optix|cuda", l)][-6:]:
                J("   |", ligne[:200])
        if ok:
            return genre, info["cartes"], cartes_smi
    J("ATTENTION : ni OptiX ni CUDA ne répondent : Cycles tournera sur le processeur (lent)")
    return "NONE", [], cartes_smi


def _logiciel(info):
    texte = " ".join(str(info.get(k, "")) for k in ("renderer", "vendor")).lower()
    return any(m in texte for m in ("llvmpipe", "softpipe", "swrast", "software"))


def choisir_apercus(prefixe, dossier, demande, env):
    """EEVEE a besoin d'un contexte graphique. Sans écran, il peut manquer, ou tourner en logiciel (très lent) :
    alors les aperçus de l'usine passent par Cycles (BIBELOTS_APERCUS=CYCLES). Rend (moteur, DISPLAY ou None, infos)."""
    if demande in ("CYCLES", "BLENDER_EEVEE_NEXT"):
        J("aperçus : moteur imposé par le lot :", demande)
        return demande, None, {}
    chemin = os.path.join(dossier, "sonde_eevee.png")
    code, _s, info = _sonde(prefixe, dossier, "sonde_eevee", SONDE_EEVEE, [chemin], env, 600)
    if code == 0 and info and os.path.isfile(chemin):
        if not _logiciel(info):
            J("sonde EEVEE : BONNE, sur la carte", info)
            return "BLENDER_EEVEE_NEXT", None, info
        J("sonde EEVEE : marche, mais en logiciel", info, "-> aperçus de l'usine par Cycles")
        return "CYCLES", None, info
    J("sonde EEVEE sans écran : refusée (code %s)" % code)
    xvfb = shutil.which("Xvfb")
    if xvfb:                                       # un écran virtuel : EEVEE en logiciel, pour les scripts qui l'exigent
        subprocess.Popen([xvfb, ":99", "-screen", "0", "1280x1024x24", "-nolisten", "tcp"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        env2 = dict(env, DISPLAY=":99")
        code, _s, info = _sonde(prefixe, dossier, "sonde_eevee", SONDE_EEVEE, [chemin], env2, 900)
        if code == 0 and info:
            J("sonde EEVEE sous Xvfb :", info, "-> DISPLAY=:99 gardé pour les scripts qui exigent EEVEE ; aperçus de l'usine par Cycles")
            return "CYCLES", ":99", info
        J("sonde EEVEE sous Xvfb : refusée (code %s)" % code)
    J("EEVEE indisponible : aperçus de l'usine par Cycles ; usine_habitant.py (EEVEE imposé) échouera")
    return "CYCLES", None, info or {}


# ---------------------------------------------------------------- relever et récolter ce qui a changé

def _sha1(chemin):
    h = hashlib.sha1()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def releve(arbre):
    """{« art/modeles/... » : (taille, date, sha1)} pour tout ce qui est sous art/modeles et art/apercus."""
    etat = {}
    for sous in RECOLTE:
        base = os.path.join(arbre, *sous.split("/"))
        for dossier, _s, fichiers in os.walk(base):
            for nom in fichiers:
                chemin = os.path.join(dossier, nom)
                rel = os.path.relpath(chemin, arbre).replace(os.sep, "/")
                st = os.stat(chemin)
                etat[rel] = (st.st_size, st.st_mtime_ns, None)
    return etat


def releve_initial(arbre):
    return {rel: (t, d, _sha1(os.path.join(arbre, *rel.split("/")))) for rel, (t, d, _h) in releve(arbre).items()}


def recolter(arbre, initial, sortie):
    """Recopie dans sortie/ les fichiers créés ou modifiés depuis le début (et retire ceux qui ont disparu depuis la
    récolte précédente). Rend (fichiers, supprimés)."""
    maintenant = releve(arbre)
    fichiers = []
    for rel, (taille, date, _h) in sorted(maintenant.items()):
        avant = initial.get(rel)
        chemin = os.path.join(arbre, *rel.split("/"))
        if avant and avant[:2] == (taille, date):
            continue
        h = _sha1(chemin)
        if avant and avant[2] == h:
            continue
        cible = os.path.join(sortie, *rel.split("/"))
        if not (os.path.isfile(cible) and os.path.getsize(cible) == taille and _sha1(cible) == h):
            os.makedirs(os.path.dirname(cible), exist_ok=True)
            shutil.copy2(chemin, cible)
        fichiers.append({"chemin": rel, "taille": taille, "sha1": h, "etat": "modifié" if avant else "nouveau"})
    gardes = {f["chemin"] for f in fichiers}
    for sous in RECOLTE:
        base = os.path.join(sortie, *sous.split("/"))
        for dossier, _s, noms in os.walk(base):
            for nom in noms:
                rel = os.path.relpath(os.path.join(dossier, nom), sortie).replace(os.sep, "/")
                if rel not in gardes:
                    os.remove(os.path.join(dossier, nom))
    supprimes = sorted(rel for rel in initial if rel not in maintenant)
    return fichiers, supprimes


def emballer_si_trop(sortie, fichiers):
    """Au-delà de MAX_FICHIERS, Kaggle refuserait la sortie : tout art/ part dans sortie/art.zip."""
    if len(fichiers) <= MAX_FICHIERS:
        return None
    archive = os.path.join(sortie, "art.zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for f in fichiers:
            z.write(os.path.join(sortie, *f["chemin"].split("/")), f["chemin"])
    shutil.rmtree(os.path.join(sortie, "art"))
    J("%d fichiers : rangés dans sortie/art.zip" % len(fichiers))
    return "art.zip"


# ---------------------------------------------------------------- lancer un travail

def _slug(texte):
    return re.sub(r"[^a-z0-9_]+", "-", texte.lower()).strip("-")[:60] or "travail"


def lancer(n, commande, prefixe, sources, env, limite, journaux):
    """Un travail, seul, depuis art/sources. Toute sa sortie va dans journaux/NN-....txt ; à l'écran, seulement les
    lignes « [quelque chose] » et les erreurs (le filtre du GUIDE)."""
    nom = "%02d-%s.txt" % (n, _slug(" ".join(commande)))
    chemin = os.path.join(journaux, nom)
    cmd = prefixe + list(commande)
    J("travail %d : %s   (limite %s)" % (n, " ".join(commande), _duree(limite)))
    t0 = time.time()
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("$ (art/sources) %s\n" % " ".join(cmd))
        p = subprocess.Popen(cmd, cwd=sources, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding="utf-8", errors="replace", bufsize=1)

        def lire():
            for ligne in p.stdout:
                f.write(ligne)
                f.flush()
                if ligne.startswith("[") or re.search(r"Error|Traceback|Exception|line \d", ligne):
                    print("    " + ligne.rstrip()[:300], flush=True)

        lecteur = threading.Thread(target=lire, daemon=True)
        lecteur.start()
        try:
            code = p.wait(timeout=limite)
            etat = "ok" if code == 0 else "échec (code %d)" % code
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
            etat = "arrêté : plus de %s" % _duree(limite)
        lecteur.join(60)
    secondes = round(time.time() - t0, 1)
    J("travail %d : %s en %s" % (n, etat, _duree(secondes)))
    return {"n": n, "commande": list(commande), "etat": etat, "secondes": secondes, "journal": "journaux/" + nom}


# ---------------------------------------------------------------- tout

def main():
    ap = argparse.ArgumentParser(description="Le carnet de Atelier (voir art/distant/LISEZMOI.md)")
    ap.add_argument("--entree", help="le dossier qui contient travaux.json (sinon cherché sous /kaggle/input)")
    ap.add_argument("--sortie", help="où ranger la sortie (Kaggle : /kaggle/working/sortie)")
    ap.add_argument("--base", default="/tmp/atelier", help="dossier de travail : l'arbre, Python, Blender")
    ap.add_argument("--travail", help="(à blanc) dossier où déballer l'arbre")
    ap.add_argument("--sec", action="store_true", help="à blanc : vérifier et préparer, AUCUN calcul, aucune installation")
    ap.add_argument("--python", default=sys.executable, help="(à blanc) le Python où vérifier bpy, numpy, pillow (sans importer bpy)")
    ap.add_argument("--simuler", action="store_true", help="(à blanc) fait comme si un travail avait écrit un fichier, pour essayer la récolte")
    args, _inconnus = ap.parse_known_args()        # sous IPython, sys.argv porte « -f noyau.json » : on l'ignore
    debut = time.time()
    kaggle = os.path.isdir("/kaggle/working")
    lieu = "à blanc" if args.sec else "kaggle" if kaggle else "colab" if os.path.isdir("/content") else "autre"

    entree = args.entree or trouver_entree([ICI, "/kaggle/input", "/content/envoi"])
    if not entree:
        raise SystemExit("[carnet] aucun travaux.json trouvé (ni à côté du carnet, ni sous /kaggle/input)")
    lot = json.load(open(os.path.join(entree, "travaux.json"), encoding="utf-8"))
    sortie = os.path.abspath(args.sortie or ("/kaggle/working/sortie" if kaggle else os.path.join(os.getcwd(), "sortie")))
    _vider(sortie)
    journaux = os.path.join(sortie, "journaux")
    os.makedirs(journaux, exist_ok=True)
    J.ouvrir(os.path.join(sortie, "journal.txt"))
    J("lot « %s » (%s), %d travaux, lieu : %s, Python hôte %s" % (lot.get("lot"), lot.get("par", "?"), len(lot.get("travaux", [])),
                                                                   lieu, sys.version.split()[0]))
    J("entrée :", entree, "| sortie :", sortie)
    manifeste = {"lot": lot.get("lot"), "lieu": lieu, "debut": time.strftime("%Y-%m-%dT%H:%M:%S"), "fin": None,
                 "machine": {}, "travaux": [], "fichiers": [], "supprimes": [], "archive": None, "remarques": []}
    chemin_manifeste = os.path.join(sortie, "manifeste.json")

    def ecrire():
        with open(chemin_manifeste, "w", encoding="utf-8") as f:
            json.dump(manifeste, f, ensure_ascii=False, indent=1)

    if LOT_ATTENDU and lot.get("lot") != LOT_ATTENDU:
        J("ARRÊT : le jeu de données porte le lot « %s », j'attendais « %s » (sa nouvelle version n'était pas prête). "
          "Rien n'est lancé : renvoyer le lot." % (lot.get("lot"), LOT_ATTENDU))
        manifeste["remarques"].append("jeu de données pas à jour : rien lancé")
        manifeste["fin"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        ecrire()
        return 0

    travail = os.path.abspath(args.travail or os.path.join(args.base, "arbre"))
    _vider(travail)
    sources = deballer(entree, travail)

    # les travaux : chacun une commande, lancée depuis art/sources
    travaux = []
    for t in lot.get("travaux", []):
        commande = t.get("commande") if isinstance(t, dict) else t
        travaux.append([str(x) for x in (commande if isinstance(commande, list) else str(commande).split())])
    refuses = {}
    for n, commande in enumerate(travaux, 1):
        fatals, avis = verifier_travail(sources, commande)
        for a in avis:
            J("travail %d, avis :" % n, a)
        if fatals:
            refuses[n] = "; ".join(fatals)
            J("travail %d REFUSÉ :" % n, refuses[n])
        else:
            J("travail %d vérifié : %s" % (n, " ".join(commande)))
    poser_police(sources)

    env = env_propre(BIBELOTS_DISTANT="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    sondes = os.path.join(args.base if not args.sec else travail, "sondes")
    if args.sec:
        J("à blanc : pas d'installation ; je regarde ce que", args.python, "a déjà (sans importer bpy)")
        code, sortie_v = sh([args.python, "-c", CODE_VERSIONS_SEC], 120, montrer=False)
        versions = _versions(sortie_v) or {}
        if code != 0:
            J("  (ce Python ne répond pas : %s)" % sortie_v.strip()[-200:])
        for cle, voulue in VERSIONS.items():
            eue = versions.get(cle)
            J("  %-7s attendu %-7s trouvé %s%s" % (cle, voulue, eue, "" if eue == voulue else "   <- DIFFÉRENT"))
        mode, prefixe, genre, cartes, moteur, display = "à blanc", [args.python, "-u", "-B"], "(sonde sautée)", [], "(sonde sautée)", None
        J("à blanc : sondes OptiX/CUDA et EEVEE sautées (aucun rendu sur cette machine)")
        cartes_smi = []
        eevee = {}
    else:
        mode, prefixe, versions = installer(os.path.join(args.base, "outils"))
        J("Blender prêt :", mode, versions)
        for cle, voulue in VERSIONS.items():
            if versions.get(cle) != voulue and not (cle == "python" and str(versions.get(cle, "")).startswith("3.11")):
                J("ATTENTION : %s %s au lieu de %s" % (cle, versions.get(cle), voulue))
        genre, cartes, cartes_smi = choisir_gpu(prefixe, sondes, str(lot.get("gpu", "auto")).upper(), env)
        moteur, display, eevee = choisir_apercus(prefixe, sondes, str(lot.get("apercus", "auto")).upper(), env)
    env["BIBELOTS_GPU"] = genre if genre in ("OPTIX", "CUDA", "NONE") else "OPTIX"
    if moteur in ("CYCLES",):
        env["BIBELOTS_APERCUS"] = moteur
    if display:
        env["DISPLAY"] = display
    manifeste["machine"] = {"installation": mode, "versions": versions, "nvidia_smi": cartes_smi, "cycles": genre,
                            "cartes": cartes, "apercus_usine": moteur, "eevee": eevee, "python_hote": sys.version.split()[0]}
    ecrire()

    initial = releve_initial(travail)
    J("relevé initial : %d fichiers sous art/modeles et art/apercus" % len(initial))
    limite_totale = min(float(lot.get("limite_totale", LIMITE_TOTALE)), 11.5 * 3600)
    limite_travail = float(lot.get("limite_travail", LIMITE_TRAVAIL))
    # autant de travaux à la fois que de cartes (2 x T4 chez Kaggle) : chacun ne voit que la sienne (CUDA_VISIBLE_DEVICES).
    # La séance compte ses heures pour la machine, pas par carte : deux cartes occupées, c'est deux fois plus de travail
    # pour le même quota. « paralleles » dans travaux.json peut le réduire (1 = un par un, comme avant).
    nb_cartes = len(cartes_smi) if genre in ("OPTIX", "CUDA") else 0
    paralleles = 1 if args.sec or nb_cartes < 2 else max(1, min(int(lot.get("paralleles", nb_cartes)), nb_cartes))
    J("travaux en même temps : %d (cartes vues : %d)" % (paralleles, nb_cartes))
    manifeste["machine"]["paralleles"] = paralleles
    places = queue.Queue()
    for i in range(paralleles):
        places.put(i)
    garde = threading.Lock()
    resultats = {}

    def un_travail(n, commande):
        if n in refuses:
            r = {"n": n, "commande": commande, "etat": "refusé : " + refuses[n], "secondes": 0}
        elif args.sec:
            J("travail %d, à blanc : (art/sources) %s" % (n, " ".join(prefixe + commande)))
            r = {"n": n, "commande": commande, "etat": "pas lancé (à blanc)", "secondes": 0}
        else:
            place = places.get()
            try:
                reste = limite_totale - (time.time() - debut)
                if reste < 300:
                    J("travail %d : pas lancé, le temps de la séance est presque écoulé" % n)
                    r = {"n": n, "commande": commande, "etat": "pas lancé (temps)", "secondes": 0}
                else:
                    env_t = dict(env)
                    if paralleles > 1:
                        env_t["CUDA_VISIBLE_DEVICES"] = str(place)
                        J("travail %d sur la carte %d" % (n, place))
                    r = lancer(n, commande, prefixe, sources, env_t, min(limite_travail, reste), journaux)
                    r["carte"] = place if paralleles > 1 else None
            finally:
                places.put(place)
        with garde:                                   # après chaque travail : rien de perdu si la séance est coupée
            resultats[n] = r
            manifeste["travaux"] = [resultats[k] for k in sorted(resultats)]
            if not args.sec:
                manifeste["fichiers"], manifeste["supprimes"] = recolter(travail, initial, sortie)
            ecrire()

    with concurrent.futures.ThreadPoolExecutor(max_workers=paralleles) as pool:
        for fait in [pool.submit(un_travail, n, commande) for n, commande in enumerate(travaux, 1)]:
            fait.result()

    if args.sec and args.simuler:
        temoin = os.path.join(travail, "art", "apercus", "_carnet_a_blanc", "temoin.txt")
        os.makedirs(os.path.dirname(temoin), exist_ok=True)
        with open(temoin, "w", encoding="utf-8") as f:
            f.write("écrit par carnet.py --sec --simuler (lot %s)\n" % lot.get("lot"))
        J("à blanc : fichier témoin écrit (comme par un travail) :", os.path.relpath(temoin, travail))
    manifeste["fichiers"], manifeste["supprimes"] = recolter(travail, initial, sortie)
    manifeste["archive"] = emballer_si_trop(sortie, manifeste["fichiers"])
    manifeste["fin"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    ecrire()
    if kaggle and not args.sec:                     # rien d'inutile dans la sortie Kaggle
        os.remove(os.path.join(sortie, MARQUE))
    bons =sum(1 for t in manifeste["travaux"] if t["etat"] == "ok")
    J("FIN : %d/%d travaux bons, %d fichiers récoltés (%s), %d disparus, en %s" % (
        bons, len(travaux), len(manifeste["fichiers"]), ", ".join("%d %s" % (sum(1 for f in manifeste["fichiers"] if f["etat"] == e), e)
                                                                   for e in ("nouveau", "modifié")),
        len(manifeste["supprimes"]), _duree(time.time() - debut)))
    for t in manifeste["travaux"]:
        J("  %2d  %-40s %s" % (t["n"], " ".join(t["commande"])[:40], t["etat"]))
    return 0


if __name__ == "__main__":
    if main():
        sys.exit(1)
