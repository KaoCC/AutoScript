#!/usr/bin/env python3


__author__ = "Chih-Chen Kao"
__copyright__ = "Copyright (C) 2018, Chih-Chen Kao"
__license__ = "GPL"



def main():

    name_list = []

    with open("names.txt", "r", encoding = 'utf8') as name_file:
        for name in name_file:
            name = name.strip('\ufeff').strip().rstrip()
            if name:
                name_list.append(name)
            else:
                print("Skipping empty string")


    template_str = ""

    with open("word_template.xml", "r", encoding = 'utf8') as template_file:
        template_str = template_file.read()

    # print(template_str)

    for name in name_list:
        print(name)
        current_str = template_str.replace("AAC_USER_NAME", name)

        with open(name + ".doc", "w", encoding = 'utf8') as output_xml:
            output_xml.write(current_str)

    print("Total: {}".format(len(name_list)))




if __name__ == "__main__":
    print(__copyright__)
    main()