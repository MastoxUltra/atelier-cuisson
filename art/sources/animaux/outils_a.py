"""Les petits outils de la session Sœur A (Animaux 2) : les gestes qui reviennent d'un animal à l'autre, rangés ici pour
que chaque fichier d'animal reste court. Ce n'est PAS le kit commun (peluche.py, atelier.py…) : il vit à côté des animaux,
et chaque fichier qui s'en sert ajoute son dossier au chemin :

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import outils_a as O

Rien ici ne touche au kit : tout est écrit avec ses fonctions.
"""
import math

import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import peluche as K


# ----- le garde-fou : A.tube divise par la longueur de chaque segment. Deux points confondus à la suite (un tracé de
# broderie qui retombe sur le même sommet, un courbe() dont le premier et le dernier coïncident) donnent des NaN, la
# boîte de l'animal devient NaN et la fiche sort vide : « seulement du ciel ». On retire donc les points confondus ;
# s'il n'en reste qu'un, un moignon minuscule. Le vrai Blender n'a pas la même lancée que le faux de la maquette.
_tube_origine = A.tube


def _tube_sur(chemin, rayon, cotes=10):
    """A.tube sans division par zéro : points non finis écartés ; points confondus (à 0,1 mm) fondus en un ; pointes (un point
    dont les deux voisins se confondent : l'aller-retour A, B, A) retirées ; jamais moins de deux points."""
    ch = np.asarray(chemin, float).reshape(-1, 3)
    ch = ch[np.isfinite(ch).all(axis=1)]
    change = True
    while change and len(ch) >= 2:
        change = False
        garde_ = [0]
        for i in range(1, len(ch)):
            if np.linalg.norm(ch[i] - ch[garde_[-1]]) > 1e-4:
                garde_.append(i)
        if len(garde_) != len(ch):
            ch = ch[garde_]
            change = True
        for i in range(1, len(ch) - 1):
            if np.linalg.norm(ch[i + 1] - ch[i - 1]) < 1e-4:
                ch = np.delete(ch, i, axis=0)
                change = True
                break
    if len(ch) < 2:
        base = ch[0] if len(ch) else np.zeros(3)
        ch = np.vstack([base, base + np.array([0.0, 0.0, 1e-3])])
    return _tube_origine(ch, rayon, cotes)


if A.tube is _tube_origine:
    A.tube = _tube_sur


def gauss(x):
    return np.exp(-np.asarray(x) ** 2)


def couche(m, mat):
    """Pose une maille par une matrice 4×4 (A.cadre) : le repère de la pièce devient celui de la matrice."""
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def teinte(m, couleur):
    m.teinte = np.tile(np.asarray(couleur, float), (len(m.v), 1))
    return m


def membre(points, rayons, paliers, cotes=18):
    """Une patte ou un bras : un boudin qui passe par ses articulations, un rayon à chacune, peint par tronçons."""
    nodes = np.linspace(0, 1, len(rayons))
    return K.tube_peint(A.courbe(points, 6), lambda t: float(np.interp(t, nodes, rayons)), paliers, cotes)


def tube_r(points, rayons, cotes=14, pas=6):
    """Un tube lissé dont le rayon est donné à chaque point."""
    nodes = np.linspace(0, 1, len(rayons))
    return A.tube(A.courbe(points, pas), lambda t: float(np.interp(t, nodes, rayons)), cotes)


def pointe(long, base, cotes=10):
    """Un petit cône arrondi (une épine, une griffe, une dent) : pied sur z = 0, bout en z = long."""
    return A.tour(A.profil([(base, 0), (0.72 * base, 0.30 * long), (0.36 * base, 0.66 * long), (0.12 * base, 0.90 * long), (0, long)], 3), cotes)


def griffe(long, base):
    """Une griffe : un cône un peu courbé vers le bas."""
    m = pointe(long, base, 8)
    return m.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] - 0.45 * long * (v[:, 2] / long) ** 2, v[:, 2]], axis=1))


