import re
import os
from file import file
from itertools import  chain
from random import randint

class TestBench (file):
    def __init__(self, name, direct=""):
        file.__init__(self, name, direct)
        self.InputList = []
        self.InputSizes = []
        self.InputSizesInt = []
        self.OutputList = []
        self.OutputSizes = []
        self.OutputSizesInt = []

    def checkInt(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def tb_validation(self):
        print ("fromatPath", self.formatPath())
        if (os.path.isdir(self.direct)):
            out_path = os.path.join(self.formatPath())
            print("Esto es out_path", out_path)
            if (os.path.isfile(out_path)):
                print("An ouput file with the same name found...")
                dups = input("Override? (Y/N): ")

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

    def __PrintVarNSize (self, tb_out,IODetector, IOSizes):
        i = 0
        for items in IODetector:
            for word in items:
                tb_out.write("  reg " + IOSizes[i] + " " + word + "_tb;\n")
            i += 1
        return tb_out

    def __PrintUUTContent(self, tb_out, IDetector, ODetector):
        temp_list = []
        temp_list.append(list(chain.from_iterable(IDetector)))
        temp_list.append(list(chain.from_iterable(ODetector)))
        temp_list = list(chain.from_iterable(temp_list))

        for i in range (len(temp_list)-1):
            tb_out.write(f".{temp_list[i]}({temp_list[i]}_tb), ")

        tb_out.write(f".{temp_list[len(temp_list)-1]}({temp_list[len(temp_list)-1]}_tb));")
        return tb_out

    def __CheckRstClk(self,tb_out, rgxempty, config, key):
        if (config[key] == "none" or config[key] == "none\""):
            tb_out.write("//No clock signal indicated in configuration file\n")
        elif (not re.match(rgxempty, config[key])):
            tb_out.write("//No valid specification of clock signal found in configuration\n")
        else:
            tb_out.write("  " + config[key] + "_tb" + " = 0;\n")
        return tb_out

    def __ClkVar(self, tb_out, config, rgxempty):
        if (config["md_clk_name"] == "none" or config["md_clk_name"] == "none\""):
            tb_out.write("\n")
        elif (not re.match(rgxempty, config["md_clk_name"]) or config["md_clk_name"] == ""):
            tb_out.write("\n")
        else:
            # print("no")
            tb_out.write("  always forever #1 " + config["md_clk_name"] + "_tb" + " = ~" + config[
                "md_clk_name"] + "_tb" + ";\n")
        return tb_out

    def __printinstances(self, tb_out, inst_mods):
        instances = inst_mods.keys()
        tb_out.write("\n\n/* -- Instances found within module -- \n")
        tb_out.write("format: <> module_name --> instance name \n\n")

        for key in instances:
            tb_out.write("<> " + key + " --> " + inst_mods[key] + "\n")
        tb_out.write("  --------------- */\n")
        return  tb_out

    def generate(self):

        if (self.config_dict["tb_dir"] == ""):
            self.direct = os.getcwd()
        if (self.tb_validation()):
            tb_path = os.path.join(self.formatPath())
            #print("Esto es tb_path", tb_path)
            tb_out = open(tb_path, "w+", 1)
            rgxepty = "(\w*)"
            mod_name = self.mod_info.module_name
            inputDetector = self.mod_info.input_list
            inputSizes = self.mod_info.input_sizes_str
            inputSizes_val = self.mod_info.input_sizes_int
            outputDetector = self.mod_info.output_list
            outputSizes = self.mod_info.output_sizes
            inst_mods = self.mod_info.instantiated_mods
            config = self.config_dict

            tb_out.write("//test bench code\n`timescale 1ns/1ps\n")
            tb_out.write("module " + mod_name + "_tb\n\n//inputs and outputs\n")

            tb_out = self.__PrintVarNSize(tb_out,inputDetector,inputSizes)
            tb_out = self.__PrintVarNSize(tb_out,outputDetector,outputSizes)

            tb_out.write("  " + mod_name + " UUT (")
            tb_out = self.__PrintUUTContent(tb_out, inputDetector, outputDetector)

            # escritura del curpo del test bench
            tb_out.write("\ninitial\n \tbegin\n\t\t$dumpfile(\"" + mod_name + "_tb.vcd\");\n")
            tb_out.write("\t\t$dumpvars (1, " + mod_name + "_tb"");\n\t\t\n//clk and rst initial values\n")

            tb_out = self.__CheckRstClk(tb_out,rgxepty,config,"md_clk_name")
            tb_out = self.__CheckRstClk(tb_out, rgxepty, config, "md_rst_name")

            tb_out.write("\n//variable changes  \n")

            # ciclo para la escitura de n pruebas aleatorias
            if (config["tb_cases"] == "none" or config["tb_cases"] == "none\""):
                tb_out.write("\n//Generation of random testcases was not selected in configuration file  \n")

            elif (self.checkInt(config["tb_cases"])):

                for j in range(0, int(config["tb_cases"])):
                    tb_out.write("\n\t\t#1\n")
                    i = 0
                    for items in inputDetector:
                        for word in items:
                            if (word == config["md_rst_name"]):
                                if (config["rst_ope"] == 'l'):
                                    rand = 1
                                    rand = str(bin(rand))
                                    tb_out.write("\t\t//" + word + "_tb = " + str(inputSizes_val[i]) + "'" + rand[
                                                                                                           1:] + "; //Change if reset is desired" + "\n")
                                else:
                                    rand = 0
                                    rand = str(bin(rand))
                                    tb_out.write("\t\t//" + word + "_tb = " + str(inputSizes_val[i]) + "'" + rand[
                                                                                                           1:] + "; //Change if reset is desired" + "\n")
                            elif (word != config["md_clk_name"]):
                                rand = randint(0, (2 ** (inputSizes_val[i]) - 1))
                                rand = str(bin(rand))
                                tb_out.write(
                                    "\t\t" + word + "_tb = " + str(inputSizes_val[i]) + "'" + rand[1:] + ";" + "\n")
                        i = i + 1

            else:
                tb_out.write(
                    "\n//There was a problem with the amout of cases indicated, please check configuration file  \n")

            tb_out.write("\n\t\t#1\n\t\t$finish;\n\tend\n")

            tb_out = self.__ClkVar(tb_out, config, rgxepty)
            tb_out.write("endmodule\n")
            tb_out = self.__printinstances(tb_out,inst_mods)
            tb_out.close()
        else:
            print("Unable to generate tb...")

if __name__ == '__main__':
    TB = TestBench("tst_testbench.txt")
    TB.generate()