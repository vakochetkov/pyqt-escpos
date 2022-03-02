import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s][%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("pyqt-escpos.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting application...")
    from gui import application
    application.main()
    logger.info("Exiting application...")