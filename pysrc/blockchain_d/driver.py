from .core.daemon import Daemon, stop as stop_daemon, get_port_number_from_logs
from .utils.arguments import Arguments
from .exceptions import OperatingSystemNotSupported, PasswordNotFound, PortNumberNotProvided, FTPHostErr, FTPLoginErr

from os import system as run, makedirs, getcwd
from os.path import join, expanduser
from platform import system as os_
from colorama import init as colorize, Fore as _
import sys, pickle, socket, warnings

class Driver:
    def __init__(self):
        # get arguments
        # at this point all arguments are defined and parsed
        self.arguments = Arguments().get
        # get FetchType enum of argpi
        self.fetchtype = Arguments().get_fetchtype
        # get operating system
        self.os = os_()
        # set config directory
        self.config = join(expanduser('~'), '.bcd')
        # make it if not there
        makedirs(self.config, exist_ok=True)
    
    @property
    def live_logs(self):
        try:
            done = []
            while True:
                with open(join(self.config, 'logs.log'), 'r+') as log_ref:
                    contents = log_ref.read()
                
                for line in contents:
                    if line not in done:
                        print(line.replace('\n', ''))
                        done.append(line)
        except KeyboardInterrupt:
            sys.exit(0)
    
    def start(self):
        # handle arguments
        # debug
        if self.arguments.__there__("--debug"):
            # if port number is not provided raise an error.
            if not self.arguments.__there__("--port"):
                print(f"{_.YELLOW}WARNING:{_.RESET} port number is not provided. Defaulting to 3000. port number should be provided!")
                port = "3000"
            else:
                port: str = self.arguments.__fetch__("--port", self.fetchtype.SINGULAR)

            # if difficulty is not provided no issue
            # run only on macos and linux
            if self.os == "Darwin" or self.os == "Linux":
                diff = '' if not self.arguments.__there__('--difficulty') else self.arguments.__fetch__('--difficulty', self.fetchtype.SINGULAR)
                if diff != '':
                    run(f"daemon-launch {port} {diff}")
                else:
                    run(f"daemon-launch {port}")

                # check for live log
                if self.arguments.__there__("-log"):
                    # show logs
                    self.live_logs
        elif self.arguments.__there__("--list"):
            headers = {
                "type": "list"
            }

            # serialize headers
            headers = pickle.dumps(headers)

            # send it to daemon
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect(('localhost', get_port_number_from_logs()))
                client.sendall(headers)

        # start with the launch comamnd
        elif self.arguments.__there__("--launch"):
            # if port number is not provided raise an error.
            if not self.arguments.__there__("--port"):
                print(f"{_.YELLOW}WARNING:{_.RESET} port number is not provided. Defaulting to 3000. port number should be provided!")
                port = "3000"
            else:
                port: str = self.arguments.__fetch__("--port", self.fetchtype.SINGULAR)
            
            # if difficulty is not provided no issue
            # run only on macos and linux
            if self.os == "Darwin" or self.os == "Linux":
                diff = '' if not self.arguments.__there__('--difficulty') else self.arguments.__fetch__('--difficulty', self.fetchtype.SINGULAR)
                if diff != '':
                    run(f"nohup daemon-launch {port} {diff} > {join(self.config, 'logs.log')} 2>&1 &")
                else:
                    run(f"nohup daemon-launch {port} > {join(self.config, 'logs.log')} 2>&1 &")

                # check for live log
                if self.arguments.__there__("-log"):
                    # show logs
                    self.live_logs
            else:
                raise OperatingSystemNotSupported("This os will be supported soon!")
        # then for stop
        elif self.arguments.__there__("--stop"):
            # stop the daemon
            stop_daemon()
        # then for add command
        elif self.arguments.__there__('--add'):
            # get location from arguments
            location: str = self.arguments.__fetch__("--add", self.fetchtype.SINGULAR)
            # set encryption
            if not self.arguments.__there__("--encrypted"):
                encryption = "false"
                password = "none"
            else:
                encryption = "true"
                if not self.arguments.__there__("--password"):
                    raise PasswordNotFound("Encryption is set to True but no password is set.")
                else:
                    # get it from the arguments
                    password: str = self.arguments.__fetch__("--password", self.fetchtype.SINGULAR)
            
            # create headers
            headers = {
                "type": "add",
                "location": location,
                "encryption": encryption,
                "password": password,
            }

            # serialize headers
            headers = pickle.dumps(headers)

            # send it to daemon
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect(('localhost', get_port_number_from_logs()))
                client.sendall(headers)
        # then for fetch command
        elif self.arguments.__there__('--fetch'):
            # get filename
            filename: str = self.arguments.__fetch__('--fetch', self.fetchtype.SINGULAR)
            # check if destination is there
            if not self.arguments.__there__('--destination'):
                # use current directory if not there
                to = getcwd()
            else:
                to: str = self.arguments.__fetch__('--destination', self.fetchtype.SINGULAR)
            
            # check password
            if not self.arguments.__there__('--password'):
                password = "none"
            else:
                password: str = self.arguments.__fetch__('--password', self.fetchtype.SINGULAR)
            
            # create headers
            headers = {
                "type": "fetch",
                "to": to,
                "filename": filename,
                "password": password,
            }

            # serialize headers
            headers = pickle.dumps(headers)

            # send it to daemon
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect(('localhost', get_port_number_from_logs()))
                client.sendall(headers)
        # then for backup
        elif self.arguments.__there__("--backup"):
            # get location
            location: str = self.arguments.__fetch__("--backup", self.fetchtype.SINGULAR)

            # create headers
            headers = {
                "type": 'backup',
                "location": location,
            }

            # serialize headers
            headers = pickle.dumps(headers)

            # send it to daemon
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect(('localhost', get_port_number_from_logs()))
                client.sendall(headers)
        elif self.arguments.__there__("--to-ftp"):
            # get filename from the argument itself
            filename: str = self.arguments.__fetch__("--to-ftp", self.fetchtype.SINGULAR)

            # check host
            if not self.arguments.__there__("--host"):
                raise FTPHostErr("Host is required to export to FTP")
            else:
                host: str = self.arguments.__fetch__("--host", self.fetchtype.SINGULAR)
            
            # check login
            if not self.arguments.__there__("--login"):
                raise FTPLoginErr("Login info is not provided. Format: username@password:port")
            else:
                login: str = self.arguments.__fetch__("--login", self.fetchtype.SINGULAR)
            
            # check password
            if not self.arguments.__there__("--password"):
                password = "none"
            else:
                password: str = self.arguments.__fetch__("--password", self.fetchtype.SINGULAR)
            
            headers = {
                "type": "send-ftp",
                "host": host,
                "login": login,
                "password": password,
                "filename": filename
            }

            headers = pickle.dumps(headers)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect(('localhost', get_port_number_from_logs()))
                client.sendall(headers)
        else:
            print("daemon: argument error. check help.")
            sys.exit(1)

def main():
    driver = Driver()
    driver.start()