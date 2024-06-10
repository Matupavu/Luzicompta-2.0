#database.py est un fichier qui contient le code pour la gestion de la base de données SQLite de l'application LuziCompta. Il contient des formules pour créer une connexion à la base de données, créer une table, insérer des données dans la table et rechercher des données dans la table. Voici le contenu du fichier database.py:

import sqlite3

def create_devis_table():
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                devis_number TEXT NOT NULL UNIQUE,
                client_name TEXT,
                requester_name TEXT,
                address TEXT,
                postal_code TEXT,
                city TEXT,
                date TEXT,
                intervention TEXT,
                amount_ht TEXT,
                amount_tva TEXT,
                amount_ttc TEXT,
                notes TEXT
            )
        ''')
        conn.commit()

def insert_devis(data):
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        # Vérifier si le numéro de devis existe déjà
        cursor.execute('''
            SELECT COUNT(*) FROM devis WHERE devis_number = ?
        ''', (data["Numéro de devis"],))
        if cursor.fetchone()[0] > 0:
            raise sqlite3.IntegrityError("Le numéro de devis existe déjà.")
        
        cursor.execute('''
            INSERT INTO devis (devis_number, client_name, requester_name, address, postal_code, city, date, intervention, amount_ht, amount_tva, amount_ttc, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["Numéro de devis"], data["Nom du client"], data["Nom du demandeur"], data["Adresse"], data["Code Postal"],
            data["Ville"], data["Date du devis"], data["Nature de l'intervention"], data["Montant HT"], data["Montant TVA"],
            data["Total dû TTC"], data["Notes"]
        ))
        conn.commit()

# Create the devis table at script execution
create_devis_table()

def create_clients_table():
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                postal_code TEXT,
                city TEXT
            )
        ''')
        conn.commit()

def insert_client(name, address, postal_code, city):
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (name, address, postal_code, city) VALUES (?, ?, ?, ?)
        ''', (name, address, postal_code, city))
        conn.commit()

def search_clients(name_prefix):
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name FROM clients WHERE name LIKE ?
        ''', (name_prefix + '%',))
        results = cursor.fetchall()
    return [result[0] for result in results]

def get_client_info(name):
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT address, postal_code, city FROM clients WHERE name = ?
        ''', (name,))
        result = cursor.fetchone()
    return result

def delete_duplicate_clients():
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM clients
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM clients
                GROUP BY name
            )
        ''')
        conn.commit()

# Create the clients table at script execution
create_clients_table()

# Requesters table functions
def create_requesters_table():
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requesters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        conn.commit()

def insert_requester(name):
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requesters (name) VALUES (?)
        ''', (name,))
        conn.commit()

def search_requesters(name_prefix):
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT name FROM requesters WHERE name LIKE ?
        ''', (name_prefix + '%',))
        results = cursor.fetchall()
    return [result[0] for result in results]

def get_requester_info(name):
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name FROM requesters WHERE name = ?
        ''', (name,))
        result = cursor.fetchone()
    return result

# Create the requesters table at script execution
create_requesters_table()
