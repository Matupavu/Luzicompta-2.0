# utils.py est un fichier qui contient le code pour sauvegarder et charger un devis. Il contient deux fonctions save_quotation et load_quotation qui sont appelées dans le fichier invoice.py pour sauvegarder et charger un devis.

import json
import os
from datetime import datetime
import sqlite3

# Obtenir le chemin absolu du répertoire courant
current_dir = os.path.dirname(os.path.abspath(__file__))
devis_dir = os.path.join(current_dir, 'devis')
invoices_dir = os.path.join(current_dir, 'invoices')

# Assurer que les répertoires pour stocker les devis et les factures existent
os.makedirs(devis_dir, exist_ok=True)
os.makedirs(invoices_dir, exist_ok=True)

def save_quotation(data, filename=None):
    """Save a quotation to a JSON file."""
    try:
        if filename is None:
            filename = os.path.join(devis_dir, f'quotation_{data["Numéro de devis"]}.json')
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Devis sauvegardé avec succès: {filename}")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du devis: {e}")
        return False

def load_quotation(devis_number=None):
    """Load a quotation from a JSON file."""
    try:
        if devis_number:
            filename = os.path.join(devis_dir, f'quotation_{devis_number}.json')
            if not os.path.exists(filename):
                print(f"Le fichier {filename} n'existe pas.")
                return None
            with open(filename, 'r') as f:
                data = json.load(f)
                if data.get("Numéro de devis") == devis_number:
                    return data
                else:
                    print(f"Numéro de devis incorrect dans le fichier {filename}.")
                    return None
        else:
            raise FileNotFoundError("Numéro de devis non spécifié.")
    except FileNotFoundError:
        print(f"Aucun devis trouvé pour {devis_number}.")
        return None
    except json.JSONDecodeError:
        print("Erreur de décodage JSON.")
        return None
    except Exception as e:
        print(f"Erreur lors du chargement du devis: {e}")
        return None

def generate_devis_number():
    """Generate a new quotation number."""
    date_str = datetime.now().strftime("%Y-%m")
    base_number = f"DE{date_str}-"
    number = 1

    # Vérifier les numéros de devis existants dans les fichiers
    if os.path.exists(devis_dir):
        files = os.listdir(devis_dir)
        existing_numbers = [int(f.split('-')[-1].split('.')[0]) for f in files if f.startswith(base_number)]
        if existing_numbers:
            number = max(existing_numbers) + 1

    # Vérifiez également dans la base de données pour les numéros de devis existants
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUBSTR(devis_number, -3, 3) FROM devis
        WHERE devis_number LIKE ?
    ''', (base_number + '%',))
    db_numbers = cursor.fetchall()
    conn.close()

    if db_numbers:
        db_numbers = [int(num[0]) for num in db_numbers]
        if db_numbers:
            number = max(number, max(db_numbers) + 1)

    return f"{base_number}{str(number).zfill(3)}"

def generate_invoice_number():
    """Generate a new invoice number."""
    date_str = datetime.now().strftime("%Y%m")
    base_number = f"FA{date_str}-"
    number = 1

    existing_numbers = []
    for f in os.listdir(invoices_dir):
        if f.startswith(base_number) and f.endswith('.json'):
            try:
                existing_numbers.append(int(f.split('-')[-1].split('.')[0]))
            except ValueError:
                pass

    if existing_numbers:
        number = max(existing_numbers) + 1

    return f"{base_number}{str(number).zfill(3)}"

# Test des fonctions de génération de numéro
if __name__ == "__main__":
    print(generate_devis_number())
    print(generate_invoice_number())
