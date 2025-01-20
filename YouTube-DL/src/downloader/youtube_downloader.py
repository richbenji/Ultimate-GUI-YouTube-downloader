import os
from pytubefix import YouTube
from src.config import Config
from src.downloader.utils import show_progress, merge_audio_video


# Fonction pour télécharger une vidéo et fusionner audio + vidéo si nécessaire
def download_and_merge(url, selected_option, status_label, progress_bar):
    """Télécharge une vidéo et fusionne audio + vidéo si nécessaire."""
    try:
        yt = YouTube(url)

        # Ajouter une méthode pour suivre la progression
        total_size = yt.streams.get_highest_resolution().filesize
        yt.register_on_progress_callback(
            lambda stream, chunk, bytes_remaining: show_progress(
                stream, chunk, bytes_remaining, total_size, progress_bar
            )
        )

        format_selected, resolution_selected = selected_option.split()

        # Rechercher le flux correspondant
        selected_stream = yt.streams.filter(mime_type=f"video/{format_selected.lower()}", res=resolution_selected).first()

        if selected_stream and selected_stream.is_progressive:
            # Téléchargement d'un flux progressif
            status_label.configure(text="Téléchargement du flux progressif...")
            selected_stream.download(filename="output.mp4")
            status_label.configure(text="Téléchargement terminé. Fichier final : output.mp4", text_color="green")
        else:
            # Téléchargement séparé de la vidéo et de l'audio
            status_label.configure(text="Téléchargement séparé de la vidéo et de l'audio...")

            video_stream = yt.streams.filter(mime_type=f"video/{format_selected.lower()}", res=resolution_selected).first()
            video_file = "video_only.mp4"
            video_stream.download(filename=video_file)

            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_file = "audio_only.mp3"
            audio_stream.download(filename=audio_file)

            # Fusionner avec FFmpeg
            status_label.configure(text="Fusion des fichiers audio et vidéo...")
            merge_audio_video(video_file, audio_file, "output.mp4")

            # Supprimer les fichiers temporaires
            os.remove(video_file)
            os.remove(audio_file)
            status_label.configure(text="Téléchargement et fusion terminés. Fichier final : output.mp4", text_color="green")

    except Exception as e:
        status_label.configure(text=f"Erreur : {e}", text_color="red")


# Classe principale pour gérer les téléchargements
class YouTubeDownloader:
    def __init__(self, output_dir=Config.DOWNLOADS_DIR):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_stream_by_resolution(self, yt, resolution):
        """Récupère un flux vidéo spécifique par résolution."""
        return yt.streams.filter(file_extension="mp4", res=resolution, progressive=True).first()

    def download_video(self, video_url, resolution):
        """Télécharge une vidéo dans une résolution spécifique."""
        try:
            yt = YouTube(video_url)

            # Ajouter une méthode pour suivre la progression
            total_size = yt.streams.get_highest_resolution().filesize
            yt.register_on_progress_callback(
                lambda stream, chunk, bytes_remaining: show_progress(
                    stream, chunk, bytes_remaining, total_size, None  # Pas de barre de progression ici
                )
            )

            stream = self.get_stream_by_resolution(yt, resolution)
            if stream:
                print(f"Téléchargement de {yt.title} en {resolution}...")
                stream.download(output_path=self.output_dir)
                return f"Téléchargé : {yt.title} ({resolution})"
            else:
                return f"Format {resolution} non disponible pour {yt.title}."
        except Exception as e:
            return f"Erreur avec {video_url} : {str(e)}"

    def download_from_file(self, file_path, resolution):
        """Télécharge des vidéos à partir d'un fichier texte."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier introuvable : {file_path}")

        results = []
        with open(file_path, "r") as f:
            urls = [line.strip() for line in f if line.strip()]

        for url in urls:
            result = self.download_video(url, resolution)
            results.append(result)
            print(result)

        return results
