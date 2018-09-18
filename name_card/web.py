





from flask import Flask, render_template, request, redirect, Response
import random, json

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

if __name__ == "__main__":
	app.run()