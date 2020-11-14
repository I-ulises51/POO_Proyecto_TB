from Testbench import TestBench
from config_file import config_file
from SourceFile import SourceFileData

config = config_file("config.txt").get_config()
print(config)
keys = config.keys()
words = []
for key in keys:
    words.append(key)
print(words)

#source = src_file(config[words[0]], config[words[1]])
#mod = source.get_content()
Source = SourceFileData(config[words[0]], config[words[1]])

print("")
print("Input information within module structure: ")

print(Source.getFileInputs())
print(Source.getFileOutputs())
print(Source.getInputSizesInt())

print("")
print("Generating Testbench: ")

tb = TestBench(config[words[2]], config[words[3]], Source, config)
tb.generate()