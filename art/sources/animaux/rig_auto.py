"""Le squelette et les cinq animations d'une bête, tirés de sa géométrie (la session Sœur A, 15/10/2026).

Un animal validé a besoin de OS, PORTEURS et ANIMATIONS (GUIDE, « Animer un animal »). Écrire quatre-vingts squelettes à la
main ne tient pas : ici, le squelette se déduit des pièces que `construire()` pose (leurs noms et leurs sommets), par plan :

    "quad"     quadrupède (ou bipède assis) : corps, cou, tête, queue, quatre membres, oreilles dans la tête
    "oiseau"   corps, tête (et cou), deux ailes, queue, deux pattes
    "poisson"  corps souple en trois tronçons (corps, q1, q2), caudale sur q2, deux pectorales, dorsale et anale sur le corps
    "dresse"   un corps d'un seul tenant qui se dresse en cou et tête (vipère) : trois os par la hauteur
    "serpent"  corps souple en une chaîne de six os le long de Y ; ce qui n'est pas le corps suit le tronçon le plus proche
    "mou"      le corps entier sur un os, une tête, des bras-chaînes (pieuvre, étoile) : respire, se balance, rampe
    "fixe"     le corps et la tête seulement (os de secours)

A la fin du fichier de la bête :

    from rig_auto import rig
    if __name__ != "__main__":
        OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")

`rig` appelle `construire()` une fois (au chargement du module, pas quand on lance la fiche). Les os dont le nom finit
par « _g » ou « _d » (minuscules) ne sont PAS recopiés en miroir : chaque côté a son propre os, à sa vraie place.
"""
import math

import numpy as np

from poses import Pose, borne, cloche, onde

TETE = ("tete", "museau", "nez", "oeil", "lourde", "paupiere", "bouche", "gueule", "sourire", "croc", "dent", "langue", "machoire",
        "bec", "oreille", "pavillon", "bois", "perche", "corne", "cloche", "favori", "collerette", "narine", "front", "calotte",
        "masque", "iris", "sourcil", "joue", "barbiche", "moustache", "caroncule", "crete", "cerne", "cil", "soie", "crochet",
        "antenne", "trompe", "fraise", "defense", "creux", "ouie", "feuille", "etoile_nez", "groin", "mufle", "levre", "dedans", "ecaille_t")
QUEUE = ("queue", "cerque", "piques", "bout_queue")
JAMBES = ("patte", "jambe", "avant", "arriere", "pied", "griffe", "sabot", "cuisse", "bras", "main", "epaule", "onglon", "orteil",
          "doigt", "chausson", "genou", "tibia", "eperon", "palette", "mollet")
