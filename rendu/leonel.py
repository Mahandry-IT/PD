def ajouter_nombres(liste):
    compteur = 0
    while True:
        saisie = input('Saisir un nombre (ou "fin") : ')
        if saisie.lower() == "fin":
            break
        try:
            nombre = float(saisie)
            if nombre.is_integer():
                nombre = int(nombre)
            liste.append(nombre)
            compteur += 1
        except ValueError:
            print("Erreur : veuillez saisir un nombre.")
    print(f"{compteur} nombre(s) ajouté(s).")


def afficher_liste(liste):
    print("Liste :", liste)


def somme(liste):
    total = sum(liste)
    print(f"Somme : {total:.2f}")