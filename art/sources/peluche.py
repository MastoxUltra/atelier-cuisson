"""Le kit de peluche : de quoi fabriquer un animal en peu de lignes, toujours dans le même style.

Un animal est une fonction qui rend un Animal ; planche() le monte, le photographie dans le jardin
et range sa fiche dans art/apercus/animaux/<nom>.png. Mode d'emploi et règles de style : GUIDE.md.

Repère : Z vers le haut, l'animal regarde vers -Y, sa gauche est en +X. Les mesures sont en mètres.
"""
import math
import os
import sys

import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import atelier as A
import garnitures as G
import matieres as M

FICHES = os.path.normpath(os.path.join(ICI, "..", "apercus", "animaux"))

# ---------------------------------------------------------------- la palette commune

CREME, ROSE, CORAIL, TURQUOISE, JAUNE, BLANC, BRUN, NOIR = M.CREME, M.ROSE, M.CORAIL, M.TURQUOISE, M.JAUNE, M.BLANC, M.BRUN, M.NOIR
LILAS = M.hexa("#b7a2f4")
CIEL = M.hexa("#8fc9f2")
MARINE = M.hexa("#2f4f8f")
MENTHE = M.hexa("#8fe0c0")
MOUTARDE = M.hexa("#e3a92b")
ROUX = M.hexa("#e8742c")
CARAMEL = M.hexa("#c7854a")
CHOCOLAT = M.hexa("#6b4226")
GRIS = M.hexa("#a9aab3")
ARDOISE = M.hexa("#5b6170")
PRUNE = M.hexa("#8a4a8f")
FRAMBOISE = M.hexa("#d8436f")
PECHE = M.hexa("#ffc09a")
SABLE = M.hexa("#e9d3a6")
OLIVE = M.hexa("#9aa14a")


# ---------------------------------------------------------------- de petits outils de sculpture

def lisse(t):
    """0 avant 0, 1 après 1, en douceur entre les deux (marche sur un tableau)."""
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def emousse(v, e):
    """Rend une boule plus carrée (e < 1) : des bouts francs, des flancs droits."""
    rho = np.hypot(v[:, 0], v[:, 1])
    k = np.where(rho > 1e-9, rho ** e / np.maximum(rho, 1e-9), 0.0)
    s = v.copy()
    s[:, 0] *= k
    s[:, 1] *= k
    s[:, 2] = np.sign(v[:, 2]) * np.abs(v[:, 2]) ** e
    return s


def bosse(v, direction, hauteur, largeur=0.3):
    """Gonfle une boule unité dans une direction (une joue, un front, un jabot). À utiliser dans sculpte()."""
    u = v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)
    c = np.asarray(direction, float)
    c = c / np.linalg.norm(c)
    return v * (1 + hauteur * np.exp(-np.sum((u - c) ** 2, axis=1) / largeur))[:, None]


def bandes(maille, paliers, axe=2):
    """Peint une maille par tranches le long d'un axe (0 = X, 1 = Y, 2 = Z de la pièce, avant de la poser) :
    bandes(queue, [(0.25, K.ROUX), (9, K.CREME)]) -> roux jusqu'à 0,25 m, crème au-delà.
    À poser ensuite avec couleur=None : le tissu et le poil prennent ces teintes."""
    t = np.zeros((len(maille.v), 3))
    reste = np.ones(len(maille.v), bool)
    for seuil, couleur in paliers:
        ici = reste & (maille.v[:, axe] <= seuil)
        t[ici] = couleur
        reste &= ~ici
    t[reste] = paliers[-1][1]
    maille.teinte = t
    return maille


def plie(z0, degres, zone=0.06):
    """Pour sculpte() : au-dessus de z0, la pièce bascule vers l'avant (une oreille qui retombe)."""
    def f(v):
        s = v.copy()
        h = v[:, 2] - z0
        t = np.clip(h / zone, 0.0, 1.0)
        a = np.radians(degres) * t * t * (3 - 2 * t)
        dessus = h > 0
        s[dessus, 1] = (v[:, 1] * np.cos(a) - h * np.sin(a))[dessus]
        s[dessus, 2] = z0 + (v[:, 1] * np.sin(a) + h * np.cos(a))[dessus]
        return s
    return f


def _monde(m, rep):
    r = np.array(rep)
    return m.v @ r[:3, :3].T + r[:3, 3]


