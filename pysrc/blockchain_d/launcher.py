from .core.daemon import Daemon
from .exceptions import PortNumberNotProvided
from sys import argv

# Parameters:
# 1. port (mandatory)
# 2. difficulty (optional)

def main():
    try:
        port = int(argv[1])
    except IndexError:
        raise PortNumberNotProvided("Port Number is mandatory. perhaps someone modified the code, try re-installing. This is not supposed to happen.")
    
    try:
        difficulty = int(argv[2])
    except IndexError:
        difficulty = 2
    
    Daemon(port=port, blockchain_difficulty=difficulty).load()