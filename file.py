import re
import os
#Parent class, gathers multiple methods used in all the child classes
class file:
    def __init__(self, name, direct): #constructor of the file class
        self.name = name
        self.direct = direct

    def formatPath(self): #function to format the paths C:\Desktop - > C:/Desktop
        rgx = r"([\\])"
        tmp = re.sub(rgx, r"/", self.direct)
        return os.path.join(tmp, self.name)

    def file_validation(self): # function to validate if file exists
        if(os.path.isfile(self.formatPath())):
            return True
        else:
            return False

    def content_validation(self, rgx_list): #function to validate the content of the file with a regex
        if(os.stat(self.formatPath()).st_size != 0):
            val_file = open(self.formatPath(), "r+", 1)
            file_cont = val_file.read()
            val_file.close()
            for key in rgx_list:
                if not re.search(key, file_cont):
                    return False #return false if a think is missing from a rgx list send
            return True #true if at least the rgx list is found once
        else:
            return False

    def read(self): #function to read the file and store it in a string
        file = open(self.formatPath(), "r+", 1)
        content = file.read()
        file.close()
        return content