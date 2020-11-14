import re
import os

class file:
    def __init__(self, name, direct):
        self.name = name
        self.direct = direct

    def formatPath(self):
        rgx = r"([\\])"
        tmp = re.sub(rgx, r"/", self.direct)
        return os.path.join(tmp, self.name)

    def file_validation(self):
        if(os.path.isfile(self.formatPath())):
            return True
        else:
            return False

    def content_validation(self, rgx_list):
        if(os.stat(self.formatPath()).st_size != 0):
            val_file = open(self.formatPath(), "r+", 1)
            file_cont = val_file.read()
            val_file.close()
            for key in rgx_list:
                if not re.search(key, file_cont):
                    return False
            return True
        else:
            return False

    def read(self):
        file = open(self.formatPath(), "r+", 1)
        content = file.read()
        file.close()
        return content