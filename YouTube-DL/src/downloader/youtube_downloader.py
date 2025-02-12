from logger_config import logger
import os
from pytubefix import YouTube
from pytubefix.cli import on_progress
from downloader.utils import merge_audio_video, sanitize_filename, show_progress
from ui.translations import texts



# Fonction pour télécharger une vidéo et fusionner audio + vidéo si nécessaire
def download_and_merge(url, selected_video_res, selected_audio_bitrate, status_label, progress_bar, output_dir=None,
                       custom_filename=None):
    """Télécharge une vidéo ou un fichier audio, ou les deux, selon les choix."""
    try:
        yt = YouTube(url, on_progress_callback=on_progress)

        status_label.configure(text=texts["downloading_video_audio"].format(title=yt.title), text_color="blue")
        logger.info(texts["downloading_video_audio_log"].format(title=yt.title))

        custom_filename = sanitize_filename(yt.title)
        final_filename = os.path.join(output_dir, f"{custom_filename}.mp4")

        ####################################################################
        # Cas 1 : Télécharger uniquement la vidéo si le bitrate est "None"
        ####################################################################

        if selected_audio_bitrate == "None":
            # Sélectionner le flux vidéo selon la résolution choisie
            video_stream = yt.streams.filter(adaptive=True, only_video=True, resolution=selected_video_res).first()
            # Vérifier que la vidéo est bien trouvée
            if not video_stream:
                error_message = texts["error_no_video"].format(title=yt.title, res=selected_video_res)
                status_label.configure(text=error_message, text_color="red")
                logger.warning(error_message)
                return

            # Récupérer la vraie taille du fichier vidéo sélectionné
            video_size = video_stream.filesize
            # Lancer la mise à jour de la barre de progression
            yt.register_on_progress_callback(lambda stream, chunk, bytes_remaining:
                                             show_progress(stream, chunk, bytes_remaining, video_size, progress_bar))

            status_label.configure(text=texts["downloading_video"], text_color="blue")
            video_stream.download(output_path=output_dir, filename=f"{custom_filename}.mp4")
            status_label.configure(text=texts["video_downloaded"].format(title=yt.title), text_color="green")
            logger.info(texts["video_downloaded_log"].format(filename=custom_filename))
            return

        ####################################################################
        # Cas 2 : Télécharger uniquement l'audio si la résolution est "None"
        ####################################################################

        if selected_video_res == "None":
            audio_stream = yt.streams.filter(adaptive=True, only_audio=True, abr=selected_audio_bitrate).first()
            if not audio_stream:
                error_message = texts["error_no_audio"].format(title=yt.title, bitrate=selected_audio_bitrate)
                status_label.configure(text=error_message, text_color="red")
                logger.warning(error_message)
                return

            # Récupérer la vraie taille du fichier vidéo sélectionné
            audio_size = audio_stream.filesize
            # Lancer la mise à jour de la barre de progression
            yt.register_on_progress_callback(lambda stream, chunk, bytes_remaining:
                                             show_progress(stream, chunk, bytes_remaining, audio_size, progress_bar))

            status_label.configure(text=texts["downloading_audio"], text_color="blue")
            audio_stream.download(output_path=output_dir, filename=f"{custom_filename}.mp3")
            status_label.configure(text=texts["audio_downloaded"].format(title=yt.title), text_color="green")
            logger.info(texts["audio_downloaded_log"].format(filename=custom_filename))
            return

        ####################################################################
        # Cas 3 : Télécharger et fusionner si les deux valeurs sont valides
        ####################################################################

        # Lancer la mise à jour de la barre de progression
        yt.register_on_progress_callback(lambda stream, chunk, bytes_remaining:
                                         progress_bar.set(
                                             0.5 * (1 - bytes_remaining / stream.filesize)
                                         )
                                         )  # Arrêter à 50%

        # Filtrer les streams vidéo et sélectionner celui avec la bonne résolution
        video_stream = yt.streams.filter(adaptive=True, only_video=True, resolution=selected_video_res).first()
        if not video_stream:
            error_message = texts["error_no_video"].format(title=yt.title, res=selected_video_res)
            status_label.configure(text=error_message, text_color="red")
            logger.warning(error_message)
            return

        # Filtrer les streams audio et sélectionner celui avec le bon bitrate
        audio_stream = yt.streams.filter(adaptive=True, only_audio=True, abr=selected_audio_bitrate).first()
        if not audio_stream:
            error_message = texts["error_no_audio"].format(title=yt.title, bitrate=selected_audio_bitrate)
            status_label.configure(text=error_message, text_color="red")
            logger.warning(error_message)
            return

        # Télécharger la vidéo et l'audio
        video_file = f"{custom_filename}_video.mp4"
        audio_file = f"{custom_filename}_audio.mp3"

        video_stream.download(output_path=output_dir, filename=video_file)
        audio_stream.download(output_path=output_dir, filename=audio_file)

        status_label.configure(text=texts["download_video_audio_completed"], text_color="blue")
        logger.info(texts["download_video_audio_completed_log"].format(title=yt.title))

        # Fusionner avec FFmpeg
        status_label.configure(text=texts["merging"], text_color="blue")

        # Mise à jour de la barre de téléchargement
        progress_bar.set(50 / 100)

        merge_audio_video(video_file, audio_file, final_filename, progress_bar)

        # Vérifier si la fusion a bien réussi avant de supprimer les fichiers temporaires
        if os.path.exists(final_filename):
            os.remove(video_file)
            os.remove(audio_file)
            status_label.configure(text=texts["temp_files_removed"].format(filename=final_filename), text_color="green")
            logger.info(texts["temp_files_removed_log"].format(filename=final_filename))
        else:
            error_message = texts["error_merge"].format(title=yt.title)
            status_label.configure(text=error_message, text_color="red")
            logger.error(error_message)
            return

        success_message = texts["download_completed"].format(title=yt.title, url=url)
        status_label.configure(text=success_message, text_color="green")
        logger.info(success_message)

    except Exception as e:
        error_message = texts["error_generic"].format(error=str(e))
        status_label.configure(text=error_message, text_color="red")
        logger.error(error_message)

