import customtkinter as ctk
from pytubefix import YouTube
from pytubefix.cli import on_progress
import threading

# Fonction pour télécharger une vidéo YouTube
def download_video(url, progress_bar, status_label):
    try:
        status_label.configure(text="Téléchargement en cours...")

        def progress_callback(stream, chunk, bytes_remaining):
            total_size = stream.filesize
            bytes_downloaded = total_size - bytes_remaining
            percentage = (bytes_downloaded / total_size) * 100
            progress_bar.set(percentage / 100)  # Mettre à jour la barre de progression

        yt = YouTube(url, on_progress_callback=progress_callback)
        ys = yt.streams.get_highest_resolution()
        ys.download()

        status_label.configure(text=f"Téléchargement terminé : {yt.title}")
    except Exception as e:
        status_label.configure(text=f"Erreur : {str(e)}")

# Interface utilisateur principale
def main():
    # Initialiser l'application CustomTkinter
    ctk.set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Téléchargeur YouTube")
    app.geometry("500x300")

    # Zone pour entrer l'URL
    url_label = ctk.CTkLabel(app, text="Entrez l'URL de la vidéo YouTube :")
    url_label.pack(pady=10)

    url_entry = ctk.CTkEntry(app, width=400)
    url_entry.pack(pady=10)

    # Barre de progression
    progress_bar = ctk.CTkProgressBar(app, width=400)
    progress_bar.set(0)
    progress_bar.pack(pady=10)

    # Label pour le statut
    status_label = ctk.CTkLabel(app, text="")
    status_label.pack(pady=10)

    # Bouton pour lancer le téléchargement
    def start_download():
        url = url_entry.get()
        if url:
            threading.Thread(target=download_video, args=(url, progress_bar, status_label)).start()
        else:
            status_label.configure(text="Veuillez entrer une URL valide.")

    download_button = ctk.CTkButton(app, text="Télécharger", command=start_download)
    download_button.pack(pady=20)

    # Lancer l'application
    app.mainloop()

if __name__ == "__main__":
    main()
