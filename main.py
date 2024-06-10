# main.py est le fichier principal de l'application LuziCompta. Il contient le code pour la fenêtre principale de l'application.

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from quotation import QuotationForm
from utils import load_quotation

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LuziCompta v2.0")
        
        self.iconbitmap("LUZITECHLOGO.ico")
        self.geometry('600x550')  # Définir la taille initiale de la fenêtre
        self.configure(bg='white')

        self.logo_image = Image.open("LUZITECHLOGO.PNG")
        self.logo_image = self.logo_image.resize((self.logo_image.width // 3, self.logo_image.height // 3), Image.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo, bg='white')
        self.logo_label.pack(pady=10)
        
        self.title_label = tk.Label(self, text="LuziCompta", font=("Qanelas-Bold", 32), bg='white', fg='black')
        self.title_label.pack(pady=20)
        
        self.subtitle_label = tk.Label(self, text="Gestion Devis et Facturation", font=("Qanelas-SemiBold", 20), bg='white', fg='black')
        self.subtitle_label.pack(pady=10)
        
        self.create_quotation_button = tk.Button(self, text="Créer un Devis", command=self.open_quotation_form, bg='white', fg='#FF4500', font=("Qanelas-Medium", 16))
        self.create_quotation_button.pack(pady=10)

        search_frame = tk.Frame(self, bg='white')
        search_frame.pack(pady=10)

        search_label = tk.Label(search_frame, text="DE", font=("Qanelas-Semibold", 16), bg='white')
        search_label.pack(side=tk.LEFT, padx=10)

        self.search_entry = tk.Entry(search_frame, font=("Qanelas-Medium", 14), width=20)
        self.search_entry.pack(side=tk.LEFT, padx=10)

        self.search_button = tk.Button(search_frame, text="Rechercher un Devis", command=self.search_quotation, bg='white', fg='#00008B', font=("Qanelas-Medium", 16))
        self.search_button.pack(side=tk.LEFT, padx=10)

    def open_quotation_form(self):
        self.withdraw()
        QuotationForm(self)

    def search_quotation(self):
        devis_number = self.search_entry.get().strip()
        if devis_number:
            devis_number = f"DE{devis_number}"
            print(f"Recherche du devis : {devis_number}")
            data = load_quotation(devis_number=devis_number)
            if data and data.get("Numéro de devis") == devis_number:
                self.withdraw()
                QuotationForm(self, devis_number=devis_number)
            else:
                messagebox.showerror("Erreur", "Devis introuvable.")
        else:
            messagebox.showerror("Erreur", "Veuillez entrer un numéro de devis valide.")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
