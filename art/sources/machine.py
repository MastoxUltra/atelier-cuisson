"""Ménager la machine : le PC d'l'auteur est un portable à un seul ventilateur, et il joue dessus.

Tout calcul Blender (une fiche d'animal, une fabrication de l'usine) passe par ici :
    with machine.tour("fiche renard", 300):      # un seul à la fois sur toute la machine, quelle que soit la session
        ... le calcul ...
Le tour attend de lui-même : qu'aucun autre calcul ne tienne le verrou, qu'aucun jeu ne tourne, que la carte graphique
soit redescendue. Il renonce au bout d'une demi-heure plutôt que de forcer.

    python machine.py                          dit seulement si la machine est libre et froide
    python machine.py prendre "essai du jeu" 240  attend son tour, puis prend le verrou pour 240 secondes au plus
    python machine.py rendre "essai du jeu"       le rend (à faire dès que l'essai est fini)
Ces deux dernières commandes servent aux autres sessions (un essai Godot, par exemple) : tant qu'elles tiennent le
verrou, aucun Blender de la session Art ne démarre ; et elles n'attendent jamais derrière plus d'un calcul.

Sur une machine louée (Kaggle, Colab : voir art/distant/), BIBELOTS_DISTANT=1 rend tour, prendre, rendre, souffler et
ceder immédiats et sans effet : ni verrou, ni jeu à ménager, ni carte qui chauffe. Sans cette variable, rien ne change.

OBLIGATOIRE depuis le 15/10/2026 (surchauffe de 9 h 15 : sept rendus Blender hors du verrou, le processeur à 97 %) :
- tout Python du venv des outils qui charge le VRAI bpy prend le verrou de lui-même, au chargement, sous le nom
  « rendu : <script> <arguments> », et le garde jusqu'à sa fin (verrou_auto ; le crochet est
  bibelots-outils/venv/Lib/site-packages/bibelots_verrou.pth). Ses enfants et ses « tour » imbriqués ne le reprennent pas ;
- avant de calculer, on regarde aussi le processeur : chargé à 60 % ou plus sur 5 s (sans compter le détenteur du verrou,
  qui à ce moment-là ne calcule pas encore), on ATTEND. La commande « prendre » (les essais du jeu) aussi.
"""
import os
import subprocess
import sys
import time
from contextlib import contextmanager

JEUX = ("league of legends", "leagueclient", "valorant", "rocketleague", "godot")
CHAUD, OCCUPEE, PATIENCE = 78.0, 40.0, 1800        # degrés, pour cent, secondes
VERROU = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".usine.verrou")
PRIORITE = VERROU + ".priorite"
_COURANT = None                                     # le tour que tient ce processus : (nom, durée)
PRESSES = ("styles", "essai du jeu", "la fiche", "la photo")   # ce qui est court ou attendu tout de suite passe devant les longues fabrications
DISTANT = os.environ.get("BIBELOTS_DISTANT") == "1"  # une machine louée (art/distant/) : on ne ménage rien
CPU_MAX, CPU_SECONDES = 60.0, 5.0                   # le processeur : au-delà de 60 % de charge sur 5 s, on attend
AUTO = "BIBELOTS_VERROU_AUTO"                       # le pid du processus qui tient le verrou pour tout son calcul (pris au
                                                    # chargement de bpy) : lui, ses enfants et ses tours imbriqués ne le reprennent pas
ARRET = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".pas_de_calcul_ici")
# L'INTERRUPTEUR : tant que ce fichier existe, aucun calcul de l'art (Blender, fiches, fabrications) ne tourne sur ce PC ;
# tout part sur Kaggle (art/distant/). Sans ce fichier : permis, un calcul à la fois par ce verrou. Les essais du jeu
# (Godot) ne sont jamais concernés. Posé le 14/10/2026 après un arrêt net de la machine à 86 °C.


JOUE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".arthur_joue")
# LA PAUSE D'ARTHUR (Principal, 15/10) : tant que ce fichier existe, RIEN ne tourne sur ce PC, pas même les essais du jeu ;
# tout part en ligne (Kaggle, GitHub, Codespaces). Principal l'efface quand l'auteur a fini de jouer.


def _interdit(nom):
    if not DISTANT and os.path.exists(JOUE):
        print("[machine] REFUSÉ : « %s ». l'auteur joue sur ce PC, rien ne tourne ici (même les essais). Travaille en ligne "
              "(art/distant/LISEZMOI.md) ou attends que Principal efface art/sources/.arthur_joue" % nom, flush=True)
        raise SystemExit(3)
    if DISTANT or "essai du jeu" in nom or not os.path.exists(ARRET):
        return
    print("[machine] REFUSÉ : « %s » ne tourne plus sur ce PC (%s). Dépose-le dans la file Kaggle : art/distant/LISEZMOI.md"
          % (nom, open(ARRET, encoding="utf-8").read().strip()), flush=True)
    raise SystemExit(3)