def fil_corps(a, nom, chemin, rayon_f, teinte_f=None, couleur=None, cotes=40, pas=10, flanc=(-1.0, 0.0, 0.0), deforme=None, poil=True):
    """Un corps long (poisson, serpent, cou) : un fuseau tourné dont le rayon est rayon_f(fraction), peint par teinte_f(maille, L),
    couché le long d'un fil. Rend (fil, longueur). Le dos est en haut quand le chemin va vers +Y avec flanc = (-1, 0, 0),
    ou vers -Y avec flanc = (1, 0, 0)."""
    fil = K.Fil(chemin, flanc=flanc, pas=pas)
    L = fil.long
    fs = np.linspace(0.0, 1.0, 160)
    prof = [(0.0, 0.0)] + [(float(rayon_f(f)), float(f * L)) for f in fs[1:-1]] + [(0.0, L)]
    m = A.tour(prof, cotes)
    if teinte_f is not None:
        m.teinte = teinte_f(m, L)
    if deforme is not None:
        m = m.sculpte(deforme(L))
    a.piece(nom, m.sculpte(fil.couche), couleur, poil=poil)
    return fil, L


def interp(points):
    """Une fonction de la fraction f, qui interpole des couples (fraction, valeur)."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return lambda f: float(np.interp(f, xs, ys))


def bandes_z(m, L, couleurs, f0=0.0, f1=1.0):
    """Des tronçons de couleur le long d'un corps tourné (z de la pièce) : couleurs = [(fraction_fin, couleur), …]."""
    t = np.zeros((len(m.v), 3))
    f = m.v[:, 2] / L
    reste = np.ones(len(f), bool)
    for fin, c in couleurs:
        ici = reste & (f <= fin)
        t[ici] = c
        reste &= ~ici
    t[reste] = couleurs[-1][1]
    return t


def moucheter(m, base, points, graine=1, nombre=80, taille=0.10, depart=None):
    """Des taches rondes (taille en radian sur la sphère unité de la pièce) semées sur une teinte de base."""
    u = m.v / np.maximum(np.linalg.norm(m.v - m.v.mean(axis=0), axis=1, keepdims=True), 1e-9)
    u = (m.v - m.v.mean(axis=0))
    u = u / np.maximum(np.linalg.norm(u, axis=1, keepdims=True), 1e-9)
    rng = np.random.default_rng(graine)
    g = rng.normal(size=(nombre, 3))
    g /= np.linalg.norm(g, axis=1, keepdims=True)
    proche = u @ g.T > np.cos(taille * rng.uniform(0.7, 1.3, nombre))[None, :]
    t = np.tile(np.asarray(base, float), (len(u), 1)) if depart is None else depart
    t[proche.any(axis=1)] = points
    return t


def nageoire(contour, ep, couleur, casse=0.010):
    """Une nageoire plate découpée dans un contour (x, y) : l'extrusion est sur Z. À poser avec couche(…, A.cadre(pos, normale_plan, haut))."""
    m = A.decoupe(contour, ep, casse)
    return teinte(m, couleur)


