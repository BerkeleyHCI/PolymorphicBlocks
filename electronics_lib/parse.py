import re

def parse(discription, regex_dictionary):
    extraction_table = {}

    if(discription[-1] != ' '):
        discription = discription + ' '
           
    for key in regex_dictionary:
        matches = re.findall(regex_dictionary[key], discription)
        if len(matches) == 1 and not (key in extraction_table):
            extraction_table[key] = matches[0]

    return extraction_table