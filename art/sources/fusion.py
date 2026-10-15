"""La base fusionnée des peluches : une peau d'une seule pièce au lieu d'un assemblage de formes posées les unes dans
les autres. ÉTEINTE par défaut : sans le réglage, rien ne change.

On l'allume, au choix :
    python usine.py <bête> fusion            la fabrication (et la répétition : usine.py <bête> essai fusion)
    python animaux/<bête>.py fusion          la fiche
    BIBELOTS_FUSION=1 dans l'environnement, ou FUSION = True en tête du fichier de la bête
« sans-fusion » sur la ligne de commande l'éteint toujours. Le test est peluche.fusion_demandee().

Ce qu'elle fait, une fois l'animal bâti (le fichier de la bête ne change pas) :

1. symetriser(a), avant tout le reste : une paire de petites pièces (un œil et son reflet, sa paupière, son cerne, un
   sourcil...) posée en miroir par rapport au plan X = 0 du MONDE alors que la pièce qui la porte est tournée (une tête
   de trois quarts) est remise en miroir dans le repère de cette pièce. Une paire déjà symétrique dans ce repère, ou
   qui n'est symétrique dans aucun des deux (une asymétrie voulue), n'est pas touchée.
2. fusionner(a), une fois l'animal à sa taille (et ses os donnés, dans l'usine) : les volumes de tissu (corps, tête,
   museau, membres, queue, oreilles, nez, dents, griffes, bec...) deviennent une seule peau :
     - remaillage en voxels (le modificateur Remesh de Blender) : l'union, sans faces enfouies ;
     - à chaque jonction de deux morceaux qui se touchent, un congé arrondi : union douce de leurs distances signées
       (rayon : CONGE fois l'épaisseur du plus fin des deux) ; deux morceaux qui ne se touchent pas ne sont pas soudés ;
     - un lissage (Taubin, qui ne fait pas maigrir), puis une décimation à peu près au nombre de triangles d'origine ;
     - la peau reprend des morceaux d'origine, par le point le plus proche : la couleur, le tissu (poil ou feutrine),
       la longueur du poil, et les poids des os (mélangés dans les congés, pour une jointure souple).
   Restent à part : les yeux, boutons, reflets, paupières, cerne, épingles, les pièces imprimées et les morceaux trop
   fins pour les voxels. Les yeux et leurs voisins sont recollés sur la nouvelle peau (un seul geste rigide), les
   détails cousus (rustines, coutures, broderies) suivent la surface point par point.
   Dans l'usine, tout ce qui suivait un os de la peau est rangé dans un seul groupe de cuisson (celui du corps) : la
   peau est cuite d'un tenant. Les paupières qui clignent et les épingles gardent le leur.
3. gonfler(), dans fusionner() quand le gonflage est demandé (ÉTEINT par défaut : « gonflage » sur la ligne de commande,
   BIBELOTS_GONFLAGE=1 ou GONFLAGE = True dans le fichier de la bête, voir peluche.gonflage_demande ; il allume aussi la
   fusion ; « sans-gonflage » l'éteint) : des volumes ronds et rembourrés, à l'échelle de la bête, sur la peau décimée :
     - l'arrondi : la peau suit sa courbure moyenne le temps qu'une arête s'arrondisse au rayon voulu (ARRONDI fois la
       bête) : les bouts de tube coupés net, les pointes de cône, les coins s'arrondissent, les creux aux jonctions se
       remplissent ;
     - la pression : la peau devient un tissu (des ressorts le long des arêtes, à leur longueur d'origine) qu'on
       rembourre : les faces planes bombent, les ventres s'arrondissent, comme une peluche qu'on remplit. Deux façons :
       « ressorts » (numpy, pas à pas, sans dynamique) ou « tissu » (le simulateur de tissu de Blender, sa pression) ;
     - des bornes : la peau ne rentre ni ne sort de plus qu'une part de son épaisseur locale (une queue fine, une oreille
       ne fondent pas), ni de plus qu'une part de la bête ; les points posés au sol y restent.
   La couleur, le tissu, le poil et les poids des os sont pris AVANT le gonflage (les points gardent leur place sur le
   tissu) ; les yeux (d'un geste, le même pour les deux), les pièces posées et les détails cousus suivent le déplacement
   de la peau. Les réglages : GONFLAGE (plus bas), ou BIBELOTS_GONFLAGE_REGLAGE="methode=tissu,pression=1.5".
"""
import math
import os
import sys
import time

import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

EXCLUS = ("oeil", "lourde", "paupiere", "cil", "cerne", "reflet", "pupille", "iris", "epingle", "couture_")
VOXELS = 400            # le plus grand côté de la bête, en voxels (au plus fin)
POINTS_MAX = 450000     # la peau remaillée ne dépasse pas ce nombre de points (sinon les voxels grossissent)
DURS = ("griffe", "croc", "dent", "ongle", "nez", "truffe", "ourlet", "interieur", "dedans_", "bois", "corne", "sabot",
        "bec", "defense", "piquant", "epine", "casque")   # 15/10 22 h 45 : le bec du perroquet fondu et gonflé perdait son crochet
# posés sur la peau fondue, pas fondus dedans, et recollés d'un seul geste (essais du 15/10 : des taches blanches aux griffes,
# la truffe du raton tombée sous la bouche, l'intérieur des oreilles froissé comme du papier par les voxels)
CONGE = 0.60            # le rayon du congé : cette part de l'épaisseur du plus fin des deux morceaux (0,30 : trop peu de gain, 15/10)
CONGE_MIN = 1.5         # ... au moins ce nombre de voxels
CONGE_MAX = 0.12        # ... au plus cette part de la bête
TROP_FIN = 2.5          # un morceau plus fin que ce nombre de voxels reste à part
LISSAGE = 18            # passes de lissage (6 : les formes restaient géométriques, 15/10)
TRIANGLES = (20000, 120000)   # la peau finale : le nombre de triangles d'origine, entre ces bornes
GONFLAGE = {                    # le gonflage (3.) : ses réglages
    "methode": "ressorts",      # « ressorts » (numpy) ou « tissu » (le simulateur de tissu de Blender)
    "pointes": 0.030,           # un bout plus pointu qu'une demi-boule de ce rayon est fermé en boule, en part de la bête (0 : non)
                                # (une queue plus fine : à la moitié, au quart de ce rayon)
    "arrondi": 0.030,           # le rayon de l'arrondi : ce qui est plus aigu s'arrondit, en part de la bête (0 : pas d'arrondi)
    "pression": 0.22,           # le gonflage g : une boule de rayon r s'élargit d'environ g r / L, un tube de 2 à 3 fois
                                # plus, un fond plat bombe (0 : pas de pression) ; 0,3 le 15/10 à 20 h (le corps trop gros)
    "fins": 2.0,                # les parties fines ou plates sont plus gonflées (une queue, un bras, une oreille, un pied plat) :
    "renfort": 3.0,             # la pression fois 1 + renfort x ((épaisseur médiane / épaisseur locale)^fins - 1), de 1 à 40
                                # fois (fins = 0 : non ; v2 du 15/10 : renfort 1, la queue restait une lame)
    "dedans": 0.06,             # la peau ne rentre pas de plus que cette part de son épaisseur locale
    "dehors": 0.30,             # ... ni ne sort de plus que cette part
    "plafond": 0.05,            # ... ni de plus que cette part de la bête
    "iterations": 0,            # les pas des ressorts (0 : selon la maille, 1500 à 9000)
    "images": 50,               # les images du simulateur de tissu
}
ESPION = None                   # pour les essais : appelé avec (a, P, Q, L, h) juste après la décimation de la peau
TETE_NOMS = ("tete", "crane", "museau", "machoire", "bec", "mufle", "groin", "trompe", "joue", "front", "menton", "levre",
             "babine", "cou", "nez", "truffe")          # gonflés comme le corps, jamais renforcés ni coupés en boule (l'okapi, 15/10)
MEMBRES = ("bras", "jambe", "cuisse", "patte", "main", "mollet", "epaule", "coude", "genou", "canon", "paturon", "avant_bras")
                                                # gonflés comme le corps, sans renfort (l'élan, le bras de la loutre, 15/10)
NAGEOIRES = ("nageoire", "pectorale", "dorsale", "anale", "caudale", "pelvienne", "ventrale", "voile")   # des plaques : ni
                                                # renforcées (un boudin) ni coupées en boule (la queue du dauphin, 15/10)
JAMBES_LONGUES = 0.25           # le bas du corps plus haut que cette part de la bête (0,28 : le cheval pas pris) : haute sur pattes (cerf, élan,
JAMBES_LONGUES_REGLAGES = {"pression": 0.12, "fins": 0.0}   # cheval, girafe) : moins de pression, aucun renfort
PAUPIERES_LOURDES = "retirer"   # sur la base gonflée, les paupières lourdes : « retirer » (Principal, 15/10 : leur trait sombre se
                                # lit comme un sourcil triste) ou « fines » (refaites fines à COUPE_MIN)
COUPE_MIN = 0.60                # sur la base gonflée, le bord des paupières lourdes à au moins 0,60 rayon au-dessus du milieu
EPAISSEUR_PAUPIERE = 0.30       # de l'œil (l'auteur, 15/10 : au moins 0,5) ; et fines (0,30 rayon au lieu de 0,62) : l'œil ouvert
MOUSTACHES = ("moustache", "vibrisse")   # refaites souples sur la base gonflée : courbes, retombantes, plus fines au bout


def _dire(*m):
    print("[fusion]", *m, flush=True)


# ---------------------------------------------------------------- de petits outils

def _triangles(faces):
    """Les triangles (éventail) d'une liste de faces."""
    t = [(f[0], f[k], f[k + 1]) for f in faces for k in range(1, len(f) - 1)]
    return np.array(t, np.int64).reshape(-1, 3)


def _aretes(faces):
    if isinstance(faces, np.ndarray) and faces.ndim == 2:
        a = np.vstack([faces[:, [k, (k + 1) % faces.shape[1]]] for k in range(faces.shape[1])]).astype(np.int64)
    else:
        a = [(f[k], f[(k + 1) % len(f)]) for f in faces for k in range(len(f))]
        a = np.array(a, np.int64).reshape(-1, 2)
    a.sort(axis=1)
    return np.unique(a, axis=0)


def _etiquettes(n, aretes):
    """Le numéro du morceau d'un seul tenant de chaque point (accrochage et saut de pointeurs)."""
    lab = np.arange(n)
    if len(aretes) == 0:
        return lab
    while True:
        la, lb = lab[aretes[:, 0]], lab[aretes[:, 1]]
        if np.array_equal(la, lb):
            return lab
        haut, bas = np.maximum(la, lb), np.minimum(la, lb)
        np.minimum.at(lab, haut, bas)
        while True:
            l2 = lab[lab]
            if np.array_equal(l2, lab):
                break
            lab = l2


def _mesures(v, tris):
    a, b, c = v[tris[:, 0]], v[tris[:, 1]], v[tris[:, 2]]
    aire = float(np.linalg.norm(np.cross(b - a, c - a), axis=1).sum() * 0.5)
    volume = float(abs(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0))
    return aire, volume


def _sdf(arbre, P, limite=None):
    """Distance signée (négative dedans) des points P (n x 3) à une maille fermée, son gradient (unitaire), le point le
    plus proche et sa face. Au-delà de « limite » : distance = limite, gradient nul, face -1."""
    n = len(P)
    q = np.zeros((n, 3))
    nr = np.zeros((n, 3))
    fi = np.full(n, -1, np.int64)
    fn = arbre.find_nearest
    for k, p in enumerate(P.tolist()):
        r = fn(p, limite) if limite is not None else fn(p)
        if r[0] is not None:
            q[k] = r[0]
            nr[k] = r[1]
            fi[k] = r[2]
    trouve = fi >= 0
    ecart = P - q
    lg = np.linalg.norm(ecart, axis=1)
    signe = np.where(np.einsum("ij,ij->i", ecart, nr) < 0, -1.0, 1.0)
    d = np.where(trouve, signe * lg, limite if limite is not None else 1e9)
    g = np.where((lg > 1e-12)[:, None], ecart / np.maximum(lg, 1e-12)[:, None] * signe[:, None], nr)
    g[~trouve] = 0.0
    return d, g, q, fi


