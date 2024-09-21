from tkinter import *
import re

class ANSIText(Text):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<KeyPress>", self.prevent_edit)

    def prevent_edit(self, event):
        # Prevent user from editing the text
        return "break"

    def insert_text_with_ansi(self, text):
        # Regex pattern to match ANSI escape sequences
        ansi_escape = re.compile(r'\x1b\[([0-9;]*)m')
        
        # Apply ANSI escape sequences
        start_index = self.index(END)
        cursor_pos = start_index
        i = 0
        while i < len(text):
            # Find the next ANSI escape sequence
            match = ansi_escape.search(text, i)
            if match:
                # Insert text before the escape sequence
                self.insert(END, text[i:match.start()])
                cursor_pos = self.index(END)

                # Process the escape sequence
                seq = match.group(1)
                self.process_ansi_sequence(seq)
                
                # Move past the escape sequence
                i = match.end()
            else:
                # Insert the remaining text
                self.insert(END, text[i:])
                break
        
        self.see(END)
    
    def process_ansi_sequence(self, seq):
        # Example of processing some basic ANSI escape codes
        colors = {
            '30': 'black',
            '31': 'red',
            '32': 'green',
            '33': 'yellow',
            '34': 'blue',
            '35': 'magenta',
            '36': 'cyan',
            '37': 'white'
        }
        tags = []
        for code in seq.split(';'):
            if code in colors:
                tags.append(('fg', colors[code]))
        if tags:
            self.tag_configure('ansi', **dict(tags))
            self.tag_add('ansi', self.index(END) + "-1c", END)