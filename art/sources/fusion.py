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
DURS = ("griffe", "croc", "dent", "ongle", "nez", "truffe", "ourlet", "interieur", "dedans_")
# posés sur la peau fondue, pas fondus dedans, et recollés d'un seul geste (essais du 15/10 : des taches blanches aux griffes,
# la truffe du raton tombée sous la bouche, l'intérieur des oreilles froissé comme du papier par les voxels)
CONGE = 0.60            # le rayon du congé : cette part de l'épaisseur du plus fin des deux morceaux (0,30 : trop peu de gain, 15/10)
CONGE_MIN = 1.5         # ... au moins ce nombre de voxels
CONGE_MAX = 0.12        # ... au plus cette part de la bête
TROP_FIN = 2.5          # un morceau plus fin que ce nombre de voxels reste à part
LISSAGE = 18            # passes de lissage (6 : les formes restaient géométriques, 15/10)
TRIANGLES = (20000, 120000)   # la peau finale : le nombre de triangles d'origine, entre ces bornes


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
        self.tris = _triangles(faces)
        self.aire, self.volume = _mesures(self.v, self.tris)
        self.epais = 4.0 * self.volume / max(self.aire, 1e-12)
        self.bas, self.haut = self.v.min(axis=0), self.v.max(axis=0)
        self.arbre = None

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
    """Une copie de la pièce réduite à quelques-uns de ses morceaux (ceux qui restent à part)."""
    vidx = np.unique(np.concatenate([m.vidx for m in morceaux]))
    loc = np.full(len(p["monde"]), -1, np.int64)
    loc[vidx] = np.arange(len(vidx))
    q = dict(p)
    q["monde"], q["loc"], q["teinte"] = p["monde"][vidx], p["loc"][vidx], np.asarray(p["teinte"])[vidx]
    q["faces"] = [tuple(int(loc[m.vidx[i]]) for i in f) for m in morceaux for f in m.f]
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


def fusionner(a):
    """La peau d'une seule pièce (voir le haut du fichier). À appeler une fois l'animal à sa taille ; dans l'usine,
    après porter() (les os de chaque pièce) et le calcul des os des paupières. Rend le nombre de pièces fondues."""
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
    nouvelles = _habiller(a, P, Q, M, h, L)
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
    _dire("fini en %.1f s" % (time.time() - t0))
    return len(fondues)


def _habiller(a, P, Q, M, h, L):
    """Couleur, tissu, longueur du poil et poids des os de chaque point de la peau, pris aux morceaux d'origine.
    Rend {clé du tissu : [pièces]} (une pièce par tissu et par longueur de poil)."""
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

    def ecart(q, n, portee):
        """De combien la peau est sortie (ou rentrée) le long de n, au-dessus des points q de la surface d'avant."""
        de = np.zeros(len(q))
        for k_, (qq, nn) in enumerate(zip(q.tolist(), n.tolist())):
            if nn == [0.0, 0.0, 0.0]:
                continue
            o = Vector(qq) + Vector(nn) * portee
            r = arbre_peau.ray_cast(o, -Vector(nn), 2 * portee)
            if r[0] is not None:
                de[k_] = portee - r[3]
        de[(de > bosse_max) | (de < -2 * h)] = 0.0                      # touché autre chose (un bras devant le corps)
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
    # les pièces posées (truffe, griffes, dents, ourlets) : chacune d'un seul geste, le long de la peau sous elle
    posees = []
    for p in a._toutes():
        if p.get("fusion") or id(p) in deja or not p["nom"].lower().startswith(DURS):
            continue
        X = p["monde"]
        c = X.mean(axis=0)
        dist, q, n = vieille_surface(c[None], portee + 0.5 * float(np.ptp(X, axis=0).max()))
        if abs(dist[0]) >= portee + 0.5 * float(np.ptp(X, axis=0).max()) or not n[0].any():
            continue
        de = ecart(q, n, portee)[0]
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


# ---------------------------------------------------------------- 3. le soudage du maillage du jeu (usine.monter_bas)

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
