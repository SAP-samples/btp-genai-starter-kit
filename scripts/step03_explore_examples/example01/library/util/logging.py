import logging
import sys
import traceback

LOGLEVEL = logging.INFO
HEADER = logging.CRITICAL + 1
USERINPUT = HEADER + 1
SUCCESS = USERINPUT + 1
CHECK = SUCCESS + 1

config = {
    "USERINPUT": USERINPUT,
    "HEADER": HEADER,
    "SUCCESS": SUCCESS,
    "CHECK": CHECK,
}


# Set custom logging levels
def set_custom_logging_levels(config={}):
    assert isinstance(config, dict), "Configuration must be a dict"

    def get_level_func(level_name, level_num):
        def _blank(self, message, *args, **kws):
            if self.isEnabledFor(level_num):
                # Yes, logger takes its '*args' as 'args'.
                self._log(level_num, message, args, **kws)

        _blank.__name__ = level_name.lower()
        return _blank

    for level_name, level_num in config.items():
        logging.addLevelName(level_num, level_name.upper())
        setattr(
            logging.Logger, level_name.lower(), get_level_func(level_name, level_num)
        )


# Custom formatter
class MyFormatterStream(logging.Formatter):
    COLOR_RESET_COLORS = "\033[0;0m"
    COLOR_TIMESTAMP = "\033[38;5;241m"

    COLOR_HEADER = "\033[38;5;15m"
    COLOR_ERROR = "\033[38;5;160m"
    COLOR_CRITICAL = "\033[38;5;160m"
    COLOR_CHECK = "\033[38;5;10m"
    COLOR_INFO = "\033[38;5;241m"
    COLOR_SUCCESS = "\033[38;5;40m"
    COLOR_WARNING = "\033[38;5;11m"
    COLOR_USERINPUT = "\033[38;5;51m"

    format_HEADER = (
        COLOR_RESET_COLORS + "-" * 80 + "\n%(msg)s\n" + "-" * 80 + COLOR_RESET_COLORS
    )
    format_ERROR = (
        COLOR_TIMESTAMP
        + "[%(asctime)s] "
        + COLOR_ERROR
        + "ERROR  : %(msg)s"
        + COLOR_RESET_COLORS
    )
    format_CHECK = (
        COLOR_TIMESTAMP
        + "[%(asctime)s] "
        + COLOR_CHECK
        + "CHECK  : %(msg)s"
        + COLOR_RESET_COLORS
    )
    format_INFO = (
        COLOR_TIMESTAMP
        + "[%(asctime)s] "
        + COLOR_INFO
        + "INFO   : %(msg)s"
        + COLOR_RESET_COLORS
    )
    format_DEBUG = (
        COLOR_TIMESTAMP
        + "[%(asctime)s] "
        + COLOR_INFO
        + "DEBUG   : %(msg)s"
        + COLOR_RESET_COLORS
    )
    format_SUCCESS = (
        COLOR_TIMESTAMP
        + "[%(asctime)s] "
        + COLOR_SUCCESS
        + "SUCCESS: %(msg)s"
        + COLOR_RESET_COLORS
    )
    format_WARNING = (
        COLOR_TIMESTAMP
        + "[%(asctime)s] "
        + COLOR_WARNING
        + "WARNING: %(msg)s"
        + COLOR_RESET_COLORS
    )
    format_USERINPUT = (
        COLOR_TIMESTAMP
        + "[%(asctime)s] "
        + COLOR_USERINPUT
        + "INPUT  : %(msg)s"
        + COLOR_RESET_COLORS
    )
    format_CRITICAL = (
        COLOR_TIMESTAMP
        + "[%(asctime)s] "
        + COLOR_CRITICAL
        + "CRITICAL : %(msg)s"
        + COLOR_RESET_COLORS
    )

    def __init__(self):
        super().__init__(
            fmt=MyFormatterStream.COLOR_TIMESTAMP + "[%(asctime)s] %(msg)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            style="%",
        )

    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated

        format_orig = self._style._fmt
        self.datefmt = "%Y-%m-%d %H:%M:%S"

        # Replace the original format with one customized by logging level
        if record.levelno == config["USERINPUT"]:
            self._style._fmt = MyFormatterStream.format_USERINPUT

        if record.levelno == config["HEADER"]:
            self._style._fmt = MyFormatterStream.format_HEADER

        if record.levelno == config["SUCCESS"]:
            self._style._fmt = MyFormatterStream.format_SUCCESS

        if record.levelno == config["CHECK"]:
            self._style._fmt = MyFormatterStream.format_CHECK

        if record.levelno == logging.DEBUG:
            self._style._fmt = MyFormatterStream.format_DEBUG

        if record.levelno == logging.INFO:
            self._style._fmt = MyFormatterStream.format_INFO

        if record.levelno == logging.WARNING:
            self._style._fmt = MyFormatterStream.format_WARNING

        if record.levelno == logging.CRITICAL:
            self._style._fmt = MyFormatterStream.format_CRITICAL

        if record.levelno == logging.ERROR:
            self._style._fmt = MyFormatterStream.format_ERROR

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