def _ecorce(v, faces):
    return BVHTree.FromPolygons(np.asarray(v, float).tolist(), [tuple(int(i) for i in f) for f in faces])


def _dans(P, bas, haut, marge):
    return np.nonzero(np.all((P >= bas - marge) & (P <= haut + marge), axis=1))[0]


# ---------------------------------------------------------------- 1. les paires en miroir dans le repère qui les porte

def _symetrique(maille, taille):
    """La maille locale est-elle symétrique par rapport à son plan X = 0 ?"""
    v = maille.v
    if len(v) < 8:
        return False
    arbre = _ecorce(v, maille.f)
    ech = v[np.linspace(0, len(v) - 1, min(len(v), 300)).astype(int)] * [-1.0, 1.0, 1.0]
    d = np.array([arbre.find_nearest(p)[3] or 0.0 for p in ech.tolist()])
    return float(d.max()) < 0.02 * taille


def symetriser(a):
    """Remet en miroir, dans le repère de la pièce qui les porte, les paires posées en miroir du monde sur une pièce
    tournée. Les yeux d'abord (avec tout ce qui est collé à eux : reflet, paupière, cerne), puis les autres paires.
    À appeler juste après construire(), avant les paupières de l'usine (elles suivent les yeux corrigés)."""
    e = float(a.echelle)
    toutes = a._toutes()
    par_nom = {}
    for p in toutes:
        par_nom.setdefault(p["nom"], []).append(p)
    # les pièces qui portent : celles qui ont un repère tourné (le plan X = 0 local n'est pas celui du monde) et symétrique
    portes = {}
    for nom, (maille, rep) in a._formes.items():
        R = np.array(rep, float)
        x = R[:3, 0] / max(np.linalg.norm(R[:3, 0]), 1e-12)
        taille = float(np.ptp(maille.v, axis=0).max())
        if abs(x[1]) < 1e-4 and abs(x[2]) < 1e-4 and abs(R[0, 3]) < 1e-7:
            portes[nom] = None                                   # un repère qui garde le plan du monde : rien à corriger
            continue
        portes[nom] = (R, maille, taille) if _symetrique(maille, taille) else None
    if not any(portes.values()):
        return 0
    arbres = {}

    def arbre(nom):
        if nom not in arbres:
            ps = par_nom[nom]
            v = np.vstack([p["monde"] for p in ps])
            d, faces = 0, []
            for p in ps:
                faces += [tuple(i + d for i in f) for f in p["faces"]]
                d += len(p["monde"])
            arbres[nom] = (_ecorce(v, faces), np.ptp(v, axis=0).max())
        return arbres[nom]

    def porteuse(c, etendue, exclus):
        """La pièce la plus proche sous le point c, nettement plus grande que la paire."""
        meilleure, dmin = None, 1e9
        for nom in a._formes:
            if nom in exclus or nom not in par_nom:
                continue
            arb, t = arbre(nom)
            if t < 2.0 * etendue:
                continue
            r = arb.find_nearest(c)
            if r[0] is not None and r[3] < dmin:
                meilleure, dmin = nom, r[3]
        return meilleure

    def geste(R, c_g, c_d):
        """Les deux centres visés (monde), ou None si la paire n'est pas un miroir du monde à corriger."""
        t = R[:3, 3] * e
        lin = R[:3, :3] * e
        inv = np.linalg.inv(lin)
        ug, ud = (c_g - t), (c_d - t)
        rg, rd = np.linalg.norm(ug), np.linalg.norm(ud)
        if rg < 1e-9 or rd < 1e-9:
            return None
        miroir = np.linalg.norm(ud / rd - ug / rg * [-1.0, 1.0, 1.0]) < 0.08 and abs(rg - rd) < 0.15 * max(rg, rd)
        lg, ld = inv @ ug, inv @ ud
        deja = np.linalg.norm(ld - lg * [-1.0, 1.0, 1.0]) < 0.03 * max(np.linalg.norm(lg), 1e-9)
        if deja or not miroir:
            return None
        cible = np.array([(lg[0] - ld[0]) * 0.5, (lg[1] + ld[1]) * 0.5, (lg[2] + ld[2]) * 0.5])
        return lin @ cible + t, lin @ (cible * [-1.0, 1.0, 1.0]) + t, t

    def bouger(pieces, c, cible, centre, porte, vers=None):
        """Tourne les pièces autour de leur centre comme elles tourneraient autour de la pièce porteuse, les pose au centre
        visé, puis les recolle à la même distance de la surface. Rend la matrice du geste."""
        q = Vector(c - centre).rotation_difference(Vector(cible - centre)).to_matrix()
        Q = np.array(q)
        arb, _t = arbre(porte)
        r0 = arb.find_nearest(c)
        d0 = (Vector(c) - r0[0]).dot(r0[1]) if r0[0] is not None else 0.0
        r1 = arb.find_nearest(cible)
        d1 = (Vector(cible) - r1[0]).dot(r1[1]) if r1[0] is not None else 0.0
        decale = (np.array(r1[1]) * (d0 - d1)) if r1[0] is not None else np.zeros(3)
        for p in pieces:
            p["monde"] = (p["monde"] - c) @ Q.T + cible + decale
        return Q, cible + decale - c

    deplaces, faits = set(), []
    # les yeux d'abord : chaque œil emmène ce qui est collé à lui
    yeux = {b[0]: b for b in a._boutons if not b[4]}
    for nom, b in list(yeux.items()):
        if not nom.endswith("_G") or nom[:-2] + "_D" not in yeux or nom not in par_nom:
            continue
        bd = yeux[nom[:-2] + "_D"]
        if bd[0] not in par_nom:
            continue
        pos_g, pos_d, r = np.array(b[1]) * e, np.array(bd[1]) * e, b[3] * e
        porte = porteuse(pos_g, 2.0 * r, set())
        if porte is None or not portes.get(porte):
            continue
        R = portes[porte][0]
        visees = geste(R, pos_g, pos_d)
        if visees is None:
            continue
        nouveaux = []
        for cote, pos, cible, nom_, entree in (("G", pos_g, visees[0], nom, b), ("D", pos_d, visees[1], bd[0], bd)):
            colles = [p for p in toutes if id(p) not in deplaces and p["nom"] != porte and
                      (p["nom"] == nom_ or (np.linalg.norm(p["monde"].mean(axis=0) - pos) < 1.8 * r and
                                            np.ptp(p["monde"], axis=0).max() < 4.5 * r))]
            Q, decale = bouger(colles, pos, cible, visees[2], porte)
            deplaces |= {id(p) for p in colles}
            vers = Q @ np.array(entree[2])
            nouveaux.append((entree[0], Vector((pos + decale) / e), Vector(vers).normalized(), entree[3], entree[4]))
            faits.append("%s (%s, %d pièces, %.1f cm)" % (nom_, porte, len(colles), 100 * np.linalg.norm(decale)))
        a._boutons = [x for x in a._boutons if x[0] not in (nom, bd[0])] + nouveaux
    # les autres paires (jamais un œil ni ce qui le touche : seuls les yeux enregistrés un par un sont corrigés, plus haut)
    pres_des_yeux = []
    for b in a._boutons:
        p0 = np.array(b[1]) * e
        pres_des_yeux += [(p0, b[3] * e)] + ([(p0 * [-1.0, 1.0, 1.0], b[3] * e)] if b[4] else [])
    for nom, ps in par_nom.items():
        if not nom.endswith("_G") or nom[:-2] + "_D" not in par_nom or nom.lower().startswith(EXCLUS):
            continue
        pd = par_nom[nom[:-2] + "_D"]
        if any(id(p) in deplaces for p in ps + pd):
            continue
        c_g = np.vstack([p["monde"] for p in ps]).mean(axis=0)
        c_d = np.vstack([p["monde"] for p in pd]).mean(axis=0)
        if any(np.linalg.norm(c - y) < 1.8 * r for y, r in pres_des_yeux for c in (c_g, c_d)):
            continue
        etendue = max(np.ptp(np.vstack([p["monde"] for p in ps]), axis=0).max(), 1e-6)
        porte = porteuse(c_g, etendue, {nom, nom[:-2] + "_D"})
        if porte is None or not portes.get(porte):
            continue
        if etendue > 0.5 * portes[porte][2] * e:                 # une grande pièce (un bras) : sa pose est voulue
            continue
        visees = geste(portes[porte][0], c_g, c_d)
        if visees is None:
            continue
        for pieces, c, cible in ((ps, c_g, visees[0]), (pd, c_d, visees[1])):
            _Q, decale = bouger(pieces, c, cible, visees[2], porte)
            deplaces |= {id(p) for p in pieces}
            faits.append("%s (%s, %.1f cm)" % (pieces[0]["nom"], porte, 100 * np.linalg.norm(decale)))
    import garnitures as G
    for nom in {p["nom"] for p in toutes if id(p) in deplaces}:
        if nom in a._arbres:
            ps = par_nom[nom]
            a._arbres[nom] = G.ecorce(np.vstack([p["monde"] for p in ps]) / e, ps[0]["faces"]) if len(ps) == 1 else a._arbres[nom]
    if faits:
        _dire("symétrie dans le repère de la tête :", " ; ".join(faits))
    return len(faits)


# ---------------------------------------------------------------- 2. la peau d'une seule pièce

class _Morceau:
    """Un morceau d'un seul tenant d'une pièce d'origine."""

    def __init__(self, piece, cle, vidx, faces):
        self.p, self.cle, self.vidx = piece, cle, vidx
        self.v = piece["monde"][vidx]
        self.f = faces
        self.vidx0, self.f0 = vidx, faces                            # tels quels (pour une pièce laissée à part : _extraire)
        self.trous = self._boucher()
        self.tris = _triangles(self.f)
        self.aire, self.volume = _mesures(self.v, self.tris)
        self.epais = 4.0 * self.volume / max(self.aire, 1e-12)
        self.bas, self.haut = self.v.min(axis=0), self.v.max(axis=0)
        self.arbre = None

    def _boucher(self):
        """Un morceau ouvert (une pièce tournée dont le profil ne part pas d'un rayon nul : un museau, une oreille du raton)
        est fermé : chaque trou reçoit un éventail vers son centre. Sans cela, ni les voxels ni les distances signées ne
        savent où est son dedans, et la fusion le mangeait (essai du 15/10 : le museau du raton coupé net, ses oreilles
        fondues, la truffe et les ourlets restés en l'air). Rend le nombre de trous bouchés."""
        if not self.f:
            return 0
        d = np.array([(f[k], f[(k + 1) % len(f)]) for f in self.f for k in range(len(f))], np.int64)
        cle_ = np.sort(d, axis=1)
        _u, inv, nb = np.unique(cle_, axis=0, return_inverse=True, return_counts=True)
        bord = d[nb[inv.ravel()] == 1]                               # les arêtes qui n'ont qu'une face : le bord d'un trou
        if not len(bord):
            return 0
        n = len(self.v)
        lab = _etiquettes(n, bord)
        sommets = np.unique(bord)
        nouveaux, faces, vidx = [], list(self.f), list(self.vidx)
        for l_ in np.unique(lab[sommets]):
            vs = sommets[lab[sommets] == l_]
            c = self.v[vs].mean(axis=0)
            ic = n + len(nouveaux)
            nouveaux.append(c)
            vidx.append(int(self.vidx[vs[int(np.argmin(np.linalg.norm(self.v[vs] - c, axis=1)))]]))
            for a_, b_ in bord[np.isin(bord[:, 0], vs)].tolist():
                faces.append((b_, a_, ic))                           # le sens inverse du bord : la normale vers dehors
        self.v = np.vstack([self.v, np.array(nouveaux)])
        self.f = faces
        self.vidx = np.array(vidx, np.int64)
        return len(nouveaux)

    def ecorce(self):
        if self.arbre is None:
            self.arbre = _ecorce(self.v, self.f)
        return self.arbre


