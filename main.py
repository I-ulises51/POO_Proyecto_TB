from Testbench import TestBench
from config_file import config_file
from Src_File import src_file

config = config_file("config.txt").get_config()
print(config)
keys = config.keys()
words = []
for key in keys:
    words.append(key)
print(words)

source = src_file(config[words[0]], config[words[1]])
mod = source.get_content()

print("")
print("Input information within module structure: ")

print(mod.input_list)
print(mod.input_sizes_str)
print(mod.input_sizes_int)

print("")
print("Generating Testbench: ")

tb = TestBench(config[words[2]], config[words[3]], mod, config)
tb.generate()