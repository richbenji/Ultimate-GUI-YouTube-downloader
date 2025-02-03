# Langue actuelle (par défaut en Français)
current_language = "Français"

#TODO : fetching_resolutions: Résolutions récupérées
#TODO : quand on clique sur le bouton "Récupérer résolutions et bitrates", il faut que ça écrive "Récupération des résolutions en cours..."
#TODO : rajouter dans les autres langues "download_completed": "Téléchargement terminé.",
#TODO : batch_download_complete : rajouté le compte de vidéos téléchargées
#TODO : complete ou completed ?


def get_current_language():
    """Retourne la langue actuelle."""
    global current_language
    return current_language

def set_current_language(language):
    """Met à jour la langue actuelle."""
    global current_language, texts
    current_language = language
    texts = translations[language]

# Dictionnaire des traductions (Français & Anglais)
translations = {
    "Français": {
        # --- Interface utilisateur (GUI) ---
        "title": "Ultimate GUI YouTube Downloader",
        "subtitle": "Une Interface Graphique pour Pytubefix",
        "status_ready": "Statut : Prêt",
        "enter_url": "Entrez l'URL de la vidéo YouTube",
        "fetching_res_bit": "Récupérer résolutions et bitrates",
        "download_button": "Télécharger",
        "open_log": "Ouvrir Log",
        "select_file": "Sélectionner un fichier texte",
        "select_resolution": "Sélectionner une résolution",
        "batch_download": "Télécharger en batch",
        "video_resolution": "Résolution vidéo",
        "audio_bitrate": "Bitrate audio",
        "download": "Télécharger",
        "selected_file": "Fichier sélectionné",
        "select_folder": "Sélectionner un dossier de destination",
        "no_folder_selected": "Aucun dossier sélectionné.",

        # --- Messages d'exécution ---
        "fetching_resolutions": "Récupération des résolutions...",
        "downloading_video": "Téléchargement de la vidéo en cours...",
        "video_downloaded": "Vidéo téléchargée avec succès.",
        "video_downloaded_log": "Vidéo téléchargée : {filename}.mp4",
        "downloading_audio": "Téléchargement de l'audio en cours...",
        "audio_downloaded": "Audio téléchargé avec succès.",
        "audio_downloaded_log": "Audio téléchargé : {filename}.mp3",
        "downloading_video_audio": "Téléchargement des fichiers audio et vidéo effectué",
        "downloading_video_audio_log": "Vidéo et audio téléchargés pour fusion : {title}",
        "merging": "Fusion de l'audio et de la vidéo...",
        "merging_files": "Fusion en cours",
        "merge_successful": "Fusion réussie",
        "download_merge_complete": "Téléchargement et fusion terminés : {filename}",
        "download_merge_complete_log": "Fusion terminée : {filename}",
        "download_completed": "Téléchargement terminé.",
        "batch_download_complete": "Téléchargement batch terminé.",

        # --- Messages d'erreur ---
        "error": "ERREUR :",
        "error_no_video": "Erreur : La vidéo '{title}' n'existe pas en {res}.",
        "error_no_audio": "Erreur : Pas d'audio disponible pour '{title}' en {bitrate}.",
        "error_no_video_available": "Aucune résolution vidéo disponible pour '{title}'.",
        "error_no_audio_available": "Aucun bitrate audio disponible pour '{title}'.",
        "error_fetching_resolutions": "Erreur lors de la récupération des résolutions",
        "error_merge": "Erreur lors de la fusion avec FFmpeg",
        "error_merge_ffmpeg": "Erreur FFmpeg : {error}",
        "FFmpeg_not_found": "FFmpeg n'est pas installé ou introuvable.",
        "error_file_not_found": "Erreur : Fichier introuvable.",
        "error_invalid_folder": "Erreur : Dossier de destination invalide.",
        "error_generic": "Une erreur est survenue : {error}",
    },

    "English": {
        # --- User Interface (GUI) ---
        "title": "Ultimate GUI YouTube Downloader",
        "subtitle": "A Pytubefix GUI",
        "status_ready": "Status: Ready",
        "enter_url": "Enter the URL of the YouTube video",
        "fetching_res_bit": "Fetching resolutions and bitrates",
        "download_button": "Download",
        "open_log": "Open Log",
        "select_file": "Select a text file",
        "select_resolution": "Select a resolution",
        "batch_download": "Batch download",
        "video_resolution": "Video resolution",
        "audio_bitrate": "Audio Bitrate",
        "download": "Download",
        "selected_file": "Selected file",
        "select_folder": "Select a destination folder",
        "no_folder_selected": "No folder selected.",

        # --- Execution Messages ---
        "fetching_resolutions": "Fetching resolutions...",
        "downloading_video": "Downloading video...",
        "video_downloaded": "Video successfully downloaded.",
        "video_downloaded_log": "Video downloaded: {filename}.mp4",
        "downloading_audio": "Downloading audio...",
        "audio_downloaded": "Audio successfully downloaded.",
        "audio_downloaded_log": "Audio downloaded: {filename}.mp3",
        "downloading_video_audio": "Downloading video and audio files completed",
        "downloading_video_audio_log": "Video and audio downloaded for merging: {title}",
        "merging": "Merging audio and video...",
        "merging_files": "Merging in progress",
        "merge_successful": "Merge successful",
        "download_merge_complete": "Download and merge complete: {filename}",
        "download_merge_complete_log": "Merge completed: {filename}",
        "batch_download_complete": "Batch download complete.",

        # --- Error Messages ---
        "error": "ERROR:",
        "error_no_video": "Error: The video '{title}' is not available in {res}.",
        "error_no_audio": "Error: No audio available for '{title}' in {bitrate}.",
        "error_no_video_available": "No video resolution available for '{title}'.",
        "error_no_audio_available": "No audio bitrate available for '{title}'.",
        "error_fetching_resolutions": "Error fetching resolutions",
        "error_merge": "Error while merging with FFmpeg",
        "error_merge_ffmpeg": "FFmpeg error: {error}",
        "FFmpeg_not_found": "FFmpeg is not installed or not found.",
        "error_file_not_found": "Error: File not found.",
        "error_invalid_folder": "Error: Invalid destination folder.",
        "error_generic": "An error occurred: {error}",
    },
    "Español": {
        # --- Interfaz de usuario (GUI) ---
        "title": "Ultimate GUI YouTube Downloader",
        "subtitle": "Una interfaz gráfica para Pytubefix",
        "status_ready": "Estado: Listo",
        "enter_url": "Ingrese la URL del video de YouTube",
        "fetching_res_bit": "Recuperando resoluciones y tasas de bits",
        "download_button": "Descargar",
        "open_log": "Abrir registro",
        "select_file": "Seleccionar un archivo de texto",
        "select_resolution": "Seleccionar una resolución",
        "batch_download": "Descarga por lotes",
        "video_resolution": "Resolución de video",
        "audio_bitrate": "Tasa de bits de audio",
        "download": "Descargar",
        "selected_file": "Archivo seleccionado",
        "select_folder": "Seleccionar una carpeta de destino",
        "no_folder_selected": "Ninguna carpeta seleccionada.",

        # --- Mensajes de ejecución ---
        "fetching_resolutions": "Recuperando resoluciones...",
        "downloading_video": "Descargando video...",
        "video_downloaded": "Video descargado con éxito.",
        "video_downloaded_log": "Video descargado: {filename}.mp4",
        "downloading_audio": "Descargando audio...",
        "audio_downloaded": "Audio descargado con éxito.",
        "audio_downloaded_log": "Audio descargado: {filename}.mp3",
        "downloading_video_audio": "Descarga de archivos de video y audio completada",
        "downloading_video_audio_log": "Video y audio descargados para la fusión: {title}",
        "merging": "Fusionando audio y video...",
        "merging_files": "Fusión en curso",
        "merge_successful": "Fusión exitosa",
        "download_merge_complete": "Descarga y fusión completadas: {filename}",
        "download_merge_complete_log": "Fusión completada: {filename}",
        "batch_download_complete": "Descarga por lotes completada.",

        # --- Mensajes de error ---
        "error": "ERROR:",
        "error_no_video": "Error: El video '{title}' no está disponible en {res}.",
        "error_no_audio": "Error: No hay audio disponible para '{title}' en {bitrate}.",
        "error_no_video_available": "No hay resolución de video disponible para '{title}'.",
        "error_no_audio_available": "No hay tasa de bits de audio disponible para '{title}'.",
        "error_fetching_resolutions": "Error al recuperar resoluciones",
        "error_merge": "Error al fusionar con FFmpeg",
        "error_merge_ffmpeg": "Error de FFmpeg: {error}",
        "FFmpeg_not_found": "FFmpeg no está instalado o no se encuentra.",
        "error_file_not_found": "Error: Archivo no encontrado.",
        "error_invalid_folder": "Error: Carpeta de destino no válida.",
        "error_generic": "Ocurrió un error: {error}",
    },
    "Deutsch": {
        # --- Benutzeroberfläche (GUI) ---
        "title": "Ultimate GUI YouTube Downloader",
        "subtitle": "Eine grafische Oberfläche für Pytubefix",
        "status_ready": "Status: Bereit",
        "enter_url": "Geben Sie die URL des YouTube-Videos ein",
        "fetching_res_bit": "Auflösungen und Bitraten abrufen",
        "download_button": "Herunterladen",
        "open_log": "Protokoll öffnen",
        "select_file": "Textdatei auswählen",
        "select_resolution": "Auflösung auswählen",
        "batch_download": "Stapel-Download",
        "video_resolution": "Videoauflösung",
        "audio_bitrate": "Audio-Bitrate",
        "download": "Herunterladen",
        "selected_file": "Ausgewählte Datei",
        "select_folder": "Zielordner auswählen",
        "no_folder_selected": "Kein Ordner ausgewählt.",

        # --- Ausführungsnachrichten ---
        "fetching_resolutions": "Auflösungen werden abgerufen...",
        "downloading_video": "Video wird heruntergeladen...",
        "video_downloaded": "Video erfolgreich heruntergeladen.",
        "video_downloaded_log": "Video heruntergeladen: {filename}.mp4",
        "downloading_audio": "Audio wird heruntergeladen...",
        "audio_downloaded": "Audio erfolgreich heruntergeladen.",
        "audio_downloaded_log": "Audio heruntergeladen: {filename}.mp3",
        "downloading_video_audio": "Download von Video- und Audiodateien abgeschlossen",
        "downloading_video_audio_log": "Video und Audio heruntergeladen für Zusammenführung: {title}",
        "merging": "Audio und Video werden zusammengeführt...",
        "merging_files": "Zusammenführung läuft",
        "merge_successful": "Zusammenführung erfolgreich",
        "download_merge_complete": "Download und Zusammenführung abgeschlossen: {filename}",
        "download_merge_complete_log": "Zusammenführung abgeschlossen: {filename}",
        "batch_download_complete": "Stapel-Download abgeschlossen.",

        # --- Fehlermeldungen ---
        "error": "FEHLER:",
        "error_no_video": "Fehler: Das Video '{title}' ist in {res} nicht verfügbar.",
        "error_no_audio": "Fehler: Kein Audio für '{title}' in {bitrate} verfügbar.",
        "error_no_video_available": "Keine Videoauflösung für '{title}' verfügbar.",
        "error_no_audio_available": "Keine Audio-Bitrate für '{title}' verfügbar.",
        "error_fetching_resolutions": "Fehler beim Abrufen der Auflösungen",
        "error_merge": "Fehler beim Zusammenführen mit FFmpeg",
        "error_merge_ffmpeg": "FFmpeg-Fehler: {error}",
        "FFmpeg_not_found": "FFmpeg ist nicht installiert oder nicht gefunden.",
        "error_file_not_found": "Fehler: Datei nicht gefunden.",
        "error_invalid_folder": "Fehler: Ungültiger Zielordner.",
        "error_generic": "Ein Fehler ist aufgetreten: {error}",
    }
}

# Variable globale contenant les traductions de la langue actuelle
texts = translations[current_language]