def _morceaux(p, cle):
    """Les morceaux d'un seul tenant d'une pièce (une patte faite d'un tube + une main + des doigts en donne cinq)."""
    n = len(p["monde"])
    lab = _etiquettes(n, _aretes(p["faces"]))
    faces_de = {}
    for f in p["faces"]:
        faces_de.setdefault(int(lab[f[0]]), []).append(f)
    sortie = []
    for l, faces in faces_de.items():
        vidx = np.unique(np.concatenate([np.asarray(f) for f in faces]))
        loc = np.full(n, -1, np.int64)
        loc[vidx] = np.arange(len(vidx))
        sortie.append(_Morceau(p, cle, vidx, [tuple(int(loc[i]) for i in f) for f in faces]))
    return sortie


def _extraire(p, morceaux):
    """Une copie de la pièce réduite à quelques-uns de ses morceaux (ceux qui restent à part), tels quels (sans bouchon)."""
    vidx = np.unique(np.concatenate([m.vidx0 for m in morceaux]))
    loc = np.full(len(p["monde"]), -1, np.int64)
    loc[vidx] = np.arange(len(vidx))
    q = dict(p)
    q["monde"], q["loc"], q["teinte"] = p["monde"][vidx], p["loc"][vidx], np.asarray(p["teinte"])[vidx]
    q["faces"] = [tuple(int(loc[m.vidx0[i]]) for i in f) for m in morceaux for f in m.f0]
    if p.get("poids"):
        q["poids"] = {o: np.asarray(w)[vidx] for o, w in p["poids"].items()}
    return q


