"""L'usine : d'un animal du kit (animaux/<nom>.py) à son modèle de jeu.

    python usine.py canard              tout : paupières, maillage allégé, textures cuites, squelette, animations,
                                        export dans art/modeles/canard/, aperçus animés dans art/apercus/animations/
    python usine.py canard sans-apercus le modèle seulement
    python usine.py canard style=B      dans un autre style que celui de l'espèce (A cousu main, B peluche de magasin,
                                        C velours ras : voir styles.py) ; vaut aussi pour « essai »
    python usine.py machine             dit seulement si la machine est libre et froide (rien n'est lancé)
    python usine.py canard fusion       sur la base fusionnée (une peau d'une seule pièce, voir fusion.py) ; éteinte par
                                        défaut, vaut aussi pour « essai » ; FUSION = True dans le fichier de la bête l'allume
    python usine.py canard gonflage     la base fusionnée, gonflée (des volumes ronds et rembourrés : fusion.gonfler) ;
                                        éteint par défaut, vaut aussi pour « essai » ; GONFLAGE = True dans le fichier l'allume

L'usine ménage la machine : une seule fabrication à la fois (un verrou), rien tant qu'un jeu tourne ou que la carte
graphique est chaude, et un repos après chaque passe de cuisson. Elle attend d'elle-même, puis renonce au bout de 30 minutes.

Le fichier de l'animal doit définir, en plus de construire() :
    OS          les os : (nom, parent, position de sa tête), dans les mesures du modèle (avant a.taille).
                Ceux qui finissent par « _G » sont recopiés en miroir en « _D ».
    PORTEURS    quelle pièce suit quel os : (début du nom de la pièce, os, a-t-il un côté).
                À la place de l'os, une fonction (points, cote) -> {os: poids} pour une pièce souple ;
                un détail cousu sur elle (joue, couture) prend la même fonction et, en troisième, l'os qui porte
                le plus la pièce : ("joue", souple, "corps"). Une étoile y prend le côté : "oreille*" -> oreille_G.
    ANIMATIONS  {nom: (nombre d'images à 30 par seconde, fonction du temps -> Pose, en boucle ?)}
                Noms attendus par le jeu : repos, avance, mange, joie, dort.

Dans une Pose, les angles sont en degrés autour des axes du monde (il regarde vers -Y, sa gauche en +X) :
    rx > 0 : ce qui est au-dessus du pivot part vers l'avant ; ce qui est en dessous part vers l'arrière
    ry > 0 : le haut penche vers sa gauche          rz > 0 : il tourne vers sa gauche
Les yeux : pose.ouvert = 1 (ouverts, par défaut) à 0 (fermés). Les paupières sont ajoutées par l'usine.
"""
import importlib
import math
import os
import sys
import time

import bpy  # avant mathutils
import bmesh
import numpy as np
from mathutils import Euler, Vector

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
sys.path.insert(0, os.path.join(ICI, "animaux"))
import atelier as A
import garnitures as G
import matieres as M
import peluche as K
from poses import Pose, borne, cloche, onde

MODELES = os.path.normpath(os.path.join(ICI, "..", "modeles"))
APERCUS = os.path.normpath(os.path.join(ICI, "..", "apercus", "animations"))
TAU = math.tau
TAILLE = 2048             # le côté des textures (4096 pour un géant de plus de 4 m : voir _fabriquer)
TAILLE_NORMALE, TAILLE_GEANT, GEANT = 2048, 4096, 4.0
TRIANGLES = 11000         # le budget du maillage du jeu


# ---------------------------------------------------------------- ménager la machine
# Le PC d'l'auteur est un portable à un seul ventilateur, et il joue dessus : voir machine.py. Une seule fabrication
# à la fois, jamais pendant un jeu ni à chaud, et la carte graphique souffle entre deux passes de cuisson.

import epingle
import machine
import styles
from machine import souffler

CUISSON_FROIDE = 74.0          # une passe de cuisson ne part pas au-dessus (elle fait monter la carte de sept degrés)


# ---------------------------------------------------------------- les poses

