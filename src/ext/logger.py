"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""

import logging
import datetime
import pytz
from discord.utils import setup_logging

class Logger:
    """
    This class is used to log messages to the console with different format for different levels of logging.
    1. debug: logs a debug message to the console
    2. info: logs an info message to the console
    3. warning: logs a warning message to the console
    4. error: logs an error message to the console
    5. critical: logs a critical message to the console
    example:- 
                Logger.debug("Debug message")
                Logger.info("Info message")
                Logger.warning("Warning message")
                Logger.error("Error message")
                Logger.critical("Critical message")
    """



    _logger = logging.getLogger("root")
    console_handler = logging.StreamHandler()
    _logger.setLevel(logging.INFO)
    _logger.addHandler(console_handler)
    setup_logging(handler=console_handler, root=True)

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
        Logger._logger.debug(message)

    @staticmethod
    def info( message):
        formatter = logging.Formatter(f"{Logger.colors('magenta')}[{Logger.get_time()}]{Logger.colors('INFO')} [%(levelname)s]: {Logger.colors('none')}%(message)s")
        Logger.console_handler.setFormatter(formatter)
        Logger._logger.info(message)

    @staticmethod
    def warning( message, _module=None, *args):
        formatter = logging.Formatter(f"{Logger.colors('magenta')}[{Logger.get_time()}]{Logger.colors('WARNING')} [%(levelname)s] {_module if _module else ''}: {Logger.colors('none')}%(message)s")
        Logger.console_handler.setFormatter(formatter)
        Logger._logger.warning(message)

    @staticmethod
    def error(*message):
        formatter = logging.Formatter(f"{Logger.colors('magenta')}[{Logger.get_time()}]{Logger.colors('ERROR')} [%(levelname)s]: {Logger.colors('none')}%(message)s")
        Logger.console_handler.setFormatter(formatter)
        Logger._logger.error("\n".join(str(m) for m in message))

    @staticmethod
    def critical( message):
        formatter = logging.Formatter(f"{Logger.colors('magenta')}[{Logger.get_time()}]{Logger.colors('CRITICAL')} [%(levelname)s]: {Logger.colors('none')}%(message)s")
        Logger.console_handler.setFormatter(formatter)
        Logger._logger.critical(message)