def paire_yeux(a, piece, centre, direction_g, rayon, fermee=None, couleur_lourde=None, coupe=0.60, haut=(0, 0, 1), decolle=0.002, nom="oeil", vivant=True, R=None):
    """Deux yeux symétriques (bouton : le style en fait un bouton à croix, un œil de feutrine ou une bille de verre).
    direction_g : où viser, depuis centre, pour l'œil gauche (+X) ; le droit est son miroir sur X.
    couleur_lourde : si donnée, une paupière lourde de cette couleur ; coupe : sa coupe (0 : à moitié fermé)."""
    for suffixe, c in (("_G", 1), ("_D", -1)):
        d = Vector((c * direction_g[0], direction_g[1], direction_g[2]))
        if R is not None:                                                    # la tête est tournée : les yeux restent symétriques DANS elle
            d = R.to_3x3() @ d
        pos, n = a.surface(piece, centre, d)
        if vivant:
            a.oeil(nom + suffixe, pos + n * decolle, n, rayon)                 # un œil vivant de feutrine, avec son reflet
        else:
            a.bouton(nom + suffixe, pos + n * decolle, n, rayon)               # un bouton : seulement pour les insectes et les bestioles
        if couleur_lourde is not None:
            h = Vector(haut)
            h = (h - n * n.dot(h)).normalized()
            a.piece("lourde" + suffixe, K.paupiere(rayon, coupe), tuple(couleur_lourde), mat=A.cadre(pos + n * decolle, n, h), poil=False)


def broder(a, nom, piece, centre, directions, rayon, couleur, decolle=0.003, lisse=4, R=None):
    ds = [Vector(d) for d in directions]
    if R is not None:
        ds = [R.to_3x3() @ d for d in ds]
    pts = a.trace(piece, centre, ds, decolle)
    if len(pts) >= 2:
        a.broderie(nom, A.courbe(pts, lisse), rayon, couleur)
    return pts


def plan_vertical(pos, tangente):
    """Le repère d'une nageoire de queue : son plan (x, y) est le plan vertical du poisson, son x suit la tangente (le contour
    part dans le sens où le corps continue), son épaisseur est sur X."""
    t = Vector(tangente).normalized()
    haut = Vector((0.0, -t.z, t.y))
    return A.cadre(Vector(pos), Vector((1.0, 0.0, 0.0)), haut)


def plan_dos(pos, haut=(0, 0, 1)):
    """Le repère d'une nageoire du dos ou du ventre : x vers l'arrière (+Y), y vers le haut, épaisseur sur X."""
    return A.cadre(Vector(pos), Vector((1.0, 0.0, 0.0)), Vector(haut))


