import os
from pytubefix import YouTube
from src.downloader.utils import show_progress, merge_audio_video, sanitize_filename


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
        sanitized_title = sanitize_filename(yt.title)
        final_filename = f"{sanitized_title}.{format_selected.lower()}"

        # Rechercher le flux correspondant
        selected_stream = yt.streams.filter(mime_type=f"video/{format_selected.lower()}", res=resolution_selected).first()

        if selected_stream and selected_stream.is_progressive:
            # Téléchargement d'un flux progressif
            status_label.configure(text="Téléchargement du flux progressif...")
            selected_stream.download(filename=final_filename)
            status_label.configure(
                text=f"Téléchargement terminé. Fichier final : {final_filename}",
                text_color="green"
            )
        else:
            # Téléchargement séparé de la vidéo et de l'audio
            status_label.configure(text="Téléchargement séparé de la vidéo et de l'audio...")

            video_stream = yt.streams.filter(mime_type=f"video/{format_selected.lower()}", res=resolution_selected).first()
            video_file = f"{sanitized_title}_video.mp4"
            video_stream.download(filename=video_file)

            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_file = f"{sanitized_title}_audio.mp3"
            audio_stream.download(filename=audio_file)

            # Fusionner avec FFmpeg
            status_label.configure(text="Fusion des fichiers audio et vidéo...")
            merge_audio_video(video_file, audio_file, final_filename)

            # Supprimer les fichiers temporaires
            os.remove(video_file)
            os.remove(audio_file)
            status_label.configure(
                text=f"Téléchargement et fusion terminés. Fichier final : {final_filename}",
                text_color="green"
            )

    except Exception as e:
        status_label.configure(text=f"Erreur : {e}", text_color="red")


def download_from_file(file_path, selected_option, status_label=None, progress_bar=None):
    """Télécharge des vidéos à partir d'un fichier texte en utilisant download_and_merge."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")

    results = []
    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    total_urls = len(urls)
    for index, url in enumerate(urls, start=1):
        try:
            # Mettre à jour la barre de progression
            if progress_bar:
                progress_bar.set((index - 1) / total_urls)

            # Télécharger la vidéo
            download_and_merge(url, selected_option, status_label, progress_bar)

            # Ajouter le résultat
            result = f"Téléchargement terminé pour : {url}"
        except Exception as e:
            result = f"Erreur avec {url} : {str(e)}"

        results.append(result)
        print(result)

        # Mettre à jour la barre de progression à 100% après la dernière vidéo
        if progress_bar and index == total_urls:
            progress_bar.set(1)

    return results