# Custom formatter
class MyFormatterFile(logging.Formatter):
    format_HEADER = "#" * 100 + "\n# %(msg)s\n" + "#" * 100
    format_ERROR = "[%(asctime)s] " + "ERROR      : %(msg)s"
    format_CHECK = "[%(asctime)s] " + "CHECK      : %(msg)s"
    format_INFO = "[%(asctime)s] " + "INFO       : %(msg)s"
    format_DEBUG = "[%(asctime)s] " + "DEBUG      : %(msg)s"
    format_SUCCESS = "[%(asctime)s] " + "SUCCESS    : %(msg)s"
    format_WARNING = "[%(asctime)s] " + "WARNING    : %(msg)s"
    format_USERINPUT = "[%(asctime)s] " + "INPUT      : %(msg)s"
    format_CRITICAL = "[%(asctime)s] " + "CRITICAL     : %(msg)s"

    def __init__(self):
        super().__init__(
            fmt=MyFormatterStream.COLOR_TIMESTAMP + "[%(asctime)s] %(msg)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            style="%",
        )

    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt
        self.datefmt = "%Y-%m-%d %H:%M:%S"

        # Replace the original format with one customized by logging level
        if record.levelno == config["USERINPUT"]:
            self._style._fmt = MyFormatterFile.format_USERINPUT

        if record.levelno == config["HEADER"]:
            self._style._fmt = MyFormatterFile.format_HEADER

        if record.levelno == config["SUCCESS"]:
            self._style._fmt = MyFormatterFile.format_SUCCESS

        if record.levelno == config["CHECK"]:
            self._style._fmt = MyFormatterFile.format_CHECK

        if record.levelno == logging.DEBUG:
            self._style._fmt = MyFormatterFile.format_DEBUG

        if record.levelno == logging.INFO:
            self._style._fmt = MyFormatterFile.format_INFO

        if record.levelno == logging.WARNING:
            self._style._fmt = MyFormatterFile.format_WARNING

        if record.levelno == logging.CRITICAL:
            self._style._fmt = MyFormatterFile.format_CRITICAL

        if record.levelno == logging.ERROR:
            self._style._fmt = MyFormatterFile.format_ERROR

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


def log_exceptions(type, value, tb):
    for line in traceback.TracebackException(type, value, tb).format(chain=True):
        logging.exception(line)
    logging.exception(value)


def initLogger():
    set_custom_logging_levels(config)

    logging.root.setLevel(10)
    thisHandler = logging.StreamHandler(sys.stdout)
    thisHandler.setLevel(LOGLEVEL)
    thisHandler.setFormatter(MyFormatterStream())
    logging.root.addHandler(thisHandler)
    logging.getLogger("httpx").setLevel(logging.WARNING)


sys.excepthook = log_exceptions
