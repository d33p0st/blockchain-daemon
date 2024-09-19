import ftplib

class FTP(ftplib.FTP):
    def retrlines(self, cmd, callback=None):
        """
        Retrieve data in line mode and return it as a list of lines along with the response code.
        """
        lines = []
        
        # Define a callback that appends each line to the list
        def append_line(line):
            lines.append(line)
        
        if callback is None:
            callback = append_line

        # Send TYPE A to the server and open a data connection
        resp = self.sendcmd('TYPE A')
        with self.transfercmd(cmd) as conn, \
                conn.makefile('r', encoding=self.encoding) as fp:
            while True:
                line = fp.readline(self.maxline + 1)
                if len(line) > self.maxline:
                    raise ftplib.Error("got more than %d bytes" % self.maxline)
                if self.debugging > 2:
                    print('*retr*', repr(line))
                if not line:
                    break
                if line[-2:] == ftplib.CRLF:
                    line = line[:-2]
                elif line[-1:] == '\n':
                    line = line[:-1]
                callback(line)
            
            # Shutdown SSL layer if needed
            if ftplib._SSLSocket is not None and isinstance(conn, ftplib._SSLSocket):
                conn.unwrap()
        
        # Return the list of lines and the final response code
        return lines, self.voidresp()