def _ligne(m, rep, cote, debut, fin):
    r = np.array(rep)
    anneaux = [a for a in m.anneaux if len(a) > 1]
    i0, i1 = min(int(len(anneaux) * debut), len(anneaux) - 1), int(len(anneaux) * fin)
    idx = [anneaux[i][cote % len(anneaux[i])] for i in range(i0, i1, 1 if i1 >= i0 else -1)]
    return (m.v[idx] @ r[:3, :3].T + r[:3, 3]), (m.normales()[idx] @ r[:3, :3].T)


def _tour(m, rep, fraction):
    r = np.array(rep)
    anneaux = [a for a in m.anneaux if len(a) > 1]
    a = anneaux[min(int(len(anneaux) * fraction), len(anneaux) - 1)]
    idx = list(a) + [a[0]]
    return (m.v[idx] @ r[:3, :3].T + r[:3, 3]), (m.normales()[idx] @ r[:3, :3].T)



def poil_par_taille(mesure):
    """La longueur du duvet (en mètres) d'un animal dont la plus grande mesure est « mesure » : elle suit la taille jusqu'à
    6 mm (vers 0,76 m), puis grandit comme sa racine carrée, pour que les géants à leur vraie taille aient un poil « entre
    les deux » (l'auteur, 15/10/2026) : environ 1,3 cm pour 3,5 m, 2,5 cm au plus (un géant de 15 m). Les animaux déjà
    faits, sous 0,76 m, ne changent pas."""
    lineaire = 0.0055 * mesure / 0.7
    if lineaire <= 0.0060:
        return float(max(0.0028, lineaire))
    return float(min(0.025, 0.0060 * (mesure / (0.7 * 0.0060 / 0.0055)) ** 0.5))

