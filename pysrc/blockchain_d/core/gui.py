from tkinter import ttk
from tkinter import *
from tkinter import filedialog

from ..exceptions import ButtonErr
from ..utils.gui.ansi_handler import ANSIText
from ..utils.gui.icon import Icon
import threading, os, time, subprocess, pyperclip

class DaemonGUI:
    LOGFILE = os.path.join(os.path.expanduser('~'), '.bcd', 'logs.log')

    def __init__(self, master: Tk, icon: str | None = None) -> None:
        # get master
        self.master = master

        # set icon
        Icon().set(self.master)

        # set title to BlockChain Daemon
        self.master.title("BlockChain Detached Controller")

        # set geometry
        self.master.geometry('530x300+400+280')

        # enclosing frame for parent
        self.enclosingFrame = ttk.Frame(self.master)
        self.enclosingFrame.pack(fill=BOTH, expand=True)

        # logging event trigger
        self.logging = threading.Event()
        self.log_thread: threading.Thread | None = None

        # setup exit protocol
        self.master.protocol('WM_DELETE_WINDOW', self.close)
    
    @staticmethod
    def makeroot() -> Tk:
        return Tk()
    
    def make_initial_screen(self):
        # create a notebook
        # notebook -|
        #           | - Blockchain (start/stop)
        #           | - Add
        #           | - Fetch (local)
        #           | - FTP
        #           | - List
        #           | - Backup
        #           | - logs

        # define empty notebook
        self.tabs = ttk.Notebook(self.enclosingFrame)
        self.tabs.pack(fill=BOTH, expand=True)

        # The actual tabs
        self.blockchainTab = ttk.Frame(self.tabs)
        self.addTab = ttk.Frame(self.tabs)
        self.fetchTab = ttk.Frame(self.tabs)
        self.ftpTab = ttk.Frame(self.tabs)
        self.logsTab = Frame(self.tabs)

        # Add these tabs to the notebook
        self.tabs.add(self.blockchainTab, text='BlockChain')
        self.tabs.add(self.addTab, text='Add')
        self.tabs.add(self.fetchTab, text='Fetch')
        self.tabs.add(self.ftpTab, text="FTP")
        self.tabs.add(self.logsTab, text='logs')

        # make these tabs individually
        self._make_blockchainTab()
        self._makelogsTab()
        self._make_addTab()
        self._make_fetchTab()
        self._makeFTP()
    
    def _makeFTP(self):
        # FTP Tab -|
        #          | - Filename
        #          | - Password
        #          | - host
        #          | - username
        #          | - pass
        #          | - port

        # enclosing frame for FTP Tab
        self.ftpEF = ttk.Frame(self.ftpTab)
        self.ftpEF.pack(expand=True, fill=BOTH)

        # create a label for host
        self.hostLabel = ttk.Label(self.ftpEF, text="Host:")
        self.hostLabel.place(anchor='center', relx=0.3, rely=0.15)
        # create a entry for host
        self.hostTExt = StringVar()
        self.hostEntry = ttk.Entry(self.ftpEF, width=17, textvariable=self.hostTExt)
        self.hostEntry.place(anchor='center', rely=0.15, relx=0.52)
        self.hostEntry.config(state=DISABLED)
        # add a button to paste the clipboard onto hostText
        self.hostPaste = ttk.Button(self.ftpEF, text="[Paste]", command=self.paste_host)
        self.hostPaste.place(anchor='center', rely=0.15, relx=0.81)

        # create label for username
        self.usernameLabel = ttk.Label(self.ftpEF, text="Username:")
        self.usernameLabel.place(anchor='center', relx=0.2, rely=0.26)

        # create username Entry
        self.usernameEntry_text = StringVar()
        self.usernameEntry = ttk.Entry(self.ftpEF, width=20, textvariable=self.usernameEntry_text)
        self.usernameEntry.place(anchor='center', relx=0.49, rely=0.26)
        self.usernameEntry.config(state=DISABLED)

        # create a paste button for username
        self.usernamePaste = ttk.Button(self.ftpEF, text="[Paste]", command=self.paste_username)
        self.usernamePaste.place(anchor='center', relx=0.81, rely=0.26)

        # create label for password
        self.ftpPassLabel = ttk.Label(self.ftpEF, text='Password:')
        self.ftpPassLabel.place(anchor='center', relx=0.2, rely=0.38)

        # create password entry
        self.ftpPassEntry_text = StringVar()
        self.ftpPassEntry = ttk.Entry(self.ftpEF, width=20, textvariable=self.ftpPassEntry_text, show='*')
        self.ftpPassEntry.place(anchor='center', relx=0.49, rely=0.38)
        self.ftpPassEntry.config(state=DISABLED)

        # create paste button for Password
        self.PasswordPaste = ttk.Button(self.ftpEF, text='[Paste]', command=self.paste_password)
        self.PasswordPaste.place(anchor='center', relx=0.81, rely=0.38)

        # create port label
        self.ftpPortLabel = ttk.Label(self.ftpEF, text="Port:")
        self.ftpPortLabel.place(anchor='center', relx=0.2, rely=0.5)

        # create port entry
        self.ftpPortEntry_TExt = StringVar()
        self.ftpPortEntry = ttk.Entry(self.ftpEF, width=2, textvariable=self.ftpPortEntry_TExt)
        self.ftpPortEntry_TExt.set("21")
        self.ftpPortEntry.place(anchor='center', relx=0.27, rely=0.5)
        self.ftpPortEntry.config(state=DISABLED)

        # create Filename Label
        self.ftpFilenameLabel = ttk.Label(self.ftpEF, text='Filename:')
        self.ftpFilenameLabel.place(anchor='center', relx=0.38, rely=0.5)

        # create Filename Entry
        self.ftpFilename_Text = StringVar()
        self.ftpFilenameEntry = ttk.Entry(self.ftpEF, width=15, textvariable=self.ftpFilename_Text)
        self.ftpFilenameEntry.place(anchor='center', rely=0.5, relx=0.60)

        # create checkbox for password,
        self.decrypt = BooleanVar()
        self.decrypt_Check = Checkbutton(self.ftpEF, text='Decrypt', variable=self.decrypt, command=self._decrypt_command)
        self.decrypt_Check.place(anchor='center', relx=0.5, rely=0.62)

        # create a Key Label and Entry
        self.ftpKeyLabel = ttk.Label(self.ftpEF, text='Key:')
        # self.ftpKeyLabel.place(anchor='center', relx=0.37, rely=0.75)
        self.ftpKeyEntry_text = StringVar()
        self.ftpKeyEntry = ttk.Entry(self.ftpEF, textvariable=self.ftpKeyEntry_text, width=12, show='*')
        # self.ftpKeyEntry.place(anchor='center', relx=0.53, rely=0.75)

        # Upload Button
        self.ftpUpload = ttk.Button(self.ftpEF, text='[Upload]', default='active', command=self._ftp_upload)
        self.ftpUpload.place(anchor='center', relx=0.5, rely=0.76)
    
    def clear_all_ftp(self):
        self.hostTExt.set("")
        self.usernameEntry_text.set("")
        self.ftpPassEntry_text.set("")
        self.ftpFilename_Text.set("")
        self.decrypt.set(False)
        self._decrypt_command()
        self.ftpKeyEntry_text.set("")
    
    def _ftp_upload(self):
        if self.ftpFilename_Text.get():
            filename = self.ftpFilename_Text.get()

            if self.hostTExt.get():
                host = self.hostTExt.get()

                if self.usernameEntry_text.get():
                    username = self.usernameEntry_text.get()

                    if self.ftpPassEntry_text.get():
                        password = self.ftpPassEntry_text.get()

                        port = self.ftpPortEntry_TExt.get()

                        if self.decrypt.get():
                            command = f"daemon -ftp {filename} --host {host} --login {username}@{password}:{port} --password {self.ftpKeyEntry_text.get()}"
                        else:
                            command = f"daemon -ftp {filename} --host {host} --login {username}@{password}:{port}"
                        
                        
                    else:
                        self.clear_all_ftp()
                else:
                    self.clear_all_ftp()
            
            else:
                self.clear_all_ftp()
        else:
            self.clear_all_ftp()
    
    def _decrypt_command(self):
        if self.decrypt.get():
            self.ftpKeyLabel.place(anchor='center', relx=0.37, rely=0.75)
            self.ftpKeyEntry.place(anchor='center', relx=0.53, rely=0.75)
            self.ftpUpload.place(anchor='center', relx=0.5, rely=0.87)
        else:
            self.ftpKeyLabel.place_forget()
            self.ftpKeyEntry.place_forget()
            self.ftpUpload.place(anchor='center', relx=0.5, rely=0.76)

    def paste_password(self):
        self.ftpPassEntry_text.set(pyperclip.paste())
    
    def paste_username(self):
        self.usernameEntry_text.set(pyperclip.paste())
    
    def paste_host(self):
        self.hostTExt.set(pyperclip.paste())
    
    
    def _make_fetchTab(self):
        # Fetch Tab -|
        #            | - Filename
        #            | - to
        #            | - password

        # enclosing Frame for Fetch Tab
        self.fEF = ttk.Frame(self.fetchTab)
        self.fEF.pack(expand=True, fill=BOTH)

        # create to-
        self.fToLabel = ttk.Label(self.fEF, text="Destination:")
        self.fToLabel.place(anchor='center', relx=0.2, rely=0.2)
        self.fTo_text = StringVar()
        self.fTo = ttk.Entry(self.fEF, textvariable=self.fTo_text, width=25)
        self.fTo_text.set("Destination Not Set.")
        self.fTo.config(state=DISABLED)
        self.fTo.place(anchor='center', relx=0.55, rely=0.2)

        # bind to - to a dialog box
        # self.fTo.bind("<Button-1>", self.select_destination)

        # select button
        self.fSelectButton = ttk.Button(self.fEF, text="[Select]", default=ACTIVE, command=self.select_destination)
        self.fSelectButton.place(anchor='center', rely=0.2, relx=0.90)

        # create a text box to add filename
        self.fFilename_Label = ttk.Label(self.fEF, text="Filename:")
        self.fFilename_Label.place(anchor='center', rely=0.35, relx=0.31)
        self.fFilename_text = StringVar()
        self.fFilename = ttk.Entry(self.fEF, width=20, textvariable=self.fFilename_text)
        # self.fFilename_text.set("Enter Filename (Click)")
        # self.fFilename.config(state=DISABLED)
        self.fFilename.place(anchor='center', relx=0.6, rely=0.35)

        # bind the filename to click and edit
        # self.fFilename.bind("<Button-1>", self.filename_handle)
        
        self.passLabel = ttk.Label(self.fEF, text="Password:")
        self.passLabel.place(anchor='center', relx=0.31, rely=0.48)
        self.pVar = StringVar()
        self.password = ttk.Entry(self.fEF, width=20, textvariable=self.pVar, show="*")
        # self.pVar.set("Enter Password (Click)")
        # self.password.config(state=DISABLED)
        self.password.place(anchor='center', relx=0.6, rely=0.48)

        # bind the password to click and edit
        # self.password.bind("<Button-1>", self.pass_handle)

        # add status label
        # self.fStatusVar = StringVar()
        # self.fStatusVar.set("asdas")
        self.fStatus = ttk.Label(self.fEF, text="")
        self.fStatus.place(anchor='center', relx=0.5, rely=0.6)

        # add button
        self.FetchButton = ttk.Button(self.fEF, text="[FETCH]", command=self._fetchButton)
        self.FetchButton.place(anchor='center', relx=0.5, rely=0.72)
    
    def _fetchButton(self):
        if self.log_thread is not None and self.log_thread.is_alive():
            if self.fTo_text.get().strip():
                dest = self.fTo_text.get().strip()
                if self.fFilename_text.get().strip():
                    filename = self.fFilename_text.get().strip()
                    
                    # command
                    command = f"daemon --fetch {filename} -to {dest} {'--password' if self.pVar.get().strip() else ''} {self.pVar.get().strip() if self.pVar.get().strip() else ''}"
                    def do_fetch(command, logfile, clear1: StringVar, clear2: StringVar, clear3: StringVar):
                        with open(logfile, 'r') as ref:
                            ref.seek(0,2)

                            subprocess.Popen(command.split(' ')).wait()

                            while True:
                                line = ref.readline()
                                if line and 'fetched' in line:
                                    clear1.set("Destination Not Set.")
                                    clear2.set("")
                                    clear3.set("")
                                    break

                                time.sleep(1)
                    
                    fetch_thread = threading.Thread(target=do_fetch, args=(command, self.LOGFILE, self.fTo_text, self.fFilename_text, self.pVar))
                    fetch_thread.start()
                else:
                    self.fStatus.after(0, lambda: self.fStatus.config(text="Please Enter Filename!"))
                    self.fStatus.after(3000, lambda:self.fStatus.config(text=""))

            else:
                self.fStatus.after(0, lambda: self.fStatus.config(text="Please Select Destination!"))
                self.fStatus.after(3000, lambda:self.fStatus.config(text=""))
            
        else:
            self.not_running_warning(self.fStatus)
    
    def select_destination(self):
        if self.log_thread is not None and self.log_thread.is_alive():
            destination = filedialog.askdirectory(initialdir=os.getcwd(), mustexist=True, title="Select a Destination")
            if destination:
                self.fTo.config(state=NORMAL)
                self.fTo_text.set(destination)
                self.fTo.config(state=DISABLED)
        else:
            self.not_running_warning(self.fStatus)
    
    def _make_addTab(self):
        # Add Tab -|
        #          | - File location Selector, Label
        #          | - Encryption Check Box
        #          | - Hidden Password label and field

        # enclosing frame for Add Tab
        self.aEF = ttk.Frame(self.addTab)
        self.aEF.pack(expand=True, fill=BOTH)

        # create file-name label
        self.aFileEntry_text = StringVar()
        self.aFileNameLabel = ttk.Entry(self.aEF, textvariable=self.aFileEntry_text, width=40)
        self.aFileEntry_text.set("No File Selected. (Click Here)")
        self.aFileNameLabel.config(state=DISABLED)
        self.aFileNameLabel.place(anchor='center', relx=0.5, rely=0.2)

        # create file-dialog button
        self.aFileNameLabel.bind("<Button-1>", self.select_file)

        # create a checkbox
        self.encrypted = BooleanVar()
        self.encryption_box = Checkbutton(self.aEF, text="Encrypt", variable=self.encrypted, command=self.show_password)
        self.encryption_box.place(anchor='center', relx=0.5, rely=0.41)

        # create a status label
        self.aStatus = ttk.Label(self.aEF, text="")
        self.aStatus.place(anchor='center', relx=0.5, rely=0.56)

        # create a password label and entry
        self.aPasswordEntry_text = StringVar()
        self.aPasswordLabel = ttk.Label(self.aEF, text="Password:")
        self.aPasswordEntry = ttk.Entry(self.aEF, width=12, show="*", textvariable=self.aPasswordEntry_text)

        # create an Add Button
        self.aButton = ttk.Button(self.aEF, text="[ADD]", default='active', command=self._addButton)
        self.aButton.place(anchor='center', relx=0.5, rely=0.69)
    
    def _addButton(self):
        if self.log_thread is not None and self.log_thread.is_alive():
            def add_file(locations: str, encryption: bool, password: str, clear1: StringVar, bool1: BooleanVar, clear2: StringVar, callab):
                for loc in locations:
                    command = f"daemon -a {loc} {'-enc' if encryption else ''} {'--password' if encryption else ''} {password if encryption else ''}"
                    subprocess.Popen(command.split(' ')).wait()
                    # check in the logs for the last line - 'Total Available' and 'filename'
                    with open(self.LOGFILE, 'r') as logref:
                        logref.seek(0, 2)

                        while True:
                            line = logref.readline()
                            if line:
                                if 'Total Available' in line and f"{os.path.basename(loc)}\']" in line:
                                    clear1.set("No File Selected. (Click Here)")
                                    bool1.set(False)
                                    clear2.set("")
                                    callab()
                                    break
                            
                            time.sleep(2)
            
            self.add_thread = threading.Thread(target=add_file, args=(self.aFileEntry_text.get().split(';'), self.encrypted.get(), self.aPasswordEntry.get() if self.encrypted.get() else '', self.aFileEntry_text, self.encrypted, self.aPasswordEntry_text, self.show_password))
            self.add_thread.start()
        else:
            self.not_running_warning(self.aStatus)
    
    def show_password(self):
        if self.encrypted.get():
            self.aPasswordLabel.place(anchor='center', relx=0.36, rely=0.69)
            self.aPasswordEntry.place(anchor='center', relx=0.58, rely=0.69)
            self.aButton.place(anchor='center', relx=0.5, rely=0.83)
        else:
            self.aPasswordLabel.place_forget()
            self.aPasswordEntry.place_forget()
            self.aButton.place(anchor='center', relx=0.5, rely=0.69)
    
    def not_running_warning(self, obj: ttk.Label):
        obj.after(0, lambda: obj.config(text="Blockchain Not Running!"))
        obj.after(3000, lambda: obj.config(text=""))
    
    def select_file(self, event):
        if self.log_thread is not None and self.log_thread.is_alive():
            filepath = filedialog.askopenfilenames()
            self.aFilePaths = None
            if len(filepath) > 0:
                self.aFilePaths = filepath
                self.aFileNameLabel.config(state=NORMAL)
                self.aFileEntry_text.set(";".join(filepath))
                self.aFileNameLabel.config(state=DISABLED)
        else:
            self.not_running_warning(self.aStatus)
    
    def _makelogsTab(self):
        # enclosing frame for Logs Tab
        self.lEF = Frame(self.logsTab)
        self.lEF.pack(fill=BOTH, expand=True)

        # create a TExt
        self.log_area = ANSIText(self.lEF, wrap="word")
        self.log_area.pack(fill=BOTH, expand=True)
        self.log_area.after(0, lambda: self.log_area.insert_text_with_ansi("BlockChain is not Running."))
        self.log_area.config(state=DISABLED)

    def _make_blockchainTab(self):
        # Blockchain Tab -|
        #                 | - Title
        #                 | - Port
        #                 | - start button

        # enclosing frame for Blockchain Tab
        self.bEF = ttk.Frame(self.blockchainTab)
        self.bEF.pack(expand=True, fill=BOTH)

        # set intro
        intro = "BlockChain"

        # set label
        self.bLabel1 = ttk.Label(self.bEF, text=intro, font=('Verdana', 18))
        self.bLabel1.place(anchor='center', relx=0.5, rely=0.25)

        # create port label
        self.bPortLabel = ttk.Label(self.bEF, text="port:", font=('Verdana'))
        self.bPortLabel.place(anchor='center', relx=0.4, rely=0.4)

        # create port entry
        self.bPortEntry_text = StringVar()
        self.bPortEntry = ttk.Entry(self.bEF, textvariable=self.bPortEntry_text, width=10)
        self.bPortEntry.place(anchor='center', relx=0.56, rely=0.4)
        self.bPortEntry_text.set("3000")

        # start button
        self.blockchainButton = ttk.Button(self.bEF, text='[START]', command=self._blockchainBtn, default='active')
        self.blockchainButton.place(anchor='center', relx=0.5, rely=0.55)
    
    def _blockchainBtn(self):
        # define a start and stop function
        def start(port: str):
            os.system(f"daemon -l --port {port}")
        
        def stop():
            os.system(f"daemon -b {os.path.join(os.path.expanduser('~'), '.bcd')}")
            try:
                os.system("daemon -s")
            except Exception:
                pass

        if self.blockchainButton.cget("text") == "[START]":
            self.bPortEntry.config(state=DISABLED)
            start_thread = threading.Thread(target=start, args=(self.bPortEntry.get().strip() if self.bPortEntry.get().strip() is not '' else '3000',))
            start_thread.start()
            start_thread.join()
            self.start_log()
            self.blockchainButton.config(text='[STOP]')

        elif self.blockchainButton.cget("text") == "[STOP]":
            stop_thread = threading.Thread(target=stop)
            stop_thread.start()
            stop_thread.join()
            self.bPortEntry.config(state=NORMAL)
            self.blockchainButton.config(text='[START]')

        else:
            raise ButtonErr("Button Malfunction.")
    
    def start_log(self):
        self.logging.clear()
        self.log_thread = None
        if self.log_thread is None or not self.log_thread.is_alive():
            self.logging.clear()
            self.log_thread = threading.Thread(target=self.log)
            self.log_thread.daemon = True
            self.log_thread.start()
    
    def stop_log(self):
        if self.log_thread is not None and self.log_thread.is_alive():
            self.logging.set()
            self.log_thread.join()
    
    def stop_log_update(self):
        with open(os.path.join(os.path.expanduser('~'), '.bcd', 'logs.log'), 'r') as logref:
            lines = logref.readlines()
        
        # clear the logs
        self.clear_log()
        
        for line in lines:
            self.log_area.after(0, self.update_log, line)
    
    def clear_log(self):
        self.log_area.config(state=NORMAL)
        self.log_area.delete("1.0", END)
        self.log_area.config(state=DISABLED)
    
    def log(self):
        self.clear_log()
        with open(self.LOGFILE, 'r') as logref:
            logref.seek(0, 2)

            while not self.logging.is_set():
                line = logref.readline()
                if line:
                    self.log_area.after(0, self.update_log, line)
                else:
                    time.sleep(1)
    
    def update_log(self, line: str):
        self.log_area.config(state=NORMAL)
        self.log_area.insert_text_with_ansi(line)
        self.log_area.see(END)
        self.log_area.config(state=DISABLED)
    
    def close(self):
        self.stop_log()
        self.master.destroy()