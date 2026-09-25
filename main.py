from rendu.leonel import ajouter_nombres, afficher_liste, somme
from rendu.clement.variance_stddiv.app.statistiques import ecart_type, variance_population
from truc import maximum, quantite


def afficher_menu() -> None:
    print("===== MENU =====")
    print("1. Ajouter des nombres")
    print("2. Afficher la liste")
    print("3. Moyenne")
    print("4. Minimum")
    print("5. Maximum")
    print("6. Quantité de données")
    print("7. Écart type")
    print("8. Somme")
    print("9. Variance de population")
    print("0. Quitter")


def lire_choix() -> int:
    while True:
        saisie = input("Votre choix : ").strip()
        try:
            choix = int(saisie)
        except ValueError:
            print("Erreur : veuillez entrer un nombre entier entre 0 et 9.")
            continue

        if 0 <= choix <= 9:
            return choix
        print("Erreur : veuillez entrer un nombre entier entre 0 et 9.")


def _appeler_ilian(nom_fonction: str, nombres: list[float]):
    # rendu/ilian.py plante à l'import (variable `lst` non définie en fin de
    # fichier) et moyenne_absurde() a en plus besoin de Docker/gcc/g++.
    # On isole l'appel pour que ce module cassé ne fasse pas planter le menu.
    try:
        from rendu import ilian
        return getattr(ilian, nom_fonction)(nombres)
    except Exception as erreur:
        print(f"Erreur : le module d'Ilian est indisponible ({erreur}).")
        return None


def main() -> None:
    nombres: list[float] = []

    while True:
        afficher_menu()
        choix = lire_choix()

        if choix == 1:
            ajouter_nombres(nombres)

        elif choix == 2:
            afficher_liste(nombres)

        elif choix == 3:
            if not nombres:
                print("La liste est vide.")
            else:
                resultat = _appeler_ilian("moyenne_absurde", nombres)
                if resultat is not None:
                    print(f"Moyenne : {resultat:.2f}")

        elif choix == 4:
            if not nombres:
                print("La liste est vide.")
            else:
                resultat = _appeler_ilian("min", nombres)
                if resultat is not None:
                    print(f"Minimum : {resultat:.2f}")

        elif choix == 5:
            if not nombres:
                print("La liste est vide.")
            else:
                resultat = maximum(nombres)
                print(f"Maximum : {resultat:.2f}")

        elif choix == 6:
            resultat = quantite(nombres)
            print(f"La liste contient {resultat} nombre(s).")

        elif choix == 7:
            if not nombres:
                print("La liste est vide.")
            else:
                resultat = ecart_type(nombres)
                print(f"Écart type : {resultat:.2f}")

        elif choix == 8:
            somme(nombres)

        elif choix == 9:
            if not nombres:
                print("La liste est vide.")
            else:
                resultat = variance_population(nombres)
                print(f"Variance de population : {resultat:.2f}")

        elif choix == 0:
            print("Au revoir")
            break

        print()


if __name__ == "__main__":
    main()
