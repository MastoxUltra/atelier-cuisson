"""Étire ou tasse un animal tout fait (sœur B, 16/10) : « python silhouettes.py » montre si ses proportions ne sont pas celles de la
bête (chameaux sur échasses, corps trop court) ; on corrige alors d'un coup, à la fin de construire(), avant « return a » :

    import deformer_b as DF
    DF.etirer(a, sy=1.25, sz=0.78)      # le corps plus long de 25 %, le tout plus bas de 22 % (pattes et cou raccourcis)

Toutes les pièces, les yeux (position, direction), le point visé du gros plan suivent. Après un changement de proportions, le
squelette généré se refait : retirer la section « pour le jeu » du fichier puis « gen_jeu.py <bête> --ecrire »."""
import numpy as np
from mathutils import Vector


def etirer(a, sx=1.0, sy=1.0, sz=1.0):
    S = np.diag([sx, sy, sz])
    Sinv_T = np.linalg.inv(S).T
    for p in a._toutes():
        p["monde"] = np.asarray(p["monde"], float) @ S.T
    if a.tete is not None:
        a.tete = Vector(tuple(S @ np.array(a.tete, float)))
    nouveaux = []
    for n, pos, vers, r, pr in a._boutons:
        v = Sinv_T @ np.array(vers, float)
        v = v / max(np.linalg.norm(v), 1e-9)
        nouveaux.append((n, Vector(tuple(S @ np.array(pos, float))), Vector(tuple(v)), r, pr))
    a._boutons = nouveaux
    return a