def oiseau(a, *, dos, ventre, tete, aile, queue, bec, patte, long=0.34, ray=0.11, incline=30.0, z0=0.12,
           tete_r=(0.062, 0.072, 0.060), tete_pos=(0.0, -0.10, 0.06), bec_long=0.07, bec_ray=0.024, bec_baisse=0.0,
           aile_dim=(0.022, 0.085, 0.180), aile_pos=(0.0, 0.0, 0.0), queue_dim=(0.040, 0.085, 0.014), queue_haut=-24.0,
           patte_long=0.10, patte_ray=0.011, oeil_r=0.016, oeil_dir=(0.74, -0.58, 0.22), bout_aile=None, coupe_dos=1.20, yeux=True, tete_rot=(-6, 0, 0), cou_ray=0.0, aile_pointue=False, bec_suit=False, peint_corps=None, peint_tete=None):
    """Un oiseau debout, d'une seule volée : un œuf incliné (le dos d'une couleur, le ventre d'une autre), une tête ronde,
    un bec en cône, deux ailes plates, une queue plate, deux pattes minces. Rend un dictionnaire de repères pour que
    l'appelant ajoute ce qui fait SON oiseau (huppe, queue en ciseaux, plastron, masque…) :
        {"T": le repère du corps, "haut": le haut du corps, "H": le centre de la tête, "a": le nom de la pièce tête}"""
    pc = A.profil([(0, 0.0), (0.55 * ray, 0.010), (0.90 * ray, 0.070 * long / 0.34), (ray, 0.160 * long / 0.34),
                   (0.88 * ray, 0.250 * long / 0.34), (0.62 * ray, 0.315 * long / 0.34), (0.34 * ray, 0.350 * long / 0.34),
                   (0, 0.362 * long / 0.34)], 6)
    corps = A.tour(pc, 40)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(np.asarray(ventre, float), (len(ang), 1))
    t[(ang < coupe_dos) & (corps.v[:, 2] > 0.03)] = np.asarray(dos, float)
    if peint_corps is not None:                       # un plastron, un masque : la couleur par point, sans boule posée dessus
        t = peint_corps(corps, t)
    corps.teinte = t
    T = A.repere((0.0, 0.040, z0), (incline, 0, 0))
    a.piece("corps", corps, None, mat=T)
    haut = Vector(T @ Vector((0, 0, 0.345 * long / 0.34)))
    H = haut + Vector(tete_pos)
    tt = A.boule(1.0, 40, 20)
    tt.teinte = np.tile(np.asarray(tete, float), (len(tt.v), 1))
    if peint_tete is not None:
        tt.teinte = peint_tete(tt, tt.teinte)
    a.piece("tete", tt.etire(*tete_r), None, pos=tuple(H), rot=tete_rot)
    if cou_ray > 0:                                   # un cou : la tête est emmanchée sur le corps, plus une boule posée dessus
        P0 = Vector(T @ Vector((0, 0, 0.250 * long / 0.34)))
        P2 = H + Vector((0.0, 0.020, -0.006))
        P1 = (P0 + P2) * 0.5 + Vector((0.0, -0.018, 0.0))
        cou = tube_r([tuple(P0), tuple(P1), tuple(P2)], [cou_ray * 1.30, cou_ray * 1.05, cou_ray * 0.92], 20)
        cou.teinte = np.tile(np.asarray(tete, float), (len(cou.v), 1))
        a.piece("cou", cou, None)
    a.tete = H + Vector((0.0, -0.08, 0.0))
    # le bec
    b = A.tour(A.profil([(bec_ray, 0), (0.88 * bec_ray, 0.30 * bec_long), (0.52 * bec_ray, 0.65 * bec_long), (0.18 * bec_ray, 0.92 * bec_long),
                         (0, bec_long)], 3), 20).etire(0.82, 0.70, 1.0)
    if bec_suit:                                      # le bec suit la tête tournée : bien attaché, jamais posé à côté
        a.piece("bec", couche(b, A.repere(H, tete_rot) @ A.cadre(Vector((0.0, -tete_r[1] * 0.90, -0.004)), (0.0, -1.0, bec_baisse), (0, 1.0, 0))), bec, poil=False)
    else:
        a.piece("bec", couche(b, A.cadre(H + Vector((0.0, -tete_r[1] * 0.92, -0.004)), (0.0, -1.0, bec_baisse), (0, 1.0, 0))), bec, poil=False)
    if yeux:
        paire_yeux(a, "tete", H, oeil_dir, oeil_r, decolle=0.002)
    # les ailes
    for nom, c in (("G", 1), ("D", -1)):
        al = A.boule(1.0, 28, 14).etire(*aile_dim)
        f = al.v[:, 2] / aile_dim[2]
        if aile_pointue:                                  # une aile qui s'effile en pointe et se bombe, pas un ovale plat
            bout = np.clip((-f - 0.05) / 0.95, 0.0, 1.0)
            al = al.sculpte(lambda v: np.stack([v[:, 0] * (1 - 0.30 * np.clip(-v[:, 2] / aile_dim[2], 0, 1)) * (1.55 - 0.9 * 0) / 1.55,
                                                v[:, 1] * (1 - 0.75 * np.clip((-v[:, 2] / aile_dim[2] - 0.05) / 0.95, 0, 1) ** 1.4),
                                                v[:, 2]], axis=1))
            f = al.v[:, 2] / aile_dim[2]
        tl = np.tile(np.asarray(aile, float), (len(f), 1))
        if bout_aile is not None:
            tl[f < -0.55] = np.asarray(bout_aile, float)
        al.teinte = tl
        a.piece("aile_" + nom, al, None, mat=T @ A.repere((c * (ray * 0.97 + aile_pos[0]), aile_pos[1], 0.165 * long / 0.34 + aile_pos[2]),
                                                          (0, 0, c * 5)))
    q = A.boule(1.0, 24, 12).etire(*queue_dim)
    q.teinte = np.tile(np.asarray(queue, float), (len(q.v), 1))
    a.piece("queue", q, None, pos=(0.0, 0.040 + 0.52 * long, z0 + 0.04 * long), rot=(queue_haut, 0, 0))
    # les pattes
    for nom, c in (("G", 1), ("D", -1)):
        jb = tube_r([(c * 0.036, 0.040, z0 + 0.02), (c * 0.040, 0.012, patte_long * 0.5), (c * 0.042, -0.008, 0.010)],
                    [patte_ray, patte_ray * 0.9, patte_ray * 0.8], 8)
        a.piece("patte_" + nom, teinte(jb, patte), None, poil=False)
        pd = A.boule(1.0, 14, 8).etire(0.026, 0.044, 0.006)
        a.piece("pied_" + nom, teinte(pd, patte), None, pos=(c * 0.044, -0.034, 0.007), poil=False)
    return {"T": T, "haut": haut, "H": H}


