from logger_config import logger
import os
from pytubefix import YouTube
from downloader.utils import show_progress, merge_audio_video, sanitize_filename


# Fonction pour télécharger une vidéo et fusionner audio + vidéo si nécessaire
def download_and_merge(url, selected_video_res, selected_audio_bitrate, status_label, progress_bar, output_dir=None,
                       custom_filename=None):
    """Télécharge une vidéo ou un fichier audio, ou les deux, selon les choix."""
    try:
        yt = YouTube(url, use_po_token=True)

        custom_filename = sanitize_filename(yt.title)
        final_filename = os.path.join(output_dir, f"{custom_filename}.mp4")

        ####################################################################
        # Cas 1 : Télécharger uniquement la vidéo si le bitrate est "None"
        ####################################################################

        if selected_audio_bitrate == "None":
            video_stream = yt.streams.filter(adaptive=True, only_video=True, resolution=selected_video_res).first()
            if not video_stream:
                error_message = f"Erreur : La vidéo '{yt.title}' n'existe pas en {selected_video_res}."
                status_label.configure(text=error_message, text_color="red")
                logger.warning(error_message)
                return

            status_label.configure(text="Téléchargement de la vidéo en cours...", text_color="blue")
            video_stream.download(output_path=output_dir, filename=f"{custom_filename}.mp4")
            status_label.configure(text="Vidéo téléchargée avec succès.", text_color="green")
            logger.info(f"Vidéo téléchargée : {custom_filename}.mp4")
            return

        ####################################################################
        # Cas 2 : Télécharger uniquement l'audio si la résolution est "None"
        ####################################################################

        if selected_video_res == "None":
            audio_stream = yt.streams.filter(adaptive=True, only_audio=True, abr=selected_audio_bitrate).first()
            if not audio_stream:
                error_message = f"Erreur : Pas d'audio disponible pour '{yt.title}' en {selected_audio_bitrate}."
                status_label.configure(text=error_message, text_color="red")
                logger.warning(error_message)
                return

            status_label.configure(text="Téléchargement de l'audio en cours...", text_color="blue")
            audio_stream.download(output_path=output_dir, filename=f"{custom_filename}.mp3")
            status_label.configure(text="Audio téléchargé avec succès.", text_color="green")
            logger.info(f"Audio téléchargé : {custom_filename}.mp3")
            return

        ####################################################################
        # Cas 3 : Télécharger et fusionner si les deux valeurs sont valides
        ####################################################################

        # Filtrer les streams vidéo et sélectionner celui avec la bonne résolution
        video_stream = yt.streams.filter(adaptive=True, only_video=True, resolution=selected_video_res).first()
        if not video_stream:
            error_message = f"Erreur : La vidéo '{yt.title}' n'existe pas en {selected_video_res}."
            status_label.configure(text=error_message, text_color="red")
            logger.warning(error_message)
            return

        # Filtrer les streams audio et sélectionner celui avec le bon bitrate
        audio_stream = yt.streams.filter(adaptive=True, only_audio=True, abr=selected_audio_bitrate).first()
        if not audio_stream:
            error_message = f"Erreur : Pas d'audio disponible pour '{yt.title}' en {selected_audio_bitrate}."
            status_label.configure(text=error_message, text_color="red")
            logger.warning(error_message)
            return

        # Télécharger la vidéo et l'audio
        video_file = f"{custom_filename}_video.mp4"
        audio_file = f"{custom_filename}_audio.mp3"

        video_stream.download(output_path=output_dir, filename=video_file)
        audio_stream.download(output_path=output_dir, filename=audio_file)

        status_label.configure(text="Téléchargement des fichiers audio et vidéo effectué", text_color="blue")
        logger.info(f"Vidéo et audio téléchargés pour fusion : {yt.title}")

        # Fusionner avec FFmpeg
        status_label.configure(
            text="Fusion de l'audio et de la vidéo...",
            text_color="blue")
        merge_audio_video(video_file, audio_file, final_filename)

        # Vérifier si la fusion a bien réussi avant de supprimer les fichiers temporaires
        if os.path.exists(final_filename):
            os.remove(video_file)
            os.remove(audio_file)
            status_label.configure(
                text=f"Téléchargement et fusion terminés : {final_filename}",
                text_color="green"
            )
            logger.info(f"Fusion terminée : {final_filename}")
        else:
            error_message = f"Erreur : La fusion de '{yt.title}' a échoué."
            status_label.configure(text=error_message, text_color="red")
            logger.error(error_message)
            return

    except Exception as e:
        error_message = f"Erreur : {e}"
        status_label.configure(text=error_message, text_color="red")
        logger.error(error_message)

def download_from_file(file_path, selected_video_res, selected_audio_bitrate, status_label, progress_bar, output_dir):
    """Télécharge plusieurs vidéos à partir d'un fichier texte."""
    if not os.path.exists(file_path):
        error_message = "Erreur : Fichier introuvable."
        status_label.configure(text=error_message, text_color="red")
        logger.error(error_message)
        return

    if not os.path.exists(output_dir):
        status_label.configure(text="Erreur : Dossier de destination invalide.", text_color="red")
        logger.error("Erreur : Dossier de destination invalide.")
        return

    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    total = len(urls)
    for i, url in enumerate(urls, start=1):
        try:
            progress_bar.set((i - 1) / total)

            yt = YouTube(url, use_po_token=True)

            # Vérifier si la vidéo est dispo en résolution demandée
            if selected_video_res != "None":
                video_stream = yt.streams.filter(adaptive=True, only_video=True, resolution=selected_video_res).first()
                if not video_stream:
                    error_message = f"Erreur : '{yt.title}' ({url}) n'existe pas en {selected_video_res}."
                    status_label.configure(text=error_message, text_color="red")
                    logger.warning(error_message)
                    continue  # Passe à la vidéo suivante

            # Récupérer le meilleur bitrate audio
            best_audio = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
            if not best_audio:
                error_message = f"Erreur : Pas d'audio disponible pour '{yt.title}' ({url})."
                status_label.configure(text=error_message, text_color="red")
                logger.warning(error_message)
                continue  # Passe à la vidéo suivante

            selected_audio_bitrate = best_audio.abr  # Ex: "128kbps", "160kbps"

            # Procéder à la fusion de l'audio et de la vidéo
            download_and_merge(url, selected_video_res, selected_audio_bitrate, status_label, progress_bar, output_dir, None)

            success_message = f"Téléchargement terminé pour : {yt.title} ({url})"
            status_label.configure(text=success_message, text_color="green")
            logger.info(success_message)

        except Exception as e:
            error_message = f"Erreur avec {url} : {str(e)}"
            status_label.configure(text=error_message, text_color="red")
            logger.error(error_message)

    progress_bar.set(1)
    logger.info("Téléchargement batch terminé.")