CEDER_A = ("essai du jeu", "la photo")             # une fabrication ne s'interrompt que pour un essai du jeu ou une photo, pas pour une fiche
_REPRISE = False                                   # une fabrication qui a cédé sa place reprend en priorité : son travail est à moitié fait


def _presse(nom):
    """Pressé par son nom, ou parce qu'on l'a lancé avec BIBELOTS_PRESSE=1 (une fabrication qu'une autre session attend),
    ou parce qu'il reprend après avoir laissé passer quelqu'un."""
    return _REPRISE or os.environ.get("BIBELOTS_PRESSE") == "1" or any(mot in nom for mot in PRESSES)


def _un_presse_attend():
    """Un calcul pressé attend-il son tour ? (il le dit en touchant un fichier, toutes les quinze secondes)"""
    try:
        return time.time() - os.path.getmtime(PRIORITE) < 40
    except OSError:
        return False


def _je_suis_presse(nom):
    try:
        with open(PRIORITE, "w", encoding="utf-8") as f:
            f.write(nom)
    except OSError:
        pass


def etat():
    """La température de la carte graphique, son occupation en pour cent, et le jeu qui tourne (ou None)."""
    temp = occupation = jeu = None
    try:
        sortie = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu,utilization.gpu", "--format=csv,noheader,nounits"],
                                capture_output=True, text=True, timeout=10).stdout
        temp, occupation = (float(x) for x in sortie.strip().splitlines()[0].split(","))
    except Exception:
        pass
    try:
        taches = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=15).stdout.lower()
        jeu = next((j for j in JEUX if j in taches), None)
    except Exception:
        pass
    return temp, occupation, jeu


def _temps_cpu():
    """(temps d'inactivité, temps total) de tous les cœurs, en centaines de nanosecondes (Windows : GetSystemTimes)."""
    import ctypes
    from ctypes import wintypes
    inactif, noyau, usager = wintypes.FILETIME(), wintypes.FILETIME(), wintypes.FILETIME()
    if not ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(inactif), ctypes.byref(noyau), ctypes.byref(usager)):
        raise OSError("GetSystemTimes")
    f = lambda t: (t.dwHighDateTime << 32) | t.dwLowDateTime
    return f(inactif), f(noyau) + f(usager)          # le temps « noyau » compte déjà l'inactivité


def charge_cpu(secondes=CPU_SECONDES):
    """La charge du processeur, en pour cent, mesurée sur « secondes » (None si on ne sait pas la lire)."""
    try:
        i0, t0 = _temps_cpu()
        time.sleep(secondes)
        i1, t1 = _temps_cpu()
    except Exception:
        return None
    total = t1 - t0
    return max(0.0, min(100.0, 100.0 * (1.0 - (i1 - i0) / total))) if total > 0 else None


def _raison(occupation_comptee=True, seuil=CHAUD, cpu=False):
    """Ce qui empêche de lancer un calcul lourd tout de suite, ou None si la machine est prête. cpu : regarder aussi la charge
    du processeur (5 s de mesure ; seulement au moment de prendre la machine, pas entre deux photos)."""
    temp, occupation, jeu = etat()
    raison = ("le jeu « %s » tourne" % jeu if jeu else "la carte graphique est à %d °C" % temp if temp is not None and temp >= seuil
              else "la carte graphique est occupée à %d %%" % occupation if occupation_comptee and occupation is not None and occupation >= OCCUPEE else None)
    if raison is None and cpu:
        charge = charge_cpu()
        if charge is not None and charge >= CPU_MAX:
            raison = "le processeur est chargé à %d %% (sur %d s)" % (charge, CPU_SECONDES)
    return raison


def _tenu_par_moi():
    """Le verrou est-il à ce processus, ou à son parent qui le tient pour tout son calcul (verrou_auto) ?"""
    try:
        _nom, pid, _duree = open(VERROU, encoding="utf-8").read().strip().split("|")
    except Exception:
        return False
    return pid == str(os.getpid()) or (pid != "" and pid == os.environ.get(AUTO, ""))