def _vers_blender(V, F, nom):
    me = bpy.data.meshes.new(nom)
    faces = F.tolist() if isinstance(F, np.ndarray) else [[int(i) for i in f] for f in F]
    me.from_pydata(np.asarray(V, float).tolist(), [], faces)
    ob = bpy.data.objects.new(nom, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _depuis_blender(ob):
    """Les points et les faces de l'objet, modificateurs appliqués ; l'objet est retiré de la scène."""
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    V = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("co", V)
    nb = np.empty(len(me.polygons), np.int32)
    me.polygons.foreach_get("loop_total", nb)
    boucles = np.empty(len(me.loops), np.int32)
    me.loops.foreach_get("vertex_index", boucles)
    ev.to_mesh_clear()
    donnees = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(donnees)
    V = V.reshape(-1, 3).astype(float)
    if len(nb) and (nb == 4).all():
        F = boucles.reshape(-1, 4)
    else:
        F = np.split(boucles, np.cumsum(nb)[:-1])
    return V, F


def _taubin(P, aretes, passes, lam=0.5, mu=-0.53):
    """Le lissage de Taubin : un pas qui lisse, un pas qui regonfle ; la forme ne maigrit pas."""
    n = len(P)
    a0, a1 = aretes[:, 0], aretes[:, 1]
    nb = np.maximum(np.bincount(a0, minlength=n) + np.bincount(a1, minlength=n), 1.0)[:, None]
    for _ in range(passes):
        for f in (lam, mu):
            s = np.stack([np.bincount(a0, weights=P[a1, k], minlength=n) + np.bincount(a1, weights=P[a0, k], minlength=n)
                          for k in range(3)], axis=1)
            P = P + f * (s / nb - P)
    return P


def _rayon_conge(m1, m2, h, L):
    return float(min(max(CONGE * min(m1.epais, m2.epais), CONGE_MIN * h), CONGE_MAX * L))


def _paires(M, h, L):
    """Les morceaux qui se touchent (ou presque) : seuls eux reçoivent un congé."""
    paires = []
    for i in range(len(M)):
        for j in range(i + 1, len(M)):
            a_, b_ = M[i], M[j]
            k = _rayon_conge(a_, b_, h, L)
            if np.any(a_.bas - k > b_.haut) or np.any(b_.bas - k > a_.haut):
                continue
            for x, y in ((a_, b_), (b_, a_)):
                idx = _dans(x.v, y.bas, y.haut, k)
                if not len(idx):
                    continue
                idx = idx[np.linspace(0, len(idx) - 1, min(len(idx), 500)).astype(int)]
                d = _sdf(y.ecorce(), x.v[idx])[0]
                if d.min() < 0.25 * k:
                    paires.append((i, j, k))
                    break
    return paires


def _conges(P, M, paires, h, L, tours=3):
    """Pousse les points de l'union vers l'union douce : pour chaque paire qui se touche, le minimum adouci (cubique) de
    leurs distances signées ; le champ est le plus petit de tous. Rend les points et le nombre de points poussés."""
    pousses = np.zeros(len(P), bool)
    for _tour in range(tours):
        besoin, regions = {}, []
        for i, j, k in paires:
            idx = _dans(P, np.maximum(M[i].bas, M[j].bas), np.minimum(M[i].haut, M[j].haut), k)
            if len(idx):
                regions.append((i, j, k, idx))
                besoin.setdefault(i, []).append(idx)
                besoin.setdefault(j, []).append(idx)
        champs = {}
        for c, lst in besoin.items():
            idx = np.unique(np.concatenate(lst))
            d, g, _q, _f = _sdf(M[c].ecorce(), P[idx], CONGE_MAX * L + 4 * h)
            champs[c] = (idx, d, g)
        meilleur = np.zeros(len(P))
        grad = np.zeros((len(P), 3))
        rayon = np.zeros(len(P))
        for i, j, k, idx in regions:
            ii, di, gi = champs[i]
            jj, dj, gj = champs[j]
            si, sj = np.searchsorted(ii, idx), np.searchsorted(jj, idx)
            a_, b_ = di[si], dj[sj]
            hh = np.maximum(k - np.abs(a_ - b_), 0.0) / k
            s = np.minimum(a_, b_) - hh ** 3 * k / 6.0
            wa = np.where(a_ <= b_, 1.0 - hh * hh * 0.5, hh * hh * 0.5)
            g = wa[:, None] * gi[si] + (1.0 - wa)[:, None] * gj[sj]
            mieux = s < meilleur[idx]
            meilleur[idx[mieux]] = s[mieux]
            grad[idx[mieux]] = g[mieux]
            rayon[idx[mieux]] = k
        sel = meilleur < -0.02 * h
        if not sel.any():
            break
        n2 = np.maximum((grad[sel] ** 2).sum(axis=1), 0.3)
        pas = (-meilleur[sel] / n2)[:, None] * grad[sel]
        lg = np.linalg.norm(pas, axis=1)
        pas *= np.minimum(1.0, rayon[sel] * 0.4 / np.maximum(lg, 1e-12))[:, None]
        P[sel] += pas
        pousses |= sel
    return P, int(pousses.sum())


def _fondre(V, F, h):
    """Le remaillage en voxels : l'union des morceaux, d'un seul tenant là où ils se touchent."""
    ob = _vers_blender(V, F, "fusion_entree")
    mod = ob.modifiers.new("voxels", "REMESH")
    mod.mode = "VOXEL"
    mod.voxel_size = h
    mod.adaptivity = 0.0
    return _depuis_blender(ob)


def _alleger(P, F, cible):
    nf = len(F)
    tris = 2 * nf if isinstance(F, np.ndarray) and F.shape[1] == 4 else sum(len(f) - 2 for f in F)
    if tris <= cible * 1.05:
        return P, F
    ob = _vers_blender(P, F, "fusion_peau")
    mod = ob.modifiers.new("allege", "DECIMATE")
    mod.ratio = cible / tris
    return _depuis_blender(ob)


def _choisir(a, h_essai, L):
    """Les pièces de tissu à fondre, et la raison de chaque mise à part."""
    k = float(a.echelle)
    yeux = []
    for nom, pos, vers, r, paire in a._boutons:
        p = np.array(pos) * k
        yeux.append((p, r * k))
        if paire:
            yeux.append((p * [-1.0, 1.0, 1.0], r * k))
    import epingle
    pris, apart = [], {}
    for cle, j in a._tissus.items():
        for p in j.pieces:
            nom = p["nom"].lower()
            if p.get("genre") != "volume" or p.get("zone") not in ("poil", "feutre"):
                continue
            pourquoi = None
            if cle[1]:
                pourquoi = "imprimée"
            elif nom.startswith(EXCLUS):
                pourquoi = "œil ou épingle"
            elif nom.startswith(DURS):
                pourquoi = "pièce posée (griffe, dent, truffe, ourlet)"
            elif str(p.get("groupe", "")).startswith(epingle.OS_LIBRES):
                pourquoi = "épingle"
            else:
                c, t = p["monde"].mean(axis=0), np.ptp(p["monde"], axis=0).max()
                if any(np.linalg.norm(c - y) < 1.8 * r and t < 4.5 * r for y, r in yeux):
                    pourquoi = "collée à un œil"
            if pourquoi:
                apart[p["nom"]] = pourquoi
            else:
                pris.append((p, cle))
    return pris, apart


def reglages_bete(a, M, P, L, reglages=None):
    """Le réglage du gonflage propre à la bête : automatique (une bête haute sur pattes, dont le bas du corps, le plus gros
    morceau, est à plus de JAMBES_LONGUES de la bête au-dessus du sol : JAMBES_LONGUES_REGLAGES), puis GONFLAGE_REGLAGES =
    {...} du fichier de la bête (passé ici, ou pris au fichier lancé), qui l'emporte."""
    base = {}
    if M:
        corps = max(M, key=lambda m: m.volume)
        haut_ = float(corps.bas[2] - float(np.asarray(P)[:, 2].min()))
        if haut_ > JAMBES_LONGUES * L:
            base.update(JAMBES_LONGUES_REGLAGES)
            _dire("haute sur pattes (le bas du corps « %s » à %.0f %% de la bête) : %s" % (
                corps.p["nom"], 100 * haut_ / L, ", ".join("%s %s" % kv for kv in sorted(JAMBES_LONGUES_REGLAGES.items()))))
        else:
            _dire("le bas du corps « %s » à %.0f %% de la bête au-dessus du sol (haute sur pattes au-delà de %.0f %%)" % (
                corps.p["nom"], 100 * haut_ / L, 100 * JAMBES_LONGUES))
    if reglages is None:
        reglages = getattr(a, "gonflage_reglages", None) or getattr(sys.modules.get("__main__"), "GONFLAGE_REGLAGES", None)
    if reglages:
        base.update(reglages)
        _dire("réglage de la bête : %s" % ", ".join("%s %s" % kv for kv in sorted(reglages.items())))
    return base


def fusionner(a, gonfle=None, reglages=None):
    """La peau d'une seule pièce (voir le haut du fichier). À appeler une fois l'animal à sa taille ; dans l'usine,
    après porter() (les os de chaque pièce) et le calcul des os des paupières. Rend le nombre de pièces fondues.
    gonfle : le gonflage (3.) ; None : celui que demandent la ligne de commande et l'environnement (peluche.gonflage_demande).
    reglages : GONFLAGE_REGLAGES du fichier de la bête (sinon pris au fichier lancé, voir reglages_bete)."""
    if gonfle is None:
        import peluche
        gonfle = peluche.gonflage_demande()
    t0 = time.time()
    if a.echelle == 1.0 and a.taille:
        a.a_taille()
    bas, haut = a.boite()
    L = float(max(haut - bas))
    pris, apart = _choisir(a, None, L)
    if len(pris) < 2:
        _dire("rien à fondre (%d pièce)" % len(pris))
        return 0
    morceaux = [m for p, cle in pris for m in _morceaux(p, cle)]
    aire = sum(m.aire for m in morceaux)
    h = max(L / VOXELS, math.sqrt(aire / POINTS_MAX))
    fins = [m for m in morceaux if m.epais < TROP_FIN * h]
    M = [m for m in morceaux if m.epais >= TROP_FIN * h]
    for m in fins:
        apart.setdefault(m.p["nom"], "trop fine (%.1f mm)" % (1000 * m.epais))
    if len(M) < 2:
        _dire("rien à fondre (%d morceau assez épais)" % len(M))
        return 0
    tris_avant = sum(len(m.tris) for m in M)
    _dire("%d pièces, %d morceaux à fondre (%d triangles) ; voxel %.1f mm ; à part : %s" % (
        len({id(m.p) for m in M}), len(M), tris_avant, 1000 * h,
        ", ".join("%s (%s)" % kv for kv in sorted(apart.items())) or "rien"))
    bouches = ["%s (%d)" % (m.p["nom"], m.trous) for m in M if m.trous]
    if bouches:
        _dire("morceaux ouverts, bouchés : " + ", ".join(bouches))

    # l'union en voxels
    V, F, d = [], [], 0
    for m in M:
        V.append(m.v)
        F += [tuple(i + d for i in f) for f in m.f]
        d += len(m.v)
    P, Q = _fondre(np.vstack(V), F, h)
    t1 = time.time()
    _dire("union en voxels : %d points, %d faces (%.1f s)" % (len(P), len(Q), t1 - t0))

    # les congés, le lissage
    paires = _paires(M, h, L)
    P, pousses = _conges(P, M, paires, h, L)
    aretes = _aretes(Q)
    P = _taubin(P, aretes, LISSAGE)
    lab = _etiquettes(len(P), aretes)
    tailles = np.bincount(lab, minlength=len(P))
    garde = tailles[lab] >= 60                                       # les miettes de voxels
    if not garde.all():
        nouv = np.cumsum(garde) - 1
        if isinstance(Q, np.ndarray):
            Q = nouv[Q[garde[Q].all(axis=1)]]
        else:
            Q = [nouv[np.asarray(f)] for f in Q if garde[np.asarray(f)].all()]
        P = P[garde]
    t2 = time.time()
    _dire("congés : %d paires qui se touchent, %d points poussés ; lissage %d passes (%.1f s)" % (len(paires), pousses, LISSAGE, t2 - t1))

    # la décimation, au nombre de triangles d'origine
    cible = int(min(max(tris_avant, TRIANGLES[0]), TRIANGLES[1]))
    P, Q = _alleger(P, Q, cible)
    Q = [tuple(int(i) for i in f) for f in (Q.tolist() if isinstance(Q, np.ndarray) else Q)]
    aretes = _aretes(Q)
    lab = _etiquettes(len(P), aretes)
    _, morceaux_peau = np.unique(lab, return_counts=True)
    t3 = time.time()
    _dire("peau : %d points, %d triangles, %d morceau(x) d'un seul tenant (%s) (%.1f s)" % (
        len(P), sum(len(f) - 2 for f in Q), len(morceaux_peau), ", ".join(str(x) for x in sorted(morceaux_peau, reverse=True)[:6]), t3 - t2))
    # ce que la peau reprend des morceaux d'origine
    liens, origine = [], []
    nouvelles = _habiller(a, P, Q, M, h, L, liens, origine)
    base = {}
    if gonfle or ESPION is not None:
        try:
            base = reglages_bete(a, M, P, L, reglages)
        except Exception as e:
            _dire("réglage de la bête illisible, je prends le réglage commun : %s" % str(e)[:120])
    if ESPION is not None:
        ESPION(a, P, Q, L, h, origine, base)

    # le gonflage (3.) : calculé ici (la couleur et les os sont pris à la peau d'avant), posé après le recollage
    gonflee = None
    if gonfle:
        try:
            gonflee, _infos = gonfler(P, Q, L, h, None, origine, base)
        except Exception:
            import traceback
            traceback.print_exc()
            _dire("GONFLAGE RATÉ : la peau reste comme fondue (voir l'erreur au-dessus)")
            gonflee = None
    ancienne_surface = (M, h, L)
    fondues = {id(m.p) for m in M}
    restes = {}
    for m in fins:
        if id(m.p) in fondues:
            restes.setdefault(id(m.p), (m.p, []))[1].append(m)
    for cle, j in list(a._tissus.items()):
        garde_ = []
        for p in j.pieces:
            if id(p) in fondues:
                if id(p) in restes:
                    garde_.append(_extraire(p, restes[id(p)][1]))
            else:
                garde_.append(p)
        j.pieces = garde_
        if not j.pieces:
            del a._tissus[cle]
    for cle, ps in nouvelles.items():
        if cle not in a._tissus:
            import atelier as A
            a._tissus[cle] = A.Jouet("%s_fusion%d" % (a.nom, len(a._tissus) + 100))
        a._tissus[cle].pieces += ps
    peau = [p for ps in nouvelles.values() for p in ps]

    # un seul groupe de cuisson pour la peau et ce qui suivait ses os (dans l'usine)
    groupes = {}
    for m in M:
        if "groupe" in m.p:
            groupes[m.p["groupe"]] = groupes.get(m.p["groupe"], 0.0) + m.aire
    if groupes:
        g0 = max(groupes, key=groupes.get)
        for p in a._toutes():
            if p.get("groupe") in groupes or p.get("fusion"):
                p["groupe"] = g0
        _dire("cuisson : les groupes %s -> « %s »" % (", ".join(sorted(groupes)), g0))

    _recoller(a, peau, ancienne_surface)
    if gonfle:                                                       # la base gonflée : des yeux ouverts, des moustaches souples
        try:
            paup = _paupieres_ouvertes(a)
            mous = _moustaches(a, peau)
            _dire("paupières : %s ; %d moustaches souples" % (", ".join(paup) or "aucune lourde", mous))
        except Exception:
            import traceback
            traceback.print_exc()
            _dire("paupières, moustaches : RATÉ (voir l'erreur au-dessus)")
    if gonflee is not None:
        _suivre(a, liens, P, gonflee, Q, h, L)
    if gonfle:                                                       # l'intérieur des oreilles, dans le pelage et creusé
        try:
            oreilles = _oreilles_douces(a, liens, gonflee if gonflee is not None else P, Q)
            if oreilles:
                _dire("intérieur des oreilles peint et creusé : " + ", ".join(oreilles))
        except Exception:
            import traceback
            traceback.print_exc()
            _dire("intérieur des oreilles : RATÉ (voir l'erreur au-dessus)")
    _dire("fini en %.1f s" % (time.time() - t0))
    return len(fondues)


def _habiller(a, P, Q, M, h, L, liens=None, origine=None):
    """Couleur, tissu, longueur du poil et poids des os de chaque point de la peau, pris aux morceaux d'origine.
    Rend {clé du tissu : [pièces]} (une pièce par tissu et par longueur de poil). liens : une liste où ranger
    (pièce, numéros de ses points dans P), pour le gonflage."""
    n = len(P)
    dmin = np.full(n, np.inf)
    dom = np.full(n, -1)
    proche = []
    marge = CONGE_MAX * L + 4 * h
    for c, m in enumerate(M):
        idx = _dans(P, m.bas, m.haut, marge)
        d, _g, q, fi = _sdf(m.ecorce(), P[idx], marge)
        ok = fi >= 0
        idx, d, q, fi = idx[ok], d[ok], q[ok], fi[ok]
        # le point de la pièce d'origine le plus proche, sur la face touchée
        sv = np.empty(len(idx), np.int64)
        for k_, (f, qq) in enumerate(zip(fi.tolist(), q)):
            face = m.f[f]
            vs = m.v[list(face)]
            sv[k_] = m.vidx[face[int(np.argmin(((vs - qq) ** 2).sum(axis=1)))]]
        proche.append((idx, d, sv))
        mieux = d < dmin[idx]
        dmin[idx[mieux]] = d[mieux]
        dom[idx[mieux]] = c
    seuls = np.nonzero(dom < 0)[0]
    if len(seuls):                                                   # loin de tout (rare) : le morceau au centre le plus proche
        centres = np.array([m.v.mean(axis=0) for m in M])
        dom[seuls] = np.argmin(((P[seuls, None, :] - centres[None]) ** 2).sum(axis=2), axis=1)
    if origine is not None:                                          # le nom de la pièce d'origine de chaque point (gonflage)
        origine.extend(str(M[c].p["nom"]).lower() for c in dom.tolist())
    teinte = np.ones((n, 3))
    zone = np.zeros(n, np.int64)                                     # 0 poil, 1 feutrine
    poil_k = np.ones(n)
    usine = all("groupe" in m.p for m in M)
    poids = {}
    total = np.zeros(n)
    for c, m in enumerate(M):
        idx, d, sv = proche[c]
        couleur = m.cle[0]
        ici = dom[idx] == c
        if couleur is not None:
            teinte[idx[ici]] = np.asarray(couleur, float)
        else:
            teinte[idx[ici]] = np.asarray(m.p["teinte"], float)[sv[ici]]
        zone[idx[ici]] = 0 if m.p.get("zone") == "poil" else 1
        poil_k[idx[ici]] = float(m.p.get("poil_k", 1.0))
        if usine:
            kc = max(CONGE * m.epais, CONGE_MIN * h) * 0.5
            b = np.clip(1.0 - (d - dmin[idx]) / kc, 0.0, 1.0) ** 2
            if m.p.get("poids"):
                for o, w in m.p["poids"].items():
                    poids.setdefault(o, np.zeros(n))
                    np.add.at(poids[o], idx, b * np.asarray(w, float)[sv])
            else:
                poids.setdefault(m.p["os"], np.zeros(n))
                np.add.at(poids[m.p["os"]], idx, b)
    if usine:
        for c in (np.unique(dom[seuls]) if len(seuls) else []):
            m = M[c]
            ici = seuls[dom[seuls] == c]
            if m.p.get("poids"):
                for o, w in m.p["poids"].items():
                    poids.setdefault(o, np.zeros(n))[ici] += float(np.mean(w))
            else:
                poids.setdefault(m.p["os"], np.zeros(n))[ici] += 1.0
        total = sum(poids.values())
        total = np.where(total > 1e-9, total, 1.0)
        poids = {o: w / total for o, w in poids.items()}
    # une pièce par (tissu, longueur de poil) : la face prend le tissu de la majorité de ses points
    niveaux = sorted(set(np.round(poil_k, 3).tolist()))
    code = zone * 100 + np.searchsorted(niveaux, np.round(poil_k, 3))
    uc, ci = np.unique(code, return_inverse=True)                    # chaque point prend le tissu de la majorité de ses voisins :
    if len(uc) > 1:                                                  # pas d'îlots de poil dans la feutrine (la baudroie, 15/10)
        ci = ci.ravel()
        Ev = _aretes(Q)
        for _ in range(3):
            votes = np.zeros((n, len(uc)))
            np.add.at(votes, (Ev[:, 0], ci[Ev[:, 1]]), 1.0)
            np.add.at(votes, (Ev[:, 1], ci[Ev[:, 0]]), 1.0)
            votes[np.arange(n), ci] += 1.5
            ci = np.argmax(votes, axis=1)
        code = uc[ci]
    face_code = np.array([np.bincount(code[list(f)]).argmax() for f in Q])
    sorties = {}
    for c in np.unique(face_code):
        faces = [Q[i] for i in np.nonzero(face_code == c)[0]]
        vidx = np.unique(np.concatenate([np.asarray(f) for f in faces]))
        loc = np.full(n, -1, np.int64)
        loc[vidx] = np.arange(len(vidx))
        z, k_ = int(c // 100), niveaux[int(c % 100)]
        p = {"nom": "peau" + ("_feutre" if z else "") + ("" if k_ == 1.0 else "_k%d" % int(round(100 * k_))),
             "monde": P[vidx].copy(), "loc": P[vidx].copy(), "faces": [tuple(int(loc[i]) for i in f) for f in faces],
             "matiere": "tissu", "os": "x", "teinte": teinte[vidx], "genre": "volume", "zone": "feutre" if z else "poil",
             "poil": None if z else "teinte", "fusion": True}
        if k_ != 1.0:
            p["poil_k"] = k_
        if usine:
            p["poids"] = {o: w[vidx] for o, w in poids.items() if w[vidx].max() > 1e-4}
            p["os"] = max(p["poids"], key=lambda o: p["poids"][o].sum())
        # deux longueurs de poil -> deux tissus (l'usine règle la longueur de chaque objet de cuisson à part)
        cle = (None, None) if k_ == 1.0 else (None, "")
        sorties.setdefault(cle, []).append(p)
        if liens is not None:
            liens.append((p, vidx))
    return sorties


def _recoller(a, peau, ancienne):
    """Les yeux (et ce qui leur est collé) suivent la peau d'un seul geste ; les détails cousus, point par point."""
    M, h, L = ancienne
    V, F, d = [], [], 0
    for p in peau:
        V.append(p["monde"])
        F += [tuple(i + d for i in f) for f in p["faces"]]
        d += len(p["monde"])
    arbre_peau = _ecorce(np.vstack(V), F)
    e = float(a.echelle)

    def vieille_surface(X, limite):
        """La surface d'avant (le plus proche des morceaux fondus) : distance signée, point, normale vers dehors."""
        dbest = np.full(len(X), limite)
        q = np.zeros((len(X), 3))
        n = np.zeros((len(X), 3))
        for m in M:
            idx = _dans(X, m.bas, m.haut, limite)
            if not len(idx):
                continue
            dd, g, qq, fi = _sdf(m.ecorce(), X[idx], limite)
            ok = (fi >= 0) & (np.abs(dd) < np.abs(dbest[idx]))
            dbest[idx[ok]], q[idx[ok]], n[idx[ok]] = dd[ok], qq[ok], g[ok]
        return dbest, q, n

    bosse_max = CONGE_MAX * L / 6.0 + 2 * h                            # le plus que la peau puisse sortir (congé, lissage)

    def ecart(q, n, portee, rentre=None):
        """De combien la peau est sortie (ou rentrée) le long de n, au-dessus des points q de la surface d'avant.
        rentre : de combien elle peut être rentrée au plus (2 voxels par défaut ; plus pour les pièces posées : un bout de
        museau ou d'oreille fin rentre d'un centimètre au lissage, la truffe et l'ourlet doivent suivre, essai du 15/10)."""
        de = np.zeros(len(q))
        for k_, (qq, nn) in enumerate(zip(q.tolist(), n.tolist())):
            if nn == [0.0, 0.0, 0.0]:
                continue
            o = Vector(qq) + Vector(nn) * portee
            r = arbre_peau.ray_cast(o, -Vector(nn), 2 * portee)
            if r[0] is not None:
                de[k_] = portee - r[3]
        de[(de > bosse_max) | (de < -(2 * h if rentre is None else rentre))] = 0.0      # touché autre chose (un bras devant le corps)
        return de

    portee = bosse_max + h
    bouges = []
    # les yeux : un geste rigide pour l'œil et tout ce qui le touche
    deja = set()
    for nom, pos, vers, r, paire in list(a._boutons):
        cotes_ = []
        for signe in ((1.0, -1.0) if paire else (1.0,)):
            c = np.array(pos) * e * [signe, 1.0, 1.0]
            dist, q, n = vieille_surface(c[None], portee)
            if abs(dist[0]) >= portee:
                continue
            cotes_.append((signe, c, n[0], ecart(q, n, portee)[0]))
        if not cotes_:
            continue
        de = float(np.mean([x[3] for x in cotes_]))                     # une paire bouge d'autant des deux côtés : des yeux égaux
        if abs(de) < 0.05 * h:
            continue
        for signe, c, nn, _de in cotes_:
            groupe_ = [p for p in a._toutes() if not p.get("fusion") and id(p) not in deja and
                       np.linalg.norm(p["monde"].mean(axis=0) - c) < 1.8 * r * e and np.ptp(p["monde"], axis=0).max() < 4.5 * r * e]
            for p in groupe_:
                p["monde"] = p["monde"] + nn * de
                deja.add(id(p))
            bouges.append("%s %+.1f mm" % (nom + ("_D" if signe < 0 else ""), 1000 * de))
    # les pièces posées (truffe, griffes, dents) : chacune d'un seul geste, le long de la peau sous elle ; celles qui sont
    # couchées sur la peau (ourlet, intérieur d'oreille) la suivent point par point (essai du 15/10 : la pointe de l'oreille
    # du raton rentrait au lissage, l'ourlet restait et sortait comme une corne blanche)
    posees = []
    couchees = ("ourlet", "interieur", "dedans_")
    for p in a._toutes():
        if p.get("fusion") or id(p) in deja or not p["nom"].lower().startswith(DURS):
            continue
        X = p["monde"]
        ext = 0.5 * float(np.ptp(X, axis=0).max())
        if p["nom"].lower().startswith(couchees):
            dist, q, n = vieille_surface(X, portee + ext)
            sur = (np.abs(dist) < portee + ext) & np.any(n != 0.0, axis=1)
            if sur.any():
                de = np.zeros(len(X))
                de[sur] = ecart(q[sur], n[sur], portee, bosse_max)
                med = float(np.median(de[sur]))
                de[sur] = np.clip(de[sur], med - 2 * h, med + 2 * h)     # la pièce suit la peau sans se déchirer (15/10)
                p["monde"] = X + n * de[:, None]
                posees.append("%s %+.1f..%+.1f mm" % (p["nom"], 1000 * de.min(), 1000 * de.max()))
            deja.add(id(p))
            continue
        c = X.mean(axis=0)
        dist, q, n = vieille_surface(c[None], portee + ext)
        if abs(dist[0]) >= portee + ext or not n[0].any():
            continue
        de = ecart(q, n, portee, bosse_max)[0]
        if abs(de) >= 0.05 * h:
            p["monde"] = X + n[0] * de
            posees.append("%s %+.1f mm" % (p["nom"], 1000 * de))
        deja.add(id(p))
    # les détails cousus : point par point
    details = 0
    for p in a._toutes():
        if p.get("fusion") or id(p) in deja or p.get("genre") != "detail":
            continue
        X = p["monde"]
        dist, q, n = vieille_surface(X, portee)
        sur = np.abs(dist) < 0.01 * L + 2 * h
        if not sur.any():
            continue
        de = np.zeros(len(X))
        de[sur] = ecart(q[sur], n[sur], portee)
        if np.abs(de).max() > 0.05 * h:
            p["monde"] = X + n * de[:, None]
            details += 1
    _dire("recollés : yeux %s ; posées %s ; %d détails cousus suivent la peau" % (", ".join(bouges) or "en place", ", ".join(posees) or "en place", details))


# ---------------------------------------------------------------- 3. le gonflage : des volumes ronds et rembourrés

def _reglages(autres=None, base=None):
    """GONFLAGE, corrigé par « base » (le réglage automatique, puis GONFLAGE_REGLAGES du fichier de la bête), puis par
    BIBELOTS_GONFLAGE_REGLAGE (« methode=tissu,pression=1.5 »), puis par « autres »."""
    r = dict(GONFLAGE)
    r.update({k: v for k, v in (base or {}).items() if k in r})
    for morceau in os.environ.get("BIBELOTS_GONFLAGE_REGLAGE", "").split(","):
        k, _egal, v = morceau.partition("=")
        k, v = k.strip(), v.strip()
        if k in r and v:
            r[k] = v if isinstance(r[k], str) else type(r[k])(float(v))
    r.update(autres or {})
    return r


def _par_sommet(T, valeurs, n):
    """La somme sur chaque sommet d'une valeur portée par chaque triangle ((m,) ou (m, 3))."""
    if valeurs.ndim == 1:
        return sum(np.bincount(T[:, k], weights=valeurs, minlength=n) for k in range(3))
    return np.stack([sum(np.bincount(T[:, k], weights=valeurs[:, j], minlength=n) for k in range(3)) for j in range(3)], axis=1)


def _normales(X, T):
    """Les normales des sommets (pondérées par l'aire des triangles), unitaires."""
    c = np.cross(X[T[:, 1]] - X[T[:, 0]], X[T[:, 2]] - X[T[:, 0]])
    nv = _par_sommet(T, c, len(X))
    return nv / np.maximum(np.linalg.norm(nv, axis=1, keepdims=True), 1e-18)


def _voisins(X, E, deg):
    """La moyenne des voisins de chaque sommet (X : (n,) ou (n, 3))."""
    n = len(X)
    if X.ndim == 1:
        return (np.bincount(E[:, 0], weights=X[E[:, 1]], minlength=n) + np.bincount(E[:, 1], weights=X[E[:, 0]], minlength=n)) / deg
    s = np.stack([np.bincount(E[:, 0], weights=X[E[:, 1], j], minlength=n) +
                  np.bincount(E[:, 1], weights=X[E[:, 0], j], minlength=n) for j in range(3)], axis=1)
    return s / deg[:, None]


def _volume(X, T):
    return float(np.einsum("ij,ij->i", X[T[:, 0]], np.cross(X[T[:, 1]], X[T[:, 2]])).sum() / 6.0)


def _epaisseur(X, T, nv, L):
    """L'épaisseur locale de la peau sous chaque point : le rayon lancé vers l'intérieur, jusqu'à l'autre face."""
    arbre = BVHTree.FromPolygons(X.tolist(), T.tolist())
    e = 1e-4 * L
    t = np.full(len(X), 0.5 * L)
    rc = arbre.ray_cast
    ok = np.linalg.norm(nv, axis=1) > 0.5
    for i, o, d in zip(np.nonzero(ok)[0].tolist(), (X[ok] - nv[ok] * e).tolist(), (-nv[ok]).tolist()):
        r = rc(o, d, L)
        if r[0] is not None:
            t[i] = r[3] + e
    return np.minimum(t, 0.5 * L)


def _borner(X, X0, n0, dedans, dehors):
    """Le long de la normale d'origine, la peau ne rentre pas de plus que « dedans » ni ne sort de plus que « dehors »."""
    u = np.einsum("ij,ij->i", X - X0, n0)
    return X + (np.clip(u, -dedans, dehors) - u)[:, None] * n0


def _arrondir(X0, T, E, deg, n0, rayon, t, dedans, dehors, sol):
    """L'arrondi : ce qui est plus aigu qu'une boule de ce rayon (une arête, un bout de tube coupé net, une pointe de cône,
    un creux à une jonction) suit sa courbure moyenne (chaque point vers la moyenne de ses voisins, le long de sa normale),
    jusqu'à n'être plus aigu ; ce qui est déjà plus doux (une joue, un ventre, un tube plus épais que le rayon) ne bouge pas,
    ni un tube fin sur sa longueur (le seuil suit aussi l'épaisseur locale t). Rend les points et le nombre de passes."""
    n = len(X0)
    lg = np.linalg.norm(X0[E[:, 1]] - X0[E[:, 0]], axis=1)
    lv = (np.bincount(E[:, 0], weights=lg, minlength=n) + np.bincount(E[:, 1], weights=lg, minlength=n)) / deg
    l2 = (np.bincount(E[:, 0], weights=lg ** 2, minlength=n) + np.bincount(E[:, 1], weights=lg ** 2, minlength=n)) / deg
    lref = max(float(np.percentile(lv, 30)), 1e-9)
    kap = 0.4 * np.minimum(1.0, (lref / np.maximum(lv, 1e-12)) ** 2)     # le même pas de temps partout (les grands triangles)
    passes = int(min(600, math.ceil(3.0 * (rayon / lref) ** 2 / 0.4)))
    # la moyenne des voisins s'écarte de l2 H / 2 le long de la normale (H : la courbure moyenne) ; au-dessous du seuil, rien
    seuil = 0.5 * l2 * np.maximum(1.0 / rayon, 1.2 / np.maximum(t, 1e-9))
    X = X0.copy()
    z0 = X0[sol, 2]
    nn = n0
    for k in range(passes):
        if k % 3 == 0:
            nn = _normales(X, T)
        d = np.einsum("ij,ij->i", _voisins(X, E, deg) - X, nn)
        d = np.sign(d) * np.maximum(np.abs(d) - seuil, 0.0)
        X = _borner(X + (kap * d)[:, None] * nn, X0, n0, dedans, dehors)
        X[sol, 2] = z0
    return X, passes


def _pointes(X0, T, E, rayon, zmin, rayon_min=0.0, interdit=None):
    """Les pointes : un bout plus pointu qu'une demi-boule de ce rayon (le bout d'une queue en cône) est coupé là où le tube
    atteint ce rayon et fermé d'une demi-boule, comme le bout cousu d'une queue de peluche. Un bout déjà rond (un doigt, une
    patte, un museau mousse), une pièce plate (une oreille) ou plus fine que le rayon sur toute sa longueur ne change pas.
    Rend les points et la liste des pointes arrondies (« raccourcie de x mm, bout de r mm »)."""
    from collections import deque
    from mathutils.kdtree import KDTree
    n = len(X0)
    X = X0.copy()
    A_, B_, C_ = X[T[:, 0]], X[T[:, 1]], X[T[:, 2]]

    def angle(u, v):
        c = np.einsum("ij,ij->i", u, v) / np.maximum(np.linalg.norm(u, axis=1) * np.linalg.norm(v, axis=1), 1e-18)
        return np.arccos(np.clip(c, -1.0, 1.0))
    defaut = 2.0 * math.pi - (np.bincount(T[:, 0], weights=angle(B_ - A_, C_ - A_), minlength=n) +
                              np.bincount(T[:, 1], weights=angle(C_ - B_, A_ - B_), minlength=n) +
                              np.bincount(T[:, 2], weights=angle(A_ - C_, B_ - C_), minlength=n))
    arbre = KDTree(n)
    for i, x in enumerate(X.tolist()):
        arbre.insert(x, i)
    arbre.balance()
    # la courbure totale (le défaut d'angle) à moins de « rayon » de chaque point : une demi-boule de ce rayon en a pi
    total = np.array([sum(defaut[j] for _c, j, _d in arbre.find_range(x, rayon)) for x in X.tolist()])
    tous = np.concatenate([E[:, 0], E[:, 1]])
    ordre = np.argsort(tous, kind="stable")
    voisins = np.concatenate([E[:, 1], E[:, 0]])[ordre]
    debut = np.searchsorted(tous[ordre], np.arange(n + 1))
    nrm = _normales(X, T)
    fait = np.zeros(n, bool)
    faites, refus = [], []

    def couper(R, s, rad, apex, axe, rho_v, larg):
        """Le bout coupé là où le tube atteint rho_v et fermé d'une demi-boule ; sinon la raison du refus (un texte qui
        commence par « non »). larg : l'épaisseur des tranches (au moins une arête de la maille, qui est grossière ici)."""
        pas = 0.25 * rho_v
        s_c = None
        for k in range(1, int(3.5 * rho_v / pas)):
            tranche = np.abs(s - k * pas) < 0.5 * larg
            if tranche.sum() >= 4 and float(np.median(rad[tranche])) >= rho_v:
                s_c = k * pas
                break
        if s_c is None:
            return "non : plus fine que %.0f mm" % (1000 * rho_v)
        if s_c < 1.3 * rho_v:                                         # déjà ronde
            return "non : déjà ronde"
        if (rad[s < s_c - 0.5 * larg] > 1.2 * rho_v).any():          # pas un bout de tube : un petit bout sur un gros (un doigt)
            return "non : un petit bout sur un gros"
        dans = np.abs(s - s_c) < 0.5 * larg
        anneau, rr = R[dans], rad[dans]
        if rr.min() < 0.5 * rr.max() or rr.max() > 1.7 * rho_v:      # une section plate (une oreille) ou qui déborde
            return "non : section plate ou débordante (%.2f, %.0f mm)" % (rr.min() / max(rr.max(), 1e-9), 1000 * rr.max())
        c = X[anneau].mean(axis=0)
        if np.linalg.norm(c - (apex - axe * s_c)) > 0.6 * rho_v:     # la section n'est pas autour de l'axe
            return "non : section hors de l'axe"
        rho = float(np.median(np.linalg.norm(X[anneau] - c, axis=1)))
        bout = R[(s < s_c) & (rad < 1.5 * rho)]
        d = X[bout] - c
        X[bout] = c + rho * d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-12)
        fait[R[s < s_c + rho_v]] = True
        return "raccourcie de %.0f mm, bout de %.0f mm" % (1000 * (s_c - rho), 1000 * rho)

    # un cône de demi-angle a porte 2 pi (1 - sin a) de courbure : 2,7 à 35°, 4,1 à 15° ; une demi-boule de rayon r, pi dans une
    # boule de rayon r. Le seuil prend les cônes jusqu'à 60° ; la coupe (un bout plus long que 1,3 rayon) trie ensuite
    for i in np.argsort(-total).tolist():
        if total[i] < 0.45 * math.pi:
            break
        if fait[i] or (interdit is not None and interdit[i]):       # jamais un museau, un bec, une tête
            continue
        apex = X[i].copy()
        proche = np.array([j for _c, j, _d in arbre.find_range(apex.tolist(), rayon)], np.int64)
        axe = nrm[proche].sum(axis=0)
        axe /= max(np.linalg.norm(axe), 1e-12)
        vu, file_ = {i}, deque([i])                                  # la région : de proche en proche, à moins de 4 rayons
        while file_:
            j = file_.popleft()
            for k in voisins[debut[j]:debut[j + 1]].tolist():
                if k not in vu and np.linalg.norm(X[k] - apex) < 4.0 * rayon:
                    vu.add(k)
                    file_.append(k)
        R = np.array(sorted(vu), np.int64)
        V = X[R] - apex
        s = -(V @ axe)                                               # la profondeur depuis la pointe, le long de l'axe
        rad = np.linalg.norm(V + s[:, None] * axe, axis=1)           # l'écart à l'axe
        fait[R[np.linalg.norm(V, axis=1) < 0.5 * rayon]] = True
        dans_r = np.isin(E[:, 0], R) & np.isin(E[:, 1], R)
        l_loc = float(np.median(np.linalg.norm(X[E[dans_r, 1]] - X[E[dans_r, 0]], axis=1))) if dans_r.any() else 0.0
        raisons = []
        for rho_v in (rayon, 0.5 * rayon, 0.25 * rayon):             # le plus gros bout rond possible ; une queue fine, le sien
            if rho_v < rayon_min:
                break
            dit = couper(R, s, rad, apex, axe, rho_v, max(0.5 * rho_v, 1.3 * l_loc))
            if not dit.startswith("non"):
                faites.append(dit)
                break
            raisons.append("%.0f mm %s" % (1000 * rho_v, dit))
        else:
            if len(refus) < 6:
                refus.append("z %.0f mm, courbure %.1f : %s" % (1000 * apex[2], total[i], " / ".join(raisons)))
    X[:, 2] = np.maximum(X[:, 2], zmin)
    if refus:
        _dire("pointes laissées (les plus pointues) : " + " ; ".join(refus))
    return X, faites


def _ressorts(X1, T, E, deg, g, L, iterations, X0, n0, dedans, dehors, sol, zmin, facteur=1.0):
    """La pression, en numpy : chaque arête est un ressort à sa longueur de départ, chaque point est poussé le long de sa
    normale ; à l'équilibre, une boule de rayon r s'étire d'environ g r / L (un tube deux à trois fois plus), un fond plat
    bombe. Pas de dynamique : des pas de relaxation (ressorts projetés, à la Jacobi). iterations <= 0 : selon la maille.
    Rend les points et le nombre de pas faits."""
    n = len(X1)
    i0, i1 = E[:, 0], E[:, 1]
    l0 = np.linalg.norm(X1[i1] - X1[i0], axis=1)
    l2 = (np.bincount(i0, weights=l0 ** 2, minlength=n) + np.bincount(i1, weights=l0 ** 2, minlength=n)) / deg
    om = 0.9
    pas = g * om * l2 / (4.0 * L) * facteur     # facteur : plus de pression dans les parties fines (gonfler, « fins »)
    if iterations <= 0:                         # assez de pas pour qu'un ventre (un dixième de la bête) trouve son équilibre
        lmed = float(np.median(np.sqrt(l2)))
        iterations = int(min(5000, max(1500, 15.0 * (0.1 * L / max(lmed, 1e-9)) ** 2)))   # 9000 au plus : 4 min sur le cheval
    X = X1.copy()
    z0 = X1[sol, 2]
    nn = n0
    temoin, k = X.copy(), 0
    for k in range(iterations):
        if k % 2 == 0:
            nn = _normales(X, T)
        X = X + pas[:, None] * nn
        d = X[i1] - X[i0]
        lg = np.linalg.norm(d, axis=1)
        c = d * (0.5 * (lg - l0) / np.maximum(lg, 1e-12))[:, None]
        corr = np.stack([np.bincount(i0, weights=c[:, j], minlength=n) - np.bincount(i1, weights=c[:, j], minlength=n)
                         for j in range(3)], axis=1)
        X = X + om * corr / deg[:, None]
        if k % 10 == 9:
            X = _borner(X, X0, n0, dedans, dehors)
        X[:, 2] = np.maximum(X[:, 2], zmin)
        X[sol, 2] = z0
        if k % 500 == 499:                      # l'équilibre : en 500 pas, plus rien ne bouge (moins de 2 % de la poussée)
            if np.linalg.norm(X - temoin, axis=1).mean() < 0.02 * 500 * float(pas.mean()):
                break
            temoin = X.copy()
    return X, k + 1


def _regler(objet, **valeurs):
    """Règle des propriétés de Blender une à une : une propriété qui manque est dite, pas fatale."""
    for k, v in valeurs.items():
        try:
            setattr(objet, k, v)
        except Exception as e:
            _dire("tissu : réglage « %s » refusé (%s)" % (k, str(e)[:80]))


def _tissu(X1, T, L, g, images):
    """La pression du simulateur de tissu de Blender (modificateur Cloth, « Pressure ») : la peau ramenée à 1 m, sans gravité
    ni collision, gonflée pendant « images » images ; le volume visé (+35 %) borne le gonflage quoi qu'il arrive.
    Rend les points (même ordre), ou None si le tissu n'a pas bougé."""
    c = 0.5 * (X1.min(axis=0) + X1.max(axis=0))
    Xn = (X1 - c) / L
    E = _aretes(T)
    l_moy = float(np.linalg.norm(Xn[E[:, 1]] - Xn[E[:, 0]], axis=1).mean())
    vol = abs(_volume(Xn, T))
    raideur = 15.0
    # des ressorts de raideur r (force r x allongement relatif) en triangles d'arête l : une tension de 1,73 r / l par unité de
    # longueur ; une boule de rayon R s'étire alors de p l R / (3,46 r) : g a le même sens qu'aux ressorts numpy (g R / L)
    p = 3.46 * g * raideur / max(l_moy, 1e-6)
    gain = max(0.35, p / 10000.0)                # le volume visé : la pression tombe à zéro quand il est atteint
    ob = _vers_blender(Xn, T, "gonflage")
    mod = ob.modifiers.new("tissu", "CLOTH")
    cs = mod.settings
    _regler(cs, quality=6, mass=0.15, air_damping=5.0, bending_model="ANGULAR", tension_stiffness=raideur,
            compression_stiffness=raideur, shear_stiffness=raideur, bending_stiffness=0.05, tension_damping=5.0,
            compression_damping=5.0, shear_damping=5.0, use_pressure=True, uniform_pressure_force=0.0, use_pressure_volume=True,
            target_volume=vol * (1.0 + gain), pressure_factor=float(min(10000.0, p / gain)), fluid_density=0.0)
    _regler(cs.effector_weights, gravity=0.0)
    _regler(mod.collision_settings, use_collision=False, use_self_collision=False)
    _regler(mod.point_cache, frame_start=1, frame_end=images)
    sc = bpy.context.scene
    avant = (sc.frame_current, sc.frame_start, sc.frame_end)
    sc.frame_start, sc.frame_end = 1, max(images, sc.frame_end)
    t0 = time.time()
    for f in range(1, images + 1):
        sc.frame_set(f)
    V, _F = _depuis_blender(ob)
    sc.frame_start, sc.frame_end = avant[1], avant[2]
    sc.frame_set(avant[0])
    if len(V) != len(X1) or not np.isfinite(V).all():
        _dire("tissu : la maille revenue ne va pas (%d points pour %d)" % (len(V), len(X1)))
        return None
    bouge = np.linalg.norm(V - Xn, axis=1)
    _dire("tissu : %d images en %.1f s ; pression %.0f (échelle %.0f), arête moyenne %.4f ; volume %+.1f %% ; déplacement moyen %.4f, "
          "max %.4f (bête ramenée à 1)" % (images, time.time() - t0, p, min(10000.0, p / gain), l_moy, 100 * (abs(_volume(V, T)) / vol - 1),
                                          bouge.mean(), bouge.max()))
    if bouge.max() < 1e-6:
        return None
    return V * L + c


def gonfler(P, F, L, h, reglages=None, noms=None, base=None):
    """Le gonflage de la peau (P, F) d'une bête de taille L (voir le haut du fichier) : rend les nouveaux points (même ordre)
    et une ligne de compte rendu. reglages : un dictionnaire qui corrige GONFLAGE (après tout le reste) ; base : celui de la
    bête (voir _reglages) ; noms : la pièce d'origine de chaque point (la tête et les membres ne sont pas renforcés)."""
    r = _reglages(reglages, base)
    t0 = time.time()
    P = np.asarray(P, float)
    if isinstance(F, np.ndarray) and F.ndim == 2 and F.shape[1] == 3:
        T = F.astype(np.int64)
    else:
        T = _triangles(F)
    if _volume(P, T) < 0:                                            # les normales vers l'extérieur
        T = T[:, [0, 2, 1]]
    n = len(P)
    E = _aretes(T)
    deg = np.maximum(np.bincount(E[:, 0], minlength=n) + np.bincount(E[:, 1], minlength=n), 1).astype(float)
    zmin = float(P[:, 2].min())
    sol = np.nonzero(P[:, 2] <= zmin + 0.004 * L)[0]                  # posés au sol : ils y restent
    tete = np.zeros(n, bool)                                         # les points venus de la tête, du cou, des membres
    membre = np.zeros(n, bool)
    plaque = np.zeros(n, bool)                                       # ... des nageoires
    if noms is not None and len(noms) == n:
        tete = np.array([str(s).lower().startswith(TETE_NOMS) for s in noms], bool)
        membre = np.array([str(s).lower().startswith(MEMBRES + NAGEOIRES) for s in noms], bool)
        plaque = np.array([str(s).lower().startswith(NAGEOIRES) for s in noms], bool)
    P0, faites = P, []
    if r["pointes"] > 0:                                             # d'abord les bouts pointus : coupés et fermés en boule
        try:
            P, faites = _pointes(P0, T, E, r["pointes"] * L, zmin, 3.0 * h, tete | plaque)
        except Exception:
            import traceback
            traceback.print_exc()
            _dire("pointes : RATÉ, je passe (voir l'erreur au-dessus)")
            P = P0
    n0 = _normales(P, T)
    t = np.maximum(_epaisseur(P, T, n0, L), TROP_FIN * h)             # rien de plus fin n'a été fondu
    for _ in range(3):
        t = 0.5 * t + 0.5 * _voisins(t, E, deg)
    dedans = r["dedans"] * t
    dehors = np.minimum(r["dehors"] * t, r["plafond"] * L)
    X, passes, pas_faits = P, 0, 0
    if r["arrondi"] > 0:
        X, passes = _arrondir(P, T, E, deg, n0, r["arrondi"] * L, t, dedans, dehors, sol)
    t1 = time.time()
    methode = r["methode"]
    if r["pression"] > 0:
        Y = None
        if methode == "tissu":
            Y = _tissu(X, T, L, r["pression"], int(r["images"]))
            if Y is None:
                _dire("tissu : rien n'a bougé, je passe aux ressorts")
                methode = "ressorts"
            else:
                u = Y - X                                            # les plis fins du tissu, lissés
                for _ in range(3):
                    u = 0.5 * u + 0.5 * _voisins(u, E, deg)
                Y = X + u
                Y[:, 2] = np.maximum(Y[:, 2], zmin)
                Y[sol, 2] = P[sol, 2]
        if methode == "ressorts":
            facteur = 1.0
            if r["fins"] > 0:                                        # une queue, une oreille, un pied plat : gonflés eux aussi
                # l'épaisseur prise sur un diamètre autour : le bout d'une queue qui s'effile garde l'épaisseur de ce qui le porte
                # et ne gonfle pas en pompon (Principal, 15/10, le raton) ; une oreille, un pied plat restent fins tout autour
                from mathutils.kdtree import KDTree
                t_med = float(np.median(t))
                kd = KDTree(n)
                for i_, x_ in enumerate(P.tolist()):
                    kd.insert(x_, i_)
                kd.balance()
                t_eff = t.copy()
                for i_ in np.nonzero(t < t_med / 1.1)[0].tolist():
                    t_eff[i_] = max(t[j_] for _c, j_, _d in kd.find_range(P[i_].tolist(), float(t[i_])))
                rapport = np.maximum(t_med / t_eff, 1.0) ** r["fins"]
                facteur = np.clip(1.0 + r["renfort"] * (rapport - 1.0), 1.0, 25.0)
                facteur[tete | membre] = 1.0                         # un museau long n'est pas une queue (l'okapi en boule, 15/10)
                for _ in range(4):                                   # sans saut d'un point à l'autre (des pics au bout de la queue, v3)
                    facteur = 0.5 * facteur + 0.5 * _voisins(facteur, E, deg)
            Y, pas_faits = _ressorts(X, T, E, deg, r["pression"], L, int(r["iterations"]), P, n0, dedans, dehors, sol, zmin, facteur)
        X = Y
    X = _borner(X, P, n0, dedans, dehors)
    X[:, 2] = np.maximum(X[:, 2], zmin)
    if not np.isfinite(X).all():
        _dire("GONFLAGE : des points perdus (NaN) ; la peau reste comme fondue")
        return P0.copy(), "raté"
    un = np.einsum("ij,ij->i", X - P, n0)
    lu = np.linalg.norm(X - P0, axis=1)
    v0, v1 = abs(_volume(P0, T)), abs(_volume(X, T))
    infos = ("pointes %s ; " % (("%.0f mm : " % (1000 * r["pointes"] * L) + (", ".join(faites) or "aucune")) if r["pointes"] > 0 else "non") +
             "arrondi %.0f mm (%d passes) ; %s g=%.2f%s ; volume %+.1f %% ; déplacement moyen %.1f mm, max %.1f mm "
             "(sorti jusqu'à %.1f, rentré jusqu'à %.1f) ; bornés : %d %% dedans, %d %% dehors ; épaisseur médiane %.0f mm (%.1f s + %.1f s)" % (
                 1000 * r["arrondi"] * L, passes, methode if r["pression"] > 0 else "sans pression", r["pression"],
                 (" (%d pas)" % pas_faits) if pas_faits else "", 100 * (v1 / v0 - 1),
                 1000 * lu.mean(), 1000 * lu.max(), 1000 * un.max(), -1000 * un.min(), 100 * np.mean(un <= -dedans * 0.999),
                 100 * np.mean(un >= dehors * 0.999), 1000 * float(np.median(t)), t1 - t0, time.time() - t1))
    _dire("gonflage :", infos)
    return X, infos


SOURCILS = ("sourcil",)          # sur la base gonflée, retirés : des traits au-dessus des yeux qui font un air inquiet (15/10)
INTERIEURS = ("ourlet", "interieur", "dedans_")   # l'intérieur des oreilles : peint dans le pelage et creusé, la pièce retirée


def _retirer(a, garder):
    """Retire de l'animal les pièces que garder(p) refuse ; rend leurs noms."""
    noms = []
    for casier in (a._tissus, a._fils, a._durs):
        for cle, j in list(casier.items()):
            parties = [p for p in j.pieces if not garder(p)]
            if parties:
                noms += [p["nom"] for p in parties]
                j.pieces = [p for p in j.pieces if garder(p)]
                if not j.pieces:
                    del casier[cle]
    return noms


def _oreilles_douces(a, liens, X, Q):
    """L'intérieur des oreilles (INTERIEURS) : au lieu d'une pièce de feutrine posée (des triangles plats de plastique,
    Principal, 15/10), la peau qu'elle couvrait prend sa couleur (le pelage, sans arête) et se creuse en douceur (au plus
    0,3 fois l'épaisseur de l'oreille) ; la pièce est retirée. X : les points finals de la peau (numéros de P)."""
    T = _triangles(Q)
    if _volume(X, T) < 0:
        T = T[:, [0, 2, 1]]
    n = len(X)
    E = _aretes(T)
    deg = np.maximum(np.bincount(E[:, 0], minlength=n) + np.bincount(E[:, 1], minlength=n), 1).astype(float)
    nv = _normales(X, T)
    couvert = np.zeros(n, bool)
    teinte = {}
    pieces = []
    for cle, j in a._tissus.items():
        for p in j.pieces:
            if p["nom"].lower().startswith(INTERIEURS) and not p.get("fusion") and len(p["monde"]):
                c = np.asarray(cle[0], float) if cle[0] is not None else np.asarray(p["teinte"], float).reshape(-1, 3).mean(axis=0)
                pieces.append((p, c))
    if not pieces:
        return []
    faites = []
    for p, c in pieces:
        Y = p["monde"]
        D = float(np.ptp(Y, axis=0).max())
        arbre = BVHTree.FromPolygons(Y.tolist(), [tuple(int(i) for i in f) for f in p["faces"]])
        idx = _dans(X, Y.min(axis=0), Y.max(axis=0), 0.3 * D)
        ici = []
        for i, x, nn in zip(idx.tolist(), X[idx].tolist(), nv[idx].tolist()):
            o = Vector(x) + Vector(nn) * D                           # vu de dehors : la pièce est-elle devant ce point ?
            r = arbre.ray_cast(o, -Vector(nn), D + 0.002 * D)
            if r[0] is not None:
                ici.append(i)
        if ici:
            ici = np.array(ici, np.int64)
            couvert[ici] = True
            for i in ici.tolist():
                teinte[i] = c
            faites.append("%s (%d points)" % (p["nom"], len(ici)))
    if not couvert.any():
        return [nm + " (rien dessous, laissée)" for nm in (p["nom"] for p, _c in pieces)]
    # le creux : doux au bord, au plus 0,3 fois l'épaisseur de l'oreille sous chaque point
    w = couvert.astype(float)
    for _ in range(4):
        w = 0.5 * w + 0.5 * _voisins(w, E, deg)
    w = np.clip((w - 0.15) / 0.85, 0.0, 1.0)
    w = w * w * (3 - 2 * w)
    zone = np.nonzero(w > 0.01)[0]
    arbre_peau = BVHTree.FromPolygons(X.tolist(), T.tolist())
    ep = np.zeros(n)
    for i, x, nn in zip(zone.tolist(), (X[zone] - nv[zone] * 1e-4).tolist(), (-nv[zone]).tolist()):
        r = arbre_peau.ray_cast(x, nn, 1.0)
        ep[i] = r[3] if r[0] is not None else 0.0
    X = X.copy()
    X[zone] -= nv[zone] * (0.3 * ep[zone] * w[zone])[:, None]
    for q, vidx in liens:                                            # la peau prend la couleur et la forme
        q["monde"] = X[vidx].copy()
        t_ = np.asarray(q["teinte"], float).copy()
        for k, i in enumerate(vidx.tolist()):
            if i in teinte:
                t_[k] = teinte[i]
        q["teinte"] = t_
    retirees = {id(p) for p, _c in pieces}
    _retirer(a, lambda q: id(q) not in retirees)
    return faites


def _repeser(p, n):
    """Une pièce refaite avec n points : sa teinte et ses poids d'os (la moyenne de chacun) suivent."""
    p["teinte"] = np.tile(np.asarray(p["teinte"], float).reshape(-1, 3).mean(axis=0), (n, 1))
    if p.get("poids"):
        p["poids"] = {o: np.full(n, float(np.mean(w))) for o, w in p["poids"].items()}


def _paupieres_ouvertes(a):
    """Sur la base gonflée, les paupières lourdes (« lourde… ») refaites : le bord à COUPE_MIN rayon au moins au-dessus du
    milieu de l'œil, fines (EPAISSEUR_PAUPIERE rayon), le bord horizontal. l'auteur (15/10) : jamais d'œil mi-clos ni grognon ;
    une paupière épaisse cache l'œil vu de trois quarts. Rend la liste « nom : coupe avant -> après »."""
    sourcils = ["%s retiré" % nm for nm in _retirer(a, lambda p: p.get("fusion") or not p["nom"].lower().startswith(SOURCILS))]
    if PAUPIERES_LOURDES == "retirer":                               # l'œil ouvert, sans trait au-dessus (Principal, 15/10)
        return sourcils + ["%s retirée" % nm for nm in _retirer(a, lambda p: p.get("fusion") or not p["nom"].lower().startswith("lourde"))]
    import atelier as A
    e = float(a.echelle)
    toutes = a._toutes()
    yeux = []
    for nom, pos, vers, r, paire in a._boutons:
        for k, nm in enumerate([nom + "_G", nom + "_D"] if paire else [nom]):
            ps = [p for p in toutes if p["nom"] == nm]
            if not ps:
                continue
            z = np.array(vers, float) * ([1.0, 1.0, 1.0] if k == 0 else [-1.0, 1.0, 1.0])
            yeux.append((np.vstack([p["monde"] for p in ps]).mean(axis=0), z / max(np.linalg.norm(z), 1e-12), float(r) * e))
    faites = []
    if not yeux:
        return sourcils
    boule = A.boule(1.0, 32, 16)
    for p in toutes:
        if not p["nom"].lower().startswith("lourde") or not len(p["monde"]):
            continue
        m = p["monde"].mean(axis=0)
        c, z, R = min(yeux, key=lambda y_: float(np.linalg.norm(y_[0] - m)))
        if np.linalg.norm(c - m) > 2.5 * R:
            continue
        x = np.cross([0.0, 0.0, 1.0], z)
        if np.linalg.norm(x) < 1e-6:
            x = np.cross([0.0, 1.0, 0.0], z)
        x /= np.linalg.norm(x)
        y = np.cross(z, x)
        avant = float(((p["monde"] - c) @ y).min() / R)              # la coupe d'aujourd'hui (le bas de la paupière)
        coupe = min(max(COUPE_MIN, avant), 0.9)
        s = boule.v * [1.30 * R, 1.30 * R, EPAISSEUR_PAUPIERE * R]
        s[:, 1] = np.maximum(s[:, 1], coupe * R)
        p["monde"] = c + s[:, 0:1] * x + s[:, 1:2] * y + s[:, 2:3] * z
        p["loc"] = s / e
        p["faces"] = [tuple(int(i) for i in f) for f in boule.f]
        _repeser(p, len(s))
        faites.append("%s %.2f -> %.2f" % (p["nom"], avant, coupe))
    return sourcils + faites


def _moustaches(a, peau):
    """Sur la base gonflée, les moustaches (MOUSTACHES) refaites souples : le même départ et la même direction, mais elles
    retombent en courbe (un quart de leur longueur au bout) et s'affinent jusqu'au tiers de leur épaisseur. Rend leur nombre."""
    import atelier as A
    V, F, d = [], [], 0
    for p in peau:
        V.append(p["monde"])
        F += [tuple(i + d for i in f) for f in p["faces"]]
        d += len(p["monde"])
    arbre = _ecorce(np.vstack(V), F)
    e = float(a.echelle)
    faites = 0
    for p in a._toutes():
        if p.get("fusion") or not p["nom"].lower().startswith(MOUSTACHES) or len(p["monde"]) < 8:
            continue
        X = np.asarray(p["monde"], float)
        if (len(X) - 2) % 6 == 0 and len(X) >= 14:                   # un fil brodé (A.tube à 6 côtés) : ses anneaux
            anneaux = X[:-2].reshape(-1, 6, 3)
            chemin = anneaux.mean(axis=1)
            rayon = float(np.median(np.linalg.norm(anneaux - chemin[:, None, :], axis=2)))
        else:                                                        # autre chose : de bout en bout, en ligne droite
            c0 = X.mean(axis=0)
            axe = np.linalg.svd(X - c0, full_matrices=False)[2][0]
            t_ = (X - c0) @ axe
            chemin = np.array([X[int(np.argmin(t_))], X[int(np.argmax(t_))]])
            rayon = float(np.median(np.linalg.norm((X - c0) - np.outer(t_, axe), axis=1)))
        if (arbre.find_nearest(chemin[-1].tolist())[3] or 0.0) < (arbre.find_nearest(chemin[0].tolist())[3] or 0.0):
            chemin = chemin[::-1]                                    # la racine d'abord (le bout le plus près de la peau)
        long_ = float(np.linalg.norm(np.diff(chemin, axis=0), axis=1).sum())
        if long_ < 1e-6:
            continue
        if len(chemin) < 3:
            chemin = np.array([chemin[0] + (chemin[-1] - chemin[0]) * u for u in np.linspace(0.0, 1.0, 4)])
        u = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(chemin, axis=0), axis=1))]) / long_
        chemin = chemin + np.outer(0.25 * long_ * u ** 2, [0.0, 0.0, -1.0])     # elle retombe, de plus en plus vers le bout
        chemin = A.courbe(chemin, 4)
        r0 = 0.85 * rayon
        m = A.tube(chemin, lambda f: r0 * (1.0 - 0.67 * f), 6)
        p["monde"] = np.asarray(m.v, float)
        p["loc"] = p["monde"] / e
        p["faces"] = [tuple(int(i) for i in f) for f in m.f]
        _repeser(p, len(m.v))
        faites += 1
    return faites


