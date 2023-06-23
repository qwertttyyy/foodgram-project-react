from pathlib import Path

from backend import settings

CACHE_PATH = Path(__file__).resolve().parent / 'cache'
FONTS_PATH = settings.BASE_DIR / 'fonts'
