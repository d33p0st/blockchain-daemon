from looger.loglib import Logger
from os.path import join, expanduser
from os import makedirs

LOGFILE = join(expanduser('~'), '.bcd', 'logs.log')
CONFIG = join(expanduser('~'), '.bcd')

class Log:
    def __init__(self) -> None:
        makedirs(CONFIG, exist_ok=True)
        self.Logger = Logger(LOGFILE)
    
    @property
    def logger(self):
        return self.Logger