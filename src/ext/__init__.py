from modules import config
import logging, datetime

__all__ = ("Database", "Tourney", "Logger")

class Tourney:
    def __init__(self, obj):
        self.tname = obj["t_name"]
        self.rch = obj["rch"]
        self.tid = obj["tid"]
        self.cch = obj["cch"]
        self.crole = obj["crole"]
        self.gch = obj["gch"]
        self.tslot = obj["tslot"]
        self.prefix = obj["prefix"]
        self.faketag = obj["faketag"]
        self.reged = obj["reged"]
        self.status = obj["status"]
        self.pub = obj["pub"]
        self.spg = obj["spg"]
        self.auto_grp = obj["auto_grp"]
        self.cgp = obj["cgp"]


class Database:
    def __init__(self):
        self.db = config.maindb
        self.sdb = config.spdb
        self.dbc = self.db["tourneydb"]["tourneydbc"]
        
    def find_one(self, obj) -> Tourney:
        return Tourney(self.db["tourneydb"]["tourneydbc"].find_one(obj))

    def find(self, obj) -> list[Tourney]:
        return [Tourney(i) for i in self.db["tourneydb"]["tourneydbc"].find(obj)]

    def insert(self, obj) -> None:
        return self.db["tourneydb"]["tourneydbc"].insert_one(obj)

    def update_one(self, obj, obj2) -> None:
        self.db["tourneydb"]["tourneydbc"].update_one(obj, obj2)

    def update_many(self, obj, obj2) -> None:
        self.db["tourneydb"]["tourneydbc"].update_many(obj, obj2)

    def delete_one(self, obj)  -> None:
        self.db["tourneydb"]["tourneydbc"].delete_one(obj)


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

    def __init__(self, level=logging.DEBUG):
        self.logger = logging.getLogger()
        self.console_handler = logging.StreamHandler()
        self.logger.setLevel(level)
        self.logger.addHandler(self.console_handler)

    def colors(self, level):
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

    def debug(self, message):
        formatter = logging.Formatter(f"{self.colors('magenta')}[{str(datetime.datetime.utcnow())[:-7]}]{self.colors('DEBUG')} [%(levelname)s]: {self.colors('none')}%(message)s")
        self.console_handler.setFormatter(formatter)
        self.logger.debug(message)

    def info(self, message):
        formatter = logging.Formatter(f"{self.colors('magenta')}[{str(datetime.datetime.utcnow())[:-7]}]{self.colors('INFO')} [%(levelname)s]: {self.colors('none')}%(message)s")
        self.console_handler.setFormatter(formatter)
        self.logger.info(message)

    def warning(self, message):
        formatter = logging.Formatter(f"{self.colors('magenta')}[{str(datetime.datetime.utcnow())[:-7]}]{self.colors('WARNING')} [%(levelname)s]: {self.colors('none')}%(message)s")
        self.console_handler.setFormatter(formatter)
        self.logger.warning(message)

    def error(self, message):
        formatter = logging.Formatter(f"{self.colors('magenta')}[{str(datetime.datetime.utcnow())[:-7]}]{self.colors('ERROR')} [%(levelname)s]: {self.colors('none')}%(message)s")
        self.console_handler.setFormatter(formatter)
        self.logger.error(message)

    def critical(self, message):
        formatter = logging.Formatter(f"{self.colors('magenta')}[{str(datetime.datetime.utcnow())[:-7]}]{self.colors('CRITICAL')} [%(levelname)s]: {self.colors('none')}%(message)s")
        self.console_handler.setFormatter(formatter)
        self.logger.critical(message)