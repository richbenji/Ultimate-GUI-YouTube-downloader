from logger_config import logger
import subprocess
from pytubefix import YouTube

def show_progress(stream, chunk, bytes_remaining, total_size, progress_bar):
    """Met à jour la barre de progression pendant le téléchargement."""
    if total_size is not None and progress_bar is not None:
        percent = (1 - bytes_remaining / total_size) * 100
        progress_bar.set(percent / 100)

# Fonction pour récupérer les résolutions disponibles
def fetch_resolutions(url, resolution_menu, bitrate_menu, status_label):
    """Récupère les résolutions disponibles pour une vidéo."""
    try:
        yt = YouTube(url, use_po_token=True)

        # Récupérer les flux vidéo adaptatifs
        video_streams = yt.streams.filter(adaptive=True, only_video=True)
        video_options = [stream.resolution for stream in video_streams if stream.resolution]
        video_options = ["None"] + sorted(set(video_options))  # Trier et éviter les doublons

        # Récupérer les flux audio adaptatifs
        audio_streams = yt.streams.filter(adaptive=True, only_audio=True)
        audio_options = [stream.abr for stream in audio_streams if stream.abr]
        audio_options = ["None"] + sorted(set(audio_options))  # Trier et éviter les doublons

        # Mise à jour des menus
        if video_options:
            resolution_menu.configure(values=video_options)
            resolution_menu.set(video_options[-1])  # Sélectionne la plus haute résolution dispo
        else:
            status_label.configure(text="Aucune résolution vidéo disponible.", text_color="red")
            logger.warning("Aucune résolution vidéo trouvée.")

        if audio_options:
            bitrate_menu.configure(values=audio_options)
            bitrate_menu.set(audio_options[-1])  # Sélectionne le bitrate audio le plus élevé
        else:
            status_label.configure(text="Aucun bitrate audio disponible.", text_color="red")
            logger.warning("Aucun bitrate audio trouvé.")

        # Affichage du statut
        if video_options or audio_options:
            status_label.configure(text="Résolutions et bitrates récupérés.", text_color="green")
            logger.info(f"Résolutions disponibles : {video_options}, Bitrates disponibles : {audio_options}")

    except Exception as e:
        error_message = f"Erreur lors de la récupération des résolutions : {e}"
        status_label.configure(text=error_message, text_color="red")
        logger.error(error_message)

def merge_audio_video(video_file, audio_file, output_file):
    """Fusionne des fichiers audio et vidéo avec FFmpeg."""
    logger.info(f"Fusion en cours : {video_file} + {audio_file} -> {output_file}")

    try:
        command = [
            "ffmpeg", "-i", video_file, "-i", audio_file,
            "-c:v", "copy", "-c:a", "aac", output_file
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logger.info(f"Fusion réussie : {output_file}")
        else:
            logger.error(f"Erreur FFmpeg : {result.stderr}")
            raise RuntimeError("Erreur lors de la fusion avec FFmpeg.")

    except FileNotFoundError:
        logger.critical("FFmpeg n'est pas installé ou introuvable.")
        raise RuntimeError("FFmpeg n'est pas installé ou introuvable dans le PATH.")


def sanitize_filename(filename):
    """Nettoie le titre pour en faire un nom de fichier valide."""
    return "".join(c for c in filename if c.isalnum() or c in " .-_").rstrip()