def souffler(quoi, occupation_comptee=True, seuil=CHAUD):
    """À appeler avant un calcul lourd : si un jeu tourne, si la carte est chaude ou prise par un autre, on attend."""
    if DISTANT:
        return
    debut = time.time()
    while True:
        raison = _raison(occupation_comptee, seuil)
        if raison is None:
            return
        if time.time() - debut > PATIENCE:
            raise SystemExit("[machine] arrêt avant %s : %s depuis %d minutes" % (quoi, raison, PATIENCE // 60))
        print("[machine] j'attends avant %s : %s" % (quoi, raison), flush=True)
        ceder()                                     # tant qu'à attendre, autant laisser passer un essai du jeu
        time.sleep(30)


def _tenu():
    """Qui tient le verrou (son nom), ou None. Un verrou plus vieux que la durée annoncée par son tenant est périmé :
    son calcul a été tué sans pouvoir le rendre."""
    try:
        nom, _pid, duree = open(VERROU, encoding="utf-8").read().strip().split("|")
        if time.time() - os.path.getmtime(VERROU) < float(duree):
            return nom
        os.remove(VERROU)
    except FileNotFoundError:
        pass
    except Exception:                               # un verrou illisible (ancien format) : on le garde vingt minutes au plus
        try:
            if time.time() - os.path.getmtime(VERROU) < 1200:
                return "un calcul"
            os.remove(VERROU)
        except OSError:
            pass
    return None


def prendre(nom, duree, patience=PATIENCE):
    """Prend le verrou pour « duree » secondes au plus. La création du fichier est atomique : deux calculs
    qui arrivent ensemble ne peuvent pas le prendre tous les deux."""
    if DISTANT:
        return
    _interdit(nom)
    if _tenu_par_moi():                             # déjà à moi (ou à mon parent) : rien à reprendre
        return
    debut = time.time()
    while True:
        if _presse(nom):
            _je_suis_presse(nom)
        tenant = _tenu()
        if tenant is None and not _presse(nom) and _un_presse_attend():
            tenant = "un calcul pressé (je le laisse passer)"
        elif tenant is None:
            try:
                poignee = os.open(VERROU, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(poignee, ("%s|%d|%d" % (nom, os.getpid(), duree)).encode("utf-8"))
                os.close(poignee)
                return
            except FileExistsError:
                tenant = "un calcul"
        if time.time() - debut > patience:
            raise SystemExit("[machine] arrêt : « %s » tient le verrou depuis %d minutes" % (tenant, patience // 60))
        print("[machine] j'attends mon tour : %s est en cours" % tenant, flush=True)
        time.sleep(15)


def rendre(nom=None, force=False):
    """Rend le verrou : le sien (même processus), ou celui qui porte ce nom (pris par la commande « prendre »). Celui d'un
    calcul entier (verrou_auto) ne se rend qu'à sa fin, ou de force (ceder)."""
    if DISTANT:
        return
    if not force and nom is None and os.environ.get(AUTO) == str(os.getpid()):
        return
    try:
        tenant, pid, _duree = open(VERROU, encoding="utf-8").read().strip().split("|")
        if (nom is None and pid == str(os.getpid())) or (nom is not None and tenant == nom):
            if _presse(tenant):                     # le suivant de la même série a quarante secondes pour se présenter
                _je_suis_presse(tenant)
            os.remove(VERROU)
    except Exception:
        pass


@contextmanager
def tour(nom, duree):
    """Un calcul lourd, seul sur la machine, à froid, sans jeu en cours.
    On n'attend JAMAIS en tenant le verrou : si la machine n'est pas prête (un jeu tourne, la carte est chaude), on le rend
    et on se représente trente secondes plus tard. Sinon un essai du jeu reste bloqué derrière un calcul qui ne calcule pas
    (la nuit du 14 octobre 2026 : vingt minutes perdues)."""
    global _COURANT
    _interdit(nom)
    if DISTANT:
        yield
        return
    if _tenu_par_moi():                             # dans un calcul qui tient déjà la machine (verrou_auto) : on continue
        ancien, _COURANT = _COURANT, (nom, duree)
        try:
            yield
        finally:
            _COURANT = ancien
        return
    debut = time.time()
    while True:
        prendre(nom, duree)
        raison = _raison(cpu=True)
        if raison is None:
            break
        rendre()
        if time.time() - debut > PATIENCE:
            raise SystemExit("[machine] arrêt avant %s : %s depuis %d minutes" % (nom, raison, PATIENCE // 60))
        print("[machine] j'attends avant %s (verrou rendu) : %s" % (nom, raison), flush=True)
        time.sleep(30)
    _COURANT = (nom, duree)
    try:
        yield
    finally:
        _COURANT = None
        rendre()


def ceder():
    """À appeler entre deux étapes d'un long calcul (avant chaque cuisson de l'usine) : si quelqu'un de pressé attend,
    un essai du jeu par exemple, on lui laisse la machine et on reprend après lui. Une fabrication tient la machine
    vingt-cinq minutes : sans cela, aucun essai du jeu ne passe pendant tout ce temps."""
    if DISTANT or _COURANT is None:
        return
    try:
        attend = open(PRIORITE, encoding="utf-8").read().strip()
    except OSError:
        return
    if not _un_presse_attend() or attend == _COURANT[0] or not any(mot in attend for mot in CEDER_A):
        return
    print("[machine] je laisse passer « %s », je reprends après" % attend, flush=True)
    global _REPRISE
    rendre(force=True)
    time.sleep(25)                                  # le temps qu'il prenne le verrou (il se présente toutes les quinze secondes)
    _REPRISE = True                                 # puis on reprend avant les autres : le travail est à moitié fait, et on attend plus longtemps
    try:
        prendre(*_COURANT, patience=3 * PATIENCE)
    finally:
        _REPRISE = False


def _battre():
    """Tant que le calcul tourne, le verrou reste frais (s'il est tué net, il est périmé dix minutes plus tard)."""
    while True:
        time.sleep(60)
        try:
            if _tenu_par_moi():
                os.utime(VERROU, None)
        except OSError:
            pass


def verrou_auto():
    """Le verrou obligatoire : appelé au chargement du vrai bpy (le crochet bibelots_verrou.pth du venv des outils). Attend son
    tour comme « tour » (verrou libre, pas de jeu, carte froide, processeur à moins de 60 %), puis tient la machine jusqu'à la
    fin du processus. Sans effet sur une machine louée, ou si le verrou est déjà à ce processus ou à son parent."""
    if DISTANT or os.environ.get(AUTO) or _tenu_par_moi():
        return
    import atexit
    import threading
    nom = "rendu : " + " ".join([os.path.basename(sys.argv[0] if sys.argv and sys.argv[0] else "python")] + list(sys.argv[1:3]))
    _interdit(nom)
    debut = time.time()
    while True:
        prendre(nom, 600)
        raison = _raison(cpu=True)
        if raison is None:
            break
        rendre(force=True)
        if time.time() - debut > PATIENCE:
            raise SystemExit("[machine] arrêt avant %s : %s depuis %d minutes" % (nom, raison, PATIENCE // 60))
        print("[machine] j'attends avant %s (verrou rendu) : %s" % (nom, raison), flush=True)
        time.sleep(30)
    os.environ[AUTO] = str(os.getpid())
    print("[machine] verrou pris pour tout le calcul : « %s »" % nom, flush=True)
    atexit.register(lambda: rendre(force=True))
    threading.Thread(target=_battre, daemon=True).start()


def prendre_au_frais(nom, duree):
    """La commande « prendre » (un essai du jeu) : le verrou, puis on attend que le processeur soit retombé sous 60 %
    (sinon on rend le verrou, et on se représente trente secondes plus tard)."""
    debut = time.time()
    while True:
        prendre(nom, duree)
        if DISTANT:
            return
        charge = charge_cpu()
        if charge is None or charge < CPU_MAX:
            return
        rendre(nom)
        if time.time() - debut > PATIENCE:
            raise SystemExit("[machine] arrêt : le processeur est resté chargé (%d %%) pendant %d minutes" % (charge, PATIENCE // 60))
        print("[machine] j'attends avant « %s » (verrou rendu) : le processeur est chargé à %d %%" % (nom, charge), flush=True)
        time.sleep(30)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "prendre":
        prendre_au_frais(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 240)
        print("[machine] verrou pris par « %s »" % sys.argv[2])
        sys.exit(0)
    if len(sys.argv) >= 3 and sys.argv[1] == "rendre":
        rendre(sys.argv[2])
        print("[machine] verrou rendu par « %s »" % sys.argv[2])
        sys.exit(0)
    temp, occupation, jeu = etat()
    tenant = _tenu()
    charge = charge_cpu()
    libre = not jeu and (temp is None or temp < CHAUD) and (occupation is None or occupation < OCCUPEE) and tenant is None and \
        (charge is None or charge < CPU_MAX)
    print("[machine] carte graphique %s °C, occupée à %s %%, processeur %s %%, jeu : %s, verrou : %s -> %s" % (
        temp, occupation, "?" if charge is None else int(round(charge)), jeu or "aucun", tenant or "libre", "LIBRE" if libre else "ATTENDRE"))
