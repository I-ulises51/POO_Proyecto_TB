import re
import os
from file import file
from itertools import  chain
from random import randint
#cambios
class TestBench (file):
    def __init__(self, name, direct, mod_info, config_dict):
        file.__init__(self,name,direct)
        self.mod_info = mod_info
        self.config_dict = config_dict

    def checkInt(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def __BaseConv(self, base, x):
        switcher = {
            "dec": ("d" + str(x)),
            "bin": (str(bin(x))[1:]),
            "hex": ("h" + str(hex(x))[2:]),
            "oct": (str(oct(x))[1:]),
        }
        return switcher.get(base, (str(bin(x))[1:]))

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

    def __PrintVarNSize (self, tb_out,IODetector, IOSizes ):
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

    def __initializeVar(self, tb_out, config, IDetecor):
        flatInputs = list(chain.from_iterable(IDetecor))
        if (config["md_clk_name"] != "none"):
            tb_out.write("\t\t" + config["md_clk_name"] + "_tb=0; //Clock Init\n")
        elif (not re.match("(\w*)", config["md_clk_name"])):
            tb_out.write("\t\t//No valid specification of clock signal found in configuration\n")
        else:
            tb_out.write("\t\t//No clock signal indicated in configuration file\n")

        if (config["rst_ope"] == "h" and  config["md_rst_name"] != "none"):
            tb_out.write("\t\t"+ config["md_rst_name"] + "_tb=1; //Reset\n")
        elif (config["rst_ope"] == "l" and config["md_rst_name"] != "none"):
            tb_out.write(("\t\t"+ config["md_rst_name"]+"_tb=0; //Reset\n"))
        elif (not re.match("(\w*)", config["md_clk_name"])):
            tb_out.write("\t\t//No valid specification of reset signal found in configuration : empty spaces? \n")
        else:
            tb_out.write("\t\t//No reset signal indicated in configuration file\n")

        for i in range(len(flatInputs)):
            if (flatInputs[i] != config["md_clk_name"] and flatInputs[i] != config["md_rst_name"]):
                tb_out.write(f"\t\t{flatInputs[i]}_tb = 0;\n")
        return  tb_out

    def __PrintFixCases(self, tb_out, config, IDetector):
        tb_out.write("\t\t//Fix step generation selected")
        flatInputs = list(chain.from_iterable(IDetector))
        initVal = int(config["tb_initval"])
        for i in range (int(config["tb_initval"]), int(config["tb_cases"])):
            for item in flatInputs:
                tb_out.write(f"\t\t{item}_tb = {initVal};\n")
            initVal += int(config["tb_inc"])
        return tb_out

    def __CasesSelection(self, tb_out, config, IDetector, ISizes_Val):
        tb_out.write("\t\t//Cases Method Selected: "+ config["tb_gen"]+" option\n")

        if (self.config_dict["tb_cases"] == "none" or self.config_dict["tb_cases"] == "none\""):
            tb_out.write("\t\t/None genearation cases option was not selected in configuration file\n")
            return tb_out

        InitVal = int(config["tb_initval"])
        if (self.checkInt(config["tb_cases"])):
            for j in range(0, int(config["tb_cases"])):
                tb_out.write("\n\t\t#1\n")
                i = 0
                for items in IDetector:
                    for word in items:
                        if (word == config["md_rst_name"]):
                            if (config["rst_ope"] == 'l'):
                                rand = str(self.__BaseConv(config["tb_base"], 1))
                                tb_out.write("\t\t//" + word + "_tb = " + str(ISizes_Val[i])
                                             + "'" + rand + "; //Change if reset is desired" + "\n")
                            else:
                                rand = str(self.__BaseConv(config["tb_base"], 0))
                                tb_out.write("\t\t//" + word + "_tb = " + str(ISizes_Val[i])
                                             + "'" + rand + "; //Change if reset is desired" + "\n")
                        elif (word != config["md_clk_name"] and (config["tb_gen"] == "rand") or
                              (config["tb_gen"] != "dec" and config["tb_gen"] != "inc" and word != config["md_clk_name"])):

                            rand = randint(0, (2 ** (ISizes_Val[i]) - 1))
                            rand = str(self.__BaseConv(config["tb_base"], rand))
                            tb_out.write(
                                "\t\t" + word + "_tb = " + str(ISizes_Val[i]) + "'" + rand + ";" + "\n")

                        elif (word != config["md_clk_name"] and (config["tb_gen"] == "dec" or config["tb_gen"] == "inc") ):
                            InitVal_Temp = str(self.__BaseConv(config["tb_base"], InitVal))
                            tb_out.write(
                                "\t\t" + word + "_tb = " + str(ISizes_Val[i]) + "'" + InitVal_Temp + ";" + "\n")
                    i = i + 1
                if(config["tb_gen"] == "dec"):
                    InitVal -= int(config["tb_inc"])
                if(config["tb_gen"] == "inc"):
                    InitVal += int(config["tb_inc"])
        else:
            tb_out.write(
                "\n//There was a problem with the amount of cases indicated, please check configuration file  \n")
        return  tb_out

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

            tb_out.write("//test bench code\n`timescale 1ns/1ps\n")
            tb_out.write("module " + self.mod_info.module_name + "_tb\n\n//inputs and outputs\n")

            tb_out = self.__PrintVarNSize(tb_out, self.mod_info.input_list, self.mod_info.input_sizes_str)
            tb_out = self.__PrintVarNSize(tb_out, self.mod_info.output_list, self.mod_info.output_sizes)

            tb_out.write("  " + self.mod_info.module_name + " UUT (")
            tb_out = self.__PrintUUTContent(tb_out, self.mod_info.input_list, self.mod_info.output_list)

            # escritura del cuerpo del test bench
            tb_out.write("\ninitial\n \tbegin\n\t\t$dumpfile(\"" + self.mod_info.module_name + "_tb.vcd\");\n")
            tb_out.write("\t\t$dumpvars (1, " + self.mod_info.module_name + "_tb"");\n\t\t\n//clk and rst initial values\n")

            tb_out = self.__initializeVar(tb_out, self.config_dict, self.mod_info.input_list)

            tb_out.write("\n//variable changes  \n")
            # ciclo para la escitura de n pruebas aleatorias
            tb_out = self.__CasesSelection(tb_out, self.config_dict, self.mod_info.input_list, self.mod_info.input_sizes_int)

            tb_out.write("\n\t\t#1\n\t\t$finish;\n\tend\n")
            tb_out = self.__ClkVar(tb_out, self.config_dict, rgxepty)
            tb_out.write("endmodule\n")
            tb_out = self.__printinstances(tb_out,self.mod_info.instantiated_mods)
            tb_out.close()
        else:
            print("Unable to generate tb...")
