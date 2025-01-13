import customtkinter as ctk
from pytubefix import YouTube
from PIL import Image
import threading
import subprocess
import os


# Fonction pour récupérer les résolutions disponibles
def fetch_resolutions(url, resolution_menu, status_label):
    try:
        yt = YouTube(url)
        streams = yt.streams.filter(adaptive=True)  # Supprime le filtre MP4 uniquement
        options = [f"{stream.mime_type.split('/')[-1].upper()} {stream.resolution}" for stream in streams if stream.resolution]
        options = list(set(options))  # Éviter les doublons
        options.sort()  # Trier par ordre croissant

        if options:
            # Mettre à jour le menu déroulant
            resolution_menu.configure(values=options)
            resolution_menu.set(options[-1])  # Par défaut, sélectionne la dernière option (résolution la plus élevée)
            status_label.configure(text="Résolutions récupérées.")
        else:
            status_label.configure(text="Aucune résolution disponible.")
    except Exception as e:
        status_label.configure(text=f"Erreur : {e}")


# Fonction principale pour télécharger et fusionner
def download_and_merge(url, selected_option, status_label, progress_bar):
    try:
        yt = YouTube(url)

        # Extraire le format et la résolution de l'option sélectionnée
        format_selected, resolution_selected = selected_option.split()

        # Rechercher le flux correspondant
        selected_stream = yt.streams.filter(mime_type=f"video/{format_selected.lower()}", res=resolution_selected).first()

        if selected_stream and selected_stream.is_progressive:
            # Si un flux progressif est disponible, téléchargez-le directement
            status_label.configure(text="Téléchargement du flux progressif...")
            selected_stream.download(filename="output.mp4")
            status_label.configure(text="Téléchargement terminé. Fichier final prêt : output.mp4")
        else:
            # Sinon, télécharger vidéo-only et audio-only
            status_label.configure(text="Téléchargement séparé de la vidéo et de l'audio...")

            # Télécharger vidéo-only
            video_stream = yt.streams.filter(mime_type=f"video/{format_selected.lower()}", res=resolution_selected).first()
            video_file = "video_only.mp4"
            video_stream.download(filename=video_file)

            # Télécharger audio-only
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_file = "audio_only.mp3"
            audio_stream.download(filename=audio_file)

            # Fusionner avec FFmpeg
            status_label.configure(text="Fusion des fichiers audio et vidéo...")
            merge_audio_video(video_file, audio_file, "output.mp4")

            # Supprimer les fichiers originaux
            os.remove(video_file)
            os.remove(audio_file)
            status_label.configure(text="Téléchargement et fusion terminés. Fichier final : output.mp4")

    except Exception as e:
        status_label.configure(text=f"Erreur : {e}")


# Fonction pour fusionner audio et vidéo avec FFmpeg
def merge_audio_video(video_file, audio_file, output_file):
    command = [
        "ffmpeg",
        "-i", video_file,
        "-i", audio_file,
        "-c:v", "copy",
        "-c:a", "aac",
        output_file
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# Interface graphique principale
def main():
    # Initialisation de CustomTkinter
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Téléchargeur YouTube")
    app.geometry("700x500")

    # Liseré supérieur avec logo et titre
    header_frame = ctk.CTkFrame(app, fg_color="blue")
    header_frame.pack(fill="x", pady=0, padx=0)

    logo_image = ctk.CTkImage(Image.open("assets/Youtube_logo.png"), size=(40, 40))
    logo_label = ctk.CTkLabel(header_frame, image=logo_image, text="", width=50)
    logo_label.pack(side="left", padx=10, pady=5)

    header_label = ctk.CTkLabel(header_frame, text="Ultimate GUI YouTube Downloader", text_color="white", font=("Arial", 20, "bold"))
    header_label.pack(side="left", padx=10)

    # Zone pour entrer l'URL
    url_frame = ctk.CTkFrame(app)
    url_frame.pack(pady=10, padx=10, fill="x")

    url_label = ctk.CTkLabel(url_frame, text="Entrez l'URL de la vidéo YouTube :")
    url_label.pack(side="left", padx=10)

    url_entry = ctk.CTkEntry(url_frame, width=400)
    url_entry.pack(side="left", padx=10)

    # Bouton pour récupérer les résolutions
    def fetch_resolutions_thread():
        threading.Thread(target=fetch_resolutions, args=(url_entry.get(), resolution_menu, status_label)).start()

    fetch_button = ctk.CTkButton(url_frame, text="Récupérer les Résolutions", command=fetch_resolutions_thread)
    fetch_button.pack(side="left", padx=10)

    # Menu déroulant pour les résolutions
    resolution_label = ctk.CTkLabel(app, text="Choisissez une résolution :")
    resolution_label.pack(pady=10)

    resolution_menu = ctk.CTkOptionMenu(app, values=[""], width=400)
    resolution_menu.pack(pady=10)

    # Barre de progression
    progress_bar = ctk.CTkProgressBar(app, width=600)
    progress_bar.set(0)
    progress_bar.pack(pady=10)

    # Label de statut
    status_label = ctk.CTkLabel(app, text="")
    status_label.pack(pady=10)

    # Bouton pour lancer le téléchargement
    def start_download():
        url = url_entry.get()
        selected_option = resolution_menu.get()
        if url and selected_option:
            threading.Thread(target=download_and_merge, args=(url, selected_option, status_label, progress_bar)).start()
        else:
            status_label.configure(text="Veuillez entrer une URL et choisir une option valide.")

    download_button = ctk.CTkButton(app, text="Télécharger et Fusionner", command=start_download)
    download_button.pack(pady=20)

    # Lancer l'application
    app.mainloop()


if __name__ == "__main__":
    main()