AILES = ("aile", "remige", "pouce", "membrane")
NAGEOIRES = ("nageoire", "pectorale", "dorsale", "anale", "caudale", "pelvienne", "ventrale", "crete_dos", "voile", "ourlet")
PAUPIERES = [("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


# --------------------------------------------------------------------------------------------- les mesures

class Mesures:
    def __init__(self, module):
        self.a = module.construire() if hasattr(module, "construire") else module()      # le module, ou sa fonction construire
        self.pieces = {}
        for p in self.a._toutes():
            v = np.asarray(p["monde"], float)
            self.pieces.setdefault(p["nom"], []).append(v)
        self.v = {n: np.vstack(vs) for n, vs in self.pieces.items()}
        tous = np.vstack(list(self.v.values()))
        self.bas, self.haut = tous.min(axis=0), tous.max(axis=0)
        self.corps_nom = "corps" if "corps" in self.v else max(self.v, key=lambda n: len(self.v[n]) * float(np.prod(np.ptp(self.v[n], axis=0) + 1e-3)))
        c = self.v[self.corps_nom]
        self.c_bas, self.c_haut = c.min(axis=0), c.max(axis=0)
        self.centre = (self.c_bas + self.c_haut) / 2.0
        self.tete_cible = np.asarray(self.a.tete if self.a.tete is not None else self.centre + np.array([0.0, -0.2, 0.2]), float)

    def cote(self, nom):
        return nom[-2:] if nom.endswith(("_G", "_D")) else ""

    def base(self, nom):
        return nom[:-2] if nom.endswith(("_G", "_D")) else nom


def _debut(nom, mots):
    n = nom.lower()
    return any(n.startswith(m) for m in mots)


def _pivot_haut(V, frac=0.25):
    """Le haut d'un groupe de sommets : (x, y) moyens du quart supérieur, z du sommet."""
    zt, zb = V[:, 2].max(), V[:, 2].min()
    h = V[V[:, 2] >= zt - frac * max(zt - zb, 1e-3)]
    return (float(h[:, 0].mean()), float(h[:, 1].mean()), float(zt - 0.01 * max(zt - zb, 0.0)))


def _t(x):
    return tuple(float(u) for u in x)


class Plan:
    """Rassemble les os, l'attribution de chaque pièce, puis fabrique OS et PORTEURS."""

    def __init__(self, m):
        self.m = m
        self.os = [("racine", None, (0.0, 0.0, 0.0)), ("corps", "racine", _t(m.centre))]
        self.attribution = {}            # nom de pièce -> os, ou (fonction de poids, os de rangement)
        self.souples = {}

    def os_(self, nom, parent, pivot):
        self.os.append((nom, parent, _t(pivot)))

    def donne(self, nom, os_):
        self.attribution[nom] = os_

    def porteurs(self):
        par_base = {}
        for nom in self.m.v:
            par_base.setdefault(self.m.base(nom), {})[self.m.cote(nom)] = self.attribution.get(nom, "corps")
        res = []
        for base in sorted(par_base, key=len, reverse=True):
            cibles = par_base[base]
            vals = list(cibles.values())
            if all(not callable(v) for v in vals) and len(set(vals)) == 1:
                res.append((base, vals[0]))
            elif all(callable(v) for v in vals) and len({id(v) for v in vals}) == 1:
                res.append((base, vals[0], "corps"))
            else:
                def poids(points, cote, cibles=cibles):
                    c = cibles.get(cote, next(iter(cibles.values())))
                    if callable(c):
                        return c(points, cote)
                    return {c: np.ones(len(points))}
                res.append((base, poids, "corps"))
        return res + PAUPIERES


# ------------------------------------------------------------------------------------------------ le quadrupède

def _leg_bones(m, plan, avec_oreilles=True):
    """Les membres : un os par membre (av_g, av_d, ar_g, ar_d), pivot au haut du groupe. Rend le dictionnaire des longueurs."""
    groupes = {}
    for nom, V in m.v.items():
        if nom == m.corps_nom or _debut(nom, TETE) or _debut(nom, QUEUE) or not _debut(nom, JAMBES):
            continue
        n = nom.lower()
        cx, cy = float(V[:, 0].mean()), float(V[:, 1].mean())
        cote = "g" if (m.cote(nom) == "_G" or (m.cote(nom) == "" and "_g" in n) or (m.cote(nom) == "" and "_d" not in n and cx > m.centre[0] + 0.01)) else "d"
        if m.cote(nom) == "_D" or "_d" in n:
            cote = "d"
        elif abs(cx - m.centre[0]) <= 0.01 and m.cote(nom) == "":
            cote = "g"
        if "arriere" in n or "cuisse" in n:
            rang = "ar"
        elif "avant" in n or "bras" in n or "main" in n or "epaule" in n:
            rang = "av"
        else:
            rang = "av" if cy < m.centre[1] else "ar"
        groupes.setdefault(rang + "_" + cote, []).append(nom)
    longueurs = {}
    for os_, noms in groupes.items():
        V = np.vstack([m.v[n] for n in noms])
        plan.os_(os_, "corps", _pivot_haut(V))
        longueurs[os_] = float(V[:, 2].max() - V[:, 2].min())
        for n in noms:
            plan.donne(n, os_)
    return longueurs


def _tete_bones(m, plan):
    """Le cou (os « cou » s'il y a une pièce « cou ») et la tête (pivot à la nuque) ; tout ce qui est « tête » la suit."""
    noms = [n for n in m.v if n != m.corps_nom and _debut(n, TETE)]
    cou = [n for n in m.v if _debut(n, ("cou",))]
    parent = "corps"
    if cou:
        V = m.v[cou[0]]
        d = np.linalg.norm(V - m.tete_cible, axis=1)
        piv = V[np.argsort(-d)[: max(8, len(V) // 12)]].mean(axis=0)
        plan.os_("cou", "corps", piv)
        for n in cou:
            plan.donne(n, "cou")
        parent = "cou"
    tv = m.v["tete"] if "tete" in m.v else (np.vstack([m.v[n] for n in noms]) if noms else None)
    if tv is not None:
        # les pièces dont le nom ne dit rien (crâne, truffe, front…) mais qui sont logées contre la tête la suivent aussi
        ctr = tv.mean(axis=0)
        rad = 0.60 * float(np.ptp(tv, axis=0).max())
        for n, V in m.v.items():
            if n in noms or n == m.corps_nom or n in cou or _debut(n, QUEUE) or _debut(n, JAMBES) or _debut(n, ("aile", "elytre", "nageoire")):
                continue
            d = np.linalg.norm(V - ctr, axis=1)
            if float(np.median(d)) < 1.15 * rad and float(d.max()) < 2.2 * rad:
                noms.append(n)
        dev = -1.0 if m.tete_cible[1] < m.centre[1] else 1.0                       # la tête est devant (−Y) ou derrière
        y_nuque = float(tv[:, 1].max() if dev < 0 else tv[:, 1].min())
        piv = (float(tv[:, 0].mean()), y_nuque - dev * 0.12 * float(np.ptp(tv[:, 1])), float(tv[:, 2].mean() - 0.10 * np.ptp(tv[:, 2])))
        plan.os_("tete", parent, piv)
        for n in noms:
            plan.donne(n, "tete")
    return bool(tv is not None), bool(cou)


def rig_quad(m, plan=None, souple=False):
    plan = plan or Plan(m)
    avec_tete, avec_cou = _tete_bones(m, plan)
    longueurs = _leg_bones(m, plan)
    chaine = []
    if souple:                                                            # le corps d'un seul tenant ondule : trois tronçons le long de Y
        noms_ch, ys_ch, _y0, _y1 = _chaine(m, plan, 4)
        chaine = noms_ch
        plan.donne(m.corps_nom, _poids_chaine(noms_ch, ys_ch))
    queue = [n for n in m.v if n != m.corps_nom and _debut(n, QUEUE)]
    if queue:
        V = np.vstack([m.v[n] for n in queue])
        racine = V[np.argmin(np.linalg.norm(V - m.centre, axis=1))]
        plan.os_("queue", "corps", racine)
        for n in queue:
            plan.donne(n, "queue")
    Lleg = float(np.mean(list(longueurs.values()))) if longueurs else 0.10
    sol = float(m.bas[2])
    chute = max(0.0, float(m.c_bas[2]) - sol - 0.01)
    avs = [o for o in plan.os if o[0].startswith(("av_", "ar_"))]
    noms = {o[0] for o in plan.os}

    def a(p, os_, rot=(0, 0, 0), pos=(0, 0, 0), ech=(1, 1, 1)):
        if os_ in noms:
            p.add(os_, rot=rot, pos=pos, ech=ech)

    def jambes(p, avant, arriere, diagonale=1.0):
        a(p, "av_g", (avant, 0, 0)); a(p, "av_d", (avant * diagonale, 0, 0))
        a(p, "ar_g", (arriere, 0, 0)); a(p, "ar_d", (arriere * diagonale, 0, 0))

    amp = 20.0 if Lleg > 0.25 else 12.0                               # les pattes courtes (assis, couché) bougent peu : sinon elles se détachent
    plie = 62.0 if Lleg > 0.20 else 22.0

    def ondule(p, t, ampli, tours=1.0):
        for k, nm in enumerate(chaine):
            if k:
                a(p, nm, rot=(0, 0, ampli * (0.5 + 0.2 * k) * math.sin(math.tau * (t * tours - 0.15 * k))))

    def repos(t):
        p = Pose(); r = onde(t, 2)
        a(p, "corps", ech=(1 + 0.012 * r, 1, 1 + 0.02 * r))
        g, d = cloche(t, 0.25, 0.13), cloche(t, 0.62, 0.12)
        a(p, "cou", rot=(2 * r, 0, 10 * g - 10 * d))
        a(p, "tete", rot=(-3 * g + 2 * r, 0, 16 * g - 18 * d))
        a(p, "queue", rot=(0, 0, 8 * onde(t, 2)))
        ondule(p, t, 5.0)
        p.ouvert = 1 - cloche(t, 0.45, 0.02) - cloche(t, 0.85, 0.02)
        return p

    def avance(t):
        p = Pose(); s = math.sin(math.tau * t); c = math.cos(math.tau * t)
        ondule(p, t, 14.0)
        a(p, "corps", pos=(0, 0, 0.012 * Lleg * abs(c)), rot=(0, 3 * s, 0))
        a(p, "av_g", (amp * s, 0, 0)); a(p, "ar_d", (amp * s, 0, 0))
        a(p, "av_d", (-amp * s, 0, 0)); a(p, "ar_g", (-amp * s, 0, 0))
        a(p, "cou", rot=(3 * c, 0, 0))
        a(p, "tete", rot=(-3 * c, 0, 4 * s))
        a(p, "queue", rot=(0, 0, 9 * s))
        return p

    def mange(t):
        p = Pose()
        haut_ = cloche(t, 0.88, 0.12)
        bas = 1 - haut_
        coups = max(0.0, onde(t, 3)) ** 2 * bas
        a(p, "corps", rot=(5 * bas, 0, 0))
        a(p, "cou", rot=(30 * bas, 0, 0))
        a(p, "tete", rot=(26 * bas + 10 * coups, 0, 8 * haut_ * onde(t, 2)))
        a(p, "queue", rot=(0, 0, 10 * onde(t, 3)))
        ondule(p, t, 4.0)
        p.ouvert = 1 - cloche(t, 0.72, 0.02)
        return p

    def joie(t):
        p = Pose()
        tasse = cloche(t, 0.12, 0.10, False)
        vol = math.sin(math.pi * borne((t - 0.18) / 0.50))
        recoit = cloche(t, 0.72, 0.10, False)
        a(p, "corps", pos=(0, 0, -0.35 * Lleg * tasse + 0.55 * Lleg * vol - 0.2 * Lleg * recoit), rot=(-8 * vol, 0, 16 * vol * onde(t, 1)))
        jambes(p, -20 * vol + 10 * tasse, 24 * vol - 10 * tasse)
        a(p, "cou", rot=(-10 * vol, 0, 0))
        a(p, "tete", rot=(-8 * vol, 0, 14 * vol * onde(t, 2)))
        a(p, "queue", rot=(0, 0, 36 * vol * onde(t, 4)))
        ondule(p, t, 20.0 * vol, 2.0)
        return p

    def dort(t):
        p = Pose(); r = onde(t, 1)
        p.ouvert = 0.0
        a(p, "corps", pos=(0, 0, -chute), rot=(0, 3, 0), ech=(1 + 0.012 * r, 1, 1 + 0.02 * r))
        a(p, "av_g", (plie, 0, 0)); a(p, "av_d", (plie - 4, 0, 0))
        a(p, "ar_g", (-plie, 0, 0)); a(p, "ar_d", (-plie + 4, 0, 0))
        a(p, "cou", rot=(22, 0, 30))
        a(p, "tete", rot=(18, 6, 24))
        a(p, "queue", rot=(0, 0, 8))
        ondule(p, t, 3.0)
        for nm in chaine[1:]:
            a(p, nm, rot=(0, 0, 8))
        return p

    anim = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
            "joie": (48, joie, False), "dort": (120, dort, True)}
    return plan, anim


# ------------------------------------------------------------------------------------------------- l'oiseau

def rig_oiseau(m):
    plan = Plan(m)
    _tete_bones(m, plan)
    noms_os = set()
    cor = m.centre
    ailes = {"g": [], "d": []}
    pattes = {"g": [], "d": []}
    queue = []
    for nom, V in m.v.items():
        if nom == m.corps_nom or _debut(nom, TETE):
            continue
        cx = float(V[:, 0].mean())
        cote = "g" if (m.cote(nom) == "_G" or (m.cote(nom) == "" and cx >= cor[0])) else "d"
        if m.cote(nom) == "_D":
            cote = "d"
        if _debut(nom, QUEUE):
            queue.append(nom)
        elif _debut(nom, AILES):
            ailes[cote].append(nom)
        elif _debut(nom, JAMBES) or float(V[:, 2].mean()) < float(m.c_bas[2]) + 0.25 * float(np.ptp(m.corps_v[:, 2]) if hasattr(m, "corps_v") else (m.c_haut[2] - m.c_bas[2])):
            pattes[cote].append(nom)
    for cote, noms in ailes.items():
        if noms:
            V = np.vstack([m.v[n] for n in noms])
            interne = V[np.argsort(np.abs(V[:, 0] - cor[0]))[: max(8, len(V) // 10)]]
            plan.os_("aile_" + cote, "corps", (float(interne[:, 0].mean()), float(V[:, 1].mean()), float(V[:, 2].max() - 0.12 * np.ptp(V[:, 2]))))
            for n in noms:
                plan.donne(n, "aile_" + cote)
    for cote, noms in pattes.items():
        if noms:
            V = np.vstack([m.v[n] for n in noms])
            plan.os_("patte_" + cote, "racine", _pivot_haut(V))
            for n in noms:
                plan.donne(n, "patte_" + cote)
    if queue:
        V = np.vstack([m.v[n] for n in queue])
        plan.os_("queue", "corps", V[np.argmin(np.linalg.norm(V - m.centre, axis=1))])
        for n in queue:
            plan.donne(n, "queue")
    noms = {o[0] for o in plan.os}
    haut_corps = float(m.c_haut[2] - m.c_bas[2])

    def a(p, os_, rot=(0, 0, 0), pos=(0, 0, 0), ech=(1, 1, 1)):
        if os_ in noms:
            p.add(os_, rot=rot, pos=pos, ech=ech)

    def ailes_(p, leve):
        a(p, "aile_g", (0.55 * leve, -0.4 * leve, -0.6 * leve))
        a(p, "aile_d", (0.55 * leve, 0.4 * leve, 0.6 * leve))

    def repos(t):
        p = Pose(); r = onde(t, 2)
        a(p, "corps", ech=(1 + 0.014 * r, 1, 1 + 0.02 * r))
        g, d = cloche(t, 0.22, 0.10), cloche(t, 0.6, 0.10)
        a(p, "cou", rot=(2 * r, 0, 12 * g - 12 * d))
        a(p, "tete", rot=(0, 0, 22 * g - 24 * d))
        ailes_(p, 5 * cloche(t, 0.80, 0.06))
        a(p, "queue", rot=(8 * cloche(t, 0.4, 0.06), 0, 0))
        p.ouvert = 1 - cloche(t, 0.45, 0.02) - cloche(t, 0.88, 0.02)
        return p

    def avance(t):
        p = Pose(); s = math.sin(math.tau * t); c = math.cos(math.tau * t)
        a(p, "corps", pos=(0, 0, 0.01 * abs(c)), rot=(0, 5 * s, 0))
        a(p, "patte_g", (30 * s, 0, 0)); a(p, "patte_d", (-30 * s, 0, 0))
        a(p, "tete", rot=(-8 * abs(c), 0, 0))
        a(p, "queue", rot=(6 * c, 0, 0))
        return p

    def mange(t):
        p = Pose(); haut_ = cloche(t, 0.88, 0.12); bas = 1 - haut_
        coups = max(0.0, onde(t, 3)) ** 2 * bas
        a(p, "corps", rot=(10 * bas, 0, 0))
        a(p, "cou", rot=(20 * bas, 0, 0))
        a(p, "tete", rot=(30 * bas + 14 * coups, 0, 0))
        a(p, "queue", rot=(-10 * bas, 0, 0))
        p.ouvert = 1 - cloche(t, 0.7, 0.02)
        return p

    def joie(t):
        p = Pose()
        tasse = cloche(t, 0.12, 0.10, False)
        vol = math.sin(math.pi * borne((t - 0.18) / 0.52))
        a(p, "corps", pos=(0, 0, 0.9 * haut_corps * vol - 0.2 * haut_corps * tasse), rot=(-14 * vol, 0, 0))
        ailes_(p, 70 * vol * (0.6 + 0.4 * onde(t, 5)) if vol > 0 else 0)
        a(p, "patte_g", (-24 * vol, 0, 0)); a(p, "patte_d", (-24 * vol, 0, 0))
        a(p, "tete", rot=(-10 * vol, 0, 0))
        a(p, "queue", rot=(18 * vol, 0, 0))
        return p

    def dort(t):
        p = Pose(); r = onde(t, 1)
        p.ouvert = 0.0
        a(p, "corps", pos=(0, 0, -0.18 * haut_corps), rot=(0, 0, 0), ech=(1 + 0.02 * r, 1, 1 + 0.03 * r))
        a(p, "patte_g", (50, 0, 0)); a(p, "patte_d", (50, 0, 0))
        a(p, "cou", rot=(14, 0, 40))
        a(p, "tete", rot=(20, 0, 70))
        ailes_(p, -4)
        return p

    anim = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
            "joie": (48, joie, False), "dort": (120, dort, True)}
    return plan, anim


# ------------------------------------------------------------------------------- le corps souple (poisson, serpent)

def _smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def _chaine(m, plan, n, axe=1):
    """n os le long de l'axe principal (Y) : pivot = le centre des sommets du corps dans la tranche. Rend (noms, ys)."""
    V = m.v[m.corps_nom]
    y0, y1 = float(V[:, axe].min()), float(V[:, axe].max())
    bornes = np.linspace(y0, y1, n + 1)
    noms, ys = [], []
    for k in range(n):
        tr = V[(V[:, axe] >= bornes[k]) & (V[:, axe] <= bornes[k + 1])]
        c = tr.mean(axis=0) if len(tr) else m.centre
        c = np.array(c, float)
        c[axe] = (bornes[k] + bornes[k + 1]) / 2.0
        noms.append("corps" if k == 0 else "s%d" % k)
        ys.append(float(c[axe]))
        if k:
            plan.os_("s%d" % k, "corps" if k == 1 else "s%d" % (k - 1), c)
        else:
            plan.os[1] = ("corps", "racine", _t(c))
    return noms, ys, y0, y1


def _poids_chaine(noms, ys):
    ys = np.asarray(ys)

    def poids(points, cote):
        y = points[:, 1]
        w = {nm: np.zeros(len(y)) for nm in noms}
        for i in range(len(y)):
            yy = y[i]
            if yy <= ys[0]:
                w[noms[0]][i] = 1.0
            elif yy >= ys[-1]:
                w[noms[-1]][i] = 1.0
            else:
                k = int(np.searchsorted(ys, yy) - 1)
                u = (yy - ys[k]) / (ys[k + 1] - ys[k])
                u = u * u * (3 - 2 * u)
                w[noms[k]][i] = 1 - u
                w[noms[k + 1]][i] = u
        return w
    return poids


def rig_serpent(m, n=6, avec_membres=False):
    plan = Plan(m)
    noms, ys, y0, y1 = _chaine(m, plan, n)
    poids = _poids_chaine(noms, ys)
    corps_w = poids
    plan.donne(m.corps_nom, corps_w)
    for nom in m.v:
        if nom == m.corps_nom:
            continue
        plan.donne(nom, corps_w)                 # tout le reste suit le tronçon voisin (souple, par ses sommets)
    inv = _debut  # noqa: F841

    def a(p, os_, rot=(0, 0, 0), pos=(0, 0, 0)):
        if os_ in noms:
            p.add(os_, rot=rot, pos=pos)

    def vague(p, t, amp, tours=1.0, dephas=0.14):
        for k, nm in enumerate(noms):
            a(p, nm, rot=(0, 0, amp * (0.4 + 0.12 * k) * math.sin(math.tau * (t * tours - k * dephas))))

    def repos(t):
        p = Pose()
        vague(p, t, 5.0, 1.0, 0.10)
        a(p, "corps", pos=(0, 0, 0.004 * math.sin(math.tau * t * 2)))
        p.ouvert = 1 - cloche(t, 0.5, 0.02)
        return p

    def avance(t):
        p = Pose()
        vague(p, t, 22.0, 1.0, 0.16)
        p.ouvert = 1.0
        return p

    def mange(t):
        p = Pose(); bas = cloche(t, 0.5, 0.35)
        vague(p, t, 4.0, 1.0, 0.1)
        a(p, "corps", rot=(18 * bas, 0, 0))
        p.ouvert = 1 - cloche(t, 0.75, 0.02)
        return p

    def joie(t):
        p = Pose(); s = math.sin(math.pi * borne(t))
        vague(p, t, 30.0 * s, 2.0, 0.12)
        a(p, "corps", rot=(-16 * s, 0, 0), pos=(0, 0, 0.04 * s))
        return p

    def dort(t):
        p = Pose(); p.ouvert = 0.0
        vague(p, t, 3.0, 1.0, 0.06)
        for k, nm in enumerate(noms):
            a(p, nm, rot=(0, 0, 8.0))
        return p

    anim = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
            "joie": (48, joie, False), "dort": (120, dort, True)}
    return plan, anim


def rig_poisson(m):
    """Corps en trois tronçons (corps, s1, s2) ; la caudale sur s2 ; les pectorales sur leur os ; ce qui est à l'intérieur suit."""
    plan = Plan(m)
    noms, ys, y0, y1 = _chaine(m, plan, 3)
    poids = _poids_chaine(noms, ys)
    pect = {"g": [], "d": []}
    for nom, V in m.v.items():
        if nom == m.corps_nom:
            plan.donne(nom, poids)
            continue
        n = nom.lower()
        if n.startswith("pectorale") or n.startswith("nageoire_p"):
            cx = float(V[:, 0].mean())
            cote = "g" if (m.cote(nom) == "_G" or (m.cote(nom) == "" and cx >= m.centre[0])) else "d"
            if m.cote(nom) == "_D":
                cote = "d"
            pect[cote].append(nom)
        elif _debut(nom, ("caudale", "queue")):
            plan.donne(nom, "s2")
        elif _debut(nom, TETE):
            plan.donne(nom, poids)
        else:
            plan.donne(nom, poids)
    for cote, nn in pect.items():
        if nn:
            V = np.vstack([m.v[n] for n in nn])
            plan.os_("pect_" + cote, "corps", V[np.argmin(np.abs(V[:, 0] - m.centre[0]))])
            for n in nn:
                plan.donne(n, "pect_" + cote)
    bones = {o[0] for o in plan.os}

    def a(p, os_, rot=(0, 0, 0), pos=(0, 0, 0)):
        if os_ in bones:
            p.add(os_, rot=rot, pos=pos)

    def nage(p, t, amp, tours=1.0):
        a(p, "corps", rot=(0, 0, -0.30 * amp * math.sin(math.tau * (t * tours - 0.10))))
        a(p, "s1", rot=(0, 0, 0.70 * amp * math.sin(math.tau * (t * tours - 0.25))))
        a(p, "s2", rot=(0, 0, 1.10 * amp * math.sin(math.tau * (t * tours - 0.42))))

    def repos(t):
        p = Pose(); nage(p, t, 5.0, 1.0)
        a(p, "pect_g", (0, 0, 8 * onde(t, 2))); a(p, "pect_d", (0, 0, -8 * onde(t, 2)))
        p.ouvert = 1 - cloche(t, 0.5, 0.02)
        return p

    def avance(t):
        p = Pose(); nage(p, t, 20.0, 1.0)
        a(p, "pect_g", (0, 0, 14 * onde(t, 2))); a(p, "pect_d", (0, 0, -14 * onde(t, 2)))
        return p

    def mange(t):
        p = Pose(); bas = cloche(t, 0.5, 0.30)
        nage(p, t, 5.0, 1.0)
        a(p, "corps", rot=(14 * bas, 0, 0))
        p.ouvert = 1 - cloche(t, 0.8, 0.02)
        return p

    def joie(t):
        p = Pose(); s = math.sin(math.pi * borne(t))
        nage(p, t, 26.0 * s, 2.0)
        a(p, "corps", rot=(-20 * s, 0, 0), pos=(0, 0, 0.05 * s))
        return p

    def dort(t):
        p = Pose(); p.ouvert = 0.0
        nage(p, t, 2.5, 1.0)
        a(p, "corps", rot=(0, 6, 0))
        return p

    anim = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
            "joie": (48, joie, False), "dort": (120, dort, True)}
    return plan, anim


def rig_dresse(m):
    """Un corps d'un seul tenant dont une partie se dresse (vipère, cobra) : corps (le tas), cou et tête, par la hauteur."""
    plan = Plan(m)
    V = m.v[m.corps_nom]
    zmax = float(V[:, 2].max()); zmin = float(V[:, 2].min())
    z0 = zmin + 0.40 * (zmax - zmin); z1 = zmin + 0.78 * (zmax - zmin)
    haut_ = V[V[:, 2] > z0]
    plan.os_("cou", "corps", (float(haut_[:, 0].mean()), float(haut_[:, 1].mean()), z0))
    tete_ = V[V[:, 2] > z1]
    plan.os_("tete", "cou", (float(tete_[:, 0].mean()), float(tete_[:, 1].mean() + 0.02), z1))
    larg = 0.5 * (z1 - z0) + 1e-4

    def poids(points, cote):
        z = points[:, 2]
        s0 = _smooth((z - z0) / larg)
        s1 = _smooth((z - z1) / larg)
        return {"corps": 1 - s0, "cou": s0 - s1, "tete": s1}
    plan.donne(m.corps_nom, poids)
    for nom in m.v:
        if nom != m.corps_nom:
            plan.donne(nom, "tete" if _debut(nom, TETE) else poids)
    bones = {o[0] for o in plan.os}

    def a(p, os_, rot=(0, 0, 0), pos=(0, 0, 0)):
        if os_ in bones:
            p.add(os_, rot=rot, pos=pos)

    def repos(t):
        p = Pose(); r = onde(t, 2)
        a(p, "corps", rot=(0, 0, 0), pos=(0, 0, 0.002 * r))
        a(p, "cou", rot=(0, 0, 12 * onde(t, 1)))
        a(p, "tete", rot=(-4 * r, 0, 16 * onde(t, 1, 0.15)))
        p.ouvert = 1 - cloche(t, 0.5, 0.02)
        return p

    def avance(t):
        p = Pose()
        a(p, "corps", rot=(0, 0, 10 * onde(t, 1)))
        a(p, "cou", rot=(0, 0, 26 * onde(t, 1, 0.25)))
        a(p, "tete", rot=(0, 0, 20 * onde(t, 1, 0.5)))
        return p

    def mange(t):
        p = Pose(); bas = cloche(t, 0.5, 0.30)
        a(p, "cou", rot=(30 * bas, 0, 0))
        a(p, "tete", rot=(26 * bas, 0, 0))
        p.ouvert = 1 - cloche(t, 0.8, 0.02)
        return p

    def joie(t):
        p = Pose(); s = math.sin(math.pi * borne(t))
        a(p, "cou", rot=(-18 * s, 0, 30 * s * onde(t, 2)))
        a(p, "tete", rot=(-12 * s, 0, -20 * s * onde(t, 2)))
        return p

    def dort(t):
        p = Pose(); p.ouvert = 0.0; r = onde(t, 1)
        a(p, "cou", rot=(52, 0, 20), pos=(0, 0, 0))
        a(p, "tete", rot=(30, 0, 10 + 2 * r))
        return p

    anim = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
            "joie": (48, joie, False), "dort": (120, dort, True)}
    return plan, anim


def rig_fixe(m):
    plan = Plan(m)
    _tete_bones(m, plan)
    bones = {o[0] for o in plan.os}

    def a(p, os_, rot=(0, 0, 0), pos=(0, 0, 0), ech=(1, 1, 1)):
        if os_ in bones:
            p.add(os_, rot=rot, pos=pos, ech=ech)

    def repos(t):
        p = Pose(); r = onde(t, 2)
        a(p, "corps", ech=(1 + 0.015 * r, 1, 1 + 0.025 * r))
        a(p, "tete", rot=(0, 0, 12 * cloche(t, 0.3, 0.15) - 12 * cloche(t, 0.7, 0.15)))
        p.ouvert = 1 - cloche(t, 0.5, 0.02)
        return p

    def avance(t):
        p = Pose(); s = math.sin(math.tau * t)
        a(p, "corps", pos=(0, 0, 0.02 * abs(s)), rot=(0, 6 * s, 0))
        a(p, "tete", rot=(0, 0, 5 * s))
        return p

    def mange(t):
        p = Pose(); bas = cloche(t, 0.5, 0.35)
        a(p, "corps", rot=(10 * bas, 0, 0))
        a(p, "tete", rot=(24 * bas + 8 * max(0.0, onde(t, 3)) ** 2 * bas, 0, 0))
        p.ouvert = 1 - cloche(t, 0.8, 0.02)
        return p

    def joie(t):
        p = Pose(); s = math.sin(math.pi * borne(t))
        a(p, "corps", pos=(0, 0, 0.12 * s), rot=(-10 * s, 20 * s * onde(t, 1), 0))
        return p

    def dort(t):
        p = Pose(); p.ouvert = 0.0; r = onde(t, 1)
        a(p, "corps", pos=(0, 0, -0.02), ech=(1 + 0.02 * r, 1, 1 + 0.03 * r))
        a(p, "tete", rot=(16, 0, 20))
        return p

    anim = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
            "joie": (48, joie, False), "dort": (120, dort, True)}
    return plan, anim


# ---------------------------------------------------------------------------------------------------- l'entrée

def rig(module, plan="quad", **opt):
    """Rend (OS, PORTEURS, ANIMATIONS) pour la bête `module` (voir le haut de ce fichier)."""
    m = Mesures(module)
    if plan in ("membres", "bras", "etoile", "meduse", "mou"):
        import rig_plus
        fabrique = {"membres": rig_plus.rig_membres, "bras": rig_plus.rig_bras, "etoile": rig_plus.rig_etoile,
                    "meduse": rig_plus.rig_meduse, "mou": rig_plus.rig_limace}[plan]
        pl, anim = fabrique(m, **opt)
    else:
        fabrique = {"quad": lambda: rig_quad(m, souple=opt.get("souple", False)), "dresse": lambda: rig_dresse(m),
                    "oiseau": lambda: rig_oiseau(m), "poisson": lambda: rig_poisson(m),
                    "serpent": lambda: rig_serpent(m, **opt), "fixe": lambda: rig_fixe(m)}[plan]
        pl, anim = fabrique()
    return pl.os, pl.porteurs(), anim