def corps_h(a, nom, pos, L, rayon_f, teinte_f=None, couleur=None, cotes=44, deforme=None, pitch=0.0, taper=None):
    """Un corps de quadrupède couché le long de Y : un fuseau tourné (z de la croupe, z = 0, au poitrail, z = L) dont le rayon est
    rayon_f(fraction), posé en pos (le centre de la croupe), le poitrail devant (-Y), incliné de pitch° (le poitrail plus haut si > 0).
    teinte_f(maille, L) donne la teinte par point ; deforme(L) rend une fonction de sculpte. Le dos de la pièce est son +Y local."""
    fs = np.linspace(0.0, 1.0, 120)
    prof = [(0.0, 0.0)] + [(float(rayon_f(f)), float(f * L)) for f in fs[1:-1]] + [(0.0, L)]
    m = A.tour(prof, cotes)
    if teinte_f is not None:
        m.teinte = teinte_f(m, L)
    if deforme is not None:
        m = m.sculpte(deforme(L))
    p = math.radians(pitch)
    avant = Vector((0.0, -math.cos(p), math.sin(p)))
    haut = Vector((0.0, math.sin(p), math.cos(p)))
    a.piece(nom, m, couleur, mat=A.cadre(Vector(pos), avant, haut))
    return A.cadre(Vector(pos), avant, haut)


def patte(a, nom, points, rayons, couleur, bas=None, bas_frac=0.58, pied=(0.040, 0.075, 0.016), pied_couleur=None, cotes=18, decale=0.0):
    """Une patte de quadrupède : un boudin qui passe par ses points (rayon à chaque point), une chaussette de couleur 'bas' sous le
    genou (depuis la fraction bas_frac), et un pied plat à plat au sol sous le dernier point. Rend les points."""
    paliers = [(1.0, couleur)] if bas is None else [(bas_frac, couleur), (1.0, bas)]
    a.piece("patte_" + nom, membre(points, rayons, paliers, cotes), None)
    if pied is not None:
        fin = points[-1]
        pc = pied_couleur if pied_couleur is not None else (bas if bas is not None else couleur)
        pd = A.boule(1.0, 20, 10).sculpte(lambda v: K.emousse(v, 0.8)).etire(*pied)
        a.piece("pied_" + nom, teinte(pd, pc), None, pos=(fin[0], fin[1] - pied[1] * 0.35 + decale, pied[2] * 0.95), poil=False)
    return points


