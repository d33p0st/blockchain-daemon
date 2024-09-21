from argpi import ArgumentDescription, Arguments as _, FetchType

class Arguments:
    def __init__(self) -> None:
        self.arguments = _().__capture__()

        # help command
        self.arguments.__add__(
            "--help",
            ArgumentDescription()
                .name("help")
                .description("shows help and exits")
                .shorthand("-h")
        )

        # debug command
        self.arguments.__add__(
            "--debug",
            ArgumentDescription()
                .name("debug")
                .description("helps debug daemon")
                .shorthand("-d")
        )

        # length
        self.arguments.__add__(
            "--list",
            ArgumentDescription().shorthand("-list")
        )

        # launch command
        self.arguments.__add__(
            "--launch",
            ArgumentDescription()
                .name("launch")
                .description("Launches the Blockchain Daemon")
                .shorthand("-l")
        )

        # launch sub command - difficulty
        self.arguments.__add__(
            "--difficulty",
            ArgumentDescription()
                .name("difficulty")
                .description("sets difficulty")
                .shorthand("-diff")
        )

        # launch sub command - port
        self.arguments.__add__(
            "--port",
            ArgumentDescription()
                .name("port")
                .description("sets port of the daemon")
                .shorthand("-p")
        )

        # launch sub command - logs
        self.arguments.__add__(
            "--live-log",
            ArgumentDescription()
                .name("live logs")
                .description("show live logs")
                .shorthand("-log")
        )

        # stop command
        self.arguments.__add__(
            "--stop",
            ArgumentDescription()
                .name("stop")
                .description("Stops the server after creating a backup")
                .shorthand("-s")
        )

        # add command
        self.arguments.__add__(
            "--add",
            ArgumentDescription()
                .name("add")
                .description("adds a file to blockchain!")
                .shorthand("-a")
        )

        # add sub command - encrypted
        self.arguments.__add__(
            "--encrypted",
            ArgumentDescription()
                .name("encrypted flag")
                .description("sets encryption as true")
                .shorthand("-enc")
        )

        # fetch command
        self.arguments.__add__(
            "--fetch",
            ArgumentDescription()
                .name("fetch")
                .description("fetches content from the blockchain")
                .shorthand("-f")
        )

        # add and fetch sub command - password
        self.arguments.__add__(
            "--password",
            ArgumentDescription()
                .name("password")
                .description("sets password for operation.")
                .shorthand("-pass")
        )

        # fetch sub command destination
        self.arguments.__add__(
            "--destination",
            ArgumentDescription()
                .name("destination")
                .description("sets destination of fetching.")
                .shorthand("-to")
        )

        # backup command
        self.arguments.__add__(
            "--backup",
            ArgumentDescription()
                .name("backup")
                .description("creates backup")
                .shorthand("-b")
        )

        # force backup
        self.arguments.__add__(
            "--force-backup",
            ArgumentDescription().shorthand("-fb")
        )

        # export to ftp
        self.arguments.__add__(
            "--to-ftp",
            ArgumentDescription()
                .name("ftp")
                .description("export to ftp server")
                .shorthand("-ftp")
        )

        # FTP host
        self.arguments.__add__(
            "--host",
            ArgumentDescription().shorthand("-host")
        )

        # FTP user info -> username@password:port
        self.arguments.__add__(
            "--login",
            ArgumentDescription().shorthand('-login')
        )

        # gui command
        self.arguments.__add__(
            "--gui",
            ArgumentDescription().shorthand('-g')
        )

        self.arguments.__analyse__()
    
    @property
    def get(self) -> _:
        return self.arguments
    
    @property
    def get_fetchtype(self):
        return FetchType