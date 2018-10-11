import codecs
import os

from builtins import FileNotFoundError
import random
from time import sleep   


# Represents a connection between a two servers/clients
# In its current form, connects the two by creating a file for them to communicate with
class Connection:
    
    def __init__(self, filename):
        self.filename = filename
        # try to open the file to read it
        try:
            while self.is_open():
                sleep(random.random())
            with codecs.open(self.filename, encoding='utf-8') as f:
                self.loc = len(f.read())
        # if the file does not exist, create it
        except (FileNotFoundError, NameError) as e:
            with open(self.filename, 'wb') as f:
                self.loc = 0
        
    
    def send_message(self, message):
        while self.is_open():
            sleep(random.random())
        with codecs.open(self.filename, 'a', encoding='utf-8') as f:
            f.write(message)
        # update the current location to avoid reading own sent message
        self.loc += len(message)
    
    def get_message(self):
        while self.is_open():
            sleep(random.random())
        with codecs.open(self.filename, 'r', encoding='utf-8') as f:
            contents = f.read()
            old_loc = self.loc
            self.loc = len(contents)
        return contents[old_loc:]
    
    # https://stackoverflow.com/a/37515805
    def is_open(self):
        if os.path.exists(self.filename):
            try:
                os.rename(self.filename, self.filename)
                return False
            except:
                return True
        raise NameError    
    