def tete_h(a, centre, rayons, couleur, museau_c=None, museau_r=(0.04, 0.05, 0.034), museau_dec=(0.0, -0.075, -0.020), nez_c=None,
           nez_r=(0.016, 0.012, 0.012), rot=(0, 0, 0), teinte_f=None, nom="tete"):
    """Une tête de mammifère : une boule étirée (rayons x, y, z), un museau rond posé devant, un nez. Rend la matrice de la tête."""
    t = A.boule(1.0, 48, 24)
    if teinte_f is not None:
        t.teinte = teinte_f(t)
    else:
        t.teinte = np.tile(np.asarray(couleur, float), (len(t.v), 1))
    a.piece(nom, t.etire(*rayons), None, pos=tuple(centre), rot=rot)
    R = A.repere(Vector(centre), rot)
    if museau_c is not None:
        m = A.boule(1.0, 32, 16).etire(*museau_r)
        a.piece("museau", teinte(m, museau_c), None, mat=R @ A.repere(museau_dec))
    if nez_c is not None:
        pos = R @ Vector((museau_dec[0], museau_dec[1] - museau_r[1] * 0.92, museau_dec[2] + museau_r[2] * 0.30))
        n = A.boule(1.0, 16, 8).etire(*nez_r)
        a.piece("nez", teinte(n, nez_c), None, pos=tuple(pos), poil=False)
    return R


def tourner(a, degres):
    """Tourne tout l'animal d'un bloc autour de la verticale (pour la FICHE seulement : mettre la constante TOURNE à 0 pour
    le jeu, c'est ce que verif_os.py réclame). Comme cheval.py : les pièces, la tête visée et les yeux déjà posés."""
    R = Matrix.Rotation(math.radians(degres), 3, "Z")
    Rn = np.array(R)
    for p in a._toutes():
        p["monde"] = p["monde"] @ Rn.T
    if a.tete is not None:
        a.tete = R @ Vector(a.tete)
    a._boutons = [(n, R @ p, R @ v, r, pr) for n, p, v, r, pr in a._boutons]


# ---------------------------------------------------------------- les pattes articulées et le gabarit du corps (15/10)

def points_jambe(haut, pied, sorte="av", plie=0.06):
    """Sept points de l'épaule (ou de la hanche) au haut du sabot : une jambe qui a un genou. 'av' : l'antérieur, le genou
    en avant ; 'ar' : le postérieur, le grasset en avant puis le jarret en arrière, comme un vrai Z. plie : de combien (m)."""
    h = np.asarray(haut, float)
    p = np.asarray(pied, float)
    pts = []
    for t in (0.0, 0.26, 0.46, 0.66, 0.84, 0.94, 1.0):
        q = h + (p - h) * t
        if sorte == "av":
            q[1] -= 0.9 * plie * math.sin(math.pi * min(t / 0.75, 1.0)) ** 1.3
        else:
            q[1] += plie * (-0.55 * math.exp(-((t - 0.24) / 0.13) ** 2) + 1.0 * math.exp(-((t - 0.54) / 0.15) ** 2)
                            - 0.20 * math.exp(-((t - 0.85) / 0.10) ** 2))
        pts.append(tuple(float(x) for x in q))
    return pts


RAYONS_AV = (1.00, 0.78, 0.66, 0.44, 0.52, 0.42, 0.40)       # l'épaule, le genou (3e) et le boulet (5e) gonflés
RAYONS_AR = (1.20, 0.88, 0.64, 0.42, 0.50, 0.42, 0.40)       # la cuisse, le jarret (3e)


