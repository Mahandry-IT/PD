# =========================================================================
# Fonction 1 : ajouter_nombres -> le detour "compilateur artisanal"
# saisie utilisateur -> tokens -> mini-langage maison -> AST -> eval()
# =========================================================================

import ast
import re


class TokenAjout:
    """Un 'compilateur' pour un langage qui ne sait faire qu'une chose :
    dire si une chaine est 'fin' ou un nombre. Totalement inutile, donc parfait."""

    GRAMMAIRE = re.compile(r"^\s*(?P<fin>fin)\s*$|^\s*(?P<nombre>-?\d+(\.\d+)?)\s*$", re.IGNORECASE)

    @staticmethod
    def analyser(saisie):
        m = TokenAjout.GRAMMAIRE.match(saisie)
        if not m:
            return ("ERREUR", None)
        if m.group("fin"):
            return ("FIN", None)
        # on reconstruit un mini programme Python juste pour appeler ast.literal_eval
        code = f"__valeur__ = {m.group('nombre')}"
        arbre = ast.parse(code)
        module = compile(arbre, "<ajout>", "exec")
        espace = {}
        exec(module, espace)
        return ("NOMBRE", espace["__valeur__"])


def ajouter_nombres(liste):
    compteur = 0
    while True:
        saisie = input('Saisir un nombre (ou "fin") : ')
        genre, valeur = TokenAjout.analyser(saisie)

        if genre == "FIN":
            break
        elif genre == "NOMBRE":
            if float(valeur).is_integer():
                valeur = int(valeur)
            liste.append(valeur)
            compteur += 1
        else:
            print("Erreur : veuillez saisir un nombre.")
    print(f"{compteur} nombre(s) ajoutÃ©(s).")


# =========================================================================
# Fonction 2 : afficher_liste -> le detour "serialisation cryptee inutile"
# liste -> JSON -> base64 -> "chiffrement" XOR -> dechiffrement -> reparsing
# =========================================================================

import json
import base64

CLE_SECRETE = 42  # niveau de securite maximal


def _chiffrer(texte):
    octets = texte.encode("utf-8")
    xor = bytes(b ^ CLE_SECRETE for b in octets)
    return base64.b64encode(xor).decode("ascii")


def _dechiffrer(jeton):
    xor = base64.b64decode(jeton.encode("ascii"))
    octets = bytes(b ^ CLE_SECRETE for b in xor)
    return octets.decode("utf-8")


def afficher_liste(liste):
    # on serialise la liste... pour la dechiffrer aussitot apres
    jeton = _chiffrer(json.dumps(liste))
    liste_reconstruite = json.loads(_dechiffrer(jeton))
    print("Liste :", liste_reconstruite)


# =========================================================================
# Fonction 8 : somme -> le detour "sous-processus qui refait l'addition"
# nombres -> fichier temporaire -> script Python enfant -> stdout -> parsing
# =========================================================================

import subprocess
import sys
import tempfile
import os


unitile = """
import sys, json
nombres = json.loads(sys.argv[1])
total = 0
for x in nombres:
    total = total + x  # une addition a la fois, comme il se doit
print(f"{total:.2f}")
"""


def somme(liste):
    dossier = tempfile.mkdtemp()
    script = os.path.join(dossier, "additionneur.py")
    with open(script, "w") as f:
        f.write(unitile)

    resultat = subprocess.run(
        [sys.executable, script, json.dumps(liste)],
        capture_output=True, text=True, check=True,
    )
    print(f"Somme : {resultat.stdout.strip()}")