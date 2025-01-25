import os

# Classe pour centraliser la configuration
class Config:
    # Répertoire de base du projet
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Dossiers principaux
    ASSETS_DIR = os.path.join(BASE_DIR, "../assets")
    FONTS_DIR = os.path.join(BASE_DIR, "../fonts")
    DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")

    # Fichiers spécifiques
    LOGO_PATH = os.path.join(ASSETS_DIR, "Youtube_logo.png")
    SVG_PATH = os.path.join(ASSETS_DIR, "YouTube_2024.svg")
    TOKEN_FILE_PATH = os.path.join(BASE_DIR, "src", "token.json")

    # Polices
    FONT_METAL_MANIA = os.path.join(FONTS_DIR, "MetalMania-Regular.ttf")
    FONT_TRADE_GOTHIC_BOLD = os.path.join(FONTS_DIR, "TradeGothic Bold.ttf")

    # Application
    APP_NAME = "Ultimate GUI YouTube Downloader"
    APP_VERSION = "1.0.0"