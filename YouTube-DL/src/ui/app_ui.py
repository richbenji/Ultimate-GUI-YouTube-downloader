import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
from tkinter import filedialog
from src.config import Config
from src.downloader.youtube_downloader import download_and_merge, YouTubeDownloader
from src.downloader.utils import fetch_resolutions
import threading


class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurations de la fenêtre principale
        self.title("Ultimate GUI YouTube Downloader")
        self.geometry("600x500")

        # Initialiser le downloader
        self.downloader = YouTubeDownloader(output_dir="downloads/")

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
        def task():
            download_and_merge(
                self.url_entry.get(),
                self.resolution_menu.get(),
                self.status_label,
                self.progress_bar
            )
            self.progress_bar.set(1)  # Forcer la barre de progression à 100% à la fin

        threading.Thread(target=task).start()

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
        threading.Thread(
            target=self.start_batch_download
        ).start()

    def start_batch_download(self):
        """Lance le téléchargement en batch."""
        try:
            results = self.downloader.download_from_file(
                self.selected_file, self.selected_batch_resolution.split()[1]
            )
            for i, result in enumerate(results):
                self.batch_progress_bar.set((i + 1) / len(results))
                self.status_label.configure(text=result, text_color="green" if "Téléchargé" in result else "red")
        except Exception as e:
            self.status_label.configure(text=f"Erreur : {e}", text_color="red")


# Exécuter l'application si le fichier est exécuté directement
if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
