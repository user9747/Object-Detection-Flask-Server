from flask import Flask,request,jsonify
from momoapp import app
from momoapp.object_detection.momo_utils import hello
from momoapp.object_detection.momo_utils import display
from momoapp.object_detection.momo_utils import detect
@app.route('/')
def root():
    return {
            'status':200,
            'welcome':'Object Detection API'
            }


@app.route('/<name>')
def hello_name(name):
    hell = hello()
    return "{} {}!".format(hell,name)

@app.route('/image', methods=['GET', 'POST'])
def add_face():
    if request.method == 'POST':
        result = detect(request.form['img'])
    return jsonify(data = result)


