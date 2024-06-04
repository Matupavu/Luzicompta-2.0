# invoice.py est un fichier qui contient le code pour transformer un devis en facture. Il contient une fonction create_invoice qui est appelée dans le fichier main.py pour transformer un devis en facture.

from tkinter import filedialog, messagebox
from fpdf import FPDF
from utils import load_quotation

def create_invoice_from_data(data=None):
    if data is None:
        data = load_quotation()
    
    if not data:
        messagebox.showerror("Erreur", "Aucun devis trouvé pour générer la facture.")
        return

    default_filename = f"Facture_{data['Numéro de devis']}.pdf"
    save_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        initialfile=default_filename,
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    
    if save_path:
        pdf = FPDF()
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
        pdf.cell(0, 10, f"Montant HT: {data['Montant HT']}", ln=True)
        pdf.cell(0, 10, f"Montant TVA: {data['Montant TVA']}", ln=True)
        pdf.cell(0, 10, f"Total dû TTC: {data['Total dû TTC']}", ln=True)

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
