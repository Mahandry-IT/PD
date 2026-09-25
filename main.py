from rendu.ilian import moyenne_absurde

def afficher_menu():
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

def lire_choix():
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


def main():
    while True:
        afficher_menu()
        choix = lire_choix()

        if choix == 1:
            print("-> Ici : ajouter des nombres")
        elif choix == 2:
            print("-> Ici : afficher la liste")
        elif choix == 3:
            print("-> Ici : moyenne")
        elif choix == 4:
            print("-> Ici : minimum")
        elif choix == 5:
            print("-> Ici : maximum")
        elif choix == 6:
            print("-> Ici : quantité de données")
        elif choix == 7:
            print("-> Ici : écart type")
        elif choix == 8:
            print("-> Ici : somme")
        elif choix == 9:
            print("-> Ici : variance de population")
        elif choix == 0:
            print("Au revoir")
            break

        print()

if __name__ == "__main__":
    main()