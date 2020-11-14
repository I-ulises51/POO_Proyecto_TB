import os
import re
from file import file


class config_file(file):

    def __init__(self, name):
        self.name = name
        self.direct = os.getcwd()
        self.ConfigValidation = self._config_validation()

    def _config_validation(self):
        lista_config = ["source_name","source_dir","tb_name","tb_dir","md_clk_name","md_rst_name","rst_ope","tb_cases"]
        config_content = self.read()
        for string in lista_config:
            if not (re.search(string,config_content)):
                return False
        return True

    def get_config(self):
        print()
        if not (self._config_validation()):
            cur_dir= str( os.getcwd())
            string = "/* Indicate filename, ex:module.sv*\nsource_name: default_design.txt\n\n/* Indicate file location directory, use full directory path */\nsource_dir:"+cur_dir+" \n\n/* Indicate desired name for the resulting testbench file, ex:module_tb.sv */\ntb_name: default_testbench.txt\n\n/* Indicate desired location (directory path) for the resulting testbench file, use full directory path */\ntb_dir: "+cur_dir+"\n\n/* Indicate name of the module clock signal (if none write none) */\nmd_clk_name: none\n\n/* Indicate name of the module reset signal (if none write none) */\nmd_rst_name: none\n\n/* Indicate if reset is active high (write h) or active low (write l), if no reset write none*/\nrst_ope: none\n\n/* Generate randomized test cases? (if yes, write the number of test cases, ex: 5, otherwise write none) */\ntb_cases: 0";
            default_config = open(self.name, "w+", 1)
            default_config.write(string)
            default_config.close()
        else:
            string = self.read()
        rgxcomments = r"(\/\*[\w\s,:\".(\)?¡!¿#$%&\/='\[\]]*\*\/)"
        rgxconfig = r"(source_name|source_dir|tb_name|tb_dir|md_clk_name|md_rst_name|rst_ope|tb_cases)[\s:\"]*([\w:\s\\\S]*)"
        configDict = {}
        tmp = re.sub(rgxcomments, "", string)
        tmp = tmp.split("\n")

        while ("" in tmp):
            tmp.remove("")

        for i in tmp:
            match = re.search(rgxconfig, i)
            if(match):
                configDict[match.group(1)] = match.group(2)

        return configDict