def jambe(a, nom, haut, pied, R, couleur, bas=None, sorte="av", plie=0.06, bas_frac=0.56, pied_dim=None, griffes=0, couleur_griffe=None):
    """Une patte articulée complète : le tube à genou et boulet marqués (rayon R à l'épaule), la chaussette 'bas', un pied à plat
    sous le dernier point, des griffes en option. Rend les points."""
    pts = points_jambe(haut, pied, sorte, plie)
    ray = [R * k for k in (RAYONS_AV if sorte == "av" else RAYONS_AR)]
    dim = pied_dim if pied_dim is not None else (0.62 * R, 1.10 * R, 0.30 * R)
    patte(a, nom, pts, ray, couleur, bas=bas, bas_frac=bas_frac, pied=dim)
    if griffes:
        fin = np.asarray(pts[-1])
        cg = couleur_griffe if couleur_griffe is not None else (0.93, 0.88, 0.76)
        for k in range(griffes):
            dx = (k - (griffes - 1) / 2.0) * 0.5 * dim[0] * 1.5 / max(griffes - 1, 1)
            g = teinte(griffe(0.060 * R / 0.06 * 0.9, 0.012 * R / 0.06), cg)
            a.piece("griffe_%s%d" % (nom, k), couche(g, A.cadre(Vector((fin[0] + dx, fin[1] - dim[1] * 0.85, dim[2] * 1.6 + 0.012)), (0.0, -1.0, -0.06), (0, 0, 1))),
                    None, poil=False)
    return pts


def gabarit(poitrail=0.0, taille=0.0, croupe=0.0, garrot=0.0, ventre=0.0, pos_poitrail=0.80, pos_taille=0.42, pos_croupe=0.10):
    """Le gabarit d'un corps de quadrupède pour corps_h(deforme=…) : de combien le poitrail bombe, la taille se creuse, la
    croupe s'élargit, le garrot monte, le ventre se rentre (fractions, 0,1 = 10 %)."""
    def faire(L):
        def f(v):
            s = v.copy()
            fr = v[:, 2] / L
            g = lambda x: np.exp(-np.asarray(x) ** 2)
            s[:, 0] *= 1 + croupe * g((fr - pos_croupe) / 0.10) - taille * g((fr - pos_taille) / 0.14) + poitrail * g((fr - pos_poitrail) / 0.12)
            dev = v[:, 1] < 0
            s[dev, 1] *= (1 - ventre * g((fr - pos_taille) / 0.14) + poitrail * 1.2 * g((fr - pos_poitrail) / 0.10))[dev]
            s[~dev, 1] *= (1 + garrot * g((fr - (pos_poitrail + 0.02)) / 0.10) + 0.5 * croupe * g((fr - pos_croupe) / 0.10))[~dev]
            return s
        return f
    return faire


def plumes(base, axe, haut, n=3, long=0.075, ray=0.0085, couleur=(1.0, 0.4, 0.35), filaments=6):
    """Des branchies en plumes : n tiges en éventail depuis `base` le long de `axe` (écartées dans le plan que `haut` porte),
    chacune bordée de filaments de chaque côté. Rend une seule maille (à poser avec couleur=None)."""
    base = Vector(base)
    axe = Vector(axe).normalized()
    haut = Vector(haut)
    lat = axe.cross(haut).normalized()
    haut = lat.cross(axe).normalized()
    m = None
    for i in range(n):
        u = (i - (n - 1) / 2.0) / max((n - 1) / 2.0, 1.0)
        d = (axe + haut * (0.55 * u)).normalized()
        L = long * (1.0 - 0.18 * abs(u))
        tige = tube_r([tuple(base), tuple(base + d * L * 0.5 + lat * 0.004), tuple(base + d * L)], [ray, ray * 0.8, ray * 0.4], 8)
        tige = teinte(tige, couleur)
        m = tige if m is None else m + tige
        for k in range(filaments):
            t = 0.25 + 0.7 * k / max(filaments - 1, 1)
            p = base + d * (L * t)
            for s in (-1, 1):
                dd = (d * 0.55 + lat * (s * 0.85)).normalized()
                f = couche(teinte(pointe(L * 0.30 * (1.0 - 0.5 * t) + 0.010, ray * 0.55, 6), couleur), A.cadre(p, dd, haut))
                m = m + f
    return m


def plan(pos, ex, ey):
    """Le repère d'une pièce plate (une aile, une nageoire) : x le long de ex, y le long de ey (orthogonalisé), z leur normale."""
    x = Vector(ex).normalized()
    y = Vector(ey)
    y = (y - x * x.dot(y)).normalized()
    z = x.cross(y)
    m = Matrix.Identity(4)
    for i2, v in enumerate((x, y, z)):
        m[0][i2], m[1][i2], m[2][i2] = v
    m[0][3], m[1][3], m[2][3] = Vector(pos)
    return m


