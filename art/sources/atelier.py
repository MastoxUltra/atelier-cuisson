"""L'atelier Blender des bibelots. Tout se fait sans fenêtre.

Repère : Z vers le haut, le jouet regarde vers -Y, sa gauche est en +X.
À l'export, cela donne dans Godot un jouet qui regarde vers +Z.

Une pièce est une Maille (des points et des faces), fabriquée par un geste de menuisier :
tourner, découper, cintrer, ou sculpter une boule. Un Jouet range ses pièces, chacune
avec sa matière et l'os qui la porte.
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector
from mathutils.geometry import tessellate_polygon

TAU = math.tau


# ---------------------------------------------------------------- les courbes

def courbe(points, pas=6, fermee=False):
    """Une courbe lisse qui passe par les points donnés."""
    pts = [np.array(p, float) for p in points]
    n = len(pts)
    sortie = []
    for i in range(n if fermee else n - 1):
        p0 = pts[(i - 1) % n] if fermee else pts[max(i - 1, 0)]
        p1 = pts[i]
        p2 = pts[(i + 1) % n] if fermee else pts[min(i + 1, n - 1)]
        p3 = pts[(i + 2) % n] if fermee else pts[min(i + 2, n - 1)]
        for k in range(pas):
            t = k / pas
            sortie.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                                 + (3 * p1 - p0 - 3 * p2 + p3) * t ** 3))
    if not fermee:
        sortie.append(pts[-1])
    return np.array(sortie)


def profil(points, pas=6):
    """Profil de tour lissé : des couples (rayon, hauteur), du bas vers le haut.
    Un bout posé sur l'axe (rayon 0) donne un dôme bien rond, sans pointe."""
    pts = [np.array(p, float) for p in points]
    n = len(pts)
    avant = pts[1] * [-1, 1] if pts[0][0] == 0 else pts[0]
    apres = pts[-2] * [-1, 1] if pts[-1][0] == 0 else pts[-1]
    tous = [avant] + pts + [apres]
    sortie = []
    for i in range(1, n):
        p0, p1, p2, p3 = tous[i - 1], tous[i], tous[i + 1], tous[i + 2]
        for k in range(pas):
            t = k / pas
            sortie.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                                 + (3 * p1 - p0 - 3 * p2 + p3) * t ** 3))
    sortie.append(pts[-1])
    s = np.array(sortie)
    s[:, 0] = np.maximum(s[:, 0], 0.0)
    if pts[0][0] == 0:
        s[0, 0] = 0.0
    if pts[-1][0] == 0:
        s[-1, 0] = 0.0
    return s


def conges(points, rayon, n=5):
    """Une ligne brisée dont on arrondit les angles (les arêtes cassées du menuisier)."""
    pts = [np.array(p, float) for p in points]
    sortie = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        la, lc = np.linalg.norm(a - b), np.linalg.norm(c - b)
        if la < 1e-9 or lc < 1e-9:
            continue
        r = min(rayon, la * 0.45, lc * 0.45)
        d = b + (a - b) / la * r
        f = b + (c - b) / lc * r
        if la > r * 4.5:
            sortie.append(b + (a - b) / la * r * 2.6)
        for k in range(n + 1):
            t = k / n
            sortie.append((1 - t) ** 2 * d + 2 * t * (1 - t) * b + t * t * f)
        if lc > r * 4.5:
            sortie.append(b + (c - b) / lc * r * 2.6)
    sortie.append(pts[-1])
    return np.array(sortie)


def cercle(rayon, n=32):
    return np.array([[math.cos(TAU * i / n) * rayon, math.sin(TAU * i / n) * rayon] for i in range(n)])


def contour_engrenage(rayon, dents, creux=0.78):
    pts = []
    for i in range(dents):
        for u, r in ((0.0, creux), (0.16, creux), (0.30, 1.0), (0.70, 1.0), (0.84, creux)):
            a = TAU * (i + u) / dents
            pts.append([math.cos(a) * rayon * r, math.sin(a) * rayon * r])
    return np.array(pts)


