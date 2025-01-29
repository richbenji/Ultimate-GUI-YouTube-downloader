import os
from pytubefix import YouTube
from downloader.utils import show_progress, merge_audio_video, sanitize_filename

# Fonction pour télécharger une vidéo et fusionner audio + vidéo si nécessaire
def download_and_merge1(url, selected_video_res, selected_audio_bitrate, status_label, progress_bar, output_dir=None,
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
                status_label.configure(text="Erreur : Résolution vidéo introuvable.", text_color="red")
                return

            status_label.configure(text="Téléchargement de la vidéo en cours...", text_color="blue")
            video_stream.download(output_path=output_dir, filename=f"{custom_filename}.mp4")
            status_label.configure(text="Vidéo téléchargée avec succès.", text_color="green")
            return

        ####################################################################
        # Cas 2 : Télécharger uniquement l'audio si la résolution est "None"
        ####################################################################

        if selected_video_res == "None":
            audio_stream = yt.streams.filter(adaptive=True, only_audio=True, abr=selected_audio_bitrate).first()
            if not audio_stream:
                status_label.configure(text="Erreur : Bitrate audio introuvable.", text_color="red")
                return

            status_label.configure(text="Téléchargement de l'audio en cours...", text_color="blue")
            audio_stream.download(output_path=output_dir, filename=f"{custom_filename}.mp3")
            status_label.configure(text="Audio téléchargé avec succès.", text_color="green")
            return

        ####################################################################
        # Cas 3 : Télécharger et fusionner si les deux valeurs sont valides
        ####################################################################

        # Filtrer les streams vidéo et sélectionner celui avec la bonne résolution
        video_stream = yt.streams.filter(adaptive=True, only_video=True, resolution=selected_video_res).first()
        if not video_stream:
            status_label.configure(text="Erreur : Résolution vidéo non trouvée.", text_color="red")
            return

        # Filtrer les streams audio et sélectionner celui avec le bon bitrate
        audio_stream = yt.streams.filter(adaptive=True, only_audio=True, abr=selected_audio_bitrate).first()
        if not audio_stream:
            status_label.configure(text="Erreur : Bitrate audio non trouvé.", text_color="red")
            return

        # Définir les fichiers de sortie temporaires
        #video_file = os.path.join(output_dir, f"{custom_filename}_video.mp4")
        #audio_file = os.path.join(output_dir, f"{custom_filename}_audio.mp3")

        # Afficher les informations
        status_label.configure(text="Téléchargement en cours...", text_color="blue")

        # Télécharger la vidéo et l'audio
        video_file = f"{custom_filename}_video.mp4"
        audio_file = f"{custom_filename}_audio.mp3"

        video_stream.download(output_path=output_dir, filename=video_file)
        audio_stream.download(output_path=output_dir, filename=audio_file)

        status_label.configure(text="Téléchargement des fichiers audio et vidéo effectué", text_color="blue")

        # Fusionner avec FFmpeg
        status_label.configure(text="Fusion de l'audio et de la vidéo...", text_color="blue")
        merge_audio_video(video_file, audio_file, final_filename)

        # Supprimer les fichiers temporaires
        # Vérifier si la fusion a bien réussi avant de supprimer les fichiers temporaires
        if os.path.exists(final_filename):
            os.remove(video_file)
            os.remove(audio_file)
        else:
            status_label.configure(text="Erreur : La fusion a échoué, le fichier final est introuvable.",
                                   text_color="red")
            return

        # Indiquer la fin du téléchargement
        status_label.configure(
            text=f"Téléchargement et fusion terminés. Fichier final : {final_filename}",
            text_color="green"
        )

    except Exception as e:
        status_label.configure(text=f"Erreur : {e}", text_color="red")

# Fonction pour télécharger une vidéo et fusionner audio + vidéo si nécessaire
def download_and_merge(url, selected_option, status_label, progress_bar, output_dir=None, custom_filename=None):
    """Télécharge une vidéo et fusionne audio + vidéo si nécessaire."""
    try:
        yt = YouTube(url, use_po_token=True)

        # Ajouter une méthode pour suivre la progression
        total_size = yt.streams.get_highest_resolution().filesize
        yt.register_on_progress_callback(
            lambda stream, chunk, bytes_remaining: show_progress(
                stream, chunk, bytes_remaining, total_size, progress_bar
            )
        )

        format_selected, resolution_selected = selected_option.split()

        # Déterminer le nom du fichier final
        if not custom_filename:
            sanitized_title = sanitize_filename(yt.title)
            custom_filename = f"{sanitized_title}.{format_selected.lower()}"

        final_filename = os.path.join(output_dir, custom_filename)

        # Rechercher le flux correspondant
        selected_stream = yt.streams.filter(mime_type=f"video/{format_selected.lower()}", res=resolution_selected).first()

        if selected_stream and selected_stream.is_progressive:
            # Téléchargement d'un flux progressif
            status_label.configure(text="Téléchargement du flux progressif...")
            selected_stream.download(output_path=output_dir, filename=custom_filename)
            status_label.configure(
                text=f"Téléchargement terminé. Fichier final : {final_filename}",
                text_color="green"
            )
        else:
            # Téléchargement séparé de la vidéo et de l'audio
            status_label.configure(text="Téléchargement séparé de la vidéo et de l'audio...")

            video_file = os.path.join(output_dir, f"{custom_filename}_video.mp4")
            audio_file = os.path.join(output_dir, f"{custom_filename}_audio.mp3")
            output_file = final_filename

            video_stream = yt.streams.filter(mime_type=f"video/{format_selected.lower()}", res=resolution_selected).first()
            video_stream.download(output_path=output_dir, filename=f"{custom_filename}_video.mp4")

            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_stream.download(output_path=output_dir, filename=f"{custom_filename}_audio.mp3")

            # Fusionner avec FFmpeg
            merge_audio_video(video_file, audio_file, output_file)

            # Supprimer les fichiers temporaires
            os.remove(video_file)
            os.remove(audio_file)

            status_label.configure(
                text=f"Téléchargement et fusion terminés. Fichier final : {output_file}",
                text_color="green"
            )

    except Exception as e:
        status_label.configure(text=f"Erreur : {e}", text_color="red")


def download_from_file(file_path, selected_option, status_label=None, progress_bar=None, output_dir=None):
    """Télécharge des vidéos à partir d'un fichier texte en utilisant download_and_merge."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")

    if not output_dir or not os.path.exists(output_dir):
        raise ValueError(f"Dossier de destination invalide : {output_dir}")

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
            download_and_merge(
                url,
                selected_option,
                status_label,
                progress_bar,
                output_dir=output_dir  # Dossier de destination
            )

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