def _champ(P, T, U):
    """Le déplacement U de la peau P, prolongé à tout point : celui du point de la peau (d'avant) le plus proche."""
    arbre = BVHTree.FromPolygons(P.tolist(), T.tolist())

    def champ(X):
        X = np.asarray(X, float).reshape(-1, 3)
        q = np.zeros_like(X)
        fi = np.full(len(X), -1, np.int64)
        for k, x in enumerate(X.tolist()):
            r = arbre.find_nearest(x)
            if r[0] is not None:
                q[k], fi[k] = r[0], r[2]
        sortie = np.zeros_like(X)
        ok = fi >= 0
        if not ok.any():
            return sortie
        tri = T[fi[ok]]
        a_, b_, c_ = P[tri[:, 0]], P[tri[:, 1]], P[tri[:, 2]]
        v0, v1, v2 = b_ - a_, c_ - a_, q[ok] - a_
        d00, d01, d11 = (v0 * v0).sum(1), (v0 * v1).sum(1), (v1 * v1).sum(1)
        d20, d21 = (v2 * v0).sum(1), (v2 * v1).sum(1)
        den = d00 * d11 - d01 * d01
        sur = np.abs(den) > 1e-30
        den = np.where(sur, den, 1.0)
        wv = np.where(sur, (d11 * d20 - d01 * d21) / den, 1.0 / 3.0)
        ww = np.where(sur, (d00 * d21 - d01 * d20) / den, 1.0 / 3.0)
        w = np.clip(np.stack([1.0 - wv - ww, wv, ww], axis=1), 0.0, 1.0)
        w /= np.maximum(w.sum(axis=1, keepdims=True), 1e-12)
        sortie[ok] = w[:, 0:1] * U[tri[:, 0]] + w[:, 1:2] * U[tri[:, 1]] + w[:, 2:3] * U[tri[:, 2]]
        return sortie
    return champ


