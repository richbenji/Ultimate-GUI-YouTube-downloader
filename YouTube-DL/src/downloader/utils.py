import os
import subprocess
from pytubefix import YouTube

def show_progress(stream, chunk, bytes_remaining, total_size, progress_bar):
    """Met à jour la barre de progression pendant le téléchargement."""
    if total_size is not None and progress_bar is not None:
        percent = (1 - bytes_remaining / total_size) * 100
        progress_bar.set(percent / 100)

# Fonction pour récupérer les résolutions disponibles
def fetch_resolutions(url, resolution_menu, status_label):
    """Récupère les résolutions disponibles pour une vidéo."""
    try:
        yt = YouTube(url, use_po_token=True)
        streams = yt.streams.filter(adaptive=True)
        options = [f"{stream.mime_type.split('/')[-1].upper()} {stream.resolution}" for stream in streams if stream.resolution]
        options = list(set(options))  # Éviter les doublons
        options.sort()  # Trier par ordre croissant

        if options:
            resolution_menu.configure(values=options)
            resolution_menu.set(options[-1])  # Sélectionner la résolution la plus élevée par défaut
            status_label.configure(text="Résolutions récupérées.", text_color="green")
        else:
            status_label.configure(text="Aucune résolution disponible.", text_color="red")
    except Exception as e:
        status_label.configure(text=f"Erreur : {e}", text_color="red")

def merge_audio_video(video_file, audio_file, output_file):
    """Fusionne des fichiers audio et vidéo avec FFmpeg."""
    try:
        command = [
            "ffmpeg", "-i", video_file, "-i", audio_file,
            "-c:v", "copy", "-c:a", "aac", output_file
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    except FileNotFoundError:
        raise RuntimeError("FFmpeg n'est pas installé ou introuvable dans le PATH.")

def sanitize_filename(filename):
    """Nettoie le titre pour en faire un nom de fichier valide."""
    return "".join(c for c in filename if c.isalnum() or c in " .-_").rstrip()

def fetch_video_resolutions(url, resolution_menu, status_label):
    """Récupère les résolutions des flux vidéo adaptatifs."""
    try:
        yt = YouTube(url, use_po_token=True)
        # Filtrer uniquement les flux vidéo adaptatifs
        video_streams = yt.streams.filter(adaptive=True, only_video=True)
        options = [f"{stream.resolution}" for stream in video_streams if stream.resolution]
        options = list(set(options))  # Éviter les doublons
        options.sort()  # Trier par ordre croissant

        if options:
            resolution_menu.configure(values=options)
            resolution_menu.set(options[-1])  # Sélectionner la résolution la plus élevée par défaut
            status_label.configure(text="Résolutions vidéo récupérées.", text_color="green")
        else:
            status_label.configure(text="Aucune résolution vidéo disponible.", text_color="red")
    except Exception as e:
        status_label.configure(text=f"Erreur : {e}", text_color="red")


def fetch_audio_bitrates(url, bitrate_menu, status_label):
    """Récupère les bitrates des flux audio adaptatifs."""
    try:
        yt = YouTube(url, use_po_token=True)
        # Filtrer uniquement les flux audio adaptatifs
        audio_streams = yt.streams.filter(adaptive=True, only_audio=True)
        options = [f"{stream.abr}" for stream in audio_streams if stream.abr]
        options = list(set(options))  # Éviter les doublons
        options.sort()  # Trier par ordre croissant

        if options:
            bitrate_menu.configure(values=options)
            bitrate_menu.set(options[-1])  # Sélectionner le bitrate le plus élevé par défaut
            status_label.configure(text="Bitrates audio récupérés.", text_color="green")
        else:
            status_label.configure(text="Aucun bitrate audio disponible.", text_color="red")
    except Exception as e:
        status_label.configure(text=f"Erreur : {e}", text_color="red")