def helice(rayon, hauteur, spires, n=64):
    t = np.linspace(0.0, 1.0, n + 1)
    a = TAU * spires * t
    return np.stack([np.cos(a) * rayon, np.sin(a) * rayon, hauteur * t], axis=1)


# ---------------------------------------------------------------- la maille

class Maille:
    """Des points et des faces. Les faces sont des listes d'indices."""

    def __init__(self, points, faces, anneaux=None):
        self.v = np.asarray(points, float).reshape(-1, 3)
        self.f = [tuple(int(i) for i in f) for f in faces]
        self.anneaux = anneaux        # pour une pièce tournée : les indices de chaque anneau, du bas vers le haut
        self.teinte = None            # une couleur par point, si la pièce en porte

    def copie(self):
        m = Maille(self.v.copy(), list(self.f), self.anneaux)
        m.teinte = None if self.teinte is None else self.teinte.copy()
        return m

    def sculpte(self, fonction):
        """fonction reçoit le tableau des points (n, 3) et rend le tableau déformé."""
        self.v = np.asarray(fonction(self.v.copy()), float)
        return self

    def etire(self, x, y=None, z=None):
        self.v = self.v * [x, x if y is None else y, x if z is None else z]
        return self

    def pose(self, pos=(0, 0, 0), rot=(0, 0, 0)):
        m = np.array(Matrix.LocRotScale(Vector(pos), Euler([math.radians(a) for a in rot]), None))
        self.v = self.v @ m[:3, :3].T + m[:3, 3]
        return self

    def __add__(self, autre):
        n = len(self.v)
        m = Maille(np.vstack([self.v, autre.v]), self.f + [tuple(i + n for i in f) for f in autre.f])
        if self.teinte is not None or autre.teinte is not None:
            a = self.teinte if self.teinte is not None else np.ones((len(self.v), 3))
            b = autre.teinte if autre.teinte is not None else np.ones((len(autre.v), 3))
            m.teinte = np.vstack([a, b])
        return m

    def peint(self, couleur):
        self.teinte = np.tile(np.asarray(couleur, float), (len(self.v), 1))
        return self

    def normales(self):
        """Une normale par point (les faces sont supposées tournées vers l'extérieur)."""
        n = np.zeros_like(self.v)
        for f in self.f:
            a, b, c = self.v[f[0]], self.v[f[1]], self.v[f[-1]]
            fn = np.cross(b - a, c - a)
            for i in f:
                n[i] += fn
        return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)


# ---------------------------------------------------------------- tourner

def tour(prof, cotes=48):
    """Pièce tournée : le profil (rayon, hauteur) tourne autour de l'axe Z."""
    points, anneaux, faces = [], [], []
    for r, z in prof:
        if r < 1e-7:
            anneaux.append([len(points)])
            points.append((0.0, 0.0, z))
        else:
            d = len(points)
            for j in range(cotes):
                a = TAU * j / cotes
                points.append((r * math.cos(a), r * math.sin(a), z))
            anneaux.append(list(range(d, d + cotes)))
    for i in range(len(anneaux) - 1):
        bas, haut = anneaux[i], anneaux[i + 1]
        if len(bas) == 1 and len(haut) == 1:
            continue
        for j in range(cotes):
            k = (j + 1) % cotes
            if len(bas) == 1:
                faces.append((bas[0], haut[k], haut[j]))
            elif len(haut) == 1:
                faces.append((bas[j], bas[k], haut[0]))
            else:
                faces.append((bas[j], bas[k], haut[k], haut[j]))
    return Maille(points, faces, anneaux)


def boule(rayon=1.0, cotes=48, anneaux=24):
    """Une boule. Sculptée ensuite, elle devient une tête, une oreille, une cuisse."""
    p = [(math.sin(math.pi * i / anneaux) * rayon, -math.cos(math.pi * i / anneaux) * rayon) for i in range(anneaux + 1)]
    p[0] = (0.0, -rayon)
    p[-1] = (0.0, rayon)
    return tour(p, cotes)


def cylindre(rayon, hauteur, casse=0.004, cotes=32, n=4):
    """Cylindre debout sur z = 0, aux arêtes cassées."""
    return tour(conges([(0, 0), (rayon, 0), (rayon, hauteur), (0, hauteur)], casse, n), cotes)


