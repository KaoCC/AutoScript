



name_list = []

with open("names.txt", "r") as name_file:
    for name in name_file:
        name_list.append(name.rstrip())


template_str = ""

with open("template.xml", "r", encoding = 'utf8') as template_file:
    template_str = template_file.read()

# print(template_str)

for name in name_list:
    print(name)
    current_str = template_str.replace("AAC_USER_NAME", name)

    with open(name + ".xml", "w", encoding = 'utf8') as output_xml:
        output_xml.write(current_str)






