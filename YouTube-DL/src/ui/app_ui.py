import logging
import os
import sys
import customtkinter as ctk
from PIL import Image
from PIL.ImageOps import expand
from customtkinter import CTkImage, CTkFont
from tkinter import filedialog, messagebox
from pathlib import Path
from pytubefix import YouTube
from config import Config
from downloader.youtube_downloader import download_and_merge, download_from_file, download_and_merge1
from downloader.utils import fetch_resolutions, fetch_video_resolutions, fetch_audio_bitrates
import threading

# Configuration de logging
LOG_LEVEL = logging.INFO
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("youtube_downloader.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurations de la fenêtre principale
        self.title("Ultimate GUI YouTube Downloader")
        self.geometry("900x500")  # Agrandir légèrement pour plus d'espace

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
        title_label = ctk.CTkLabel(
            title_frame,
            text="Ultimate GUI YouTube Downloader",
            text_color="white",
            font=trade_gothic_font,
            padx=10,
            pady=10   # Plus d'espace autour du texte
        )
        title_label.grid(row=0, column=1, sticky="ew", pady=(10,0))

        # Ajouter le sous-titre
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="A Pytubefix GUI",
            text_color="white",
            font=CTkFont(size=20)
        )
        subtitle_label.grid(row=1, column=1, sticky="ew", padx=0, pady=(10, 10))

    def create_status(self):
        """Créer un frame pour la barre de statut et les widgets d'URL."""
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 10))

        # Configurer la grille du frame pour éviter le chevauchement
        self.status_frame.grid_columnconfigure(0, weight=1)  # Étendre les widgets horizontalement
        self.status_frame.grid_rowconfigure(0, weight=1)  # Première ligne
        self.status_frame.grid_rowconfigure(1, weight=1)  # Deuxième ligne

        # Ajouter la barre de statut en haut du frame
        self.status_label = ctk.CTkLabel(self.status_frame, text="Statut : Prêt", text_color="green")
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
        url_label = ctk.CTkLabel(parent_frame, text="Entrez l'URL de la vidéo YouTube :")
        url_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))

        # Champ d'entrée pour l'URL
        self.url_entry = ctk.CTkEntry(parent_frame,
                                 placeholder_text="https://www.youtube.com/watch?v=...",
                                 width=400)
        self.url_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Bouton pour récupérer les options vidéo et audio
        fetch_options_button = ctk.CTkButton(
            parent_frame,
            text="Récupérer Résolutions et Bitrates",
            command=self.fetch_video_and_audio_options_thread
        )
        fetch_options_button.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))

        # Labels et dropdowns pour sélectionner les résolutions
        resolution_label = ctk.CTkLabel(parent_frame, text="Video Resolution:")
        resolution_label.grid(row=2, column=0, sticky="e", padx=(0,10), pady=(10, 5))

        self.resolution_dropdown = ctk.CTkComboBox(parent_frame, values=["N/A"])
        self.resolution_dropdown.grid(row=2, column=1, sticky="w", padx=10, pady=(10, 5))

        bitrate_label = ctk.CTkLabel(parent_frame, text="Audio Bitrate:")
        bitrate_label.grid(row=3, column=0, sticky="e", padx=(0,10), pady=(5, 20))

        self.bitrate_dropdown = ctk.CTkComboBox(parent_frame, values=["N/A"])
        self.bitrate_dropdown.grid(row=3, column=1, sticky="w", padx=10, pady=(5, 20))

        self.download_button = ctk.CTkButton(parent_frame,
                                        text="Télécharger",
                                        command=self.download_video_thread,
                                        state="disabled"
                                        )
        self.download_button.grid(row=4, column=0, columnspan=2, sticky="ew", padx=100, pady=(10, 20))

    def create_batch_download_widgets(self, parent_frame):
        """Widgets pour téléchargement en batch."""
        # Frame pour le contenu
        parent_frame.columnconfigure(0, weight=1)

        # Bouton pour sélectionner un fichier texte
        self.file_button = ctk.CTkButton(parent_frame, text="Sélectionner un fichier texte", command=self.select_file)
        self.file_button.grid(row=0, column=0, sticky="ew", padx=10, pady=(20, 10))

        # Label pour sélectionner une résolution
        resolution_label = ctk.CTkLabel(parent_frame, text="Sélectionner une résolution :")
        resolution_label.grid(row=1, column=0, sticky="w", padx=10, pady=(10, 0))

        # Menu déroulant pour choisir la résolution
        self.batch_resolution_menu = ctk.CTkOptionMenu(
            parent_frame,
            values=["mp4 1080p", "mp4 720p", "mp4 360p"],
            command=self.set_batch_resolution
        )
        self.batch_resolution_menu.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.selected_batch_resolution = "mp4 720p"  # A quoi sert cette ligne ????

        # Bouton pour démarrer le téléchargement en lot
        self.batch_download_button = ctk.CTkButton(
            parent_frame,
            text="Télécharger en batch",
            command=self.download_batch_thread,
            state="disabled"
        )
        self.batch_download_button.grid(row=3, column=0, sticky="ew", padx=10, pady=(10, 20))

    def fetch_resolutions_thread(self):
        """Thread pour récupérer les résolutions d'une vidéo unique."""
        threading.Thread(
            target=fetch_resolutions,
            args=(self.url_entry.get(), self.batch_resolution_menu, self.status_label),
        ).start()

    def download_batch_thread(self):
        output_dir = filedialog.askdirectory(title="Sélectionner un dossier de destination")
        if not output_dir:
            messagebox.showwarning("Avertissement", "Aucun dossier sélectionné.")
            return

        def task():
            try:
                results = download_from_file(
                    self.selected_file, self.selected_batch_resolution, self.status_label, self.batch_progress_bar, output_dir
                )
                self.status_label.configure(text="Téléchargement terminé.", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"Erreur : {e}", text_color="red")

        threading.Thread(target=task).start()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")])
        if file_path:
            self.selected_file = file_path
            self.batch_download_button.configure(state="normal")
            self.status_label.configure(text=f"Fichier sélectionné : {file_path}", text_color="blue")

    def set_batch_resolution(self, resolution):
        self.selected_batch_resolution = resolution

    def fetch_video_and_audio_options_thread(self):
        """Thread pour récupérer les résolutions vidéo et les bitrates audio."""
        def task():
            url = self.url_entry.get()
            try:
                # Récupérer les résolutions vidéo
                yt = YouTube(url, use_po_token=True)

                # Flux vidéo (adaptatifs, uniquement vidéo)
                video_streams = yt.streams.filter(adaptive=True, only_video=True)
                video_options = [stream.resolution for stream in video_streams if stream.resolution]
                video_options = ["None"] + sorted(set(video_options))  # Trier et éviter les doublons

                # Mettre à jour le menu des résolutions
                if video_options:
                    self.resolution_dropdown.configure(values=video_options)
                    self.resolution_dropdown.set(video_options[-1])  # Résolution la plus élevée par défaut

                # Flux audio (adaptatifs, uniquement audio)
                audio_streams = yt.streams.filter(adaptive=True, only_audio=True)
                audio_options = [stream.abr for stream in audio_streams if stream.abr]
                audio_options = ["None"] + sorted(set(audio_options))  # Trier et éviter les doublons

                # Mettre à jour le menu des bitrates
                if audio_options:
                    self.bitrate_dropdown.configure(values=audio_options)
                    self.bitrate_dropdown.set(audio_options[-1])  # Bitrate le plus élevé par défaut

                # Mettre à jour le statut
                self.status_label.configure(text="Résolutions et bitrates récupérés.", text_color="green")

            except Exception as e:
                self.status_label.configure(text=f"Erreur : {e}", text_color="red")
            self.download_button.configure(state="normal")

        # Exécuter la tâche dans un thread séparé
        threading.Thread(target=task).start()

    def download_video_thread(self):
        """Lance le téléchargement en arrière-plan."""
        try:
            # Récupérer l'URL saisie par l'utilisateur
            url = self.url_entry.get()

            # Initialiser l'objet YouTube pour récupérer le titre de la vidéo
            yt = YouTube(url, use_po_token=True)
            sanitized_title = "".join(c for c in yt.title if c.isalnum() or c in " .-_").rstrip()  # Nettoyer le titre

            # Ouvrir la boîte de dialogue avec le titre pré-rempli
            save_path = filedialog.asksaveasfilename(
                initialfile=f"{sanitized_title}.mp4",  # Utiliser le titre nettoyé
                defaultextension=".mp4",
                filetypes=[("Fichiers MP4", "*.mp4"), ("Fichier MP3", "*.mp3"), ("Tous les fichiers", "*.*")]
            )

            if not save_path:
                # L'utilisateur a annulé la boîte de dialogue
                self.status_label.configure(text="Téléchargement annulé.", text_color="red")
                return

            # Extraire le dossier de destination et le nom du fichier à partir du chemin sélectionné
            output_dir = os.path.dirname(save_path)  # Récupérer le dossier choisi
            custom_filename = os.path.basename(save_path)  # Récupérer le nom du fichier

            threading.Thread(
                target=download_and_merge1,
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
            self.status_label.configure(text=f"Erreur : {e}", text_color="red")


if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
