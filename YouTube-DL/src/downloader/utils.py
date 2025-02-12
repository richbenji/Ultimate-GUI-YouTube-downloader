import shutil
import time
import subprocess
from logger_config import logger
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.exceptions import RegexMatchError, VideoUnavailable
from ui.translations import texts


def show_progress(stream, chunk, bytes_remaining, total_size, progress_bar):
    """Met à jour la barre de progression pendant le téléchargement."""
    if total_size is not None and progress_bar is not None:
        percent = (1 - bytes_remaining / total_size)
        progress_bar.set(percent)

# Fonction pour récupérer les résolutions disponibles
def fetch_resolutions(url, resolution_menu, bitrate_menu, status_label, progress_bar):
    """Récupère les résolutions disponibles pour une vidéo."""
    try:
        progress_bar.set(0)  # Réinitialisation de la barre de progression

        status_label.configure(text=texts["fetching_resolutions"], text_color="green")

        time.sleep(0.2)  # Pause courte pour rendre la progression visible
        progress_bar.set(0.1)  # Début du processus

        try:
            yt = YouTube(url, on_progress_callback=on_progress)
        # Détection des URL invalides
        except RegexMatchError:
            error_message = texts["error_invalid_url"].format(url=url)
            status_label.configure(text=error_message, text_color="red")
            logger.error(error_message)
            return
        except VideoUnavailable:
            # Détection des vidéos supprimées / bloquées
            error_message = texts["error_video_unavailable"].format(url=url)
            status_label.configure(text=error_message, text_color="red")
            logger.warning(error_message)
            return

        progress_bar.set(0.25)  # Progression : récupération des flux vidéo

        # Récupérer les flux vidéo adaptatifs
        video_streams = yt.streams.filter(adaptive=True, only_video=True)
        video_options = [stream.resolution for stream in video_streams if stream.resolution]
        video_options = ["None"] + sorted(set(video_options))  # Trier et éviter les doublons

        progress_bar.set(0.5)  # Progression : récupération des flux audio

        # Récupérer les flux audio adaptatifs
        audio_streams = yt.streams.filter(adaptive=True, only_audio=True)
        audio_options = [stream.abr for stream in audio_streams if stream.abr]
        audio_options = ["None"] + sorted(set(audio_options))  # Trier et éviter les doublons

        progress_bar.set(0.75)  # Progression : mise à jour des menus

        # Mise à jour des menus
        if video_options:
            resolution_menu.configure(values=video_options)
            resolution_menu.set(video_options[-1])  # Sélectionne la plus haute résolution dispo
        else:
            error_message = texts["error_no_video_available"].format(title=yt.title)
            status_label.configure(text=error_message, text_color="red")
            logger.warning(error_message)

        if audio_options:
            bitrate_menu.configure(values=audio_options)
            bitrate_menu.set(audio_options[-1])  # Sélectionne le bitrate audio le plus élevé
        else:
            error_message = texts["error_no_audio_available"].format(title=yt.title)
            status_label.configure(text=error_message, text_color="red")
            logger.warning(error_message)

        time.sleep(0.3)  # Pause courte pour voir la dernière étape
        progress_bar.set(1.0)  # Fin du processus

        # Affichage du statut
        if video_options or audio_options:
            status_label.configure(text=texts["fetching_completed"], text_color="green")
            logger.info(f"{texts['fetching_completed']}: {video_options}, {audio_options}")

    except Exception as e:
        error_message = f"{texts['error_fetching_resolutions']} {e}"
        status_label.configure(text=error_message, text_color="red")
        logger.error(error_message)

def merge_audio_video(video_file, audio_file, output_file, progress_bar):
    """Fusionne des fichiers audio et vidéo avec FFmpeg."""

    # Vérifier si FFmpeg est installé
    if not shutil.which("ffmpeg"):
        logger.critical(texts["FFmpeg_not_found"])
        raise RuntimeError(texts["FFmpeg_not_found"])

    logger.info(f"{texts['merging_files']} : {video_file} + {audio_file} -> {output_file}")

    try:
        command = [
            "ffmpeg", "-i", video_file, "-i", audio_file,
            "-c:v", "copy", "-c:a", "aac", output_file
        ]

        # subprocess.Popen() permet d'exécuter une commande en arrière-plan et de suivre sa progression.
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Suivre la barre de progression
        progress = 50  # On commence la fusion à 50% (car le téléchargement est terminé)
        while process.poll() is None:  # Tant que FFmpeg tourne
            progress += 1  # Augmente progressivement
            if progress > 99:
                progress = 99  # Ne dépasse pas 99% tant que la fusion n'est pas finie
            progress_bar.set(progress / 100)  # Mise à jour de la barre
            time.sleep(0.3)  # Petite pause pour éviter une mise à jour trop rapide

        # Vérifier si la fusion a réussi
        if process.returncode == 0:
            progress_bar.set(1)  # Mettre la barre à 100% à la fin
            logger.info(f"{texts['merge_successful']} : {output_file}")
        else:
            logger.error(f"{texts['error_merge_ffmpeg']} : {process.stderr}")
            raise RuntimeError(texts['error_merge_ffmpeg'])

    except FileNotFoundError:
        logger.critical(texts['FFmpeg_not_found'])
        raise RuntimeError(texts['FFmpeg_not_found'])


def sanitize_filename(filename):
    """Nettoie le titre pour en faire un nom de fichier valide."""
    return "".join(c for c in filename if c.isalnum() or c in " .-_").rstrip()