class Fil:
    """Un chemin lissé : de quoi coucher une pièce tournée le long d'un cou en S, d'une queue, d'un corps de serpent.
        fil = K.Fil([(0, 0, 0.2), (0, -0.1, 0.4), (0, -0.05, 0.6)], flanc=(1, 0, 0))
        cou = A.tour(profil, 32).sculpte(fil.couche)       # la pièce garde ses anneaux : coutures et rustines marchent dessus
    flanc : la direction du côté gauche de la pièce (d'équerre avec le plan où le chemin se tient).
    haut : pour un corps couché au sol qui tourne dans tous les sens (un serpent, une anguille en boucles), la direction du
    dessus : le repère est refait en chaque point, la nuque toujours vers « haut », le flanc d'équerre (16/10 : avec un flanc
    fixe, là où le chemin passait par le flanc, la nuque tombait à zéro et le tube s'écrasait en ruban tordu, le ventre
    clair tournant autour du corps). Sans « haut », rien ne change ; là où le chemin monte droit vers « haut », le flanc
    fixe reprend la main."""

    def __init__(self, points, flanc=(1, 0, 0), pas=8, haut=None):
        self.p = A.courbe(points, pas)
        self.fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(self.p, axis=0), axis=1))])
        self.sens = np.gradient(self.p, self.fait, axis=0)
        self.long = float(self.fait[-1])
        self.flanc = np.asarray(flanc, float) / np.linalg.norm(flanc)
        self.haut = None if haut is None else np.asarray(haut, float) / np.linalg.norm(haut)
        self.nuques = None
        if self.haut is not None:                                    # un repère à rotation minimale, parti de la nuque vers « haut »
            t = self.sens / np.maximum(np.linalg.norm(self.sens, axis=1, keepdims=True), 1e-12)
            n0 = self.haut - (t[0] @ self.haut) * t[0]
            if np.linalg.norm(n0) < 1e-3:
                n0 = np.cross(t[0], self.flanc)
            r = np.zeros_like(t)
            r[0] = n0 / np.linalg.norm(n0)
            for i in range(len(t) - 1):                              # la double réflexion (Wang et al.) : pas de torsion
                v1 = self.p[i + 1] - self.p[i]
                c1 = float(v1 @ v1)
                if c1 < 1e-18:
                    r[i + 1] = r[i]
                    continue
                rl = r[i] - (2.0 / c1) * (v1 @ r[i]) * v1
                tl = t[i] - (2.0 / c1) * (v1 @ t[i]) * v1
                v2 = t[i + 1] - tl
                c2 = float(v2 @ v2)
                r[i + 1] = rl - (2.0 / c2) * (v2 @ rl) * v2 if c2 > 1e-18 else rl
            # le bout (une tête) finit le dessus vers « haut » : un cou qui monte en reculant puis se recourbe arrivait tête en
            # bas ; la torsion qui manque est répartie le long de la partie qui se dresse (contrôle à sec du 16/10)
            fin = self.haut - (t[-1] @ self.haut) * t[-1]
            if np.linalg.norm(fin) > 1e-3:
                fin = fin / np.linalg.norm(fin)
                phi = math.atan2(float(np.cross(r[-1], fin) @ t[-1]), float(r[-1] @ fin))
                couche_ = np.abs(t @ self.haut) < 0.30                # couché au sol (ou presque)
                dresses = np.nonzero(~couche_)[0]
                debut = 0
                if len(dresses):                                     # le début de la dernière partie dressée
                    avant_ = np.nonzero(couche_[:dresses[-1]])[0]
                    debut = int(avant_[-1]) if len(avant_) else 0
                s_a, s_b = self.fait[debut], self.fait[-1]
                if abs(phi) > 1e-3 and s_b > s_a:
                    th = phi * np.clip((self.fait - s_a) / (s_b - s_a), 0.0, 1.0)
                    tr = np.cross(t, r)
                    r = r * np.cos(th)[:, None] + tr * np.sin(th)[:, None]
            self.nuques = r

    def _repere(self, s):
        """(centre, avant, nuque, flanc) à s mètres de la base."""
        centre = np.stack([np.interp(s, self.fait, self.p[:, k]) for k in range(3)], axis=-1)
        avant = np.stack([np.interp(s, self.fait, self.sens[:, k]) for k in range(3)], axis=-1)
        avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
        if self.nuques is None:
            return centre, avant, np.cross(avant, self.flanc), np.broadcast_to(self.flanc, np.shape(avant)).copy()
        nuque = np.stack([np.interp(s, self.fait, self.nuques[:, k]) for k in range(3)], axis=-1)
        nuque = nuque - np.sum(nuque * avant, axis=-1, keepdims=True) * avant
        nuque = nuque / np.maximum(np.linalg.norm(nuque, axis=-1, keepdims=True), 1e-12)
        return centre, avant, nuque, np.cross(nuque, avant)

    def cadre(self, s):
        """À s mètres de la base : le centre du fil, la direction où il va, et sa nuque (le dessus)."""
        centre, avant, nuque, _f = self._repere(s)
        return centre, avant, nuque

    def couche(self, v):
        """Pour sculpte() : couche une pièce tournée toute droite (son axe Z) le long du fil. Son +X devient le flanc, son +Y la nuque."""
        s = np.clip(v[:, 2], 0.0, self.long)
        centre, avant, nuque, flanc = self._repere(s)
        return centre + avant * (v[:, 2] - s)[:, None] + v[:, 0:1] * flanc + v[:, 1:2] * nuque

    def vise(self, s, devant, cote, haut):
        """Depuis le centre du fil à la hauteur s : ce centre, et une direction (vers l'avant, vers le flanc, vers la nuque).
        Pour a.surface(), a.rustine(), a.oeil() sur une pièce couchée."""
        centre, avant, nuque, flanc = self._repere(s)
        return Vector(centre), Vector(avant * devant + flanc * cote + nuque * haut)


def tube_peint(chemin, rayon, paliers, cotes=12):
    """Un tube peint par tronçons le long de son chemin : une patte à chaussette, une antenne à bout clair, une queue baguée.
    paliers = [(fraction du chemin, couleur), ...], la dernière fraction à 1 ou plus. À poser avec couleur=None.
    Le chemin est recoupé tous les 4 mm pour que la limite des couleurs reste nette."""
    ch = np.asarray(chemin, float)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(ch, axis=0), axis=1))])
    t = np.linspace(0.0, 1.0, max(6, int(fait[-1] / 0.004)))
    ch = np.stack([np.interp(t * fait[-1], fait, ch[:, k]) for k in range(3)], axis=1)
    m = A.tube(ch, rayon, cotes)
    t = np.concatenate([np.repeat(t, cotes), [0.0, 1.0]])           # les anneaux du tube, puis ses deux bouchons
    m.teinte = np.zeros((len(t), 3))
    for seuil, couleur in reversed(paliers):
        m.teinte[t <= seuil] = couleur
    return m


