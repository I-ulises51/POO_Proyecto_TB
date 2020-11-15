import os
import re
from file import file

cur_dir = str(os.getcwd())
DefaultTemplate = "/* Indicate filename, ex:module.sv*\nsource_name: default.txt\n\n/* Indicate file location directory, use full directory path */\nsource_dir:" + cur_dir \
                  + " \n\n/* Indicate desired name for the resulting testbench file, ex:module_tb.sv */\ntb_name: default_testbench.txt\n"\
                  +"\n/* Indicate desired location (directory path) for the resulting testbench file, use full directory path */\ntb_dir: " \
                  + cur_dir + "\n\n/* Indicate name of the module clock signal (if none write none) */\nmd_clk_name: none\n\n"\
                  +"/* Indicate name of the module reset signal (if none write none) */\nmd_rst_name: none\n\n/* Indicate if reset is active high (write h) or active low (write l), if no reset write none*/\nrst_ope: none\n\n"+\
                  "/* Generate randomized test cases? (if yes, write the number of test cases, ex: 5, otherwise write none) */\ntb_cases: \n\n/* Type of testbench case generation, inc for incremental, -dec for decremental, defaults to random*/\ntb_gen: rand\n\n"\
                  +"/* When using inc or dec, initial value for testbench cases*/\ntb_initval: 0\n\n/* When using inc or dec, value amount to increase/decrease per case*/\ntb_inc: 1\n\n"\
                  +"/* Indicate number base to be used in testbench cases, hex for hexadecimal, dec for decimal*, defaults to binary*/\ntb_base: bin";

class config_file(file):

    def __init__(self, name):
        self.name = name
        self.direct = os.getcwd()
        self.ConfigValidation = self._config_validation()

    def _config_validation(self):
        lista_config = ["source_name", "source_dir", "tb_name", "tb_dir"
            , "md_clk_name", "md_rst_name", "rst_ope", "tb_cases"
            , "tb_gen", "tb_initval", "tb_inc", "tb_base"]

        if (self.file_validation()):
            config_content = self.read()
            for string in lista_config:
                if not (re.search(string, config_content)):
                    return False
            return True
        else:
            config = open("config.txt", "w+")
            config.write(DefaultTemplate)
            config.close()
            return False

    def get_config(self):
        print()
        if not (self._config_validation()):
            default_config = open(self.name, "w+", 1)
            default_config.write(DefaultTemplate)
            default_config.close()
        else:
            default = self.read()
        rgxcomments = r"(\/\*[\w\s,:\".(\)?¡!¿#$%&\/='\[\]]*\*\/)"
        rgxconfig = r"(source_name|source_dir|tb_name|tb_dir|md_clk_name|md_rst_name|rst_ope|tb_cases|tb_gen|tb_initval|tb_inc|tb_base)[\s:\"]*([\w:\s\\\S]*)"
        configDict = {}
        tmp = re.sub(rgxcomments, "", DefaultTemplate)
        tmp = tmp.split("\n")

        while ("" in tmp):
            tmp.remove("")

        for i in tmp:
            match = re.search(rgxconfig, i)
            if (match):
                configDict[match.group(1)] = match.group(2)

        if not (configDict["tb_initval"]).isdigit():
            configDict["tb_initval"] = '0'

        if not (configDict["tb_inc"]).isdigit():
            configDict["tb_inc"] = '1'

        return configDict
