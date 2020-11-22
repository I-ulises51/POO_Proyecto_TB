import re
import os
import  itertools
from file import file
from random import randint
#Testbench class focuse in the creation of the testbench with the previous data
class TestBench (file):
    def __init__(self, name, direct, mod_info, config_dict): #constructor for this class
        file.__init__(self,name,direct) #constructor of the file clas
        self.mod_info = mod_info #new attribute, a SourceFileData object
        self.config_dict = config_dict #new attribute, Dictionary with all the configurtion parameters

    def checkInt(self, string): #checks if thestring passed can be turned to a Int
        try:
            int(string)
            return True
        except ValueError:
            return False

    def __BaseConv(self, base, x): #Base converter, method used to switch a number to a base
        switcher = {
            "dec": ("d" + str(x)), #from dec to decimal
            "bin": (str(bin(x))[1:]), #from decimal to binary
            "hex": ("h" + str(hex(x))[2:]), #to hexadecimal
            "oct": (str(oct(x))[1:]), #to octal
        }
        return switcher.get(base, (str(bin(x))[1:])) #returns the option selected

    def tb_validation(self): #validates if a file al ready exist with the same name
        print ("fromatPath", self.formatPath())
        #this method ask the user if they want to overwrite a file with the same name, if the user say yes the file is override
        if (os.path.isdir(self.direct)):
            out_path = os.path.join(self.formatPath())
            if (os.path.isfile(out_path)):
                print("An ouput file with the same name found...")
                dups = input("Override? (Y/N): ")
                #in case the user says no, the method creates a new file with the same name and a number added Example.txt -> Example[1].txt
                if (dups == "N"):
                    print("Creating duplicate instance of file...")
                    rgxfile = r"([\w]*)((\((\d*)\)\.)|\.)(txt|sv)"
                    while (os.path.isfile(out_path)):
                        head_tail = os.path.split(out_path)
                        file = re.search(rgxfile, head_tail[1])

                        # print("Match gp1: ", file.group(1))
                        if file.group(4):
                            print("Match gp4: ", file.group(4))
                        # print("Match gp5: ", file.group(5))
                        if file.group(4):
                            tmp = file.group(1) + "(" + str(int(file.group(4)) + 1) + ")" + "." + file.group(5)
                        else:
                            tmp = file.group(1) + "(" + str(1) + ")" + "." + file.group(5)

                        # print("New name for dups file: " + tmp)
                        out_path = os.path.join(self.formatPath(), tmp)
                        # print("New path: " + out_path)
                        self.name = tmp
                        self.config_dict["tb_name"] = tmp
                    # print("Final chosen path was: ", out_path)
                    # print("New dictionary: ", config)
            return True
        else:
            return False

    def __PrintVarNSize (self, tb_out,IODetector, IOSizes, IOSelect): #method used to write in a string the inputs and outputs in order
        i = 0
        for items in IODetector:
            for word in items:
                if IOSelect == 'input': #in this case it th IOSelect is Input, we put in the tesbench the word reg
                    tb_out.write("reg" + IOSizes[i] + " " + word + "_tb;\n")
                elif IOSelect == 'output': #for this case the word is wire
                    tb_out.write("wire" + IOSizes[i] + " " + word + "_tb;\n")

            i += 1 #counter to cover all the list items
        return tb_out

    def __PrintUUTContent(self, tb_out, IDetector, ODetector):
        temp_list = []
        temp_list.append(list(itertools.chain.from_iterable(IDetector)))
        temp_list.append(list(itertools.chain.from_iterable(ODetector)))
        temp_list = list(itertools.chain.from_iterable(temp_list))

        for i in range (len(temp_list)-1):
            tb_out.write(f".{temp_list[i]}({temp_list[i]}_tb), ")

        tb_out.write(f".{temp_list[len(temp_list)-1]}({temp_list[len(temp_list)-1]}_tb));")
        return tb_out

    def __initializeVar(self, tb_out, config, IDetecor): #method used to declare the first variables
        #receives a 2d list and converts it to 1d [[1],[2],[3]] -> [1,2,3]
        flatInputs = list(itertools.chain.from_iterable(IDetecor))
        #depending on the users choice, this controls the clk's options
        if (config["md_clk_name"] != "none"):
            tb_out.write("\t\t" + config["md_clk_name"] + "_tb=0; //Clock Init\n")
        elif (not re.match("(\w*)", config["md_clk_name"])):
            tb_out.write("\t\t//No valid specification of clock signal found in configuration\n")
        else:
            tb_out.write("\t\t//No clock signal indicated in configuration file\n")

        #depending on the users choice, this controls the rst's options
        if (config["rst_ope"] == "h" and  config["md_rst_name"] != "none"):
            tb_out.write("\t\t"+ config["md_rst_name"] + "_tb=1; //Reset\n")
        elif (config["rst_ope"] == "l" and config["md_rst_name"] != "none"):
            tb_out.write(("\t\t"+ config["md_rst_name"]+"_tb=0; //Reset\n"))
        elif (not re.match("(\w*)", config["md_clk_name"])):
            tb_out.write("\t\t//No valid specification of reset signal found in configuration : empty spaces? \n")
        else:
            tb_out.write("\t\t//No reset signal indicated in configuration file\n")

        #uses the 1d list to print in order all the variables
        for i in range(len(flatInputs)):
            if (flatInputs[i] != config["md_clk_name"] and flatInputs[i] != config["md_rst_name"]):
                tb_out.write(f"\t\t{flatInputs[i]}_tb = 0;\n")
        return  tb_out #returns the string modified

    def __CasesSelection(self, tb_out, config, IDetector, ISizes_Val): #Method use dependin on what the user wants for the case generator
        tb_out.write("\t\t//Cases Method Selected: "+ config["tb_gen"]+" option\n") #prints the method selectes

        if (self.config_dict["tb_cases"] == "none" or self.config_dict["tb_cases"] == "none\""): #in case nothing was selected
            tb_out.write("\t\t/None genearation cases option was not selected in configuration file\n") #the following message is printed
            return tb_out

        InitVal = int(config["tb_initval"]) #Initial value for dec and ic casses
        if (self.checkInt(config["tb_cases"])): #checks if it is a integer
            for j in range(0, int(config["tb_cases"])): #for depending on how many cases the user wants
                tb_out.write("\n\t\t#1\n")
                i = 0
                for items in IDetector: #for used to pass through all the list
                    for word in items:
                        #if used to detct rst name and print it depending of the users choice
                        if (word == config["md_rst_name"]):
                            if (config["rst_ope"] == 'l'):
                                rand = str(self.__BaseConv(config["tb_base"], 1))
                                tb_out.write("\t\t//" + word + "_tb = " + str(ISizes_Val[i])
                                             + "'" + rand + "; //Change if reset is desired" + "\n")
                            else:
                                rand = str(self.__BaseConv(config["tb_base"], 0))
                                tb_out.write("\t\t//" + word + "_tb = " + str(ISizes_Val[i])
                                             + "'" + rand + "; //Change if reset is desired" + "\n")
                        #if used to print the rest of the variable with a random number
                        elif (word != config["md_clk_name"] and (config["tb_gen"] == "rand") or
                              (config["tb_gen"] != "dec" and config["tb_gen"] != "inc" and word != config["md_clk_name"])):

                            rand = randint(0, (2 ** (ISizes_Val[i]) - 1))
                            rand = str(self.__BaseConv(config["tb_base"], rand))
                            tb_out.write(
                                "\t\t" + word + "_tb = " + str(ISizes_Val[i]) + "'" + rand + ";" + "\n")
                        #if used to prin dec and inc cases, each of this case have the ability to switch the base hex,oct, dec, bin.
                        elif (word != config["md_clk_name"] and (config["tb_gen"] == "dec" or config["tb_gen"] == "inc") ):
                            VarValue = str(self.__BaseConv(config["tb_base"], InitVal))
                            tb_out.write("\t\t" + word + "_tb = " + str(ISizes_Val[i]) + "'" + VarValue + ";" + "\n")
                    i = i + 1
                    #if's used to detect if the value should be added or decreased
                if(config["tb_gen"] == "dec"):
                    InitVal -= int(config["tb_inc"])
                if(config["tb_gen"] == "inc"):
                    InitVal += int(config["tb_inc"])
        #in case something strange happens we print the following message
        else:
            tb_out.write(
                "\n//There was a problem with the amount of cases indicated, please check configuration file  \n")
        return  tb_out

    def __ClkVar(self, tb_out, config, rgxempty):
        #method used for the always forever line, detects if a clk was declared or not
        if (config["md_clk_name"] == "none" or config["md_clk_name"] == "none\""): #if not, nothing is written
            tb_out.write("\n")
        elif (not re.match(rgxempty, config["md_clk_name"]) or config["md_clk_name"] == ""): #if a match is not found, nothing is written
            tb_out.write("\n")
        else:
            tb_out.write("  always forever #1 " + config["md_clk_name"] + "_tb" + " = ~" + config[ #other cases, we write the name and the instruction
                "md_clk_name"] + "_tb" + ";\n")
        return tb_out

    def __printinstances(self, tb_out, inst_mods): #method used to print the instances found in the Top module
        instances = inst_mods.keys()
        #takes a dictionary and its keys
        tb_out.write("\n\n/* -- Instances found within module -- \n")
        tb_out.write("format: <> module_name --> instance name \n\n")

        for key in instances:#loop that prints all the dictionary content
            tb_out.write("<> " + key + " --> " + inst_mods[key] + "\n")
        tb_out.write("  --------------- */\n")
        return  tb_out

    def generate(self): #method in charge of creating the testbench
        if (self.config_dict["tb_dir"] == ""): #if the directory option is empty, the file is created in the cwd
            self.direct = os.getcwd()

        if (self.tb_validation()): #validates id a file all ready exists and returns true when a decision was made
            tb_path = os.path.join(self.formatPath()) #creation of the path where to write the file
            #print("Esto es tb_path", tb_path)
            tb_out = open(tb_path, "w+", 1) #file creation
            rgxepty = "(\w*)"
            #starting with the template
            tb_out.write("//test bench code\n`timescale 1ns/1ps\n")
            #printing the module name to the testbench
            tb_out.write("module " + self.mod_info.module_name + "_tb\n\n//inputs and outputs\n")
            #printing the inputs and outputs at the start of the testbench
            tb_out = self.__PrintVarNSize(tb_out, self.mod_info.input_list, self.mod_info.input_sizes_str, 'input')
            tb_out = self.__PrintVarNSize(tb_out, self.mod_info.output_list, self.mod_info.output_sizes, 'output')
            #printing the UUt line, with all the variables and the right connections to the top Module
            tb_out.write(self.mod_info.module_name + " UUT (")
            tb_out = self.__PrintUUTContent(tb_out, self.mod_info.input_list, self.mod_info.output_list)

            # escritura del cuerpo del test bench
            tb_out.write("\ninitial\n \tbegin\n\t\t$dumpfile(\"" + self.mod_info.module_name + "_tb.vcd\");\n")
            tb_out.write("\t\t$dumpvars (1, " + self.mod_info.module_name + "_tb"");\n\t\t\n\t\t//clk and rst initial values\n")
            #Setting all the input variables to 0
            tb_out = self.__initializeVar(tb_out, self.config_dict, self.mod_info.input_list)

            tb_out.write("\n\t\t//variable changes  \n")
            # Generates the cases depending on the options the user selected
            tb_out = self.__CasesSelection(tb_out, self.config_dict, self.mod_info.input_list, self.mod_info.input_sizes_int)
            #printing the always forever for the clock if needed
            tb_out.write("\n\t\t#1\n\t\t$finish;\n\tend\n")
            tb_out = self.__ClkVar(tb_out, self.config_dict, rgxepty)
            tb_out.write("endmodule\n")
            #printing the instances found in the top module
            tb_out = self.__printinstances(tb_out,self.mod_info.instantiated_mods)
            tb_out.close()
        else:
            #if anything fails, message to declare a failure
            print("Unable to generate tb...")