def tore(grand, petit, cotes=48, section=14):
    """Un anneau couché autour de l'axe Z."""
    points, faces = [], []
    for i in range(cotes):
        a = TAU * i / cotes
        for j in range(section):
            b = TAU * j / section
            r = grand + petit * math.cos(b)
            points.append((r * math.cos(a), r * math.sin(a), petit * math.sin(b)))
    for i in range(cotes):
        for j in range(section):
            a, b = i * section + j, ((i + 1) % cotes) * section + j
            c, d = ((i + 1) % cotes) * section + (j + 1) % section, i * section + (j + 1) % section
            faces.append((a, b, c, d))
    return Maille(points, faces)


# ---------------------------------------------------------------- découper

def decoupe(contour, epaisseur, casse=0.006, n=4, trou=0.0):
    """Pièce découpée : une silhouette dans le plan XY, de l'épaisseur voulue le long de Z,
    aux arêtes arrondies. trou > 0 perce un trou rond au centre."""
    c = np.asarray(contour, float)
    aire = 0.5 * np.sum(c[:, 0] * np.roll(c[:, 1], -1) - np.roll(c[:, 0], -1) * c[:, 1])
    if aire < 0:
        c = c[::-1]
    m = len(c)
    apres = np.roll(c, -1, axis=0) - c
    avant = c - np.roll(c, 1, axis=0)

    def normale(d):
        nrm = np.stack([d[:, 1], -d[:, 0]], axis=1)
        return nrm / np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)

    ns = normale(apres) + normale(avant)
    ns /= np.maximum(np.linalg.norm(ns, axis=1, keepdims=True), 1e-9)
    h = epaisseur * 0.5
    r = min(casse, h * 0.95)
    couches = [(h, r * 2.6)]          # un appui sur la face : le reflet de l'arête ne bave pas dessus
    for k in range(n + 1):
        a = math.pi * 0.5 * (1 - k / n)
        couches.append((h - r + r * math.sin(a), r * (1 - math.cos(a))))
    if h - r > r * 1.8:
        couches.append((h - r * 2.6, 0.0))
    couches += [(-z, d) for z, d in reversed(couches)]
    points, faces = [], []
    for z, d in couches:
        for i in range(m):
            q = c[i] - ns[i] * d
            points.append((q[0], q[1], z))
    nc = len(couches)
    for k in range(nc - 1):
        for i in range(m):
            j = (i + 1) % m
            faces.append((k * m + i, (k + 1) * m + i, (k + 1) * m + j, k * m + j))
    dernier = (nc - 1) * m
    if trou > 0.0:
        d0 = len(points)
        for z in (h, -h):
            for i in range(m):
                u = c[i] / max(np.linalg.norm(c[i]), 1e-9) * trou
                points.append((u[0], u[1], z))
        for i in range(m):
            j = (i + 1) % m
            faces.append((i, j, d0 + j, d0 + i))
            faces.append((dernier + j, dernier + i, d0 + m + i, d0 + m + j))
            faces.append((d0 + i, d0 + j, d0 + m + j, d0 + m + i))
    else:
        dessus = [Vector((points[i][0], points[i][1], 0.0)) for i in range(m)]
        for t in tessellate_polygon([dessus]):
            faces.append((t[0], t[1], t[2]))
            faces.append((dernier + t[2], dernier + t[1], dernier + t[0]))
    return Maille(points, faces)


# ---------------------------------------------------------------- cintrer

