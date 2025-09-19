import os, logging
# from modules.openai.client import process_audio
from share.usecases import transcribe_file
from share.utils import cleanup_temp_files

logger = logging.getLogger(__name__)
TEMP_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "temp")

# Функция transcribe_file теперь импортируется из share.usecases
# чтобы избежать дублирования кода