def _suivre(a, liens, P, X, Q, h, L):
    """La peau gonflée prend sa place ; les yeux (et ce qui leur est collé) suivent d'un seul geste, le même des deux côtés
    pour une paire ; une pièce qui épouse la peau (rustine, couture, ourlet) la suit point par point, les autres (truffe,
    griffes, dents, moustaches) d'un seul geste, celui de leur point le plus proche de la peau."""
    T = _triangles(Q)
    if _volume(P, T) < 0:
        T = T[:, [0, 2, 1]]
    champ = _champ(P, T, X - P)
    for p, vidx in liens:
        p["monde"] = X[vidx].copy()                                  # « loc » (le repère du tissu) reste celui d'avant
    deja = {id(p) for p, _v in liens}
    e = float(a.echelle)
    yeux, boutons = [], []
    gestes = {}
    for nom, pos, vers, r, paire in a._boutons:
        cs = [np.array(pos, float) * e]
        if paire:
            cs.append(cs[0] * [-1.0, 1.0, 1.0])
        ds = champ(np.array(cs))
        if paire:
            m = 0.5 * (ds[0] + ds[1] * [-1.0, 1.0, 1.0])
            ds = np.array([m, m * [-1.0, 1.0, 1.0]])
        gestes[nom] = (cs, ds, np.array(vers, float))
    for nom in list(gestes):                     # deux yeux posés un à un (« _G », « _D ») : à la même hauteur sur la peau
        autre = nom[:-2] + "_D"
        if nom.endswith("_G") and autre in gestes and len(gestes[nom][1]) == 1 and len(gestes[autre][1]) == 1:
            (cg, dg, ng), (cd, dd, nd) = gestes[nom], gestes[autre]
            s = 0.5 * (float(dg[0] @ ng) + float(dd[0] @ nd))
            gestes[nom] = (cg, dg + (s - float(dg[0] @ ng)) * ng, ng)
            gestes[autre] = (cd, dd + (s - float(dd[0] @ nd)) * nd, nd)
    for nom, pos, vers, r, paire in list(a._boutons):
        cs, ds, _n = gestes[nom]
        for c, d in zip(cs, ds):
            for p in a._toutes():
                if p.get("fusion") or id(p) in deja:
                    continue
                if np.linalg.norm(p["monde"].mean(axis=0) - c) < 1.8 * r * e and np.ptp(p["monde"], axis=0).max() < 4.5 * r * e:
                    p["monde"] = p["monde"] + d
                    deja.add(id(p))
        yeux.append("%s %.1f mm" % (nom, 1000 * np.linalg.norm(ds[0])))
        boutons.append((nom, Vector(np.array(pos, float) + ds[0] / e), vers, r, paire))
    a._boutons = boutons
    arbre = BVHTree.FromPolygons(P.tolist(), T.tolist())
    colle = max(3.0 * h, 0.012 * L)
    suit, geste = 0, 0
    for p in a._toutes():
        if p.get("fusion") or id(p) in deja or not len(p["monde"]):
            continue
        Xp = p["monde"]
        dist = np.array([(arbre.find_nearest(x)[3] or 0.0) for x in Xp.tolist()])
        if np.percentile(dist, 80) < colle or float(np.ptp(Xp, axis=0).max()) > 0.15 * L:   # une grande pièce (les piquants)
            p["monde"] = Xp + champ(Xp)
            suit += 1
        else:
            p["monde"] = Xp + champ(Xp[int(np.argmin(dist))])[0]
            geste += 1
        deja.add(id(p))
    if a.tete is not None:
        a.tete = Vector(np.array(a.tete, float) + champ(np.array(a.tete, float))[0])
    a._champ_gonflage = champ
    _dire("gonflage posé : yeux %s ; %d pièces suivent la peau point par point, %d d'un seul geste" % (
        ", ".join(yeux) or "aucun", suit, geste))


