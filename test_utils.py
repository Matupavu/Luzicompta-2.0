from utils import save_quotation, load_quotation, generate_devis_number

# Générer un numéro de devis pour le test
devis_number = generate_devis_number()

data = {
    "Numéro de devis": devis_number,
    "Nom du client": "Client Test",
    "Nom du demandeur": "Demandeur Test",
    "Adresse": "123 Rue Exemple",
    "Code Postal": "75001",
    "Ville": "Paris",
    "Date du devis": "01/01/2024",
    "Nature de l'intervention": "Test de sauvegarde",
    "Tableau": [
        ["Service A", "U", 1, 1000, 1000, "20%", 200, 1200]
    ],
    "Montant HT": "1000",
    "Montant TVA": "200",
    "Total dû TTC": "1200",
    "Notes": "Ceci est une note de test"
}

# Sauvegarder le devis
save_quotation(data)

# Charger le devis
loaded_data = load_quotation(devis_number=devis_number)
print(loaded_data)
