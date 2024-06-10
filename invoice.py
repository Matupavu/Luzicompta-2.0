# invoice.py

import os
import json
from tkinter import filedialog, messagebox
from fpdf import FPDF
from utils import load_quotation

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Title', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_invoice_from_data(data=None):
    if data is None:
        data = load_quotation()  # Charger les données si elles ne sont pas fournies
    
    if not data:
        messagebox.showerror("Erreur", "Aucun devis trouvé pour générer la facture.")
        return

    invoices_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'invoices')
    if not os.path.exists(invoices_dir):
        os.makedirs(invoices_dir)

    json_filename = os.path.join(invoices_dir, f"{data['Numéro de facture']}.json")
    pdf_filename = f"{data['Numéro de facture']}.pdf"
    save_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        initialfile=pdf_filename,
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    
    if save_path:
        # Sauvegarder les données de la facture en JSON
        try:
            with open(json_filename, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            print(f"Fichier JSON de la facture créé avec succès : {json_filename}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création du fichier JSON: {e}")

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Ajouter le logo
        try:
            pdf.image("LUZITECHLOGO.PNG", x=10, y=8, w=33)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout du logo: {e}")

        # Titre de la facture
        pdf.set_xy(50, 10)
        pdf.set_font("Arial", size=24)
        pdf.cell(0, 10, "Facture", ln=True, align='C')

        # Informations du client
        pdf.set_font("Arial", size=12)
        pdf.ln(20)
        pdf.cell(0, 10, f"Nom du client: {data['Nom du client']}", ln=True)
        pdf.cell(0, 10, f"Nom du demandeur: {data['Nom du demandeur']}", ln=True)
        pdf.cell(0, 10, f"Adresse: {data['Adresse']}", ln=True)
        pdf.cell(0, 10, f"Code Postal: {data['Code Postal']}", ln=True)
        pdf.cell(0, 10, f"Ville: {data['Ville']}", ln=True)

        # Date de la facture
        pdf.ln(10)
        pdf.cell(0, 10, f"Date: {data['Date du devis']}", ln=True)

        # Tableau des interventions
        pdf.ln(10)
        pdf.cell(0, 10, "Tableau des Interventions", ln=True)
        table_headers = ["Description de l'intervention", "U", "Qté", "Prix HT", "Total HT", "TVA", "Total TVA", "Total TTC"]
        column_widths = [60, 10, 10, 20, 20, 10, 20, 20]

        # En-têtes du tableau
        for i, header in enumerate(table_headers):
            pdf.cell(column_widths[i], 10, header, 1, 0, 'C')
        pdf.ln()

        # Contenu du tableau
        for row in data["Tableau"]:
            for i, item in enumerate(row):
                pdf.cell(column_widths[i], 10, str(item), 1, 0, 'C')
            pdf.ln()

        # Totaux
        pdf.ln(10)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 10, f"Montant HT (en €): {data['Montant HT']}", ln=True)
        pdf.cell(0, 10, f"Montant TVA (en €): {data['Montant TVA']}", ln=True)
        pdf.cell(0, 10, f"Total dû TTC (en €): {data['Total dû TTC']}", ln=True)

        # Notes
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Notes: {data['Notes']}")

        # Mentions légales
        pdf.ln(10)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, "Mentions légales:", ln=True)
        pdf.multi_cell(0, 10, "Votre texte de mentions légales ici...")

        # Enregistrer le PDF
        try:
            pdf.output(save_path)
            print(f"PDF de facture généré avec succès : {save_path}")
            messagebox.showinfo("Succès", f"La facture a été sauvegardée avec succès à l'emplacement suivant : {save_path}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde de la facture: {e}")
    else:
        messagebox.showwarning("Annulé", "La sauvegarde de la facture a été annulée.")
