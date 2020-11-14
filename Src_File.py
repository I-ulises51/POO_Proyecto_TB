import re
from file import  file


class module:
    def __init__(self, module_name, input_list, input_sizes_str, input_sizes_int, output_list, output_sizes,
                 instantiated_mods):
        self.module_name = module_name
        self.input_list = input_list
        self.input_sizes_str = input_sizes_str
        self.input_sizes_int = input_sizes_int
        self.output_list = output_list
        self.output_sizes = output_sizes
        self.instantiated_mods = instantiated_mods

class src_file(file):

    def alignVar(self, ContentList):
        rgxinouts = r", *(input|output|inout)"
        tmp = re.sub(rgxinouts, r"\n\1", ContentList)
        return (re.sub(r"\t", " ", tmp))

    def Rmvspaces(self, ContentList):  # removes blank spaces of a list ['',1,2] -> [1,2]
        if (type(ContentList) != str):  # sometimes a string pass through, we check the case to prevent an error
            while ("" in ContentList):
                ContentList.remove("")
            return ContentList  # return the list without blank spaces
        else:
            return ContentList

    def DetectRGX(self, ContentList, rgx, GroupNum):
        Detected = []
        for i in range(0, len(ContentList) - 1):
            if (re.search(rgx, ContentList[i])):
                Detected.append(re.search(rgx, ContentList[i]).group(GroupNum))
        return Detected

    def splitVar(self, ContentList):
        List = []
        count = 0
        # print("Inicio:", ContentList)
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
            List[count] = self.Rmvspaces(List[count])  # remuebe espacios en blanco creditos a Irving Sanchez
            count += 1
        return self.Rmvspaces(List)

    def RmvComments(self, FileContentComments):
        rgxcomments = r"(\/\*[,\w\s\'\/\W\[\r\n\*]*\*\/)|(\/\/\s*([\w #$%&\(\)=\!\?\¡\¿¨*+-_\[\]\{\}\".,;:]*))"
        return (re.sub(rgxcomments, "", FileContentComments))

    def SubParams(self, ContentList):
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

    def numsize(self, ContentList):
        rgx = r"(\[(\d+):(\d+)\])"
        x = []
        for i in ContentList:
            if i == "":
                x.append(int(1))
            else:
                y = re.match(rgx, i)
                x.append(abs(int(y[2]) - int(y[3])) + 1)
        return x

    def findInstances(self, ContentList):
        instDict = {}
        rgxinst = r"([\w_]*)\s*([\w_]*)\s*(\([\w_\-\(\)\[\], .:]*\))"

        for i in ContentList:
            match = re.search(rgxinst, i)
            if (match):
                # match.group(3) contains all wires connected to the instance
                instDict[match.group(1)] = match.group(2)

        return (instDict)

    def get_content(self):
        rgxinout = ["(module)", "(input)", "(output)"]

        if self.file_validation():
            if self.content_validation(rgxinout):
                rgx2 = "module\\s+([a-zA-Z]\\w*)"
                rgx3 = "(input)\s*(logic|reg|\s)*\s*(\[\d+:\d+\]|\s*)\s*([a-zA-Z\w, ]*)"
                rgx4 = "(output)\s*(logic|reg|\s)*\s*(\[\d+:\d+\]|\s*)\s*([a-zA-Z\w, ]*)"

                source_string = self.read()

                source_string = self.RmvComments(source_string)
                source_string = self.alignVar(source_string)

                ContentList = source_string.split("\n")  # separar el string

                while ("" in ContentList):
                    ContentList.remove("")

                ContentList = self.SubParams(ContentList)

                ModuleDetector = self.DetectRGX(ContentList, rgx2, 1)
                mod_name = ModuleDetector[0]

                inputDetector = self.splitVar(self.DetectRGX(ContentList, rgx3, 4))

                inputSizes = self.DetectRGX(ContentList, rgx3, 3)
                inputSizes_val = self.numsize(inputSizes)

                outputDetector = self.splitVar(self.DetectRGX(ContentList, rgx4, 4))

                outputSizes = self.DetectRGX(ContentList, rgx4, 3)

                inst_mods = self.findInstances(ContentList)

                module_model = module(mod_name, inputDetector, inputSizes, inputSizes_val, outputDetector, outputSizes,
                                      inst_mods)

                return module_model

        else:
            return False