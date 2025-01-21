import logging
import sys
import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
from tkinter import filedialog, messagebox
from pathlib import Path
from pytubefix import YouTube  # Import ajouté ici
from src.config import Config
from src.downloader.youtube_downloader import download_and_merge, download_from_file
from src.downloader.utils import fetch_resolutions
import threading


# Configuration de logging
LOG_LEVEL = logging.INFO  # Changez en logging.DEBUG pour des logs détaillés
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
        self.geometry("600x500")

        # Ajouter le liseré bleu avec le logo et le titre
        self.create_top_banner()

        # Widgets pour téléchargement d'une seule vidéo
        self.create_single_download_widgets()

        # Widgets pour téléchargement en batch
        self.create_batch_download_widgets()

    def create_top_banner(self):
        """Créer un liseré bleu avec le logo et le titre."""
        top_frame = ctk.CTkFrame(self, height=50, fg_color="blue")
        top_frame.pack(fill="x", side="top")

        # Charger le logo YouTube
        logo_image = Image.open(Config.LOGO_PATH).resize((40, 40), Image.Resampling.LANCZOS)
        logo_image = CTkImage(logo_image)

        logo_label = ctk.CTkLabel(top_frame, image=logo_image, text="")
        logo_label.image = logo_image
        logo_label.pack(side="left", padx=10)

        # Charger la police TradeGothic
        ctk.FontManager.load_font(Config.FONT_TRADE_GOTHIC_BOLD)
        trade_gothic_font = ctk.CTkFont(family="TradeGothic", size=20)

        # Titre de l'application
        title_label = ctk.CTkLabel(
            top_frame,
            text="Ultimate GUI YouTube Downloader",
            text_color="white",
            font=trade_gothic_font,
        )
        title_label.pack(side="left", padx=10)

    def create_single_download_widgets(self):
        """Widgets pour téléchargement d'une seule vidéo."""
        self.url_label = ctk.CTkLabel(self, text="Entrez l'URL de la vidéo YouTube :")
        self.url_label.pack(pady=(10, 5))

        self.url_entry = ctk.CTkEntry(self, placeholder_text="https://www.youtube.com/watch?v=...", width=400)
        self.url_entry.pack(pady=5)

        self.fetch_button = ctk.CTkButton(
            self, text="Récupérer les résolutions", command=self.fetch_resolutions_thread
        )
        self.fetch_button.pack(pady=10)

        self.resolution_menu = ctk.CTkOptionMenu(self, values=[""], width=300)
        self.resolution_menu.pack(pady=(5, 15))

        self.download_button = ctk.CTkButton(
            self, text="Télécharger", command=self.download_thread, state="disabled"
        )
        self.download_button.pack(pady=10)

        # Barre de progression pour téléchargement unique
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Statut : Prêt", text_color="green")
        self.status_label.pack(pady=5)

    def create_batch_download_widgets(self):
        """Widgets pour téléchargement en batch."""
        batch_frame = ctk.CTkFrame(self)
        batch_frame.pack(pady=20, padx=10, fill="x")

        # Bouton pour sélectionner un fichier texte
        self.file_button = ctk.CTkButton(batch_frame, text="Sélectionner un fichier texte", command=self.select_file)
        self.file_button.pack(pady=5)

        # Menu déroulant pour choisir la résolution
        self.batch_resolution_menu = ctk.CTkOptionMenu(
            batch_frame, values=["mp4 720p", "mp4 360p"], command=self.set_batch_resolution
        )
        self.batch_resolution_menu.pack(pady=5)
        self.selected_batch_resolution = "mp4 720p"

        # Bouton pour démarrer le téléchargement en lot
        self.batch_download_button = ctk.CTkButton(
            batch_frame, text="Télécharger en batch", command=self.download_batch_thread, state="disabled"
        )
        self.batch_download_button.pack(pady=10)

        # Barre de progression pour téléchargement en lot
        self.batch_progress_bar = ctk.CTkProgressBar(self, width=400)
        self.batch_progress_bar.set(0)
        self.batch_progress_bar.pack(pady=10)

    def fetch_resolutions_thread(self):
        """Thread pour récupérer les résolutions d'une vidéo unique."""
        threading.Thread(
            target=fetch_resolutions,
            args=(self.url_entry.get(), self.resolution_menu, self.status_label),
        ).start()
        self.download_button.configure(state="normal")

    def download_thread(self):
        """Thread pour télécharger une seule vidéo."""
        try:
            # Récupérer l'URL saisie par l'utilisateur
            url = self.url_entry.get()

            # Initialiser l'objet YouTube pour récupérer le titre de la vidéo
            yt = YouTube(url)
            sanitized_title = "".join(c for c in yt.title if c.isalnum() or c in " .-_").rstrip()  # Nettoyer le titre

            # Ouvrir la boîte de dialogue avec le titre pré-rempli
            save_path = filedialog.asksaveasfilename(
                initialfile=f"{sanitized_title}.mp4",  # Utiliser le titre nettoyé
                defaultextension=".mp4",
                filetypes=[("Fichiers MP4", "*.mp4"), ("Tous les fichiers", "*.*")]
            )

            if not save_path:
                # L'utilisateur a annulé la boîte de dialogue
                self.status_label.configure(text="Téléchargement annulé.", text_color="red")
                return

            # Lancer le téléchargement dans un thread
            def task():
                try:
                    selected_option = self.resolution_menu.get()
                    output_dir = str(Path(save_path).parent)
                    custom_filename = str(Path(save_path).name)

                    download_and_merge(
                        url,
                        selected_option,
                        self.status_label,
                        self.progress_bar,
                        output_dir,
                        custom_filename
                    )
                    self.progress_bar.set(1)  # Forcer la barre de progression à 100%
                except Exception as e:
                    self.status_label.configure(text=f"Erreur : {e}", text_color="red")

            threading.Thread(target=task).start()

        except Exception as e:
            self.status_label.configure(text=f"Erreur : {e}", text_color="red")

    def select_file(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier texte."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            self.selected_file = file_path
            self.batch_download_button.configure(state="normal")
            self.status_label.configure(text=f"Fichier sélectionné : {file_path}", text_color="blue")

    def set_batch_resolution(self, resolution):
        """Définit la résolution sélectionnée pour le téléchargement en lot."""
        self.selected_batch_resolution = resolution

    def download_batch_thread(self):
        """Thread pour télécharger plusieurs vidéos depuis un fichier texte."""
        # Ouvrir une boîte de dialogue pour sélectionner un dossier
        output_dir = filedialog.askdirectory(title="Sélectionner un dossier de destination")
        if not output_dir:
            messagebox.showwarning("Avertissement", "Aucun dossier sélectionné.")
            return

        def task():
            try:
                results = download_from_file(
                    self.selected_file,  # Le fichier texte contenant les URLs
                    self.selected_batch_resolution,  # La résolution sélectionnée
                    self.status_label,  # Le label pour afficher le statut
                    self.batch_progress_bar,  # La barre de progression
                    output_dir  # Le dossier de destination
                )
                self.status_label.configure(text="Téléchargement terminé.", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"Erreur : {e}", text_color="red")

        threading.Thread(target=task).start()


# Exécuter l'application si le fichier est exécuté directement
if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