class Animateur:
    def __init__(self, arm, echelle):
        self.arm, self.k = arm, echelle
        self.repos = {b.name: b.matrix_local.to_3x3() for b in arm.data.bones}

    def poser(self, pose):
        for pb in self.arm.pose.bones:
            o = pose.os.get(pb.name)
            if o is None:
                o = {"rot": (0, 0, 0), "pos": (0, 0, 0), "ech": (1, 1, 1)}
                if pb.name.startswith("paupiere"):
                    s = max(0.03, 1.0 - pose.ouvert)
                    o["ech"] = (s, s, s)
            r = self.repos[pb.name]
            rq = r.to_quaternion()
            q = Euler([math.radians(a) for a in o["rot"]], "XYZ").to_quaternion()
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = rq.conjugated() @ q @ rq
            rt = r.transposed()
            pb.location = rt @ (Vector(o["pos"]) * self.k)          # les déplacements sont dans les mesures du modèle
            pb.scale = [abs(rt[i][0]) * o["ech"][0] + abs(rt[i][1]) * o["ech"][1] + abs(rt[i][2]) * o["ech"][2] for i in range(3)]
        bpy.context.view_layer.update()

    def enregistrer(self, nom, images, fonction, boucle):
        ad = self.arm.animation_data or self.arm.animation_data_create()
        action = bpy.data.actions.new(nom)
        ad.action = action
        for f in range(images + 1):
            self.poser(fonction((f % images) / images if boucle else f / images))
            for pb in self.arm.pose.bones:
                if pb.name.startswith(epingle.OS_LIBRES):         # le jeu les commande lui-même
                    continue
                for canal in ("location", "rotation_quaternion", "scale"):
                    pb.keyframe_insert(canal, frame=f)
        piste = ad.nla_tracks.new()
        piste.name = nom
        piste.strips.new(nom, 0, action)
        ad.action = None


def squelette(nom, objets, liste_os, k):
    arm = bpy.data.armatures.new("Squelette")
    ob = bpy.data.objects.new(nom.capitalize(), arm)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    for n, parent, tete in liste_os:
        b = arm.edit_bones.new(n)
        b.head = Vector(tete) * k
        b.tail = b.head + Vector((0, 0, 0.06 * k))
        b.roll = 0.0
        if parent:
            b.parent = arm.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    for o in objets:
        o.parent = ob
        o.modifiers.new("Squelette", "ARMATURE").object = ob
    return ob


def tous_les_os(liste):
    """Ajoute les os de droite, miroirs de ceux de gauche."""
    return list(liste) + [(n.replace("_G", "_D"), p.replace("_G", "_D") if p else p, (-t[0], t[1], t[2])) for n, p, t in liste if n.endswith("_G")]


# ---------------------------------------------------------------- les paupières

def paupieres(a):
    """Pour chaque œil en bouton, une paupière de feutrine de la couleur de la tête, fermée au repos,
    avec le trait brodé de l'œil qui dort. Rend les os à ajouter : (nom, pièce voisine, position).
    Un animal peut régler les siennes dans construire() : a.couleur_paupiere (sinon la couleur moyenne de la pièce voisine,
    grise sur une tête noire et blanche) et a.large_paupiere (1,14 fois l'œil ; plus large si sa pupille se déplace)."""
    ajouts = []
    for i, (nom, pos, vers, rayon, paire) in enumerate([b for b in a._boutons if b[0].startswith("oeil")]):
        voisine = min(a._arbres, key=lambda n: a._arbres[n].find_nearest(pos)[3] if a._arbres[n].find_nearest(pos)[3] is not None else 1e9)
        r, e = rayon * getattr(a, "large_paupiere", 1.14), rayon * max(0.16, (getattr(a, "_bombe", 0.28) - 0.21) / 2.2)
        haut = (0, 0, 1) if abs(vers.z) < 0.9 else (0, -1, 0)
        rep = A.cadre(pos + vers * rayon * 0.31, vers, haut)
        suffixe = "" if paire else "_%d" % i
        calotte = A.tour(A.conges([(0, 0), (r, 0), (r, e), (r * 0.6, e * 1.9), (0, e * 2.2)], e * 0.5, 2), 28)
        a.piece("paupiere" + suffixe, calotte, getattr(a, "couleur_paupiere", None) or a._couleurs[voisine], mat=rep, poil=False, paire=paire)
        arc = [rep @ Vector((r * 0.70 * u, -r * 0.05 - r * 0.30 * (1 - u * u), e * 2.1 * (1 - 0.35 * u * u) + 0.0008)) for u in np.linspace(-1, 1, 11)]
        a.broderie("cil" + suffixe, arc, max(0.0012, rayon * 0.06), K.BRUN, paire=paire)
        ajouts.append(("paupiere" + suffixe + ("_G" if paire else ""), voisine, tuple(rep @ Vector((0, r, 0)))))
    return ajouts


