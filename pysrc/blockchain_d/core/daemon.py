from .blockchain import BlockChain
from ..exceptions import ProcessIDNotFound
from ..utils.logger import Log, LOGFILE

from typing import Any
from os import getpid, unlink, system as run, listdir
from os.path import join, expanduser, exists
import socket, pickle, sys



# logger
logger = Log().logger

class Daemon:
    def __init__(self, port: int, host: Any = 'localhost', blockchain_difficulty: int = 2):
        """
        ##### `Create a Daemon using this class`
        """
        self.difficulty = blockchain_difficulty
        self.host = host
        self.port = port

        # set config directory and log file
        self.config = join(expanduser('~'), '.bcd')
        self.logfile = join(self.config, 'logs.log')
    
    def load(self) -> None:
        # if exists log file, check if the logs is more than 1000 lines
        # if it is, delete the contents
        if exists(self.logfile):
            with open(self.logfile, 'r+') as log_ref:
                count = len(log_ref.readlines())
            
            if count > 1000:
                unlink(self.logfile)
        
        with BlockChain(self.difficulty) as blockchain:
            logger.info("BlockChain server Online.", False)
            logger.debug(f"ProcessID: {getpid()}", False)
            logger.debug(f"Listening @port {self.port}", False)
            # at this point it has loaded and checked for any backup possible.
            # it should now be on the lookout for message on a port
            while True: # run continuously
                # set request to none
                request = None
                # while request is None,
                while request == None:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                        server.bind((self.host, self.port))
                        server.listen()

                        conn, addr = server.accept()
                        with conn:
                            data = conn.recv(3072)
                            if data:
                                request = pickle.loads(data)
                            else:
                                continue
                
                # the loop will break once the request is recieved
                # request will strictly be of the form:
                # {
                #  "type:" either of 'add', 'fetch', 'backup',
                #  ... different for different type
                #  'add' will have these: location (str), encryption (bool-str), password: (str-None)
                #  'fetch' will have these: to (str), filename (str), password (str-None)
                #  'backup' will have these: location (str)
                #  'send-ftp' will have these: host, login, filename, password
                # }

                try:
                    # for `add` request
                    if request['type'] == 'add':
                        # get encryption value
                        password = None
                        if request['encryption'].lower() == "true":
                            encryption = True
                        else:
                            encryption = False
                        
                        # if encryption is true, get password
                        if encryption:
                            if request['password'].lower() != "none":
                                password = request['password']
                            else:
                                password = None
                        
                        # add it to the blockchain
                        blockchain.add(file_loc=request['location'], encryption=encryption, password=None if password == None else password.encode('ascii'))
                        logger.info(f"Added {request['location']} to blockchain.", False)
                        logger.debug(f"Total Available: {blockchain.generator.list()}", False)
                    elif request['type'] == 'fetch':
                        # resolve password
                        if request['password'].lower() == "none":
                            password = None
                        else:
                            password = request['password'].encode('ascii')
                        
                        # fetch request
                        if blockchain.fetch(request['filename'], request['to'], password):
                            logger.debug(f"fetched {request['filename']} to {join(request['to'], request['filename'])}.", False)
                        else:
                            logger.err(f"Failed to get {request['filename']} from the blockchain.", False)
                            logger.debug(f"Files currently on the blockchain: {blockchain.generator.list()}", False)
                    elif request['type'] == 'backup':
                        blockchain.generator.exit_protocol(request['location'])
                        logger.info(f"Backup created at: {request['location']}", False)
                        # get currently available backups as debug
                        logger.debug(f"Available Backups: {sort_and_return_backups(self.config, "bcDaemon_", "_", 1)}", False)
                    elif request["type"] == "list":
                        logger.debug(f"{blockchain.generator.list()}", False)
                    elif request["type"] == "send-ftp":
                        if request["password"].lower() == "none":
                            password = None
                        else:
                            password = request["password"].encode('ascii')
                        
                        host = request['host']
                        login = request['login']
                        filename = request['filename']

                        if blockchain.send_ftp(filename, host, login, password):
                            logger.debug(f"sent {filename} to {host}.", False)
                        else:
                            logger.debug(f"Failed to send {filename} to {host}")
                except Exception as e:
                    logger.err(f"Exception Occured: {e}.", False)


# ---------------------------------- RESERVED -------------------------------
def stop():
    # read the lines from log file
    with open(LOGFILE, 'r+') as log_ref:
        # get it in reverse order
        log_contents = log_ref.readlines()[::-1]
    
    # check for 'ProcessID' in the latest lines
    # set a default None value
    process_id = None
    for line in log_contents:
        if 'ProcessID' in line:
            # replace '\n' and split with whitespaces
            parts = line.replace('\n', '').split(' ')
            process_id = int(parts[-1]) # get the last value, i.e. process id
            break
    
    # create a backup before leaving - check if needed
    run(f"daemon -b {join(expanduser('~'), '.bcd')}")
    
    if process_id == None:
        logger.err(f"Failed to get process ID from logs, Check the process ID from the logs@{LOGFILE} and kill it. Or restart the system to terminate.", False)
    else:
        logger.info(f"Stopped daemon@{process_id}", False)
        run(f"kill {process_id}")

def get_port_number_from_logs() -> int:
    # read the lines from log_file
    with open(LOGFILE, 'r+') as log_ref:
        log_contents = log_ref.readlines()[::-1] # reverse it
    
    # check for 'Listening' in the latest lines
    # set a default value as default (3000)
    port_num = None # default

    for line in log_contents:
        if 'Listening' in line:
            # replace '\n' and split with whitespaces
            parts = line.replace('\n', '').split(' ')
            port_num = int(parts[-1]) # get the last value
            break
    
    if port_num == None:
        # it will be there in the logs, else it is not running.
        print("Either the logs have been deleted in which case you should restart your computer or the daemon is not online.")
        sys.exit(1)
    else:
        return port_num

def sort_and_return_backups(dir: str, prefix: str, splitter: str, split_key_index: int) -> list[str]:
    allfiles = listdir(dir)
    files = []
    for file in allfiles:
        if file.startswith(prefix):
            files.append(file)
    
    return list(sorted(files, reverse=True, key=lambda x: int(x.split(splitter)[split_key_index])))