def paupiere(rayon, coupe=0.3):
    """Une lourde paupière de feutrine, qui coiffe le haut d'un œil de ce rayon : l'air blasé, sévère ou endormi.
    coupe : la hauteur de son bord au-dessus du milieu de l'œil, en rayons (0 = l'œil à moitié fermé).
    À poser dans le repère de l'œil (A.cadre(pos, vers, haut)), sous un nom qui commence par « lourde » :
    le mot « paupiere » est réservé aux paupières qui clignent, ajoutées par l'usine."""
    def f(v):
        s = v * [1.30 * rayon, 1.30 * rayon, 0.62 * rayon]
        s[:, 1] = np.maximum(s[:, 1], coupe * rayon)
        return s
    return A.boule(1.0, 32, 16).sculpte(f)


# ---------------------------------------------------------------- l'animal

class Animal:
    """Les pièces d'une peluche, rangées par tissu. Voir GUIDE.md."""

    def __init__(self, nom):
        self.nom = nom
        self.tete = None           # le point à viser pour le gros plan : l'AVANT du visage (un Vector)
        self.poil_long = None      # la longueur du poil en mètres ; par défaut elle suit la taille de l'animal
        self.taille = None         # sa plus grande dimension dans le jeu, en mètres (voir le tableau du guide)
        self._tissus, self._fils, self._durs = {}, {}, {}
        self._formes, self._arbres = {}, {}
        self._couleurs, self._boutons = {}, []      # pour l'usine : la couleur de chaque pièce, les boutons posés
        self.echelle = 1.0                          # le facteur appliqué par a_taille()

    def _jouet(self, casier, cle, lettre):
        if cle not in casier:
            casier[cle] = A.Jouet("%s_%s%d" % (self.nom, lettre, len(casier)))
        return casier[cle]

    def _poser(self, jouet, nom, maille, matiere, mat, paire, genre="detail", zone="fil"):
        """genre : « volume » (une forme du maillage du jeu) ou « detail » (cuit dans la texture).
        zone : « poil », « feutre » (tissu ras), « piece » (rapiéçage), « fil » ou « dur »."""
        avant = len(jouet.pieces)
        (jouet.paire if paire else jouet.piece)(nom, maille, matiere, "x", mat=mat)
        for p in jouet.pieces[avant:]:
            p["genre"], p["zone"] = genre, zone
        return jouet.pieces[avant:]

    def piece(self, nom, maille, couleur, pos=(0, 0, 0), rot=(0, 0, 0), mat=None, poil=True, paire=False, motif=None):
        """Une pièce de tissu. couleur : une couleur de la palette, ou None si la maille porte sa teinte.
        poil : la peluche à poil court (True) ou la feutrine rase (False).
        paire : la même en miroir de l'autre côté (on décrit celle de gauche, en +X).
        motif : ("pois", couleur) ou ("rayures", couleur) pour un tissu imprimé (sans poil)."""
        rep = mat if mat is not None else A.repere(pos, rot)
        for p in self._poser(self._jouet(self._tissus, (couleur, motif), "t"), nom, maille, "tissu", rep, paire, "volume", "feutre"):
            if poil and motif is None:
                p["poil"] = couleur if couleur is not None else ("teinte" if maille.teinte is not None else None)
            else:
                p["poil"] = None
            p["zone"] = "poil" if p["poil"] is not None else "feutre"
        self._couleurs[nom] = couleur if couleur is not None else (tuple(maille.teinte.mean(axis=0)) if maille.teinte is not None else CREME)
        self._formes[nom] = (maille, rep)
        self._arbres[nom] = G.ecorce(_monde(maille, rep), maille.f)
        return maille

    def surface(self, sur, centre, direction):
        """Le point de la surface de « sur » visé depuis « centre » (dans la pièce) dans une direction, et sa normale :
        point, normale = a.surface("tete", TETE, (0.6, -0.6, 0.3)) ; puis a.bouton("oeil", point, normale, ...)."""
        p, n, _i, _d = self._arbres[sur].ray_cast(Vector(centre), Vector(direction).normalized())
        if p is None:
            raise ValueError("Rien dans cette direction depuis ce centre sur la pièce " + sur)
        return p, n

    def rustine(self, nom, sur, centre, axe, ouverture, couleur, epaisseur=0.003, feston=18, fil=JAUNE, paire=False, motif=None):
        """Un morceau de feutrine cousu sur la pièce « sur ». Depuis « centre » (un point À L'INTÉRIEUR de la
        pièce), on regarde le long de « axe » : le morceau couvre ce qu'on voit dans un cône d'« ouverture »
        radians (un nombre, ou une fonction de l'angle pour une forme non ronde).
        feston : le nombre de points de couture autour (0 = pas de couture)."""
        forme = ouverture if callable(ouverture) else (lambda th: ouverture)
        arbre = self._arbres[sur]
        for p in self._poser(self._jouet(self._tissus, (couleur, motif), "t"), nom,
                             G.rustine(arbre, Vector(centre), axe, forme, epaisseur, 7, 48), "tissu", None, paire, "detail", "piece"):
            p["poil"] = None
        if feston:
            self._poser(self._jouet(self._fils, fil, "f"), nom, G.surjet(arbre, Vector(centre), axe, forme, feston, epaisseur, 0.0014), "fil", None, paire)

    def couture(self, nom, sur, cote, debut=0.1, fin=0.9, style="biais", fil=CARAMEL, paire=False, large=0.009, haut=0.0045, pas=0.014):
        """Une couture d'assemblage le long d'une pièce tournée (A.tour ou A.boule) : « cote » est le numéro du
        méridien (0 = +X de la pièce, un quart des côtés = +Y, etc.), debut et fin vont de 0 à 1 le long de la pièce.
        style : « biais », « croix » ou « droit ». large, haut, pas : la taille des points, leur hauteur au-dessus
        du tissu et leur écart ; sur une feutrine sans poil ou un petit animal, prendre plus petit (haut=0.0015)."""
        m, rep = self._formes[sur]
        self._poser(self._jouet(self._fils, fil, "f"), nom,
                    G.piqure(*_ligne(m, rep, cote, debut, fin), pas=pas, large=large, fil=min(0.0014, large * 0.16), haut=haut, style=style), "fil", None, paire)

    def ourlet(self, nom, sur, fraction, fil=CARAMEL, paire=False, haut=0.004, pas=0.012):
        """Un point avant tout autour d'une pièce tournée, à la hauteur « fraction » (0 à 1) : le tour d'un pied.
        haut : la hauteur du fil au-dessus du tissu (0.0015 sur une feutrine sans poil)."""
        m, rep = self._formes[sur]
        self._poser(self._jouet(self._fils, fil, "f"), nom, G.couture(*_tour(m, rep, fraction), pas, pas * 0.58, 0.0015, haut), "fil", None, paire)

    def bouton(self, nom, pos, vers, rayon=0.03, couleur=NOIR, fil=JAUNE, paire=False):
        """Un bouton cousu (un œil, une attache). pos : son centre, posé sur la surface ; vers : la direction qu'il regarde."""
        r = rayon
        b = A.tour(A.conges([(0, r * 0.11), (r * 0.61, r * 0.11), (r * 0.72, 0.0), (r, 0.0), (r, r * 0.28), (r * 0.75, r * 0.28),
                             (r * 0.64, r * 0.17), (0, r * 0.17)], min(0.0015, r * 0.05), 3), 36)
        rep = A.repere(Vector(pos), A.viser(vers))
        self._poser(self._jouet(self._durs, couleur, "d"), nom, b, "bouton", rep, paire, "volume", "dur")
        self._boutons.append((nom, Vector(pos), Vector(vers).normalized(), rayon, paire))
        e, h, f = r * 0.30, r * 0.19, max(0.0011, r * 0.045)
        croix = A.tube([(-e, -e, h), (0, 0, h + f), (e, e, h)], f, 6) + A.tube([(-e, e, h), (0, 0, h + f * 1.6), (e, -e, h)], f, 6)
        self._poser(self._jouet(self._fils, fil, "f"), nom, croix, "fil", rep, paire)

    def oeil(self, nom, pos, vers, rayon=0.03, paire=False):
        """Un œil vivant, en feutrine : une pastille noire mate et son reflet blanc, du même côté pour les deux yeux.
        À mettre à la place d'un bouton quand l'animal doit avoir le regard doux (les boutons à croix peuvent inquiéter).
        pos : son centre, posé sur la surface ; vers : la direction qu'il regarde. L'usine lui pose une paupière."""
        self._boutons.append((nom, Vector(pos), Vector(vers).normalized(), rayon, paire))
        r = rayon * 1.15
        for suffixe, cote in ((("_G", 1), ("_D", -1)) if paire else (("", 1),)):
            p, v = Vector((cote * pos[0], pos[1], pos[2])), Vector((cote * vers[0], vers[1], vers[2]))
            rep = A.cadre(p, v)
            reflet = (nom[:-2] + "_reflet" + nom[-2:]) if nom.endswith(("_G", "_D")) else nom + "_reflet" + suffixe
            for nom_, maille, teinte in ((nom + suffixe, A.boule(1.0, 28, 12).etire(r, r, r * 0.16), NOIR),
                                         (reflet, A.boule(1.0, 16, 8).etire(r * 0.30, r * 0.30, r * 0.09).pose((r * 0.34, r * 0.34, r * 0.15)), BLANC)):
                for q in self._poser(self._jouet(self._tissus, (teinte, None), "t"), nom_, maille, "tissu", rep, False, "volume", "dur"):
                    q["poil"] = None

    def trace(self, sur, centre, directions, decolle=0.004):
        """Les points de la surface de « sur » visés depuis « centre » dans chaque direction : pour broder dessus.
        decolle : la hauteur du fil au-dessus du tissu (4 mm pour passer au-dessus du poil, 1 mm sur une feutrine rase)."""
        points = []
        for d in directions:
            p, n, _i, _d = self._arbres[sur].ray_cast(Vector(centre), Vector(d).normalized())
            if p is not None:
                points.append(p + n * decolle)
        return points

    def broderie(self, nom, points, rayon=0.0018, couleur=BRUN, paire=False):
        """Un fil brodé qui passe par les points donnés (une bouche, une moustache, une griffe)."""
        self._poser(self._jouet(self._fils, couleur, "f"), nom, A.tube(points, rayon, 6), "fil", None, paire)

    # --- le montage et les mesures ---

    def _toutes(self):
        return [p for casier in (self._tissus, self._fils, self._durs) for j in casier.values() for p in j.pieces]

    def boite(self):
        pts = np.vstack([p["monde"] for p in self._toutes()])
        return pts.min(axis=0), pts.max(axis=0)

    def a_taille(self):
        """Met l'animal à sa taille de jeu, les pieds toujours au sol. Rend le facteur appliqué."""
        if self.taille and self.echelle == 1.0:
            bas, haut = self.boite()
            self.echelle = self.taille / float(max(haut - bas))
            for p in self._toutes():
                p["monde"] = p["monde"] * self.echelle
            if self.tete is not None:
                self.tete = Vector(self.tete) * self.echelle
        return self.echelle

    def matiere(self, casier, cle, nom):
        """La matière Blender d'un tissu, d'un fil ou d'un bouton de cet animal."""
        if casier is self._tissus:
            return M.tissu(nom, cle[0], cle[1][1], cle[1][0]) if cle[1] else M.feutre(nom, cle[0])
        return M.fil(nom, cle) if casier is self._fils else M.bouton(nom, cle)

    def monter(self, brins=None):
        self.a_taille()
        poilues = [p for j in self._tissus.values() for p in j.pieces if p.get("poil") is not None]
        if poilues and brins != 0:
            aire = 0.0
            for p in poilues:
                v = p["monde"]
                for f in p["faces"]:
                    for k in range(1, len(f) - 1):
                        aire += 0.5 * np.linalg.norm(np.cross(v[f[k]] - v[f[0]], v[f[k + 1]] - v[f[0]]))
            bas, haut = self.boite()
            long = self.poil_long or poil_par_taille(float(max(haut - bas)))
            nombre = brins or int(min(520000, max(60000, 620000 * aire * (0.0055 / long) ** 1.5)))
            couvrants = [p for p in self._toutes() if p.get("poil") is None]
            A.Jouet(self.nom + "_duvet").monter_brins(G.duvet(poilues, couvrants, nombre, long, 0.00036 * long / 0.0055, None), M.duvet())
        for (couleur, motif), j in self._tissus.items():
            j.monter()
            if motif:
                j.habiller({"tissu": M.tissu(j.nom, couleur, motif[1], motif[0])})
            else:
                j.habiller({"tissu": M.feutre(j.nom, couleur)})
        for couleur, j in self._fils.items():
            j.monter()
            j.habiller({"fil": M.fil(j.nom, couleur)})
        for couleur, j in self._durs.items():
            j.monter()
            j.habiller({"bouton": M.bouton(j.nom, couleur)})


