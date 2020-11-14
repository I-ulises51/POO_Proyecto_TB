import re
import os
from file import  file

rgxModule = "module\\s+([a-zA-Z]\\w*)"
rgxInput = "(input)\s*(logic|reg|\s)*\s*(\[\d+:\d+\]|\s*)\s*([a-zA-Z\w, ]*)"
rgxOutput = "(output)\s*(logic|reg|\s)*\s*(\[\d+:\d+\]|\s*)\s*([a-zA-Z\w, ]*)"

class src_file(file):
    def __init__(self, name, direct = ""):
        file.__init__(self, name, direct)
        if self.file_validation():
            rgxinout = ["(module)", "(input)", "(output)"]
            if self.content_validation(rgxinout):
                self.source_string = self.read()
                self.source_string = self.__RmvComments(self.source_string)
                self.source_string = self.__alignVar(self.source_string)
                self.source_string = self.source_string.split("\n")
                self.source_string = self.__SubParams(self.source_string)
                #self.source_string = self.__SubParams((self.__alignVar(self.__RmvComments(self.read()))).split("\n"))
            else:
                self.name = "default.txt"
                self.direct = os.getcwd()
                self.source_string = self.read()
                self.source_string = self.source_string.split("\n")
                #self.source_string = ((self.read()).split("\n"))

    def getsourceString(self):
        return self.source_string

    def __alignVar(self, ContentList):
        rgxinouts = r", *(input|output|inout)"
        tmp = re.sub(rgxinouts, r"\n\1", ContentList)
        return re.sub(r"\t", " ", tmp)

    def __Rmvspaces(self, ContentList):  # removes blank spaces of a list ['',1,2] -> [1,2]
        if (type(ContentList) != str):  # sometimes a string pass through, we check the case to prevent an error
            while ("" in ContentList):
                ContentList.remove("")
            return ContentList  # return the list without blank spaces
        else:
            return ContentList

    def __DetectRGX(self, ContentList, rgx, GroupNum):
        Detected = []
        for i in range(0, len(ContentList) - 1):
            if (re.search(rgx, ContentList[i])):
                Detected.append(re.search(rgx, ContentList[i]).group(GroupNum))
        return Detected

    def __splitVar(self, ContentList):
        List = []
        count = 0
        rgx = r",\s*;*"  # busca patron de ", "
        template = ['out', '']  # caso especial de la ultima variable
        for I in ContentList:  # ciclo para recorrer todas las cadenas de caracteres
            if (re.search(rgx, I)):  # si encuentra una ", " divide la variable
                List.append((re.sub(rgx, " ", I)).split(" "))  # crea una lista con las cadenas separadas
            else:
                # print("Template before changes: ", template)
                template[0] = I  # caso especial de la ultima variable cambia a la primera posicion
                List.append(template)
                template = ['out', '']
            List[count] = self.__Rmvspaces(List[count])  # remuebe espacios en blanco creditos a Irving Sanchez
            count += 1
        return self.__Rmvspaces(List)

    def __RmvComments(self, FileContentComments):
        rgxcomments = r"(\/\*[,\w\s\'\/\W\[\r\n\*]*\*\/)|(\/\/\s*([\w #$%&\(\)=\!\?\¡\¿¨*+-_\[\]\{\}\".,;:]*))"
        return (re.sub(rgxcomments, "", FileContentComments))

    def __SubParams(self, ContentList):
        List = []
        paramDict = {}
        paramkeys = []
        rgxparam = "((parameter)\s*([\w]*)\s*=\s*([\w']*))"

        for i in ContentList:
            paramatch = re.search(rgxparam, i)
            if (paramatch):
                paramDict[paramatch.group(3)] = paramatch.group(4)
                paramkeys.append(paramatch.group(3))

        for element in ContentList:
            for key in paramkeys:
                if (re.search(key, element)):
                    element = re.sub(key, paramDict[key], element)
            List.append(element)

        return (List)

    def __numsize(self, ContentList):
        rgx = r"(\[(\d+):(\d+)\])"
        x = []
        for i in ContentList:
            if not i:
                x.append(int(1))
            else:
                y = re.match(rgx, i[0])
                x.append(abs(int(y[2]) - int(y[3])) + 1)
        return x

    def __findInstances(self, ContentList):
        instDict = {}
        rgxinst = r"([\w_]*)\s*([\w_]*)\s*(\([\w_\-\(\)\[\], .:]*\))"
        for i in ContentList:
            match = re.search(rgxinst, i)
            if (match):
                # match.group(3) contains all wires connected to the instance
                instDict[match.group(1)] = match.group(2)

        return (instDict)

    def getFileModule(self):
        ModuleDetector = self.__DetectRGX(self.source_string, rgxModule, 1)
        return ModuleDetector[0]

    def getFileInputs(self):
        return self.__splitVar(self.__DetectRGX(self.source_string, rgxInput, 4))

    def getInputSizes(self):
        return self.__DetectRGX(self.source_string, rgxInput, 3)

    def getInputSizesInt(self):
        return self.__numsize(self.__splitVar(self.getInputSizes()))

    def getFileOutputs(self):
        return self.__splitVar(self.__DetectRGX(self.source_string, rgxOutput, 4))

    def getOutputSizes(self):
        return self.__DetectRGX(self.source_string, rgxOutput, 3)

    def getOutputSizesInt(self):
        return self.__numsize(self.__splitVar(self.getOutputSizes()))

    def getInstantiatedMods(self):
        return self.__findInstances(self.source_string)

class SourceFileData (src_file):
    def __init__(self, name, direct = ""):
        src_file.__init__(self, name , direct)
        Source = src_file(name, direct)
        self.module_name = Source.getFileModule()
        self.input_list = Source.getFileInputs()
        self.input_sizes_str = Source.getInputSizes()
        self.input_sizes_int = Source.getInputSizesInt()
        self.output_list = Source.getFileOutputs()
        self.output_sizes = Source.getOutputSizes()
        self.instantiated_mods = Source.getInstantiatedMods()


if __name__ == '__main__':

    Source = src_file("Test.txt")
    print("--------------Module Test.txt-------------")
    print(Source.getFileModule())

    print("--------------Input Test.txt-------------")
    print("Variables", Source.getFileInputs())
    print("Size", Source.getInputSizes())
    print("Size Int", Source.getInputSizesInt())

    print("--------------Output Test.txt-------------")
    print("Variable", Source.getFileOutputs())
    print("Size", Source.getOutputSizes())
    print("Size Int", Source.getOutputSizesInt())

    print("--------------SFD Test.txt-------------")
    Data = SourceFileData("Test.txt")
    print (Data.getFileModule())