def sur_corps(fil, L, rayon_f, f, ang, cote=1, sx=1.0, sy=1.0, ext=0.0):
    """Un point de la surface d'un corps couché sur un fil (fil_corps), et sa normale, sans lancer de rayons : à la fraction f,
    l'angle ang (degrés, 0 : le dos, 180 : le ventre), du côté `cote` (+1 : le côté du flanc, -1 : l'autre) ; sx, sy : les facteurs
    d'aplatissement appliqués au corps (un déformé qui écrase X ou Y) ; ext : de combien au-dessus de la peau."""
    c, av, nq = (Vector(q) for q in fil.cadre(f * L))
    fl = Vector(fil.flanc).normalized()
    r = float(rayon_f(f))
    th = math.radians(ang)
    n = (fl * (cote * math.sin(th) / max(sx, 1e-6)) + nq * (math.cos(th) / max(sy, 1e-6))).normalized()
    p = c + fl * (cote * math.sin(th) * r * sx) + nq * (math.cos(th) * r * sy) + n * ext
    return p, n


def points_lumineux(pts_normales, rayon, couleur):
    """Une maille de petites pastilles posées à plat (photophores, pois) : pts_normales = [(point, normale), …]."""
    m = None
    for p, n in pts_normales:
        up = Vector((0.0, 0.0, 1.0)) if abs(n.z) < 0.9 else Vector((0.0, 1.0, 0.0))
        d = couche(teinte(A.boule(1.0, 10, 6).etire(rayon, rayon, rayon * 0.45), couleur), A.cadre(p, n, up))
        m = d if m is None else m + d
    return m


def pince(long, large, ouverture=34.0, couleur=None, bout=None):
    """Une pince dessinée (crabe, écrevisse, bernard) : la paume bombée, puis DEUX doigts qui s'effilent et se courbent l'un
    vers l'autre, séparés par un jour ; la pince regarde vers +Z (le doigt fixe en bas, le mobile ouvert de `ouverture`°).
    À poser avec couche(m, A.cadre(pos, direction, haut)). Pas de boule : la paume est aplatie, les doigts finissent en pointe."""
    L, W = long, large
    paume = A.boule(1.0, 28, 14).sculpte(lambda v: K.emousse(v, 0.88)).etire(0.52 * W, 0.34 * W, 0.40 * L).pose((0.0, 0.0, 0.26 * L))

    def doigt(sens):
        prof = A.profil([(0.19 * W, 0), (0.17 * W, 0.18 * L), (0.12 * W, 0.40 * L), (0.065 * W, 0.58 * L), (0.02 * W, 0.70 * L), (0, 0.74 * L)], 4)
        d = A.tour(prof, 18).etire(0.82, 1.0, 1.0)
        # le doigt se courbe vers l'autre : le bout rentre
        d = d.sculpte(lambda v: np.stack([v[:, 0] - sens * 0.10 * W * (v[:, 2] / (0.74 * L)) ** 2, v[:, 1], v[:, 2]], axis=1))
        ang = math.radians(ouverture) * 0.5
        dirv = Vector((sens * math.sin(ang), 0.0, math.cos(ang)))
        return couche(d, A.cadre(Vector((sens * 0.20 * W, 0.0, 0.40 * L)), dirv, (0, 1, 0)))
    m = paume + doigt(1.0) + doigt(-1.0)
    if couleur is not None:
        m.teinte = np.tile(np.asarray(couleur, float), (len(m.v), 1))
        if bout is not None:                                    # le bout des doigts d'une autre couleur
            m.teinte[m.v[:, 2] > 0.92 * L] = np.asarray(bout, float)
    return m
