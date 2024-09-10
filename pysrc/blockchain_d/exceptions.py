# blockchain.py
# exception: if encryption is true but password not given
# NOTE: this will be shared by driver.py
class PasswordNotFound(Exception):
    pass

# launcher.py
# warning
class PortNumberNotProvided(Warning):
    pass

# driver.py
# exception: OS not supported Yet
class OperatingSystemNotSupported(Exception):
    pass

# daemon.py
# exception: if process_id is not found in the logs
class ProcessIDNotFound(Exception):
    pass