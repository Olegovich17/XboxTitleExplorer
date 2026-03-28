# -*- coding: utf-8 -*-
"""Entry point for Xbox Title Explorer."""
import sys
sys.dont_write_bytecode = True

import atexit
import logging

from PyQt6.QtWidgets import QApplication

from core.config import APP_BASE_PATH, cleanup_temp_file, TEMP_LIST_PATH
from gui import MainWindow
from gui.styles import Theme
from resources.locales import APP_TITLE

logger = logging.getLogger(__name__)


def setup_logging(debug: bool) -> None:
    """Configure logging to file and terminal if debug mode is enabled."""
    if not debug:
        logging.disable(logging.CRITICAL)
        return

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(APP_BASE_PATH / 'app.log', mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    logger.info("Logging initialized in debug mode")


def main() -> None:
    debug_mode = "--debug" in sys.argv
    setup_logging(debug_mode)
    
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    
    Theme.apply_theme(app)
    
    atexit.register(cleanup_temp_file, TEMP_LIST_PATH)
    
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.exception("Application crashed")
        sys.exit(1)




if __name__ == "__main__":
    main()
