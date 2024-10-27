import logging
import datetime
import pytz

class Logger:
    """
    This class is used to log messages to the console with different format for different levels of logging.
    1. debug: logs a debug message to the console
    2. info: logs an info message to the console
    3. warning: logs a warning message to the console
    4. error: logs an error message to the console
    5. critical: logs a critical message to the console
    example:- logger = Logger()
                logger.debug("Debug message")
                logger.info("Info message")
                logger.warning("Warning message")
                logger.error("Error message")
                logger.critical("Critical message")
    """



    logger = logging.getLogger("root")
    console_handler = logging.StreamHandler()
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    @staticmethod
    def get_time():
        return str(datetime.datetime.now(pytz.timezone("Asia/Kolkata")))[:-7]
    
    @staticmethod
    def colors(level):
        colors = {
            "DEBUG":"\u001b[34m", 
            "INFO":"\u001b[32m", 
            "WARNING":"\033[1;33m", 
            "ERROR":"\033[1;31m", 
            "CRITICAL":"\033[1;31m", 
            "none":"\u001b[0m", 
            "reset":"\u001b[0m", 
            "bold":"\u001b[1m", 
            "underline":"\u001b[4m", 
            "blink":"\u001b[5m", 
            "reverse":"\u001b[7m", 
            "invisible":"\u001b[8m", 
            "magenta":"\u001b[35m"}
        return colors[level]


    @staticmethod
    def debug(message):
        formatter = logging.Formatter(f"{Logger.colors('magenta')}[{Logger.get_time()}]{Logger.colors('DEBUG')} [%(levelname)s]: {Logger.colors('none')}%(message)s")
        Logger.console_handler.setFormatter(formatter)
        Logger.logger.debug(message)

    @staticmethod
    def info( message):
        formatter = logging.Formatter(f"{Logger.colors('magenta')}[{Logger.get_time()}]{Logger.colors('INFO')} [%(levelname)s]: {Logger.colors('none')}%(message)s")
        Logger.console_handler.setFormatter(formatter)
        Logger.logger.info(message)

    @staticmethod
    def warning( message):
        formatter = logging.Formatter(f"{Logger.colors('magenta')}[{Logger.get_time()}]{Logger.colors('WARNING')} [%(levelname)s]: {Logger.colors('none')}%(message)s")
        Logger.console_handler.setFormatter(formatter)
        Logger.logger.warning(message)

    @staticmethod
    def error( message):
        formatter = logging.Formatter(f"{Logger.colors('magenta')}[{Logger.get_time()}]{Logger.colors('ERROR')} [%(levelname)s]: {Logger.colors('none')}%(message)s")
        Logger.console_handler.setFormatter(formatter)
        Logger.logger.error(message)

    @staticmethod
    def critical( message):
        formatter = logging.Formatter(f"{Logger.colors('magenta')}[{Logger.get_time()}]{Logger.colors('CRITICAL')} [%(levelname)s]: {Logger.colors('none')}%(message)s")
        Logger.console_handler.setFormatter(formatter)
        Logger.logger.critical(message)


