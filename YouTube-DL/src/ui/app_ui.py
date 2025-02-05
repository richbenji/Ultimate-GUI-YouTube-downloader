import os
import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage, CTkFont
from tkinter import filedialog, messagebox
from pytubefix import YouTube
from config import Config
from ui.translations import get_current_language, set_current_language, translations, texts
from downloader.youtube_downloader import download_from_file, download_and_merge
from downloader.utils import fetch_resolutions, sanitize_filename
import threading


class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Stocker la langue courante et son dictionnaire de traductions
        #self.language = get_current_language()
        #self.texts = translations[self.language]

        # Configurations de la fenêtre principale
        self.title(texts["title"])  # Titre de la fenêtre
        self.geometry("900x500")  # Taille de la fenêtre

        # Couleurs de l'interface
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configurer la grille de la fenêtre principale
        self.grid_columnconfigure(0, weight=1)  # Colonne gauche
        self.grid_columnconfigure(1, weight=1)  # Colonne droite
        self.grid_rowconfigure(2, weight=1)  # Ligne pour les frames principales

        # Ajouter le frame pour le titre et le logo
        self.create_header_frame()

        # Ajouter un frame pour la barre de statut
        self.create_status()

        # Ajouter les frames côte à côte
        self.create_main_frames()

    def create_header_frame(self):
        """Créer un frame pour le titre et le logo."""
        title_frame = ctk.CTkFrame(self)
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10))

        # Configurer la grille pour centrer le titre et sous-titre
        title_frame.columnconfigure(0, weight=0)  # Colonne vide à gauche
        title_frame.columnconfigure(1, weight=1)  # Colonne centrale pour centrer le texte
        title_frame.columnconfigure(2, weight=0)  # Colonne pour le logo

        # Ajouter le sélecteur de langue en haut à gauche
        self.language_menu = ctk.CTkComboBox(
            title_frame,
            values=["Français", "English", "Español", "Deutsch", "Italiano"],
            command=self.change_language
        )
        self.language_menu.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.language_menu.set(get_current_language())  # Langue par défaut

        # Charger le logo
        logo_image = Image.open(Config.LOGO_PATH)
        logo_ctk_image = CTkImage(logo_image, size=(50,50))

        logo_label = ctk.CTkLabel(title_frame, image=logo_ctk_image, text="")
        logo_label.image = logo_ctk_image
        logo_label.grid(row=0, column=2, rowspan=2, sticky="e", padx=10, pady=10)

        # Charger la police TradeGothic
        ctk.FontManager.load_font(Config.FONT_TRADE_GOTHIC_BOLD)
        trade_gothic_font = ctk.CTkFont(family="TradeGothic", size=28)

        # Ajouter le titre
        self.title_label = ctk.CTkLabel(
            title_frame,
            text=texts["title"],
            text_color="white",
            font=trade_gothic_font,
            padx=10,
            pady=10
        )
        self.title_label.grid(row=0, column=1, sticky="ew", pady=(10,0))

        # Ajouter le sous-titre
        self.subtitle_label = ctk.CTkLabel(
            title_frame,
            text=texts["subtitle"],
            text_color="white",
            font=CTkFont(size=20)
        )
        self.subtitle_label.grid(row=1, column=1, sticky="ew", padx=0, pady=(10, 10))

    def create_status(self):
        """Créer un frame pour la barre de statut et les widgets d'URL."""
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 10))

        # Configurer la grille du frame pour éviter le chevauchement
        self.status_frame.grid_columnconfigure(0, weight=1)  # Étendre les widgets horizontalement
        self.status_frame.grid_rowconfigure(0, weight=1)  # Première ligne
        self.status_frame.grid_rowconfigure(1, weight=1)  # Deuxième ligne

        # Ajouter la barre de statut en haut du frame
        self.status_label = ctk.CTkLabel(self.status_frame,
                                         text=texts["status_ready"],
                                         text_color="green")
        self.status_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        # Barre de progression pour téléchargement en lot
        self.batch_progress_bar = ctk.CTkProgressBar(self.status_frame, width=400)
        self.batch_progress_bar.set(0)
        self.batch_progress_bar.grid(row=1, column=0, sticky="ew", padx=(50,50), pady=(10, 20))

    def create_main_frames(self):
        """Créer les frames pour les téléchargements côte à côte."""
        # Frame principale pour les deux sections
        url_frame = ctk.CTkFrame(self)
        url_frame.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=(10,20))

        batch_frame = ctk.CTkFrame(self)
        batch_frame.grid(row=2, column=1, sticky="nsew", padx=(10, 20), pady=(10,20))

        # Configurer les colonnes pour que les frames occupent l'espace
        self.grid_columnconfigure(0, weight=1)  # Colonne gauche
        self.grid_columnconfigure(1, weight=1)  # Colonne droite

        # Ajouter les widgets spécifiques à chaque frame
        self.create_url_frame(url_frame)
        self.create_batch_download_widgets(batch_frame)

    def create_url_frame(self, parent_frame):
        # Frame pour le contenu
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.columnconfigure(1, weight=1)

        # Label pour l'URL
        self.url_label = ctk.CTkLabel(parent_frame, text=texts["enter_url"])
        self.url_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))

        # Champ d'entrée pour l'URL
        self.url_entry = ctk.CTkEntry(parent_frame,
                                 placeholder_text="https://www.youtube.com/watch?v=...",
                                 width=400)
        self.url_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Bouton pour récupérer les options vidéo et audio
        self.fetch_options_button = ctk.CTkButton(
            parent_frame,
            text=texts["fetching_res_bit"],
            command=self.fetch_video_and_audio_options_thread
        )
        self.fetch_options_button.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))

        # Labels et dropdowns pour sélectionner les résolutions
        self.resolution_label = ctk.CTkLabel(parent_frame, text=texts["video_resolution"])
        self.resolution_label.grid(row=2, column=0, sticky="e", padx=(0,10), pady=(10, 5))

        self.resolution_dropdown = ctk.CTkComboBox(parent_frame, values=["N/A"])
        self.resolution_dropdown.grid(row=2, column=1, sticky="w", padx=10, pady=(10, 5))

        self.bitrate_label = ctk.CTkLabel(parent_frame, text=texts["audio_bitrate"])
        self.bitrate_label.grid(row=3, column=0, sticky="e", padx=(0,10), pady=(5, 20))

        self.bitrate_dropdown = ctk.CTkComboBox(parent_frame, values=["N/A"])
        self.bitrate_dropdown.grid(row=3, column=1, sticky="w", padx=10, pady=(5, 20))

        self.download_button = ctk.CTkButton(parent_frame,
                                        text=texts["download_button"],
                                        command=self.download_video_thread,
                                        state="disabled"
                                        )
        self.download_button.grid(row=4, column=0, columnspan=2, sticky="ew", padx=100, pady=(10, 20))

    def create_batch_download_widgets(self, parent_frame):
        """Widgets pour téléchargement en batch."""
        # Frame pour le contenu
        parent_frame.columnconfigure(0, weight=1)

        # Bouton pour sélectionner un fichier texte
        self.file_button = ctk.CTkButton(parent_frame,
                                         text=texts["select_file"],
                                         command=self.select_file)
        self.file_button.grid(row=0, column=0, sticky="ew", padx=10, pady=(20, 10))

        # Label pour sélectionner une résolution
        self.resolution_label = ctk.CTkLabel(parent_frame,
                                        text=texts["select_resolution"])
        self.resolution_label.grid(row=1, column=0, sticky="w", padx=10, pady=(10, 0))

        # Menu déroulant pour choisir la résolution
        self.batch_resolution_menu = ctk.CTkOptionMenu(
            parent_frame,
            values=["mp4 1080p", "mp4 720p", "mp4 360p", "audio only"],
            command=self.set_batch_resolution
        )
        self.batch_resolution_menu.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.selected_batch_resolution = "mp4 720p"  #TODO Comment ça marche ????

        # Bouton pour démarrer le téléchargement en lot
        self.batch_download_button = ctk.CTkButton(
            parent_frame,
            text=texts["batch_download"],
            command=self.download_batch_thread,
            state="disabled"
        )
        self.batch_download_button.grid(row=3, column=0, sticky="ew", padx=10, pady=(10, 20))

    def fetch_resolutions_thread(self):
        """Thread pour récupérer les résolutions d'une vidéo unique."""
        print("fetch_resolutions_thread: Début")  # Ajoute ce print pour voir si la fonction est appelée

        threading.Thread(
            target=fetch_resolutions,
            args=(self.url_entry.get(), self.batch_resolution_menu, self.status_label, self.batch_progress_bar),
        ).start()

    def download_batch_thread(self):

        # Remettre la barre de progression à zéro avant de commencer
        self.batch_progress_bar.set(0)

        output_dir = filedialog.askdirectory(title=texts["select_folder"])

        if not output_dir:
            messagebox.showwarning(
                texts["error"],
                texts["no_folder_selected"]
            )
            return

        # Récupérer la résolution sélectionnée
        selected_option = self.batch_resolution_menu.get()  # Ex: "mp4 720p", "mp4 360p", "audio only"

        # Déterminer si on télécharge une vidéo ou juste de l'audio
        if selected_option == "audio only":
            selected_video_res = "None"
        else:
            selected_video_res = selected_option.split()[1]  # Récupérer "720p", "360p", etc.

        selected_audio_bitrate = "best"  # Toujours prendre le meilleur bitrate audio

        def task():
            try:
                download_from_file(
                    self.selected_file,
                    selected_video_res,
                    selected_audio_bitrate,
                    self.status_label,
                    self.batch_progress_bar,
                    output_dir
                )

            except Exception as e:
                self.after(0, lambda: self.status_label.configure(
                    text=f"{texts['error']} {e}",
                    text_color="red")
                           )

        # Lancer `task` dans un thread
        threading.Thread(target=task, daemon=True).start()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")])
        if file_path:
            self.selected_file = file_path
            self.batch_download_button.configure(state="normal")
            self.status_label.configure(text=f"{texts["selected_file"]} : {file_path}",
                                        text_color="blue")

        # Remettre la barre de progression à zéro avant de commencer
        self.batch_progress_bar.set(0)

    def set_batch_resolution(self, resolution):  ### TODO : A QUOI SERT CETTE FONCTION ?
        self.selected_batch_resolution = resolution

    def fetch_video_and_audio_options_thread(self):
        """Thread pour récupérer les résolutions vidéo et les bitrates audio."""

        # Remettre la barre de progression à zéro avant de commencer
        self.batch_progress_bar.set(0)

        def task():
            url = self.url_entry.get()
            try:
                fetch_resolutions(url, self.resolution_dropdown, self.bitrate_dropdown, self.status_label, self.batch_progress_bar)
            except Exception as e:
                error_message = f"{texts['error']} : {e}"  # Capture l'erreur ici
                self.after(0, lambda: self.status_label.configure(text=error_message, text_color="red"))

        self.after(0, lambda: self.download_button.configure(state="normal"))

        # Exécuter la tâche dans un thread séparé
        threading.Thread(target=task, daemon=True).start()

    def download_video_thread(self):
        """Lance le téléchargement en arrière-plan."""
        try:
            # Remettre la barre de progression à zéro avant de commencer
            self.batch_progress_bar.set(0)

            # Récupérer l'URL saisie par l'utilisateur
            url = self.url_entry.get()

            # Initialiser l'objet YouTube pour récupérer le titre de la vidéo
            yt = YouTube(url, use_po_token=True)
            sanitized_title = sanitize_filename(yt.title)   # Nettoyer le titre

            # Déterminer l'extension selon le choix de l'utilisateur
            selected_video_res = self.resolution_dropdown.get()
            selected_audio_bitrate = self.bitrate_dropdown.get()

            if selected_audio_bitrate == "None":
                extension = ".mp4"  # Cas 1 : Vidéo seule
            elif selected_video_res == "None":
                extension = ".mp3"  # Cas 2 : Audio seul
            else:
                extension = ".mp4"  # Cas 3 : Fusion Audio + Vidéo en MP4

            # Ouvrir la boîte de dialogue avec le titre pré-rempli
            save_path = filedialog.asksaveasfilename(
                initialfile=f"{sanitized_title}{extension}",  # Utiliser le titre nettoyé
                defaultextension=extension,
                filetypes=[("Fichiers MP4", "*.mp4"), ("Fichier MP3", "*.mp3"), ("Tous les fichiers", "*.*")]
            )

            if not save_path:
                # L'utilisateur a annulé la boîte de dialogue
                self.status_label.configure(text=texts["download_cancelled"],
                                            text_color="red")
                return

            # Extraire le dossier de destination et le nom du fichier à partir du chemin sélectionné
            output_dir = os.path.dirname(save_path)  # Récupérer le dossier choisi
            custom_filename = os.path.basename(save_path)  # Récupérer le nom du fichier

            threading.Thread(
                target=download_and_merge,
                args=(
                    self.url_entry.get(),
                    self.resolution_dropdown.get(),  # Résolution choisie
                    self.bitrate_dropdown.get(),  # Bitrate choisi
                    self.status_label,
                    self.batch_progress_bar,
                    output_dir,  # Utiliser le dossier sélectionné
                    custom_filename  # Utiliser le nom de fichier sélectionné
                )
            ).start()
        except Exception as e:
            self.status_label.configure(text=f"{texts['error']} : {e}", text_color="red")

    def change_language(self, selected_language):
        """Change la langue de l'interface."""
        set_current_language(selected_language)  # Met à jour la langue globale
        texts = translations[selected_language]

        # Mettre à jour les labels et boutons fixes
        self.title_label.configure(text=texts["title"])
        self.subtitle_label.configure(text=texts["subtitle"])
        self.status_label.configure(text=texts["status_ready"], text_color="green")
        self.fetch_options_button.configure(text=texts["fetching_res_bit"])
       # self.log_button.configure(text=texts["open_log"])
        self.file_button.configure(text=texts["select_file"])
        self.batch_download_button.configure(text=texts["batch_download"])
        self.download_button.configure(text=texts["download"])
        self.resolution_label.configure(text=texts["video_resolution"])
        self.bitrate_label.configure(text=texts["audio_bitrate"])

        # Mettre à jour les placeholders et valeurs par défaut
        self.url_label.configure(text=texts["enter_url"])
        self.language_menu.set(selected_language)

        # Mettre à jour les menus déroulants
        self.resolution_dropdown.configure(values=[texts["select_resolution"]])
        self.bitrate_dropdown.configure(values=[texts["audio_bitrate"]])


if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