def tube(chemin, rayon, cotes=10):
    """Un fil ou un tube le long d'un chemin. rayon : un nombre, ou une fonction de 0 à 1."""
    ch = np.asarray(chemin, float)
    n = len(ch)
    points, faces = [], []
    avant = ch[1] - ch[0]
    avant /= np.linalg.norm(avant)
    haut = np.array([1.0, 0, 0]) if abs(avant[2]) > 0.9 else np.array([0, 0, 1.0])
    cote = np.cross(avant, haut)
    cote /= np.linalg.norm(cote)
    for i in range(n):
        t = ch[min(i + 1, n - 1)] - ch[max(i - 1, 0)]
        t /= np.linalg.norm(t)
        axe = np.cross(avant, t)
        s = np.linalg.norm(axe)
        if s > 1e-6:
            ang = math.atan2(s, float(np.dot(avant, t)))
            cote = np.array(Matrix.Rotation(ang, 3, Vector(axe / s)) @ Vector(cote))
        avant = t
        bi = np.cross(t, cote)
        bi /= np.linalg.norm(bi)
        r = rayon(i / (n - 1)) if callable(rayon) else rayon
        for j in range(cotes):
            a = TAU * j / cotes
            points.append(ch[i] + (cote * math.cos(a) + bi * math.sin(a)) * r)
    for i in range(n - 1):
        for j in range(cotes):
            k = (j + 1) % cotes
            faces.append((i * cotes + j, i * cotes + k, (i + 1) * cotes + k, (i + 1) * cotes + j))
    for bout, sens in ((0, -1), (n - 1, 1)):
        centre = len(points)
        t = ch[min(bout + 1, n - 1)] - ch[max(bout - 1, 0)]
        t /= np.linalg.norm(t)
        r = rayon(bout / (n - 1)) if callable(rayon) else rayon
        points.append(ch[bout] + t * sens * r * 0.6)
        for j in range(cotes):
            k = (j + 1) % cotes
            faces.append((centre, bout * cotes + j, bout * cotes + k) if sens > 0 else (centre, bout * cotes + k, bout * cotes + j))
    return Maille(points, faces)


def ressort(rayon, hauteur, spires, fil, cotes=8):
    return tube(helice(rayon, hauteur, spires, int(spires * 20)), fil, cotes)


# ---------------------------------------------------------------- les repères

def repere(pos=(0, 0, 0), rot=(0, 0, 0), ech=(1, 1, 1)):
    """Une matrice : où poser la pièce, comment la tourner (degrés), comment l'étirer."""
    return Matrix.LocRotScale(Vector(pos), Euler([math.radians(a) for a in rot]), Vector(ech))


def viser(direction):
    """Les angles (degrés) qui couchent l'axe Z d'une pièce le long d'une direction."""
    q = Vector((0, 0, 1)).rotation_difference(Vector(direction).normalized())
    return tuple(math.degrees(a) for a in q.to_euler())


def cadre(pos, avant, haut=(0, 0, 1)):
    """Une matrice dont l'axe Z regarde vers « avant » et l'axe Y monte vers « haut »."""
    z = Vector(avant).normalized()
    x = Vector(haut).cross(z).normalized()
    y = z.cross(x)
    m = Matrix.Identity(4)
    for i, axe_ in enumerate((x, y, z)):
        m[0][i], m[1][i], m[2][i] = axe_
    m[0][3], m[1][3], m[2][3] = pos
    return m


def tourne(axe, degres, v):
    """Le vecteur v tourné autour d'un axe."""
    return Matrix.Rotation(math.radians(degres), 3, Vector(axe).normalized()) @ Vector(v)


# ---------------------------------------------------------------- le jouet

