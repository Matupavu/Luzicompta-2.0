#pdf_generator.py

import os
from fpdf import FPDF
import json

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Add a Unicode font (DejaVuSans)
        self.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)
        self.add_font("DejaVu", "I", "DejaVuSans-Oblique.ttf", uni=True)

    def header(self):
        # Add the logo (increase the size)
        try:
            self.image("LUZITECHLOGO.PNG", x=10, y=8, w=70)  # Augmenter la largeur du logo
        except Exception as e:
            print(f"Erreur lors de l'ajout du logo : {e}")

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

def generate_custom_pdf(data, save_path):
    pdf = PDF()
    pdf.add_page()
    
    # Add company information (positioned below the logo)
    pdf.set_font("DejaVu", 'B', size=11)
    pdf.set_xy(10, 60)  # Positionner les informations sous le logo
    pdf.cell(0, 5, "LUZITECH", ln=True, align='L')
    
    pdf.set_font("DejaVu", size=11)
    pdf.set_xy(10, 65)
    pdf.cell(0, 5, "23 Rue le Brecq", ln=True, align='L')
    pdf.set_xy(10, 70)
    pdf.cell(0, 5, "45290 NOGENT SUR VERNISSON", ln=True, align='L')
    pdf.set_xy(10, 75)
    pdf.cell(0, 5, "06 50 65 01 00", ln=True, align='L')
    pdf.set_xy(10, 80)
    pdf.cell(0, 5, "luzitech45@gmail.com", ln=True, align='L')
    
    # Add Devis title with number
    pdf.set_font("DejaVu", 'B', size=16)
    pdf.set_xy(120, 20)
    pdf.cell(0, 10, f"Devis N° {data['Numéro de devis']}", ln=True, align='L')
    
    # Add Devis information
    pdf.set_font("DejaVu", 'B', size=11)
    pdf.set_xy(120, 40)
    pdf.cell(30, 10, "Date :", ln=False, align='L')
    pdf.set_font("DejaVu", size=11)
    pdf.cell(0, 10, f"{data['Date du devis']}", ln=True, align='L')
    
    # Add Client information
    pdf.set_xy(120, 60)
    pdf.set_font("DejaVu", 'B', size=11)
    pdf.cell(0, 10, "CLIENT:", ln=True, align='L')
    
    pdf.set_font("DejaVu", size=11)
    pdf.set_xy(120, 70)
    pdf.cell(0, 5, f"{data['Nom du client']}", ln=True, align='L')
    pdf.set_xy(120, 75)
    pdf.cell(0, 5, f"{data['Adresse']}", ln=True, align='L')
    pdf.set_xy(120, 80)
    pdf.cell(0, 5, f"{data['Code Postal']} {data['Ville']}", ln=True, align='L')

    # Add Demandeur information
    pdf.set_xy(10, 90)
    pdf.set_font("DejaVu", 'B', size=11)
    pdf.cell(40, 10, "Demandeur :", ln=False, align='L')
    pdf.set_font("DejaVu", size=11)
    pdf.cell(0, 10, f"{data['Nom du demandeur']}", ln=True, align='L')

    # Add Nature de l'intervention
    pdf.set_xy(10, 100)
    pdf.set_font("DejaVu", 'B', size=11)
    pdf.cell(60, 10, "Nature de l'intervention :", ln=False, align='L')
    pdf.set_font("DejaVu", size=11)
    pdf.multi_cell(190, 10, data["Nature de l'intervention"])  # Spécifier la largeur pour éviter l'erreur

    # Add the table header
    pdf.set_xy(10, 120)
    table_headers = [
        "Description de l'intervention", "U", "Qté", "Prix HT", "Total HT", "TVA", "Total TVA", "Total TTC"
    ]
    column_widths = [80, 10, 10, 20, 20, 10, 20, 20]  # Ajustez les largeurs de colonnes ici

    pdf.set_font("DejaVu", 'B', size=10)  # Titres en gras
    for i, header in enumerate(table_headers):
        pdf.cell(column_widths[i], 10, header, 1, 0, 'C')
    pdf.ln()

    # Add the table rows
    pdf.set_font("DejaVu", size=10)  # Texte du tableau
    for row in data["Tableau"]:
        if row[0]:  # Vérifier si la première colonne n'est pas vide
            for i, item in enumerate(row):
                pdf.cell(column_widths[i], 10, str(item), 1, 0, 'C')
            pdf.ln()

    # Add the totals in a table format
    total_table_start_y = pdf.get_y() + 10
    total_table_column_widths = [40, 30]  # Largeurs des colonnes du tableau des totaux
    total_labels = ["Montant HT (en €)", "Montant TVA (en €)", "Total dû TTC (en €)"]
    total_values = [data['Montant HT'], data['Montant TVA'], data['Total dû TTC']]

    pdf.set_xy(120, total_table_start_y)
    for label, value in zip(total_labels, total_values):
        pdf.set_font("DejaVu", 'B', size=10)  # Titres en gras
        pdf.cell(total_table_column_widths[0], 10, label, 1, 0, 'L')
        pdf.set_font("DejaVu", size=10)
        pdf.cell(total_table_column_widths[1], 10, value, 1, 1, 'R')
        total_table_start_y += 10

    # Add signatures
    signature_start_y = total_table_start_y + 20
    pdf.set_xy(10, signature_start_y)
    signature_column_widths = [65, 65, 65]  # Largeurs des colonnes du tableau des signatures
    pdf.set_font("DejaVu", 'B', size=10)
    pdf.multi_cell(signature_column_widths[0], 40, "Nom client :", border=1, align='L')
    pdf.set_xy(10 + signature_column_widths[0], signature_start_y)  # Positionner la deuxième colonne
    pdf.multi_cell(signature_column_widths[1], 40, "Cachet de l'entreprise :", border=1, align='L')
    pdf.set_xy(10 + signature_column_widths[0] + signature_column_widths[1], signature_start_y)  # Positionner la troisième colonne
    pdf.multi_cell(signature_column_widths[2], 40, "Signature :", border=1, align='L')

    # Add terms
    pdf.set_font("DejaVu", 'I', size=9)
    pdf.set_xy(10, signature_start_y + 50)
    pdf.multi_cell(0, 5, "Délai d'intervention : A convenir suivant planning\nDurée de validité du devis : 1 mois\nConditions de paiement : A réception de facture", align='C')

    pdf.output(save_path)
    print(f"PDF de devis généré avec succès : {save_path}")

# Modification pour sauvegarder uniquement dans le dossier devis
def save_quotation(data):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        devis_dir = os.path.join(current_dir, 'devis')
        if not os.path.exists(devis_dir):
            os.makedirs(devis_dir)
        filename = os.path.join(devis_dir, f'quotation_{data["Numéro de devis"]}.json')
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Devis sauvegardé avec succès: {filename}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du devis: {e}")
