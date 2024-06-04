# quotation.py est un fichier qui contient le code pour créer un devis. Il contient une classe QuotationForm qui est appelée dans le fichier main.py pour créer un devis.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, StringVar, Scrollbar, Canvas
from tkcalendar import DateEntry
from fpdf import FPDF
from utils import save_quotation, generate_devis_number, load_quotation
import csv
from invoice import create_invoice_from_data
from database import insert_client, insert_requester, search_clients, search_requesters, get_client_info, get_requester_info, delete_duplicate_clients, insert_devis

class QuotationForm(tk.Toplevel):
    def __init__(self, parent, devis_number=None):
        super().__init__(parent)
        self.title("LuziCompta - Créer un Devis")

        self.state('zoomed')
        self.configure(bg='white')
        self.geometry("+100+100")

        # Générer un nouveau numéro de devis uniquement si devis_number n'est pas spécifié
        self.devis_number = devis_number or generate_devis_number()

        try:
            self.iconbitmap("LUZITECHLOGO.ico")
        except Exception as e:
            messagebox.showerror("Erreur", f"Fichier d'icône introuvable : {e}")

        # Création d'un canvas et d'un frame avec scrollbar
        self.canvas = Canvas(self, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Ajouter le support pour la roulette de la souris
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

        form_frame = tk.Frame(self.scrollable_frame, bg='white')
        form_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(self.scrollable_frame, bg='white')
        button_frame.pack(pady=10)

        self.postal_codes = self.load_postal_codes()

        self.fields = {
            "Numéro de devis": tk.Label(form_frame, text=self.devis_number, font=("Qanelas-Semibold", 16), bg='white'),
            "Nom du client": None,
            "Nom du demandeur": None,
            "Adresse": None,
            "Code Postal": None
        }

        self.client_name_var = StringVar()
        self.client_name_var.trace("w", self.update_client_suggestions)

        self.requester_name_var = StringVar()
        self.requester_name_var.trace("w", self.update_requester_suggestions)

        light_orange_bg = '#FFFAF0'  # Arrière-plan orange clair

        row = 0
        col = 0
        for field, widget in self.fields.items():
            label = tk.Label(form_frame, text=field, font=("Qanelas-Semibold", 16), bg='white')
            label.grid(row=row, column=col * 2, pady=5, padx=5, sticky='e')
            if widget:
                widget.grid(row=row, column=col * 2 + 1, pady=5, padx=5, sticky='w')
            else:
                if field == "Nom du client":
                    entry = ttk.Combobox(form_frame, font=("Qanelas-Medium", 14), width=30, textvariable=self.client_name_var)
                elif field == "Nom du demandeur":
                    entry = ttk.Combobox(form_frame, font=("Qanelas-Medium", 14), width=30, textvariable=self.requester_name_var)
                else:
                    entry = tk.Entry(form_frame, font=("Qanelas-Medium", 14), width=30, bg=light_orange_bg)
                entry.grid(row=row, column=col * 2 + 1, pady=5, padx=5, sticky='w')
                entry.configure(background=light_orange_bg)
                if field == "Adresse":
                    entry.bind("<KeyRelease>", self.capitalize_words)
                self.fields[field] = entry

            if col == 1:
                col = 0
                row += 1
            else:
                col += 1

        self.fields["Nom du client"].bind("<KeyRelease>", self.to_uppercase)
        self.fields["Nom du client"].bind("<<ComboboxSelected>>", self.on_client_select)
        self.fields["Nom du demandeur"].bind("<KeyRelease>", self.to_uppercase)
        self.fields["Nom du demandeur"].bind("<<ComboboxSelected>>", self.on_requester_select)
        self.fields["Code Postal"].bind("<KeyRelease>", self.format_code_postal)
        self.fields["Code Postal"].bind("<KeyRelease>", self.suggest_city)

        row += 1

        self.city_listbox_frame = tk.Frame(self.scrollable_frame)
        self.city_listbox = tk.Listbox(self.city_listbox_frame, font=("Qanelas-Medium", 14), width=30, height=4)
        self.city_listbox.bind("<<ListboxSelect>>", self.on_city_select)

        self.city_scrollbar = tk.Scrollbar(self.city_listbox_frame, orient="vertical")
        self.city_scrollbar.config(command=self.city_listbox.yview)
        self.city_listbox.config(yscrollcommand=self.city_scrollbar.set)

        self.city_listbox.pack(side="left", fill="both", expand=True)
        self.city_scrollbar.pack(side="right", fill="y")

        ville_label = tk.Label(form_frame, text="Ville", font=("Qanelas-Semibold", 16), bg='white')
        ville_label.grid(row=row, column=0, pady=5, padx=5, sticky='e')
        self.ville_entry = tk.Entry(form_frame, font=("Qanelas-Medium", 14), width=30, bg=light_orange_bg)
        self.ville_entry.grid(row=row, column=1, pady=5, padx=5, sticky='w')
        self.ville_entry.bind("<KeyRelease>", self.capitalize_words)
        self.fields["Ville"] = self.ville_entry
        row += 1

        date_label = tk.Label(form_frame, text="Date du devis", font=("Qanelas-Semibold", 16), bg='white')
        date_label.grid(row=row, column=0, pady=5, padx=5, sticky='e')
        self.date_entry = DateEntry(form_frame, font=("Qanelas-Medium", 14), width=27, date_pattern='dd/MM/yyyy', bg=light_orange_bg)
        self.date_entry.grid(row=row, column=1, pady=5, padx=5, sticky='w')
        row += 1

        description_label = tk.Label(form_frame, text="Nature de l'intervention", font=("Qanelas-Semibold", 16), bg='white')
        description_label.grid(row=row, column=0, pady=5, padx=5, sticky='e')
        self.description_entry = tk.Entry(form_frame, font=("Qanelas-Medium", 14), width=50, bg=light_orange_bg)
        self.description_entry.grid(row=row, column=1, columnspan=3, pady=5, padx=5, sticky='w')
        self.description_entry.bind("<KeyRelease>", self.capitalize_first_letter)
        row += 1

        # Utilisation d'un canvas pour le tableau afin d'éviter le conflit de gestionnaires de géométrie
        self.table_canvas = Canvas(form_frame, bg='white')
        self.table_canvas.grid(row=row, column=0, columnspan=4, pady=10, padx=5, sticky='nsew')

        self.table_scrollbar = Scrollbar(form_frame, orient="vertical", command=self.table_canvas.yview)
        self.table_scrollbar.grid(row=row, column=4, pady=10, sticky='ns')

        self.table_frame = tk.Frame(self.table_canvas, bg='white')
        self.table_frame.bind(
            "<Configure>",
            lambda e: self.table_canvas.configure(
                scrollregion=self.table_canvas.bbox("all")
            )
        )

        self.table_canvas.create_window((0, 0), window=self.table_frame, anchor="nw", width=form_frame.winfo_width() - 50)
        self.table_canvas.configure(yscrollcommand=self.table_scrollbar.set)

        self.table_headers = ["Description de l'intervention", "U", "Qté", "Prix HT", "Total HT", "TVA", "Total TVA", "Total TTC"]
        self.column_widths = [30, 3, 4, 6, 6, 3, 8, 10]
        self.entries = []

        for i, (header, width) in enumerate(zip(self.table_headers, self.column_widths)):
            label = tk.Label(self.table_frame, text=header, font=("Qanelas-Semibold", 14), bg='white', width=width)
            label.grid(row=0, column=i, padx=5, pady=5, sticky='w')

        if not devis_number:
            self.add_table_row(self.table_frame)

        row += 1
        montant_ht_label = tk.Label(form_frame, text="Montant HT", font=("Qanelas-Semibold", 16), bg='white')
        montant_ht_label.grid(row=row, column=0, pady=5, padx=5, sticky='e')
        self.montant_ht_entry = tk.Entry(form_frame, font=("Qanelas-Medium", 14), width=30, state='readonly', bg=light_orange_bg)
        self.montant_ht_entry.grid(row=row, column=1, pady=5, padx=5, sticky='w')

        row += 1
        montant_tva_label = tk.Label(form_frame, text="Montant TVA", font=("Qanelas-Semibold", 16), bg='white')
        montant_tva_label.grid(row=row, column=0, pady=5, padx=5, sticky='e')
        self.montant_tva_entry = tk.Entry(form_frame, font=("Qanelas-Medium", 14), width=30, state='readonly', bg=light_orange_bg)
        self.montant_tva_entry.grid(row=row, column=1, pady=5, padx=5, sticky='w')

        row += 1
        total_du_ttc_label = tk.Label(form_frame, text="Total dû TTC", font=("Qanelas-Semibold", 16), bg='white')
        total_du_ttc_label.grid(row=row, column=0, pady=5, padx=5, sticky='e')
        self.total_du_ttc_entry = tk.Entry(form_frame, font=("Qanelas-Medium", 14), width=30, state='readonly', bg=light_orange_bg)
        self.total_du_ttc_entry.grid(row=row, column=1, pady=5, padx=5, sticky='w')

        notes_label = tk.Label(form_frame, text="Notes", font=("Qanelas-Semibold", 16), bg='white')
        notes_label.grid(row=row + 1, column=0, pady=5, padx=5, sticky='ne')
        self.notes_text = tk.Text(form_frame, font=("Qanelas-Medium", 14), width=50, height=3, bg=light_orange_bg)
        self.notes_text.grid(row=row + 1, column=1, columnspan=3, pady=5, padx=5, sticky='w')
        self.notes_text.bind("<KeyRelease>", self.capitalize_first_letter_text)  # Majuscule pour le champ Notes

        self.save_button = tk.Button(button_frame, text="Créer le devis", command=self.save_quotation, bg='white', fg='#006400', font=("Qanelas-Medium", 16))
        self.save_button.pack(side=tk.LEFT, padx=10)

        self.cancel_button = tk.Button(button_frame, text="Annuler", command=self.cancel, bg='white', fg='#FF0000', font=("Qanelas-Medium", 16))
        self.cancel_button.pack(side=tk.LEFT, padx=10)

        self.convert_button = tk.Button(button_frame, text="Convertir en Facture Maintenant", command=self.convert_to_invoice_now, bg='white', fg='#800080', font=("Qanelas-Medium", 16))
        self.convert_button.pack(side=tk.LEFT, padx=10)

        button_frame.pack(pady=20)

        self.fields["Nom du client"].focus_set()  # Placer le curseur dans le champ "Nom du client"

        if devis_number:
            self.load_quotation_data(devis_number)

    def _on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def move_window(self, event):
        self.geometry(f'+{event.x_root}+{event.y_root}')

    def to_uppercase(self, event):
        widget = event.widget
        current_text = widget.get()
        widget.delete(0, tk.END)
        widget.insert(0, current_text.upper())

    def capitalize_first_letter(self, event):
        widget = event.widget
        current_text = widget.get()
        if current_text and current_text[0].islower():
            widget.delete(0, tk.END)
            widget.insert(0, current_text.capitalize())

    def capitalize_first_letter_text(self, event):
        widget = event.widget
        current_text = widget.get("1.0", tk.END).strip()
        if current_text and current_text[0].islower():
            widget.delete("1.0", tk.END)
            widget.insert("1.0", current_text.capitalize())

    def capitalize_words(self, event):
        widget = event.widget
        current_text = widget.get()
        if event.keysym in ['space', 'Return']:
            words = current_text.split(' ')
            capitalized_words = [word.capitalize() for word in words]
            new_text = ' '.join(capitalized_words)
            widget.delete(0, tk.END)
            widget.insert(0, new_text)

    def format_code_postal(self, event):
        widget = event.widget
        current_text = widget.get()
        formatted_text = ''.join(filter(str.isdigit, current_text))
        if len(formatted_text) > 5:
            formatted_text = formatted_text[:5]
        if len(formatted_text) > 2:
            formatted_text = formatted_text[:2] + ' ' + formatted_text[2:]
        widget.delete(0, tk.END)
        widget.insert(0, formatted_text)

    def suggest_city(self, event):
        code_postal = self.fields["Code Postal"].get().replace(" ", "")
        if code_postal in self.postal_codes:
            villes = self.postal_codes[code_postal]
            if len(villes) == 1:
                self.ville_entry.delete(0, tk.END)
                self.ville_entry.insert(0, villes[0])
                self.city_listbox_frame.place_forget()
            else:
                self.city_listbox.delete(0, tk.END)
                for ville in villes:
                    self.city_listbox.insert(tk.END, ville)
                self.city_listbox_frame.place(x=self.ville_entry.winfo_x(), y=self.ville_entry.winfo_y() + self.ville_entry.winfo_height())
                self.city_listbox_frame.lift()
        else:
            self.city_listbox_frame.place_forget()

    def on_city_select(self, event):
        if not self.city_listbox.curselection():
            return
        selected_city = self.city_listbox.get(self.city_listbox.curselection())
        self.ville_entry.delete(0, tk.END)
        self.ville_entry.insert(0, selected_city)
        self.city_listbox_frame.place_forget()

    def load_postal_codes(self):
        postal_codes = {}
        try:
            with open('postal_codes.csv', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                next(reader)
                for row in reader:
                    if len(row) == 2:
                        code_postal, ville = row
                        code_postal = code_postal.strip()
                        ville = ville.strip()
                        if code_postal in postal_codes:
                            postal_codes[code_postal].append(ville)
                        else:
                            postal_codes[code_postal] = [ville]
        except FileNotFoundError:
            messagebox.showerror("Erreur", "Le fichier postal_codes.csv est introuvable.")
        return postal_codes

    def add_table_row(self, table_frame, row_data=None):
        row_index = len(self.entries) + 1
        row_entries = []
        for i, (header, width) in enumerate(zip(self.table_headers, self.column_widths)):
            if header == "U":
                entry = ttk.Combobox(table_frame, values=["U", "F", "Ens", "H"], font=("Qanelas-Medium", 12), width=width, background='#FFFAF0')
                if row_data:
                    entry.set(row_data[i])  # Set to row_data if provided
                else:
                    entry.set("U")
            elif header == "TVA":
                entry = ttk.Combobox(table_frame, values=["0%", "10%", "20%"], font=("Qanelas-Medium", 12), width=width, background='#FFFAF0')
                if row_data:
                    entry.set(row_data[i])  # Set to row_data if provided
                else:
                    entry.set("20%")
                entry.bind("<FocusOut>", self.calculate_row)
                entry.bind("<Return>", self.calculate_row_and_move_next)
            elif header in ["Prix HT", "Total HT", "Total TVA", "Total TTC"]:
                entry = tk.Entry(table_frame, font=("Qanelas-Medium", 12), width=width, bg='#FFFAF0')
                if row_data:
                    entry.insert(0, row_data[i])  # Insert row_data if provided
                if header != "Prix HT":
                    entry.configure(state='readonly')
                entry.bind("<FocusOut>", self.calculate_row)
                entry.bind("<Return>", self.calculate_row_and_move_next)
            else:
                entry = tk.Entry(table_frame, font=("Qanelas-Medium", 12), width=width, bg='#FFFAF0')
                if row_data:
                    entry.insert(0, row_data[i])  # Insert row_data if provided
                entry.bind("<KeyRelease>", self.capitalize_first_letter)
                entry.bind("<FocusOut>", self.check_last_row_filled)
                entry.bind("<Return>", self.calculate_row_and_move_next)
            entry.grid(row=row_index, column=i, padx=5, pady=5)
            row_entries.append(entry)
        self.entries.append(row_entries)

    def calculate_row(self, event):
        widget = event.widget
        row_index = int(widget.grid_info()['row']) - 1
        row_entries = self.entries[row_index]

        try:
            qty = float(row_entries[2].get())
            price_ht = float(row_entries[3].get())
        except ValueError:
            qty = price_ht = 0

        total_ht = qty * price_ht
        row_entries[4].configure(state='normal')
        row_entries[4].delete(0, tk.END)
        row_entries[4].insert(0, f"{total_ht:.2f}")
        row_entries[4].configure(state='readonly')

        try:
            tva_rate = row_entries[5].get().strip('%')
            tva_rate = float(tva_rate) / 100
        except ValueError:
            tva_rate = 0

        total_tva = total_ht * tva_rate
        row_entries[6].configure(state='normal')
        row_entries[6].delete(0, tk.END)
        row_entries[6].insert(0, f"{total_tva:.2f}")
        row_entries[6].configure(state='readonly')

        total_ttc = total_ht + total_tva
        row_entries[7].configure(state='normal')
        row_entries[7].delete(0, tk.END)
        row_entries[7].insert(0, f"{total_ttc:.2f}")
        row_entries[7].configure(state='readonly')

        self.check_last_row_filled(event)
        self.update_totals()

    def calculate_row_and_move_next(self, event):
        self.calculate_row(event)
        self.move_to_next_description(event)

    def move_to_next_description(self, event):
        row_index = int(event.widget.grid_info()['row'])
        next_row_index = row_index + 1
        if next_row_index < len(self.entries):
            next_description = self.entries[next_row_index][0]
            next_description.focus()
        return "break"

    def focus_next_window(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def check_last_row_filled(self, event):
        last_row = self.entries[-1]
        if all(entry.get() for entry in last_row):
            self.add_table_row(event.widget.master)

    def update_totals(self):
        total_ht = sum(float(row[4].get() or 0) for row in self.entries if row[4].get())
        total_tva = sum(float(row[6].get() or 0) for row in self.entries if row[6].get())
        total_ttc = sum(float(row[7].get() or 0) for row in self.entries if row[7].get())

        self.montant_ht_entry.configure(state='normal')
        self.montant_ht_entry.delete(0, tk.END)
        self.montant_ht_entry.insert(0, f"{total_ht:.2f}")
        self.montant_ht_entry.configure(state='readonly')

        self.montant_tva_entry.configure(state='normal')
        self.montant_tva_entry.delete(0, tk.END)
        self.montant_tva_entry.insert(0, f"{total_tva:.2f}")
        self.montant_tva_entry.configure(state='readonly')

        self.total_du_ttc_entry.configure(state='normal')
        self.total_du_ttc_entry.delete(0, tk.END)
        self.total_du_ttc_entry.insert(0, f"{total_ttc:.2f}")
        self.total_du_ttc_entry.configure(state='readonly')

    def validate_entries(self):
        errors = []

        required_fields = ["Nom du client", "Nom du demandeur", "Adresse", "Code Postal", "Ville"]
        for field in required_fields:
            entry = self.fields.get(field)
            if entry and isinstance(entry, (tk.Entry, ttk.Combobox)) and not entry.get().strip():
                errors.append(f"Le champ '{field}' est obligatoire.")
        
        code_postal = self.fields["Code Postal"].get().replace(" ", "")
        if not code_postal.isdigit() or len(code_postal) != 5:
            errors.append("Le code postal doit être composé de 5 chiffres.")

        return errors

    def save_quotation(self):
        errors = self.validate_entries()
        if errors:
            messagebox.showerror("Erreur de validation", "\n".join(errors))
            return

        data = {field: (entry.get() if isinstance(entry, (tk.Entry, ttk.Combobox)) else entry.cget("text")) for field, entry in self.fields.items()}
        data["Numéro de devis"] = self.devis_number
        data["Ville"] = self.ville_entry.get()
        data["Date du devis"] = self.date_entry.get()
        data["Nature de l'intervention"] = self.description_entry.get()
        data["Tableau"] = [[entry.get() for entry in row] for row in self.entries if any(entry.get() for entry in row)]
        data["Montant HT"] = self.montant_ht_entry.get()
        data["Montant TVA"] = self.montant_tva_entry.get()
        data["Total dû TTC"] = self.total_du_ttc_entry.get()
        data["Notes"] = self.notes_text.get("1.0", tk.END).strip()  # Ajout des notes

        print(f"Sauvegarde des données du devis : {data}")

        # Éviter les doublons dans les clients
        existing_client = get_client_info(data["Nom du client"])
        if not existing_client:
            insert_client(data["Nom du client"], data["Adresse"], data["Code Postal"], data["Ville"])

        delete_duplicate_clients()  # Supprimer les doublons avant de sauvegarder

        # Sauvegarder le demandeur indépendamment
        existing_requester = get_requester_info(data["Nom du demandeur"])
        if not existing_requester:
            insert_requester(data["Nom du demandeur"])

        # Sauvegarder le devis
        save_quotation(data)
        insert_devis(data)  # Enregistrer les données du devis dans la base de données

        self.generate_pdf(data)
        self.close_form()

    def generate_pdf(self, data):
        default_filename = f"{data['Numéro de devis']}.pdf"
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_filename,
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if save_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            pdf.image("LUZITECHLOGO.PNG", x=10, y=8, w=33)

            pdf.set_xy(50, 10)
            pdf.set_font("Arial", size=24)
            pdf.cell(0, 10, "Devis", ln=True, align='C')

            pdf.set_font("Arial", size=12)
            pdf.ln(20)
            pdf.cell(0, 10, f"Numéro de devis: {data['Numéro de devis']}", ln=True)
            pdf.cell(0, 10, f"Nom du client: {data['Nom du client']}", ln=True)
            pdf.cell(0, 10, f"Nom du demandeur: {data['Nom du demandeur']}", ln=True)
            pdf.cell(0, 10, f"Adresse: {data['Adresse']}", ln=True)
            pdf.cell(0, 10, f"Code Postal: {data['Code Postal']}", ln=True)
            pdf.cell(0, 10, f"Ville: {data['Ville']}", ln=True)

            pdf.ln(10)
            pdf.cell(0, 10, f"Date du devis: {data['Date du devis']}", ln=True)

            pdf.ln(10)
            pdf.cell(0, 10, "Tableau des Interventions", ln=True)
            table_headers = ["Description de l'intervention", "U", "Qté", "Prix HT", "Total HT", "TVA", "Total TVA", "Total TTC"]
            column_widths = [60, 10, 10, 20, 20, 10, 20, 20]

            for i, header in enumerate(table_headers):
                pdf.cell(column_widths[i], 10, header, 1, 0, 'C')
            pdf.ln()

            for row in data["Tableau"]:
                for i, item in enumerate(row):
                    pdf.cell(column_widths[i], 10, str(item), 1, 0, 'C')
                pdf.ln()

            pdf.ln(10)
            pdf.cell(0, 10, f"Montant HT: {data['Montant HT']}", ln=True)
            pdf.cell(0, 10, f"Montant TVA: {data['Montant TVA']}", ln=True)
            pdf.cell(0, 10, f"Total dû TTC: {data['Total dû TTC']}", ln=True)

            pdf.ln(10)
            pdf.multi_cell(0, 10, f"Notes: {data['Notes']}")

            pdf.ln(10)
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 10, "Mentions légales:", ln=True)
            pdf.multi_cell(0, 10, "Votre texte de mentions légales ici...")

            pdf.output(save_path)
            print(f"PDF de devis généré avec succès : {save_path}")
            messagebox.showinfo("Succès", f"Le devis a été sauvegardé avec succès à l'emplacement suivant : {save_path}")
        else:
            messagebox.showwarning("Annulé", "La sauvegarde du devis a été annulée.")

    def close_form(self):
        self.destroy()
        self.master.deiconify()

    def cancel(self):
        self.close_form()
    
    def convert_to_invoice_now(self):
        data = {field: entry.get() for field, entry in self.fields.items()}
        data["Numéro de devis"] = self.devis_number
        data["Ville"] = self.ville_entry.get()
        data["Date du devis"] = self.date_entry.get()
        data["Nature de l'intervention"] = self.description_entry.get()
        data["Tableau"] = [[entry.get() for entry in row] for row in self.entries if any(entry.get() for entry in row)]
        data["Montant HT"] = self.montant_ht_entry.get()
        data["Montant TVA"] = self.montant_tva_entry.get()
        data["Total dû TTC"] = self.total_du_ttc_entry.get()
        data["Notes"] = self.notes_text.get("1.0", tk.END).strip()
        create_invoice_from_data(data)
        messagebox.showinfo("Succès", "Les données du devis ont été converties en facture.")
        self.close_form()

    def update_client_suggestions(self, *args):
        if len(self.client_name_var.get()) >= 3:
            suggestions = search_clients(self.client_name_var.get())
            self.fields["Nom du client"]["values"] = suggestions
            if suggestions:
                self.fields["Nom du client"].event_generate('<Down>')  # Ouvrir la liste déroulante

    def update_requester_suggestions(self, *args):
        if len(self.requester_name_var.get()) >= 3:
            suggestions = search_requesters(self.requester_name_var.get())
            self.fields["Nom du demandeur"]["values"] = suggestions
            if suggestions:
                self.fields["Nom du demandeur"].event_generate('<Down>')  # Ouvrir la liste déroulante

    def on_client_select(self, event):
        selected_client = self.client_name_var.get()
        client_info = get_client_info(selected_client)
        if client_info:
            self.fields["Nom du client"].delete(0, tk.END)
            self.fields["Nom du client"].insert(0, selected_client)
            self.fields["Adresse"].delete(0, tk.END)
            self.fields["Adresse"].insert(0, client_info[0])
            self.fields["Code Postal"].delete(0, tk.END)
            self.fields["Code Postal"].insert(0, client_info[1])
            self.ville_entry.delete(0, tk.END)
            self.ville_entry.insert(0, client_info[2])

    def on_requester_select(self, event):
        selected_requester = self.requester_name_var.get()
        requester_info = get_requester_info(selected_requester)
        if requester_info:
            self.fields["Nom du demandeur"].delete(0, tk.END)
            self.fields["Nom du demandeur"].insert(0, selected_requester)

    def load_quotation_data(self, devis_number):
        data = load_quotation(devis_number)
        if data:
            self.fields["Nom du client"].delete(0, tk.END)
            self.fields["Nom du client"].insert(0, data["Nom du client"])
            self.fields["Nom du demandeur"].delete(0, tk.END)
            self.fields["Nom du demandeur"].insert(0, data["Nom du demandeur"])
            self.fields["Adresse"].delete(0, tk.END)
            self.fields["Adresse"].insert(0, data["Adresse"])
            self.fields["Code Postal"].delete(0, tk.END)
            self.fields["Code Postal"].insert(0, data["Code Postal"])
            self.ville_entry.delete(0, tk.END)
            self.ville_entry.insert(0, data["Ville"])
            self.date_entry.set_date(data["Date du devis"])
            self.description_entry.delete(0, tk.END)
            self.description_entry.insert(0, data["Nature de l'intervention"])
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert(tk.END, data["Notes"])
            for row_data in data["Tableau"]:
                self.add_table_row(self.table_frame, row_data=row_data)
                self.calculate_row_on_load(row_data)  # Calculer les lignes lors du chargement des données
            self.update_totals()

    def calculate_row_on_load(self, row_data):
        row_index = len(self.entries) - 1
        row_entries = self.entries[row_index]

        try:
            qty = float(row_data[2])
            price_ht = float(row_data[3])
        except ValueError:
            qty = price_ht = 0

        total_ht = qty * price_ht
        row_entries[4].configure(state='normal')
        row_entries[4].delete(0, tk.END)
        row_entries[4].insert(0, f"{total_ht:.2f}")
        row_entries[4].configure(state='readonly')

        try:
            tva_rate = row_data[5].strip('%')
            tva_rate = float(tva_rate) / 100
        except ValueError:
            tva_rate = 0

        total_tva = total_ht * tva_rate
        row_entries[6].configure(state='normal')
        row_entries[6].delete(0, tk.END)
        row_entries[6].insert(0, f"{total_tva:.2f}")
        row_entries[6].configure(state='readonly')

        total_ttc = total_ht + total_tva
        row_entries[7].configure(state='normal')
        row_entries[7].delete(0, tk.END)
        row_entries[7].insert(0, f"{total_ttc:.2f}")
        row_entries[7].configure(state='readonly')

if __name__ == "__main__":
    root = tk.Tk()
    app = QuotationForm(root)
    root.mainloop()