def download_from_file(file_path, selected_video_res, selected_audio_bitrate, status_label, progress_bar, output_dir):
    """Télécharge plusieurs vidéos à partir d'un fichier texte."""
    if not os.path.exists(file_path):
        error_message = texts["error_file_not_found"]
        status_label.configure(text=error_message, text_color="red")
        logger.error(error_message)
        return

    if not os.path.exists(output_dir):
        error_message = texts["error_invalid_folder"]
        status_label.configure(text=error_message, text_color="red")
        logger.error(error_message)
        return

    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    total = len(urls)
    success_count = 0  # Compteur pour compter le nombre de téléchargements réussis

    for i, url in enumerate(urls, start=1):
        try:
            progress_text = texts["progress_batch_download"].format(current=i, total=total)
            status_label.configure(text=progress_text, text_color="blue")
            logger.info(progress_text)

            progress_bar.set((i - 1) / total)

            yt = YouTube(url, on_progress_callback=on_progress)

            # Vérifier si la vidéo est dispo en résolution demandée
            if selected_video_res != "None":
                video_stream = yt.streams.filter(adaptive=True, only_video=True, resolution=selected_video_res).first()
                if not video_stream:
                    error_message = texts["error_no_video"].format(title=yt.title, res=selected_video_res)
                    status_label.configure(text=error_message, text_color="red")
                    logger.warning(error_message)
                    continue  # Passe à la vidéo suivante
                else:
                    status_label.configure(text=texts["video_found"].format(title=yt.title, res=selected_video_res), text_color="blue")
                    logger.info(texts["video_found_log"].format(title=yt.title, res=selected_video_res))

            # Récupérer le meilleur bitrate audio
            best_audio = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
            if not best_audio:
                error_message = texts["error_no_audio"].format(title=yt.title, bitrate=selected_audio_bitrate)
                status_label.configure(text=error_message, text_color="red")
                logger.warning(error_message)
                continue  # Passe à la vidéo suivante

            selected_audio_bitrate = best_audio.abr  # Ex: "128kbps", "160kbps"

            # Procéder à la fusion de l'audio et de la vidéo
            download_and_merge(url, selected_video_res, selected_audio_bitrate, status_label, progress_bar, output_dir, None)

            # Mise à jour du compteur de succès
            success_count += 1

        except Exception as e:
            error_message = texts["error_generic"].format(error=str(e))
            status_label.configure(text=error_message, text_color="red")
            logger.error(error_message)


    progress_bar.set(1)
    final_status = texts["batch_download_summary"].format(success=success_count, total=total)
    status_label.configure(text=final_status, text_color="green")
    logger.info(final_status)

