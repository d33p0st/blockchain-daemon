
from ..rust import BlockChainGenerator
from ..exceptions import PasswordNotFound
from os.path import join as joinPath, expanduser, basename, expandvars
from os import makedirs, unlink, listdir, getcwd, system

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.exceptions import InvalidSignature
from cryptography.fernet import InvalidToken
from base64 import urlsafe_b64encode as b_encode
from tkinter.messagebox import askokcancel
from ..utils.logger import Log
import tkinter as tk
import ftplib
import io

# setup logger
logger = Log().logger

class BlockChain:
    def __init__(self, difficulty: int = 2) -> None:
        self.difficulty = difficulty
    
    def __enter__(self) -> 'BlockChain':
        # as soon as the context is in place, define and make config dir.
        self.config = joinPath(expanduser('~'), '.bcd')
        makedirs(self.config, exist_ok=True)
        logger.info(f"checking config dir: {self.config}", False)

        # create a generator object
        self.generator = BlockChainGenerator(self.difficulty)
        logger.info(f"creating blockchain from scratch ...", False)

        # check for backup and load it
        self.generator.load_backup(self.config)
        logger.info(f"looking for backups ...", False)

        # delete all backups
        for file in listdir(self.config):
            if file.startswith("bcDaemon_"):
                unlink(joinPath(self.config, file))
        
        logger.info("deleting any obsolete backups dangling around ...", False)

        # return self
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        # on exit, create a new backup
        logger.info("Exit triggered, preparing backup", False)
        self.generator.exit_protocol(self.config)

    def add(self, file_loc: str, encryption: bool = False, password: bytes | None = None) -> None:
        """##### `Add a block into the blockchain.`

        ### Parameters
        `file_loc (str):` location of the file to be added to the blockchain.
        
        `encryption (bool):` By default encryption is OFF. Set it to True for encryption. A password will be needed encoded in ascii (bytes).

        `password (bytes | None):` By default encryption will be False and password will be set to None. If encryption is set to True, Set password of your choice encoded in ascii. (bytes)

        ### Usage
        >>> from bc_daemon.core import BlockChain
        >>> with BlockChain(difficulty=4) as bc:
        ...     bc.add("~/abc.txt", True, "1234".encode('ascii'))
        """
        logger.info(f"Preparing to {basename(file_loc)}", False)
        # expand the path
        file_loc = expanduser(expandvars(file_loc))
        if file_loc.startswith("./"):
            file_loc = joinPath(getcwd(), file_loc[2:])
        # get filename from it
        filename = basename(file_loc)
        # get the data in bytes
        with open(file_loc, 'rb+') as file_ref:
            file_contents = file_ref.read()
        
        # if encryption is needed, create encryption parameters and encrypt the data
        # but first check if encryption is try and password is not provided.
        if encryption:
            logger.info(f"Encryption is set as ON for file: {filename}", False)
            if password == None:
                raise PasswordNotFound("\'encryption\' parameter is set to True but no password was provided.")
            
            __kdf = PBKDF2HMAC(
                algorithm=SHA256(),
                length=32,
                salt="BlockChain Generator personal salt. mmmmm its so salty. wish it was a bit sweet too".encode("ascii"),
                iterations=500000,
            )

            __fernet = Fernet(b_encode(__kdf.derive(password)))

            file_contents = __fernet.encrypt(file_contents)
            logger.info(f"Encrypted Contents of file {filename}", False)
        
        # once everything is ready, call the add_block method from rust bin
        self.generator.add_block(filename, file_loc, file_contents, encryption)
    
    @property
    def length(self) -> int:
        """`returns length of the blockchain`"""
        # return length of the chain
        return self.generator.len()
    
    def fetch(self, filename: str, to: str, password: bytes | None) -> bool:
        """##### `creates a new file at given directory from the blockchain`

        ### Parameters
        `filename (str):` the filename of the file.

        `to (str):` the directory where the file will be created.
        """
        # write the contents from the block chain to the file.
        # print(filename, to)
        logger.info(f"Trying to find {filename} on blockchain", False)
        self.generator.iterate_and_write(filename, joinPath(expanduser(expandvars(to)), filename))
        
        # the contents needs to be read again and decrypted.
        if password != None:
            with open(joinPath(expanduser(expandvars(to)), filename), 'rb+') as file_ref:
                contents = file_ref.read()
            
            __kdf = PBKDF2HMAC(
                algorithm=SHA256(),
                length=32,
                salt="BlockChain Generator personal salt. mmmmm its so salty. wish it was a bit sweet too".encode("ascii"),
                iterations=500000,
            )

            __fernet = Fernet(b_encode(__kdf.derive(password)))

            try:
                # try to decrypt with the given key
                contents = __fernet.decrypt(contents)

                # write the contents
                with open(joinPath(expanduser(expandvars(to)), filename), 'wb+') as file_ref:
                    file_ref.write(contents)
                return True
            except (InvalidToken, InvalidSignature):
                # if it fails, show a warning dialog and record the response
                root = tk.Tk()
                root.withdraw()
                response = askokcancel("Warning!", "The given password did not match.")
                # if the user pressed ok, delete the generated file.
                if response:
                    unlink(joinPath(expanduser(expandvars(to)), filename))
                    return False
                else:
                    # if the user pressed cancel, keep the encrypted file.
                    return False
        else:
            return True
    
    def send_ftp(self, filename: str, host: str, login: str, password: bytes | None) -> bool:
        # write the contents from the block chain to the file.
        # print(filename, to)
        logger.info(f"Trying to find {filename} on blockchain", False)
        data = self.generator.iterate_and_find(filename)
    
        # parse login
        username = login.split('@')[0].strip()
        passd = login.split('@')[-1].split(':')[0].strip()
        port = login.split('@')[-1].split(":")[-1].strip()
        
        # the contents needs to be read again and decrypted.
        if password != None:
            __kdf = PBKDF2HMAC(
                algorithm=SHA256(),
                length=32,
                salt="BlockChain Generator personal salt. mmmmm its so salty. wish it was a bit sweet too".encode("ascii"),
                iterations=500000,
            )

            __fernet = Fernet(b_encode(__kdf.derive(password)))

            try:
                # try to decrypt with the given key
                contents = __fernet.decrypt(data)

                try:
                    ftp = ftplib.FTP()
                    logger.info(ftp.connect(host, int(port)), False)
                    logger.info(ftp.login(username, passd), False)
                    with io.BytesIO(contents) as ref:
                        logger.info(ftp.storbinary(f"STOR {filename}", ref), False)
                    logger.debug(ftp.retrlines("LIST"), False)
                    logger.info(ftp.quit(), False)
                    return True
                except Exception as e:
                    logger.info(e, False)
                    return False
            except (InvalidToken, InvalidSignature):
                logger.err("Failed to decrypt File. Returing encrypted.", False)
                try:
                    ftp = ftplib.FTP()
                    logger.info(ftp.connect(host, int(port)), False)
                    logger.info(ftp.login(username, passd), False)
                    with io.BytesIO(data) as ref:
                        logger.info(ftp.storbinary(f"STOR {filename}", ref), False)
                    logger.debug(ftp.retrlines("LIST"), False)
                    logger.info(ftp.quit(), False)
                    return True
                except Exception as e:
                    logger.info(e, False)
                    return False
        else:
            try:
                ftp = ftplib.FTP()
                logger.info(ftp.connect(host, int(port)), False)
                logger.info(ftp.login(username, passd), False)
                with io.BytesIO(data) as ref:
                    logger.info(ftp.storbinary(f"STOR {filename}", ref), False)
                logger.debug(ftp.retrlines("LIST"), False)
                logger.info(ftp.quit(), False)
                return True
            except Exception as e:
                logger.info(e, False)
                return False

        
    @property
    def is_valid(self) -> bool:
        """Checks if the current blockchain is valid or not."""
        # return True/False
        logger.info("Checking blockchain for validity ...")
        return self.generator.valid()