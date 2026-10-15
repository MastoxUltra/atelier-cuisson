"""Les plans de squelette qui s'ajoutent à rig_auto.py (la session Sœur A, 15/10/2026) :

    "membres"  arthropodes et insectes : un os par patte (les pièces qui se touchent forment un membre), antennes, ailes, pinces,
               queue ; souple=True : le corps d'un seul tenant ondule aussi (tardigrade)
    "bras"     la pieuvre : un os par bras (les pièces « bras_# »), les ventouses suivent le bras le plus proche
    "etoile"   une pièce d'un seul tenant en étoile : un os par bras, poids par secteur angulaire
    "meduse"   la cloche qui pulse, rubans et filaments un par un
    "mou"      une limace de mer : chaîne de tronçons le long de Y, reptation par une onde verticale
"""
import math

import numpy as np

from poses import Pose, borne, cloche, onde
from rig_auto import (Plan, TETE, _chaine, _debut, _poids_chaine, _smooth, _tete_bones)


def _composantes(noms, V, seuil=0.02):
    """Regroupe des pièces qui se touchent (distance mini entre sommets < seuil) : un membre et ses griffes ne font qu'un."""
    echant = {n: V[n][:: max(1, len(V[n]) // 160)] for n in noms}
    parent = {n: n for n in noms}

    def racine(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i, n1 in enumerate(noms):
        for n2 in noms[i + 1:]:
            d = np.linalg.norm(echant[n1][:, None, :] - echant[n2][None, :, :], axis=2).min()
            if d < seuil:
                parent[racine(n1)] = racine(n2)
    groupes = {}
    for n in noms:
        groupes.setdefault(racine(n), []).append(n)
    return list(groupes.values())


def _racine_membre(V, centre):
    """Le point d'un groupe de sommets le plus proche du centre du corps : là où le membre s'attache."""
    return V[np.argmin(np.linalg.norm(V - centre, axis=1))]


def _animations(repos, avance, mange, joie, dort):
    return {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
            "joie": (48, joie, False), "dort": (120, dort, True)}


def rig_membres(m, souple=False, bat_des_ailes=None):
    plan = Plan(m)
    _tete_bones(m, plan)
    chaine = []
    if souple:
        noms_ch, ys_ch, _a, _b = _chaine(m, plan, 4)
        chaine = noms_ch
        plan.donne(m.corps_nom, _poids_chaine(noms_ch, ys_ch))
    tete_noms = {n for n in m.v if n != m.corps_nom and _debut(n, TETE) and not _debut(n, ("antenne", "barbule", "tige"))}
    reste = [n for n in m.v if n != m.corps_nom and n not in tete_noms]

    def cote_de(nom, V):
        c = m.cote(nom)
        if c == "_G":
            return "g"
        if c == "_D":
            return "d"
        n = nom.lower()
        if "_g" in n[-4:]:
            return "g"
        if "_d" in n[-4:]:
            return "d"
        return "g" if float(V[:, 0].mean()) >= m.centre[0] else "d"
    ant = {"g": [], "d": []}
    ailes = {"g": [], "d": []}
    pinces = {"g": [], "d": []}
    queue = []
    pattes = []
    for n in reste:
        V = m.v[n]
        if _debut(n, ("antenne", "barbule")):
            ant[cote_de(n, V)].append(n)
        elif _debut(n, ("aile", "elytre", "nervure")):
            ailes[cote_de(n, V)].append(n)
        elif _debut(n, ("bras", "pince", "palme", "main", "poing", "paume", "doigt_fixe", "doigt_mobile", "pique", "genale")):
            pinces[cote_de(n, V)].append(n)
        elif _debut(n, ("queue", "ampoule", "dard", "telson", "cerque", "piques")):
            queue.append(n)
        elif _debut(n, ("patte", "jambe", "cuisse", "tibia", "eperon", "griffe", "pied", "doigt")):
            pattes.append(n)
    a_tete = "tete" if "tete" in {o[0] for o in plan.os} else "corps"
    for cote, noms in ant.items():
        if noms:
            Vg = np.vstack([m.v[n] for n in noms])
            plan.os_("ant_" + cote, a_tete, _racine_membre(Vg, m.tete_cible))
            for n in noms:
                plan.donne(n, "ant_" + cote)
    for cote, noms in ailes.items():
        if noms:
            Vg = np.vstack([m.v[n] for n in noms])
            interne = Vg[np.argsort(np.abs(Vg[:, 0] - m.centre[0]))[: max(8, len(Vg) // 10)]]
            plan.os_("aile_" + cote, "corps", interne.mean(axis=0))
            for n in noms:
                plan.donne(n, "aile_" + cote)
    for cote, noms in pinces.items():
        if noms:
            Vg = np.vstack([m.v[n] for n in noms])
            plan.os_("pince_" + cote, "corps", _racine_membre(Vg, m.centre))
            for n in noms:
                plan.donne(n, "pince_" + cote)
    if queue:
        Vg = np.vstack([m.v[n] for n in queue])
        plan.os_("queue", "corps", _racine_membre(Vg, m.centre))
        for n in queue:
            plan.donne(n, "queue")
    jambes = []
    if pattes:
        infos = []
        for noms in _composantes(pattes, m.v):
            Vg = np.vstack([m.v[n] for n in noms])
            c = "g" if float(Vg[:, 0].mean()) >= m.centre[0] else "d"
            infos.append((c, float(Vg[:, 1].mean()), noms, Vg))
        for c in ("g", "d"):
            for rang, (_c, _y, noms, Vg) in enumerate(sorted([x for x in infos if x[0] == c], key=lambda x: x[1])):
                os_ = "l%d_%s" % (rang, c)
                plan.os_(os_, "corps", _racine_membre(Vg, m.centre))
                jambes.append((os_, c, rang))
                for n in noms:
                    plan.donne(n, os_)
    bones = {o[0] for o in plan.os}
    haut_corps = float(m.c_haut[2] - m.c_bas[2])
    vole = bool(ailes["g"] or ailes["d"]) if bat_des_ailes is None else bat_des_ailes

    def a(p, os_, rot=(0, 0, 0), pos=(0, 0, 0), ech=(1, 1, 1)):
        if os_ in bones:
            p.add(os_, rot=rot, pos=pos, ech=ech)

    def ondule(p, t, ampli, tours=1.0):
        for k, nm in enumerate(chaine):
            if k:
                a(p, nm, rot=(0, 0, ampli * (0.5 + 0.2 * k) * math.sin(math.tau * (t * tours - 0.15 * k))))

    def marche(p, t, ampli):
        for os_, c, rang in jambes:
            ph = 0.5 * ((rang + (0 if c == "g" else 1)) % 2)
            sg = 1.0 if c == "g" else -1.0
            a(p, os_, rot=(0, 0, sg * ampli * math.sin(math.tau * (t - ph))))

    def pattes_pose(p, ampli):
        for os_, c, rang in jambes:
            sg = 1.0 if c == "g" else -1.0
            a(p, os_, rot=(0, 0, sg * ampli * (1 - 2.0 * (rang % 2))))

    def ailes_(p, leve):
        a(p, "aile_g", (0.55 * leve, -0.4 * leve, -0.6 * leve))
        a(p, "aile_d", (0.55 * leve, 0.4 * leve, 0.6 * leve))

    def repos(t):
        p = Pose(); r = onde(t, 2)
        a(p, "corps", ech=(1 + 0.012 * r, 1, 1 + 0.02 * r))
        a(p, "ant_g", rot=(0, 0, 12 * onde(t, 2))); a(p, "ant_d", rot=(0, 0, -12 * onde(t, 2, 0.25)))
        a(p, "tete", rot=(0, 0, 10 * cloche(t, 0.3, 0.12) - 10 * cloche(t, 0.7, 0.12)))
        a(p, "pince_g", rot=(-8 * cloche(t, 0.55, 0.12), 0, 0)); a(p, "pince_d", rot=(-8 * cloche(t, 0.55, 0.12), 0, 0))
        a(p, "queue", rot=(-5 * r, 0, 5 * onde(t, 1)))
        ailes_(p, 4 * cloche(t, 0.8, 0.06))
        ondule(p, t, 4.0)
        p.ouvert = 1 - cloche(t, 0.45, 0.02)
        return p

    def avance(t):
        p = Pose(); s = math.sin(math.tau * t)
        if vole:
            a(p, "corps", pos=(0, 0, 0.25 * haut_corps + 0.06 * haut_corps * s), rot=(-6, 0, 0))
            ailes_(p, 50 * math.sin(math.tau * t * 6))
            for os_, c, rang in jambes:
                a(p, os_, rot=(10, 0, 0))
        else:
            a(p, "corps", pos=(0, 0, 0.02 * haut_corps * abs(s)), rot=(0, 2.5 * s, 0))
            marche(p, t, 22.0)
            a(p, "pince_g", rot=(0, 0, 10 * s)); a(p, "pince_d", rot=(0, 0, -10 * s))
        a(p, "ant_g", rot=(0, 0, 14 * onde(t, 3))); a(p, "ant_d", rot=(0, 0, -14 * onde(t, 3)))
        a(p, "queue", rot=(0, 0, 10 * s))
        ondule(p, t, 10.0)
        return p

    def mange(t):
        p = Pose(); haut_ = cloche(t, 0.88, 0.12); bas = 1 - haut_
        a(p, "corps", rot=(8 * bas, 0, 0))
        a(p, "tete", rot=(22 * bas + 8 * max(0.0, onde(t, 3)) ** 2 * bas, 0, 0))
        for nm in ("pince_g", "pince_d"):
            a(p, nm, rot=(-30 * bas * (0.5 + 0.5 * onde(t, 3)), 0, 0))
        a(p, "ant_g", rot=(0, 0, 10 * onde(t, 4))); a(p, "ant_d", rot=(0, 0, -10 * onde(t, 4)))
        ondule(p, t, 3.0)
        p.ouvert = 1 - cloche(t, 0.7, 0.02)
        return p

    def joie(t):
        p = Pose(); s = math.sin(math.pi * borne(t))
        a(p, "corps", pos=(0, 0, 0.55 * haut_corps * s), rot=(-8 * s, 14 * s * onde(t, 1), 0))
        for nm in ("pince_g", "pince_d"):
            a(p, nm, rot=(-55 * s, 0, 18 * s * onde(t, 3)))
        ailes_(p, 60 * s * (0.5 + 0.5 * onde(t, 4)))
        a(p, "queue", rot=(-25 * s, 0, 0))
        pattes_pose(p, 10 * s)
        ondule(p, t, 8.0 * s, 2.0)
        return p

    def dort(t):
        p = Pose(); p.ouvert = 0.0; r = onde(t, 1)
        a(p, "corps", pos=(0, 0, -0.12 * haut_corps), ech=(1 + 0.02 * r, 1, 1 + 0.03 * r))
        pattes_pose(p, 14.0)
        a(p, "tete", rot=(16, 0, 14)); a(p, "queue", rot=(10, 0, 0))
        a(p, "ant_g", rot=(0, 0, 22)); a(p, "ant_d", rot=(0, 0, -22))
        for nm in ("pince_g", "pince_d"):
            a(p, nm, rot=(12, 0, 0))
        ailes_(p, -3)
        ondule(p, t, 2.0)
        return p
    return plan, _animations(repos, avance, mange, joie, dort)


def rig_bras(m, noms_bras=("bras_",)):
    """La pieuvre : chaque bras est une pièce, un os par bras (pivot à sa racine) ; les ventouses suivent le bras le plus proche."""
    plan = Plan(m)
    _tete_bones(m, plan)
    bras = [n for n in sorted(m.v) if _debut(n, noms_bras) and "oeil" not in n]
    dirs, racines, sects = {}, {}, {}
    for k, n in enumerate(bras):
        V = m.v[n]
        r = _racine_membre(V, m.centre)
        bout = V[np.argmax(np.linalg.norm(V - r, axis=1))]
        d = bout - r
        nrm = float(np.hypot(d[0], d[1])) or 1.0
        nom = "b%d" % k
        dirs[nom] = (d[1] / nrm, -d[0] / nrm)                            # l'axe qui lève le bout du bras
        racines[nom], sects[nom] = r, V
        plan.os_(nom, "corps", r)
        plan.donne(n, nom)
    noms_b = list(racines)

    def proche(points, cote):
        w = {b: np.zeros(len(points)) for b in noms_b}
        dm = np.stack([np.linalg.norm(points[:, None, :] - sects[b][None, :: max(1, len(sects[b]) // 120), :], axis=2).min(axis=1)
                       for b in noms_b], axis=1)
        for i, j in enumerate(dm.argmin(axis=1)):
            w[noms_b[j]][i] = 1.0
        return w
    for n in m.v:
        if n not in bras and _debut(n, ("ventouse", "pastille")) and noms_b:
            plan.donne(n, proche)
    bones = {o[0] for o in plan.os}

    def a(p, os_, rot=(0, 0, 0), pos=(0, 0, 0), ech=(1, 1, 1)):
        if os_ in bones:
            p.add(os_, rot=rot, pos=pos, ech=ech)

    def bras_(p, t, lev, bal, tours=1.0, dephase=0.125):
        for k, nm in enumerate(noms_b):
            ax, ay = dirs[nm]
            ang = lev * (0.5 + 0.5 * math.sin(math.tau * (t * tours - dephase * k)))
            a(p, nm, rot=(ax * ang, ay * ang, bal * math.sin(math.tau * (t * tours - dephase * k + 0.25))))

    def repos(t):
        p = Pose(); r = onde(t, 2)
        a(p, "tete", rot=(2 * r, 0, 6 * cloche(t, 0.3, 0.15) - 6 * cloche(t, 0.7, 0.15)))
        bras_(p, t, 10.0, 8.0, 1.0)
        p.ouvert = 1 - cloche(t, 0.5, 0.02)
        return p

    def avance(t):
        p = Pose()
        a(p, "corps", pos=(0, 0, 0.02 * abs(math.sin(math.tau * t))))
        bras_(p, t, 26.0, 16.0, 1.0)
        a(p, "tete", rot=(-4 * math.sin(math.tau * t), 0, 0))
        return p

    def mange(t):
        p = Pose(); bas = cloche(t, 0.5, 0.35)
        bras_(p, t, 14.0 * (0.5 + bas), 10.0, 2.0)
        a(p, "tete", rot=(18 * bas, 0, 0))
        p.ouvert = 1 - cloche(t, 0.8, 0.02)
        return p

    def joie(t):
        p = Pose(); s = math.sin(math.pi * borne(t))
        bras_(p, t, 70.0 * s, 20.0 * s, 2.0)
        a(p, "corps", pos=(0, 0, 0.10 * s))
        a(p, "tete", rot=(-10 * s, 0, 0))
        return p

    def dort(t):
        p = Pose(); p.ouvert = 0.0; r = onde(t, 1)
        bras_(p, t, 5.0, 3.0, 1.0)
        a(p, "corps", pos=(0, 0, -0.01), ech=(1 + 0.03 * r, 1 + 0.03 * r, 1 - 0.04 * r))
        a(p, "tete", rot=(14, 0, 10))
        return p
    return plan, _animations(repos, avance, mange, joie, dort)


def rig_etoile(m, nb=5, angles_deg=None):
    """L'étoile de mer : une pièce d'un seul tenant ; un os par bras (pivot au centre), poids par secteur angulaire."""
    plan = Plan(m)
    V = m.v[m.corps_nom]
    cx, cy = float((V[:, 0].min() + V[:, 0].max()) / 2), float((V[:, 1].min() + V[:, 1].max()) / 2)
    cz = float(V[:, 2].min() + 0.30 * np.ptp(V[:, 2]))
    ang = [math.radians(x) for x in angles_deg] if angles_deg else [math.tau * k / nb + math.pi / 2 for k in range(nb)]
    nb = len(ang)
    rmax = float(np.hypot(V[:, 0] - cx, V[:, 1] - cy).max())
    noms = ["b%d" % k for k in range(nb)]
    for k in range(nb):
        plan.os_(noms[k], "corps", (cx, cy, cz))

    def poids(points, cote):
        dx, dy = points[:, 0] - cx, points[:, 1] - cy
        r = np.hypot(dx, dy)
        th = np.arctan2(dy, dx)
        w = np.zeros((len(points), nb))
        for k in range(nb):
            d = np.abs((th - ang[k] + math.pi) % math.tau - math.pi)
            w[:, k] = np.exp(-(d / 0.42) ** 2)
        w = w / (w.sum(axis=1, keepdims=True) + 1e-9)
        dehors = _smooth((r - 0.22 * rmax) / (0.30 * rmax))
        res = {noms[k]: w[:, k] * dehors for k in range(nb)}
        res["corps"] = 1.0 - dehors
        return res
    plan.donne(m.corps_nom, poids)
    bones = {o[0] for o in plan.os}
    dirs = [(math.sin(t_), -math.cos(t_)) for t_ in ang]                 # l'axe qui lève le bout d'un bras de direction t_

    def a(p, os_, rot=(0, 0, 0), pos=(0, 0, 0), ech=(1, 1, 1)):
        if os_ in bones:
            p.add(os_, rot=rot, pos=pos, ech=ech)

    def bras_(p, t, lev, tours=1.0, dephase=0.2, base=0.0):
        for k, nm in enumerate(noms):
            ax, ay = dirs[k]
            ang_k = base + lev * (0.5 + 0.5 * math.sin(math.tau * (t * tours - dephase * k)))
            a(p, nm, rot=(ax * ang_k, ay * ang_k, 0))

    def repos(t):
        p = Pose(); r = onde(t, 2)
        a(p, "corps", ech=(1 + 0.01 * r, 1 + 0.01 * r, 1 + 0.02 * r))
        bras_(p, t, 8.0, 1.0)
        p.ouvert = 1 - cloche(t, 0.5, 0.02)
        return p

    def avance(t):
        p = Pose()
        bras_(p, t, 30.0, 1.0, 0.2)
        a(p, "corps", rot=(0, 0, 8 * math.sin(math.tau * t)), pos=(0, 0, 0.01 * abs(math.sin(math.tau * t))))
        return p

    def mange(t):
        p = Pose(); bas = cloche(t, 0.5, 0.35)
        bras_(p, t, 12.0, 2.0, 0.2, base=-6 * bas)
        p.ouvert = 1 - cloche(t, 0.75, 0.02)
        return p

    def joie(t):
        p = Pose(); s = math.sin(math.pi * borne(t))
        bras_(p, t, 25.0 * s, 2.0, 0.2, base=55 * s)
        a(p, "corps", pos=(0, 0, 0.06 * s), rot=(0, 0, 40 * s))
        return p

    def dort(t):
        p = Pose(); p.ouvert = 0.0; r = onde(t, 1)
        bras_(p, t, 3.0, 1.0, 0.2, base=-4)
        a(p, "corps", ech=(1 + 0.02 * r, 1 + 0.02 * r, 1 + 0.03 * r))
        return p
    return plan, _animations(repos, avance, mange, joie, dort)


def rig_meduse(m):
    """La méduse : la cloche pulse ; chaque ruban ou filament est une pièce, un os (pivot en haut), qui ondule."""
    plan = Plan(m)
    pend = [n for n in sorted(m.v) if _debut(n, ("ruban", "filament", "tentacule", "bras"))]
    for k, n in enumerate(pend):
        V = m.v[n]
        haut = V[V[:, 2] >= V[:, 2].max() - 0.1 * np.ptp(V[:, 2])].mean(axis=0)
        plan.os_("t%d" % k, "corps", haut)
        plan.donne(n, "t%d" % k)
    _tete_bones(m, plan)
    bones = {o[0] for o in plan.os}
    N = len(pend)

    def a(p, os_, rot=(0, 0, 0), pos=(0, 0, 0), ech=(1, 1, 1)):
        if os_ in bones:
            p.add(os_, rot=rot, pos=pos, ech=ech)

    def pend_(p, t, amp, tours=1.0):
        for k in range(N):
            ph = 0.11 * k
            a(p, "t%d" % k, rot=(amp * math.sin(math.tau * (t * tours - ph)), 0, 0.6 * amp * math.sin(math.tau * (t * tours - ph + 0.25))))

    def repos(t):
        p = Pose(); r = onde(t, 2)
        a(p, "corps", ech=(1 + 0.04 * r, 1 + 0.04 * r, 1 - 0.05 * r), pos=(0, 0, 0.01 * r))
        pend_(p, t, 8.0)
        p.ouvert = 1 - cloche(t, 0.5, 0.02)
        return p

    def avance(t):
        p = Pose(); r = onde(t, 2)
        a(p, "corps", ech=(1 + 0.12 * r, 1 + 0.12 * r, 1 - 0.14 * r), pos=(0, 0, 0.04 * (1 + r)))
        pend_(p, t, 16.0, 2.0)
        return p

    def mange(t):
        p = Pose(); bas = cloche(t, 0.5, 0.3)
        a(p, "corps", rot=(12 * bas, 0, 0), ech=(1 + 0.05 * onde(t, 3), 1 + 0.05 * onde(t, 3), 1))
        pend_(p, t, 10.0, 1.0)
        p.ouvert = 1 - cloche(t, 0.8, 0.02)
        return p

    def joie(t):
        p = Pose(); s = math.sin(math.pi * borne(t))
        a(p, "corps", ech=(1 + 0.14 * s * onde(t, 3), 1 + 0.14 * s * onde(t, 3), 1 - 0.16 * s * onde(t, 3)), pos=(0, 0, 0.14 * s), rot=(0, 0, 72 * s))
        pend_(p, t, 24.0 * s, 3.0)
        return p

    def dort(t):
        p = Pose(); p.ouvert = 0.0; r = onde(t, 1)
        a(p, "corps", ech=(1 + 0.03 * r, 1 + 0.03 * r, 1 - 0.04 * r), pos=(0, 0, -0.02))
        pend_(p, t, 4.0)
        return p
    return plan, _animations(repos, avance, mange, joie, dort)


def rig_limace(m, n=5):
    """Une limace de mer : la chaîne de tronçons le long de Y, tout suit par les poids ; la reptation : une onde verticale
    qui court, le corps qui s'étire et se contracte."""
    plan = Plan(m)
    noms, ys, _y0, _y1 = _chaine(m, plan, n)
    poids = _poids_chaine(noms, ys)
    for nom in m.v:
        plan.donne(nom, poids)
    bones = {o[0] for o in plan.os}

    def a(p, os_, rot=(0, 0, 0), pos=(0, 0, 0), ech=(1, 1, 1)):
        if os_ in bones:
            p.add(os_, rot=rot, pos=pos, ech=ech)

    def onde_(p, t, amp, lat, tours=1.0, etire=0.0):
        for k, nm in enumerate(noms):
            ph = 0.17 * k
            s_ = math.sin(math.tau * (t * tours - ph))
            a(p, nm, rot=(amp * s_, 0, lat * math.sin(math.tau * (t * tours - ph + 0.25))), ech=(1.0, 1.0 + etire * s_, 1.0 - 0.5 * etire * s_))

    def repos(t):
        p = Pose(); onde_(p, t, 3.0, 4.0, 1.0, 0.02)
        p.ouvert = 1 - cloche(t, 0.5, 0.02)
        return p

    def avance(t):
        p = Pose(); onde_(p, t, 10.0, 6.0, 2.0, 0.07)
        return p

    def mange(t):
        p = Pose(); bas = cloche(t, 0.5, 0.35)
        onde_(p, t, 4.0, 3.0, 1.0, 0.02)
        a(p, "corps", rot=(16 * bas, 0, 0))
        p.ouvert = 1 - cloche(t, 0.8, 0.02)
        return p

    def joie(t):
        p = Pose(); s = math.sin(math.pi * borne(t))
        onde_(p, t, 24.0 * s, 16.0 * s, 2.0, 0.10 * s)
        a(p, "corps", rot=(-18 * s, 0, 0), pos=(0, 0, 0.05 * s))
        return p

    def dort(t):
        p = Pose(); p.ouvert = 0.0
        onde_(p, t, 1.5, 2.0, 1.0, 0.02)
        for nm in noms[1:]:
            a(p, nm, rot=(0, 0, 6.0))
        return p
    return plan, _animations(repos, avance, mange, joie, dort)
