
# Version 1.1
# Author: Chih-Chen Kao

import re


preamble = "MAC,PORT,IP\n"

data_regex = r"((\w\w\w\w.\w\w\w\w.\w\w\w\w),(\w+/\w+/?\w*),(\d+.\d+.\d+.(\d+))\s+)"

format_pattern = "{},{},{}\n"

print("Pattern Formatting ...")
with open("file_list.txt") as file_name:
    for file in file_name:
        with open("formatted_" + file.rstrip(), "a", encoding = "ascii") as formatted_file:
            formatted_file.write(preamble)

            with open(file.rstrip()) as file_context:
                counter = 1
                for line in file_context:

                    if line is "\n":
                        continue

                    counter += 1

                    match = re.fullmatch(data_regex, line)
                    if match is not None:
                        formatted_file.write(format_pattern.format(match[2], match[3], match[5]))
                    else:
                        print("Error!!! --- : Line: " + line + "File: " + file + "Line Number: " + str(counter))


print("Job done !")




