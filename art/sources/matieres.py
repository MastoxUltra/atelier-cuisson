"""Les matières, écrites comme des formules.

    g = Formule("bois")
    x, y, z = g.xyz(g.loc())
    g.sortie(couleur=g.couleur(ROUGE) * (0.9 + 0.1 * g.bruit(g.loc(), 40)), rugosite=0.3)

« loc » est la position du point dans le repère de sa pièce : les motifs restent collés à elle.
« teinte » est la couleur portée par le point (franges, herbe).
"""
import bpy


def hexa(code):
    """Une couleur d'écran (« #ff7f96 ») en couleur de lumière, celle que Blender attend."""
    code = code.lstrip("#")
    c = [int(code[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


CREME = hexa("#fff0cf")
ROSE = hexa("#ff8fa3")
CORAIL = hexa("#f4553b")
TURQUOISE = hexa("#12b8b0")
JAUNE = hexa("#ffc83a")
BRUN = hexa("#3a2416")
BOIS = hexa("#d6a66c")
BLANC = hexa("#fffaf0")
NOIR = (0.004, 0.004, 0.005)


class X:
    """Une valeur dans le graphe : un nombre, ou un vecteur / une couleur (vec = True)."""

    def __init__(self, g, prise, vec=False):
        self.g, self.s, self.vec = g, prise, vec

    def _op(self, autre, op, inverse=False):
        a, b = (autre, self) if inverse else (self, autre)
        vec = (isinstance(a, X) and a.vec) or (isinstance(b, X) and b.vec) or isinstance(a, tuple) or isinstance(b, tuple)
        return self.g.vecteur(op, a, b) if vec else self.g.nombre(op, a, b)

    def __add__(self, o): return self._op(o, "ADD")
    def __radd__(self, o): return self._op(o, "ADD", True)
    def __sub__(self, o): return self._op(o, "SUBTRACT")
    def __rsub__(self, o): return self._op(o, "SUBTRACT", True)
    def __mul__(self, o): return self._op(o, "MULTIPLY")
    def __rmul__(self, o): return self._op(o, "MULTIPLY", True)
    def __truediv__(self, o): return self._op(o, "DIVIDE")
    def __rtruediv__(self, o): return self._op(o, "DIVIDE", True)
    def __neg__(self): return self._op(-1.0, "MULTIPLY")


class Formule:
    def __init__(self, nom):
        self.mat = bpy.data.materials.new(nom)
        self.mat.use_nodes = True
        self.arbre = self.mat.node_tree
        self.arbre.nodes.clear()
        self._geo = None

    # --- la plomberie ---

    def _noeud(self, genre, **reglages):
        n = self.arbre.nodes.new(genre)
        for k, v in reglages.items():
            setattr(n, k, v)
        return n

    def _pose(self, entree, valeur):
        if valeur is None:
            return
        if isinstance(valeur, X):
            self.arbre.links.new(valeur.s, entree)
        elif isinstance(valeur, (int, float)):
            if entree.type == "VALUE":
                entree.default_value = float(valeur)
            elif entree.type == "RGBA":
                entree.default_value = (valeur, valeur, valeur, 1.0)
            else:
                entree.default_value = (valeur, valeur, valeur)
        else:
            v = tuple(valeur)
            entree.default_value = (*v[:3], 1.0) if entree.type == "RGBA" else v[:3]

    def nombre(self, op, a, b=None, c=None):
        n = self._noeud("ShaderNodeMath", operation=op)
        for i, v in enumerate((a, b, c)):
            self._pose(n.inputs[i], v)
        return X(self, n.outputs[0])

    def vecteur(self, op, a, b=None):
        n = self._noeud("ShaderNodeVectorMath", operation=op)
        self._pose(n.inputs[0], a)
        self._pose(n.inputs[1], b)
        if op in ("LENGTH", "DOT_PRODUCT", "DISTANCE"):
            return X(self, n.outputs[1])
        return X(self, n.outputs[0], True)

    # --- les sources ---

    def loc(self):
        return X(self, self._noeud("ShaderNodeAttribute", attribute_name="loc").outputs["Vector"], True)

    def teinte(self):
        return X(self, self._noeud("ShaderNodeAttribute", attribute_name="teinte").outputs["Color"], True)

    def couleur(self, c):
        n = self._noeud("ShaderNodeRGB")
        n.outputs[0].default_value = (*c, 1.0)
        return X(self, n.outputs[0], True)

    def _geometrie(self):
        if self._geo is None:
            self._geo = self._noeud("ShaderNodeNewGeometry")
        return self._geo

    def pointu(self):
        """Proche de 0,5 sur une surface lisse, plus grand sur une arête saillante."""
        return X(self, self._geometrie().outputs["Pointiness"])

    def normale(self):
        return X(self, self._geometrie().outputs["Normal"], True)

    def position(self):
        return X(self, self._geometrie().outputs["Position"], True)

    def xyz(self, v):
        n = self._noeud("ShaderNodeSeparateXYZ")
        self._pose(n.inputs[0], v)
        return X(self, n.outputs[0]), X(self, n.outputs[1]), X(self, n.outputs[2])

    def vec(self, x, y, z):
        n = self._noeud("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)):
            self._pose(n.inputs[i], v)
        return X(self, n.outputs[0], True)

    # --- les outils ---

    def bruit(self, p, echelle=5.0, detail=2.0, rugosite=0.5):
        n = self._noeud("ShaderNodeTexNoise")
        self._pose(n.inputs["Vector"], p)
        n.inputs["Scale"].default_value = echelle
        n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rugosite
        return X(self, n.outputs[0])

    def cellules(self, p, echelle=5.0):
        n = self._noeud("ShaderNodeTexVoronoi")
        self._pose(n.inputs["Vector"], p)
        n.inputs["Scale"].default_value = echelle
        return X(self, n.outputs[0])

    def lisse(self, x, a, b):
        """0 quand x vaut a, 1 quand x vaut b, en douceur entre les deux."""
        n = self._noeud("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP")
        self._pose(n.inputs["Value"], x)
        self._pose(n.inputs["From Min"], a)
        self._pose(n.inputs["From Max"], b)
        return X(self, n.outputs[0])

    def mele(self, a, b, t):
        """La couleur a, remplacée par b là où t vaut 1."""
        n = self._noeud("ShaderNodeMix", data_type="RGBA")
        n.clamp_factor = True
        prises = {s.identifier: s for s in n.inputs}
        self._pose(prises["Factor_Float"], t)
        self._pose(prises["A_Color"], a)
        self._pose(prises["B_Color"], b)
        return X(self, {s.identifier: s for s in n.outputs}["Result_Color"], True)

    def abs(self, x): return self.nombre("ABSOLUTE", x)
    def racine(self, x): return self.nombre("SQRT", x)
    def frac(self, x): return self.nombre("FRACT", x)
    def sin(self, x): return self.nombre("SINE", x)
    def cos(self, x): return self.nombre("COSINE", x)
    def angle(self, y, x): return self.nombre("ARCTAN2", y, x)
    def mini(self, a, b): return self.nombre("MINIMUM", a, b)
    def maxi(self, a, b): return self.nombre("MAXIMUM", a, b)
    def borne(self, x): return self.maxi(self.mini(x, 1.0), 0.0)
    def longueur(self, v): return self.vecteur("LENGTH", v)

    # --- la sortie ---

    def sortie(self, couleur, rugosite=0.5, metal=0.0, relief=None, force=0.4, distance=0.002, **autres):
        """autres : n'importe quelle entrée du Principled, par exemple **{"Sheen Weight": 1.0}."""
        b = self._noeud("ShaderNodeBsdfPrincipled")
        self._pose(b.inputs["Base Color"], couleur)
        self._pose(b.inputs["Roughness"], rugosite)
        self._pose(b.inputs["Metallic"], metal)
        for nom, v in autres.items():
            self._pose(b.inputs[nom], v)
        if relief is not None:
            bosse = self._noeud("ShaderNodeBump")
            bosse.inputs["Strength"].default_value = force
            bosse.inputs["Distance"].default_value = distance
            self._pose(bosse.inputs["Height"], relief)
            self.arbre.links.new(bosse.outputs[0], b.inputs["Normal"])
        s = self._noeud("ShaderNodeOutputMaterial")
        self.arbre.links.new(b.outputs[0], s.inputs["Surface"])
        return self.mat


# ---------------------------------------------------------------- le bois peint

def bois_peint(nom, peinture=None, teinte=BOIS, usure_max=1.0, brillant=1.0):
    """Du bois tourné. peinture(g, p) rend la couleur de la laque ; None laisse le bois nu, ciré.
    La laque s'écaille sur les arêtes et laisse voir le bois."""
    g = Formule(nom)
    p = g.loc()
    x, y, z = g.xyz(p)
    ondule = g.bruit(p, 7.0, 2.0)
    a, b = x + 0.013, y * 0.5 + 0.007
    cerne_ = g.frac(g.racine(a * a + b * b) * 55.0 + ondule * 3.0 + z * 3.0)
    cerne = g.lisse(cerne_, 0.0, 0.25) * g.lisse(cerne_, 1.0, 0.55)
    fibre = g.bruit(g.vec(x * 60.0, y * 60.0, z * 3.0), 1.0, 3.0)
    bois = g.couleur(teinte) * (0.72 + 0.32 * cerne) * (0.88 + 0.24 * fibre)
    if peinture is None:
        return g.sortie(bois, 0.42 + 0.2 * fibre, relief=cerne * 0.6 + fibre * 0.4, force=0.35, distance=0.0008,
                        **{"Coat Weight": 0.25, "Coat Roughness": 0.3})
    coups = g.bruit(g.vec(x * 8.0, y * 8.0, z * 45.0), 1.0, 2.0)
    laque = peinture(g, p) * (0.93 + 0.12 * coups)
    eclats = g.lisse(g.pointu(), 0.56, 0.66) * g.lisse(g.bruit(p, 55.0, 2.0), 0.40, 0.55)
    griffes = g.lisse(g.bruit(g.vec(x * 30.0, y * 30.0, z * 240.0), 1.0, 2.0), 0.76, 0.80) * g.lisse(g.bruit(p, 9.0), 0.58, 0.68)
    usure = g.borne(eclats + griffes * 0.7) * usure_max
    return g.sortie(g.mele(laque, bois, usure), 0.14 + (1.0 - brillant) * 0.4 + usure * 0.45 + coups * 0.06,
                    relief=coups * (0.12 + (1.0 - brillant)) - usure * 1.0 + cerne * usure * 0.3, force=0.5, distance=0.0012,
                    **{"Coat Weight": (1.0 - usure) * brillant, "Coat Roughness": 0.06})


def metal(nom, couleur, rugosite=0.24):
    g = Formule(nom)
    p = g.loc()
    x, y, z = g.xyz(p)
    rayures = g.bruit(g.vec(x * 400.0, y * 400.0, z * 30.0), 1.0, 2.0)
    taches = g.bruit(p, 30.0, 3.0)
    return g.sortie(g.couleur(couleur) * (0.86 + 0.2 * taches), rugosite + 0.16 * taches + 0.06 * rayures, 1.0,
                    relief=rayures, force=0.12, distance=0.0003)


def oeil_de_verre(nom, iris=hexa("#7a4a1c")):
    """Une bille de verre sombre : pupille noire, iris brun en couronne. L'axe du regard est +Z."""
    g = Formule(nom)
    p = g.loc()
    x, y, z = g.xyz(p)
    h = z / g.longueur(p)
    stries = g.bruit(g.vec(g.angle(y, x) * 9.0, h * 3.0, 0.0), 4.0, 2.0)
    couronne = g.lisse(h, 0.55, 0.68) * g.lisse(h, 0.90, 0.84)
    c = g.mele(g.couleur(NOIR), g.couleur(iris) * (0.6 + 0.9 * stries), couronne)
    return g.sortie(c, 0.03, **{"Coat Weight": 1.0, "Coat Roughness": 0.02, "Specular IOR Level": 0.8})


def oeil_dessine(nom, mat=True, pupille=0.72):
    """Un œil de dessin animé : du blanc, une grande pupille noire, un reflet. L'axe du regard est +Z."""
    g = Formule(nom)
    p = g.loc()
    x, y, z = g.xyz(p)
    r = g.longueur(p)
    h = z / r
    noir = g.lisse(h, pupille - 0.012, pupille + 0.012)
    reflet = g.lisse(g.longueur(p / r - (0.30, 0.42, 0.855)), 0.17, 0.14)
    c = g.mele(g.mele(g.couleur(BLANC), g.couleur(NOIR), noir), g.couleur((1.0, 1.0, 1.0)), reflet)
    return g.sortie(c, 0.55 if mat else 0.12, **{"Coat Weight": 0.0 if mat else 0.8})


# ---------------------------------------------------------------- le papier

def papier(nom):
    """Du papier de soie : mat, un peu translucide. Sa couleur est la teinte portée par les points."""
    g = Formule(nom)
    p = g.position()
    grain = g.bruit(p, 420.0, 3.0)
    plis = g.bruit(p, 55.0, 2.0)
    c = g.teinte() * (0.9 + 0.16 * grain)
    return g.sortie(c, 0.86, relief=grain * 0.5 + plis, force=0.45, distance=0.0012,
                    **{"Subsurface Weight": 0.35, "Subsurface Scale": 0.01, "Sheen Weight": 0.25, "Sheen Roughness": 0.6})


def papier_uni(nom, couleur, brillant=False):
    g = Formule(nom)
    grain = g.bruit(g.position(), 420.0, 3.0)
    return g.sortie(g.couleur(couleur) * (0.92 + 0.14 * grain), 0.25 if brillant else 0.8, relief=grain, force=0.3, distance=0.0006)


# ---------------------------------------------------------------- la feutrine et le fil

def feutre(nom, couleur=None):
    """De la feutrine : mate, pelucheuse, avec ses fibres en vrac.
    couleur : une couleur fixe, ou None pour prendre la teinte portée par les points."""
    g = Formule(nom)
    base = g.couleur(couleur) if couleur is not None else g.teinte()
    couleur = couleur or (0.8, 0.8, 0.8)
    p = g.position()
    fibres = g.bruit(p, 900.0, 3.0, 0.7)
    meches = g.bruit(g.vec(*[c * k for c, k in zip(g.xyz(p), (160.0, 700.0, 160.0))]), 1.0, 2.0)
    nuage = g.bruit(p, 22.0, 2.0)
    c = base * (0.82 + 0.2 * fibres + 0.1 * meches) * (0.94 + 0.12 * nuage)
    return g.sortie(c, 1.0, relief=fibres * 0.7 + meches * 0.5, force=0.9, distance=0.0009,
                    **{"Sheen Weight": 1.0, "Sheen Roughness": 0.45, "Sheen Tint": (*[min(1.0, v * 1.6 + 0.2) for v in couleur], 1.0),
                       "Specular IOR Level": 0.1})


def tissu(nom, fond, motif, genre="pois"):
    """De la feutrine imprimée : des pois ou des rayures d'une seconde couleur."""
    g = Formule(nom)
    p = g.position()
    x, y, z = g.xyz(p)
    if genre == "pois":
        dessin = g.lisse(g.cellules(p, 46.0), 0.30, 0.25)
    else:
        dessin = g.lisse(g.sin((x * 0.6 + y * 0.3 + z) * 330.0), -0.15, 0.15)
    fibres = g.bruit(p, 900.0, 3.0, 0.7)
    c = g.mele(g.couleur(fond), g.couleur(motif), dessin) * (0.84 + 0.22 * fibres)
    return g.sortie(c, 1.0, relief=fibres, force=0.8, distance=0.0008,
                    **{"Sheen Weight": 1.0, "Sheen Roughness": 0.45, "Specular IOR Level": 0.1})


def duvet(nom="duvet"):
    """Le poil d'une peluche. Sa couleur est la teinte portée par les brins."""
    g = Formule(nom)
    return g.sortie(g.teinte(), 0.9, **{"Sheen Weight": 0.7, "Sheen Roughness": 0.5, "Specular IOR Level": 0.12,
                                        "Subsurface Weight": 0.2, "Subsurface Scale": 0.004})


def fil(nom, couleur):
    g = Formule(nom)
    torsade = g.bruit(g.position(), 1500.0, 2.0)
    return g.sortie(g.couleur(couleur) * (0.8 + 0.4 * torsade), 0.75, relief=torsade, force=0.6, distance=0.0003,
                    **{"Sheen Weight": 0.6})


def bouton(nom, couleur=NOIR):
    g = Formule(nom)
    return g.sortie(g.couleur(couleur), 0.08, **{"Coat Weight": 1.0, "Coat Roughness": 0.03})


# ---------------------------------------------------------------- la pâte à modeler

def pate(nom, couleur=None):
    """De la pâte à modeler : des empreintes de doigts, de petits creux, une peau un peu cireuse.
    couleur : une couleur fixe, ou None pour prendre la teinte portée par les points."""
    g = Formule(nom)
    p = g.position()
    x, y, z = g.xyz(p)
    tord = g.bruit(p, 14.0, 2.0)
    doigts = g.sin((x * 0.6 + y * 0.5 + z * 0.9) * 2600.0 + tord * 60.0)
    zone = g.lisse(g.bruit(p, 26.0, 2.0), 0.48, 0.62)
    creux = g.bruit(p, 95.0, 2.0)
    marbre = g.bruit(p, 38.0, 3.0)
    base = g.couleur(couleur) if couleur is not None else g.teinte()
    c = base * (0.9 + 0.2 * marbre)
    return g.sortie(c, 0.42 + 0.2 * creux, relief=doigts * zone * 0.35 + creux * 0.9, force=0.5, distance=0.0012,
                    **{"Subsurface Weight": 0.35, "Subsurface Scale": 0.012, "Specular IOR Level": 0.35})


# ---------------------------------------------------------------- le studio

def gazon(nom="gazon"):
    g = Formule(nom)
    return g.sortie(g.teinte(), 0.55, **{"Subsurface Weight": 0.3, "Subsurface Scale": 0.02, "Specular IOR Level": 0.3})


def terre(nom="terre"):
    g = Formule(nom)
    p = g.position()
    motte = g.bruit(p, 3.0, 4.0)
    fin = g.bruit(p, 60.0, 3.0)
    c = g.mele(g.couleur(hexa("#2f5c1c")), g.couleur(hexa("#4d7d26")), motte) * (0.8 + 0.4 * fin)
    return g.sortie(c, 0.9, relief=fin, force=0.6, distance=0.004)
