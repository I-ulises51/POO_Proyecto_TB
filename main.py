
#import of class files
from Testbench import TestBench
from config_file import config_file
from SourceFile import SourceFileData

config = config_file("config.txt").get_config() #declaring a conjfig_file object and getting the dictionary with the configuration parameters
print(config)
keys = config.keys() #function to save the keywords of the parameters
words = []
#pstoring the keys in a list for future use
for key in keys:
    words.append(key)
print(words)

Source = SourceFileData(config[words[0]], config[words[1]]) #declaring a SourcefileData object to get information from source file
#config[word[0]]  = name of the Top module, written in the configuration file
#config[word[1]]  = directory of the Top module, written in the configuration file
print("")
print("Input information within module structure: ")

print(Source.getFileInputs()) #printing the inputs
print(Source.getFileOutputs()) #printing the outputs
print(Source.getInputSizesInt()) #printing the size of the variables

print("")
print("Generating Testbench: ")

tb = TestBench(config[words[2]], config[words[3]], Source, config) #function to get infromation for the test bench
tb.generate()#function for test bech generate