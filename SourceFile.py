import re
import os
from file import  file
#Regex used in our code to find keywords and its values Module, Input and Outputs
rgxModule = "module\\s+([a-zA-Z]\\w*)"
rgxInput = "(input)\s*(logic|reg|\s)*\s*(\[\d+:\d+\]|\s*)\s*([a-zA-Z\w, ]*)"
rgxOutput = "(output)\s*(logic|reg|\s)*\s*(\[\d+:\d+\]|\s*)\s*([a-zA-Z\w, ]*)"

#Class src_file in charge of the TopModule processing
class src_file(file):
    def __init__(self, name, direct = ""): #constructor of the class src_file
        #self.direct = os.getcwd()
        file.__init__(self, name, direct) #constructor of the class file, used in the clas src_file
        if self.file_validation(): #If for validating that the TopModule file exists
            rgxinout = ["(module)", "(input)", "(output)"] #List for the content validation
            if self.content_validation(rgxinout): #We search the Top Module presents all of the keywords
                self.source_string = self.read() #Storing the content of the file in a variable
                self.source_string = self.__RmvComments(self.source_string) #removing the comments from the file
                self.source_string = self.__alignVar(self.source_string) #split the inputs declared in a same line, this way our regx can detect it
                self.source_string = self.source_string.split("\n") #we create a new list, splitting the string by \n
                self.source_string = self.__SubParams(self.source_string) #replacing the parameters declared inside the content
                #self.source_string = self.__SubParams((self.__alignVar(self.__RmvComments(self.read()))).split("\n"))
            else:# if the TopModule doesnt contain a keyword
                self.name = "default.txt" #we set the values to a default TopModule
                self.direct = os.getcwd() #The Default file is stored in the same directory as the python code
                self.source_string = self.read()#we store the content in a variable
                self.source_string = self.source_string.split("\n") #splits the content in a list by \n
                #self.source_string = ((self.read()).split("\n"))
        else: #if the TopModule is not found, we take again the default.txt
            self.name = "default.txt"
            self.direct = os.getcwd()
            self.source_string = self.read()
            self.source_string = self.source_string.split("\n")

    def getsourceString(self): #method used to get the content of the file
        return self.source_string

    def __alignVar(self, ContentList): #method used to split the inputs declared on a same line
        rgxinouts = r", *(input|output|inout)" #regex to find the keywords
        tmp = re.sub(rgxinouts, r"\n\1", ContentList) #replacing it for the same keyword plus a \n
        return re.sub(r"\t", " ", tmp) #returning a new string

    def __Rmvspaces(self, ContentList):  # removes blank spaces of a list ['',1,2] -> [1,2]
        if (type(ContentList) != str):  # sometimes a string pass through, we check the case to prevent an error
            while ("" in ContentList):
                ContentList.remove("")
            return ContentList  # return the list without blank spaces
        else:
            return ContentList

    def __DetectRGX(self, ContentList, rgx, GroupNum): #method used to return a list with a specific regex
        Detected = []
        for i in range(0, len(ContentList) - 1):#For used to cover all the list with the content split
            if (re.search(rgx, ContentList[i])): #if used to find the regex pattern
                Detected.append(re.search(rgx, ContentList[i]).group(GroupNum)) #creating a list with the matches
        return Detected #returns the list with the matches

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

    def __RmvComments(self, FileContentComments): #funtion used to remmove all the comments on the top module
        rgxcomments = r"(\/\*[,\w\s\'\/\W\[\r\n\*]*\*\/)|(\/\/\s*([\w #$%&\(\)=\!\?\¡\¿¨*+-_\[\]\{\}\".,;:]*))" # regex for short and long comments
        return (re.sub(rgxcomments, "", FileContentComments))

    def __SubParams(self, ContentList): #function used to replace the keyword parameters inside a variable
        List = []
        paramDict = {}
        paramkeys = []
        rgxparam = "((parameter)\s*([\w]*)\s*=\s*([\w']*))" #regex used to find the keyword parameters

        for i in ContentList: # for used to create a dictionary with the key as the parameter's name and value as the value of the parametes
            paramatch = re.search(rgxparam, i)
            if (paramatch):
                paramDict[paramatch.group(3)] = paramatch.group(4)
                paramkeys.append(paramatch.group(3))
        # for used to replace each element with its value
        for element in ContentList:
            for key in paramkeys:
                if (re.search(key, element)):
                    element = re.sub(key, paramDict[key], element)
            List.append(element)

        return (List)

    def __numsize(self, ContentList):#Method used to detect the value of a variable, [7:0] - > 8 bits
        rgx = r"(\[(\d+):(\d+)\])"
        x = []
        for i in ContentList:
            if not i:
                x.append(int(1))
            else:
                y = re.match(rgx, i[0])
                x.append(abs(int(y[2]) - int(y[3])) + 1)
        return x

    def __findInstances(self, ContentList): #method used to find instances on a TopModule file
        instDict = {}
        rgxinst = r"([\w_]*)\s*([\w_]*)\s*(\([\w_\-\(\)\[\], .:]*\))"
        for i in ContentList:
            match = re.search(rgxinst, i)
            if (match):
                # match.group(3) contains all wires connected to the instance
                instDict[match.group(1)] = match.group(2)

        return (instDict) #at the final it returns a dictionary with all the instances found

    def getFileModule(self): #getter used to return the name of the Module found
        ModuleDetector = self.__DetectRGX(self.source_string, rgxModule, 1)
        return ModuleDetector[0]

    def getFileInputs(self): #getter that return a list of all the inputs found in the Top Module
        return self.__splitVar(self.__DetectRGX(self.source_string, rgxInput, 4))

    def getInputSizes(self): #getter that return a list of all the Sizes of the inputs found in the Top Module
        return self.__DetectRGX(self.source_string, rgxInput, 3)

    def getInputSizesInt(self):  #getter that return a list of all the inputs found in the Top Module but in integers
        return self.__numsize(self.__splitVar(self.getInputSizes()))

    def getFileOutputs(self): #getter that return a list of all the outputs found in the Top Module
        return self.__splitVar(self.__DetectRGX(self.source_string, rgxOutput, 4))

    def getOutputSizes(self): #getter that return a list of all the outputs sizes found in the Top Module
        return self.__DetectRGX(self.source_string, rgxOutput, 3)

    def getOutputSizesInt(self): #getter that return a list of all the outputs sizes found in the Top Module but in integers
        return self.__numsize(self.__splitVar(self.getOutputSizes()))

    def getInstantiatedMods(self):  #getter that returns a dictionary with all the instances found in the TopModule
        return self.__findInstances(self.source_string)

class SourceFileData (src_file): #The class SourceFileData serves as a recopilation for all the important information
    def __init__(self, name, direct = ""):
        src_file.__init__(self, name , direct)
        #Source = src_file(name, direct)
        self.module_name = src_file.getFileModule(self) #Module name
        self.input_list = src_file.getFileInputs(self) #Inputs
        self.input_sizes_str = src_file.getInputSizes(self) #Inputs Sizes -> [7:0]
        self.input_sizes_int = src_file.getInputSizesInt(self) # Input Sizes -> 8 bits
        self.output_list = src_file.getFileOutputs(self) #Outputs
        self.output_sizes = src_file.getOutputSizes(self) #Outputs Sizes [7:0]
        self.instantiated_mods = src_file.getInstantiatedMods(self) #all the intances found
