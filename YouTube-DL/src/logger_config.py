import logging


# Configuration du logging
LOG_FILE = "youtube_downloader.log"  # Nom du fichier log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w"),
        logging.StreamHandler()  # Affiche aussi les logs dans la console
    ]
)

logger = logging.getLogger(__name__)