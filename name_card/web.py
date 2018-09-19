





from flask import Flask, render_template, request, redirect, Response, send_file
import random, json

import zipfile

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html', name='Joe')



@app.route('/receiver', methods = ['POST'])
def worker():
    data = request.get_json(force = True)
    print(data)

    result = ''

    for item in data:
        result += str(item['make']) + '\n'

    return result


@app.route('/nametag', methods = ['POST'])
def read_name():
    data = request.get_json(force = True)
    # print("[{}]".format(data))

    result = ''

    name_list = []

    for line in data:
        print(line)
        result += "[{}]".format(line)
        name_list.append(line)


    template_str = ""

    with open("template.xml", "r", encoding = 'utf8') as template_file:
        template_str = template_file.read()

    for name in name_list:
        print(name)
        tmp_template_str = template_str
        current_str = tmp_template_str.replace("AAC_USER_NAME", name)

        with open(name + ".doc", "w", encoding = 'utf8') as output_xml:
            output_xml.write(current_str)


    with zipfile.ZipFile('result.zip', 'w') as name_zip:
        for name in name_list:
            name_zip.write(name + '.doc')
    
    return send_file("result.zip", mimetype = "application/zip",  as_attachment = True, attachment_filename='result.zip')

if __name__ == "__main__":
	app.run()