# ---------------------------------------------------------------- la fiche

def _jardin(bas, haut):
    A.studio()
    bpy.data.objects["sol"].data.materials.clear()
    bpy.data.objects["sol"].data.materials.append(M.terre())
    bpy.data.objects["soleil"].rotation_euler = [math.radians(a) for a in (50, 0, 76)]
    cx, cy = (bas[0] + haut[0]) * 0.5, (bas[1] + haut[1]) * 0.5
    rx, ry = (haut[0] - bas[0]) * 0.5 + 0.06, (haut[1] - bas[1]) * 0.5 + 0.06

    def clairiere(x, y):
        return 0.25 + 0.75 * np.clip((np.hypot((x - cx) / rx, (y - cy) / ry) - 0.8) / 0.5, 0, 1)
    h = A.Jouet("herbe")
    h.piece("herbe", G.herbe(2.6, 90000, 3, clairiere), "gazon", "x")
    h.monter()
    h.habiller({"gazon": M.gazon()})


def fusion_demandee(module=None):
    """La base fusionnée (fusion.py), ÉTEINTE par défaut : « fusion » sur la ligne de commande, BIBELOTS_FUSION=1, ou
    FUSION = True dans le fichier de la bête ; « sans-fusion » l'éteint toujours. Le gonflage (gonflage_demande) l'allume aussi."""
    if "sans-fusion" in sys.argv:
        return False
    if "fusion" in sys.argv[1:] or os.environ.get("BIBELOTS_FUSION") == "1":
        return True
    return bool(getattr(module, "FUSION", False)) or gonflage_demande(module)