def os_suivent(a, liste, k, garder=()):
    """Les os posés sur la peau (paupières, épingles) suivent le gonflage : liste de (nom, parent, tête) dans les mesures du
    modèle (avant a.taille, facteur k). Ceux de « garder » (les os de la bête) ne bougent pas."""
    champ = getattr(a, "_champ_gonflage", None)
    if champ is None:
        return liste
    sortie = []
    for n, parent, t in liste:
        if n in garder:
            sortie.append((n, parent, t))
            continue
        d = champ(np.array(t, float) * k)[0] / k
        sortie.append((n, parent, tuple(float(x) for x in np.array(t, float) + d)))
    return sortie


# ---------------------------------------------------------------- 4. le soudage du maillage du jeu (usine.monter_bas)

def souder(ob, pieces):
    """Les pièces de la peau (une par tissu) se touchent bord à bord : on soude leurs points communs avant d'alléger,
    pour que le maillage du jeu n'ait pas de fente entre le poil et la feutrine."""
    import bmesh
    debut, plages = 0, []
    for p in pieces:
        if p.get("fusion"):
            plages.append(np.arange(debut, debut + len(p["monde"])))
        debut += len(p["monde"])
    if not plages:
        return 0
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    vs = [bm.verts[int(i)] for i in np.concatenate(plages)]
    avant = len(bm.verts)
    taille = max(ob.dimensions) if max(ob.dimensions) > 0 else 1.0
    bmesh.ops.remove_doubles(bm, verts=vs, dist=1e-6 * taille)
    apres = len(bm.verts)
    bm.to_mesh(ob.data)
    bm.free()
    return avant - apres