# ---------------------------------------------------------------- quel os porte quelle pièce

def porter(a, porteurs):
    k = a.echelle
    for p in a._toutes():
        nom = p["nom"]
        cote = nom[-2:] if nom.endswith(("_G", "_D")) else ""
        base = nom[:-2] if cote else nom
        for entree in porteurs:
            if base.startswith(entree[0]):
                cible = entree[1]
                if callable(cible):
                    points = p["monde"] / k * ([-1, 1, 1] if cote == "_D" else [1, 1, 1])
                    p["poids"] = {o: np.asarray(w, float) for o, w in cible(points, cote).items()}
                    # un détail cousu sur une pièce souple se déforme comme elle, et se range avec elle pour la cuisson
                    force = entree[2].replace("*", cote) if len(entree) > 2 and isinstance(entree[2], str) else None
                    p["groupe"] = force or max(p["poids"], key=lambda o: p["poids"][o].sum())
                else:
                    p["os"] = cible + (cote if len(entree) > 2 and entree[2] else "")
                    p["groupe"] = p["os"]
                break
        else:
            print("[usine] aucun os pour la pièce", nom, ": elle suit « corps »", flush=True)
            p["os"] = p["groupe"] = "corps"


def volumes_libres(a):
    """Un fil brodé qui ne repose sur rien (une moustache, une antenne) n'est pas un détail à cuire : c'est un volume."""
    arbres = [G.ecorce(p["monde"], p["faces"]) for p in a._toutes() if p["genre"] == "volume"]
    seuil = 0.008 * a.echelle
    for j in a._fils.values():
        for p in j.pieces:
            pts = p["monde"][::max(1, len(p["monde"]) // 24)]
            loin = sum(1 for q in pts if min((arbre.find_nearest(Vector(q))[3] or 9.0) for arbre in arbres) > seuil)
            if loin > len(pts) * 0.5:
                p["genre"] = "volume"


# ---------------------------------------------------------------- le modèle détaillé et le maillage léger

def monter_hauts(a):
    """Le modèle détaillé, un objet par tissu, par os et par zone : « canard_t0@tete#poil »."""
    objets = []
    for casier, cle_matiere in ((a._tissus, "tissu"), (a._fils, "fil"), (a._durs, "bouton")):
        for cle, jouet in casier.items():
            matiere = a.matiere(casier, cle, jouet.nom)
            for groupe, zone in sorted({(p["groupe"], p["zone"]) for p in jouet.pieces}):
                morceau = A.Jouet("%s@%s#%s" % (jouet.nom, groupe, zone))
                morceau.pieces = [p for p in jouet.pieces if p["groupe"] == groupe and p["zone"] == zone]
                morceau.monter()
                morceau.objet["poil_k"] = min(float(p.get("poil_k", 1.0)) for p in morceau.pieces)
                morceau.habiller({cle_matiere: matiere})
                objets.append(morceau.objet)
    return objets


def monter_bas(a):
    """Le maillage du jeu : les volumes seuls, un objet par os, allégés jusqu'au budget de triangles."""
    volumes = [p for p in a._toutes() if p["genre"] == "volume"]
    triangles = sum(len(f) - 2 for p in volumes for f in p["faces"])
    part = min(1.0, TRIANGLES / triangles)
    objets = []
    for groupe in sorted({p["groupe"] for p in volumes}):
        j = A.Jouet(groupe)
        j.pieces = [dict(p, matiere="cuit") for p in volumes if p["groupe"] == groupe]
        ob = j.monter()
        if any(p.get("fusion") for p in j.pieces):           # la base fusionnée : ses pièces se soudent bord à bord
            import fusion
            fusion.souder(ob, j.pieces)
        if part < 0.98 and not groupe.startswith(epingle.OS_LIBRES):
            allege = ob.modifiers.new("allege", "DECIMATE")
            allege.ratio = part
            bpy.ops.object.select_all(action="DESELECT")
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.modifier_apply(modifier=allege.name)
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            for f in bm.faces:
                f.smooth = True
            for e in bm.edges:
                e.smooth = not (len(e.link_faces) == 2 and e.calc_face_angle(0.0) > math.radians(50))
            bm.to_mesh(ob.data)
            bm.free()
        objets.append(ob)
    print("[bas]", triangles, "triangles détaillés ->", sum(len(p.vertices) - 2 for o in objets for p in o.data.polygons), flush=True)
    return objets


def deplier(bas):
    bpy.ops.object.select_all(action="DESELECT")
    for o in bas:
        o.select_set(True)
    bpy.context.view_layer.objects.active = bas[0]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.01, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    for geste in (lambda: bpy.ops.uv.select_all(action="SELECT"), bpy.ops.uv.average_islands_scale,
                  lambda: bpy.ops.uv.pack_islands(margin=0.01, rotate=True)):
        try:
            geste()
        except Exception as e:
            print("[deplier] geste ignoré :", str(e)[:90])
    bpy.ops.object.mode_set(mode="OBJECT")


# ---------------------------------------------------------------- la cuisson

def _emission(nom, couleur):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    t = m.node_tree
    t.nodes.clear()
    e = t.nodes.new("ShaderNodeEmission")
    e.inputs[0].default_value = (*couleur, 1.0)
    t.links.new(e.outputs[0], t.nodes.new("ShaderNodeOutputMaterial").inputs[0])
    return m


ZONES = {"poil": (0.5, 0, 0), "piece": (0, 1, 0), "feutre": (0, 0, 1), "fil": (0, 0, 0), "dur": (0, 0, 0)}


def cuire(nom, bas, hauts, k):
    sc = bpy.context.scene
    monde = bpy.data.worlds.new("cuisson")
    monde.light_settings.distance = 0.12 * k
    sc.world = monde
    cuit = bpy.data.materials.new("cuit")
    cuit.use_nodes = True
    noeud = cuit.node_tree.nodes.new("ShaderNodeTexImage")
    cuit.node_tree.nodes.active = noeud
    for o in bas:
        o.data.materials.append(cuit)

    def rayons(objets, visible):
        for o in objets:
            o.visible_diffuse = o.visible_glossy = o.visible_transmission = o.visible_shadow = visible

    fonds = {"couleur": (0.9, 0.85, 0.7, 1), "relief": (0.5, 0.5, 1, 1), "rugosite": (1, 1, 1, 1), "ombre": (1, 1, 1, 1), "zones": (0, 0, 0, 1)}
    images = {}
    for n, fond in fonds.items():
        img = bpy.data.images.new("%s_%s" % (nom, n), TAILLE, TAILLE, alpha=False, is_data=(n != "couleur"))
        img.generated_color = fond
        images[n] = img

    def passe(n, genre, grains, filtre=None):
        t0 = time.time()
        noeud.image = images[n]
        sc.cycles.samples = grains
        for o in bas:
            sources = [h for h in hauts if ("@%s#" % o.name) in h.name]
            bpy.ops.object.select_all(action="DESELECT")
            for h in sources:
                h.select_set(True)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            options = dict(type=genre, use_selected_to_active=True, cage_extrusion=0.012 * k, max_ray_distance=0.035 * k,
                           margin=10, use_clear=False, normal_space="TANGENT")
            if filtre:
                options["pass_filter"] = filtre
            machine.ceder()
            souffler("la cuisson « %s »" % n, False, CUISSON_FROIDE)      # une passe fait monter la carte de sept degrés : on part de plus bas
            t1 = time.time()
            bpy.ops.object.bake(**options)
            time.sleep(0 if machine.DISTANT else min(12.0, time.time() - t1))   # elle se repose autant qu'elle vient de travailler (pas une machine louée)
        print("[cuisson]", n, round(time.time() - t0, 1), "s", flush=True)

    rayons(bas, False)
    passe("couleur", "DIFFUSE", 2, {"COLOR"})
    passe("relief", "NORMAL", 4)
    passe("rugosite", "ROUGHNESS", 2)
    anciennes = {}
    for h in hauts:
        zone = ZONES[h.name.split("#")[1]]
        marque = _emission("zone_" + h.name, (max(0.30, zone[0] * h.get("poil_k", 1.0)) if zone[0] else 0.0, zone[1], zone[2]))
        anciennes[h.name] = [s.material for s in h.material_slots]
        for s in h.material_slots:
            s.material = marque
    passe("zones", "EMIT", 1)
    for h in hauts:
        for s, m in zip(h.material_slots, anciennes[h.name]):
            s.material = m
    # l'ombre de contact se cuit sur le maillage léger lui-même, toutes ses pièces en place
    t0 = time.time()
    rayons(bas, True)
    for h in hauts:
        h.hide_render = True
    noeud.image = images["ombre"]
    sc.cycles.samples = 32
    for o in bas:
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        machine.ceder()
        souffler("la cuisson de l'ombre", False, CUISSON_FROIDE)
        t1 = time.time()
        bpy.ops.object.bake(type="AO", use_selected_to_active=False, margin=10, use_clear=False)
        time.sleep(0 if machine.DISTANT else min(12.0, time.time() - t1))
    print("[cuisson] ombre", round(time.time() - t0, 1), "s", flush=True)
    return images


def _tableau(img):
    a = np.empty(TAILLE * TAILLE * 4, np.float32)
    img.pixels.foreach_get(a)
    return (np.clip(a.reshape(TAILLE, TAILLE, 4)[::-1, :, :3], 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)


def enregistrer(nom, images):
    from PIL import Image
    dossier = os.path.join(MODELES, nom)
    os.makedirs(dossier, exist_ok=True)
    orm = np.stack([_tableau(images["ombre"])[:, :, 0], _tableau(images["rugosite"])[:, :, 0], np.zeros((TAILLE, TAILLE), np.uint8)], axis=2)
    for n, tab in (("couleur", _tableau(images["couleur"])), ("relief", _tableau(images["relief"])), ("orm", orm), ("zones", _tableau(images["zones"]))):
        Image.fromarray(tab, "RGB").save(os.path.join(dossier, "%s_%s.png" % (nom, n)), optimize=True)
    print("[textures]", dossier, flush=True)


# ---------------------------------------------------------------- les aperçus animés

def _habit_d_apercu(modele, images):
    m = bpy.data.materials.new("apercu")
    m.use_nodes = True
    t = m.node_tree
    b = t.nodes["Principled BSDF"]
    for n, entree in (("couleur", "Base Color"), ("rugosite", "Roughness")):
        tex = t.nodes.new("ShaderNodeTexImage")
        tex.image = images[n]
        t.links.new(tex.outputs[0], b.inputs[entree])
    tex = t.nodes.new("ShaderNodeTexImage")
    tex.image = images["relief"]
    carte = t.nodes.new("ShaderNodeNormalMap")
    t.links.new(tex.outputs[0], carte.inputs["Color"])
    t.links.new(carte.outputs[0], b.inputs["Normal"])
    b.inputs["Sheen Weight"].default_value = 1.0
    modele.data.materials.clear()
    modele.data.materials.append(m)


def apercus(nom, a, arm, animateur, animations, modele, images):
    """Le modèle du jeu, avec son poil, photographié image par image : une planche de poses et une image animée par animation."""
    from PIL import Image
    _habit_d_apercu(modele, images)
    poilues = [p for p in a._toutes() if p.get("poil") is not None]
    if poilues:
        couvrants = [p for p in a._toutes() if p.get("poil") is None]
        bas, haut = a.boite()
        long = K.poil_par_taille(float(max(haut - bas)))
        duvet = A.Jouet(nom + "_duvet")
        ob = duvet.monter_brins(G.duvet(poilues, couvrants, 170000, long, 0.00042 * long / 0.0055, None), M.duvet())
        ob.parent = arm
        ob.modifiers.new("Squelette", "ARMATURE").object = arm
    bas, haut = a.boite()
    K._jardin(bas, haut)
    sc = bpy.context.scene
    sc.render.engine = os.environ.get("BIBELOTS_APERCUS", "BLENDER_EEVEE_NEXT")   # sur une machine louée sans écran, le carnet peut demander CYCLES
    sc.eevee.taa_render_samples = 16
    bpy.data.lights["soleil"].energy = 2.5
    sc.view_settings.exposure = -0.55
    taille = max(haut[2] * 1.3, 0.8 * max(haut[0] - bas[0], haut[1] - bas[1]))
    centre = Vector(((bas[0] + haut[0]) * 0.5, (bas[1] + haut[1]) * 0.5, haut[2] * 0.55))
    depuis = centre + Vector((0.55, -0.80, 0.36)).normalized() * (2.7 * taille + 0.3)
    os.makedirs(APERCUS, exist_ok=True)
    # allégés le 15/10 (session Puissance, mesure sur le héron : les aperçus = 65 % du temps) : la scène n'est plus
    # resynchronisée à chaque image ; seules les 6 images de la planche gardent 640 x 360 et 16 échantillons, celles du GIF
    # sont prises à leur taille finale (480 x 270) à 8 échantillons ; une boucle longue (100 images et plus) : une sur 4.
    sc.render.use_persistent_data = True
    for n, (images_, fonction, boucle) in animations.items():
        pas = 4 if images_ >= 100 else 2
        cadres_f = list(range(0, images_ if boucle else images_ + 1, pas))
        planche_i = {int(i * (len(cadres_f) - 1) / 5) for i in range(6)}       # les mêmes 6 que « choisies »
        vues = []
        for i, f in enumerate(cadres_f):
            animateur.poser(fonction(f / images_))
            chemin = os.path.join(APERCUS, "_%s_%s_%03d.png" % (nom, n, f))
            if i in planche_i:
                A.photo(chemin, depuis, centre, 46, (640, 360), 16)
            else:
                A.photo(chemin, depuis, centre, 46, (480, 270), 8)
            vues.append(chemin)
        choisies = [vues[int(i * (len(vues) - 1) / 5)] for i in range(6)]
        planche = Image.new("RGB", (1920, 720))
        for i, c in enumerate(choisies):
            planche.paste(Image.open(c).convert("RGB"), ((i % 3) * 640, (i // 3) * 360))
        planche.save(os.path.join(APERCUS, "%s-poses-%s.png" % (nom, n)))
        cadres = [Image.open(c).convert("RGB").resize((480, 270), Image.LANCZOS).quantize(colors=128, method=Image.Quantize.MEDIANCUT) for c in vues]
        cadres = cadres * (3 if len(cadres) < 20 else 1)
        cadres[0].save(os.path.join(APERCUS, "%s-%s.gif" % (nom, n)), save_all=True, append_images=cadres[1:], duration=int(1000 * pas / 30), loop=0)
        for c in vues:
            os.remove(c)
        print("[apercu]", nom, n, flush=True)


# ---------------------------------------------------------------- la chaîne entière

def _epingles(a, module):
    """Si l'espèce est un Épinglé (son fichier définit EPINGLE), plante ses épingles et ouvre sa couture."""
    if not hasattr(module, "EPINGLE") or "sans-epingles" in sys.argv:
        return []
    return epingle.epingler(a, **module.EPINGLE)


def _os_de(a, piece):
    """L'os qui porte une pièce (pour une pièce souple : son os de rangement)."""
    for p in a._toutes():
        if p["nom"] == piece:
            return p["groupe"]
    return "corps"


def _style():
    """Le style demandé sur la ligne de commande (style=B), sinon celui de l'espèce."""
    demande = [x.split("=")[1].upper() for x in sys.argv if x.startswith("style=")]
    return demande[0] if demande else styles.style_de(sys.argv[1])


def fabriquer(nom, avec_apercus=True):
    with machine.tour("la fabrication de « %s »" % nom, 1500):
        _fabriquer(nom, avec_apercus)


def _fabriquer(nom, avec_apercus=True):
    module = importlib.import_module(nom)
    A.neuf()
    bpy.context.scene.render.fps = 30
    style = _style()
    a = styles.construire(nom, style, module)
    fondre = K.fusion_demandee(module)                         # la base fusionnée : éteinte par défaut (fusion.py)
    if fondre:
        import fusion
        fusion.symetriser(a)
    lids = paupieres(a)
    piques = _epingles(a, module)
    k = a.a_taille()
    global TAILLE                                             # un géant de 15 m en 2048 px est floue de près
    TAILLE = TAILLE_GEANT if (a.taille or 0.0) > GEANT else TAILLE_NORMALE
    porteurs = epingle.porteurs(piques) + list(module.PORTEURS) + [("paupiere", "paupiere", True), ("cil", "paupiere", True)]
    porter(a, porteurs)
    volumes_libres(a)
    groupe_de = {p["nom"]: p["groupe"] for p in a._toutes()}
    liste_os = list(module.OS) + [(n, groupe_de.get(voisine + "_G", groupe_de.get(voisine, "corps")), t) for n, voisine, t in lids]
    liste_os = tous_les_os(liste_os) + [(n, _os_de(a, piece), t) for n, piece, t in piques]
    if fondre:
        fusion.fusionner(a, K.gonflage_demande(module), getattr(module, "GONFLAGE_REGLAGES", None))
        liste_os = fusion.os_suivent(a, liste_os, k, {o[0] for o in tous_les_os(list(module.OS))})   # le gonflage déplace paupières et épingles

    hauts = monter_hauts(a)
    bas = monter_bas(a)
    deplier(bas)
    images = cuire(nom, bas, hauts, k)
    enregistrer(nom, images)
    import brut                                                # sa robe sauvage, tirée des textures qu'on vient de cuire
    brut.robe(nom)
    for h in hauts:
        bpy.data.objects.remove(h)

    bpy.ops.object.select_all(action="DESELECT")
    for o in bas:
        o.select_set(True)
    bpy.context.view_layer.objects.active = bas[0]
    bpy.ops.object.join()
    modele = bpy.context.view_layer.objects.active
    modele.name = modele.data.name = nom
    print("[maillage]", sum(len(p.vertices) - 2 for p in modele.data.polygons), "triangles,", len(liste_os), "os", flush=True)
    arm = squelette(nom, [modele], liste_os, k)
    animateur = Animateur(arm, k)
    for n, (images_, fonction, boucle) in module.ANIMATIONS.items():
        animateur.enregistrer(n, images_, fonction, boucle)
    bpy.ops.object.select_all(action="DESELECT")
    modele.select_set(True)
    arm.select_set(True)
    chemin = os.path.join(MODELES, nom, nom + ".glb")
    bpy.ops.export_scene.gltf(filepath=chemin, export_format="GLB", use_selection=True, export_animations=True,
                              export_animation_mode="NLA_TRACKS", export_force_sampling=True, export_frame_range=False,
                              export_skins=True, export_materials="PLACEHOLDER")
    retirees = epingle.nettoyer_glb(chemin) if piques else 0
    print("[export]", chemin, round(os.path.getsize(chemin) / 1e6, 2), "Mo", ("(%d pistes d'épingles retirées)" % retirees) if piques else "", flush=True)
    import json                                                # ce que le jeu doit savoir de cet animal : son style, les réglages de son poil
    ancienne = os.path.join(MODELES, nom, nom + ".json")       # les robes réglées à la main pour cette espèce survivent à une refabrication
    robes_gardees = json.load(open(ancienne, encoding="utf-8")).get("robes") if os.path.exists(ancienne) else None
    with open(os.path.join(MODELES, nom, nom + ".json"), "w", encoding="utf-8") as f:
        fiche = {"style": style, "taille": a.taille, "poil": styles.reglages(style, a.taille)}
        if robes_gardees:
            fiche["robes"] = robes_gardees
        for cle, valeur in getattr(module, "POIL", {}).items():   # une variante peut régler son poil : « longueur_x » multiplie, le reste remplace
            if cle.endswith("_x"):
                fiche["poil"][cle[:-2]] = round(fiche["poil"].get(cle[:-2], 0.0) * valeur, 4)
            else:
                fiche["poil"][cle] = valeur
        if piques:                                             # un Épinglé : les os que le jeu met à l'échelle 1 (épinglé) ou 0 (guéri)
            fiche["epingle"] = {"os": [n for n, _piece, _t in piques]}
        json.dump(fiche, f, ensure_ascii=False, indent=1)
    import marges                                              # le fond entre les îlots prend la couleur des îlots (plus de lignes claires aux coutures du dépliage)
    marges.corriger(nom)
    import robes                                               # la couleur moyenne de chaque zone : les robes gagnées (robes.gd) en ont besoin
    robes.ecrire(nom)
    if avec_apercus:
        arm.animation_data_clear()
        apercus(nom, a, arm, animateur, module.ANIMATIONS, modele, images)


def essayer(nom, lesquelles=()):
    """La répétition, en une minute : le modèle détaillé sans poil ni cuisson, son squelette, et pour chaque
    animation une planche de six poses. C'est là qu'on règle les gestes ; fabriquer() ne vient qu'à la fin."""
    with machine.tour("la répétition de « %s »" % nom, 240):
        _essayer(nom, lesquelles)


def _essayer(nom, lesquelles=()):
    from PIL import Image
    module = importlib.import_module(nom)
    A.neuf()
    a = styles.construire(nom, _style(), module)
    fondre = K.fusion_demandee(module)                         # la base fusionnée : éteinte par défaut (fusion.py)
    if fondre:
        import fusion
        fusion.symetriser(a)
    lids = paupieres(a)
    piques = _epingles(a, module)
    k = a.a_taille()
    porter(a, epingle.porteurs(piques) + list(module.PORTEURS) + [("paupiere", "paupiere", True), ("cil", "paupiere", True)])
    groupe_de = {p["nom"]: p["groupe"] for p in a._toutes()}
    liste_os = tous_les_os(list(module.OS) + [(n, groupe_de.get(voisine + "_G", groupe_de.get(voisine, "corps")), t) for n, voisine, t in lids])
    liste_os += [(n, _os_de(a, piece), t) for n, piece, t in piques]
    if fondre:
        fusion.fusionner(a, K.gonflage_demande(module), getattr(module, "GONFLAGE_REGLAGES", None))
        liste_os = fusion.os_suivent(a, liste_os, k, {o[0] for o in tous_les_os(list(module.OS))})   # le gonflage déplace paupières et épingles
    connus = {o[0] for o in liste_os}
    for p in a._toutes():
        for o in (list(p["poids"]) if p.get("poids") else [p["os"]]):
            if o not in connus:
                print("[usine] la pièce", p["nom"], "suit l'os « %s », qui n'existe pas dans OS" % o, flush=True)
    arm = squelette(nom, monter_hauts(a), liste_os, k)
    animateur = Animateur(arm, k)
    bas, haut = a.boite()
    K._jardin(bas, haut)
    sc = bpy.context.scene
    sc.render.engine = os.environ.get("BIBELOTS_APERCUS", "BLENDER_EEVEE_NEXT")   # idem (machine louée sans écran)
    sc.eevee.taa_render_samples = 16
    bpy.data.lights["soleil"].energy = 2.5
    sc.view_settings.exposure = -0.55
    taille = max(haut[2] * 1.3, 0.8 * max(haut[0] - bas[0], haut[1] - bas[1]))
    centre = Vector(((bas[0] + haut[0]) * 0.5, (bas[1] + haut[1]) * 0.5, haut[2] * 0.55))
    depuis = centre + Vector((0.55, -0.80, 0.36)).normalized() * (2.7 * taille + 0.3)
    os.makedirs(APERCUS, exist_ok=True)
    for n, (images_, fonction, boucle) in module.ANIMATIONS.items():
        if lesquelles and n not in lesquelles:
            continue
        planche = Image.new("RGB", (1920, 720))
        for i in range(6):
            animateur.poser(fonction(i / 6 if boucle else i / 5))
            chemin = os.path.join(APERCUS, "_%s_%s_essai.png" % (nom, n))
            A.photo(chemin, depuis, centre, 46, (640, 360), 16)
            planche.paste(Image.open(chemin).convert("RGB"), ((i % 3) * 640, (i // 3) * 360))
            os.remove(chemin)
        planche.save(os.path.join(APERCUS, "%s-poses-%s.png" % (nom, n)))
        print("[essai]", nom, n, flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "machine":
        os.system('"%s" "%s"' % (sys.executable, os.path.join(ICI, "machine.py")))
    elif "essai" in sys.argv:
        essayer(sys.argv[1], [x for x in sys.argv[2:] if x not in ("essai", "fusion", "sans-fusion", "gonflage", "sans-gonflage")])
    else:
        fabriquer(sys.argv[1], "sans-apercus" not in sys.argv)