_GARDEES = None


def gardees():
    """Les bêtes gardées par l'auteur (animaux/gardees.txt, tiré de VALIDATIONS.md) : elles restent sur leur base."""
    global _GARDEES
    if _GARDEES is None:
        try:
            with open(os.path.join(ICI, "animaux", "gardees.txt"), encoding="utf-8") as f:
                _GARDEES = {l.strip() for l in f if l.strip() and not l.startswith("#")}
        except OSError:
            _GARDEES = set()
    return _GARDEES


def gonflage_demande(module=None):
    """Le gonflage des volumes sur la base fusionnée (fusion.gonfler : des volumes ronds et rembourrés). ALLUMÉ PAR DÉFAUT
    depuis le 15/10 à 20 h 50 (l'auteur, par Principal) pour toute bête, SAUF les bêtes gardées (gardees()), qui restent sur leur
    base. « gonflage » sur la ligne de commande ou BIBELOTS_GONFLAGE=1 l'allument toujours ; GONFLAGE = True/False dans le
    fichier de la bête décide pour elle ; « sans-gonflage », « sans-fusion » ou BIBELOTS_GONFLAGE=0 l'éteignent."""
    if "sans-gonflage" in sys.argv or "sans-fusion" in sys.argv or os.environ.get("BIBELOTS_GONFLAGE") == "0":
        return False
    if "gonflage" in sys.argv[1:] or os.environ.get("BIBELOTS_GONFLAGE") == "1":
        return True
    if module is None:
        return False
    if hasattr(module, "GONFLAGE"):
        return bool(module.GONFLAGE)
    nom = str(getattr(module, "__name__", "")).rsplit(".", 1)[-1]
    if nom in ("", "__main__"):
        nom = os.path.splitext(os.path.basename(str(getattr(module, "__file__", "") or "")))[0]
    return bool(nom) and nom not in gardees()