class Jouet:
    """Les pièces d'un bibelot, puis sa maille unique, son squelette, ses textures."""

    def __init__(self, nom):
        self.nom = nom
        self.pieces = []
        self.os = []          # (nom, parent, tête)

    def piece(self, nom, maille, matiere, os, pos=(0, 0, 0), rot=(0, 0, 0), ech=(1, 1, 1), mat=None, _miroir=False):
        """Pose une pièce. mat : une matrice complète, à la place de pos / rot / ech."""
        m = np.array(mat if mat is not None else repere(pos, rot, ech))
        monde = maille.v @ m[:3, :3].T + m[:3, 3]
        loc = maille.v.copy()
        faces = list(maille.f)
        if _miroir:
            monde = monde * [-1, 1, 1]
            loc = loc * [-1, 1, 1]
            faces = [f[::-1] for f in faces]
        teinte = maille.teinte if maille.teinte is not None else np.ones((len(loc), 3))
        self.pieces.append({"nom": nom, "monde": monde, "loc": loc, "faces": faces, "matiere": matiere, "os": os, "teinte": teinte})

    def paire(self, nom, maille, matiere, os, pos=(0, 0, 0), rot=(0, 0, 0), ech=(1, 1, 1), mat=None):
        """La même pièce des deux côtés. On décrit celle de gauche (+X) ; « _G » devient « _D »."""
        self.piece(nom + "_G", maille, matiere, os, pos, rot, ech, mat)
        self.piece(nom + "_D", maille, matiere, os.replace("_G", "_D"), pos, rot, ech, mat, True)

    def articulation(self, nom, parent, tete, miroir=False):
        self.os.append((nom, parent, tuple(tete)))
        if miroir:
            p = parent.replace("_G", "_D") if parent else parent
            self.os.append((nom.replace("_G", "_D"), p, (-tete[0], tete[1], tete[2])))

    # --- la maille unique ---

    def monter_brins(self, maille, matiere):
        """Pour des centaines de milliers de brins (poil, herbe) : une maille directe, sans retouche."""
        me = bpy.data.meshes.new(self.nom)
        nq, nt = len(maille.quads), len(maille.tris)
        me.vertices.add(len(maille.v))
        me.vertices.foreach_set("co", maille.v.ravel())
        me.loops.add(nq * 4 + nt * 3)
        me.loops.foreach_set("vertex_index", np.concatenate([maille.quads.ravel(), maille.tris.ravel()]))
        me.polygons.add(nq + nt)
        me.polygons.foreach_set("loop_start", np.concatenate([np.arange(nq) * 4, nq * 4 + np.arange(nt) * 3]))
        me.polygons.foreach_set("loop_total", np.concatenate([np.full(nq, 4), np.full(nt, 3)]))
        me.polygons.foreach_set("use_smooth", np.ones(nq + nt, dtype=bool))
        me.update(calc_edges=True)
        c = me.color_attributes.new("teinte", "FLOAT_COLOR", "POINT")
        c.data.foreach_set("color", np.hstack([maille.teinte, np.ones((len(maille.teinte), 1))]).ravel())
        me.materials.append(matiere)
        ob = bpy.data.objects.new(self.nom, me)
        bpy.context.scene.collection.objects.link(ob)
        for nom, w in (getattr(maille, "poids", None) or {}).items():
            groupe = ob.vertex_groups.new(name=nom)
            w = np.round(np.asarray(w) * 10) / 10
            for niveau in np.unique(w):
                if niveau > 0:
                    groupe.add(np.nonzero(w == niveau)[0].tolist(), float(niveau), "REPLACE")
        self.objet = ob
        return ob

    def monter(self):
        points, faces, loc, mat_de_face, groupes = [], [], [], [], {}
        self.matieres = []
        for p in self.pieces:
            d = sum(len(a) for a in points)
            points.append(p["monde"])
            loc.append(p["loc"])
            faces += [tuple(i + d for i in f) for f in p["faces"]]
            if p["matiere"] not in self.matieres:
                self.matieres.append(p["matiere"])
            mat_de_face += [self.matieres.index(p["matiere"])] * len(p["faces"])
            # « poids » : {os: un poids par point}, pour une pièce souple ; sinon la pièce suit un seul os
            for os_, w in (p.get("poids") or {p["os"]: None}).items():
                groupes.setdefault(os_, []).append((d, len(p["monde"]), w))
        points = np.vstack(points)
        me = bpy.data.meshes.new(self.nom)
        me.from_pydata(points.tolist(), [], faces)
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f in bm.faces:
            f.smooth = True
        for e in bm.edges:
            if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > math.radians(42):
                e.smooth = False
        bm.to_mesh(me)
        bm.free()
        a = me.attributes.new("loc", "FLOAT_VECTOR", "POINT")
        a.data.foreach_set("vector", np.vstack(loc).ravel())
        t = np.vstack([p["teinte"] for p in self.pieces])
        c = me.color_attributes.new("teinte", "FLOAT_COLOR", "POINT")
        c.data.foreach_set("color", np.hstack([t, np.ones((len(t), 1))]).ravel())
        me.polygons.foreach_set("material_index", mat_de_face)
        ob = bpy.data.objects.new(self.nom, me)
        bpy.context.scene.collection.objects.link(ob)
        for nom, morceaux in groupes.items():
            groupe = ob.vertex_groups.new(name=nom)
            for d, n, w in morceaux:
                if w is None:
                    groupe.add(list(range(d, d + n)), 1.0, "REPLACE")
                    continue
                w = np.round(np.asarray(w) * 50) / 50
                for niveau in np.unique(w):
                    if niveau > 0:
                        groupe.add((d + np.nonzero(w == niveau)[0]).tolist(), float(niveau), "REPLACE")
        self.objet = ob
        return ob

    def habiller(self, matieres):
        """Donne à chaque nom de matière la matière Blender du dictionnaire."""
        for nom in self.matieres:
            self.objet.data.materials.append(matieres[nom])