def planche(construire, titre=None):
    """La fiche d'un animal, rendue à son tour : un seul calcul à la fois sur la machine, jamais pendant un jeu
    ni à chaud (voir machine.py). L'attente peut durer plusieurs minutes : ce n'est pas une panne."""
    import machine
    with machine.tour("la fiche " + os.path.splitext(os.path.basename(sys.argv[0]))[0], 400):
        return _planche(construire, titre)


def _planche(construire, titre=None):
    """Monte l'animal rendu par construire(), le photographie sous trois angles et assemble sa fiche."""
    from PIL import Image, ImageDraw, ImageFont
    A.neuf()
    a = construire()
    if fusion_demandee(sys.modules.get("__main__")):         # éteinte par défaut : voir fusion.py
        import fusion
        fusion.symetriser(a)
        fusion.fusionner(a, gonflage_demande(sys.modules.get("__main__")))
    a.monter()
    bas, haut = a.boite()
    _jardin(bas, haut)
    taille = max(haut[2] * 1.12, 0.8 * max(haut[0] - bas[0], haut[1] - bas[1]))
    centre = Vector(((bas[0] + haut[0]) * 0.5, (bas[1] + haut[1]) * 0.5, haut[2] * 0.45))
    recul = 2.45 * taille + 0.25
    tete = Vector(a.tete) if a.tete is not None else centre + Vector((0, -(haut[1] - bas[1]) * 0.3, haut[2] * 0.2))
    recul_pres = 0.38 + 0.8 * min(haut[2], 0.8 * (haut[0] - bas[0]) + 0.2)
    vise_pres = tete
    try:                                                     # la tête entière dans le cadre, museau compris (Cohérence, 16/10 : zèbre, girafe…)
        ORNEMENTS = ("corne", "bois", "ramure", "panache")       # on vise la tête et le museau ; les bois et les cornes ne comptent que pour le recul (16/10 : cerf)
        nom_ = lambda p: str(p.get("nom", "")).lower()
        morceaux = [p["monde"] for p in a._toutes() if nom_(p).startswith(("tete", "museau", "nez", "truffe", "bec", "oreille", "machoire", "joue"))]
        ornements = [p["monde"] for p in a._toutes() if nom_(p).startswith(ORNEMENTS)]
        peau_seule = False
        if not morceaux and a.tete is not None:              # la base fusionnée : une seule peau, on prend ce qui entoure la tête
            T = np.vstack([p["monde"] for p in a._toutes() if not nom_(p).startswith(ORNEMENTS)])
            pres_ = np.linalg.norm(T - np.asarray(a.tete, float), axis=1) < 0.28 * taille   # 0,45 prenait le cou des bêtes à long cou (16/10)
            morceaux = [T[pres_]] if pres_.sum() > 50 else []
            peau_seule = bool(morceaux)
        if morceaux:
            V = np.vstack(morceaux)
            tb, th = V.min(axis=0), V.max(axis=0)
            recul_pres = max(recul_pres, 1.35 * float(np.linalg.norm(th - tb)) + 0.15)
            vise_pres = Vector(a.tete) if peau_seule else Vector(((tb + th) * 0.5).tolist())   # la peau seule : a.tete est au centre de la tête
            if ornements:                                    # le recul couvre aussi la ramure, vue autour de la tête
                O = np.vstack([V] + ornements)
                ob, oh = O.min(axis=0), O.max(axis=0)
                cv = np.asarray(tuple(vise_pres), float)
                ecart = max(float(np.linalg.norm(oh - cv)), float(np.linalg.norm(ob - cv)))
                recul_pres = max(recul_pres, 2.5 * ecart + 0.15)
    except Exception:
        pass
    dir_pres = Vector((0.40, -0.86, 0.22)).normalized()         # par défaut : de trois quarts avant, la bête regardant vers -Y
    cap = getattr(a, "cap_tete", None)                          # a.cap_tete : l'avant de la tête (poissons couchés, têtes tournées), 16/10
    if cap is not None:
        c = Vector(tuple(float(v) for v in cap))
        if c.length > 1e-6:
            c.normalize()
            ch = Vector((c.x, c.y, 0.0))
            lat = Vector((-ch.y, ch.x, 0.0)).normalized() if ch.length > 1e-6 else Vector((1.0, 0.0, 0.0))
            dir_pres = (0.40 * lat + 0.86 * c + Vector((0.0, 0.0, 0.22))).normalized()
    os.makedirs(FICHES, exist_ok=True)
    vues = [("face", centre + Vector((0.55, -0.80, 0.38)).normalized() * recul, centre, (1280, 720), 110, tete, 2.8),
            ("dos", centre + Vector((0.55, 0.78, 0.42)).normalized() * recul, centre, (640, 360), 64, centre, 4.0),
            ("pres", vise_pres + dir_pres * recul_pres, vise_pres, (640, 360), 64, vise_pres, 4.0)]
    fichiers = []
    for nom, depuis, vers, dims, grains, net, ouverture in vues:
        chemin = os.path.join(FICHES, "_%s_%s.png" % (a.nom, nom))
        A.photo(chemin, depuis, vers, 46, dims, grains, net, ouverture)
        fichiers.append(chemin)
    fiche = Image.new("RGB", (1920, 720), (20, 20, 20))
    fiche.paste(Image.open(fichiers[0]).convert("RGB"), (0, 0))
    fiche.paste(Image.open(fichiers[2]).convert("RGB"), (1280, 0))
    fiche.paste(Image.open(fichiers[1]).convert("RGB"), (1280, 360))
    dessin = ImageDraw.Draw(fiche)
    police = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 40)
    texte = titre or a.nom.capitalize()
    large = dessin.textlength(texte, font=police)
    dessin.rounded_rectangle((28, 26, 28 + large + 44, 26 + 68), 22, fill=(255, 246, 224))
    dessin.text((50, 34), texte, font=police, fill=(70, 44, 24))
    sortie = os.path.join(FICHES, a.nom + ".png")
    fiche.save(sortie)
    for f in fichiers:
        os.remove(f)
    print("[fiche]", sortie, flush=True)
    return sortie