# ---------------------------------------------------------------- la scène et les photos

def neuf():
    try:      # priorité basse : la machine sert à autre chose pendant ce temps
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
    except Exception:
        pass
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    choix = os.environ.get("BIBELOTS_GPU", "OPTIX")      # OPTIX ici ; sur une machine louée (art/distant/), le carnet peut demander CUDA
    try:
        prefs.compute_device_type = choix
        prefs.get_devices()
        for d in prefs.devices:
            d.use = d.type == choix
        sc.cycles.device = "GPU"
        if os.environ.get("BIBELOTS_DISTANT") == "1":
            print("[atelier] Cycles sur", choix, [d.name for d in prefs.devices if d.use] or "(aucune carte : CPU)", flush=True)
    except Exception:
        sc.cycles.device = "CPU"
    return sc


def _principled(nom, couleur, rugosite=0.5, metal=0.0):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*couleur, 1.0)
    b.inputs["Roughness"].default_value = rugosite
    b.inputs["Metallic"].default_value = metal
    return m


def studio(sol=(0.42, 0.62, 0.25)):
    """Un coin de jardin pour les photos : un sol, un soleil chaud, un ciel doux."""
    sc = bpy.context.scene
    monde = bpy.data.worlds.new("ciel")
    monde.use_nodes = True
    fond = monde.node_tree.nodes["Background"]
    fond.inputs[0].default_value = (0.62, 0.78, 1.0, 1.0)
    fond.inputs[1].default_value = 0.9
    sc.world = monde
    me = bpy.data.meshes.new("sol")
    me.from_pydata([(-30, -30, 0), (30, -30, 0), (30, 30, 0), (-30, 30, 0)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new("sol", me)
    sc.collection.objects.link(ob)
    me.materials.append(_principled("sol", sol, 0.9))
    for nom, energie, angle, rot, teinte in (("soleil", 3.6, 6.0, (48, 0, 38), (1.0, 0.93, 0.80)),
                                             ("contre", 1.1, 20.0, (62, 0, -150), (0.75, 0.86, 1.0))):
        l = bpy.data.lights.new(nom, "SUN")
        l.energy = energie
        l.angle = math.radians(angle)
        l.color = teinte
        o = bpy.data.objects.new(nom, l)
        o.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(o)
    sc.view_settings.view_transform = "Khronos PBR Neutral"
    return ob


def photo(chemin, depuis, vers, focale=60.0, taille=(1280, 720), grains=96, net=None, ouverture=4.0):
    """net : le point sur lequel faire la mise au point (le reste devient flou)."""
    sc = bpy.context.scene
    cam = bpy.data.objects.get("appareil")
    if cam is None:
        cam = bpy.data.objects.new("appareil", bpy.data.cameras.new("appareil"))
        sc.collection.objects.link(cam)
        sc.camera = cam
    cam.data.lens = focale
    cam.data.dof.use_dof = net is not None
    if net is not None:
        cam.data.dof.focus_distance = (Vector(net) - Vector(depuis)).length
        cam.data.dof.aperture_fstop = ouverture
    cam.location = depuis
    cam.rotation_euler = (Vector(vers) - Vector(depuis)).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = taille
    sc.cycles.samples = grains
    sc.cycles.use_denoising = True
    sc.render.filepath = chemin
    bpy.ops.render.render(write_still=True)
    print("[photo]", os.path.basename(chemin))
